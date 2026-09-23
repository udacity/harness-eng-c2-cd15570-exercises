"""Run the controlled ablation study and generate CSV, JSON, and Markdown artifacts."""

from __future__ import annotations

import argparse
import os
import random
from pathlib import Path

from catalog import discover_skills
from config import CONFIGS
from experiment import PauseController, failed_trial_result, run_trial
from metrics import aggregate_results, build_failures, write_artifacts
from tasks import load_core_scenarios, load_scenario, scenario_names


BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills"
REPORTS_DIR = BASE_DIR / "reports"
BASE_URL = "https://openai.vocareum.com/v1"


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate returns-harness configurations with controlled ablations."
    )
    parser.add_argument(
        "--config",
        choices=("all", *CONFIGS),
        default="all",
        help="Configuration to evaluate; defaults to all six.",
    )
    parser.add_argument(
        "--task",
        choices=("all", *scenario_names()),
        default="all",
        help="One task to run; all means the five core tasks.",
    )
    parser.add_argument(
        "--include-optional",
        action="store_true",
        help="Include duplicate_refund when --task all is selected.",
    )
    parser.add_argument(
        "--runs",
        type=positive_int,
        default=3,
        help="Repeated trials per task/configuration; defaults to 3.",
    )
    parser.add_argument("--model", help="Override OPENAI_MODEL for this study.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPORTS_DIR,
        help="Artifact directory; defaults to reports/.",
    )
    parser.add_argument(
        "--pause",
        action="store_true",
        help="Wait for Return after each model call. Batch mode is noninteractive by default.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=15570,
        help="Seed used to randomize trial execution order; defaults to 15570.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        from dotenv import load_dotenv
        from openai import OpenAI
    except ImportError as error:
        raise SystemExit("Install dependencies with: python3 -m pip install -r requirements.txt") from error
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(f"Set OPENAI_API_KEY in {BASE_DIR / '.env'}.")
    model = args.model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = OpenAI(base_url=BASE_URL, api_key=api_key)
    catalog = discover_skills(SKILLS_DIR)

    config_names = list(CONFIGS) if args.config == "all" else [args.config]
    if args.task == "all":
        scenarios = load_core_scenarios()
        if args.include_optional:
            scenarios.append(load_scenario("duplicate_refund"))
    else:
        scenarios = [load_scenario(args.task)]

    projected = len(config_names) * len(scenarios) * args.runs
    print("================ HARNESS ABLATION STUDY ================")
    print(f"Model:          {model}")
    print(f"Configurations: {', '.join(config_names)}")
    print(f"Tasks:          {', '.join(item['task_id'] for item in scenarios)}")
    print(f"Trials each:    {args.runs}")
    print(f"Total trials:   {projected}")
    print(f"Order seed:     {args.seed}")
    print(f"Pauses:         {'enabled' if args.pause else 'disabled for batch execution'}")

    results = []
    failures = []
    plan = [
        (config_name, scenario, trial_number)
        for trial_number in range(1, args.runs + 1)
        for scenario in scenarios
        for config_name in config_names
    ]
    random.Random(args.seed).shuffle(plan)
    output_dir = args.output_dir.resolve()
    consecutive_errors = 0
    paths = None
    for execution_index, (config_name, scenario, trial_number) in enumerate(plan, start=1):
        pause = PauseController(enabled=args.pause)
        try:
            result, trial_failures, _ = run_trial(
                client,
                model,
                config_name=config_name,
                scenario=scenario,
                trial_number=trial_number,
                catalog=catalog,
                pause=pause,
            )
            consecutive_errors = 0
        except Exception as error:
            consecutive_errors += 1
            result = failed_trial_result(
                model=model,
                config_name=config_name,
                scenario=scenario,
                trial_number=trial_number,
                error=error,
            )
            trial_failures = build_failures(result)
            print(
                f"\nTRIAL FAILED: {result['run_id']}\n"
                f"{result['run_error']}\n"
                "The failure is recorded; completed rows are being checkpointed."
            )

        result["execution_index"] = execution_index
        result["study_seed"] = args.seed
        result["study_expected_configurations"] = list(config_names)
        result["study_expected_tasks"] = [item["task_id"] for item in scenarios]
        result["study_expected_runs"] = args.runs
        result["study_expected_trials"] = projected
        results.append(result)
        failures.extend(trial_failures)
        paths = write_artifacts(results, failures, output_dir)
        print(f"\nPROGRESS: {execution_index}/{projected} trials complete or recorded")

        if consecutive_errors >= 3:
            raise SystemExit(
                "Stopped after three consecutive trial exceptions. "
                f"Partial artifacts are saved in {output_dir}."
            )

    assert paths is not None
    aggregates = aggregate_results(results)
    print("\n================ EVALUATION COMPLETE ================")
    for name, aggregate in aggregates.items():
        quality = aggregate["quality_mean"]
        quality_text = "N/A" if quality is None else f"{quality:.2f}"
        invalid_text = "N/A" if aggregate["invalid_actions"] is None else str(aggregate["invalid_actions"])
        unauthorized_text = (
            "N/A"
            if aggregate["unauthorized_actions"] is None
            else str(aggregate["unauthorized_actions"])
        )
        print(
            f"{name:14} success={aggregate['success_rate']:.1%} "
            f"quality={quality_text} invalid={invalid_text} "
            f"unauthorized={unauthorized_text}"
        )
    print(f"Results CSV: {paths['results']}")
    print(f"Failures JSON: {paths['failures']}")
    print(f"Markdown report: {paths['report']}")


if __name__ == "__main__":
    main()
