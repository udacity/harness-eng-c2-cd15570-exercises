"""Deterministic safety rules used for enforcement and read-only observation."""

import json
from typing import Any

from models import HookResult


MUTATION_TOOLS = {"rollback_deployment", "update_incident_status"}


def mutation_signature(tool_name: str, arguments: dict[str, Any]) -> str:
    return f"{tool_name}:{json.dumps(arguments, sort_keys=True, separators=(',', ':'))}"


def run_before_tool_hooks(
    tool_name: str,
    arguments: dict[str, Any],
    incident: dict[str, Any],
    evidence: dict[str, Any],
    executed_signatures: set[str],
) -> HookResult:
    """Return the deterministic decision without mutating incident state."""

    if tool_name not in MUTATION_TOOLS:
        return HookResult(True)
    findings: dict[str, list[str]] = {
        "fresh_health_evidence": (
            []
            if evidence.get("health_checked") is True
            else ["A fresh service-health check is required before mutation."]
        ),
        "rollback_target_exists": [],
        "rollback_target_last_known_good": [],
        "mutation_not_repeated": (
            []
            if mutation_signature(tool_name, arguments) not in executed_signatures
            else ["The same production mutation already executed."]
        ),
        "resolution_state_valid": [],
    }
    codes: list[str] = []
    if tool_name == "rollback_deployment":
        target = arguments.get("target_version")
        versions = {item.get("version") for item in incident["deployment_history"]}
        if target not in versions:
            findings["rollback_target_exists"] = [
                f"Rollback target {target!r} is absent from deployment history."
            ]
            codes.append("rollback_target_missing")
        last_known_good = any(
            item.get("version") == target and item.get("last_known_good") is True
            for item in incident["deployment_history"]
        )
        if not last_known_good:
            findings["rollback_target_last_known_good"] = [
                f"Rollback target {target!r} is not last-known-good."
            ]
            codes.append("rollback_target_not_last_known_good")
    if (
        tool_name == "update_incident_status"
        and arguments.get("status") == "RESOLVED"
        and not (
            incident.get("service_health") == "HEALTHY"
            and incident.get("recovery_confirmed") is True
        )
    ):
        findings["resolution_state_valid"] = [
            "The incident cannot be resolved before confirmed recovery."
        ]
        codes.append("premature_resolution")
    if findings["fresh_health_evidence"]:
        codes.append("missing_fresh_health")
    if findings["mutation_not_repeated"]:
        codes.append("repeated_mutation")
    checks = {name: not messages for name, messages in findings.items()}
    violations = [
        message for messages in findings.values() for message in messages
    ]
    return HookResult(not violations, violations, checks, codes)
