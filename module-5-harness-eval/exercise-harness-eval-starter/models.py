"""Small shared result structures and exact-money helpers."""

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any


@dataclass(frozen=True, slots=True)
class PermissionResult:
    """A deterministic authorization decision for one proposed action."""

    allowed: bool
    required_permission: str | None
    reason: str


@dataclass(slots=True)
class HookResult:
    """The combined result of the deterministic checks relevant to a tool."""

    allowed: bool
    violations: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)
    codes: list[str] = field(default_factory=list)


def money_to_cents(value: Any) -> int:
    """Convert a dollar value to exact integer cents or reject it."""

    if isinstance(value, bool):
        raise ValueError("Money must be a dollar amount with at most two decimal places.")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError("Money must be a dollar amount with at most two decimal places.") from error
    if not amount.is_finite():
        raise ValueError("Money must be a finite dollar amount.")
    cents = amount * 100
    if cents != cents.to_integral_value():
        raise ValueError("Money must have at most two decimal places.")
    return int(cents)


def format_cents(cents: int) -> str:
    """Format integer cents as a JSON-friendly dollar string."""

    if type(cents) is not int:
        raise ValueError("Cents must be an integer.")
    sign = "-" if cents < 0 else ""
    absolute = abs(cents)
    return f"{sign}{absolute // 100}.{absolute % 100:02d}"
