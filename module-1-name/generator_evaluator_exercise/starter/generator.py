"""TODO 1: make the generator request; TODO 4: use revision feedback."""

from openai import OpenAI


# ========================
# This prompt defines the generator's job: write an analysis for review.
# Keep self-scoring out of the main exercise.
# ========================
GENERATOR_SYSTEM_PROMPT = """You are an incident-analysis assistant.
Reason from the supplied evidence, discuss alternatives and uncertainty, and
recommend useful next steps. Write approximately 400–700 words. Do not score
your own work."""


def generate_response(
    client: OpenAI,
    model: str,
    case: str,
    task: str,
    previous_response: str | None = None,
    evaluator_feedback: str | None = None,
) -> tuple[str, object | None]:
    # ========================
    # Keep the original incident and task on every attempt. Only a revision
    # should add the previous answer and evaluator feedback.
    # ========================
    user_message = f"INCIDENT\n{case}\n\nTASK\n{task}"
    if previous_response is not None:
        user_message += (
            f"\n\nPREVIOUS RESPONSE\n{previous_response}"
            f"\n\nEVALUATOR FEEDBACK\n{evaluator_feedback}"
            "\n\nProduce a revised complete response. Use the feedback where "
            "appropriate, but independently reconsider the incident."
        )

    # ========================
    # TODO 1: Call client.responses.create with the generator system message
    # and user_message. Return the response text and API-reported usage.
    # TODO 4: main.py should pass previous_response and evaluator_feedback
    # only when another generator attempt is allowed.
    # ========================
    raise NotImplementedError("TODO 1: implement the generator model invocation in starter/generator.py")
