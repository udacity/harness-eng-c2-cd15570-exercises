"""Regression tests for strict evaluator parsing and exact case-ID checks."""

from __future__ import annotations

import sys
from types import ModuleType
import unittest


try:
    import openai  # noqa: F401
except ModuleNotFoundError:
    openai_stub = ModuleType("openai")
    openai_stub.OpenAI = object
    sys.modules["openai"] = openai_stub

from harness.loops.external_evaluation_loop import (  # noqa: E402
    deterministic_criterion_passed,
    evaluate_deterministic_criteria,
    inferential_criterion_passed,
)
from harness.loops.self_evaluation_loop import passed  # noqa: E402


VALID_SELF_EVALUATION = """
WORD_COUNT: PASS
CASE_ID: PASS
POLICY_COMPLIANCE: PASS
USEFUL_NEXT_STEP: PASS
VERDICT: PASS
FEEDBACK: All criteria passed.
""".strip()


class ExactCaseIdTests(unittest.TestCase):
    customer_case = "- **Case ID:** CASE-1842"

    @staticmethod
    def candidate(case_id: str) -> str:
        return " ".join([case_id, *(["word"] * 99)])

    def test_complete_case_id_passes(self) -> None:
        accepted, results = evaluate_deterministic_criteria(
            self.candidate("(CASE-1842)"), self.customer_case
        )
        self.assertTrue(accepted)
        self.assertIn("CASE_ID: PASS", results[1])

    def test_longer_numeric_case_id_does_not_pass(self) -> None:
        accepted, results = evaluate_deterministic_criteria(
            self.candidate("CASE-18420"), self.customer_case
        )
        self.assertFalse(accepted)
        self.assertIn("CASE_ID: FAIL", results[1])

    def test_case_id_with_identifier_suffix_does_not_pass(self) -> None:
        accepted, _ = evaluate_deterministic_criteria(
            self.candidate("CASE-1842-extra"), self.customer_case
        )
        self.assertFalse(accepted)

    def test_duplicate_deterministic_results_are_rejected(self) -> None:
        results = [
            "CASE_ID: PASS (expected CASE-1842)",
            "CASE_ID: FAIL (expected CASE-1842)",
        ]
        self.assertFalse(deterministic_criterion_passed(results, "CASE_ID"))


class SelfEvaluationContractTests(unittest.TestCase):
    def test_one_consistent_pass_is_accepted(self) -> None:
        self.assertTrue(passed(VALID_SELF_EVALUATION))

    def test_conflicting_verdicts_are_rejected(self) -> None:
        evaluation = VALID_SELF_EVALUATION + "\nVERDICT: FAIL"
        self.assertFalse(passed(evaluation))

    def test_duplicate_pass_verdicts_are_rejected(self) -> None:
        evaluation = VALID_SELF_EVALUATION + "\nVERDICT: PASS"
        self.assertFalse(passed(evaluation))

    def test_malformed_verdict_is_rejected(self) -> None:
        evaluation = VALID_SELF_EVALUATION.replace(
            "VERDICT: PASS", "VERDICT: PASS because every check passed"
        )
        self.assertFalse(passed(evaluation))

    def test_pass_verdict_cannot_override_failed_criterion(self) -> None:
        evaluation = VALID_SELF_EVALUATION.replace(
            "CASE_ID: PASS", "CASE_ID: FAIL"
        )
        self.assertFalse(passed(evaluation))

    def test_missing_criterion_is_rejected(self) -> None:
        evaluation = VALID_SELF_EVALUATION.replace("CASE_ID: PASS\n", "")
        self.assertFalse(passed(evaluation))


class IndependentEvaluationContractTests(unittest.TestCase):
    def test_one_exact_pass_per_criterion_is_accepted(self) -> None:
        evaluation = (
            "POLICY_COMPLIANCE: PASS\n"
            "USEFUL_NEXT_STEP: PASS\n"
            "FEEDBACK: All inferential criteria passed."
        )
        self.assertTrue(
            inferential_criterion_passed(evaluation, "POLICY_COMPLIANCE")
        )
        self.assertTrue(
            inferential_criterion_passed(evaluation, "USEFUL_NEXT_STEP")
        )

    def test_conflicting_criterion_lines_are_rejected(self) -> None:
        evaluation = (
            "POLICY_COMPLIANCE: PASS\n"
            "POLICY_COMPLIANCE: FAIL\n"
            "USEFUL_NEXT_STEP: PASS"
        )
        self.assertFalse(
            inferential_criterion_passed(evaluation, "POLICY_COMPLIANCE")
        )

    def test_malformed_criterion_decision_is_rejected(self) -> None:
        self.assertFalse(
            inferential_criterion_passed(
                "POLICY_COMPLIANCE: PASS with reservations",
                "POLICY_COMPLIANCE",
            )
        )


if __name__ == "__main__":
    unittest.main()
