"""Run the Module 1 incident-response generator-evaluator demo."""

import argparse
import os
import sys
import traceback
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from harness.loops import run_basic, run_external, run_self
from harness.models import RunResult, Scenario
from harness.providers import LiveProvider, Provider, ScriptedProvider
from harness.run_log import tee_run_output
from harness.scenario import authoritative_context, load_scenario, requirements_context


BASE_DIR = Path(__file__).parent
DEFAULT_SCENARIO = BASE_DIR / "scenarios" / "inc_2048.json"
OUTPUT_DIR = BASE_DIR / "output"
RUNNERS: dict[str, Callable[..., RunResult]] = {
    "basic": run_basic,
    "self": run_self,
    "external": run_external,
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
        "--provider",
        choices=["scripted", "live"],
        default="scripted",
        help="Use deterministic responses or a live model (default: scripted).",
    )
    parser.add_argument(
        "--scenario",
        type=Path,
        default=DEFAULT_SCENARIO,
        help="Path to the incident scenario JSON.",
    )
    parser.add_argument(
        "--model",
        help="Override OPENAI_MODEL for a live run.",
    )
    parser.add_argument(
        "--pause",
        action="store_true",
        help="Wait for Return after every model/evaluation cycle.",
    )
    return parser.parse_args()


def create_provider(kind: str, model_override: str | None) -> tuple[Provider, str, str]:
    if kind == "scripted":
        return ScriptedProvider(), "scripted-fixture", "local"

    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            f"Set OPENAI_API_KEY in {BASE_DIR / '.env'} before using --provider live."
        )
    model = model_override or os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
    base_url = os.getenv(
        "OPENAI_BASE_URL", "https://openai.vocareum.com/v1"
    ).strip()
    return LiveProvider(OpenAI(base_url=base_url, api_key=api_key), model), model, base_url


def pause_callback(enabled: bool) -> Callable[[], None]:
    if not enabled:
        return lambda: None

    def pause() -> None:
        input("\nCycle complete. Press Return to continue...")

    return pause


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
    print("Note: authorization is not enforced until the Module 4 demo.")
    print("\nAUTHORITATIVE INCIDENT FACTS")
    print(authoritative_context(scenario))
    print("\nOPERATOR REQUEST")
    print(scenario.request)
    print("\nRESPONSE REQUIREMENTS")
    print(requirements_context(scenario))


def run_modes(args: argparse.Namespace, scenario: Scenario) -> list[RunResult]:
    modes = ["basic", "self", "external"] if args.mode == "compare" else [args.mode]
    results: list[RunResult] = []
    pause = pause_callback(args.pause)

    for mode in modes:
        provider, model, endpoint = create_provider(args.provider, args.model)
        print("\n============================================================")
        print(f"{mode.upper()} LOOP")
        print("============================================================")
        print(f"Provider: {provider.name}")
        print(f"Model: {model}")
        print(f"Endpoint: {endpoint}")
        result = RUNNERS[mode](provider, scenario, pause=pause)
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
    log_path = OUTPUT_DIR / f"{args.mode}-{args.provider}-{timestamp}.log"
    with tee_run_output(log_path):
        print(f"Run output saved to: {log_path}")
        try:
            scenario = load_scenario(args.scenario)
            print_scenario(scenario)
            results = run_modes(args, scenario)
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
