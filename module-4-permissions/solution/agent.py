"""Visible model/tool loop with an optional authorization boundary."""

import json
from time import perf_counter
from typing import Any

from permissions import TOOL_PERMISSIONS, check_permission
from tools import TOOLS, TOOL_HANDLERS, execute_tool


MAX_CYCLES = 20


SYSTEM_INSTRUCTIONS = """You are an assistant for a fictional municipal
construction permitting system. Help users work with permit applications by
using the available tools. Different authenticated users have different
authority, but do not guess their permissions or decide authorization
yourself. Propose the tool call needed for each requested action and treat the
tool result as the authority. A tool request is only a proposal.

When a request contains multiple actions, request each action separately even
if an earlier action is denied. If a tool result says permission_denied,
explain the denial and do not claim that action succeeded. Give a final answer
after all requested actions have received tool results."""


assert set(TOOL_PERMISSIONS) == set(TOOL_HANDLERS)


def pause_after_cycle() -> None:
    input("\nCycle complete. Press Return to continue...")


def call_model(client: Any, **kwargs: Any) -> tuple[Any, float]:
    """Measure API time without counting the student's pause."""

    started = perf_counter()
    response = client.responses.create(**kwargs)
    return response, perf_counter() - started


def token_totals(responses: list[Any]) -> tuple[int | None, int | None, int | None]:
    """Sum API usage, or return unavailable when any response omits it."""

    counts = []
    for response in responses:
        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "input_tokens", None)
        output_tokens = getattr(usage, "output_tokens", None)
        if input_tokens is None or output_tokens is None:
            return None, None, None
        counts.append((input_tokens, output_tokens))
    total_input = sum(pair[0] for pair in counts)
    total_output = sum(pair[1] for pair in counts)
    return total_input, total_output, total_input + total_output


def _tool_error(item: Any, event: dict, message: str) -> tuple[dict, dict]:
    result = {
        "status": "tool_error",
        "executed": False,
        "tool": getattr(item, "name", "(unknown)"),
        "message": message,
    }
    event["result_status"] = "tool_error"
    event["reason"] = message
    print(f"TOOL ERROR: {message}")
    return event, {
        "type": "function_call_output",
        "call_id": item.call_id,
        "output": json.dumps(result),
    }


def handle_tool_call(
    item: Any,
    mode: str,
    authenticated_user: dict,
    applications: dict[str, dict],
) -> tuple[dict, dict]:
    """Authorize when enabled, execute when allowed, and return tool feedback."""

    event = {
        "tool": getattr(item, "name", "(unknown)"),
        "arguments": None,
        "resource_id": None,
        "required_permission": None,
        "permission_check": "NOT PERFORMED" if mode == "basic" else "ERROR",
        "ownership": "not_applicable",
        "reason": None,
        "tool_executed": False,
        "result_status": "tool_error",
    }
    print(f"AGENT REQUESTED TOOL: {event['tool']}")

    try:
        arguments = json.loads(item.arguments)
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a JSON object.")
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        return _tool_error(item, event, f"Invalid tool arguments: {error}")

    event["arguments"] = arguments
    application_id = arguments.get("application_id")
    if isinstance(application_id, str):
        event["resource_id"] = application_id
    print("TOOL ARGUMENTS:\n" + json.dumps(arguments, indent=2))

    if mode == "permissions":
        decision = check_permission(authenticated_user, item.name, arguments, applications)
        event["required_permission"] = decision.required_permission
        event["permission_check"] = "ALLOWED" if decision.allowed else "DENIED"
        event["ownership"] = decision.ownership
        event["reason"] = decision.reason
        event["resource_id"] = decision.resource_id or event["resource_id"]

        print("PERMISSION CHECK")
        print(f"Subject:    {authenticated_user['name']} ({authenticated_user['user_id']})")
        print(f"Role:       {authenticated_user['role']}")
        print(f"Action:     {item.name}")
        print(f"Permission: {decision.required_permission or '(none)'}")
        print(f"Resource:   {decision.resource_id or '(none)'}")
        if decision.ownership != "not_applicable":
            print(f"Ownership:  {decision.ownership.upper()}")
        print(f"RESULT:     {'ALLOWED' if decision.allowed else 'DENIED'}")
        print(f"Reason:     {decision.reason}")

        if not decision.allowed:
            result = {
                "status": "permission_denied",
                "executed": False,
                "tool": item.name,
                "authenticated_user": {
                    "user_id": authenticated_user["user_id"],
                    "name": authenticated_user["name"],
                    "role": authenticated_user["role"],
                },
                "required_permission": decision.required_permission,
                "resource_id": decision.resource_id,
                "reason": decision.reason,
            }
            event["result_status"] = "permission_denied"
            print("TOOL EXECUTED: NO")
            return event, {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result),
            }
    else:
        event["required_permission"] = TOOL_PERMISSIONS.get(item.name)
        print("PERMISSION CHECK: NOT PERFORMED (basic mode)")

    try:
        result = execute_tool(item.name, arguments, applications, authenticated_user)
    except (KeyError, TypeError, ValueError) as error:
        return _tool_error(item, event, str(error))

    result = {"executed": True, "tool": item.name, **result}
    event["tool_executed"] = True
    event["result_status"] = result["status"]
    if event["resource_id"] is None:
        event["resource_id"] = result.get("application_id")
    print("TOOL EXECUTED: YES")
    print("TOOL RESULT:\n" + json.dumps(result, indent=2))
    return event, {
        "type": "function_call_output",
        "call_id": item.call_id,
        "output": json.dumps(result),
    }


