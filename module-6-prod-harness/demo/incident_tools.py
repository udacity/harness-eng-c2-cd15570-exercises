"""Simulated incident tools; policy and safety live in Hermes hooks."""

from collections.abc import Callable
from typing import Any


INCIDENT_PARAMETERS = {
    "type": "object",
    "properties": {"incident_id": {"type": "string"}},
    "required": ["incident_id"],
    "additionalProperties": False,
}

TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "get_incident": {
        "name": "get_incident",
        "description": "Read trusted incident status and assignment.",
        "parameters": INCIDENT_PARAMETERS,
    },
    "get_service_health": {
        "name": "get_service_health",
        "description": "Read a fresh checkout-api health snapshot.",
        "parameters": INCIDENT_PARAMETERS,
    },
    "get_deployment_history": {
        "name": "get_deployment_history",
        "description": "Read current and last-known-good deployment evidence.",
        "parameters": INCIDENT_PARAMETERS,
    },
    "query_service_logs": {
        "name": "query_service_logs",
        "description": "Read recent trusted checkout-api log evidence.",
        "parameters": INCIDENT_PARAMETERS,
    },
    "rollback_deployment": {
        "name": "rollback_deployment",
        "description": "Propose a production rollback for harness enforcement.",
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
    "update_incident_status": {
        "name": "update_incident_status",
        "description": "Propose an incident-status change for harness enforcement.",
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
}


def _exact(arguments: dict[str, Any], required: set[str]) -> None:
    if not isinstance(arguments, dict) or set(arguments) != required:
        raise ValueError("Tool arguments do not match the required schema.")
    if any(
        not isinstance(arguments[name], str) or not arguments[name].strip()
        for name in required
    ):
        raise ValueError("Every tool argument must be a nonempty string.")


def _same_incident(arguments: dict[str, Any], incident: dict[str, Any]) -> None:
    if arguments["incident_id"] != incident["incident_id"]:
        raise ValueError(f"Unknown incident: {arguments['incident_id']!r}.")


def get_incident(arguments: dict[str, Any], incident: dict[str, Any]) -> dict:
    _exact(arguments, {"incident_id"})
    _same_incident(arguments, incident)
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "service": incident["service"],
        "assigned_user_id": incident["assigned_user_id"],
        "incident_status": incident["incident_status"],
        "current_deployment": incident["current_deployment"],
    }


def get_service_health(arguments: dict[str, Any], incident: dict[str, Any]) -> dict:
    _exact(arguments, {"incident_id"})
    _same_incident(arguments, incident)
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "service_health": incident["service_health"],
        "checkout_error_rate_percent": incident["checkout_error_rate_percent"],
        "recovery_confirmed": incident["recovery_confirmed"],
    }


def get_deployment_history(
    arguments: dict[str, Any], incident: dict[str, Any]
) -> dict:
    _exact(arguments, {"incident_id"})
    _same_incident(arguments, incident)
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "deployments": incident["deployment_history"],
    }


def query_service_logs(arguments: dict[str, Any], incident: dict[str, Any]) -> dict:
    _exact(arguments, {"incident_id"})
    _same_incident(arguments, incident)
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "entries": incident["logs"],
    }


def rollback_deployment(
    arguments: dict[str, Any], incident: dict[str, Any]
) -> dict:
    _exact(arguments, {"incident_id", "target_version"})
    _same_incident(arguments, incident)
    previous = incident["current_deployment"]
    target = arguments["target_version"]
    incident["current_deployment"] = target
    incident["rollback_performed"] = True
    for deployment in incident["deployment_history"]:
        deployment["current"] = deployment["version"] == target
    incident["actions"].append(
        {"tool": "rollback_deployment", "target_version": target}
    )
    return {
        "status": "rolled_back",
        "executed": True,
        "incident_id": incident["incident_id"],
        "from_version": previous,
        "target_version": target,
    }


def update_incident_status(
    arguments: dict[str, Any], incident: dict[str, Any]
) -> dict:
    _exact(arguments, {"incident_id", "status"})
    _same_incident(arguments, incident)
    previous = incident["incident_status"]
    incident["incident_status"] = arguments["status"]
    incident["actions"].append(
        {"tool": "update_incident_status", "status": arguments["status"]}
    )
    return {
        "status": "updated",
        "executed": True,
        "incident_id": incident["incident_id"],
        "previous_status": previous,
        "new_status": arguments["status"],
    }


HANDLERS: dict[str, Callable[[dict[str, Any], dict[str, Any]], dict]] = {
    "get_incident": get_incident,
    "get_service_health": get_service_health,
    "get_deployment_history": get_deployment_history,
    "query_service_logs": query_service_logs,
    "rollback_deployment": rollback_deployment,
    "update_incident_status": update_incident_status,
}

assert set(TOOL_SCHEMAS) == set(HANDLERS)


def execute_tool(
    name: str, arguments: dict[str, Any], incident: dict[str, Any]
) -> dict[str, Any]:
    try:
        return HANDLERS[name](arguments, incident)
    except KeyError as error:
        raise ValueError(f"Unsupported incident tool: {name!r}.") from error
