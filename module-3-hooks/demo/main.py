"""Run the cumulative Module 3 incident-response hooks demo."""

import argparse
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent import run_agent
from catalog import discover_skills
from evaluator import evaluate_final_note
from run_log import tee_run_output
from scenario import incident_context, load_scenario


BASE_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = BASE_DIR / "scenarios"
SKILLS_DIR = BASE_DIR / "skills"
OUTPUT_DIR = BASE_DIR / "output"
MODEL = "gpt-4.1-mini"
BASE_URL = "https://openai.vocareum.com/v1"


def parse_args() -> argparse.Namespace:
    scenario_names = sorted(path.stem for path in SCENARIOS_DIR.glob("*.json"))
    parser = argparse.ArgumentParser(
        description="Compare an incident agent with and without mutation hooks."
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=("basic", "hooks", "compare"),
        default="compare",
    )
    parser.add_argument(
        "--scenario",
        choices=(*scenario_names, "all"),
        default="unsafe_remediation",
        help="Incident scenario to run, or all (default: unsafe_remediation).",
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


def print_summary(run: dict[str, Any]) -> None:
    violations = (
        "not checked"
        if run["mode"] == "basic"
        else "not run"
        if not run["hook_executed"]
        else str(run["violations_detected"])
    )
    before = run["initial_incident"]
    after = run["final_incident"]
    print("\n================ EXECUTION SUMMARY ================")
    print(f"Mode:                 {run['mode']}")
    print(f"Scenario:             {run['scenario_id']}")
    print(f"Skills loaded:        {', '.join(run['loaded_skills']) or 'none'}")
    print(f"Tool calls:           {len(run['events'])}")
    print(f"Mutations requested:  {run['mutations_requested']}")
    print(f"Hook executed:        {'yes' if run['hook_executed'] else 'no'}")
    print(f"Failed rules:         {violations}")
    print(f"Mutations executed:   {run['mutations_executed']}")
    print(f"Deployment:           {before['current_deployment']} -> {after['current_deployment']}")
    print(f"Incident status:      {before['incident_status']} -> {after['incident_status']}")
    print(f"Final status:         {run['status']}")
    print(f"Model cycles:         {run['cycles']}")
    print(
        f"Serving API tokens:   {run['input_tokens']} input + "
        f"{run['output_tokens']} output = {run['total_tokens']} total"
    )
    print(f"Model seconds:        {run['model_seconds']} (excludes presenter pauses)")
    if run["mode"] == "basic":
        print("Basic mode intentionally does not check mutation invariants in Python.")


def _final_state(run: dict[str, Any] | None) -> str:
    if run is None:
        return "(not run)"
    incident = run["final_incident"]
    return f"{incident['current_deployment']} / {incident['incident_status']}"


def _hook_decision(run: dict[str, Any] | None) -> str:
    if run is None:
        return "(not run)"
    blocked_events = [
        event for event in run["events"] if event["status"] == "blocked"
    ]
    blocked_counts: dict[str, int] = {}
    for event in blocked_events:
        blocked_counts[event["tool"]] = blocked_counts.get(event["tool"], 0) + 1
    blocked_tools = ", ".join(
        f"{name} x{count}" if count > 1 else name
        for name, count in blocked_counts.items()
    )
    decisions: list[str] = []
    if run["mutations_executed"]:
        decisions.append(f"ALLOWED {run['mutations_executed']}")
    if blocked_events:
        decisions.append(f"BLOCKED {len(blocked_events)}: {blocked_tools}")
    return "; ".join(decisions) or "NO MUTATION DECISION"


def _hook_benefit(
    basic: dict[str, Any] | None, hooks: dict[str, Any] | None
) -> str:
    if hooks is None:
        return "Run compare mode to observe the hook."

    blocked = any(event["status"] == "blocked" for event in hooks["events"])
    if basic is None:
        return (
            "Unsafe request prevented before execution."
            if blocked
            else "Allowed after safety checks passed."
        )

    basic_final = basic["final_incident"]
    hooks_final = hooks["final_incident"]
    initial = basic["initial_incident"]
    benefits: list[str] = []

    basic_changed_deployment = (
        basic_final["current_deployment"] != initial["current_deployment"]
    )
    basic_used_non_lkg = (
        basic_final["current_deployment"]
        != initial["last_known_good_deployment"]
    )
    hook_avoided_basic_deployment = (
        hooks_final["current_deployment"]
        != basic_final["current_deployment"]
    )
    if basic_changed_deployment and basic_used_non_lkg and hook_avoided_basic_deployment:
        benefits.append("prevented rollback to a version not marked last-known-good")

    basic_resolved_without_recovery = basic_final["incident_status"] == "RESOLVED" and (
        basic_final["service_health"] != "HEALTHY"
        or not basic_final["recovery_confirmed"]
    )
    hook_kept_incident_open = hooks_final["incident_status"] != "RESOLVED"
    if basic_resolved_without_recovery and hook_kept_incident_open:
        benefits.append("kept the incident open while service was DEGRADED")

    if hooks["mutations_executed"] and blocked:
        benefits.append(
            "allowed the checked change and blocked an unsafe/repeated request"
        )
    elif not benefits and blocked:
        benefits.append("prevented an unsafe/repeated request")
    elif not blocked and hooks["mutations_executed"]:
        benefits.append("allowed the change after its checks passed")
    elif not benefits:
        benefits.append("no mutation decision observed")

    return "; ".join(benefits)


def print_comparison(rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        run = row["run"]
        grouped.setdefault(run["scenario_id"], {})[run["mode"]] = run

    print("\n================ WHY HOOKS ARE SAFER ================")
    print(
        "Scenario             | Basic final (unchecked)      | "
        "Hooks final (checked)        | Hook decision                                      | "
        "Safety benefit"
    )
    print(
        "---------------------+------------------------------+"
        "------------------------------+----------------------------------------------------+"
        "---------------------------------------------------------"
    )
    for scenario_id, runs in grouped.items():
        basic = runs.get("basic")
        hooks = runs.get("hooks")
        print(
            f"{scenario_id:<21}| "
            f"{_final_state(basic):<29}| "
            f"{_final_state(hooks):<29}| "
            f"{_hook_decision(hooks):<51}| "
            f"{_hook_benefit(basic, hooks)}"
        )
    print(
        "Basic shows the state produced when mutation calls execute without the "
        "hook. Hooks shows the state after each call is checked before execution."
    )
    print("Evaluator calls are benchmark overhead, excluded from serving metrics.")


def run_demo(args: argparse.Namespace) -> None:
    catalog = discover_skills(SKILLS_DIR)
    scenario_paths = (
        sorted(SCENARIOS_DIR.glob("*.json"))
        if args.scenario == "all"
        else [SCENARIOS_DIR / f"{args.scenario}.json"]
    )
    modes = ("basic", "hooks") if args.mode == "compare" else (args.mode,)
    client = create_client()

    print("\n============================================================")
    print("INCIDENT-RESPONSE HOOKS DEMO")
    print("============================================================")
    print(f"Model: {MODEL} | Endpoint: {BASE_URL}")
    print(f"Skills available: {', '.join(catalog)}")
    print("Permissions are displayed but intentionally not enforced until Module 4.")

    rows: list[dict[str, Any]] = []
    for path in scenario_paths:
        scenario = load_scenario(path)
        print("\n============================================================")
        print(f"SCENARIO: {scenario['scenario_id']}")
        print("============================================================")
        print(f"Authenticated role: {scenario['authenticated_user']['role']}")
        print("\nOPERATOR REQUEST\n" + scenario["request"])
        print("\nINITIAL AUTHORITATIVE INCIDENT STATE")
        print(incident_context(scenario["incident"]))

        for mode in modes:
            print("\n============================================================")
            print(f"MODE: {mode.upper()}")
            print("============================================================")
            run = run_agent(
                client, MODEL, scenario, mode, catalog, pause=pause_after_cycle
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
        "A prompt or skill may describe safe behavior, but only harness code at "
        "the execution boundary can deterministically prevent an unsafe tool call."
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
