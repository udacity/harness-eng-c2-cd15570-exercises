import argparse
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from harness.loops.basic_loop import run_basic_loop
from harness.loops.external_evaluation_loop import run_external_evaluation_loop
from harness.loops.self_evaluation_loop import run_self_evaluation_loop
from harness.pauses import pause_after_case
from harness.run_log import tee_run_output


# =============================================================================
# Define the location of the exercise data
# =============================================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REFERENCE_DIR = DATA_DIR / "reference"
OUTPUT_DIR = BASE_DIR / "output"


# =============================================================================
# Map each CLI argument to its harness loop
# =============================================================================
LOOPS = {
    "basic": run_basic_loop,
    "self": run_self_evaluation_loop,
    "external": run_external_evaluation_loop,
}


# =============================================================================
# Load LLM settings from .env and create the Vocareum OpenAI client
# =============================================================================
def create_llm_client() -> tuple[OpenAI, str, str]:
    load_dotenv(BASE_DIR / ".env")

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            f"Set OPENAI_API_KEY in {BASE_DIR / '.env'} before running the harness."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    base_url = "https://openai.vocareum.com/v1"
    client = OpenAI(base_url=base_url, api_key=api_key)
    return client, model, base_url


# =============================================================================
# Load one policy or requirements document from the reference folder
# =============================================================================
def load_document(filename: str) -> str:
    return (REFERENCE_DIR / filename).read_text(encoding="utf-8")


# =============================================================================
# Load every customer case from the cases folder
# =============================================================================
def load_customer_cases() -> list[tuple[str, str]]:
    case_paths = sorted((DATA_DIR / "cases").glob("*.md"))
    return [
        (path.stem.replace("_", " ").title(), path.read_text(encoding="utf-8"))
        for path in case_paths
    ]


# =============================================================================
# Read the loop selected on the command line
# =============================================================================
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one stage of the generator-evaluator harness."
    )
    parser.add_argument(
        "loop",
        choices=LOOPS,
        help="Harness loop to run: basic, self, or external.",
    )
    return parser.parse_args()


# =============================================================================
# Create the shared resources and run the selected loop
# =============================================================================
def run_selected_loop(args: argparse.Namespace) -> None:
    client, model, base_url = create_llm_client()
    refund_policy = load_document("refund_policy.md")
    customer_cases = load_customer_cases()
    response_requirements = load_document("response_requirements.md")

    print("\n============================================================")
    print("GENERATOR-EVALUATOR HARNESS")
    print("============================================================")
    print(f"Selected loop: {args.loop}")
    print(f"Model: {model}")
    print(f"API endpoint: {base_url}")

    print("\n==================== REFUND POLICY ====================")
    print(refund_policy)

    print("\n================ RESPONSE REQUIREMENTS ================")
    print(response_requirements)

    print(f"\n==================== {args.loop.upper()} LOOP ====================")
    selected_loop = LOOPS[args.loop]
    false_positive_count = 0

    for case_number, (case_name, customer_case) in enumerate(customer_cases, start=1):
        print("\n============================================================")
        print(f"CASE {case_number} OF {len(customer_cases)}: {case_name}")
        print("============================================================")
        print(customer_case)

        result = selected_loop(
            client,
            model,
            refund_policy,
            customer_case,
            response_requirements,
        )

        if args.loop == "external":
            _, false_positive_observed = result
            false_positive_count += int(false_positive_observed)

        pause_after_case(case_number, len(customer_cases))

    print("\n============================================================")
    print(f"COMPLETED {len(customer_cases)} CUSTOMER CASES")
    if args.loop == "external":
        print(
            "Cases with an observed self-evaluation false positive: "
            f"{false_positive_count} of {len(customer_cases)}"
        )
        if false_positive_count == 0:
            print("No self-evaluation false positive was reproduced in this run.")
    print("============================================================")


def main() -> None:
    args = parse_args()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    log_path = OUTPUT_DIR / f"{args.loop}-{timestamp}.log"

    with tee_run_output(log_path):
        print(f"Run output saved to: {log_path}")
        try:
            run_selected_loop(args)
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
