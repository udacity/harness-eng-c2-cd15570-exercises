"""Simulated incident tools; authorization and safety policy live elsewhere."""

from collections.abc import Callable
from typing import Any

from data import USERS


INCIDENT_ID_PARAMETERS = {
    "type": "object",
    "properties": {"incident_id": {"type": "string"}},
    "required": ["incident_id"],
    "additionalProperties": False,
}

TOOLS = [
    {
        "type": "function",
        "name": "get_incident",
        "description": "Get the trusted incident header and assignment.",
        "parameters": INCIDENT_ID_PARAMETERS,
    },
    {
        "type": "function",
        "name": "get_service_health",
        "description": "Get a fresh service-health snapshot.",
        "parameters": INCIDENT_ID_PARAMETERS,
    },
    {
        "type": "function",
        "name": "get_deployment_history",
        "description": "Get deployment and last-known-good evidence.",
        "parameters": INCIDENT_ID_PARAMETERS,
    },
    {
        "type": "function",
        "name": "query_service_logs",
        "description": "Get recent trusted checkout-api log evidence.",
        "parameters": INCIDENT_ID_PARAMETERS,
    },
    {
        "type": "function",
        "name": "rollback_deployment",
        "description": "Request a production rollback decision from the harness.",
        "parameters": {
            "type": "object",
            "properties": {
                "incident_id": {"type": "string"},
                "target_version": {"type": "string"},
            },
            "required": ["incident_id", "target_version"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "update_incident_status",
        "description": "Request an incident-status change from the harness.",
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
    },
    {
        "type": "function",
        "name": "reassign_incident",
        "description": "Assign the incident to another trusted operations user.",
        "parameters": {
            "type": "object",
            "properties": {
                "incident_id": {"type": "string"},
                "new_assignee_user_id": {"type": "string"},
            },
            "required": ["incident_id", "new_assignee_user_id"],
            "additionalProperties": False,
        },
    },
]


def _exact_arguments(arguments: dict, required: set[str]) -> None:
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be an object.")
    missing = required - arguments.keys()
    unexpected = arguments.keys() - required
    if missing:
        raise ValueError(f"Missing required arguments: {', '.join(sorted(missing))}.")
    if unexpected:
        raise ValueError(f"Unexpected arguments: {', '.join(sorted(unexpected))}.")
    for name in required:
        if not isinstance(arguments[name], str) or not arguments[name].strip():
            raise ValueError(f"{name} must be a nonempty string.")


def _incident(arguments: dict, incident: dict) -> None:
    if arguments["incident_id"] != incident.get("incident_id"):
        raise ValueError(f"Unknown incident: {arguments['incident_id']}.")


def _get_incident(arguments: dict, incident: dict) -> dict:
    _exact_arguments(arguments, {"incident_id"})
    _incident(arguments, incident)
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "environment": incident["environment"],
        "service": incident["service"],
        "assigned_user_id": incident["assigned_user_id"],
        "incident_status": incident["incident_status"],
        "current_deployment": incident["current_deployment"],
    }


def _get_health(arguments: dict, incident: dict) -> dict:
    _exact_arguments(arguments, {"incident_id"})
    _incident(arguments, incident)
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "service_health": incident["service_health"],
        "checkout_error_rate_percent": incident["checkout_error_rate_percent"],
        "recovery_confirmed": incident["recovery_confirmed"],
    }


def _get_deployments(arguments: dict, incident: dict) -> dict:
    _exact_arguments(arguments, {"incident_id"})
    _incident(arguments, incident)
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "deployments": incident["deployment_history"],
    }


def _get_logs(arguments: dict, incident: dict) -> dict:
    _exact_arguments(arguments, {"incident_id"})
    _incident(arguments, incident)
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "entries": incident["logs"],
    }


def _rollback(arguments: dict, incident: dict) -> dict:
    _exact_arguments(arguments, {"incident_id", "target_version"})
    _incident(arguments, incident)
    previous = incident["current_deployment"]
    target = arguments["target_version"]
    incident["current_deployment"] = target
    incident["rollback_performed"] = True
    for deployment in incident["deployment_history"]:
        deployment["current"] = deployment.get("version") == target
    action = {
        "tool": "rollback_deployment",
        "from_version": previous,
        "target_version": target,
    }
    incident["actions"].append(action)
    return {"status": "rolled_back", "incident_id": incident["incident_id"], **action}


def _update_status(arguments: dict, incident: dict) -> dict:
    _exact_arguments(arguments, {"incident_id", "status"})
    _incident(arguments, incident)
    if arguments["status"] not in {"INVESTIGATING", "MONITORING", "RESOLVED"}:
        raise ValueError("Unsupported incident status.")
    previous = incident["incident_status"]
    incident["incident_status"] = arguments["status"]
    action = {
        "tool": "update_incident_status",
        "previous_status": previous,
        "new_status": arguments["status"],
    }
    incident["actions"].append(action)
    return {"status": "updated", "incident_id": incident["incident_id"], **action}


def _reassign(arguments: dict, incident: dict) -> dict:
    _exact_arguments(arguments, {"incident_id", "new_assignee_user_id"})
    _incident(arguments, incident)
    known_ids = {user["user_id"] for user in USERS.values()}
    target = arguments["new_assignee_user_id"]
    if target not in known_ids:
        raise ValueError(f"Unknown assignee: {target}.")
    previous = incident["assigned_user_id"]
    incident["assigned_user_id"] = target
    action = {
        "tool": "reassign_incident",
        "previous_assignee_user_id": previous,
        "new_assignee_user_id": target,
    }
    incident["actions"].append(action)
    return {"status": "reassigned", "incident_id": incident["incident_id"], **action}


TOOL_HANDLERS: dict[str, Callable[[dict, dict], dict]] = {
    "get_incident": _get_incident,
    "get_service_health": _get_health,
    "get_deployment_history": _get_deployments,
    "query_service_logs": _get_logs,
    "rollback_deployment": _rollback,
    "update_incident_status": _update_status,
    "reassign_incident": _reassign,
}

assert {tool["name"] for tool in TOOLS} == set(TOOL_HANDLERS)


def execute_tool(tool_name: str, arguments: dict, incident: dict) -> dict[str, Any]:
    """Dispatch an allowlisted tool without performing authorization or policy."""

    try:
        handler = TOOL_HANDLERS[tool_name]
    except KeyError as error:
        raise ValueError(f"Unsupported tool: {tool_name}.") from error
    return handler(arguments, incident)
