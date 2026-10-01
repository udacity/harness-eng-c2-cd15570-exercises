"""Run the cumulative Module 4 incident authorization demo."""

import argparse
import json
import os
import sys
import traceback
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent import run_agent
from catalog import discover_skills
from clients import ScriptedClient
from data import USERS, fresh_incident
from evaluator import evaluate_final_note
from run_log import tee_run_output
from scenario import incident_context, load_scenario


BASE_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = BASE_DIR / "scenarios"
SKILLS_DIR = BASE_DIR / "skills"
OUTPUT_DIR = BASE_DIR / "output"


def parse_args() -> argparse.Namespace:
    names = sorted(path.stem for path in SCENARIOS_DIR.glob("*.json"))
    parser = argparse.ArgumentParser(
        description="Compare incident tools with and without authorization."
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=("basic", "permissions", "compare"),
        default="compare",
    )
    parser.add_argument(
        "--scenario",
        choices=names,
        default="unauthorized_rollback",
        help="Request to run (default: unauthorized_rollback).",
    )
    parser.add_argument(
        "--provider",
        choices=("scripted", "live"),
        default="scripted",
        help="Use deterministic fixtures or a live model (default: scripted).",
    )
    parser.add_argument("--model", help="Override OPENAI_MODEL for live runs.")
    parser.add_argument(
        "--pause", action="store_true", help="Wait for Return after each model cycle."
    )
    return parser.parse_args()


def create_client(
    provider: str, model_override: str | None, scenario: dict
) -> tuple[Any, str, str]:
    if provider == "scripted":
        return ScriptedClient(scenario), "scripted-fixture", "local"

    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv(BASE_DIR / ".env")
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            f"Set OPENAI_API_KEY in {BASE_DIR / '.env'} before using --provider live."
        )
    model = model_override or os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
    base_url = os.getenv(
        "OPENAI_BASE_URL", "https://openai.vocareum.com/v1"
    ).strip()
    return OpenAI(base_url=base_url, api_key=key), model, base_url


def pause_callback(enabled: bool) -> Callable[[], None]:
    if not enabled:
        return lambda: None

    def pause() -> None:
        input("\nCycle complete. Press Return to continue...")

    return pause


def print_evaluation(evaluation: dict[str, Any]) -> None:
    print("\nINDEPENDENT EVALUATION")
    print(
        f"WORD_COUNT: {'PASS' if evaluation['word_count_passed'] else 'FAIL'} "
        f"({evaluation['word_count']} words; expected 60)"
    )
    print(
        f"INCIDENT_ID: {'PASS' if evaluation['incident_id_passed'] else 'FAIL'}"
    )
    print(evaluation["raw_review"])
    print(f"OVERALL: {'PASS' if evaluation['passed'] else 'FAIL'}")
    print(
        "Benchmark overhead: "
        f"{evaluation['benchmark_input_tokens']} input + "
        f"{evaluation['benchmark_output_tokens']} output tokens; "
        f"{evaluation['benchmark_seconds']} seconds."
    )


def business_events(run: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        event
        for event in run["events"]
        if event["permission_check"] != "NOT APPLICABLE"
    ]


def print_summary(run: dict[str, Any]) -> None:
    user = run["authenticated_user"]
    events = business_events(run)
    checked = [
        event
        for event in events
        if event["permission_check"] in ("ALLOWED", "DENIED")
    ]
    allowed = [event for event in events if event["permission_check"] == "ALLOWED"]
    denied = [event for event in events if event["permission_check"] == "DENIED"]
    executed = [event for event in events if event["tool_executed"]]
    hooked = [event for event in events if event["hook_executed"]]
    blocked = [event for event in events if event["result_status"] == "blocked"]
    before = run["initial_incident"]
    after = run["final_incident"]

    print("\n================ EXECUTION SUMMARY ================")
    print(f"Mode:                    {run['mode']}")
    print(f"Authenticated user:      {user['name']} ({user['user_id']})")
    print(f"Role:                    {user['role']}")
    print(f"Skills loaded:           {', '.join(run['loaded_skills']) or 'none'}")
    print(f"Business tool calls:     {len(events)}")
    if run["mode"] == "basic":
        print("Permission checks:       NOT PERFORMED")
    else:
        print(f"Permission checks:       {len(checked)}")
        print(f"Actions allowed:         {len(allowed)}")
        print(f"Actions denied:          {len(denied)}")
    print(f"Safety hooks executed:   {len(hooked)}")
    print(f"Actions hook-blocked:    {len(blocked)}")
    print(f"Business tools executed: {len(executed)}")
    print(f"Deployment:              {before['current_deployment']} -> {after['current_deployment']}")
    print(f"Incident status:         {before['incident_status']} -> {after['incident_status']}")
    print(f"Assigned user:           {before['assigned_user_id']} -> {after['assigned_user_id']}")
    print(f"Model cycles:            {run['cycles']}")
    print(
        f"Serving API tokens:      {run['input_tokens']} input + "
        f"{run['output_tokens']} output = {run['total_tokens']} total"
    )
    print(f"Model seconds:           {run['model_seconds']} (excludes presenter pauses)")

    print("\nACTION RESULTS")
    if not events:
        print("No business tool was requested; no permission decision was made.")
    for index, event in enumerate(events, start=1):
        print(f"{index}. Tool:                {event['tool']}")
        print(f"   Resource:            {event['resource_id'] or '(none)'}")
        print(f"   Required permission: {event['required_permission'] or '(none)'}")
        print(f"   Permission result:   {event['permission_check']}")
        if event["ownership"] != "not_applicable":
            print(f"   Assignment:          {event['ownership'].upper()}")
        print(f"   Safety hook:         {'RAN' if event['hook_executed'] else 'NOT RUN'}")
        print(f"   Tool executed:       {'YES' if event['tool_executed'] else 'NO'}")
        print(f"   Result status:       {event['result_status']}")


