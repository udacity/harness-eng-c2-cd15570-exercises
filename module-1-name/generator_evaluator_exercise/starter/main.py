"""Fill the loop so the harness, rather than the LLM, controls attempts."""

from shared.case import INCIDENT, TASK
from shared.config import get_client, load_settings
from shared.models import Evaluation
from starter.evaluator import evaluate_response
from starter.generator import generate_response


# ========================
# Students should use these harness settings for the loop. The generator and
# evaluator provide work and judgment; Python controls attempts and stopping.
# ========================
MAX_ATTEMPTS = 3
PASS_THRESHOLD = 4.2
CRITERIA = (
    ("Evidence grounding", "evidence_grounding"),
    ("Causal reasoning", "causal_reasoning"),
    ("Completeness", "completeness"),
    ("Uncertainty", "uncertainty"),
    ("Actionability", "actionability"),
)


def calculate_usage(usage: object | None) -> int | None:
    # ========================
    # Usage may be absent. None means the API did not report token counts.
    # ========================
    return getattr(usage, "total_tokens", None)


def print_evaluation(attempt: int, candidate: str, evaluation: Evaluation) -> None:
    # ========================
    # This formatter is ready to use in the loop. It exposes the candidate,
    # five rationales, and harness result for each attempt.
    # ========================
    print("=" * 60)
    print(f"Attempt {attempt}")
    print("=" * 60)
    print("\nGENERATOR RESPONSE")
    print("-" * 60)
    print(candidate)
    print("\nINDEPENDENT EVALUATION")
    print("-" * 60)
    for label, field in CRITERIA:
        criterion = getattr(evaluation, field)
        print(f"{label + ':':22} {criterion.score}/5 — {criterion.rationale}")
    print(f"\nOverall: {evaluation.overall_score:.1f} / 5.0")
    print(f"\nBiggest weakness:\n{evaluation.biggest_weakness}")
    print(f"\nEvaluator feedback:\n{evaluation.feedback}")
    print(f"\nThreshold: {PASS_THRESHOLD:.1f}")
    # ========================
    # A final below-threshold attempt ends the run instead of asking for a
    # revision that the harness cannot make.
    # ========================
    if evaluation.overall_score >= PASS_THRESHOLD:
        result = "PASS"
    elif attempt == MAX_ATTEMPTS:
        result = "MAX ATTEMPTS REACHED"
    else:
        result = "REVISE"
    print(f"Result: {result}")


def run_harness() -> None:
    print("=" * 60)
    print("GENERATOR–EVALUATOR HARNESS (STARTER)")
    print("=" * 60)

    # ========================
    # TODO 3: Load models and client, then loop up to MAX_ATTEMPTS through
    # generate → evaluate → display → threshold check. Make overall_score the
    # exact average of the five evaluator scores. The harness owns stopping.
    # TODO 4: If another attempt is allowed, send the current candidate and
    # evaluation.feedback into the next generator call. Finish by reporting
    # attempts, score change, and any API-reported token totals.
    # ========================
    raise NotImplementedError("TODO 3: implement the harness loop in starter/main.py")


if __name__ == "__main__":
    try:
        run_harness()
    except NotImplementedError as exc:
        print(f"\nStarter incomplete: {exc}")
        print("See starter/README.md for the four student tasks.")
