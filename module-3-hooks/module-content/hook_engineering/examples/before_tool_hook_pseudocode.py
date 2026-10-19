"""Provider-shaped pseudocode for deterministic before-tool enforcement."""

import json
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class CheckFinding:
    name: str
    status: str  # PASS, FAIL, ERROR, or NOT_APPLICABLE
    message: str = ""


@dataclass(frozen=True)
class HookDecision:
    allowed: bool
    findings: tuple[CheckFinding, ...] = field(default_factory=tuple)


def before_tool_call(
    tool_name: str,
    arguments: Any,
    trusted_state: dict[str, Any],
    executed_signatures: set[str],
) -> HookDecision:
    """Return a deterministic decision for one protected mutation."""

    if tool_name not in {"rollback_deployment", "update_incident_status"}:
        return blocked("supported_tool", "Unsupported hook target.")
    if not isinstance(arguments, dict):
        return blocked("argument_shape", "Arguments must be an object.")

    try:
        validate_exact_argument_shape(tool_name, arguments)
        if arguments["incident_id"] != trusted_state["incident_id"]:
            return blocked("incident_identity", "Incident ID mismatch.")

        findings = tuple(
            check(tool_name, arguments, trusted_state, executed_signatures)
            for check in ANTIDOTES
        )
    except (KeyError, TypeError, ValueError) as error:
        return blocked("hook_error", f"Unable to validate safely: {error}")

    allowed = all(
        finding.status in {"PASS", "NOT_APPLICABLE"}
        for finding in findings
    )
    return HookDecision(allowed, findings)


def dispatch_proposed_call(
    item: Any,
    trusted_state: dict[str, Any],
    executed_signatures: set[str],
    execute: Callable[[str, dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    """Parse, authorize elsewhere, validate, then execute only on allow."""

    try:
        arguments = json.loads(item.arguments)
    except (json.JSONDecodeError, TypeError) as error:
        return tool_output(item.call_id, {"status": "blocked", "error": str(error)})

    # A production path performs identity/resource authorization here.
    decision = before_tool_call(
        item.name, arguments, trusted_state, executed_signatures
    )
    if not decision.allowed:
        return tool_output(
            item.call_id,
            {
                "status": "blocked",
                "tool_executed": False,
                "findings": [finding.__dict__ for finding in decision.findings],
            },
        )

    # For shared mutable state, combine validation and mutation atomically or
    # execute with an expected state/version precondition.
    result = execute(item.name, arguments)
    executed_signatures.add(canonical_signature(item.name, arguments))
    trusted_state["health_evidence_fresh"] = False
    return tool_output(
        item.call_id,
        {"status": "executed", "tool_executed": True, "result": result},
    )


def blocked(name: str, message: str) -> HookDecision:
    return HookDecision(False, (CheckFinding(name, "ERROR", message),))


def canonical_signature(tool_name: str, arguments: dict[str, Any]) -> str:
    return f"{tool_name}:{json.dumps(arguments, sort_keys=True, separators=(',', ':'))}"


def tool_output(call_id: str, value: dict[str, Any]) -> dict[str, str]:
    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": json.dumps(value, sort_keys=True),
    }


def validate_exact_argument_shape(tool_name: str, arguments: dict[str, Any]) -> None:
    expected = {
        "rollback_deployment": {"incident_id", "target_version"},
        "update_incident_status": {"incident_id", "status"},
    }[tool_name]
    if set(arguments) != expected:
        raise ValueError(f"Expected exactly {sorted(expected)}")


def check_fresh_evidence(
    tool_name: str,
    arguments: dict[str, Any],
    state: dict[str, Any],
    executed: set[str],
) -> CheckFinding:
    del tool_name, arguments, executed
    if state.get("health_evidence_fresh") is True:
        return CheckFinding("fresh_health_evidence", "PASS")
    return CheckFinding(
        "fresh_health_evidence", "FAIL", "Fresh health evidence is required."
    )


def check_not_repeated(
    tool_name: str,
    arguments: dict[str, Any],
    state: dict[str, Any],
    executed: set[str],
) -> CheckFinding:
    del state
    if canonical_signature(tool_name, arguments) not in executed:
        return CheckFinding("mutation_not_repeated", "PASS")
    return CheckFinding(
        "mutation_not_repeated", "FAIL", "Equivalent mutation already executed."
    )


ANTIDOTES = (check_fresh_evidence, check_not_repeated)