def print_comparison(rows: list[dict[str, Any]]) -> None:
    if len(rows) < 2:
        return
    print("\n================ ENFORCEMENT COMPARISON ================")
    print("Mode        | Allowed | Denied | Hooked | Executed | Deploy       | Status")
    print("------------+---------+--------+--------+----------+--------------+--------------")
    for row in rows:
        run = row["run"]
        events = business_events(run)
        allowed = sum(event["permission_check"] == "ALLOWED" for event in events)
        denied = sum(event["permission_check"] == "DENIED" for event in events)
        hooked = sum(event["hook_executed"] for event in events)
        executed = sum(event["tool_executed"] for event in events)
        print(
            f"{run['mode']:<12}| {str(allowed) if run['mode'] == 'permissions' else 'n/a':<8}| "
            f"{str(denied) if run['mode'] == 'permissions' else 'n/a':<7}| "
            f"{hooked:<7}| {executed:<9}| "
            f"{run['final_incident']['current_deployment']:<13}| "
            f"{run['final_incident']['incident_status']}"
        )
    print("Evaluator calls are benchmark overhead, excluded from serving metrics.")


def run_demo(args: argparse.Namespace) -> None:
    scenario = load_scenario(SCENARIOS_DIR / f"{args.scenario}.json")
    authenticated_user = dict(USERS[scenario["authenticated_user"]])
    catalog = discover_skills(SKILLS_DIR)
    modes = ("basic", "permissions") if args.mode == "compare" else (args.mode,)
    pause = pause_callback(args.pause)
    client, model, endpoint = create_client(args.provider, args.model, scenario)

    print("\n============================================================")
    print("INCIDENT-RESPONSE PERMISSIONS DEMO")
    print("============================================================")
    print(f"Provider: {args.provider} | Model: {model} | Endpoint: {endpoint}")
    print(f"Scenario: {scenario['scenario_id']}")
    print(f"Skills available: {', '.join(catalog)}")
    print("\nAUTHENTICATED USER (trusted application state)")
    print(json.dumps(authenticated_user, indent=2))
    print("\nUSER REQUEST")
    print(scenario["request"])
    print("\nPRISTINE INCIDENT STATE FOR EACH MODE")
    print(incident_context(fresh_incident()))
    print("\nBoth modes retain Module 3 safety hooks; only authorization changes.")

    rows: list[dict[str, Any]] = []
    for mode in modes:
        incident = fresh_incident()
        print("\n============================================================")
        print(f"MODE: {mode.upper()}")
        print("============================================================")
        run = run_agent(
            client,
            model,
            mode,
            authenticated_user,
            scenario,
            incident,
            catalog,
            pause=pause,
        )
        evaluation = evaluate_final_note(
            client,
            model,
            run["final_incident"],
            run["events"],
            run["output"],
        )
        print_evaluation(evaluation)
        print_summary(run)
        rows.append({"run": run, "evaluation": evaluation})

    print_comparison(rows)
    print("\nTeaching takeaway:")
    print(
        "Tool availability creates capability, not authority. The harness must "
        "authorize the trusted subject, proposed action, and resource before "
        "running independent safety checks and executing the tool."
    )


def main() -> None:
    args = parse_args()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = OUTPUT_DIR / f"{args.mode}-{args.scenario}-{args.provider}-{timestamp}.log"
    with tee_run_output(log_path):
        print(f"Run output saved to: {log_path}")
        try:
            run_demo(args)
        except KeyboardInterrupt:
            print("\nRun interrupted.", file=sys.stderr)
            raise SystemExit(130)
        except SystemExit as error:
            if isinstance(error.code, str):
                print(error.code, file=sys.stderr)
                raise SystemExit(1)
            raise
        except Exception:
            traceback.print_exc()
            raise SystemExit(1)


if __name__ == "__main__":
    main()
