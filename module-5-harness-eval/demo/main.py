"""Run the Module 5 harness evaluation demo."""

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from catalog import discover_skills
from config import CONFIGS
from evaluate import REPORTS_DIR, create_client, print_trial_labels, run_study
from experiment import PauseController, run_trial
from run_log import tee_run_output
from tasks import load_scenario, scenario_names


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
SKILLS_DIR = BASE_DIR / "skills"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the complete ablation study or inspect one trial."
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=("compare", "trial"),
        default="compare",
        help="Compare configurations (default) or inspect one trial.",
    )
    parser.add_argument("--config", choices=("all", *CONFIGS))
    parser.add_argument("--scenario", choices=("all", *scenario_names()))
    parser.add_argument("--runs", type=positive_int, default=1)
    parser.add_argument("--model")
    parser.add_argument(
        "--judge-model",
        help="Override OPENAI_JUDGE_MODEL for blind offline scoring.",
    )
    parser.add_argument("--output-dir", type=Path, default=REPORTS_DIR)
    parser.add_argument("--seed", type=int, default=15570)
    parser.add_argument(
        "--no-pause",
        action="store_true",
        help="Disable Return-to-continue pauses after generator cycles.",
    )
    args = parser.parse_args()
    if args.mode == "trial":
        args.config = args.config or "full"
        args.scenario = args.scenario or "routine_triage"
        if args.config == "all" or args.scenario == "all":
            parser.error("trial mode requires one configuration and one scenario")
        if args.runs != 1:
            parser.error("--runs applies only to compare mode")
    else:
        args.config = args.config or "all"
        args.scenario = args.scenario or "all"
    return args


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def run_demo(args: argparse.Namespace) -> None:
    scenario = load_scenario(args.scenario)
    client, model, endpoint = create_client(args.model)
    judge_model = (
        args.judge_model or os.getenv("OPENAI_JUDGE_MODEL", "").strip() or model
    )
    config = CONFIGS[args.config]
    print("\n============================================================")
    print("INCIDENT HARNESS EVALUATION — SINGLE TRIAL")
    print("============================================================")
    print(f"Model: {model} | Judge: {judge_model} | Endpoint: {endpoint}")
    print_trial_labels(1, 1, scenario, args.config)
    print(
        "Components: "
        + json.dumps(
            {
                "skills": config.skills,
                "online_evaluator": config.evaluator,
                "hooks": config.hooks,
                "permissions": config.permissions,
            }
        )
    )
    result, failures, _, run = run_trial(
        client,
        model,
        config_name=args.config,
        scenario=scenario,
        trial_number=1,
        catalog=discover_skills(SKILLS_DIR),
        judge_model=judge_model,
        pause=PauseController(not args.no_pause),
    )
    print("\n================ TRIAL SUMMARY ================")
    print(f"Task success:            {result['task_success']}")
    print(f"Blind quality:           {result['quality_score']}/5")
    print(f"Invalid action executed: {result['invalid_action_executed']}")
    print(f"Unauthorized action:     {result['unauthorized_action']}")
    print(f"Skills loaded:           {', '.join(result['skills_loaded']) or 'none'}")
    print(f"Revision occurred:       {result['revision_occurred']}")
    print(f"Serving tokens:          {result['total_tokens']}")
    print(f"Benchmark tokens:        {result['benchmark_total_tokens']} (excluded)")
    print(f"Final deployment:        {run['final_incident']['current_deployment']}")
    print(f"Final incident status:   {run['final_incident']['incident_status']}")
    print(f"Structured failures:     {len(failures)}")
    for failure in failures:
        print(f"- {failure['failure_type']}: {failure['description']}")


def main() -> None:
    args = parse_args()
    if args.mode == "compare":
        try:
            client, model, endpoint = create_client(args.model)
            judge_model = (
                args.judge_model
                or os.getenv("OPENAI_JUDGE_MODEL", "").strip()
                or model
            )
            run_study(
                client,
                model,
                endpoint,
                judge_model=judge_model,
                config_name=args.config,
                scenario_name=args.scenario,
                runs=args.runs,
                output_dir=args.output_dir,
                seed=args.seed,
                pause=not args.no_pause,
            )
        except KeyboardInterrupt:
            print("\nRun interrupted.", file=sys.stderr)
            raise SystemExit(130)
        except Exception:
            traceback.print_exc()
            raise SystemExit(1)
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = OUTPUT_DIR / f"{args.config}-{args.scenario}-{timestamp}.log"
    with tee_run_output(log_path):
        print(f"Run output saved to: {log_path}")
        try:
            run_demo(args)
        except KeyboardInterrupt:
            print("\nRun interrupted.", file=sys.stderr)
            raise SystemExit(130)
        except Exception:
            traceback.print_exc()
            raise SystemExit(1)


if __name__ == "__main__":
    main()
