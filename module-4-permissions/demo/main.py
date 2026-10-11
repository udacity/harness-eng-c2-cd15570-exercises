"""Run the cumulative Module 4 incident authorization demo."""

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent import run_agent
from catalog import discover_skills
from data import USERS, fresh_incident
from evaluator import evaluate_final_note
from run_log import tee_run_output
from scenario import incident_context, load_scenario


BASE_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = BASE_DIR / "scenarios"
SKILLS_DIR = BASE_DIR / "skills"
OUTPUT_DIR = BASE_DIR / "output"
MODEL = "gpt-4.1-mini"
BASE_URL = "https://openai.vocareum.com/v1"
SCENARIO_LABELS = {
    "unauthorized_rollback": "UNAUTHORIZED ROLLBACK",
    "commander_rollback": "AUTHORIZED COMMANDER ROLLBACK",
    "impersonation_attempt": "IMPERSONATION ATTEMPT",
    "responder_rollback_resolve": "RESPONDER ROLLBACK AND RESOLUTION",
    "commander_premature_resolution": "COMMANDER PREMATURE RESOLUTION",
    "assigned_read": "ASSIGNED INCIDENT READ",
    "unassigned_read": "UNASSIGNED INCIDENT READ",
    "admin_reassign": "ADMINISTRATOR REASSIGNMENT",
}


def scenario_names() -> list[str]:
    available = {path.stem for path in SCENARIOS_DIR.glob("*.json")}
    ordered = [name for name in SCENARIO_LABELS if name in available]
    return ordered + sorted(available - set(ordered))


def parse_args() -> argparse.Namespace:
    names = scenario_names()
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
        choices=(*names, "all"),
        default="unauthorized_rollback",
        help="Incident scenario to run, or all (default: unauthorized_rollback).",
    )
    return parser.parse_args()


def create_client() -> Any:
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv(BASE_DIR / ".env")
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise SystemExit(f"Set OPENAI_API_KEY in {BASE_DIR / '.env'}.")
    return OpenAI(base_url=BASE_URL, api_key=key)


def pause_after_cycle() -> None:
    input("\nCycle complete. Press Return to continue...")


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


TOOL_LABELS = {
    "get_incident": "incident read",
    "get_service_health": "health read",
    "get_deployment_history": "deployment read",
    "query_service_logs": "log read",
    "rollback_deployment": "rollback",
    "update_incident_status": "status update",
    "reassign_incident": "reassignment",
}
READ_TOOLS = {
    "get_incident",
    "get_service_health",
    "get_deployment_history",
    "query_service_logs",
}


