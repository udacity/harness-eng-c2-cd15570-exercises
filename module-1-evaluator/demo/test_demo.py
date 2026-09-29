"""Deterministic tests for the Module 1 incident-response demo."""

import unittest
from pathlib import Path

from harness.clients import SCRIPTED_INITIAL, SCRIPTED_REVISED, ScriptedClient
from harness.loops.basic_loop import run_basic_loop
from harness.loops.external_evaluation_loop import (
    deterministic_criterion_passed,
    evaluate_deterministic_criteria,
    extract_incident_id,
    inferential_criterion_passed,
    run_external_evaluation_loop,
)
from harness.loops.self_evaluation_loop import (
    criterion_passed,
    passed,
    run_self_evaluation_loop,
)
from harness.scenario import load_scenario


BASE_DIR = Path(__file__).parent
MODEL = "scripted-fixture"


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
        self.assertEqual(
            self.scenario.response_requirements["required_word_count"], 60
        )
        self.assertFalse(self.scenario.incident["rollback_performed"])
        self.assertFalse(self.scenario.incident["recovery_confirmed"])

    def test_exact_incident_id_and_word_count_are_checked_in_python(self) -> None:
        initial_passed, initial_results = evaluate_deterministic_criteria(
            SCRIPTED_INITIAL, self.scenario
        )
        revised_passed, revised_results = evaluate_deterministic_criteria(
            SCRIPTED_REVISED, self.scenario
        )
        self.assertFalse(initial_passed)
        self.assertTrue(
            deterministic_criterion_passed(initial_results, "INCIDENT_ID")
        )
        self.assertFalse(
            deterministic_criterion_passed(initial_results, "WORD_COUNT")
        )
        self.assertTrue(revised_passed)
        self.assertTrue(
            deterministic_criterion_passed(revised_results, "WORD_COUNT")
        )

    def test_named_result_parsers_fail_closed(self) -> None:
        self.assertEqual(extract_incident_id(self.scenario.request), "INC-2048")
        self.assertTrue(passed("VERDICT: PASS"))
        self.assertFalse(passed("FEEDBACK: Everything should PASS"))
        self.assertTrue(criterion_passed("WORD_COUNT: PASS", "WORD_COUNT"))
        self.assertFalse(
            inferential_criterion_passed(
                "FEEDBACK: FACTUAL_GROUNDING should PASS", "FACTUAL_GROUNDING"
            )
        )


class LoopAndConversationBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = load_scenario(BASE_DIR / "scenarios" / "inc_2048.json")

    def test_basic_loop_revises_but_never_claims_quality(self) -> None:
        client = ScriptedClient()
        result = run_basic_loop(
            client, MODEL, self.scenario, emit=lambda _: None
        )
        calls = client.responses.calls
        self.assertEqual(len(result.attempts), 2)
        self.assertIsNone(result.accepted)
        self.assertNotIn("previous_response_id", calls[0])
        self.assertEqual(calls[1]["previous_response_id"], "scripted-1")

    def test_self_loop_stops_when_its_own_review_passes(self) -> None:
        client = ScriptedClient()
        result = run_self_evaluation_loop(
            client, MODEL, self.scenario, emit=lambda _: None
        )
        calls = client.responses.calls
        self.assertEqual(len(result.attempts), 1)
        self.assertTrue(result.accepted)
        self.assertIn("resolved", result.final_response)
        self.assertNotIn("previous_response_id", calls[0])
        self.assertEqual(calls[1]["previous_response_id"], "scripted-1")

    def test_self_revision_continues_from_the_review_response(self) -> None:
        client = ScriptedClient(self_verdicts=[False, True])
        result = run_self_evaluation_loop(
            client, MODEL, self.scenario, emit=lambda _: None
        )
        calls = client.responses.calls
        self.assertEqual(len(result.attempts), 2)
        self.assertTrue(result.accepted)
        self.assertEqual(calls[1]["previous_response_id"], "scripted-1")
        self.assertEqual(calls[2]["previous_response_id"], "scripted-2")
        self.assertEqual(calls[3]["previous_response_id"], "scripted-3")

    def test_external_loop_uses_fresh_review_and_candidate_revision_branches(self) -> None:
        client = ScriptedClient()
        result = run_external_evaluation_loop(
            client, MODEL, self.scenario, emit=lambda _: None
        )
        calls = client.responses.calls
        self.assertEqual(len(result.attempts), 2)
        self.assertTrue(result.accepted)
        self.assertTrue(result.false_positive_observed)
        self.assertFalse(result.attempts[0].independent_passed)
        self.assertTrue(result.attempts[1].independent_passed)
        self.assertEqual(result.final_response, SCRIPTED_REVISED)

        self.assertNotIn("previous_response_id", calls[0])
        self.assertEqual(calls[1]["previous_response_id"], "scripted-1")
        self.assertNotIn("previous_response_id", calls[2])
        self.assertIn(SCRIPTED_INITIAL, calls[2]["input"])
        self.assertEqual(calls[3]["previous_response_id"], "scripted-1")
        self.assertEqual(calls[4]["previous_response_id"], "scripted-4")
        self.assertNotIn("previous_response_id", calls[5])
        self.assertIn(SCRIPTED_REVISED, calls[5]["input"])


if __name__ == "__main__":
    unittest.main()
