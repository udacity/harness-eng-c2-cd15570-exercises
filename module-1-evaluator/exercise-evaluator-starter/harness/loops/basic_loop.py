from openai import OpenAI

from harness.generator import GENERATOR_INSTRUCTIONS, generate_initial_response
from harness.pauses import pause_after_cycle


# =============================================================================
# Run a fixed number of generator iterations without an evaluator
# =============================================================================
def run_basic_loop(
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
        print("Stage: Generate a customer response")
        print("\nGenerator output:")
        print(response.output_text)

        if attempt == max_attempts:
            print("\nStop reason: The basic loop reached its fixed cycle limit.")
            pause_after_cycle()
            break

        revision_request = (
            "Rewrite your previous response so it is clearer. Preserve the "
            "same decision and priorities. Return only the revised response."
        )
        print("\nNext input to the generator:")
        print(revision_request)

        pause_after_cycle()
        response = client.responses.create(
            model=model,
            instructions=GENERATOR_INSTRUCTIONS,
            previous_response_id=response.id,
            input=revision_request,
        )

    return response.output_text
