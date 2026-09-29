"""Build comparable summaries from raw Responses API objects."""

from typing import Any

from harness.models import Attempt, RunResult


def build_result(
    client: Any,
    *,
    mode: str,
    attempts: list[Attempt],
    stop_reason: str,
    accepted: bool | None,
    false_positive_observed: bool = False,
) -> RunResult:
    responses: list[Any] = []
    for attempt in attempts:
        responses.append(attempt.candidate)
        if attempt.self_evaluation is not None:
            responses.append(attempt.self_evaluation)
        if attempt.external_evaluation is not None:
            responses.append(attempt.external_evaluation)

    input_tokens = 0
    output_tokens = 0
    model_seconds = 0.0
    timings = getattr(client, "response_seconds", {})
    for response in responses:
        usage = getattr(response, "usage", None)
        input_tokens += int(getattr(usage, "input_tokens", 0) or 0)
        output_tokens += int(getattr(usage, "output_tokens", 0) or 0)
        model_seconds += float(timings.get(str(response.id), 0.0))

    return RunResult(
        mode=mode,
        attempts=tuple(attempts),
        final_response=str(attempts[-1].candidate.output_text),
        stop_reason=stop_reason,
        accepted=accepted,
        false_positive_observed=false_positive_observed,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        model_seconds=model_seconds,
    )
