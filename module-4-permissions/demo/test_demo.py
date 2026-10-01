"""Deterministic tests for the cumulative Module 4 permissions demo."""

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from agent import ALL_TOOLS, build_instructions, handle_tool_call, run_agent
from catalog import discover_skills
from clients import FINAL_RESPONSES, ScriptedClient
from data import USERS, fresh_incident
from evaluator import evaluate_final_note
from permissions import (
    ROLE_PERMISSIONS,
    SUPPORT_ASSIGNED_PERMISSIONS,
    TOOL_PERMISSIONS,
    check_permission,
)
from scenario import load_scenario
from tools import TOOL_HANDLERS, execute_tool


BASE_DIR = Path(__file__).parent
MODEL = "scripted-fixture"


def tool_call(
    name: str, arguments: dict, call_id: str = "call-1"
) -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        arguments=json.dumps(arguments),
        call_id=call_id,
    )


class DemoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = discover_skills(BASE_DIR / "skills")

    def scenario(self, name: str = "unauthorized_rollback") -> dict:
        return load_scenario(BASE_DIR / "scenarios" / f"{name}.json")

    def execute_demo(self, mode: str, name: str = "unauthorized_rollback") -> tuple:
        scenario = self.scenario(name)
        client = ScriptedClient(scenario)
        result = run_agent(
            client,
            MODEL,
            mode,
            USERS[scenario["authenticated_user"]],
            scenario,
            fresh_incident(),
            self.catalog,
            emit=lambda _: None,
        )
        return client, result


class PermissionMatrixTests(DemoTestCase):
    def assert_decision(
        self,
        user_key: str,
        tool: str,
        allowed: bool,
        incident: dict | None = None,
    ) -> None:
        arguments = {"incident_id": "INC-2048"}
        if tool == "rollback_deployment":
            arguments["target_version"] = "checkout-v41"
        elif tool == "update_incident_status":
            arguments["status"] = "MONITORING"
        elif tool == "reassign_incident":
            arguments["new_assignee_user_id"] = "OPS-102"
        decision = check_permission(
            USERS[user_key], tool, arguments, incident or fresh_incident()
        )
        self.assertEqual(decision.allowed, allowed, decision)

    def test_permission_definitions_cover_every_business_tool(self) -> None:
        self.assertEqual(set(TOOL_PERMISSIONS), set(TOOL_HANDLERS))
        exposed_business_tools = {
            tool["name"] for tool in ALL_TOOLS if tool["name"] != "load_skill"
        }
        self.assertEqual(exposed_business_tools, set(TOOL_PERMISSIONS))
        self.assertEqual(
            ROLE_PERMISSIONS["administrator"]
            - ROLE_PERMISSIONS["incident_commander"],
            {"incident.reassign"},
        )

    def test_support_engineer_can_read_assigned_incident_only(self) -> None:
        for tool in SUPPORT_ASSIGNED_PERMISSIONS:
            self.assert_decision("support_sam", tool, True)
            self.assert_decision("support_riley", tool, False)
        self.assert_decision("support_sam", "rollback_deployment", False)
        self.assert_decision("support_sam", "update_incident_status", False)

    def test_responder_commander_and_administrator_permissions(self) -> None:
        for tool in (
            "get_incident",
            "get_service_health",
            "get_deployment_history",
            "query_service_logs",
            "rollback_deployment",
        ):
            self.assert_decision("responder_jordan", tool, True)
        self.assert_decision("responder_jordan", "update_incident_status", False)
        self.assert_decision("commander_morgan", "update_incident_status", True)
        self.assert_decision("commander_morgan", "reassign_incident", False)
        for tool in TOOL_PERMISSIONS:
            self.assert_decision("admin_taylor", tool, True)

    def test_unknown_tools_resources_and_identities_fail_closed(self) -> None:
        incident = fresh_incident()
        cases = [
            check_permission(USERS["admin_taylor"], "unknown", {}, incident),
            check_permission(
                USERS["admin_taylor"],
                "get_incident",
                {"incident_id": "INC-NOPE"},
                incident,
            ),
            check_permission(
                {"user_id": "OPS-X", "role": "invented"},
                "get_incident",
                {"incident_id": "INC-2048"},
                incident,
            ),
            check_permission(
                USERS["admin_taylor"], "get_incident", {}, incident
            ),
        ]
        self.assertTrue(all(not decision.allowed for decision in cases))

    def test_request_text_cannot_change_authenticated_identity(self) -> None:
        scenario = self.scenario("impersonation_attempt")
        self.assertIn("administrator", scenario["request"])
        decision = check_permission(
            USERS[scenario["authenticated_user"]],
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v41"},
            fresh_incident(),
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.required_permission, "deployment.rollback")


class EnforcementBoundaryTests(DemoTestCase):
    def test_underlying_tools_do_not_hide_authorization_or_hook_policy(self) -> None:
        incident = fresh_incident()
        execute_tool(
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v40"},
            incident,
        )
        execute_tool(
            "update_incident_status",
            {"incident_id": "INC-2048", "status": "RESOLVED"},
            incident,
        )
        self.assertEqual(incident["current_deployment"], "checkout-v40")
        self.assertEqual(incident["incident_status"], "RESOLVED")

    def test_permission_denial_prevents_hook_and_tool_execution(self) -> None:
        incident = fresh_incident()
        event, output = handle_tool_call(
            tool_call(
                "rollback_deployment",
                {"incident_id": "INC-2048", "target_version": "checkout-v41"},
            ),
            "permissions",
            USERS["support_sam"],
            incident,
            {"health_checked": True},
            set(),
            self.catalog,
            emit=lambda _: None,
        )
        self.assertEqual(event["permission_check"], "DENIED")
        self.assertFalse(event["hook_executed"])
        self.assertFalse(event["tool_executed"])
        self.assertEqual(incident["current_deployment"], "checkout-v42")
        self.assertEqual(json.loads(output["output"])["status"], "permission_denied")

    def test_authorized_action_can_still_be_blocked_by_safety_hook(self) -> None:
        incident = fresh_incident()
        event, output = handle_tool_call(
            tool_call(
                "update_incident_status",
                {"incident_id": "INC-2048", "status": "RESOLVED"},
            ),
            "permissions",
            USERS["commander_morgan"],
            incident,
            {"health_checked": True},
            set(),
            self.catalog,
            emit=lambda _: None,
        )
        self.assertEqual(event["permission_check"], "ALLOWED")
        self.assertTrue(event["hook_executed"])
        self.assertFalse(event["tool_executed"])
        self.assertEqual(incident["incident_status"], "INVESTIGATING")
        self.assertEqual(json.loads(output["output"])["status"], "blocked")

    def test_basic_skips_permission_but_retains_safety_hook(self) -> None:
        incident = fresh_incident()
        event, _ = handle_tool_call(
            tool_call(
                "rollback_deployment",
                {"incident_id": "INC-2048", "target_version": "checkout-v41"},
            ),
            "basic",
            USERS["support_sam"],
            incident,
            {"health_checked": True},
            set(),
            self.catalog,
            emit=lambda _: None,
        )
        self.assertEqual(event["permission_check"], "NOT PERFORMED")
        self.assertTrue(event["hook_executed"])
        self.assertTrue(event["tool_executed"])
        self.assertEqual(incident["current_deployment"], "checkout-v41")

    def test_catalog_prompt_contains_metadata_not_skill_bodies(self) -> None:
        instructions = build_instructions(self.catalog)
        self.assertIn("safe_remediation", instructions)
        self.assertNotIn("# Safe remediation", instructions)
        self.assertNotIn("Treat a production mutation as a proposed", instructions)


class AgentLoopTests(DemoTestCase):
    def test_default_scenario_is_unsafe_without_permissions_and_denied_with_them(self) -> None:
        _, basic = self.execute_demo("basic")
        _, protected = self.execute_demo("permissions")
        self.assertEqual(basic["final_incident"]["current_deployment"], "checkout-v41")
        self.assertEqual(
            protected["final_incident"]["current_deployment"], "checkout-v42"
        )
        self.assertTrue(
            any(
                event["permission_check"] == "DENIED"
                for event in protected["events"]
            )
        )
        self.assertEqual(
            basic["loaded_skills"], ["incident_triage", "safe_remediation"]
        )

    def test_assignment_and_impersonation_scenarios(self) -> None:
        _, assigned = self.execute_demo("permissions", "assigned_read")
        _, unassigned = self.execute_demo("permissions", "unassigned_read")
        _, impersonation = self.execute_demo("permissions", "impersonation_attempt")
        self.assertEqual(assigned["events"][-1]["permission_check"], "ALLOWED")
        self.assertEqual(unassigned["events"][-1]["permission_check"], "DENIED")
        self.assertEqual(impersonation["events"][-1]["permission_check"], "DENIED")
        self.assertEqual(
            impersonation["authenticated_user"]["role"], "support_engineer"
        )

    def test_each_action_is_authorized_independently(self) -> None:
        _, result = self.execute_demo("permissions", "responder_rollback_resolve")
        rollback = next(
            event for event in result["events"] if event["tool"] == "rollback_deployment"
        )
        resolve = next(
            event
            for event in result["events"]
            if event["tool"] == "update_incident_status"
        )
        self.assertEqual(rollback["permission_check"], "ALLOWED")
        self.assertTrue(rollback["tool_executed"])
        self.assertEqual(resolve["permission_check"], "DENIED")
        self.assertFalse(resolve["hook_executed"])
        self.assertEqual(result["final_incident"]["incident_status"], "INVESTIGATING")

    def test_modes_expose_identical_prompt_tools_identity_and_request(self) -> None:
        clients = {}
        for mode in ("basic", "permissions"):
            client, _ = self.execute_demo(mode)
            clients[mode] = client
        basic_call = clients["basic"].responses.calls[0]
        protected_call = clients["permissions"].responses.calls[0]
        self.assertEqual(basic_call["tools"], protected_call["tools"])
        self.assertEqual(basic_call["instructions"], protected_call["instructions"])
        self.assertEqual(basic_call["input"], protected_call["input"])

    def test_every_scripted_note_has_sixty_words(self) -> None:
        for candidate in FINAL_RESPONSES:
            with self.subTest(candidate=candidate[:35]):
                self.assertEqual(len(candidate.split()), 60)

    def test_evaluator_is_fresh_and_excluded_from_serving_metrics(self) -> None:
        client, result = self.execute_demo("permissions")
        serving_total = result["total_tokens"]
        evaluation = evaluate_final_note(
            client,
            MODEL,
            result["final_incident"],
            result["events"],
            result["output"],
        )
        self.assertTrue(evaluation["passed"])
        self.assertNotIn("previous_response_id", client.responses.calls[-1])
        self.assertEqual(result["total_tokens"], serving_total)

    def test_every_scenario_references_trusted_data_and_known_tools(self) -> None:
        for path in (BASE_DIR / "scenarios").glob("*.json"):
            with self.subTest(scenario=path.stem):
                scenario = load_scenario(path)
                self.assertIn(scenario["authenticated_user"], USERS)
                for action in scenario["scripted_actions"]:
                    self.assertIn(action["tool"], TOOL_HANDLERS)


if __name__ == "__main__":
    unittest.main()
