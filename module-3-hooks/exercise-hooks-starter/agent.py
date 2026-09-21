"""Run an expense agent until it answers, with an optional before-tool hook."""

import json
from time import perf_counter
from typing import Any

from hooks import before_tool_call
from tools import get_expense_item, get_expense_report, submit_expense_report


MAX_CYCLES = 24


POLICY_INSTRUCTIONS = """You are an expense report assistant. The user wants an
expense report submitted. Use get_expense_report to retrieve the report header
and item indices. Then use get_expense_item to inspect every numbered item,
one at a time. You need all items to detect duplicate receipts and verify the
total. Review the complete report against the company policy:

- Each meal expense must be $100 or less.
- Any individual expense over $500 requires manager approval.
- Duplicate receipt IDs must not be reimbursed.
- The reported total must equal the sum of all expense line items.
- Every expense amount must be greater than zero.

After inspecting every item, request submission with submit_expense_report,
even if your review found a possible violation. The request is a proposal;
the harness decides whether it may execute. Do not end the task merely
because you spotted a violation. Ask the submission tool for its decision,
then explain any violations it returns. Do not change report data or claim
submission succeeded unless the tool result says it did. Give a final answer
when you have the submission result."""

REPORT_ID_PARAMETERS = {
    "type": "object",
    "properties": {"report_id": {"type": "string"}},
    "required": ["report_id"],
    "additionalProperties": False,
}

GET_REPORT_TOOL = {
    "type": "function",
    "name": "get_expense_report",
    "description": "Get report metadata and indices; line-item details require get_expense_item.",
    "parameters": REPORT_ID_PARAMETERS,
}

GET_ITEM_TOOL = {
    "type": "function",
    "name": "get_expense_item",
    "description": "Get one numbered line item from the selected expense report.",
    "parameters": {
        "type": "object",
        "properties": {
            "report_id": {"type": "string"},
            "item_index": {"type": "integer", "minimum": 1},
        },
        "required": ["report_id", "item_index"],
        "additionalProperties": False,
    },
}

SUBMIT_TOOL = {
    "type": "function",
    "name": "submit_expense_report",
    "description": (
        "Request the harness's submission decision for the loaded report. "
        "Call after inspecting every item, even if you suspect a policy violation; "
        "the tool result says whether the request was blocked or submitted."
    ),
    "parameters": REPORT_ID_PARAMETERS,
}


def pause_after_cycle() -> None:
    """Let a student inspect this cycle before the next model call or summary."""
    input("\nCycle complete. Press Return to continue...")


def call_model(client: Any, **kwargs: Any) -> tuple[Any, float]:
    """Measure model time without counting the student's pause."""
    started = perf_counter()
    response = client.responses.create(**kwargs)
    return response, perf_counter() - started


def token_totals(responses: list[Any]) -> tuple[int | None, int | None, int | None]:
    """Sum API usage, or return unavailable when any response omits usage."""
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


def _tool_result(item: Any, mode: str, source_report: dict) -> tuple[dict, dict]:
    """Execute or block one proposed tool call and return its tool feedback."""
    event = {
        "tool": item.name,
        "hook_executed": False,
        "checks": {},
        "violations": [],
        "tool_executed": False,
        "submission_executed": False,
        "item_index": None,
        "status": "tool_error",
    }
    print(f"AGENT REQUESTED TOOL: {item.name}")
    try:
        arguments = json.loads(item.arguments)
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a JSON object.")
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        result = {"status": "tool_error", "message": f"Invalid tool arguments: {error}"}
        print(f"TOOL ERROR: {result['message']}")
        return event, {"type": "function_call_output", "call_id": item.call_id, "output": json.dumps(result)}

    print("TOOL ARGUMENTS:\n" + json.dumps(arguments, indent=2))
    if item.name not in ("get_expense_report", "get_expense_item", "submit_expense_report"):
        result = {"status": "tool_error", "message": f"Unsupported tool: {item.name}"}
        print(f"TOOL ERROR: {result['message']}")
    elif arguments.get("report_id") != source_report.get("report_id"):
        result = {"status": "tool_error", "message": "Report ID does not match the loaded report."}
        print(f"TOOL ERROR: {result['message']}")
    elif item.name == "get_expense_report":
        result = get_expense_report(source_report)
        event["tool_executed"] = True
        event["status"] = "retrieved"
        print(f"TOOL: REPORT HEADER RETRIEVED; {result['expense_count']} ITEMS AVAILABLE")
    elif item.name == "get_expense_item":
        item_index = arguments.get("item_index")
        if type(item_index) is not int or not 1 <= item_index <= len(source_report["expenses"]):
            result = {"status": "tool_error", "message": "Item index is out of range."}
            print(f"TOOL ERROR: {result['message']}")
        else:
            result = get_expense_item(source_report, item_index)
            event["tool_executed"] = True
            event["item_index"] = item_index
            event["status"] = "item_retrieved"
            print(f"TOOL: EXPENSE ITEM {item_index} RETRIEVED")
    elif mode == "hooks":
        # TODO: Run before_tool_call *before* the submission tool. Pass the
        # original source_report, not report data generated by the model.
        # Set event["hook_executed"] and record the hook's checks and
        # violations. Print each check's PASS/FAIL result so the run log is
        # inspectable.
        #
        # If blocked, do not call submit_expense_report. Set event status to
        # "blocked" and return a result with status, report_id, and the
        # violations. The loop will send that result to the model through
        # function_call_output so it can explain the decision.
        #
        # If allowed, run the same submit_expense_report used by basic mode,
        # then record that the submission tool actually executed.
        raise NotImplementedError("Connect the before-tool hook to submission.")
    else:
        print("HOOKS: Disabled; policy violations not checked.")
        result = submit_expense_report(source_report)
        event["tool_executed"] = True
        event["submission_executed"] = True
        event["status"] = "submitted"
        print("TOOL: EXPENSE REPORT SUBMITTED")

    tool_output = {"type": "function_call_output", "call_id": item.call_id, "output": json.dumps(result)}
    return event, tool_output


