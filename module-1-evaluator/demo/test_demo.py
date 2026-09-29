"""Deterministic tests for the Module 1 incident-response demo."""

import unittest
from pathlib import Path
from types import SimpleNamespace

from harness.evaluation import SELF_CRITERIA, deterministic_checks, parse_review
from harness.loops import run_basic, run_external, run_self
from harness.providers import (
    SCRIPTED_INITIAL,
    SCRIPTED_REVISED,
    LiveProvider,
    ScriptedProvider,
)
from harness.scenario import load_scenario


BASE_DIR = Path(__file__).parent


class ScenarioAndEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = load_scenario(BASE_DIR / "scenarios" / "inc_2048.json")

    def test_shared_incident_contract_is_stable(self) -> None:
        self.assertEqual(self.scenario.incident_id, "INC-2048")
        self.assertEqual(self.scenario.incident["service"], "checkout-api")
        self.assertEqual(self.scenario.incident["current_deployment"], "checkout-v42")
        self.assertEqual(
            self.scenario.incident["last_known_good_deployment"], "checkout-v41"
        )
        self.assertEqual(self.scenario.incident["service_health"], "DEGRADED")
        self.assertFalse(self.scenario.incident["rollback_performed"])
        self.assertFalse(self.scenario.incident["recovery_confirmed"])

    def test_deterministic_checks_use_code_not_model_judgment(self) -> None:
        initial = {check.name: check for check in deterministic_checks(
            SCRIPTED_INITIAL, self.scenario
        )}
        revised = {check.name: check for check in deterministic_checks(
            SCRIPTED_REVISED, self.scenario
        )}
        self.assertTrue(initial["INCIDENT_ID"].passed)
        self.assertFalse(initial["LENGTH"].passed)
        self.assertTrue(revised["INCIDENT_ID"].passed)
        self.assertTrue(revised["LENGTH"].passed)

    def test_review_parser_fails_closed_on_missing_fields(self) -> None:
        review = parse_review(
            "INCIDENT_ID: PASS\nVERDICT: PASS\nFEEDBACK: Looks good.",
            SELF_CRITERIA,
            require_verdict=True,
        )
        self.assertFalse(review.verdict)
        self.assertFalse(review.criteria["LENGTH"])
        self.assertIn("missing", review.feedback.lower())

    def test_review_parser_rejects_an_inconsistent_overall_pass(self) -> None:
        review = parse_review(
            "\n".join(
                [
                    "INCIDENT_ID: PASS",
                    "LENGTH: FAIL",
                    "FACTUAL_GROUNDING: PASS",
                    "USEFUL_NEXT_STEP: PASS",
                    "VERDICT: PASS",
                    "FEEDBACK: The response is too short.",
                ]
            ),
            SELF_CRITERIA,
            require_verdict=True,
        )
        self.assertFalse(review.verdict)


class LoopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = load_scenario(BASE_DIR / "scenarios" / "inc_2048.json")

    def test_basic_loop_revises_but_never_claims_quality(self) -> None:
        provider = ScriptedProvider()
        result = run_basic(provider, self.scenario, emit=lambda _: None)
        self.assertEqual(len(result.attempts), 2)
        self.assertIsNone(result.accepted)
        self.assertEqual(
            [action for action, _ in provider.call_log],
            ["generate_initial", "clarify"],
        )

    def test_self_loop_can_stop_on_a_false_positive(self) -> None:
        provider = ScriptedProvider()
        result = run_self(provider, self.scenario, emit=lambda _: None)
        self.assertEqual(len(result.attempts), 1)
        self.assertTrue(result.accepted)
        self.assertIn("resolved", result.final_response)
        self.assertFalse(result.false_positive_observed)

    def test_external_loop_reviews_same_candidate_and_corrects_it(self) -> None:
        provider = ScriptedProvider()
        result = run_external(provider, self.scenario, emit=lambda _: None)
        self.assertEqual(len(result.attempts), 2)
        self.assertTrue(result.accepted)
        self.assertTrue(result.false_positive_observed)
        self.assertFalse(result.attempts[0].independent_passed)
        self.assertTrue(result.attempts[1].independent_passed)
        self.assertEqual(result.final_response, SCRIPTED_REVISED)

        first_self_candidate = next(
            candidate
            for action, candidate in provider.call_log
            if action == "self_review"
        )
        first_external_candidate = next(
            candidate
            for action, candidate in provider.call_log
            if action == "external_review"
        )
        self.assertEqual(first_self_candidate, first_external_candidate)
        self.assertEqual(first_self_candidate, SCRIPTED_INITIAL)


class LiveProviderBoundaryTests(unittest.TestCase):
    def test_self_review_continues_candidate_but_external_review_starts_fresh(self) -> None:
        scenario = load_scenario(BASE_DIR / "scenarios" / "inc_2048.json")

        class FakeResponses:
            def __init__(self) -> None:
                self.calls: list[dict] = []

            def create(self, **kwargs):
                self.calls.append(kwargs)
                number = len(self.calls)
                return SimpleNamespace(
                    id=f"response-{number}",
                    output_text="placeholder",
                    usage=SimpleNamespace(input_tokens=3, output_tokens=2),
                )

        responses = FakeResponses()
        provider = LiveProvider(SimpleNamespace(responses=responses), "demo-model")
        candidate = provider.generate_initial(scenario)
        provider.self_review(candidate, scenario)
        provider.external_review(candidate, scenario)

        self.assertNotIn("previous_response_id", responses.calls[0])
        self.assertEqual(
            responses.calls[1]["previous_response_id"], candidate.response_id
        )
        self.assertNotIn("previous_response_id", responses.calls[2])
        self.assertEqual(
            [call["model"] for call in responses.calls],
            ["demo-model", "demo-model", "demo-model"],
        )


if __name__ == "__main__":
    unittest.main()
