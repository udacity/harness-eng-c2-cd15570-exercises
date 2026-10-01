"""Deterministic tests for the Module 2 incident-response skills demo."""

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from agent import (
    SKILL_TOOL,
    build_selection_instructions,
    resolve_skill_call,
    run_basic,
    run_with_skills,
)
from catalog import catalog_prompt, discover_skills
from clients import ScriptedClient
from evaluator import evaluate_final_note
from scenario import build_brief, load_incident, load_request


BASE_DIR = Path(__file__).parent
MODEL = "scripted-fixture"


class DemoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.incident = load_incident(BASE_DIR / "data" / "incident.json")
        cls.catalog = discover_skills(BASE_DIR / "skills")

    def request(self, name: str):
        return load_request(BASE_DIR / "requests" / f"{name}.json")


class ScenarioAndCatalogTests(DemoTestCase):
    def test_shared_incident_contract_is_stable(self) -> None:
        self.assertEqual(self.incident["incident_id"], "INC-2048")
        self.assertEqual(self.incident["service"], "checkout-api")
        self.assertEqual(self.incident["current_deployment"], "checkout-v42")
        self.assertEqual(
            self.incident["last_known_good_deployment"], "checkout-v41"
        )
        self.assertEqual(self.incident["service_health"], "DEGRADED")
        self.assertFalse(self.incident["rollback_performed"])
        self.assertFalse(self.incident["recovery_confirmed"])

    def test_catalog_exposes_only_names_and_descriptions(self) -> None:
        self.assertEqual(
            set(self.catalog),
            {
                "incident_triage",
                "checkout_service_runbook",
                "safe_remediation",
                "incident_communications",
            },
        )
        prompt = catalog_prompt(self.catalog)
        self.assertIn("incident_triage", prompt)
        self.assertIn("checkout_service_runbook", prompt)
        self.assertNotIn("# Incident triage", prompt)
        self.assertNotIn("Start from observed incident state", prompt)

    def test_load_skill_tool_schema_is_strict(self) -> None:
        parameters = SKILL_TOOL["parameters"]
        self.assertEqual(SKILL_TOOL["name"], "load_skill")
        self.assertEqual(parameters["required"], ["skill_name"])
        self.assertFalse(parameters["additionalProperties"])
        self.assertEqual(
            parameters["properties"]["skill_name"]["type"], "string"
        )

    def test_selection_instructions_do_not_contain_skill_bodies(self) -> None:
        catalog_text, instructions = build_selection_instructions(self.catalog)
        self.assertIn(catalog_text, instructions)
        self.assertIn("load_skill", instructions)
        self.assertNotIn("# Safe remediation", instructions)
        self.assertNotIn("Treat a production mutation", instructions)


class SkillResolutionTests(DemoTestCase):
    def test_valid_skill_call_returns_full_text_and_provenance(self) -> None:
        item = SimpleNamespace(
            name="load_skill",
            arguments=json.dumps({"skill_name": "incident_triage"}),
            call_id="call-1",
        )
        record, output = resolve_skill_call(item, self.catalog)
        self.assertTrue(record["loaded"])
        self.assertEqual(record["skill"], "incident_triage")
        self.assertTrue(record["path"].endswith("incident_triage/SKILL.md"))
        self.assertIn("# Incident triage", output["output"])
        self.assertEqual(output["call_id"], "call-1")

    def test_unknown_or_malformed_skill_calls_fail_without_path_loading(self) -> None:
        unknown = SimpleNamespace(
            name="load_skill",
            arguments=json.dumps({"skill_name": "../secret"}),
            call_id="call-2",
        )
        malformed = SimpleNamespace(
            name="load_skill",
            arguments="not-json",
            call_id="call-3",
        )
        for item in (unknown, malformed):
            record, output = resolve_skill_call(item, self.catalog)
            self.assertFalse(record["loaded"])
            self.assertIsNone(record["path"])
            self.assertEqual(record["chars"], 0)
            self.assertTrue(output["output"].startswith("ERROR:"))


class AgentLoopTests(DemoTestCase):
    def test_basic_sends_every_complete_skill_in_one_cycle(self) -> None:
        request = self.request("checkout_diagnosis")
        brief = build_brief(self.incident, request)
        client = ScriptedClient()
        result = run_basic(
            client, MODEL, brief, self.catalog, emit=lambda _: None
        )
        self.assertEqual(result["cycles"], 1)
        self.assertEqual(len(client.responses.calls), 1)
        self.assertIn("# Incident triage", client.responses.calls[0]["instructions"])
        self.assertIn(
            "# Incident communications", client.responses.calls[0]["instructions"]
        )
        self.assertEqual(len(result["output"].split()), 60)

    def test_on_demand_path_loads_relevant_skills_then_removes_tool(self) -> None:
        request = self.request("checkout_diagnosis")
        brief = build_brief(self.incident, request)
        client = ScriptedClient()
        result = run_with_skills(
            client, MODEL, brief, self.catalog, emit=lambda _: None
        )
        calls = client.responses.calls
        self.assertEqual(result["cycles"], 2)
        self.assertEqual(result["loaded_skills"], list(request.expected_skills))
        self.assertIn("tools", calls[0])
        self.assertEqual(calls[1]["previous_response_id"], "scripted-1")
        self.assertNotIn("tools", calls[1])
        self.assertEqual(len(result["output"].split()), 60)

        eager_client = ScriptedClient()
        eager = run_basic(
            eager_client, MODEL, brief, self.catalog, emit=lambda _: None
        )
        self.assertLess(result["full_skill_chars"], eager["full_skill_chars"])

    def test_no_skill_selection_still_reaches_the_writing_cycle(self) -> None:
        request = self.request("stakeholder_update")
        client = ScriptedClient(forced_skills=[])
        result = run_with_skills(
            client,
            MODEL,
            build_brief(self.incident, request),
            self.catalog,
            emit=lambda _: None,
        )
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["loaded_skills"], [])
        self.assertEqual(len(client.responses.calls), 2)

    def test_supplied_evaluator_is_fresh_and_separate_from_serving_metrics(self) -> None:
        request = self.request("checkout_diagnosis")
        client = ScriptedClient()
        run = run_with_skills(
            client,
            MODEL,
            build_brief(self.incident, request),
            self.catalog,
            emit=lambda _: None,
        )
        serving_total = run["total_tokens"]
        evaluation = evaluate_final_note(
            client, MODEL, self.incident, request, run["output"]
        )
        self.assertTrue(evaluation["passed"])
        self.assertEqual(evaluation["word_count"], 60)
        self.assertEqual(len(client.responses.calls), 3)
        self.assertNotIn("previous_response_id", client.responses.calls[2])
        self.assertEqual(run["total_tokens"], serving_total)


if __name__ == "__main__":
    unittest.main()
