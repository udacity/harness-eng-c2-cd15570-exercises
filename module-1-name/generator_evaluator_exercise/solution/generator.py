"""Produce a complete incident analysis, then revise it when given feedback."""

from openai import OpenAI


# ========================
# The generator's system prompt asks for incident analysis, not a score. Its
# work is to produce a candidate the separate evaluator can review.
# ========================
GENERATOR_SYSTEM_PROMPT = """You are an incident-analysis assistant.
Reason from the supplied evidence, distinguish the immediate failure mechanism
from a possible underlying trigger, and explain meaningful alternatives and
uncertainties. Recommend concrete diagnostic and remediation steps. Write a
complete response of approximately 400–700 words. Do not score your own work."""


def generate_response(
    client: OpenAI,
    model: str,
    case: str,
    task: str,
    previous_response: str | None = None,
    evaluator_feedback: str | None = None,
) -> tuple[str, object | None]:
    # ========================
    # Every attempt includes the original incident and task. The generator
    # gets a fresh request rather than inheriting an evaluator conversation.
    # ========================
    user_message = f"INCIDENT\n{case}\n\nTASK\n{task}"
    # ========================
    # A revision includes both the old answer and actionable feedback. This
    # gives the generator a target for improvement without replacing the task.
    # ========================
    if previous_response is not None:
        user_message += (
            f"\n\nPREVIOUS RESPONSE\n{previous_response}"
            f"\n\nEVALUATOR FEEDBACK\n{evaluator_feedback}"
            "\n\nProduce a revised complete response. Use the evaluator feedback "
            "where appropriate, but independently reconsider the incident "
            "rather than blindly following the evaluator."
        )

    # ========================
    # This is the generation API call. Its system prompt and message list are
    # different from those used by the independent evaluator.
    # ========================
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    candidate = response.output_text
    # ========================
    # A missing text response cannot be sent to the evaluator as a candidate.
    # Keep this as basic API error handling, not an answer-quality check.
    # ========================
    if not candidate:
        raise RuntimeError("The generator returned no text. Check the API response.")
    return candidate, response.usage
