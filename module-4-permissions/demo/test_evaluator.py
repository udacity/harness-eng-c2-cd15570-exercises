"""Regression tests for the Module 4 final-note evaluator contract."""

from types import SimpleNamespace
import unittest

from evaluator import criterion_passed, evaluate_final_note


class EvaluationContractTests(unittest.TestCase):
    incident = {"incident_id": "INC-2048"}

    @staticmethod
    def candidate(incident_id: str) -> str:
        return " ".join([incident_id, *(["word"] * 59)])

    def evaluate(self, candidate: str, review: str) -> dict:
        response = SimpleNamespace(output_text=review, usage=None)
        client = SimpleNamespace(
            responses=SimpleNamespace(create=lambda **_kwargs: response)
        )
        return evaluate_final_note(
            client,
            "scripted-fixture",
            self.incident,
            [],
            candidate,
        )

    def test_complete_incident_id_passes(self) -> None:
        result = self.evaluate(
            self.candidate("(INC-2048)"),
            "FACTUAL_GROUNDING: PASS\nUSEFUL_NEXT_STEP: PASS",
        )
        self.assertTrue(result["incident_id_passed"])
        self.assertTrue(result["passed"])

    def test_longer_incident_id_does_not_pass(self) -> None:
        result = self.evaluate(
            self.candidate("INC-20480"),
            "FACTUAL_GROUNDING: PASS\nUSEFUL_NEXT_STEP: PASS",
        )
        self.assertFalse(result["incident_id_passed"])
        self.assertFalse(result["passed"])

    def test_incident_id_with_identifier_suffix_does_not_pass(self) -> None:
        result = self.evaluate(
            self.candidate("INC-2048-extra"),
            "FACTUAL_GROUNDING: PASS\nUSEFUL_NEXT_STEP: PASS",
        )
        self.assertFalse(result["incident_id_passed"])

    def test_conflicting_criterion_lines_do_not_pass(self) -> None:
        review = (
            "FACTUAL_GROUNDING: PASS\n"
            "FACTUAL_GROUNDING: FAIL\n"
            "USEFUL_NEXT_STEP: PASS"
        )
        result = self.evaluate(self.candidate("INC-2048"), review)
        self.assertFalse(result["factual_grounding_passed"])
        self.assertFalse(result["passed"])

    def test_duplicate_pass_lines_do_not_pass(self) -> None:
        review = "FACTUAL_GROUNDING: PASS\nFACTUAL_GROUNDING: PASS"
        self.assertFalse(criterion_passed(review, "FACTUAL_GROUNDING"))

    def test_malformed_decision_does_not_pass(self) -> None:
        self.assertFalse(
            criterion_passed(
                "FACTUAL_GROUNDING: PASS with reservations",
                "FACTUAL_GROUNDING",
            )
        )

    def test_missing_criterion_does_not_pass(self) -> None:
        result = self.evaluate(
            self.candidate("INC-2048"),
            "FACTUAL_GROUNDING: PASS",
        )
        self.assertTrue(result["factual_grounding_passed"])
        self.assertFalse(result["useful_next_step_passed"])
        self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
