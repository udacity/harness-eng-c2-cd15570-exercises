"""Regression tests for strict evaluator parsing and exact incident IDs."""

from __future__ import annotations

import unittest

from harness.loops.external_evaluation_loop import (
    deterministic_criterion_passed,
    evaluate_deterministic_criteria,
    inferential_criterion_passed,
)
from harness.loops.self_evaluation_loop import criterion_passed, passed
from harness.models import Scenario


VALID_SELF_EVALUATION = """
WORD_COUNT: PASS
INCIDENT_ID: PASS
FACTUAL_GROUNDING: PASS
USEFUL_NEXT_STEP: PASS
VERDICT: PASS
FEEDBACK: All criteria passed.
""".strip()


class ExactIncidentIdTests(unittest.TestCase):
    scenario = Scenario(
        scenario_id="test",
        request="Investigate INC-2048.",
        authenticated_user={
            "user_id": "OPS-1",
            "name": "Test Operator",
            "role": "responder",
        },
        incident={"incident_id": "INC-2048"},
        response_requirements={"required_word_count": 4},
    )

    def test_complete_incident_id_passes(self) -> None:
        accepted, results = evaluate_deterministic_criteria(
            "Status (INC-2048) remains degraded.", self.scenario
        )
        self.assertTrue(accepted)
        self.assertIn("INCIDENT_ID: PASS", results[1])

    def test_longer_numeric_incident_id_does_not_pass(self) -> None:
        accepted, results = evaluate_deterministic_criteria(
            "Status INC-20480 remains degraded.", self.scenario
        )
        self.assertFalse(accepted)
        self.assertIn("INCIDENT_ID: FAIL", results[1])

    def test_incident_id_with_identifier_suffix_does_not_pass(self) -> None:
        accepted, _ = evaluate_deterministic_criteria(
            "Status INC-2048-extra remains degraded.", self.scenario
        )
        self.assertFalse(accepted)

    def test_duplicate_deterministic_results_are_rejected(self) -> None:
        results = [
            "INCIDENT_ID: PASS (expected INC-2048)",
            "INCIDENT_ID: FAIL (expected INC-2048)",
        ]
        self.assertFalse(
            deterministic_criterion_passed(results, "INCIDENT_ID")
        )


class SelfEvaluationContractTests(unittest.TestCase):
    def test_one_consistent_pass_is_accepted(self) -> None:
        self.assertTrue(passed(VALID_SELF_EVALUATION))

    def test_conflicting_verdicts_are_rejected(self) -> None:
        self.assertFalse(passed(VALID_SELF_EVALUATION + "\nVERDICT: FAIL"))

    def test_duplicate_pass_verdicts_are_rejected(self) -> None:
        self.assertFalse(passed(VALID_SELF_EVALUATION + "\nVERDICT: PASS"))

    def test_malformed_verdict_is_rejected(self) -> None:
        evaluation = VALID_SELF_EVALUATION.replace(
            "VERDICT: PASS", "VERDICT: PASS because every check passed"
        )
        self.assertFalse(passed(evaluation))

    def test_pass_verdict_cannot_override_failed_criterion(self) -> None:
        evaluation = VALID_SELF_EVALUATION.replace(
            "FACTUAL_GROUNDING: PASS", "FACTUAL_GROUNDING: FAIL"
        )
        self.assertFalse(passed(evaluation))

    def test_duplicate_criterion_is_rejected_in_comparison(self) -> None:
        evaluation = VALID_SELF_EVALUATION + "\nINCIDENT_ID: FAIL"
        self.assertFalse(criterion_passed(evaluation, "INCIDENT_ID"))


class IndependentEvaluationContractTests(unittest.TestCase):
    def test_one_exact_pass_per_criterion_is_accepted(self) -> None:
        evaluation = (
            "FACTUAL_GROUNDING: PASS\n"
            "USEFUL_NEXT_STEP: PASS\n"
            "FEEDBACK: All inferential criteria passed."
        )
        self.assertTrue(
            inferential_criterion_passed(evaluation, "FACTUAL_GROUNDING")
        )
        self.assertTrue(
            inferential_criterion_passed(evaluation, "USEFUL_NEXT_STEP")
        )

    def test_conflicting_criterion_lines_are_rejected(self) -> None:
        evaluation = (
            "FACTUAL_GROUNDING: PASS\n"
            "FACTUAL_GROUNDING: FAIL\n"
            "USEFUL_NEXT_STEP: PASS"
        )
        self.assertFalse(
            inferential_criterion_passed(evaluation, "FACTUAL_GROUNDING")
        )

    def test_malformed_criterion_decision_is_rejected(self) -> None:
        self.assertFalse(
            inferential_criterion_passed(
                "FACTUAL_GROUNDING: PASS with reservations",
                "FACTUAL_GROUNDING",
            )
        )


if __name__ == "__main__":
    unittest.main()