def count_failed_rules(events: list[dict]) -> int:
    """Count distinct failed policy checks across all hooked submissions.

    TODO: Use each event's checks mapping. If a malformed report was blocked
    before individual checks could run, count its violation messages instead.
    An allowed submission has zero failed rules.
    """
    raise NotImplementedError("Summarize hook violations.")


def run_agent(client: Any, model: str, report: dict, mode: str) -> dict:
    """Call the model, handle proposed tools, and pause after every cycle."""
    if mode not in ("basic", "hooks"):
        raise ValueError(f"Unknown mode: {mode}")

    request = (
        f"Please review every line item and submit expense report {report['report_id']}. "
        "Use the tools to retrieve the report header and its individual items."
    )
    responses = []
    events = []
    model_seconds = 0.0
    final_text = ""
    model_input: Any = request
    previous_response_id: str | None = None

    cycle = 0
    while True:
        if cycle >= MAX_CYCLES:
            raise RuntimeError(f"Agent did not produce a final answer within {MAX_CYCLES} cycles.")
        cycle += 1
        print(f"\n--- {mode.upper()} CYCLE {cycle} ---")
        kwargs: dict[str, Any] = {
            "model": model,
            "instructions": POLICY_INSTRUCTIONS,
            "input": model_input,
            "tools": [GET_REPORT_TOOL, GET_ITEM_TOOL, SUBMIT_TOOL],
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
                event, tool_output = _tool_result(item, mode, report)
                events.append(event)
                tool_outputs.append(tool_output)
            model_input = tool_outputs
            previous_response_id = response.id
        elif response_text:
            final_text = response_text
            print("FINAL RESPONSE:\n" + final_text)
        else:
            print("No tool call or final answer was returned; asking the agent to continue.")
            model_input = "Continue the task. Call a tool if needed, or give a final answer."
            previous_response_id = response.id
        pause_after_cycle()
        if final_text:
            break

    input_tokens, output_tokens, total_tokens = token_totals(responses)
    tool_executed = any(event["tool_executed"] for event in events)
    submission_executed = any(event["submission_executed"] for event in events)
    blocked = any(event["status"] == "blocked" for event in events)
    tool_error = any(event["status"] == "tool_error" for event in events)
    hook_executed = any(event["hook_executed"] for event in events)
    if submission_executed:
        status = "submitted"
    elif blocked:
        status = "blocked"
    elif tool_error:
        status = "tool_error"
    else:
        status = "not_submitted"

    return {
        "mode": mode,
        "report_id": report.get("report_id"),
        "tool_requested": ", ".join(event["tool"] for event in events) or "none",
        "hook_executed": hook_executed,
        "violations_detected": count_failed_rules(events) if mode == "hooks" and hook_executed else None,
        "tool_executed": tool_executed,
        "report_retrieved": any(event["status"] == "retrieved" for event in events),
        "items_inspected": len({
            event["item_index"] for event in events if event["status"] == "item_retrieved"
        }),
        "item_count": len(report["expenses"]),
        "submission_requested": any(event["tool"] == "submit_expense_report" for event in events),
        "submission_executed": submission_executed,
        "status": status,
        "final_text": final_text,
        "cycles": len(responses),
        "model_seconds": round(model_seconds, 3),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "events": events,
    }
