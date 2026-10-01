"""Deterministic checks that run immediately before production mutations."""

import json
from typing import Any

from models import HookResult


MUTATION_TOOLS = {"rollback_deployment", "update_incident_status"}
CHECK_NAMES = (
    "fresh_health_evidence",
    "rollback_target_exists",
    "rollback_target_last_known_good",
    "mutation_not_repeated",
    "resolution_state_valid",
)


def mutation_signature(tool_name: str, arguments: dict[str, Any]) -> str:
    return f"{tool_name}:{json.dumps(arguments, sort_keys=True, separators=(',', ':'))}"


def check_fresh_health_evidence(evidence: dict[str, Any]) -> list[str]:
    return [] if evidence.get("health_checked") is True else [
        "A fresh service-health check is required before a production mutation."
    ]


def check_rollback_target_exists(
    tool_name: str, arguments: dict[str, Any], incident: dict[str, Any]
) -> list[str]:
    if tool_name != "rollback_deployment":
        return []
    target = arguments.get("target_version")
    versions = {entry.get("version") for entry in incident["deployment_history"]}
    return [] if target in versions else [
        f"Rollback target {target!r} is absent from deployment history."
    ]


def check_rollback_target_last_known_good(
    tool_name: str, arguments: dict[str, Any], incident: dict[str, Any]
) -> list[str]:
    if tool_name != "rollback_deployment":
        return []
    target = arguments.get("target_version")
    valid = any(
        entry.get("version") == target and entry.get("last_known_good") is True
        for entry in incident["deployment_history"]
    )
    return [] if valid else [
        f"Rollback target {target!r} is not marked last-known-good."
    ]


def check_mutation_not_repeated(
    tool_name: str,
    arguments: dict[str, Any],
    executed_signatures: set[str],
) -> list[str]:
    signature = mutation_signature(tool_name, arguments)
    return [] if signature not in executed_signatures else [
        "The same production mutation already executed in this run."
    ]


def check_resolution_state_valid(
    tool_name: str, arguments: dict[str, Any], incident: dict[str, Any]
) -> list[str]:
    if tool_name != "update_incident_status" or arguments.get("status") != "RESOLVED":
        return []
    valid = (
        incident.get("service_health") == "HEALTHY"
        and incident.get("recovery_confirmed") is True
    )
    return [] if valid else [
        f"{incident.get('incident_id', 'Incident')} cannot be resolved while "
        "service health is not HEALTHY and recovery is unconfirmed."
    ]


def validate_mutation(
    tool_name: str,
    arguments: dict[str, Any],
    incident: dict[str, Any],
    evidence: dict[str, Any],
    executed_signatures: set[str],
) -> HookResult:
    """Run every invariant and return one combined allow/block decision."""

    findings = {
        "fresh_health_evidence": check_fresh_health_evidence(evidence),
        "rollback_target_exists": check_rollback_target_exists(
            tool_name, arguments, incident
        ),
        "rollback_target_last_known_good": check_rollback_target_last_known_good(
            tool_name, arguments, incident
        ),
        "mutation_not_repeated": check_mutation_not_repeated(
            tool_name, arguments, executed_signatures
        ),
        "resolution_state_valid": check_resolution_state_valid(
            tool_name, arguments, incident
        ),
    }
    checks = {name: not messages for name, messages in findings.items()}
    violations = [
        message for messages in findings.values() for message in messages
    ]
    return HookResult(not violations, violations, checks)


def before_tool_call(
    tool_name: str,
    arguments: Any,
    incident: dict[str, Any],
    evidence: dict[str, Any],
    executed_signatures: set[str],
) -> HookResult:
    """Fail closed, then validate a supported production mutation."""

    if tool_name not in MUTATION_TOOLS:
        return HookResult(False, [f"Unsupported hook target: {tool_name}"])
    if not isinstance(arguments, dict):
        return HookResult(False, ["Tool arguments must be a JSON object."])
    if arguments.get("incident_id") != incident.get("incident_id"):
        return HookResult(False, ["Incident ID does not match trusted state."])
    if tool_name == "rollback_deployment":
        if set(arguments) != {"incident_id", "target_version"} or not isinstance(
            arguments.get("target_version"), str
        ):
            return HookResult(False, ["Rollback arguments are malformed."])
    if tool_name == "update_incident_status":
        if set(arguments) != {"incident_id", "status"} or arguments.get("status") not in {
            "INVESTIGATING",
            "MONITORING",
            "RESOLVED",
        }:
            return HookResult(False, ["Incident-status arguments are malformed."])
    return validate_mutation(
        tool_name, arguments, incident, evidence, executed_signatures
    )
