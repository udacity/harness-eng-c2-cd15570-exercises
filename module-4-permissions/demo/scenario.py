"""Load and validate one authorization demo scenario."""

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from data import USERS


def load_scenario(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Scenario must be a JSON object.")
    if raw.get("scenario_id") != path.stem:
        raise ValueError("scenario_id must match the scenario filename.")
    if raw.get("authenticated_user") not in USERS:
        raise ValueError("Scenario must reference a trusted user key.")
    if not isinstance(raw.get("request"), str) or not raw["request"].strip():
        raise ValueError("Scenario request must be a nonempty string.")
    if not isinstance(raw.get("expected_skills"), list) or any(
        not isinstance(name, str) for name in raw.get("expected_skills", [])
    ):
        raise ValueError("expected_skills must be a list of names.")
    actions = raw.get("scripted_actions")
    if not isinstance(actions, list) or not actions:
        raise ValueError("scripted_actions must be a nonempty list.")
    for action in actions:
        if (
            not isinstance(action, dict)
            or not isinstance(action.get("tool"), str)
            or not isinstance(action.get("arguments"), dict)
        ):
            raise ValueError("Every scripted action needs a tool and arguments.")
    return deepcopy(raw)


def incident_context(incident: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"Incident ID: {incident['incident_id']}",
            f"Environment: {incident['environment']}",
            f"Service: {incident['service']}",
            f"Assigned user: {incident['assigned_user_id']}",
            f"Incident status: {incident['incident_status']}",
            f"Service health: {incident['service_health']}",
            f"Checkout error rate: {incident['checkout_error_rate_percent']}%",
            f"Current deployment: {incident['current_deployment']}",
            f"Last-known-good deployment: {incident['last_known_good_deployment']}",
            f"Rollback performed: {incident['rollback_performed']}",
            f"Recovery confirmed: {incident['recovery_confirmed']}",
        ]
    )
