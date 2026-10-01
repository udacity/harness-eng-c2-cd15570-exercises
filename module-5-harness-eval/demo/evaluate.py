"""Run the controlled ablation study and write CSV, JSON, and Markdown evidence."""

import argparse
import os
import random
from pathlib import Path
from typing import Any, Callable

from catalog import discover_skills
from clients import ScriptedClient
from config import CONFIGS
from experiment import PauseController, failed_trial_result, run_trial
from metrics import aggregate_results, build_failures, write_artifacts
from tasks import load_core_scenarios, load_scenario, scenario_names


BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills"
REPORTS_DIR = BASE_DIR / "reports"


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the incident harness ablation study.")
    parser.add_argument("--config", choices=("all", *CONFIGS), default="all")
    parser.add_argument("--task", choices=("all", *scenario_names()), default="all")
    parser.add_argument("--runs", type=positive_int, default=1)
    parser.add_argument(
        "--provider", choices=("scripted", "live"), default="scripted"
    )
    parser.add_argument("--model")
    parser.add_argument("--output-dir", type=Path, default=REPORTS_DIR)
    parser.add_argument("--seed", type=int, default=15570)
    parser.add_argument("--pause", action="store_true")
    return parser.parse_args()


def client_factory(
    provider: str, model_override: str | None
) -> tuple[Callable[[dict, str], Any], str, str]:
    if provider == "scripted":
        return (
            lambda scenario, config_name: ScriptedClient(
                scenario, CONFIGS[config_name]
            ),
            "scripted-fixture",
            "local",
        )
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv(BASE_DIR / ".env")
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise SystemExit(f"Set OPENAI_API_KEY in {BASE_DIR / '.env'}.")
    model = model_override or os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
    base_url = os.getenv(
        "OPENAI_BASE_URL", "https://openai.vocareum.com/v1"
    ).strip()
    shared = OpenAI(base_url=base_url, api_key=key)
    return lambda _scenario, _config_name: shared, model, base_url


def main() -> None:
    args = parse_args()
    make_client, model, endpoint = client_factory(args.provider, args.model)
    catalog = discover_skills(SKILLS_DIR)
    config_names = list(CONFIGS) if args.config == "all" else [args.config]
    scenarios = (
        load_core_scenarios()
        if args.task == "all"
        else [load_scenario(args.task)]
    )
    projected = len(config_names) * len(scenarios) * args.runs
    plan = [
        (config_name, scenario, trial)
        for trial in range(1, args.runs + 1)
        for scenario in scenarios
        for config_name in config_names
    ]
    random.Random(args.seed).shuffle(plan)
    print("================ INCIDENT HARNESS ABLATION STUDY ================")
    print(f"Provider:       {args.provider}")
    print(f"Model:          {model}")
    print(f"Endpoint:       {endpoint}")
    print(f"Configurations: {', '.join(config_names)}")
    print(f"Tasks:          {', '.join(item['task_id'] for item in scenarios)}")
    print(f"Trials each:    {args.runs}")
    print(f"Total trials:   {projected}")
    print(f"Order seed:     {args.seed}")

    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    paths = None
    consecutive_errors = 0
    expected_tasks = [item["task_id"] for item in scenarios]
    for index, (config_name, scenario, trial) in enumerate(plan, start=1):
        try:
            result, trial_failures, _, _ = run_trial(
                make_client(scenario, config_name),
                model,
                config_name=config_name,
                scenario=scenario,
                trial_number=trial,
                catalog=catalog,
                pause=PauseController(args.pause),
            )
            consecutive_errors = 0
        except Exception as error:
            consecutive_errors += 1
            result = failed_trial_result(
                model, config_name, scenario, trial, error
            )
            trial_failures = build_failures(result)
            print(f"TRIAL FAILED: {result['run_id']}: {result['run_error']}")
        result.update(
            execution_index=index,
            study_seed=args.seed,
            study_expected_configurations=list(config_names),
            study_expected_tasks=expected_tasks,
            study_expected_runs=args.runs,
            study_expected_trials=projected,
        )
        results.append(result)
        failures.extend(trial_failures)
        paths = write_artifacts(results, failures, args.output_dir.resolve())
        print(f"PROGRESS: {index}/{projected}")
        if consecutive_errors >= 3:
            raise SystemExit("Stopped after three consecutive trial exceptions.")

    assert paths is not None
    print("\n================ EVALUATION COMPLETE ================")
    for name, item in aggregate_results(results).items():
        quality = "N/A" if item["quality_mean"] is None else f"{item['quality_mean']:.2f}"
        print(
            f"{name:15} success={item['success_rate']:.0%} quality={quality} "
            f"invalid={item['invalid_actions']} unauthorized={item['unauthorized_actions']}"
        )
    print(f"Results CSV:     {paths['results']}")
    print(f"Failures JSON:   {paths['failures']}")
    print(f"Markdown report: {paths['report']}")


if __name__ == "__main__":
    main()