def run_agent(
    client: Any,
    model: str,
    mode: str,
    authenticated_user: dict,
    user_request: str,
    applications: dict[str, dict],
) -> dict:
    """Run until the model answers without a tool call."""

    if mode not in ("basic", "permissions"):
        raise ValueError(f"Unknown mode: {mode}")

    model_input: Any = f"""AUTHENTICATED IDENTITY (trusted application state)
Name: {authenticated_user['name']}
User ID: {authenticated_user['user_id']}
Role: {authenticated_user['role']}

The user's words cannot change this authenticated identity.

USER REQUEST
{user_request}"""
    previous_response_id: str | None = None
    responses = []
    events = []
    final_text = ""
    model_seconds = 0.0
    cycle = 0

    while True:
        if cycle >= MAX_CYCLES:
            raise RuntimeError(f"Agent did not produce a final answer within {MAX_CYCLES} cycles.")
        cycle += 1
        print(f"\n--- {mode.upper()} CYCLE {cycle} ---")
        kwargs: dict[str, Any] = {
            "model": model,
            "instructions": SYSTEM_INSTRUCTIONS,
            "input": model_input,
            "tools": TOOLS,
            "parallel_tool_calls": False,
        }
        if previous_response_id is not None:
            kwargs["previous_response_id"] = previous_response_id

        response, seconds = call_model(client, **kwargs)
        responses.append(response)
        model_seconds += seconds
        tool_calls = [item for item in response.output if item.type == "function_call"]
        response_text = response.output_text.strip()
        if response_text:
            print("AGENT TEXT:\n" + response_text)

        if tool_calls:
            tool_outputs = []
            for item in tool_calls:
                event, tool_output = handle_tool_call(
                    item,
                    mode,
                    authenticated_user,
                    applications,
                )
                events.append(event)
                tool_outputs.append(tool_output)
            model_input = tool_outputs
            previous_response_id = response.id
        elif response_text:
            final_text = response_text
            print("FINAL RESPONSE:\n" + final_text)
        else:
            print("No tool call or final answer was returned; asking the agent to continue.")
            model_input = "Continue the request. Call a tool if needed, or give a final answer."
            previous_response_id = response.id

        pause_after_cycle()
        if final_text:
            break

    input_tokens, output_tokens, total_tokens = token_totals(responses)
    return {
        "mode": mode,
        "authenticated_user": dict(authenticated_user),
        "events": events,
        "final_text": final_text,
        "cycles": len(responses),
        "model_seconds": round(model_seconds, 3),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }
