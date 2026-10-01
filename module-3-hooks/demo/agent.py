"""Run the incident agent with an optional before-mutation hook."""

import json
from collections.abc import Callable
from copy import deepcopy
from time import perf_counter
from typing import Any

from catalog import catalog_prompt, load_skill
from hooks import MUTATION_TOOLS, before_tool_call, mutation_signature
from tools import (
    get_deployment_history,
    get_incident,
    get_service_health,
    query_service_logs,
    rollback_deployment,
    update_incident_status,
)


MAX_CYCLES = 20

BASE_INSTRUCTIONS = """You are an incident-response assistant. Investigate the
requested production incident using the available retrieval tools. Use
load_skill when its catalog description is relevant; the catalog does not
contain the detailed skill instructions. Treat every production mutation as a
proposal until its tool result confirms execution.

You must request every mutation explicitly requested by the operator, even if
your reasoning or a loaded skill suggests it is unsafe. The harness, not the
model, makes the final allow/block decision. After each mutation result,
continue until all requested mutations have decisions. Explain blocked calls
using the returned violations. Never claim recovery that the tools do not
confirm. Your final response must contain exactly 60 whitespace-separated
words, include INC-2048, describe the final state accurately, and give one
useful next step."""

INCIDENT_ID_PARAMETERS = {
    "type": "object",
    "properties": {"incident_id": {"type": "string"}},
    "required": ["incident_id"],
    "additionalProperties": False,
}

LOAD_SKILL_TOOL: dict[str, Any] = {
    "type": "function",
    "name": "load_skill",
    "description": "Load the full instructions for one relevant catalog skill.",
    "parameters": {
        "type": "object",
        "properties": {"skill_name": {"type": "string"}},
        "required": ["skill_name"],
        "additionalProperties": False,
    },
}

GET_INCIDENT_TOOL = {
    "type": "function",
    "name": "get_incident",
    "description": "Get the trusted incident header and current deployment.",
    "parameters": INCIDENT_ID_PARAMETERS,
}

GET_HEALTH_TOOL = {
    "type": "function",
    "name": "get_service_health",
    "description": "Get a fresh health snapshot for the incident's service.",
    "parameters": INCIDENT_ID_PARAMETERS,
}

GET_DEPLOYMENTS_TOOL = {
    "type": "function",
    "name": "get_deployment_history",
    "description": "Get deployment versions and last-known-good evidence.",
    "parameters": INCIDENT_ID_PARAMETERS,
}

GET_LOGS_TOOL = {
    "type": "function",
    "name": "query_service_logs",
    "description": "Get recent authoritative log evidence for the service.",
    "parameters": INCIDENT_ID_PARAMETERS,
}

ROLLBACK_TOOL = {
    "type": "function",
    "name": "rollback_deployment",
    "description": (
        "Request a production rollback decision. The harness may allow or block it."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "incident_id": {"type": "string"},
            "target_version": {"type": "string"},
        },
        "required": ["incident_id", "target_version"],
        "additionalProperties": False,
    },
}

UPDATE_STATUS_TOOL = {
    "type": "function",
    "name": "update_incident_status",
    "description": (
        "Request an incident-status mutation. The harness may allow or block it."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "incident_id": {"type": "string"},
            "status": {
                "type": "string",
                "enum": ["INVESTIGATING", "MONITORING", "RESOLVED"],
            },
        },
        "required": ["incident_id", "status"],
        "additionalProperties": False,
    },
}

TOOLS = [
    LOAD_SKILL_TOOL,
    GET_INCIDENT_TOOL,
    GET_HEALTH_TOOL,
    GET_DEPLOYMENTS_TOOL,
    GET_LOGS_TOOL,
    ROLLBACK_TOOL,
    UPDATE_STATUS_TOOL,
]

RETRIEVAL_TOOLS = {
    "get_incident",
    "get_service_health",
    "get_deployment_history",
    "query_service_logs",
}


def build_instructions(catalog: dict) -> str:
    """Add routing metadata, but not complete skill bodies, to the prompt."""

    return BASE_INSTRUCTIONS + "\n\nAVAILABLE SKILLS\n" + catalog_prompt(catalog)


def call_model(client: Any, **kwargs: Any) -> tuple[Any, float]:
    started = perf_counter()
    response = client.responses.create(**kwargs)
    return response, perf_counter() - started


def token_totals(responses: list[Any]) -> tuple[int | None, int | None, int | None]:
    counts: list[tuple[int, int]] = []
    for response in responses:
        usage = getattr(response, "usage", None)
        input_count = getattr(usage, "input_tokens", None)
        output_count = getattr(usage, "output_tokens", None)
        if input_count is None or output_count is None:
            return None, None, None
        counts.append((input_count, output_count))
    input_tokens = sum(pair[0] for pair in counts)
    output_tokens = sum(pair[1] for pair in counts)
    return input_tokens, output_tokens, input_tokens + output_tokens


