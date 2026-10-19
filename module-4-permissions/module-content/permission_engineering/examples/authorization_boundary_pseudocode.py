"""Framework-neutral pseudocode for a permission-enforced tool boundary."""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Principal:
    subject_id: str
    role: str
    tenant_id: str


@dataclass(frozen=True)
class Decision:
    outcome: str
    required_permission: str | None
    reason_code: str
    policy_version: str


def denied_output(call_id: str, tool_name: str, decision: Decision) -> dict[str, Any]:
    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": {
            "status": "permission_denied",
            "executed": False,
            "tool": tool_name,
            "required_permission": decision.required_permission,
            "reason_code": decision.reason_code,
        },
    }


def handle_proposed_call(
    *,
    call_id: str,
    tool_name: str,
    raw_arguments: str,
    principal: Principal,
    parse_and_validate: Callable[[str, str], dict[str, Any]],
    resolve_resource: Callable[[str, dict[str, Any]], dict[str, Any]],
    authorize: Callable[[Principal, str, dict[str, Any]], Decision],
    run_safety_hook: Callable[[str, dict[str, Any], dict[str, Any]], bool],
    dispatch: Callable[[str, dict[str, Any], Principal], dict[str, Any]],
) -> dict[str, Any]:
    """Only explicit authorization and safety allow execution."""

    try:
        arguments = parse_and_validate(tool_name, raw_arguments)
        resource = resolve_resource(tool_name, arguments)
        decision = authorize(principal, tool_name, resource)
    except Exception:
        # Production code catches bounded error types and records diagnostics.
        decision = Decision("ERROR", None, "AUTHORIZATION_UNAVAILABLE", "unknown")
        return denied_output(call_id, tool_name, decision)

    if decision.outcome != "ALLOW":
        return denied_output(call_id, tool_name, decision)

    if not run_safety_hook(tool_name, arguments, resource):
        return {
            "type": "function_call_output",
            "call_id": call_id,
            "output": {
                "status": "blocked",
                "executed": False,
                "tool": tool_name,
            },
        }

    result = dispatch(tool_name, arguments, principal)
    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": {"status": "executed", "executed": True, "result": result},
    }
