"""Review and revise an incident update inside the generator conversation."""

from collections.abc import Callable
from typing import Any

from harness.generator import REVISION_INSTRUCTIONS, generate_initial_response
from harness.models import Attempt, RunResult, Scenario
from harness.results import build_result
from harness.scenario import authoritative_context, requirements_context


SELF_EVALUATOR_INSTRUCTIONS = """
Review the incident update you just wrote against the authoritative facts and
all response requirements. You are evaluating your own response in the same
conversation.

Return exactly these six lines:
WORD_COUNT: PASS or FAIL
INCIDENT_ID: PASS or FAIL
FACTUAL_GROUNDING: PASS or FAIL
USEFUL_NEXT_STEP: PASS or FAIL
VERDICT: PASS or FAIL
FEEDBACK: one concise explanation of every failure
""".strip()


def passed(evaluation: str) -> bool:
    """Trust only an explicit `VERDICT: PASS`; missing output fails closed."""

    for line in evaluation.splitlines():
        label, separator, decision = line.partition(":")
        if separator and label.strip().upper() == "VERDICT":
            return decision.strip().upper() == "PASS"
    return False


def criterion_passed(evaluation: str, criterion: str) -> bool:
    """Read one exact named decision without matching PASS in feedback."""

    for line in evaluation.splitlines():
        label, separator, decision = line.partition(":")
        if separator and label.strip().upper() == criterion:
            return decision.strip().upper() == "PASS"
    return False


def evaluate_own_response(
    client: Any,
    model: str,
    response: Any,
    scenario: Scenario,
) -> Any:
    """Continue from the candidate so the generator reviews its own work."""

    return client.responses.create(
        model=model,
        instructions=SELF_EVALUATOR_INSTRUCTIONS,
        previous_response_id=response.id,
        input=f"""
Evaluate your previous update against these authoritative inputs.

AUTHORITATIVE INCIDENT FACTS
{authoritative_context(scenario)}

RESPONSE REQUIREMENTS
{requirements_context(scenario)}
""".strip(),
    )


def run_self_evaluation_loop(
    client: Any,
    model: str,
    scenario: Scenario,
    *,
    max_attempts: int = 2,
    emit: Callable[[str], None] = print,
    pause: Callable[[], None] = lambda: None,
) -> RunResult:
    """Stop on self PASS or revise through at most two attempts."""

    response = generate_initial_response(client, model, scenario)
    attempts: list[Attempt] = []

    for number in range(1, max_attempts + 1):
        emit(f"\n---------------- CYCLE {number} OF {max_attempts} ----------------")
        emit("Initial generation: previous_response_id=NONE" if number == 1 else "Revised candidate received")
        emit("\nGenerator output:")
        emit(response.output_text)

        emit(f"\nSelf-review call: previous_response_id={response.id}")
        evaluation = evaluate_own_response(client, model, response, scenario)
        attempts.append(
            Attempt(
                number=number,
                candidate=response,
                self_evaluation=evaluation,
            )
        )
        emit("\nSelf-evaluator output:")
        emit(evaluation.output_text)

        if passed(evaluation.output_text):
            emit("Self-evaluator verdict: PASS")
            emit("Stop reason: the self-evaluator accepted its own response.")
            pause()
            return build_result(
                client,
                mode="self",
                attempts=attempts,
                stop_reason="self-evaluator returned PASS",
                accepted=True,
            )

        emit("Self-evaluator verdict: FAIL")
        if number == max_attempts:
            emit("Stop reason: the self-evaluation attempt limit was reached.")
            pause()
            return build_result(
                client,
                mode="self",
                attempts=attempts,
                stop_reason="self-evaluation attempt limit reached",
                accepted=False,
            )

        emit(f"Self revision call: previous_response_id={evaluation.id}")
        pause()
        response = client.responses.create(
            model=model,
            instructions=REVISION_INSTRUCTIONS,
            previous_response_id=evaluation.id,
            input=(
                "Revise the incident update using your evaluation. Return only "
                "the revised incident update."
            ),
        )

    raise AssertionError("self-evaluation loop exited unexpectedly")
