"""Trusted subject-action-resource authorization for Hermes tool proposals."""

from dataclasses import asdict, dataclass
from typing import Any


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
}

TOOL_PERMISSIONS = {
    "get_incident": "incident.read",
    "get_service_health": "service_health.read",
    "get_deployment_history": "deployment.read",
    "query_service_logs": "logs.read",
    "rollback_deployment": "deployment.rollback",
    "update_incident_status": "incident.status.update",
}

ASSIGNED_PERMISSIONS = {
    "get_incident": "incident.read_assigned",
    "get_service_health": "service_health.read_assigned",
    "get_deployment_history": "deployment.read_assigned",
    "query_service_logs": "logs.read_assigned",
}


@dataclass(frozen=True, slots=True)
class PermissionDecision:
    allowed: bool
    required_permission: str | None
    rule: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def decide(
    user: dict[str, str],
    tool_name: str,
    arguments: dict[str, Any],
    incident: dict[str, Any],
) -> PermissionDecision:
    ordinary = TOOL_PERMISSIONS.get(tool_name)
    if ordinary is None:
        return PermissionDecision(False, None, "default_deny", "Unknown tool.")
    role = user.get("role")
    user_id = user.get("user_id")
    if (
        not isinstance(role, str)
        or role not in ROLE_PERMISSIONS
        or not isinstance(user_id, str)
        or not user_id.strip()
    ):
        return PermissionDecision(
            False, ordinary, "identity.invalid", "Trusted identity is invalid."
        )
    incident_id = arguments.get("incident_id")
    if incident_id != incident.get("incident_id"):
        return PermissionDecision(
            False,
            ordinary,
            "resource.known_incident",
            "The requested incident does not exist.",
        )
    if role == "support_engineer" and tool_name in ASSIGNED_PERMISSIONS:
        required = ASSIGNED_PERMISSIONS[tool_name]
        if incident.get("assigned_user_id") != user_id:
            return PermissionDecision(
                False,
                required,
                "resource.assigned_user",
                "The support engineer is not assigned to this incident.",
            )
        return PermissionDecision(
            required in ROLE_PERMISSIONS[role],
            required,
            "resource.assigned_user",
            "The support engineer is assigned and has assigned-read authority.",
        )
    allowed = ordinary in ROLE_PERMISSIONS[role]
    return PermissionDecision(
        allowed,
        ordinary,
        "role.permission",
        (
            f"Role {role!r} has {ordinary}."
            if allowed
            else f"Role {role!r} does not have {ordinary}."
        ),
    )

