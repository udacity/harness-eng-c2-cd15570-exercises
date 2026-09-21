"""Behavior checks for the expense policy hook; no API key is required."""

import copy
import json
import unittest
from pathlib import Path

from hooks import before_tool_call, validate_expense_submission


EXAMPLES = Path(__file__).resolve().parent / "examples"


def report_named(name: str) -> dict:
    return json.loads((EXAMPLES / f"{name}.json").read_text(encoding="utf-8"))


class ExpenseHookTests(unittest.TestCase):
    def test_supplied_scenarios(self) -> None:
        valid = validate_expense_submission(report_named("valid_expense"))
        self.assertTrue(valid.allowed)
        self.assertEqual(set(valid.checks), {
            "positive_amounts", "meal_limit", "manager_approval",
            "unique_receipts", "reported_total",
        })
        self.assertTrue(all(valid.checks.values()))

        multiple = validate_expense_submission(report_named("multiple_violations"))
        self.assertFalse(multiple.allowed)
        self.assertEqual(
            {name for name, passed in multiple.checks.items() if not passed},
            {"meal_limit", "manager_approval", "unique_receipts", "reported_total"},
        )
        self.assertTrue(multiple.violations)

        ambiguous = validate_expense_submission(report_named("ambiguous"))
        self.assertFalse(ambiguous.allowed)
        self.assertEqual(
            {name for name, passed in ambiguous.checks.items() if not passed},
            {"reported_total"},
        )

    def test_exact_meal_limit(self) -> None:
        report = report_named("valid_expense")
        report["expenses"][1]["amount"] = 100.00
        report["reported_total"] = 905.00
        self.assertTrue(validate_expense_submission(report).checks["meal_limit"])

        report["expenses"][1]["amount"] = 100.01
        report["reported_total"] = 905.01
        self.assertFalse(validate_expense_submission(report).checks["meal_limit"])

    def test_exact_approval_threshold(self) -> None:
        report = report_named("valid_expense")
        report["expenses"][0]["amount"] = 500.00
        report["reported_total"] = 940.00
        self.assertTrue(validate_expense_submission(report).checks["manager_approval"])

        report["expenses"][0]["amount"] = 500.01
        report["reported_total"] = 940.01
        self.assertFalse(validate_expense_submission(report).checks["manager_approval"])

        report["manager_approved"] = True
        self.assertTrue(validate_expense_submission(report).checks["manager_approval"])

    def test_positive_amount_and_receipts(self) -> None:
        report = report_named("valid_expense")
        report["expenses"][1]["amount"] = 0.00
        report["reported_total"] = 805.00
        self.assertFalse(validate_expense_submission(report).checks["positive_amounts"])

        report = report_named("valid_expense")
        report["expenses"][1]["receipt_id"] = report["expenses"][0]["receipt_id"]
        self.assertFalse(validate_expense_submission(report).checks["unique_receipts"])

        report = report_named("valid_expense")
        report["expenses"][1]["receipt_id"] = ""
        self.assertFalse(validate_expense_submission(report).checks["unique_receipts"])

    def test_invalid_money_values(self) -> None:
        for value in (True, "NaN", "Infinity", "not money", 0.001):
            with self.subTest(value=value):
                report = report_named("valid_expense")
                report["expenses"][0]["amount"] = value
                result = validate_expense_submission(report)
                self.assertFalse(result.allowed)
                self.assertFalse(result.checks["positive_amounts"])
                self.assertFalse(result.checks["reported_total"])

    def test_one_cent_total_difference(self) -> None:
        report = report_named("valid_expense")
        report["reported_total"] = 889.99
        self.assertFalse(validate_expense_submission(report).checks["reported_total"])

    def test_malformed_report_fails_closed(self) -> None:
        report = copy.deepcopy(report_named("valid_expense"))
        report["expenses"] = "not a list"
        result = validate_expense_submission(report)
        self.assertFalse(result.allowed)
        self.assertTrue(result.violations)

    def test_before_tool_call(self) -> None:
        report = report_named("valid_expense")
        self.assertTrue(before_tool_call("submit_expense_report", {"report": report}).allowed)
        self.assertFalse(before_tool_call("unknown_tool", {"report": report}).allowed)
        self.assertFalse(before_tool_call("submit_expense_report", {}).allowed)


if __name__ == "__main__":
    unittest.main()