def _tool_names(events: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for event in events:
        name = event["tool"]
        counts[name] = counts.get(name, 0) + 1
    read_count = sum(count for name, count in counts.items() if name in READ_TOOLS)
    labels: list[str] = []
    if read_count == 1:
        read_name = next(name for name in counts if name in READ_TOOLS)
        labels.append(TOOL_LABELS[read_name])
    elif read_count > 1:
        labels.append(f"evidence reads x{read_count}")
    for name, count in counts.items():
        if name in READ_TOOLS:
            continue
        label = TOOL_LABELS.get(name, name)
        labels.append(f"{label} x{count}" if count > 1 else label)
    return ", ".join(labels) or "none"


def _basic_result(run: dict[str, Any] | None) -> str:
    if run is None:
        return "not run"
    events = business_events(run)
    executed = [event for event in events if event["tool_executed"]]
    blocked = [event for event in events if event["result_status"] == "blocked"]
    parts = [f"executed: {_tool_names(executed)}"]
    if blocked:
        parts.append(f"hook blocked: {_tool_names(blocked)}")
    return "; ".join(parts)


def _permissions_result(run: dict[str, Any] | None) -> str:
    if run is None:
        return "not run"
    events = business_events(run)
    executed = [event for event in events if event["tool_executed"]]
    denied = [event for event in events if event["permission_check"] == "DENIED"]
    blocked = [event for event in events if event["result_status"] == "blocked"]
    parts = [f"executed after ALLOW: {_tool_names(executed)}"]
    if denied:
        parts.append(f"denied: {_tool_names(denied)}")
    if blocked:
        parts.append(f"hook blocked: {_tool_names(blocked)}")
    return "; ".join(parts)


def _authorization_effect(
    basic: dict[str, Any] | None, permissions: dict[str, Any] | None
) -> str:
    if permissions is None:
        return "Run compare mode to observe authorization."
    events = business_events(permissions)
    denied = [event for event in events if event["permission_check"] == "DENIED"]
    allowed = [event for event in events if event["permission_check"] == "ALLOWED"]
    blocked = [event for event in allowed if event["result_status"] == "blocked"]
    effects: list[str] = []
    if denied:
        effects.append(f"stopped unauthorized {_tool_names(denied)}")
    elif allowed:
        effects.append(f"verified authority for {len(allowed)} call(s)")
    if blocked:
        effects.append(f"hook independently blocked {_tool_names(blocked)}")
    if basic is not None:
        before = basic["final_incident"]
        after = permissions["final_incident"]
        changed = []
        for label, key in (
            ("deployment", "current_deployment"),
            ("status", "incident_status"),
            ("assignee", "assigned_user_id"),
        ):
            if before[key] != after[key]:
                changed.append(f"{label} {before[key]} -> {after[key]}")
        if changed:
            effects.append("; ".join(changed))
    return "; ".join(effects) or "no business tool call was proposed"


def print_comparison(rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        run = row["run"]
        grouped.setdefault(run["scenario_id"], {})[run["mode"]] = run

    table_rows: list[tuple[str, str, str, str]] = []
    for scenario_id, runs in grouped.items():
        basic = runs.get("basic")
        permissions = runs.get("permissions")
        table_rows.append(
            (
                scenario_id,
                _basic_result(basic),
                _permissions_result(permissions),
                _authorization_effect(basic, permissions),
            )
        )

    headers = (
        "Scenario",
        "Without permissions (basic)",
        "With permissions",
        "What permissions added",
    )
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in table_rows))
        for index in range(len(headers))
    ]
    print("\n================ PERMISSIONS VALUE COMPARISON ================")
    print(" | ".join(f"{value:<{widths[index]}}" for index, value in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))
    for row in table_rows:
        print(" | ".join(f"{value:<{widths[index]}}" for index, value in enumerate(row)))
    print(
        "Basic skips authorization, while existing safety hooks still check mutations. "
        "Permissions checks every proposed action and resource before hooks or tools run."
    )
    print("Evaluator calls are benchmark overhead, excluded from serving metrics.")


def run_demo(args: argparse.Namespace) -> None:
    catalog = discover_skills(SKILLS_DIR)
    scenario_paths = (
        [SCENARIOS_DIR / f"{name}.json" for name in scenario_names()]
        if args.scenario == "all"
        else [SCENARIOS_DIR / f"{args.scenario}.json"]
    )
    modes = ("basic", "permissions") if args.mode == "compare" else (args.mode,)
    client = create_client()

    print("\n============================================================")
    print("INCIDENT-RESPONSE PERMISSIONS DEMO")
    print("============================================================")
    print(f"Model: {MODEL} | Endpoint: {BASE_URL}")
    print(f"Skills available: {', '.join(catalog)}")
    print("\nBoth modes retain Module 3 safety hooks; only authorization changes.")

    rows: list[dict[str, Any]] = []
    scenario_count = len(scenario_paths)
    for scenario_number, path in enumerate(scenario_paths, start=1):
        scenario = load_scenario(path)
        authenticated_user = dict(USERS[scenario["authenticated_user"]])
        print("\n============================================================")
        print(f"SCENARIO {scenario_number} OF {scenario_count} START")
        label = SCENARIO_LABELS.get(
            scenario["scenario_id"], scenario["scenario_id"].upper()
        )
        print(
            f"{label} ({scenario['scenario_id']})"
        )
        print("============================================================")
        print("\nAUTHENTICATED USER (trusted application state)")
        print(json.dumps(authenticated_user, indent=2))
        print("\nUSER REQUEST")
        print(scenario["request"])
        print("\nPRISTINE INCIDENT STATE FOR EACH MODE")
        print(incident_context(fresh_incident()))

        for mode in modes:
            incident = fresh_incident()
            print("\n============================================================")
            print(f"{mode.upper()} LOOP START")
            print("============================================================")
            run = run_agent(
                client,
                MODEL,
                mode,
                authenticated_user,
                scenario,
                incident,
                catalog,
                pause=pause_after_cycle,
            )
            evaluation = evaluate_final_note(
                client,
                MODEL,
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
    log_path = OUTPUT_DIR / f"{args.mode}-{args.scenario}-{timestamp}.log"
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
