"""Simulated incident tools; optional harness boundaries live elsewhere."""

from collections.abc import Callable
from typing import Any


INCIDENT_ID_PARAMETERS = {
    "type": "object",
    "properties": {"incident_id": {"type": "string"}},
    "required": ["incident_id"],
    "additionalProperties": False,
}

BUSINESS_TOOLS = [
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
        "description": "Request a production rollback.",
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
        "description": "Request an incident-status change.",
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
]

TOOLS = BUSINESS_TOOLS


def _exact(arguments: dict, required: set[str]) -> None:
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be an object.")
    missing = required - arguments.keys()
    extra = arguments.keys() - required
    if missing or extra:
        raise ValueError("Tool arguments do not match the required schema.")
    for name in required:
        if not isinstance(arguments[name], str) or not arguments[name].strip():
            raise ValueError(f"{name} must be a nonempty string.")


def _same_incident(arguments: dict, incident: dict) -> None:
    if arguments["incident_id"] != incident.get("incident_id"):
        raise ValueError(f"Unknown incident: {arguments['incident_id']}.")


def get_incident(arguments: dict, incident: dict) -> dict:
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


def get_service_health(arguments: dict, incident: dict) -> dict:
    _exact(arguments, {"incident_id"})
    _same_incident(arguments, incident)
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "service_health": incident["service_health"],
        "checkout_error_rate_percent": incident["checkout_error_rate_percent"],
        "recovery_confirmed": incident["recovery_confirmed"],
    }


def get_deployment_history(arguments: dict, incident: dict) -> dict:
    _exact(arguments, {"incident_id"})
    _same_incident(arguments, incident)
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "deployments": incident["deployment_history"],
    }


def query_service_logs(arguments: dict, incident: dict) -> dict:
    _exact(arguments, {"incident_id"})
    _same_incident(arguments, incident)
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "entries": incident["logs"],
    }


def rollback_deployment(arguments: dict, incident: dict) -> dict:
    _exact(arguments, {"incident_id", "target_version"})
    _same_incident(arguments, incident)
    previous = incident["current_deployment"]
    target = arguments["target_version"]
    incident["current_deployment"] = target
    incident["rollback_performed"] = True
    for item in incident["deployment_history"]:
        item["current"] = item.get("version") == target
    incident["actions"].append(
        {"tool": "rollback_deployment", "target_version": target}
    )
    return {
        "status": "rolled_back",
        "incident_id": incident["incident_id"],
        "from_version": previous,
        "target_version": target,
    }


def update_incident_status(arguments: dict, incident: dict) -> dict:
    _exact(arguments, {"incident_id", "status"})
    _same_incident(arguments, incident)
    if arguments["status"] not in {"INVESTIGATING", "MONITORING", "RESOLVED"}:
        raise ValueError("Unsupported incident status.")
    previous = incident["incident_status"]
    incident["incident_status"] = arguments["status"]
    incident["actions"].append(
        {"tool": "update_incident_status", "status": arguments["status"]}
    )
    return {
        "status": "updated",
        "incident_id": incident["incident_id"],
        "previous_status": previous,
        "new_status": arguments["status"],
    }


TOOL_HANDLERS: dict[str, Callable[[dict, dict], dict]] = {
    "get_incident": get_incident,
    "get_service_health": get_service_health,
    "get_deployment_history": get_deployment_history,
    "query_service_logs": query_service_logs,
    "rollback_deployment": rollback_deployment,
    "update_incident_status": update_incident_status,
}

assert {tool["name"] for tool in BUSINESS_TOOLS} == set(TOOL_HANDLERS)


def execute_tool(tool_name: str, arguments: dict, incident: dict) -> dict[str, Any]:
    try:
        handler = TOOL_HANDLERS[tool_name]
    except KeyError as error:
        raise ValueError(f"Unsupported tool: {tool_name}.") from error
    return handler(arguments, incident)
