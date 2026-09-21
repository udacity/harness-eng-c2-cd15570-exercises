"""Deterministic policy checks run immediately before expense submission."""

from decimal import Decimal, InvalidOperation
from typing import Any

from models import HookResult


CENT = Decimal("0.01")
MEAL_LIMIT = Decimal("100.00")
APPROVAL_THRESHOLD = Decimal("500.00")


def _money(value: Any) -> Decimal | None:
    """Parse a finite dollar amount represented to the cent, without floats."""

    if isinstance(value, bool):
        return None
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount != amount.quantize(CENT):
            return None
        return amount
    except (InvalidOperation, TypeError, ValueError):
        return None


def check_positive_amounts(report: dict) -> list[str]:
    """Every line item must have a valid amount greater than zero."""

    violations = []
    for index, expense in enumerate(report["expenses"], start=1):
        amount = _money(expense.get("amount"))
        if amount is None or amount <= 0:
            violations.append(f"Expense {index} must have an amount greater than $0.00, to the cent.")
    return violations


def check_meal_limit(report: dict) -> list[str]:
    """A meal may cost at most $100.00."""

    violations = []
    for index, expense in enumerate(report["expenses"], start=1):
        if str(expense.get("category", "")).strip().lower() != "meal":
            continue
        amount = _money(expense.get("amount"))
        if amount is not None and amount > MEAL_LIMIT:
            violations.append(f"Meal expense {index} is ${amount:.2f}, above the $100.00 limit.")
    return violations


def check_manager_approval(report: dict) -> list[str]:
    """Any individual expense above $500.00 needs manager approval."""

    if report.get("manager_approved") is True:
        return []
    violations = []
    for index, expense in enumerate(report["expenses"], start=1):
        amount = _money(expense.get("amount"))
        if amount is not None and amount > APPROVAL_THRESHOLD:
            violations.append(
                f"Expense {index} is ${amount:.2f}, above $500.00, but manager approval is missing."
            )
    return violations


def check_unique_receipts(report: dict) -> list[str]:
    """A receipt ID may appear only once in a report."""

    seen = set()
    violations = []
    for index, expense in enumerate(report["expenses"], start=1):
        receipt_id = expense.get("receipt_id")
        if not isinstance(receipt_id, str) or not receipt_id.strip():
            violations.append(f"Expense {index} needs a receipt ID.")
        elif receipt_id in seen:
            violations.append(f"Receipt ID {receipt_id!r} is duplicated at expense {index}.")
        else:
            seen.add(receipt_id)
    return violations


def check_reported_total(report: dict) -> list[str]:
    """The reported total must equal the line-item sum exactly to the cent."""

    reported_total = _money(report.get("reported_total"))
    amounts = [_money(expense.get("amount")) for expense in report["expenses"]]
    if reported_total is None or any(amount is None for amount in amounts):
        return ["Reported total and every line-item amount must be valid dollar amounts to the cent."]
    actual_total = sum(amounts, Decimal("0.00"))
    if reported_total != actual_total:
        return [
            f"Reported total is ${reported_total:.2f}, but line items sum to ${actual_total:.2f}."
        ]
    return []


CHECKS = {
    "positive_amounts": check_positive_amounts,
    "meal_limit": check_meal_limit,
    "manager_approval": check_manager_approval,
    "unique_receipts": check_unique_receipts,
    "reported_total": check_reported_total,
}


def validate_expense_submission(report: dict) -> HookResult:
    """Run all five checks and combine their findings into one decision."""

    if not isinstance(report, dict):
        return HookResult(False, ["Submission must contain a report object."])
    expenses = report.get("expenses")
    if not isinstance(expenses, list) or any(not isinstance(item, dict) for item in expenses):
        return HookResult(False, ["Report expenses must be a list of expense objects."])

    violations: list[str] = []
    checks: dict[str, bool] = {}
    for name, check in CHECKS.items():
        findings = check(report)
        checks[name] = not findings
        violations.extend(findings)
    return HookResult(not violations, violations, checks)


def before_tool_call(tool_name: str, arguments: dict) -> HookResult:
    """Authorize a proposed expense submission before the tool is run."""

    if tool_name != "submit_expense_report":
        return HookResult(False, [f"Unsupported tool: {tool_name}."])
    if not isinstance(arguments, dict):
        return HookResult(False, ["Tool arguments must be an object containing a report."])
    return validate_expense_submission(arguments.get("report"))
