"""Supplied Module 1 evaluation boundary applied to each final note."""

from time import perf_counter
from typing import Any

from scenario import IncidentRequest, incident_context


EVALUATOR_INSTRUCTIONS = """
You are an independent incident-response evaluator. You did not write the
candidate. Judge only the authoritative evidence supplied in this fresh
request. Return exactly these three lines:
FACTUAL_GROUNDING: PASS or FAIL
USEFUL_NEXT_STEP: PASS or FAIL
FEEDBACK: one concise explanation of every failure
""".strip()


def criterion_passed(evaluation: str, criterion: str) -> bool:
    for line in evaluation.splitlines():
        label, separator, decision = line.partition(":")
        if separator and label.strip().upper() == criterion:
            return decision.strip().upper() == "PASS"
    return False


def evaluate_final_note(
    client: Any,
    model: str,
    incident: dict,
    request: IncidentRequest,
    candidate: str,
) -> dict:
    """Combine exact Python checks with a fresh inferential model review."""

    expected_words = 60
    word_count = len(candidate.split())
    word_count_passed = word_count == expected_words
    incident_id_passed = incident["incident_id"] in candidate

    started = perf_counter()
    response = client.responses.create(
        model=model,
        instructions=EVALUATOR_INSTRUCTIONS,
        input=f"""
AUTHORITATIVE INCIDENT FACTS
{incident_context(incident)}

OPERATOR REQUEST
{request.request}

CANDIDATE NOTE
{candidate}
""".strip(),
    )
    seconds = perf_counter() - started
    grounding = criterion_passed(response.output_text, "FACTUAL_GROUNDING")
    next_step = criterion_passed(response.output_text, "USEFUL_NEXT_STEP")
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", None)
    output_tokens = getattr(usage, "output_tokens", None)
    passed = word_count_passed and incident_id_passed and grounding and next_step
    return {
        "passed": passed,
        "word_count": word_count,
        "word_count_passed": word_count_passed,
        "incident_id_passed": incident_id_passed,
        "factual_grounding_passed": grounding,
        "useful_next_step_passed": next_step,
        "raw_review": response.output_text,
        "benchmark_input_tokens": input_tokens,
        "benchmark_output_tokens": output_tokens,
        "benchmark_seconds": round(seconds, 3),
    }
