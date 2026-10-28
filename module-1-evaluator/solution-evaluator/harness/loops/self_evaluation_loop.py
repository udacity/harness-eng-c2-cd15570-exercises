from typing import Any

from openai import OpenAI

from harness.generator import REVISION_INSTRUCTIONS, generate_initial_response
from harness.pauses import pause_after_cycle


# =============================================================================
# Give the model a neutral rubric for reviewing its own response
# =============================================================================
SELF_EVALUATOR_INSTRUCTIONS = """
You are a customer-support quality evaluator. Review the customer response in
this conversation against every supplied criterion.

Return exactly these six lines:
WORD_COUNT: PASS or FAIL
CASE_ID: PASS or FAIL
POLICY_COMPLIANCE: PASS or FAIL
USEFUL_NEXT_STEP: PASS or FAIL
VERDICT: PASS or FAIL
FEEDBACK: one concise explanation of every failure
""".strip()


# =============================================================================
# Validate the self-evaluator's complete decision contract
# =============================================================================
SELF_EVALUATION_CRITERIA = (
    "WORD_COUNT",
    "CASE_ID",
    "POLICY_COMPLIANCE",
    "USEFUL_NEXT_STEP",
)
VALID_DECISIONS = {"PASS", "FAIL"}


def unique_decision(evaluation: str, expected_label: str) -> str | None:
    """Return one exact PASS/FAIL decision; reject missing or duplicate labels."""

    decisions: list[str] = []
    normalized_label = expected_label.strip().upper()
    for line in evaluation.splitlines():
        label, separator, decision = line.partition(":")
        if not separator or label.strip().upper() != normalized_label:
            continue
        normalized_decision = decision.strip().upper()
        if normalized_decision not in VALID_DECISIONS:
            return None
        decisions.append(normalized_decision)
    return decisions[0] if len(decisions) == 1 else None


def passed(evaluation: str) -> bool:
    """Accept only one consistent PASS verdict with four passing criteria."""

    criterion_decisions = [
        unique_decision(evaluation, criterion)
        for criterion in SELF_EVALUATION_CRITERIA
    ]
    verdict = unique_decision(evaluation, "VERDICT")
    return verdict == "PASS" and all(
        decision == "PASS" for decision in criterion_decisions
    )


# =============================================================================
# Evaluate a generated response inside its existing conversation
# =============================================================================
def evaluate_own_response(
    client: OpenAI,
    model: str,
    response: Any,
    refund_policy: str,
    customer_case: str,
    response_requirements: str,
) -> Any:
    return client.responses.create(
        model=model,
        instructions=SELF_EVALUATOR_INSTRUCTIONS,
        previous_response_id=response.id,
        input=f"""
Evaluate your previous customer response against these authoritative inputs.

REFUND POLICY
{refund_policy}

CUSTOMER CASE
{customer_case}

RESPONSE REQUIREMENTS
{response_requirements}
""".strip(),
    )


# =============================================================================
# Generate, self-evaluate, and revise in one shared conversation
# =============================================================================
def run_self_evaluation_loop(
    client: OpenAI,
    model: str,
    refund_policy: str,
    customer_case: str,
    response_requirements: str,
    max_attempts: int = 2,
) -> str:
    response = generate_initial_response(
        client,
        model,
        refund_policy,
        customer_case,
        response_requirements,
    )

    for attempt in range(1, max_attempts + 1):
        print(f"\n---------------- CYCLE {attempt} OF {max_attempts} ----------------")
        print("Stage 1: Generate a customer response")
        print("\nGenerator output:")
        print(response.output_text)

        print("\nStage 2: Evaluate in the same conversation")
        evaluation = evaluate_own_response(
            client,
            model,
            response,
            refund_policy,
            customer_case,
            response_requirements,
        )
        print("\nSelf-evaluator output:")
        print(evaluation.output_text)

        if passed(evaluation.output_text):
            print("\nCycle decision: PASS")
            print("Stop reason: The self-evaluator accepted the response.")
            pause_after_cycle()
            return response.output_text

        print("\nCycle decision: FAIL")
        if attempt == max_attempts:
            print("\nStop reason: The self-evaluation loop reached its cycle limit.")
            pause_after_cycle()
            break

        revision_request = (
            "Revise the customer response using your evaluation. Return "
            "only the revised response."
        )
        print("\nFeedback cycle: Send the self-evaluation back to the generator.")
        print("Next input to the generator:")
        print(revision_request)

        pause_after_cycle()
        response = client.responses.create(
            model=model,
            instructions=REVISION_INSTRUCTIONS,
            previous_response_id=evaluation.id,
            input=revision_request,
        )

    return response.output_text
