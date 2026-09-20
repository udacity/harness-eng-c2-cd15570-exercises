import re

from openai import OpenAI

from harness.generator import REVISION_INSTRUCTIONS, generate_initial_response
from harness.loops.self_evaluation_loop import evaluate_own_response, passed
from harness.pauses import pause_after_cycle


# =============================================================================
# Give the independent evaluator its own role and decision format
# =============================================================================
EVALUATOR_INSTRUCTIONS = """
You are an independent customer-support quality evaluator. You did not write
the candidate response. Judge only the evidence supplied in this request.

Return exactly these three lines:
POLICY_COMPLIANCE: PASS or FAIL
USEFUL_NEXT_STEP: PASS or FAIL
FEEDBACK: one concise explanation of every inferential failure
""".strip()

REQUIRED_WORD_COUNT = 100


# =============================================================================
# Check the two criteria that do not require model judgment
# =============================================================================
def extract_case_id(customer_case: str) -> str:
    case_id_match = re.search(r"\bCASE-\d+\b", customer_case)
    if not case_id_match:
        raise ValueError("Customer case does not contain a CASE-#### identifier.")
    return case_id_match.group()


def evaluate_deterministic_criteria(
    candidate: str,
    customer_case: str,
) -> tuple[bool, list[str]]:
    word_count = len(candidate.split())
    expected_case_id = extract_case_id(customer_case)
    length_passed = word_count == REQUIRED_WORD_COUNT
    case_id_passed = expected_case_id in candidate

    results = [
        (
            f"WORD_COUNT: {'PASS' if length_passed else 'FAIL'} "
            f"({word_count} words; expected {REQUIRED_WORD_COUNT})"
        ),
        (
            f"CASE_ID: {'PASS' if case_id_passed else 'FAIL'} "
            f"(expected {expected_case_id})"
        ),
    ]
    return length_passed and case_id_passed, results


# =============================================================================
# Read one deterministic result from the human-readable result lines
# =============================================================================
def deterministic_criterion_passed(results: list[str], criterion: str) -> bool:
    return any(result.startswith(f"{criterion}: PASS") for result in results)


# =============================================================================
# Check the two criteria that require independent model judgment
# =============================================================================
def inferential_criterion_passed(evaluation: str, criterion: str) -> bool:
    for line in evaluation.splitlines():
        label, separator, decision = line.partition(":")
        if separator and label.strip().upper() == criterion:
            return decision.strip().upper() == "PASS"
    return False


def evaluate_inferential_criteria(
    client: OpenAI,
    model: str,
    refund_policy: str,
    customer_case: str,
    response_requirements: str,
    candidate: str,
) -> tuple[bool, str]:
    evaluation = client.responses.create(
        model=model,
        instructions=EVALUATOR_INSTRUCTIONS,
        input=f"""
REFUND POLICY
{refund_policy}

CUSTOMER CASE
{customer_case}

RESPONSE REQUIREMENTS
{response_requirements}

CANDIDATE RESPONSE
{candidate}
""".strip(),
    )

    policy_passed = inferential_criterion_passed(
        evaluation.output_text,
        "POLICY_COMPLIANCE",
    )
    next_step_passed = inferential_criterion_passed(
        evaluation.output_text,
        "USEFUL_NEXT_STEP",
    )
    return policy_passed and next_step_passed, evaluation.output_text


# =============================================================================
# Generate, evaluate independently, revise, and re-evaluate
# =============================================================================
def run_external_evaluation_loop(
    client: OpenAI,
    model: str,
    refund_policy: str,
    customer_case: str,
    response_requirements: str,
    max_attempts: int = 3,
) -> tuple[str, bool]:
    response = generate_initial_response(
        client,
        model,
        refund_policy,
        customer_case,
        response_requirements,
    )
    false_positive_observed = False

    for attempt in range(1, max_attempts + 1):
        candidate = response.output_text
        print(f"\n---------------- CYCLE {attempt} OF {max_attempts} ----------------")
        print("Stage 1: Generate a customer response")
        print("\nGenerator output:")
        print(candidate)

        print("\nStage 2: Self-evaluate in the generator conversation")
        self_evaluation = evaluate_own_response(
            client,
            model,
            response,
            refund_policy,
            customer_case,
            response_requirements,
        )
        self_passed = passed(self_evaluation.output_text)
        print("\nSelf-evaluator output:")
        print(self_evaluation.output_text)
        print(f"Self-evaluator verdict: {'PASS' if self_passed else 'FAIL'}")

        print("\nStage 3: Run the two deterministic checks")
        deterministic_passed, deterministic_results = evaluate_deterministic_criteria(
            candidate,
            customer_case,
        )

        for result in deterministic_results:
            print(result)

        print("\nStage 4: Evaluate in a fresh, independent conversation")
        inferential_passed, inferential_results = evaluate_inferential_criteria(
            client,
            model,
            refund_policy,
            customer_case,
            response_requirements,
            candidate,
        )

        print("\nIndependent evaluator output:")
        print(inferential_results)

        external_passed = deterministic_passed and inferential_passed
        print(f"Independent evaluator verdict: {'PASS' if external_passed else 'FAIL'}")

        print("\nCriteria comparison for this response:")
        print("Criterion          | Self | Independent")
        print("-------------------+------+------------")
        independent_checks = {
            "WORD_COUNT": deterministic_criterion_passed(
                deterministic_results, "WORD_COUNT"
            ),
            "CASE_ID": deterministic_criterion_passed(
                deterministic_results, "CASE_ID"
            ),
            "POLICY_COMPLIANCE": inferential_criterion_passed(
                inferential_results, "POLICY_COMPLIANCE"
            ),
            "USEFUL_NEXT_STEP": inferential_criterion_passed(
                inferential_results, "USEFUL_NEXT_STEP"
            ),
        }
        for criterion, independent_passed in independent_checks.items():
            self_check_passed = inferential_criterion_passed(
                self_evaluation.output_text, criterion
            )
            self_label = "PASS" if self_check_passed else "FAIL"
            independent_label = "PASS" if independent_passed else "FAIL"
            print(f"{criterion:<19}| {self_label:<5}| {independent_label}")

        print("\nComparison:")
        if self_passed and not external_passed:
            false_positive_observed = True
            print("FALSE POSITIVE OBSERVED: Self-evaluation passed a flawed response.")
        elif self_passed and external_passed:
            print("AGREEMENT: Both evaluators passed the response.")
        elif not self_passed and not external_passed:
            print("AGREEMENT: Both evaluators found a problem.")
        else:
            print("DISAGREEMENT: Self-evaluation failed a response that passed externally.")

        if external_passed:
            print("\nCycle decision: PASS")
            print("Stop reason: All four evaluation criteria passed.")
            pause_after_cycle()
            return candidate, false_positive_observed

        print("\nCycle decision: FAIL")
        if attempt == max_attempts:
            print("\nStop reason: The external evaluation loop reached its cycle limit.")
            pause_after_cycle()
            break

        feedback = "\n".join(deterministic_results + [inferential_results])
        revision_request = f"""
Revise your previous customer response so all four criteria pass.

INDEPENDENT EVALUATOR FEEDBACK
{feedback}

Return only the revised customer response.
""".strip()

        print("\nStage 5: Send independent feedback back to the generator")
        print("\nNext input to the generator:")
        print(revision_request)

        pause_after_cycle()
        response = client.responses.create(
            model=model,
            instructions=REVISION_INSTRUCTIONS,
            previous_response_id=response.id,
            input=revision_request,
        )

    return response.output_text, false_positive_observed
