"""Compare same-conversation review with checks outside that conversation."""

import re
from collections.abc import Callable
from typing import Any

from harness.generator import REVISION_INSTRUCTIONS, generate_initial_response
from harness.loops.self_evaluation_loop import (
    criterion_passed,
    evaluate_own_response,
    passed,
)
from harness.models import Attempt, RunResult, Scenario
from harness.results import build_result
from harness.scenario import authoritative_context, requirements_context


EVALUATOR_INSTRUCTIONS = """
You are an independent incident-response evaluator. You did not write the
candidate. Judge only the authoritative evidence supplied in this request.

Return exactly these three lines:
FACTUAL_GROUNDING: PASS or FAIL
USEFUL_NEXT_STEP: PASS or FAIL
FEEDBACK: one concise explanation of every failure
""".strip()


def extract_incident_id(request: str) -> str:
    """Extract the exact INC-#### identifier required by the task."""

    match = re.search(r"\bINC-\d+\b", request)
    if not match:
        raise ValueError("Operator request does not contain an INC-#### identifier.")
    return match.group()


def evaluate_deterministic_criteria(
    candidate: str,
    scenario: Scenario,
) -> tuple[bool, list[str]]:
    """Check exact criteria in Python rather than asking a model."""

    expected_words = int(scenario.response_requirements["required_word_count"])
    expected_id = extract_incident_id(scenario.request)
    word_count = len(candidate.split())
    word_count_passed = word_count == expected_words
    incident_id_passed = expected_id in candidate
    results = [
        (
            f"WORD_COUNT: {'PASS' if word_count_passed else 'FAIL'} "
            f"({word_count} words; expected exactly {expected_words})"
        ),
        (
            f"INCIDENT_ID: {'PASS' if incident_id_passed else 'FAIL'} "
            f"(expected {expected_id})"
        ),
    ]
    return word_count_passed and incident_id_passed, results


def deterministic_criterion_passed(results: list[str], criterion: str) -> bool:
    return any(result.startswith(f"{criterion}: PASS") for result in results)


def inferential_criterion_passed(evaluation: str, criterion: str) -> bool:
    for line in evaluation.splitlines():
        label, separator, decision = line.partition(":")
        if separator and label.strip().upper() == criterion:
            return decision.strip().upper() == "PASS"
    return False


def evaluator_feedback(evaluation: str) -> str:
    for line in evaluation.splitlines():
        label, separator, feedback = line.partition(":")
        if separator and label.strip().upper() == "FEEDBACK" and feedback.strip():
            return feedback.strip()
    return "The independent evaluator returned malformed or missing feedback."


def evaluate_inferential_criteria(
    client: Any,
    model: str,
    scenario: Scenario,
    candidate: str,
) -> tuple[bool, Any]:
    """Start a fresh evaluator conversation for judgment-based criteria."""

    evaluation = client.responses.create(
        model=model,
        instructions=EVALUATOR_INSTRUCTIONS,
        input=f"""
AUTHORITATIVE INCIDENT FACTS
{authoritative_context(scenario)}

RESPONSE REQUIREMENTS
{requirements_context(scenario)}

CANDIDATE UPDATE
{candidate}
""".strip(),
    )
    inferential_passed = inferential_criterion_passed(
        evaluation.output_text, "FACTUAL_GROUNDING"
    ) and inferential_criterion_passed(
        evaluation.output_text, "USEFUL_NEXT_STEP"
    )
    return inferential_passed, evaluation


