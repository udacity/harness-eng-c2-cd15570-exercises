"""Student work: evaluate a candidate outside the generator conversation."""

from openai import OpenAI

from harness.generator import REVISION_INSTRUCTIONS, generate_initial_response
from harness.loops.self_evaluation_loop import evaluate_own_response, passed
from harness.pauses import pause_after_cycle


# TODO: Instruct a fresh evaluator to judge only the two criteria that require
# interpretation: POLICY_COMPLIANCE and USEFUL_NEXT_STEP. Require one PASS or
# FAIL line for each and a FEEDBACK line explaining failures. Give it no access
# to the generator's previous_response_id.
EVALUATOR_INSTRUCTIONS = """TODO: Define the independent evaluator's role and output format."""

REQUIRED_WORD_COUNT = 100


def extract_case_id(customer_case: str) -> str:
    """Return the exact CASE-#### identifier in a case.

    TODO: Extract the identifier. Raise ValueError if the case has none.
    """
    raise NotImplementedError("Extract the case ID.")


def evaluate_deterministic_criteria(
    candidate: str,
    customer_case: str,
) -> tuple[bool, list[str]]:
    """Check word count and case ID without asking a model.

    TODO: Count words with len(candidate.split()), as the requirements say.
    Check that the exact case ID appears in the candidate. Return an overall
    Boolean plus human-readable lines beginning WORD_COUNT: and CASE_ID:;
    include the observed word count so the generator can fix it.
    """
    raise NotImplementedError("Add deterministic response checks.")


def deterministic_criterion_passed(results: list[str], criterion: str) -> bool:
    """Read one PASS or FAIL from deterministic result lines.

    TODO: Return True only for an explicit '<criterion>: PASS' result.
    """
    raise NotImplementedError("Read a deterministic criterion result.")


def inferential_criterion_passed(evaluation: str, criterion: str) -> bool:
    """Read one named PASS or FAIL from the independent model's output.

    TODO: Match the criterion label, not an arbitrary PASS in feedback.
    Missing or malformed results should fail closed.
    """
    raise NotImplementedError("Read an inferential criterion result.")


def evaluate_inferential_criteria(
    client: OpenAI,
    model: str,
    refund_policy: str,
    customer_case: str,
    response_requirements: str,
    candidate: str,
) -> tuple[bool, str]:
    """Return the fresh evaluator's overall result and raw feedback.

    TODO: Call client.responses.create with EVALUATOR_INSTRUCTIONS and the
    policy, case, requirements, and candidate response in the input. Start a
    fresh conversation: omit previous_response_id. Parse both named criteria
    with inferential_criterion_passed; both must pass.
    """
    raise NotImplementedError("Add the fresh evaluator call.")


def run_external_evaluation_loop(
    client: OpenAI,
    model: str,
    refund_policy: str,
    customer_case: str,
    response_requirements: str,
    max_attempts: int = 3,
) -> tuple[str, bool]:
    """Return (last customer response, false_positive_observed).

    TODO:
    1. Generate a candidate and self-evaluate it in the generator conversation.
    2. Check the *same candidate* with evaluate_deterministic_criteria and
       evaluate_inferential_criteria. The external verdict passes only when
       all four checks pass.
    3. Print each stage and a four-criterion Self | Independent comparison.
       This column combines Python's deterministic checks with the fresh
       model's two inferential checks.
    4. Set false_positive_observed if self-review returns an overall PASS
       while any external criterion returns FAIL. Keep it True if a later
       cycle passes; the summary counts cases where it happened at least once.
    5. On external FAIL, send both Python and independent-model feedback to
       the generator for a revision. Continue from the *candidate response id*,
       so the generator receives external feedback but does not inherit the
       separate evaluator's conversation. Stop at PASS or max_attempts.
    6. Call pause_after_cycle after every cycle, including the final one.
    """
    raise NotImplementedError("Implement the external evaluation loop.")
