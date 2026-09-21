"""Expense tools; submission is deliberately free of policy checks."""


def get_expense_report(report: dict) -> dict:
    """Return report metadata and the indices of items to inspect."""

    return {
        "status": "found",
        "report_id": report.get("report_id"),
        "employee": report.get("employee"),
        "manager_approved": report.get("manager_approved"),
        "reported_total": report.get("reported_total"),
        "expense_count": len(report["expenses"]),
        "item_indices": list(range(1, len(report["expenses"]) + 1)),
        "next_step": "Retrieve each numbered item with get_expense_item before requesting submission.",
    }


def get_expense_item(report: dict, item_index: int) -> dict:
    """Return one numbered expense item, using one-based indices."""

    return {
        "status": "found",
        "report_id": report.get("report_id"),
        "item_index": item_index,
        "expense": report["expenses"][item_index - 1],
    }


def submit_expense_report(report: dict) -> dict:
    """Return a receipt for a submitted report without external side effects."""

    return {"status": "submitted", "report_id": report.get("report_id")}
