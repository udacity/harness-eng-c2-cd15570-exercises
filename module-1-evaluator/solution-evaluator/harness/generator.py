from typing import Any

from openai import OpenAI


# =============================================================================
# Define neutral instructions for the customer-support generator
# =============================================================================
GENERATOR_INSTRUCTIONS = """
You are a customer-support agent. Write an accurate and helpful response using
only the supplied policy, customer case, and response requirements. Do not
invent approvals, exceptions, or policy details. Return only the customer
response.
""".strip()


# =============================================================================
# Define instructions for revisions requested by an evaluator
# =============================================================================
REVISION_INSTRUCTIONS = """
You are a careful customer-support agent. Revise the response using the
evaluator's feedback. Follow the supplied policy and every response requirement.
Do not preserve a decision that conflicts with the policy.
Return only the revised customer response.
""".strip()


# =============================================================================
# Build the shared task used by all three loops
# =============================================================================
def build_generation_prompt(
    refund_policy: str,
    customer_case: str,
    response_requirements: str,
) -> str:
    return f"""
Write a response to the customer.

REFUND POLICY
{refund_policy}

CUSTOMER CASE
{customer_case}

RESPONSE REQUIREMENTS
{response_requirements}

Return only the customer response.
""".strip()


# =============================================================================
# Generate the first response from the real model
# =============================================================================
def generate_initial_response(
    client: OpenAI,
    model: str,
    refund_policy: str,
    customer_case: str,
    response_requirements: str,
) -> Any:
    return client.responses.create(
        model=model,
        instructions=GENERATOR_INSTRUCTIONS,
        input=build_generation_prompt(
            refund_policy,
            customer_case,
            response_requirements,
        ),
    )
