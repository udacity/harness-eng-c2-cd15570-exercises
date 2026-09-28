"""Run one interactive returns-harness configuration and scenario."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from catalog import discover_skills
from config import CONFIGS
from experiment import PauseController, run_trial
from run_log import tee_run_output
from tasks import load_scenario, scenario_names


BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills"
OUTPUT_DIR = BASE_DIR / "output"
BASE_URL = "https://openai.vocareum.com/v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one online-store returns harness configuration."
    )
    parser.add_argument("--config", choices=tuple(CONFIGS), default="full")
    parser.add_argument(
        "--scenario",
        choices=scenario_names(),
        default="simple_return",
        help="Task to run; defaults to simple_return.",
    )
    parser.add_argument("--model", help="Override OPENAI_MODEL for this run.")
    parser.add_argument(
        "--no-pause",
        action="store_true",
        help="Do not wait for Return after each model cycle.",
    )
    return parser.parse_args()


def _show(value: Any) -> str:
    return "N/A" if value is None else str(value)


def print_summary(
    result: dict[str, Any],
    failures: list[dict[str, Any]],
    store: dict[str, Any],
    order_ids: list[str],
) -> None:
    print("\n================ TRIAL SUMMARY ================")
    print(f"Configuration:            {result['configuration']}")
    print(f"Task:                     {result['task_name']} ({result['task_id']})")
    print(f"Task success:             {'YES' if result['task_success'] else 'NO'}")
    print(f"Blind quality score:      {_show(result['quality_score'])}")
    print(f"Generator calls:          {result['generator_calls']}")
    print(f"Online evaluator calls:   {result['evaluator_calls']}")
    print(f"Text-only revisions:      {result['revision_calls']}")
    print(f"Offline benchmark calls:  {result['benchmark_calls']} (excluded from serving cost)")
    print(f"Tool calls:               {result['tool_calls']}")
    print(f"Skills loaded:            {', '.join(result['skills_loaded']) or '(none)'}")
    print(f"Permission checks:        {_show(result['permission_checks'])}")
    print(f"Permission denials:       {_show(result['permission_denials'])}")
    print(f"Hook checks:              {_show(result['hook_checks'])}")
    print(f"Hook blocks:              {_show(result['hook_blocks'])}")
    print(f"Unauthorized execution:   {'YES' if result['unauthorized_action'] else 'NO'}")
    print(f"Invalid action executed:  {'YES' if result['invalid_action_executed'] else 'NO'}")
    print(
        "Serving API tokens:       "
        f"{_show(result['input_tokens'])} input + {_show(result['output_tokens'])} output "
        f"= {_show(result['total_tokens'])} total"
    )
    print(f"Serving model seconds:    {result['model_seconds']}")
    print(f"Total experiment runtime: {result['total_runtime_seconds']} seconds (Return waits excluded)")
    print("\nFINAL CUSTOMER RESPONSE")
    print(result["final_response"] or "(empty)")

    print("\nRELEVANT FINAL STATE")
    for order_id in order_ids:
        print(json.dumps(store["orders"].get(order_id, {"order_id": order_id, "status": "NOT FOUND"}), indent=2))
        for return_id, record in store["returns"].items():
            if record.get("order_id") == order_id:
                print(json.dumps(record, indent=2))

    print("\nFAILURES")
    if not failures:
        print("No failure record was generated for this trial.")
    for failure in failures:
        print(f"- {failure['failure_type']}: {failure['description']}")


def main() -> None:
    args = parse_args()
    try:
        from dotenv import load_dotenv
        from openai import OpenAI
    except ImportError as error:
        raise SystemExit("Install dependencies with: python3 -m pip install -r requirements.txt") from error
    scenario = load_scenario(args.scenario)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = OUTPUT_DIR / f"{args.config}-{args.scenario}-{stamp}.log"

    with tee_run_output(log_path):
        print(f"Run output saved to: {log_path}")
        load_dotenv(BASE_DIR / ".env")
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise SystemExit(f"Set OPENAI_API_KEY in {BASE_DIR / '.env'}.")
        model = args.model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        client = OpenAI(base_url=BASE_URL, api_key=api_key)
        catalog = discover_skills(SKILLS_DIR)
        pause = PauseController(enabled=not args.no_pause)
        result, failures, store = run_trial(
            client,
            model,
            config_name=args.config,
            scenario=scenario,
            trial_number=1,
            catalog=catalog,
            pause=pause,
        )
        print_summary(result, failures, store, scenario["order_ids"])


if __name__ == "__main__":
    main()
