"""Deterministic subject-action-resource authorization rules."""

from typing import Any

from models import PermissionResult


ROLE_PERMISSIONS = {
    "contractor": {
        "permit.create",
        "permit.read_own",
        "permit.edit_own",
        "permit.submit_own",
    },
    "reviewer": {
        "permit.read",
        "permit.review",
        "permit.request_corrections",
    },
    "supervisor": {
        "permit.read",
        "permit.review",
        "permit.request_corrections",
        "permit.approve",
        "permit.reject",
    },
    "administrator": {
        "permit.read",
        "permit.review",
        "permit.request_corrections",
        "permit.approve",
        "permit.reject",
        "permit.issue",
        "permit.revoke",
    },
}


TOOL_PERMISSIONS = {
    "create_application": "permit.create",
    "read_application": "permit.read",
    "edit_application": "permit.edit",
    "submit_application": "permit.submit",
    "request_corrections": "permit.request_corrections",
    "approve_application": "permit.approve",
    "reject_application": "permit.reject",
    "issue_permit": "permit.issue",
    "revoke_permit": "permit.revoke",
}


CONTRACTOR_OWN_PERMISSIONS = {
    "read_application": "permit.read_own",
    "edit_application": "permit.edit_own",
    "submit_application": "permit.submit_own",
}


def _resource_id(arguments: Any) -> str | None:
    if not isinstance(arguments, dict):
        return None
    application_id = arguments.get("application_id")
    return application_id if isinstance(application_id, str) and application_id else None


def check_permission(
    user: dict,
    tool_name: str,
    arguments: dict,
    applications: dict[str, dict],
) -> PermissionResult:
    """Authorize one proposed tool action using trusted user and resource data."""

    if tool_name not in TOOL_PERMISSIONS:
        return PermissionResult(False, None, f"Unknown tool {tool_name!r}; authorization denied.")

    role = user.get("role") if isinstance(user, dict) else None
    user_id = user.get("user_id") if isinstance(user, dict) else None
    if role not in ROLE_PERMISSIONS or not isinstance(user_id, str):
        return PermissionResult(False, TOOL_PERMISSIONS[tool_name], "Authenticated identity is invalid.")
    if not isinstance(arguments, dict):
        return PermissionResult(False, TOOL_PERMISSIONS[tool_name], "Tool arguments must be an object.")

    role_permissions = ROLE_PERMISSIONS[role]
    if tool_name == "create_application":
        required = TOOL_PERMISSIONS[tool_name]
        allowed = required in role_permissions
        reason = (
            f"Role {role!r} has {required}."
            if allowed
            else f"Role {role!r} does not have {required}."
        )
        return PermissionResult(allowed, required, reason)

    required = (
        CONTRACTOR_OWN_PERMISSIONS[tool_name]
        if role == "contractor" and tool_name in CONTRACTOR_OWN_PERMISSIONS
        else TOOL_PERMISSIONS[tool_name]
    )
    application_id = _resource_id(arguments)
    if application_id is None:
        return PermissionResult(
            False,
            required,
            "A valid application_id is required for authorization.",
        )
    application = applications.get(application_id)
    if application is None:
        return PermissionResult(
            False,
            required,
            f"Application {application_id!r} does not exist; authorization denied.",
            resource_id=application_id,
        )

    if role == "contractor" and tool_name in CONTRACTOR_OWN_PERMISSIONS:
        owns_resource = application.get("owner_user_id") == user_id
        if not owns_resource:
            return PermissionResult(
                False,
                required,
                f"Contractor {user_id} does not own application {application_id}.",
                resource_id=application_id,
                ownership="no_match",
            )
        allowed = required in role_permissions
        reason = (
            f"Contractor {user_id} owns {application_id} and has {required}."
            if allowed
            else f"Role {role!r} does not have {required}."
        )
        return PermissionResult(
            allowed,
            required,
            reason,
            resource_id=application_id,
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
        resource_id=application_id,
    )
