"""Deterministic subject-action-resource authorization rules."""

from typing import Any

from models import PermissionResult


ROLE_PERMISSIONS = {
    "support_engineer": {
        "incident.read_assigned",
        "service_health.read_assigned",
        "deployment.read_assigned",
        "logs.read_assigned",
    },
    "responder": {
        "incident.read",
        "service_health.read",
        "deployment.read",
        "logs.read",
        "deployment.rollback",
    },
    "incident_commander": {
        "incident.read",
        "service_health.read",
        "deployment.read",
        "logs.read",
        "deployment.rollback",
        "incident.status.update",
    },
    "administrator": {
        "incident.read",
        "service_health.read",
        "deployment.read",
        "logs.read",
        "deployment.rollback",
        "incident.status.update",
        "incident.reassign",
    },
}


TOOL_PERMISSIONS = {
    "get_incident": "incident.read",
    "get_service_health": "service_health.read",
    "get_deployment_history": "deployment.read",
    "query_service_logs": "logs.read",
    "rollback_deployment": "deployment.rollback",
    "update_incident_status": "incident.status.update",
    "reassign_incident": "incident.reassign",
}


SUPPORT_ASSIGNED_PERMISSIONS = {
    "get_incident": "incident.read_assigned",
    "get_service_health": "service_health.read_assigned",
    "get_deployment_history": "deployment.read_assigned",
    "query_service_logs": "logs.read_assigned",
}


def _resource_id(arguments: Any) -> str | None:
    if not isinstance(arguments, dict):
        return None
    incident_id = arguments.get("incident_id")
    return incident_id if isinstance(incident_id, str) and incident_id else None


def check_permission(
    user: dict,
    tool_name: str,
    arguments: dict,
    incident: dict,
) -> PermissionResult:
    """Authorize one proposed action using trusted user and incident data."""

    if tool_name not in TOOL_PERMISSIONS:
        return PermissionResult(
            False, None, f"Unknown tool {tool_name!r}; authorization denied."
        )

    role = user.get("role") if isinstance(user, dict) else None
    user_id = user.get("user_id") if isinstance(user, dict) else None
    ordinary_permission = TOOL_PERMISSIONS[tool_name]
    if role not in ROLE_PERMISSIONS or not isinstance(user_id, str):
        return PermissionResult(
            False, ordinary_permission, "Authenticated identity is invalid."
        )
    if not isinstance(arguments, dict):
        return PermissionResult(
            False, ordinary_permission, "Tool arguments must be an object."
        )

    required = (
        SUPPORT_ASSIGNED_PERMISSIONS[tool_name]
        if role == "support_engineer" and tool_name in SUPPORT_ASSIGNED_PERMISSIONS
        else ordinary_permission
    )
    incident_id = _resource_id(arguments)
    if incident_id is None:
        return PermissionResult(
            False,
            required,
            "A valid incident_id is required for authorization.",
        )
    if incident_id != incident.get("incident_id"):
        return PermissionResult(
            False,
            required,
            f"Incident {incident_id!r} does not exist; authorization denied.",
            resource_id=incident_id,
        )

    role_permissions = ROLE_PERMISSIONS[role]
    if role == "support_engineer" and tool_name in SUPPORT_ASSIGNED_PERMISSIONS:
        assigned = incident.get("assigned_user_id") == user_id
        if not assigned:
            return PermissionResult(
                False,
                required,
                f"Support engineer {user_id} is not assigned to incident {incident_id}.",
                resource_id=incident_id,
                ownership="no_match",
            )
        allowed = required in role_permissions
        reason = (
            f"Support engineer {user_id} is assigned to {incident_id} and has {required}."
            if allowed
            else f"Role {role!r} does not have {required}."
        )
        return PermissionResult(
            allowed,
            required,
            reason,
            resource_id=incident_id,
            ownership="match",
        )

    allowed = required in role_permissions
    reason = (
        f"Role {role!r} has {required}."
        if allowed
        else f"Role {role!r} does not have {required}."
    )
    return PermissionResult(
        allowed,
        required,
        reason,
        resource_id=incident_id,
    )
