"""Compare an expense agent with and without a before-tool hook."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from agent import run_agent
from run_log import tee_run_output


BASE_DIR = Path(__file__).resolve().parent
EXAMPLES_DIR = BASE_DIR / "examples"
OUTPUT_DIR = BASE_DIR / "output"
BASE_URL = "https://openai.vocareum.com/v1"


def parse_args() -> argparse.Namespace:
    scenarios = sorted(path.stem for path in EXAMPLES_DIR.glob("*.json"))
    parser = argparse.ArgumentParser(description="Run the expense agent with or without policy hooks.")
    parser.add_argument("--mode", choices=("basic", "hooks"), required=True)
    parser.add_argument("--scenario", choices=scenarios, default="multiple_violations")
    return parser.parse_args()


def print_summary(run: dict) -> None:
    if run["mode"] == "basic":
        violations = "not checked"
    elif not run["hook_executed"]:
        violations = "not run"
    else:
        violations = str(run["violations_detected"])

    print("\n================ EXECUTION SUMMARY ================")
    print(f"Mode:                 {run['mode']}")
    print(f"Report:               {run['report_id']}")
    print(f"Tool calls:           {len(run['events'])}")
    print(f"Report retrieved:     {'yes' if run['report_retrieved'] else 'no'}")
    print(f"Items inspected:      {run['items_inspected']}/{run['item_count']}")
    print(f"Submission requested: {'yes' if run['submission_requested'] else 'no'}")
    print(f"Hook executed:        {'yes' if run['hook_executed'] else 'no'}")
    print(f"Violations detected:  {violations}")
    print(f"Submission executed:  {'yes' if run['submission_executed'] else 'no'}")
    print(f"Final status:         {run['status']}")
    print(f"Model cycles:         {run['cycles']}")
    print(
        f"API tokens:           {run['input_tokens']} input + "
        f"{run['output_tokens']} output = {run['total_tokens']} total"
    )
    print(f"Model seconds:        {run['model_seconds']} (excludes time waiting for Return)")
    if run["mode"] == "basic":
        print("Basic mode does not check expense-policy violations in Python.")


def main() -> None:
    args = parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = OUTPUT_DIR / f"{args.mode}-{args.scenario}-{stamp}.log"

    with tee_run_output(log_path):
        print(f"Run output saved to: {log_path}")
        load_dotenv(BASE_DIR / ".env")
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise SystemExit(f"Set OPENAI_API_KEY in {BASE_DIR / '.env'}.")
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        client = OpenAI(base_url=BASE_URL, api_key=api_key)

        report_path = EXAMPLES_DIR / f"{args.scenario}.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        print("\nEXPENSE REPORT HOOKS HARNESS")
        print(f"Mode: {args.mode} | Scenario: {args.scenario} | Model: {model}")
        print("Both modes use the same policy prompt and selected report.")
        print("The agent chooses tool calls; the loop ends when it gives a final answer.")
        print("\nSELECTED REPORT (the agent retrieves this through a tool):\n" + json.dumps(report, indent=2))

        run = run_agent(client, model, report, args.mode)
        print_summary(run)


if __name__ == "__main__":
    main()
