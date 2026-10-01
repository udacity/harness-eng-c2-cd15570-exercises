"""Deterministic tests for the Module 3 incident-response hooks demo."""

import unittest
from copy import deepcopy
from pathlib import Path

from agent import build_instructions, run_agent
from catalog import discover_skills
from clients import (
    BLOCKED_RESPONSE,
    PREMATURE_RESPONSE,
    RESOLUTION_BLOCKED_RESPONSE,
    ScriptedClient,
    UNSAFE_RESPONSE,
    VALID_RESPONSE,
)
from evaluator import evaluate_final_note
from hooks import CHECK_NAMES, before_tool_call, mutation_signature
from scenario import load_scenario
from tools import rollback_deployment, update_incident_status


BASE_DIR = Path(__file__).parent
MODEL = "scripted-fixture"


class DemoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = discover_skills(BASE_DIR / "skills")

    def scenario(self, name: str = "unsafe_remediation") -> dict:
        return load_scenario(BASE_DIR / "scenarios" / f"{name}.json")

    def incident(self) -> dict:
        return deepcopy(self.scenario()["incident"])


class HookUnitTests(DemoTestCase):
    def test_valid_last_known_good_rollback_passes_every_check(self) -> None:
        result = before_tool_call(
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v41"},
            self.incident(),
            {"health_checked": True},
            set(),
        )
        self.assertTrue(result.allowed)
        self.assertEqual(set(result.checks), set(CHECK_NAMES))
        self.assertTrue(all(result.checks.values()))
        self.assertEqual(result.violations, [])

    def test_known_but_not_last_known_good_target_is_blocked(self) -> None:
        result = before_tool_call(
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v40"},
            self.incident(),
            {"health_checked": True},
            set(),
        )
        self.assertFalse(result.allowed)
        self.assertTrue(result.checks["rollback_target_exists"])
        self.assertFalse(result.checks["rollback_target_last_known_good"])

    def test_unknown_target_fails_exists_and_last_known_good(self) -> None:
        result = before_tool_call(
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v99"},
            self.incident(),
            {"health_checked": True},
            set(),
        )
        self.assertFalse(result.checks["rollback_target_exists"])
        self.assertFalse(result.checks["rollback_target_last_known_good"])
        self.assertEqual(len(result.violations), 2)

    def test_mutation_without_fresh_health_evidence_is_blocked(self) -> None:
        result = before_tool_call(
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v41"},
            self.incident(),
            {"health_checked": False},
            set(),
        )
        self.assertFalse(result.allowed)
        self.assertFalse(result.checks["fresh_health_evidence"])

    def test_repeated_mutation_is_blocked(self) -> None:
        arguments = {"incident_id": "INC-2048", "target_version": "checkout-v41"}
        signature = mutation_signature("rollback_deployment", arguments)
        result = before_tool_call(
            "rollback_deployment",
            arguments,
            self.incident(),
            {"health_checked": True},
            {signature},
        )
        self.assertFalse(result.allowed)
        self.assertFalse(result.checks["mutation_not_repeated"])

    def test_degraded_incident_cannot_be_resolved(self) -> None:
        result = before_tool_call(
            "update_incident_status",
            {"incident_id": "INC-2048", "status": "RESOLVED"},
            self.incident(),
            {"health_checked": True},
            set(),
        )
        self.assertFalse(result.allowed)
        self.assertFalse(result.checks["resolution_state_valid"])

    def test_hook_fails_closed_for_unknown_or_malformed_calls(self) -> None:
        incident = self.incident()
        cases = [
            ("delete_incident", {"incident_id": "INC-2048"}),
            ("rollback_deployment", "not-an-object"),
            (
                "rollback_deployment",
                {"incident_id": "INC-OTHER", "target_version": "checkout-v41"},
            ),
            ("update_incident_status", {"incident_id": "INC-2048"}),
        ]
        for tool_name, arguments in cases:
            with self.subTest(tool_name=tool_name, arguments=arguments):
                result = before_tool_call(
                    tool_name, arguments, incident, {"health_checked": True}, set()
                )
                self.assertFalse(result.allowed)
                self.assertTrue(result.violations)


