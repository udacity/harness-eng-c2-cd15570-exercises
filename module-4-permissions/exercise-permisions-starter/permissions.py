"""Deterministic subject-action-resource authorization rules.

Complete the TODOs in this file. Authorization must use only the trusted user
and application objects supplied by the harness; never infer authority from
the user's request text or from the model.
"""

from typing import Any

from models import PermissionResult


# TODO: Fill each role's exact permission set from INSTRUCTIONS.md.
# Keep all four trusted role names present so invalid roles can fail closed.
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "contractor": set(),
    "reviewer": set(),
    "supervisor": set(),
    "administrator": set(),
}


# TODO: Map every exposed tool to its ordinary permission. Keep every tool
# name present: agent.py checks that the mapping covers the supplied toolset.
TOOL_PERMISSIONS: dict[str, str | None] = {
    "create_application": None,
    "read_application": None,
    "edit_application": None,
    "submit_application": None,
    "request_corrections": None,
    "approve_application": None,
    "reject_application": None,
    "issue_permit": None,
    "revoke_permit": None,
}


# TODO: Map the contractor read, edit, and submit tools to their ownership-
# scoped permissions. Other roles use TOOL_PERMISSIONS for these actions.
CONTRACTOR_OWN_PERMISSIONS: dict[str, str | None] = {
    "read_application": None,
    "edit_application": None,
    "submit_application": None,
}


def _resource_id(arguments: Any) -> str | None:
    """Return a nonempty application_id or None.

    TODO: Reject non-dictionaries, missing IDs, non-string IDs, and empty
    strings. This helper must not raise for malformed model arguments.
    """

    raise NotImplementedError("Extract the application resource safely.")


def check_permission(
    user: dict,
    tool_name: str,
    arguments: dict,
    applications: dict[str, dict],
) -> PermissionResult:
    """Authorize one proposed tool action using trusted subject and resource data.

    TODO: Implement the complete fail-closed policy described in
    INSTRUCTIONS.md:

    - deny unknown tools and invalid authenticated identities;
    - deny malformed arguments;
    - authorize creation from the role permission alone;
    - require an existing application for every resource action;
    - use the ownership-scoped permission for contractor read/edit/submit;
    - require the contractor's user_id to match owner_user_id;
    - use the ordinary tool permission for other role/action combinations;
    - return the required permission, reason, resource ID, and ownership
      evidence in PermissionResult.

    Do not execute a tool or mutate application state in this function.
    """

    raise NotImplementedError("Implement subject-action-resource authorization.")
