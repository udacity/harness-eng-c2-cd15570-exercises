"""Inspect one task and one harness configuration interactively."""

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from catalog import discover_skills
from config import CONFIGS
from evaluate import client_factory
from experiment import PauseController, run_trial
from run_log import tee_run_output
from tasks import load_scenario, scenario_names


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
SKILLS_DIR = BASE_DIR / "skills"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect one incident harness trial.")
    parser.add_argument("--config", choices=CONFIGS, default="full")
    parser.add_argument("--scenario", choices=scenario_names(), default="routine_triage")
    parser.add_argument("--provider", choices=("scripted", "live"), default="scripted")
    parser.add_argument("--model")
    parser.add_argument("--pause", action="store_true")
    return parser.parse_args()


def run_demo(args: argparse.Namespace) -> None:
    scenario = load_scenario(args.scenario)
    make_client, model, endpoint = client_factory(args.provider, args.model)
    config = CONFIGS[args.config]
    print("\n============================================================")
    print("INCIDENT HARNESS EVALUATION — SINGLE TRIAL")
    print("============================================================")
    print(f"Provider: {args.provider} | Model: {model} | Endpoint: {endpoint}")
    print(f"Task: {scenario['task_id']} | Configuration: {args.config}")
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
        make_client(scenario, args.config),
        model,
        config_name=args.config,
        scenario=scenario,
        trial_number=1,
        catalog=discover_skills(SKILLS_DIR),
        pause=PauseController(args.pause),
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
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = OUTPUT_DIR / f"{args.config}-{args.scenario}-{args.provider}-{timestamp}.log"
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