def _event(tool_name: str) -> dict[str, Any]:
    return {
        "tool": tool_name,
        "skill": None,
        "skill_loaded": False,
        "hook_executed": False,
        "checks": {},
        "violations": [],
        "tool_executed": False,
        "mutation_executed": False,
        "status": "tool_error",
    }


def _output(call_id: str, result: Any) -> dict[str, str]:
    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": result if isinstance(result, str) else json.dumps(result),
    }


def _tool_result(
    item: Any,
    mode: str,
    incident: dict[str, Any],
    evidence: dict[str, Any],
    executed_signatures: set[str],
    catalog: dict,
    *,
    emit: Callable[[str], None] = print,
) -> tuple[dict[str, Any], dict[str, str]]:
    """Execute or block one proposed tool call and return feedback to the model."""

    event = _event(item.name)
    emit(f"AGENT REQUESTED TOOL: {item.name}")
    try:
        arguments = json.loads(item.arguments)
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a JSON object.")
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        result = {"status": "tool_error", "message": f"Invalid arguments: {error}"}
        emit(f"TOOL ERROR: {result['message']}")
        return event, _output(item.call_id, result)

    emit("TOOL ARGUMENTS:\n" + json.dumps(arguments, indent=2))

    if item.name == "load_skill":
        try:
            if set(arguments) != {"skill_name"} or not isinstance(
                arguments.get("skill_name"), str
            ):
                raise ValueError("arguments must contain only string skill_name")
            name = arguments["skill_name"]
            skill_text, path = load_skill(name, catalog)
            event.update(
                skill=name,
                skill_loaded=True,
                tool_executed=True,
                status="skill_loaded",
            )
            emit(f"SKILL LOADED: {name} ({path})")
            return event, _output(item.call_id, skill_text)
        except (KeyError, TypeError, ValueError) as error:
            result = {"status": "tool_error", "message": str(error)}
            emit(f"TOOL ERROR: {result['message']}")
            return event, _output(item.call_id, result)

    if item.name not in RETRIEVAL_TOOLS | MUTATION_TOOLS:
        result = {"status": "tool_error", "message": f"Unsupported tool: {item.name}"}
        emit(f"TOOL ERROR: {result['message']}")
        return event, _output(item.call_id, result)
    if arguments.get("incident_id") != incident.get("incident_id"):
        result = {
            "status": "tool_error",
            "message": "Incident ID does not match trusted state.",
        }
        emit(f"TOOL ERROR: {result['message']}")
        return event, _output(item.call_id, result)

    if item.name == "rollback_deployment" and (
        set(arguments) != {"incident_id", "target_version"}
        or not isinstance(arguments.get("target_version"), str)
    ):
        result = {"status": "tool_error", "message": "Malformed rollback arguments."}
        emit(f"TOOL ERROR: {result['message']}")
        return event, _output(item.call_id, result)
    if item.name == "update_incident_status" and (
        set(arguments) != {"incident_id", "status"}
        or arguments.get("status") not in {"INVESTIGATING", "MONITORING", "RESOLVED"}
    ):
        result = {
            "status": "tool_error",
            "message": "Malformed incident-status arguments.",
        }
        emit(f"TOOL ERROR: {result['message']}")
        return event, _output(item.call_id, result)

    if item.name in RETRIEVAL_TOOLS:
        if set(arguments) != {"incident_id"}:
            result = {"status": "tool_error", "message": "Malformed retrieval arguments."}
            emit(f"TOOL ERROR: {result['message']}")
            return event, _output(item.call_id, result)
        if item.name == "get_incident":
            result = get_incident(incident)
        elif item.name == "get_service_health":
            result = get_service_health(incident)
            evidence["health_checked"] = True
        elif item.name == "get_deployment_history":
            result = get_deployment_history(incident)
        else:
            result = query_service_logs(incident)
        event.update(tool_executed=True, status="retrieved")
        emit(f"TOOL EXECUTED: {item.name}")
        return event, _output(item.call_id, result)

    if mode == "hooks":
        event["hook_executed"] = True
        emit(f"HOOK: before_tool_call -> {item.name}")
        decision = before_tool_call(
            item.name, arguments, incident, evidence, executed_signatures
        )
        event["checks"] = decision.checks
        event["violations"] = list(decision.violations)
        for check_name, passed in decision.checks.items():
            emit(f"CHECK: {check_name}: {'PASS' if passed else 'FAIL'}")
        if not decision.allowed:
            event["status"] = "blocked"
            emit("HOOK RESULT: BLOCKED")
            for violation in decision.violations:
                emit(f"VIOLATION: {violation}")
            emit("MUTATION TOOL: NOT EXECUTED")
            result = {
                "status": "blocked",
                "incident_id": incident["incident_id"],
                "tool": item.name,
                "message": "Mutation blocked by the before-tool hook.",
                "violations": list(decision.violations),
            }
            return event, _output(item.call_id, result)
        emit("HOOK RESULT: ALLOWED")
    else:
        emit("HOOKS: Disabled; mutation invariants were not checked.")

    if item.name == "rollback_deployment":
        result = rollback_deployment(incident, arguments.get("target_version"))
    else:
        result = update_incident_status(incident, arguments.get("status"))
    executed_signatures.add(mutation_signature(item.name, arguments))
    evidence["health_checked"] = False
    event.update(
        tool_executed=True,
        mutation_executed=True,
        status="executed",
    )
    emit(f"MUTATION TOOL EXECUTED: {item.name}")
    return event, _output(item.call_id, result)


