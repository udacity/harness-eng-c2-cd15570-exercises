"""Illustrative least-privilege catalog shaping for Module 4.

Filtering is defense in depth. Every invocation still needs a fresh runtime
authorization decision because a visible tool can target different resources.
"""

from dataclasses import dataclass
from typing import Any


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


@dataclass(frozen=True)
class TrustedPrincipal:
    user_id: str
    role: str


def potential_permission(principal: TrustedPrincipal, tool_name: str) -> str | None:
    """Return the permission that could make a tool useful to this role."""

    if principal.role == "contractor" and tool_name in CONTRACTOR_OWN_PERMISSIONS:
        return CONTRACTOR_OWN_PERMISSIONS[tool_name]
    return TOOL_PERMISSIONS.get(tool_name)


def permitted_tool_catalog(
    principal: TrustedPrincipal,
    all_tools: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Offer only tools supported by current trusted role entitlements."""

    grants = ROLE_PERMISSIONS.get(principal.role)
    if grants is None:
        return []

    visible: list[dict[str, Any]] = []
    for tool in all_tools:
        name = tool.get("name")
        if not isinstance(name, str):
            continue
        required = potential_permission(principal, name)
        if required is not None and required in grants:
            visible.append(tool)
    return visible


def assert_catalog_coverage(all_tools: list[dict[str, Any]]) -> None:
    """Fail deployment when a dispatchable tool lacks an authorization rule."""

    names = {tool.get("name") for tool in all_tools}
    if names != set(TOOL_PERMISSIONS):
        missing_policy = names - set(TOOL_PERMISSIONS)
        stale_policy = set(TOOL_PERMISSIONS) - names
        raise RuntimeError(
            f"Tool/policy mismatch: missing={sorted(missing_policy)!r}, "
            f"stale={sorted(stale_policy)!r}"
        )


if __name__ == "__main__":
    tools = [{"name": name} for name in TOOL_PERMISSIONS]
    assert_catalog_coverage(tools)
    alex = TrustedPrincipal(user_id="USR-101", role="contractor")
    assert [tool["name"] for tool in permitted_tool_catalog(alex, tools)] == [
        "create_application",
        "read_application",
        "edit_application",
        "submit_application",
    ]
