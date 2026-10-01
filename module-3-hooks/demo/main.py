"""Run the cumulative Module 3 incident-response hooks demo."""

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
from evaluator import evaluate_final_note
from run_log import tee_run_output
from scenario import incident_context, load_scenario


BASE_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = BASE_DIR / "scenarios"
SKILLS_DIR = BASE_DIR / "skills"
OUTPUT_DIR = BASE_DIR / "output"


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
        choices=scenario_names,
        default="unsafe_remediation",
        help="Incident scenario to run (default: unsafe_remediation).",
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


def create_client(provider: str, model_override: str | None) -> tuple[Any, str, str]:
    if provider == "scripted":
        return ScriptedClient(), "scripted-fixture", "local"

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


def print_comparison(rows: list[dict[str, Any]]) -> None:
    if len(rows) < 2:
        return
    print("\n================ STATE COMPARISON ================")
    print("Mode  | Hook | Failed rules | Executed | Deployment   | Status")
    print("------+-------+--------------+----------+--------------+--------------")
    for row in rows:
        run = row["run"]
        failed = (
            "n/a" if run["violations_detected"] is None else run["violations_detected"]
        )
        print(
            f"{run['mode']:<6}| "
            f"{'yes' if run['hook_executed'] else 'no':<5}| "
            f"{str(failed):<13}| "
            f"{str(run['mutations_executed']):<9}| "
            f"{run['final_incident']['current_deployment']:<13}| "
            f"{run['final_incident']['incident_status']}"
        )
    print("Evaluator calls are benchmark overhead, excluded from serving metrics.")


def run_demo(args: argparse.Namespace) -> None:
    scenario = load_scenario(SCENARIOS_DIR / f"{args.scenario}.json")
    catalog = discover_skills(SKILLS_DIR)
    modes = ("basic", "hooks") if args.mode == "compare" else (args.mode,)
    pause = pause_callback(args.pause)
    client, model, endpoint = create_client(args.provider, args.model)

    print("\n============================================================")
    print("INCIDENT-RESPONSE HOOKS DEMO")
    print("============================================================")
    print(f"Provider: {args.provider} | Model: {model} | Endpoint: {endpoint}")
    print(f"Scenario: {scenario['scenario_id']}")
    print(f"Skills available: {', '.join(catalog)}")
    print(f"Authenticated role: {scenario['authenticated_user']['role']}")
    print("Permissions are displayed but intentionally not enforced until Module 4.")
    print("\nOPERATOR REQUEST\n" + scenario["request"])
    print("\nINITIAL AUTHORITATIVE INCIDENT STATE")
    print(incident_context(scenario["incident"]))
    print("\nSCRIPTED MUTATION PROPOSALS")
    print(json.dumps(scenario["scripted_mutations"], indent=2))

    rows: list[dict[str, Any]] = []
    for mode in modes:
        print("\n============================================================")
        print(f"MODE: {mode.upper()}")
        print("============================================================")
        run = run_agent(client, model, scenario, mode, catalog, pause=pause)
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
        "A prompt or skill may describe safe behavior, but only harness code at "
        "the execution boundary can deterministically prevent an unsafe tool call."
    )


def main() -> None:
    args = parse_args()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = (
        OUTPUT_DIR
        / f"{args.mode}-{args.scenario}-{args.provider}-{timestamp}.log"
    )
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
