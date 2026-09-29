"""A fixed two-cycle loop with no quality judgment."""

from collections.abc import Callable
from typing import Any

from harness.generator import GENERATOR_INSTRUCTIONS, generate_initial_response
from harness.models import Attempt, RunResult, Scenario
from harness.results import build_result


def run_basic_loop(
    client: Any,
    model: str,
    scenario: Scenario,
    *,
    emit: Callable[[str], None] = print,
    pause: Callable[[], None] = lambda: None,
) -> RunResult:
    """Generate, request a clearer version, and stop without evaluating it."""

    first = generate_initial_response(client, model, scenario)
    attempts = [Attempt(number=1, candidate=first)]
    emit("\n---------------- CYCLE 1 OF 2 ----------------")
    emit("Initial generation: previous_response_id=NONE")
    emit("\nGenerator output:")
    emit(first.output_text)
    emit("Evaluation: NOT PERFORMED")
    pause()

    emit(f"\nClarifying revision: previous_response_id={first.id}")
    second = client.responses.create(
        model=model,
        instructions=GENERATOR_INSTRUCTIONS,
        previous_response_id=first.id,
        input=(
            "Rewrite your previous incident update so it is clearer and more "
            "concise. Return only the revised update."
        ),
    )
    attempts.append(Attempt(number=2, candidate=second))
    emit("\n---------------- CYCLE 2 OF 2 ----------------")
    emit("\nGenerator output:")
    emit(second.output_text)
    emit("Evaluation: NOT PERFORMED")
    emit("Stop reason: fixed two-cycle limit; this is not evidence of quality.")
    pause()

    return build_result(
        client,
        mode="basic",
        attempts=attempts,
        stop_reason="fixed cycle limit reached without evaluation",
        accepted=None,
    )
