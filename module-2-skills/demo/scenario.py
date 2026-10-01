"""Load the shared incident state and one Module 2 request."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class IncidentRequest:
    request_id: str
    request: str
    expected_skills: tuple[str, ...]


def _mapping(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def load_incident(path: Path) -> dict[str, Any]:
    incident = _mapping(path)
    required = {
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
        "authenticated_user",
    }
    missing = required - set(incident)
    if missing:
        raise ValueError(f"Incident is missing: {', '.join(sorted(missing))}")
    return incident


def load_request(path: Path) -> IncidentRequest:
    raw = _mapping(path)
    request_id = raw.get("request_id")
    request = raw.get("request")
    expected_skills = raw.get("expected_skills")
    if not isinstance(request_id, str) or not request_id:
        raise ValueError(f"request_id must be a nonempty string in {path}")
    if request_id != path.stem:
        raise ValueError(f"request_id must match filename in {path}")
    if not isinstance(request, str) or not request:
        raise ValueError(f"request must be a nonempty string in {path}")
    if not isinstance(expected_skills, list) or not all(
        isinstance(name, str) and name for name in expected_skills
    ):
        raise ValueError(f"expected_skills must contain names in {path}")
    return IncidentRequest(request_id, request, tuple(expected_skills))


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
            f"Restart performed: {incident['restart_performed']}",
            f"Recovery confirmed: {incident['recovery_confirmed']}",
        ]
    )


def build_brief(incident: dict[str, Any], request: IncidentRequest) -> str:
    """Create the identical task input used by both skill-loading modes."""

    return f"""
REQUEST ID
{request.request_id}

AUTHORITATIVE INCIDENT FACTS
{incident_context(incident)}

OPERATOR REQUEST
{request.request}
""".strip()