class BoundaryTests(DemoTestCase):
    def test_tools_do_not_hide_hook_policy(self) -> None:
        incident = self.incident()
        rollback_deployment(incident, "checkout-v40")
        update_incident_status(incident, "RESOLVED")
        self.assertEqual(incident["current_deployment"], "checkout-v40")
        self.assertEqual(incident["incident_status"], "RESOLVED")
        self.assertEqual(len(incident["actions"]), 2)

    def test_prompt_contains_catalog_metadata_but_not_skill_bodies(self) -> None:
        instructions = build_instructions(self.catalog)
        self.assertIn("incident_triage", instructions)
        self.assertIn("safe_remediation", instructions)
        self.assertNotIn("# Incident triage", instructions)
        self.assertNotIn("Treat a production mutation as a proposed", instructions)


class AgentLoopTests(DemoTestCase):
    def execute_demo(
        self, mode: str, scenario_name: str = "unsafe_remediation"
    ) -> tuple:
        client = ScriptedClient()
        result = run_agent(
            client,
            MODEL,
            self.scenario(scenario_name),
            mode,
            self.catalog,
            emit=lambda _: None,
        )
        return client, result

    def test_basic_mode_executes_both_unsafe_mutations(self) -> None:
        _, result = self.execute_demo("basic")
        self.assertFalse(result["hook_executed"])
        self.assertEqual(result["mutations_requested"], 2)
        self.assertEqual(result["mutations_executed"], 2)
        self.assertEqual(result["final_incident"]["current_deployment"], "checkout-v40")
        self.assertEqual(result["final_incident"]["incident_status"], "RESOLVED")
        self.assertEqual(result["loaded_skills"], ["incident_triage", "safe_remediation"])
        self.assertEqual(len(result["output"].split()), 60)

    def test_hooks_mode_blocks_mutations_and_returns_violations_to_model(self) -> None:
        client, result = self.execute_demo("hooks")
        self.assertTrue(result["hook_executed"])
        self.assertEqual(result["mutations_requested"], 2)
        self.assertEqual(result["mutations_executed"], 0)
        self.assertEqual(result["final_incident"]["current_deployment"], "checkout-v42")
        self.assertEqual(result["final_incident"]["incident_status"], "INVESTIGATING")
        blocked_inputs = [
            call["input"]
            for call in client.responses.calls
            if isinstance(call.get("input"), list)
            and any(
                '"status": "blocked"' in item.get("output", "")
                for item in call["input"]
            )
        ]
        self.assertEqual(len(blocked_inputs), 2)
        self.assertEqual(len(result["output"].split()), 60)

    def test_valid_rollback_is_allowed_by_hook(self) -> None:
        _, result = self.execute_demo("hooks", "valid_rollback")
        self.assertEqual(result["status"], "mutated")
        self.assertEqual(result["mutations_executed"], 1)
        self.assertEqual(result["final_incident"]["current_deployment"], "checkout-v41")
        self.assertEqual(result["final_incident"]["incident_status"], "INVESTIGATING")
        current_versions = [
            item["version"]
            for item in result["final_incident"]["deployment_history"]
            if item["current"]
        ]
        self.assertEqual(current_versions, ["checkout-v41"])

    def test_premature_resolution_is_blocked(self) -> None:
        _, result = self.execute_demo("hooks", "premature_resolution")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["mutations_executed"], 0)
        self.assertEqual(result["final_incident"]["incident_status"], "INVESTIGATING")
        self.assertEqual(result["output"], RESOLUTION_BLOCKED_RESPONSE)

    def test_every_scripted_final_note_has_exactly_sixty_words(self) -> None:
        for candidate in (
            BLOCKED_RESPONSE,
            RESOLUTION_BLOCKED_RESPONSE,
            UNSAFE_RESPONSE,
            VALID_RESPONSE,
            PREMATURE_RESPONSE,
        ):
            with self.subTest(candidate=candidate[:30]):
                self.assertEqual(len(candidate.split()), 60)

    def test_module_one_evaluator_is_fresh_and_excluded_from_serving_metrics(self) -> None:
        client, result = self.execute_demo("hooks")
        serving_total = result["total_tokens"]
        evaluation = evaluate_final_note(
            client,
            MODEL,
            result["final_incident"],
            result["events"],
            result["output"],
        )
        self.assertTrue(evaluation["passed"])
        self.assertEqual(evaluation["word_count"], 60)
        self.assertNotIn("previous_response_id", client.responses.calls[-1])
        self.assertEqual(result["total_tokens"], serving_total)


if __name__ == "__main__":
    unittest.main()