def count_failed_rules(events: list[dict[str, Any]]) -> int:
    """Count distinct failed checks, with fail-closed errors as violations."""

    failed = {
        name
        for event in events
        for name, passed in event["checks"].items()
        if not passed
    }
    if failed:
        return len(failed)
    return len(
        {
            violation
            for event in events
            if event["hook_executed"]
            for violation in event["violations"]
        }
    )


def run_agent(
    client: Any,
    model: str,
    scenario: dict[str, Any],
    mode: str,
    catalog: dict,
    *,
    emit: Callable[[str], None] = print,
    pause: Callable[[], None] = lambda: None,
) -> dict[str, Any]:
    """Call the model until it answers, handling every requested tool call."""

    if mode not in ("basic", "hooks"):
        raise ValueError(f"Unknown mode: {mode}")

    incident = deepcopy(scenario["incident"])
    initial_incident = deepcopy(incident)
    evidence: dict[str, Any] = {"health_checked": False}
    executed_signatures: set[str] = set()
    responses: list[Any] = []
    events: list[dict[str, Any]] = []
    model_seconds = 0.0
    final_text = ""
    model_input: Any = (
        f"SCENARIO ID: {scenario['scenario_id']}\n"
        f"AUTHENTICATED USER: {json.dumps(scenario['authenticated_user'])}\n"
        f"OPERATOR REQUEST: {scenario['request']}"
    )
    previous_response_id: str | None = None
    instructions = build_instructions(catalog)

    for cycle in range(1, MAX_CYCLES + 1):
        emit(f"\n--- {mode.upper()} CYCLE {cycle} ---")
        kwargs: dict[str, Any] = {
            "model": model,
            "instructions": instructions,
            "input": model_input,
            "tools": TOOLS,
            "parallel_tool_calls": False,
        }
        if previous_response_id is not None:
            kwargs["previous_response_id"] = previous_response_id

        response, seconds = call_model(client, **kwargs)
        responses.append(response)
        model_seconds += seconds
        tool_calls = [
            item for item in response.output if item.type == "function_call"
        ]
        response_text = response.output_text.strip()
        if response_text:
            emit("AGENT TEXT:\n" + response_text)
        if tool_calls:
            tool_outputs: list[dict[str, str]] = []
            for item in tool_calls:
                event, tool_output = _tool_result(
                    item,
                    mode,
                    incident,
                    evidence,
                    executed_signatures,
                    catalog,
                    emit=emit,
                )
                events.append(event)
                tool_outputs.append(tool_output)
            model_input = tool_outputs
            previous_response_id = response.id
        elif response_text:
            final_text = response_text
            emit("FINAL INCIDENT NOTE:\n" + final_text)
        else:
            emit("No tool call or final answer; asking the agent to continue.")
            model_input = "Continue the task: call a tool or give the final note."
            previous_response_id = response.id
        pause()
        if final_text:
            break
    else:
        raise RuntimeError(
            f"Agent did not produce a final answer within {MAX_CYCLES} cycles."
        )

    input_tokens, output_tokens, total_tokens = token_totals(responses)
    mutation_events = [event for event in events if event["tool"] in MUTATION_TOOLS]
    blocked = any(event["status"] == "blocked" for event in mutation_events)
    executed = any(event["mutation_executed"] for event in mutation_events)
    tool_error = any(event["status"] == "tool_error" for event in events)
    status = (
        "blocked"
        if blocked
        else "mutated"
        if executed
        else "tool_error"
        if tool_error
        else "no_mutation"
    )
    return {
        "mode": mode,
        "scenario_id": scenario["scenario_id"],
        "status": status,
        "output": final_text,
        "initial_incident": initial_incident,
        "final_incident": deepcopy(incident),
        "loaded_skills": list(
            dict.fromkeys(
                event["skill"] for event in events if event["skill_loaded"]
            )
        ),
        "events": events,
        "hook_executed": any(event["hook_executed"] for event in events),
        "violations_detected": (
            count_failed_rules(events)
            if mode == "hooks" and any(event["hook_executed"] for event in events)
            else None
        ),
        "mutations_requested": len(mutation_events),
        "mutations_executed": sum(
            event["mutation_executed"] for event in mutation_events
        ),
        "cycles": len(responses),
        "model_seconds": round(model_seconds, 3),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }
