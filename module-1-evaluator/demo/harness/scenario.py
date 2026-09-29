"""Load and validate the immutable incident scenario."""

import json
from pathlib import Path
from typing import Any

from harness.models import Scenario


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
}


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return value


def load_scenario(path: Path) -> Scenario:
    """Load one scenario and fail early when its contract is incomplete."""

    raw = _require_mapping(json.loads(path.read_text(encoding="utf-8")), "scenario")
    incident = _require_mapping(raw.get("incident"), "incident")
    user = _require_mapping(raw.get("authenticated_user"), "authenticated_user")
    requirements = _require_mapping(
        raw.get("response_requirements"), "response_requirements"
    )

    missing_incident = REQUIRED_INCIDENT_FIELDS - set(incident)
    if missing_incident:
        missing = ", ".join(sorted(missing_incident))
        raise ValueError(f"incident is missing required fields: {missing}")

    for field_name in ("scenario_id", "request"):
        if not isinstance(raw.get(field_name), str) or not raw[field_name].strip():
            raise ValueError(f"{field_name} must be a nonempty string.")
    for field_name in ("user_id", "name", "role"):
        if not isinstance(user.get(field_name), str) or not user[field_name].strip():
            raise ValueError(f"authenticated_user.{field_name} must be nonempty.")

    minimum = requirements.get("minimum_words")
    maximum = requirements.get("maximum_words")
    required_id = requirements.get("required_incident_id")
    criteria = requirements.get("inferential_criteria")
    if type(minimum) is not int or type(maximum) is not int or not 0 < minimum <= maximum:
        raise ValueError("response word limits must be positive ordered integers.")
    if required_id != incident["incident_id"]:
        raise ValueError("required_incident_id must match incident.incident_id.")
    if not isinstance(criteria, list) or not criteria or not all(
        isinstance(item, str) and item.strip() for item in criteria
    ):
        raise ValueError("inferential_criteria must contain nonempty strings.")

    return Scenario(
        scenario_id=raw["scenario_id"],
        request=raw["request"],
        authenticated_user=dict(user),
        incident=dict(incident),
        response_requirements=dict(requirements),
    )


def authoritative_context(scenario: Scenario) -> str:
    """Render stable facts for generation and independent evaluation."""

    incident = scenario.incident
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
            f"Restart performed: {incident['restart_performed']}",
            f"Recovery confirmed: {incident['recovery_confirmed']}",
        ]
    )


def requirements_context(scenario: Scenario) -> str:
    """Render the response rubric without adding untrusted facts."""

    requirements = scenario.response_requirements
    inferential = "\n".join(
        f"- {criterion}" for criterion in requirements["inferential_criteria"]
    )
    return (
        f"- Include the exact incident ID {requirements['required_incident_id']}.\n"
        f"- Write {requirements['minimum_words']} to "
        f"{requirements['maximum_words']} whitespace-separated words.\n"
        f"{inferential}"
    )
