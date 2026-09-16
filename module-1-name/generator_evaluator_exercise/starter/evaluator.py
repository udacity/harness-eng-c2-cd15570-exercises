"""TODO 2: make a separate, structured evaluator request."""

from openai import OpenAI

from shared.models import Evaluation


# ========================
# The evaluator reviews a candidate; it does not produce another answer.
# Its prompt asks for evidence-based scores and actionable feedback.
# ========================
EVALUATOR_SYSTEM_PROMPT = """You are an independent reviewer. Inferentially
score the candidate from 1 to 5 on evidence grounding, causal reasoning,
completeness, uncertainty, and actionability. Give a rationale for each score.
Set overall_score to the average. Identify the biggest weakness and offer
specific revision feedback. Do not rewrite the response."""


def evaluate_response(
    client: OpenAI, model: str, case: str, task: str, candidate: str
) -> tuple[Evaluation, object | None]:
    # ========================
    # This input is separate from the generator's conversation. It contains
    # the original incident, task, and current candidate only.
    # ========================
    evaluator_input = [
        {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"INCIDENT\n{case}\n\nORIGINAL TASK\n{task}"
                f"\n\nCANDIDATE RESPONSE\n{candidate}"
            ),
        },
    ]
    # ========================
    # TODO 2: Call client.responses.parse with evaluator_input and
    # text_format=Evaluation. Return the parsed review and reported usage.
    # Do not pass prior feedback or generator conversation state here.
    # ========================
    raise NotImplementedError("TODO 2: implement the independent evaluator invocation in starter/evaluator.py")
