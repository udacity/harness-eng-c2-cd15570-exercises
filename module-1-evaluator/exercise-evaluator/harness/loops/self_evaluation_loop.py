"""Student work: let the generator review and revise its own customer response."""

from typing import Any

from openai import OpenAI

from harness.generator import REVISION_INSTRUCTIONS, generate_initial_response
from harness.pauses import pause_after_cycle


# TODO: Write instructions that ask the model to check all four response
# requirements. Require one PASS or FAIL line for WORD_COUNT, CASE_ID,
# POLICY_COMPLIANCE, and USEFUL_NEXT_STEP, followed by VERDICT and FEEDBACK.
# A PASS verdict should mean every criterion passed.
SELF_EVALUATOR_INSTRUCTIONS = """TODO: Define the self-evaluator's role and output format."""


def passed(evaluation: str) -> bool:
    """Return True only when the evaluation explicitly reports VERDICT: PASS.

    TODO: Parse the verdict line. Missing or malformed verdicts should fail
    closed so the loop cannot accept an unreviewed response.
    """
    raise NotImplementedError("Parse the self-evaluator verdict.")


def evaluate_own_response(
    client: OpenAI,
    model: str,
    response: Any,
    refund_policy: str,
    customer_case: str,
    response_requirements: str,
) -> Any:
    """Ask the model to review its own response in the generator conversation.

    TODO: Call client.responses.create with SELF_EVALUATOR_INSTRUCTIONS.
    Continue from response.id using previous_response_id, and supply the
    policy, case, and requirements as authoritative inputs. Return the raw
    Responses API result so the caller can read its id and output_text.
    """
    raise NotImplementedError("Add the same-conversation evaluation call.")


def run_self_evaluation_loop(
    client: OpenAI,
    model: str,
    refund_policy: str,
    customer_case: str,
    response_requirements: str,
    max_attempts: int = 2,
) -> str:
    """Return the last customer response after self-review or the cycle limit.

    TODO:
    1. Generate the first response with generate_initial_response.
    2. For each cycle, print the candidate and call evaluate_own_response.
    3. Print the review and stop early only when passed(...) returns True.
    4. On FAIL, ask for a revision using REVISION_INSTRUCTIONS and continue
       from the *evaluation response id*. Do not revise after the last cycle.
    5. Call pause_after_cycle after every cycle, including the final one.

    The default permits an initial draft and at most one revision per case.
    """
    raise NotImplementedError("Implement the self-evaluation loop.")
