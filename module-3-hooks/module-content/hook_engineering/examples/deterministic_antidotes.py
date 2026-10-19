"""Small pure antidotes illustrating exact threshold and state rules."""

from decimal import Decimal, InvalidOperation
from typing import Any


CENT = Decimal("0.01")
MEAL_LIMIT = Decimal("100.00")
APPROVAL_THRESHOLD = Decimal("500.00")


def money(value: Any) -> Decimal | None:
    """Return a finite cent-precise value, or None for invalid input."""

    if isinstance(value, bool):
        return None
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount != amount.quantize(CENT):
            return None
        return amount
    except (InvalidOperation, TypeError, ValueError):
        return None


def meal_limit_violation(category: Any, amount_value: Any) -> str | None:
    """Exactly 100.00 passes; 100.01 fails for a meal."""

    if str(category).strip().lower() != "meal":
        return None
    amount = money(amount_value)
    if amount is None:
        return "Meal amount must be a finite dollar value to the cent."
    if amount > MEAL_LIMIT:
        return f"Meal amount ${amount:.2f} exceeds $100.00."
    return None


def approval_violation(amount_value: Any, manager_approved: Any) -> str | None:
    """Only an amount above 500.00 needs explicit approval."""

    amount = money(amount_value)
    if amount is None:
        return "Expense amount must be a finite dollar value to the cent."
    if amount > APPROVAL_THRESHOLD and manager_approved is not True:
        return f"Expense ${amount:.2f} requires manager approval."
    return None


def resolution_violation(health: Any, recovery_confirmed: Any) -> str | None:
    """Resolution requires two exact trusted-state conditions."""

    if health == "HEALTHY" and recovery_confirmed is True:
        return None
    return "Resolution requires HEALTHY service and confirmed recovery."
