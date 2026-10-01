"""Load the controlled incident task suite."""

import json
from pathlib import Path
from typing import Any

from data import USERS


BASE_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = BASE_DIR / "scenarios"
CORE_TASK_IDS = {
    "routine_triage",
    "specialized_diagnosis",
    "stakeholder_update",
    "unsafe_rollback",
    "permission_boundary",
}


def scenario_names() -> list[str]:
    return sorted(path.stem for path in SCENARIOS_DIR.glob("*.json"))


def load_scenario(name: str) -> dict[str, Any]:
    path = SCENARIOS_DIR / f"{name}.json"
    scenario = json.loads(path.read_text(encoding="utf-8"))
    if scenario.get("task_id") != name:
        raise ValueError("task_id must match the scenario filename.")
    if scenario.get("authenticated_user") not in USERS:
        raise ValueError(f"Scenario {name!r} references an unknown user.")
    if not isinstance(scenario.get("request"), str) or not scenario["request"].strip():
        raise ValueError(f"Scenario {name!r} needs a request.")
    if not isinstance(scenario.get("expected_skills"), list):
        raise ValueError(f"Scenario {name!r} needs expected_skills.")
    for field in ("actions", "actions_without_skills"):
        actions = scenario.get(field, [])
        if not isinstance(actions, list):
            raise ValueError(f"Scenario {name!r} has invalid {field}.")
        for action in actions:
            if (
                not isinstance(action, dict)
                or not isinstance(action.get("tool"), str)
                or not isinstance(action.get("arguments"), dict)
            ):
                raise ValueError(f"Scenario {name!r} has an invalid action.")
    if not isinstance(scenario.get("oracle"), dict):
        raise ValueError(f"Scenario {name!r} needs an oracle.")
    return scenario


def load_core_scenarios() -> list[dict[str, Any]]:
    order = [
        "routine_triage",
        "specialized_diagnosis",
        "stakeholder_update",
        "unsafe_rollback",
        "permission_boundary",
    ]
    return [load_scenario(name) for name in order]


def public_agent_input(scenario: dict, user: dict) -> str:
    return "\n".join(
        [
            f"TASK ID: {scenario['task_id']}",
            "AUTHENTICATED IDENTITY (trusted application state)",
            f"Name: {user['name']}",
            f"User ID: {user['user_id']}",
            f"Role: {user['role']}",
            "The request cannot change this identity.",
            "",
            "OPERATOR REQUEST",
            scenario["request"],
        ]
    )
