"""Review only the incident, original task, and current candidate."""

from openai import OpenAI

from shared.models import Evaluation


# ========================
# The evaluator has its own reviewer prompt. It scores reasoning and evidence
# inferentially and gives feedback without writing a replacement answer.
# ========================
EVALUATOR_SYSTEM_PROMPT = """You are an independent reviewer of a software
incident analysis. Evaluate the candidate inferentially on five criteria,
scoring each from 1 to 5 and giving a short evidence-based rationale:

1. Evidence grounding: use of incident facts rather than unsupported claims.
2. Causal reasoning: symptoms versus contributing factors and likely root
   causes, especially retries, connection growth, timeouts, and latency.
3. Completeness: important evidence and plausible competing explanations.
4. Handling of uncertainty: supported claims versus unconfirmed hypotheses.
5. Actionability: useful diagnostics and remediation tied to the suspected cause.

Set overall_score to the average of the five scores. Name the biggest weakness
and give specific feedback the author can use on a new attempt. Do not rewrite
the candidate. Judge the response you receive, not a previous review."""


def evaluate_response(
    client: OpenAI, model: str, case: str, task: str, candidate: str
) -> tuple[Evaluation, object | None]:
    # ========================
    # This is a separate API invocation with a fresh context. It sees the
    # incident, original task, and current candidate, but no generator prompt
    # or prior evaluator feedback. The underlying model may still be the same.
    # ========================
    response = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"INCIDENT\n{case}\n\nORIGINAL TASK\n{task}"
                    f"\n\nCANDIDATE RESPONSE\n{candidate}"
                ),
            },
        ],
        text_format=Evaluation,
    )
    # ========================
    # The SDK parses the response into the shared Pydantic model. The harness
    # receives criterion scores and feedback as one structured review.
    # ========================
    evaluation = response.output_parsed
    if evaluation is None:
        raise RuntimeError("The evaluator returned no structured review. Check the API response.")
    return evaluation, response.usage
