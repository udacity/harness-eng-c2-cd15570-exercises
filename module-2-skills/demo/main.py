"""Run the Module 2 incident-response skills demo."""

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
from scenario import build_brief, incident_context, load_incident, load_request


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "incident.json"
REQUESTS_DIR = BASE_DIR / "requests"
SKILLS_DIR = BASE_DIR / "skills"
OUTPUT_DIR = BASE_DIR / "output"
MODEL = "gpt-4.1-mini"
BASE_URL = "https://openai.vocareum.com/v1"


def parse_args() -> argparse.Namespace:
    names = sorted(path.stem for path in REQUESTS_DIR.glob("*.json"))
    parser = argparse.ArgumentParser(
        description="Compare eager context with on-demand incident skills."
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=("basic", "skills", "compare"),
        default="compare",
    )
    parser.add_argument(
        "--request",
        choices=(*names, "all"),
        default="checkout_diagnosis",
        help="Incident request to run (default: checkout_diagnosis).",
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


def percent_change(basic: int | float | None, skills: int | float | None) -> str:
    if basic is None or skills is None or basic == 0:
        return "n/a"
    change = (skills - basic) / basic * 100
    return "0.0%" if change == 0 else f"{change:+.1f}%"


def print_comparison(rows: list[dict]) -> None:
    print("\n================ SERVING CONTEXT, TOKENS, AND TIME ================")
    print(
        "Request              | Mode   | Skill chars | Input | Output | Total | "
        "Seconds | Skills loaded"
    )
    print(
        "---------------------+--------+-------------+-------+--------+-------+"
        "---------+----------------"
    )
    basic_by_request = {
        row["request_id"]: row["run"]
        for row in rows
        if row["run"]["mode"] == "basic"
    }
    for row in rows:
        run = row["run"]
        skills = (
            "(all in prompt)"
            if run["mode"] == "basic"
            else ", ".join(run["loaded_skills"]) or "(none)"
        )
        print(
            f"{row['request_id']:<21}| {run['mode']:<7}| "
            f"{str(run['full_skill_chars']):<12}| {str(run['input_tokens']):<6}| "
            f"{str(run['output_tokens']):<7}| {str(run['total_tokens']):<6}| "
            f"{run['elapsed_seconds']:<8}| {skills}"
        )
        if run["mode"] == "skills" and row["request_id"] in basic_by_request:
            basic = basic_by_request[row["request_id"]]
            print(
                f"{row['request_id']:<21}| {'change':<7}| "
                f"{percent_change(basic['full_skill_chars'], run['full_skill_chars']):<12}| "
                f"{percent_change(basic['input_tokens'], run['input_tokens']):<6}| "
                f"{percent_change(basic['output_tokens'], run['output_tokens']):<7}| "
                f"{percent_change(basic['total_tokens'], run['total_tokens']):<6}| "
                f"{percent_change(basic['elapsed_seconds'], run['elapsed_seconds']):<8}| "
                "(skills vs basic)"
            )
    print("Evaluator calls are experiment overhead and are excluded from this table.")


def run_demo(args: argparse.Namespace) -> None:
    incident = load_incident(DATA_PATH)
    catalog = discover_skills(SKILLS_DIR)
    request_paths = (
        sorted(REQUESTS_DIR.glob("*.json"))
        if args.request == "all"
        else [REQUESTS_DIR / f"{args.request}.json"]
    )
    modes = ("basic", "skills") if args.mode == "compare" else (args.mode,)
    client = create_client()

    print("\n============================================================")
    print("INCIDENT-RESPONSE SKILLS DEMO")
    print("============================================================")
    print(f"Model: {MODEL} | Endpoint: {BASE_URL}")
    print(f"Skills available: {', '.join(catalog)}")
    print("\nAUTHORITATIVE INCIDENT FACTS")
    print(incident_context(incident))

    rows: list[dict] = []
    for path in request_paths:
        request = load_request(path)
        brief = build_brief(incident, request)
        print("\n============================================================")
        print(f"REQUEST: {request.request_id}")
        print("============================================================")
        print(request.request)
        print(f"Expected relevant skills: {', '.join(request.expected_skills)}")

        for mode in modes:
            run = run_agent(
                client,
                MODEL,
                brief,
                mode,
                catalog,
                pause=pause_after_cycle,
            )
            evaluation = evaluate_final_note(
                client, MODEL, incident, request, run["output"]
            )
            selected_as_expected = (
                None
                if mode == "basic"
                else set(run["loaded_skills"]) == set(request.expected_skills)
            )
            print("\nINDEPENDENT EVALUATION")
            print(f"WORD_COUNT: {'PASS' if evaluation['word_count_passed'] else 'FAIL'} ({evaluation['word_count']} words; expected 60)")
            print(f"INCIDENT_ID: {'PASS' if evaluation['incident_id_passed'] else 'FAIL'}")
            print(evaluation["raw_review"])
            print(f"OVERALL: {'PASS' if evaluation['passed'] else 'FAIL'}")
            print(
                "Benchmark overhead: "
                f"{evaluation['benchmark_input_tokens']} input + "
                f"{evaluation['benchmark_output_tokens']} output tokens; "
                f"{evaluation['benchmark_seconds']} seconds."
            )
            if selected_as_expected is not None:
                print(f"Expected skill selection matched: {selected_as_expected}")
            print(
                f"{mode.upper()} SERVING METRICS: {run['input_tokens']} input + "
                f"{run['output_tokens']} output = {run['total_tokens']} tokens; "
                f"{run['elapsed_seconds']} model seconds."
            )
            rows.append(
                {
                    "request_id": request.request_id,
                    "run": run,
                    "evaluation": evaluation,
                    "selected_as_expected": selected_as_expected,
                }
            )

    print_comparison(rows)
    print("\nTeaching takeaway:")
    print(
        "On-demand skills expose a small routing catalog first and return full "
        "instructions only for selected names. That can reduce irrelevant "
        "context, but the extra model cycle can increase latency."
    )


def main() -> None:
    args = parse_args()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = OUTPUT_DIR / f"{args.mode}-{args.request}-{timestamp}.log"
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
