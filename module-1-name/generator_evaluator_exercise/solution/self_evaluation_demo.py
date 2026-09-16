"""Optional comparison: self-review in the generator context vs fresh review."""

from openai import OpenAIError
from pydantic import BaseModel

from shared.case import INCIDENT, TASK
from shared.config import get_client, load_settings
from solution.evaluator import evaluate_response
from solution.generator import GENERATOR_SYSTEM_PROMPT


# ========================
# The optional demo needs only one self-assigned average and a rationale.
# It does not use self-review as the main harness evaluator.
# ========================
class SelfScore(BaseModel):
    score: float
    rationale: str


def main() -> None:
    generator_model, evaluator_model = load_settings()
    client = get_client()

    # ========================
    # Produce one original answer. Both reviews below judge this same text so
    # any score difference comes from their evaluation contexts.
    # ========================
    original = client.responses.create(
        model=generator_model,
        input=[
            {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
            {"role": "user", "content": f"INCIDENT\n{INCIDENT}\n\nTASK\n{TASK}"},
        ],
    )
    candidate = original.output_text
    if not candidate:
        raise RuntimeError("The generator returned no text. Check the API response.")

    # ========================
    # previous_response_id keeps the self-review in the generator's own
    # conversation, including the answer it just produced.
    # ========================
    self_review = client.responses.parse(
        model=generator_model,
        previous_response_id=original.id,
        input=[
            {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Evaluate the incident analysis you just wrote on evidence "
                    "grounding, causal reasoning, completeness, uncertainty, "
                    "and actionability. Give a self-assigned average score from "
                    "1 to 5 and a brief rationale."
                ),
            },
        ],
        text_format=SelfScore,
    )
    if self_review.output_parsed is None:
        raise RuntimeError("The self-review returned no structured score.")

    # ========================
    # The independent reviewer gets a new request with only the case, task,
    # and original candidate. It does not see the self-assigned score.
    # ========================
    independent, _ = evaluate_response(
        client, evaluator_model, INCIDENT, TASK, candidate
    )
    independent.overall_score = sum(
        criterion.score for criterion in (
            independent.evidence_grounding,
            independent.causal_reasoning,
            independent.completeness,
            independent.uncertainty,
            independent.actionability,
        )
    ) / 5

    # ========================
    # Print both scores for comparison. A mismatch is informative, but the
    # structural lesson holds even when the scores happen to agree.
    # ========================
    print("SELF-EVALUATION COMPARISON")
    print("\nOriginal generator response:\n")
    print(candidate)
    print(f"\nSelf-assigned score: {self_review.output_parsed.score:.1f} / 5.0")
    print(f"Self-review rationale: {self_review.output_parsed.rationale}")
    print(f"\nIndependent evaluator score: {independent.overall_score:.1f} / 5.0")
    print(f"Independent evaluator feedback: {independent.feedback}")


if __name__ == "__main__":
    try:
        main()
    except (OpenAIError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}")
        raise SystemExit(1) from exc