def run_external_evaluation_loop(
    client: Any,
    model: str,
    scenario: Scenario,
    *,
    max_attempts: int = 3,
    emit: Callable[[str], None] = print,
    pause: Callable[[], None] = lambda: None,
) -> RunResult:
    """Evaluate the same candidate on both paths and revise from external feedback."""

    response = generate_initial_response(client, model, scenario)
    attempts: list[Attempt] = []
    false_positive_observed = False

    for number in range(1, max_attempts + 1):
        candidate = response.output_text
        emit(f"\n---------------- CYCLE {number} OF {max_attempts} ----------------")
        emit("Initial generation: previous_response_id=NONE" if number == 1 else "Revised candidate received")
        emit("\nGenerator output:")
        emit(candidate)

        emit(f"\nSelf-review call: previous_response_id={response.id}")
        self_evaluation = evaluate_own_response(client, model, response, scenario)
        self_passed = passed(self_evaluation.output_text)
        emit("\nSelf-evaluator output:")
        emit(self_evaluation.output_text)

        deterministic_passed, deterministic_results = evaluate_deterministic_criteria(
            candidate, scenario
        )
        emit("\nDeterministic Python checks:")
        for result in deterministic_results:
            emit(result)

        emit("\nExternal review call: previous_response_id=NONE (fresh conversation)")
        inferential_passed, external_evaluation = evaluate_inferential_criteria(
            client, model, scenario, candidate
        )
        emit("\nIndependent evaluator output:")
        emit(external_evaluation.output_text)

        independent_passed = deterministic_passed and inferential_passed
        attempts.append(
            Attempt(
                number=number,
                candidate=response,
                self_evaluation=self_evaluation,
                deterministic_results=deterministic_results,
                external_evaluation=external_evaluation,
                independent_passed=independent_passed,
            )
        )

        independent = {
            "WORD_COUNT": deterministic_criterion_passed(
                deterministic_results, "WORD_COUNT"
            ),
            "INCIDENT_ID": deterministic_criterion_passed(
                deterministic_results, "INCIDENT_ID"
            ),
            "FACTUAL_GROUNDING": inferential_criterion_passed(
                external_evaluation.output_text, "FACTUAL_GROUNDING"
            ),
            "USEFUL_NEXT_STEP": inferential_criterion_passed(
                external_evaluation.output_text, "USEFUL_NEXT_STEP"
            ),
        }
        emit("\nCriteria comparison for this candidate:")
        emit("Criterion          | Self | Independent")
        emit("-------------------+------+------------")
        for criterion, independent_result in independent.items():
            self_result = criterion_passed(self_evaluation.output_text, criterion)
            self_label = "PASS" if self_result else "FAIL"
            independent_label = "PASS" if independent_result else "FAIL"
            emit(f"{criterion:<19}| {self_label:<5}| {independent_label}")

        if self_passed and not independent_passed:
            false_positive_observed = True
            emit("FALSE POSITIVE OBSERVED: self-evaluation accepted a flawed update.")
        elif self_passed and independent_passed:
            emit("AGREEMENT: both evaluation paths accepted this update.")
        elif not self_passed and not independent_passed:
            emit("AGREEMENT: both evaluation paths found a problem.")
        else:
            emit("DISAGREEMENT: self-evaluation rejected an independently passing update.")

        if independent_passed:
            emit("Stop reason: every independent criterion passed.")
            pause()
            return build_result(
                client,
                mode="external",
                attempts=attempts,
                stop_reason="all independent criteria passed",
                accepted=True,
                false_positive_observed=false_positive_observed,
            )

        if number == max_attempts:
            emit("Stop reason: the independent-evaluation attempt limit was reached.")
            pause()
            return build_result(
                client,
                mode="external",
                attempts=attempts,
                stop_reason="independent-evaluation attempt limit reached",
                accepted=False,
                false_positive_observed=false_positive_observed,
            )

        feedback = "\n".join(
            deterministic_results + [evaluator_feedback(external_evaluation.output_text)]
        )
        emit("\nIndependent feedback sent to the generator:")
        emit(feedback)
        emit(f"External revision call: previous_response_id={response.id}")
        pause()
        response = client.responses.create(
            model=model,
            instructions=REVISION_INSTRUCTIONS,
            previous_response_id=response.id,
            input=f"""
Revise the previous incident update so every criterion passes.

INDEPENDENT EVALUATION FEEDBACK
{feedback}

Return only the revised incident update.
""".strip(),
        )

    raise AssertionError("external-evaluation loop exited unexpectedly")
