"""Deterministic role-based authorization for store actions."""

from typing import Any

from models import PermissionResult, format_cents, money_to_cents


ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "support_agent": frozenset(
        {
            "order.read",
            "return.create",
            "store_credit.issue",
            "refund.issue_up_to_100",
            "return.update",
        }
    ),
    "supervisor": frozenset(
        {
            "order.read",
            "return.create",
            "store_credit.issue",
            "refund.issue_up_to_500",
            "return.update",
        }
    ),
    "administrator": frozenset(
        {
            "order.read",
            "return.create",
            "store_credit.issue",
            "refund.issue",
            "refund.override",
            "return.update",
        }
    ),
}


TOOL_PERMISSIONS = {
    "lookup_order": "order.read",
    "create_return": "return.create",
    "issue_refund": "refund.issue",
    "issue_store_credit": "store_credit.issue",
    "update_return": "return.update",
    "get_return_status": "order.read",
}


REFUND_SCOPES: dict[str, tuple[str, int | None]] = {
    "support_agent": ("refund.issue_up_to_100", 10000),
    "supervisor": ("refund.issue_up_to_500", 50000),
    "administrator": ("refund.issue", None),
}


def check_permission(
    user: dict,
    tool_name: str,
    arguments: dict,
    store: dict | None = None,
) -> PermissionResult:
    """Authorize one proposed action from trusted identity and arguments.

    ``store`` is accepted for a uniform dispatcher interface. These role rules
    do not depend on mutable store state.
    """

    del store
    if tool_name not in TOOL_PERMISSIONS:
        return PermissionResult(False, None, f"Unknown tool {tool_name!r}; authorization denied.")
    if not isinstance(user, dict):
        return PermissionResult(False, TOOL_PERMISSIONS[tool_name], "Authenticated identity is invalid.")
    role = user.get("role")
    user_id = user.get("user_id")
    if role not in ROLE_PERMISSIONS or not isinstance(user_id, str) or not user_id:
        return PermissionResult(False, TOOL_PERMISSIONS[tool_name], "Authenticated identity is invalid.")
    if not isinstance(arguments, dict):
        return PermissionResult(False, TOOL_PERMISSIONS[tool_name], "Tool arguments must be an object.")

    if tool_name == "issue_refund":
        required, limit_cents = REFUND_SCOPES[role]
        try:
            amount_cents = money_to_cents(arguments.get("refund_amount"))
        except ValueError as error:
            return PermissionResult(False, required, f"Cannot authorize refund: {error}")
        if required not in ROLE_PERMISSIONS[role]:
            return PermissionResult(False, required, f"Role {role!r} does not have {required}.")
        if limit_cents is not None and amount_cents > limit_cents:
            return PermissionResult(
                False,
                required,
                f"Role {role!r} may issue refunds only up to ${format_cents(limit_cents)}.",
            )
        return PermissionResult(True, required, f"Role {role!r} may issue this refund amount.")

    required = TOOL_PERMISSIONS[tool_name]
    allowed = required in ROLE_PERMISSIONS[role]
    reason = (
        f"Role {role!r} has {required}."
        if allowed
        else f"Role {role!r} does not have {required}."
    )
    return PermissionResult(allowed, required, reason)
