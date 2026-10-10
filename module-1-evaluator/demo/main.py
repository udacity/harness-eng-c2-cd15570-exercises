"""Run the Module 1 incident-response generator-evaluator demo."""

import argparse
import os
import sys
import traceback
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from harness.clients import TimedClient
from harness.loops.basic_loop import run_basic_loop
from harness.loops.external_evaluation_loop import run_external_evaluation_loop
from harness.loops.self_evaluation_loop import run_self_evaluation_loop
from harness.models import RunResult, Scenario
from harness.pauses import pause_after_cycle, pause_after_loop_start
from harness.run_log import tee_run_output
from harness.scenario import authoritative_context, load_scenario, requirements_context


BASE_DIR = Path(__file__).parent
DEFAULT_SCENARIO = BASE_DIR / "scenarios" / "inc_2048.json"
OUTPUT_DIR = BASE_DIR / "output"
RUNNERS: dict[str, Callable[..., RunResult]] = {
    "basic": run_basic_loop,
    "self": run_self_evaluation_loop,
    "external": run_external_evaluation_loop,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare evaluator boundaries on the INC-2048 response task."
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="compare",
        choices=["basic", "self", "external", "compare"],
        help="Loop to run; compare runs all three in order (default: compare).",
    )
    parser.add_argument(
        "--scenario",
        type=Path,
        default=DEFAULT_SCENARIO,
        help="Path to the incident scenario JSON.",
    )
    parser.add_argument(
        "--model",
        help="Override OPENAI_MODEL for this run.",
    )
    return parser.parse_args()


def create_llm_client(model_override: str | None) -> tuple[Any, str, str]:
    """Create the same Vocareum OpenAI client used by the Module 1 solution."""
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            f"Set OPENAI_API_KEY in {BASE_DIR / '.env'} before running the demo."
        )
    model = model_override or os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
    base_url = "https://openai.vocareum.com/v1"
    client = TimedClient(OpenAI(base_url=base_url, api_key=api_key))
    return client, model, base_url


def print_scenario(scenario: Scenario) -> None:
    user = scenario.authenticated_user
    print("\n============================================================")
    print("INCIDENT-RESPONSE GENERATOR–EVALUATOR DEMO")
    print("============================================================")
    print(f"Scenario: {scenario.scenario_id}")
    print(
        "Trusted user context: "
        f"{user['name']} ({user['user_id']}), role={user['role']}"
    )
    print("\nAUTHORITATIVE INCIDENT FACTS")
    print(authoritative_context(scenario))
    print("\nOPERATOR REQUEST")
    print(scenario.request)
    print("\nRESPONSE REQUIREMENTS")
    print(requirements_context(scenario))


def run_modes(
    args: argparse.Namespace,
    scenario: Scenario,
    client: Any,
    model: str,
    endpoint: str,
) -> list[RunResult]:
    modes = ["basic", "self", "external"] if args.mode == "compare" else [args.mode]
    results: list[RunResult] = []

    for mode in modes:
        print("\n============================================================")
        print(f"{mode.upper()} LOOP")
        print("============================================================")
        print(f"Model: {model}")
        print(f"API endpoint: {endpoint}")
        pause_after_loop_start(mode)
        result = RUNNERS[mode](client, model, scenario, pause=pause_after_cycle)
        results.append(result)
        print("\nRUN SUMMARY")
        print(f"Attempts: {len(result.attempts)}")
        print(f"Accepted: {result.accepted if result.accepted is not None else 'NOT CHECKED'}")
        print(f"Stop reason: {result.stop_reason}")
        false_positive = (
            str(result.false_positive_observed)
            if result.mode == "external"
            else "NOT MEASURED"
        )
        print(f"Self-evaluation false positive observed: {false_positive}")
        print(f"Input tokens: {result.input_tokens}")
        print(f"Output tokens: {result.output_tokens}")
        print(f"Total tokens: {result.total_tokens}")
        print(f"Model seconds: {result.model_seconds:.3f}")

    return results


def print_comparison(results: list[RunResult]) -> None:
    if len(results) < 2:
        return
    print("\n============================================================")
    print("MODE COMPARISON")
    print("============================================================")
    print("Mode      | Attempts | Decision     | False positive | Tokens | Seconds")
    print("----------+----------+--------------+----------------+--------+--------")
    for result in results:
        if result.accepted is None:
            decision = "NOT CHECKED"
        else:
            decision = "PASS" if result.accepted else "FAIL"
        false_positive = (
            "YES" if result.false_positive_observed else "NO"
        ) if result.mode == "external" else "NOT MEASURED"
        print(
            f"{result.mode:<10}| {len(result.attempts):<9}| {decision:<13}| "
            f"{false_positive:<15}| {result.total_tokens:<7}| "
            f"{result.model_seconds:.3f}"
        )
    print("\nTeaching takeaway:")
    print(
        "A stopping condition is only as trustworthy as the evaluator behind it. "
        "Independent deterministic and inferential checks can catch errors that "
        "same-conversation self-review accepts."
    )


def main() -> None:
    args = parse_args()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = OUTPUT_DIR / f"{args.mode}-live-{timestamp}.log"
    with tee_run_output(log_path):
        print(f"Run output saved to: {log_path}")
        try:
            scenario = load_scenario(args.scenario)
            client, model, endpoint = create_llm_client(args.model)
            print_scenario(scenario)
            results = run_modes(args, scenario, client, model, endpoint)
            print_comparison(results)
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
