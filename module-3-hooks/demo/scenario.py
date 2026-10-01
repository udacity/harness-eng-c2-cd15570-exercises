"""Load an isolated mutable incident scenario for one run."""

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


REQUIRED_INCIDENT_FIELDS = {
    "incident_id",
    "environment",
    "service",
    "incident_status",
    "service_health",
    "checkout_error_rate_percent",
    "current_deployment",
    "last_known_good_deployment",
    "rollback_performed",
    "restart_performed",
    "recovery_confirmed",
    "deployment_history",
    "logs",
    "actions",
}


def load_scenario(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Scenario must be a JSON object.")
    incident = raw.get("incident")
    if not isinstance(incident, dict):
        raise ValueError("Scenario incident must be a JSON object.")
    missing = REQUIRED_INCIDENT_FIELDS - set(incident)
    if missing:
        raise ValueError(f"Incident is missing: {', '.join(sorted(missing))}")
    if raw.get("scenario_id") != path.stem:
        raise ValueError("scenario_id must match the scenario filename.")
    if not isinstance(raw.get("scripted_mutations"), list):
        raise ValueError("scripted_mutations must be a list.")
    return deepcopy(raw)


def fresh_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(scenario)


def incident_context(incident: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"Incident ID: {incident['incident_id']}",
            f"Environment: {incident['environment']}",
            f"Service: {incident['service']}",
            f"Incident status: {incident['incident_status']}",
            f"Service health: {incident['service_health']}",
            f"Checkout error rate: {incident['checkout_error_rate_percent']}%",
            f"Current deployment: {incident['current_deployment']}",
            f"Last-known-good deployment: {incident['last_known_good_deployment']}",
            f"Rollback performed: {incident['rollback_performed']}",
            f"Recovery confirmed: {incident['recovery_confirmed']}",
        ]
    )
