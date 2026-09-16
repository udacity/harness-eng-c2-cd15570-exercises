"""The harness owns the generator → evaluator → feedback → generator loop."""

from openai import OpenAIError

from shared.case import INCIDENT, TASK
from shared.config import get_client, load_settings
from shared.models import Evaluation
from solution.evaluator import evaluate_response
from solution.generator import generate_response


# ========================
# These are harness settings. The model can recommend improvements, but only
# this Python loop decides whether a response passes or gets another attempt.
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
    """Return API-reported total tokens, if the response included usage."""
    # ========================
    # Usage is optional in an API response. Returning None lets the console
    # distinguish missing usage from a genuine zero-token report.
    # ========================
    return getattr(usage, "total_tokens", None)


def print_evaluation(attempt: int, candidate: str, evaluation: Evaluation) -> None:
    # ========================
    # Showing the candidate and each criterion rationale makes the independent
    # review visible to students, not just its final number.
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
    # On the final allowed attempt, a below-threshold score means the harness
    # has stopped. It must not announce another revision.
    # ========================
    if evaluation.overall_score >= PASS_THRESHOLD:
        result = "PASS"
    elif attempt == MAX_ATTEMPTS:
        result = "MAX ATTEMPTS REACHED"
    else:
        result = "REVISE"
    print(f"Result: {result}")


def run_harness() -> None:
    # ========================
    # Configuration and client creation happen before the loop. The same SDK
    # client can make separate requests because each request supplies its own
    # prompt and input context.
    # ========================
    generator_model, evaluator_model = load_settings()
    client = get_client()
    print("=" * 60)
    print("GENERATOR–EVALUATOR HARNESS")
    print("=" * 60)

    # ========================
    # These two values are empty on attempt one. They are filled only after a
    # failed review so the next generator call can make a complete revision.
    # ========================
    previous_response = None
    evaluator_feedback = None
    scores: list[float] = []
    generator_tokens = 0
    evaluator_tokens = 0
    generator_usage_seen = False
    evaluator_usage_seen = False

    for attempt in range(1, MAX_ATTEMPTS + 1):
        # ========================
        # Generate first. Attempt one receives the incident and task; later
        # attempts also receive the prior answer and evaluator feedback.
        # ========================
        candidate, generation_usage = generate_response(
            client, generator_model, INCIDENT, TASK,
            previous_response, evaluator_feedback,
        )
        # ========================
        # Evaluate second. This function builds a fresh request containing the
        # original task, incident, and current candidate only.
        # ========================
        evaluation, review_usage = evaluate_response(
            client, evaluator_model, INCIDENT, TASK, candidate
        )

        # ========================
        # The model makes all five inferential quality judgments. Arithmetic
        # only makes their displayed average exact; it adds no quality check.
        # ========================
        evaluation.overall_score = sum(
            getattr(evaluation, field).score for _, field in CRITERIA
        ) / len(CRITERIA)
        scores.append(evaluation.overall_score)
        print_evaluation(attempt, candidate, evaluation)

        # ========================
        # Count tokens separately for generator and evaluator requests so the
        # console shows the usage of both parts of the harness.
        # ========================
        used = calculate_usage(generation_usage)
        if used is not None:
            generator_tokens += used
            generator_usage_seen = True
        used = calculate_usage(review_usage)
        if used is not None:
            evaluator_tokens += used
            evaluator_usage_seen = True

        # ========================
        # The harness owns both stopping conditions. If neither condition is
        # met, it carries this review's feedback into the next generator call.
        # ========================
        if evaluation.overall_score >= PASS_THRESHOLD or attempt == MAX_ATTEMPTS:
            break
        previous_response = candidate
        evaluator_feedback = evaluation.feedback

    # ========================
    # Report the observed score change. An improvement is possible, not
    # guaranteed; the final status reflects the harness's stopping decision.
    # ========================
    print("\nFINAL RESULT")
    print(f"Attempts: {len(scores)}")
    print(f"Initial score: {scores[0]:.1f}")
    print(f"Final score: {scores[-1]:.1f}")
    print(f"Improvement: {scores[-1] - scores[0]:+.1f}")
    print(f"Status: {'PASS' if scores[-1] >= PASS_THRESHOLD else 'MAX ATTEMPTS REACHED'}")
    if generator_usage_seen or evaluator_usage_seen:
        print(f"Generator tokens: {generator_tokens if generator_usage_seen else 'unavailable'}")
        print(f"Evaluator tokens: {evaluator_tokens if evaluator_usage_seen else 'unavailable'}")
        if generator_usage_seen and evaluator_usage_seen:
            print(f"Total tokens: {generator_tokens + evaluator_tokens}")


if __name__ == "__main__":
    try:
        run_harness()
    except (OpenAIError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}")
        raise SystemExit(1) from exc
