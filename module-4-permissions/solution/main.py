"""Run a permitting agent with authorization disabled or enforced."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from agent import run_agent
from data import USERS, fresh_applications
from run_log import tee_run_output


BASE_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = BASE_DIR / "scenarios"
OUTPUT_DIR = BASE_DIR / "output"
BASE_URL = "https://openai.vocareum.com/v1"


def parse_args() -> argparse.Namespace:
    scenario_names = sorted(path.stem for path in SCENARIOS_DIR.glob("*.json"))
    parser = argparse.ArgumentParser(
        description="Compare exposed permit tools with and without authorization."
    )
    parser.add_argument("--mode", choices=("basic", "permissions"), required=True)
    parser.add_argument(
        "--scenario",
        choices=scenario_names,
        default="contractor_approve_issue",
        help="Request to run; defaults to contractor_approve_issue.",
    )
    parser.add_argument(
        "--user",
        choices=sorted(USERS),
        help="Override the scenario's authenticated user using the trusted user registry.",
    )
    return parser.parse_args()


def load_scenario(name: str) -> dict:
    path = SCENARIOS_DIR / f"{name}.json"
    scenario = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(scenario.get("authenticated_user"), str):
        raise ValueError(f"Scenario {name!r} needs authenticated_user.")
    if not isinstance(scenario.get("request"), str) or not scenario["request"].strip():
        raise ValueError(f"Scenario {name!r} needs a request.")
    application_ids = scenario.get("application_ids", [])
    if not isinstance(application_ids, list) or any(not isinstance(value, str) for value in application_ids):
        raise ValueError(f"Scenario {name!r} has invalid application_ids.")
    if scenario["authenticated_user"] not in USERS:
        raise ValueError(f"Scenario {name!r} names an unknown authenticated user.")
    scenario["application_ids"] = application_ids
    return scenario


def print_applications(label: str, applications: dict[str, dict], application_ids: list[str]) -> None:
    print(f"\n{label}")
    for application_id in application_ids:
        application = applications.get(application_id)
        print(json.dumps(application or {"application_id": application_id, "status": "NOT FOUND"}, indent=2))


def print_summary(
    run: dict,
    applications: dict[str, dict],
    application_ids: list[str],
) -> None:
    user = run["authenticated_user"]
    events = run["events"]
    checked = [event for event in events if event["permission_check"] in ("ALLOWED", "DENIED")]
    allowed = [event for event in events if event["permission_check"] == "ALLOWED"]
    denied = [event for event in events if event["permission_check"] == "DENIED"]
    executed = [event for event in events if event["tool_executed"]]

    print("\n================ EXECUTION SUMMARY ================")
    print(f"Mode:                    {run['mode']}")
    print(f"Authenticated user:      {user['name']} ({user['user_id']})")
    print(f"Role:                    {user['role']}")
    print(f"Model cycles:            {run['cycles']}")
    print(f"Tool calls:              {len(events)}")
    if run["mode"] == "basic":
        print("Permission checks:       NOT PERFORMED")
    else:
        print(f"Permission checks:       {len(checked)}")
        print(f"Actions allowed:         {len(allowed)}")
        print(f"Actions denied:          {len(denied)}")
    print(f"Tools executed:          {len(executed)}")
    print(
        f"API tokens:              {run['input_tokens']} input + "
        f"{run['output_tokens']} output = {run['total_tokens']} total"
    )
    print(f"Model seconds:           {run['model_seconds']} (excludes time waiting for Return)")

    print("\nACTION RESULTS")
    if not events:
        print("No tool was requested; no permission decision was made.")
    for index, event in enumerate(events, start=1):
        print(f"{index}. Tool:                {event['tool']}")
        print(f"   Resource:            {event['resource_id'] or '(none)'}")
        print(f"   Required permission: {event['required_permission'] or '(none)'}")
        print(f"   Permission result:   {event['permission_check']}")
        if event["ownership"] != "not_applicable":
            print(f"   Ownership:           {event['ownership'].upper()}")
        print(f"   Tool executed:       {'YES' if event['tool_executed'] else 'NO'}")
        print(f"   Result status:       {event['result_status']}")

    touched_ids = [
        event["resource_id"]
        for event in events
        if isinstance(event.get("resource_id"), str)
    ]
    final_ids = list(dict.fromkeys([*application_ids, *touched_ids]))
    print("\nFINAL APPLICATION STATE")
    for application_id in final_ids:
        application = applications.get(application_id)
        if application is None:
            print(f"{application_id}: NOT FOUND")
        else:
            print(
                f"{application_id}: status={application['status']}; "
                f"project={application['project']!r}; owner={application['owner_user_id']}"
            )


def main() -> None:
    args = parse_args()
    scenario = load_scenario(args.scenario)
    user_key = args.user or scenario["authenticated_user"]
    authenticated_user = dict(USERS[user_key])
    applications = fresh_applications()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = OUTPUT_DIR / f"{args.mode}-{args.scenario}-{user_key}-{stamp}.log"
    with tee_run_output(log_path):
        print(f"Run output saved to: {log_path}")
        load_dotenv(BASE_DIR / ".env")
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise SystemExit(f"Set OPENAI_API_KEY in {BASE_DIR / '.env'}.")
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        client = OpenAI(base_url=BASE_URL, api_key=api_key)

        mode_label = (
            "BASIC — PERMISSIONS DISABLED"
            if args.mode == "basic"
            else "PERMISSIONS — AUTHORIZATION ENABLED"
        )
        print("\n==================================================")
        print(f"MODE: {mode_label}")
        print("==================================================")
        print(f"Scenario: {args.scenario}")
        print(f"Model: {model}")
        print("\nAUTHENTICATED USER (trusted application state)")
        print(f"Name:    {authenticated_user['name']}")
        print(f"User ID: {authenticated_user['user_id']}")
        print(f"Role:    {authenticated_user['role']}")
        print("\nUSER REQUEST")
        print(scenario["request"])
        print("\nBoth modes expose the same nine tools. The agent chooses each next action.")
        print_applications("INITIAL APPLICATION STATE", applications, scenario["application_ids"])

        run = run_agent(
            client,
            model,
            args.mode,
            authenticated_user,
            scenario["request"],
            applications,
        )
        print_summary(run, applications, scenario["application_ids"])


if __name__ == "__main__":
    main()
