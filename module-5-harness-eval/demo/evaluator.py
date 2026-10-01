"""Online critic, text-only revision, and blind offline judge."""

import json
from dataclasses import dataclass
from time import perf_counter
from typing import Any


ONLINE_INSTRUCTIONS = """You are an online incident-response critic. Score the
candidate using only production-available request and tool evidence. Return one
JSON object with integer fields correctness, clarity, next_step, claim_support,
tool_consistency from 1 through 5, plus nonempty notes. Do not revise."""

BLIND_INSTRUCTIONS = """You are a blind offline incident-response judge. The
harness configuration is withheld. Score the final response against the task
expectation and confirmed trace. Return one JSON object with integer fields
correctness, clarity, next_step, claim_support, tool_consistency from 1 through
5, plus nonempty notes. Do not revise or execute tools."""

REVISION_INSTRUCTIONS = """You revise an incident-response response from an
independent critic's feedback. This is text only: you have no tools and cannot
perform, reverse, retry, or confirm actions. Preserve tool outcomes exactly.
Return only the revised response."""


@dataclass(frozen=True)
class Score:
    correctness: int
    clarity: int
    next_step: int
    claim_support: int
    tool_consistency: int
    overall: float
    notes: str


def _metrics(response: Any, seconds: float, purpose: str) -> dict[str, Any]:
    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", None)
    output_tokens = getattr(usage, "output_tokens", None)
    total_tokens = getattr(usage, "total_tokens", None)
    if total_tokens is None and isinstance(input_tokens, int) and isinstance(output_tokens, int):
        total_tokens = input_tokens + output_tokens
    return {
        "purpose": purpose,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "model_seconds": round(seconds, 3),
    }


def parse_score(text: str) -> Score:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"Evaluator output is not JSON: {error}") from error
    fields = (
        "correctness",
        "clarity",
        "next_step",
        "claim_support",
        "tool_consistency",
    )
    if not isinstance(value, dict) or any(
        type(value.get(field)) is not int or not 1 <= value[field] <= 5
        for field in fields
    ):
        raise ValueError("Evaluator scores must be integers from 1 through 5.")
    notes = value.get("notes")
    if not isinstance(notes, str) or not notes.strip():
        raise ValueError("Evaluator notes must be nonempty.")
    scores = [value[field] for field in fields]
    return Score(
        **{field: value[field] for field in fields},
        overall=sum(scores) / len(scores),
        notes=notes.strip(),
    )


def evaluate_response(
    client: Any,
    model: str,
    *,
    candidate: str,
    request: str,
    trace: list[dict[str, Any]],
    expected_behavior: str,
    blind: bool,
) -> tuple[Score | None, dict[str, Any], str | None]:
    instructions = BLIND_INSTRUCTIONS if blind else ONLINE_INSTRUCTIONS
    started = perf_counter()
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=(
            f"REQUEST\n{request}\n\nEXPECTED BEHAVIOR\n{expected_behavior}"
            f"\n\nCANDIDATE RESPONSE\n{candidate}"
            f"\n\nCONFIRMED TOOL TRACE\n{json.dumps(trace, indent=2)}"
        ),
    )
    metric = _metrics(
        response,
        perf_counter() - started,
        "benchmark_judge" if blind else "online_evaluator",
    )
    try:
        return parse_score(response.output_text), metric, None
    except ValueError as error:
        return None, metric, str(error)


def revise_response_once(
    client: Any,
    model: str,
    *,
    candidate: str,
    request: str,
    trace: list[dict[str, Any]],
    score: Score,
) -> tuple[str, dict[str, Any]]:
    started = perf_counter()
    response = client.responses.create(
        model=model,
        instructions=REVISION_INSTRUCTIONS,
        input=(
            f"REQUEST\n{request}\n\nCANDIDATE RESPONSE\n{candidate}"
            f"\n\nCRITIC SCORE\n{score.overall}/5: {score.notes}"
            f"\n\nIMMUTABLE TOOL TRACE\n{json.dumps(trace, indent=2)}"
        ),
    )
    text = response.output_text.strip()
    if not text:
        raise ValueError("Revision returned empty text.")
    return text, _metrics(response, perf_counter() - started, "revision")
