"""The four deterministic validity checks used before store mutations."""

from collections.abc import Callable

from models import HookResult, format_cents, money_to_cents


Check = Callable[[dict, dict], list[str]]


def _order(arguments: dict, store: dict) -> dict:
    order_id = arguments.get("order_id")
    if not isinstance(order_id, str) or not order_id:
        raise ValueError("A nonempty order_id is required for validation.")
    try:
        return store["orders"][order_id]
    except (KeyError, TypeError) as error:
        raise ValueError(f"Unknown order: {order_id}.") from error


def check_nonpositive_refund(arguments: dict, store: dict) -> list[str]:
    """A refund must be greater than zero."""

    del store
    amount_cents = money_to_cents(arguments.get("refund_amount"))
    if amount_cents <= 0:
        return ["Refund amount must be greater than $0.00."]
    return []


def check_refund_overpayment(arguments: dict, store: dict) -> list[str]:
    """A refund may not exceed the original amount paid."""

    order = _order(arguments, store)
    amount_cents = money_to_cents(arguments.get("refund_amount"))
    paid_cents = order["amount_paid_cents"]
    if amount_cents > paid_cents:
        return [
            f"Refund ${format_cents(amount_cents)} exceeds the "
            f"${format_cents(paid_cents)} originally paid."
        ]
    return []


def check_duplicate_refund(arguments: dict, store: dict) -> list[str]:
    """An order that was already refunded may not be refunded again."""

    order = _order(arguments, store)
    if order.get("refund_issued") is True:
        return [f"Order {order['order_id']} has already been refunded."]
    return []


def check_invalid_quantity(arguments: dict, store: dict) -> list[str]:
    """A return quantity may not exceed the quantity purchased for the SKU."""

    order = _order(arguments, store)
    sku = arguments.get("sku")
    quantity = arguments.get("quantity")
    if not isinstance(sku, str) or not sku:
        raise ValueError("A nonempty sku is required for validation.")
    if type(quantity) is not int:
        raise ValueError("Return quantity must be an integer.")
    item = next((candidate for candidate in order["items"] if candidate["sku"] == sku), None)
    if item is None:
        raise ValueError(f"SKU {sku!r} is not part of order {order['order_id']}.")
    if quantity > item["quantity"]:
        return [
            f"Return quantity {quantity} exceeds the purchased quantity "
            f"{item['quantity']} for {sku}."
        ]
    return []


HOOKS_BY_TOOL: dict[str, tuple[tuple[str, Check], ...]] = {
    "issue_refund": (
        ("nonpositive_refund", check_nonpositive_refund),
        ("refund_overpayment", check_refund_overpayment),
        ("duplicate_refund", check_duplicate_refund),
    ),
    "create_return": (("invalid_quantity", check_invalid_quantity),),
}


def run_before_tool_hooks(tool_name: str, arguments: dict, store: dict) -> HookResult:
    """Run only the deterministic checks that apply to the proposed tool."""

    if not isinstance(arguments, dict):
        return HookResult(False, ["Tool arguments must be an object."], {}, ["invalid_arguments"])

    violations: list[str] = []
    checks: dict[str, bool] = {}
    codes: list[str] = []
    for code, check in HOOKS_BY_TOOL.get(tool_name, ()):
        try:
            findings = check(arguments, store)
        except (KeyError, TypeError, ValueError) as error:
            findings = [f"Validation could not be completed: {error}"]
        passed = not findings
        checks[code] = passed
        if not passed:
            codes.append(code)
            violations.extend(findings)
    return HookResult(not violations, violations, checks, codes)


# The harness calls this alias immediately before executing a business tool.
before_tool_call = run_before_tool_hooks

