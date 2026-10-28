"""Supplied Module 1 evaluation boundary applied to each final note."""

import json
import re
from time import perf_counter
from typing import Any


EVALUATOR_INSTRUCTIONS = """
You are an independent incident-response evaluator. You did not write the
candidate. Judge only the authoritative final state and execution evidence in
this fresh request. Return exactly these three lines:
FACTUAL_GROUNDING: PASS or FAIL
USEFUL_NEXT_STEP: PASS or FAIL
FEEDBACK: one concise explanation of every failure
""".strip()


VALID_DECISIONS = {"PASS", "FAIL"}


def unique_decision(evaluation: str, expected_criterion: str) -> str | None:
    """Return one exact decision; reject missing, malformed, or duplicate lines."""

    decisions: list[str] = []
    normalized_criterion = expected_criterion.strip().upper()
    for line in evaluation.splitlines():
        label, separator, decision = line.partition(":")
        if not separator or label.strip().upper() != normalized_criterion:
            continue
        normalized_decision = decision.strip().upper()
        if normalized_decision not in VALID_DECISIONS:
            return None
        decisions.append(normalized_decision)
    return decisions[0] if len(decisions) == 1 else None


def criterion_passed(evaluation: str, criterion: str) -> bool:
    return unique_decision(evaluation, criterion) == "PASS"


def contains_exact_incident_id(candidate: str, expected_id: str) -> bool:
    """Match one complete INC-#### token rather than a longer identifier."""

    pattern = (
        rf"(?<![A-Za-z0-9_-]){re.escape(expected_id)}"
        r"(?![A-Za-z0-9_-])"
    )
    return re.search(pattern, candidate) is not None


def evaluate_final_note(
    client: Any,
    model: str,
    incident: dict[str, Any],
    events: list[dict[str, Any]],
    candidate: str,
) -> dict[str, Any]:
    """Combine exact Python checks with a fresh inferential model review."""

    word_count = len(candidate.split())
    word_count_passed = word_count == 60
    incident_id_passed = contains_exact_incident_id(
        candidate, str(incident["incident_id"])
    )

    started = perf_counter()
    response = client.responses.create(
        model=model,
        instructions=EVALUATOR_INSTRUCTIONS,
        input=(
            "AUTHORITATIVE FINAL INCIDENT STATE\n"
            + json.dumps(incident, indent=2)
            + "\n\nEXECUTION EVIDENCE\n"
            + json.dumps(events, indent=2)
            + "\n\nCANDIDATE NOTE\n"
            + candidate
        ),
    )
    seconds = perf_counter() - started
    grounding = criterion_passed(response.output_text, "FACTUAL_GROUNDING")
    next_step = criterion_passed(response.output_text, "USEFUL_NEXT_STEP")
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", None)
    output_tokens = getattr(usage, "output_tokens", None)
    return {
        "passed": (
            word_count_passed and incident_id_passed and grounding and next_step
        ),
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
