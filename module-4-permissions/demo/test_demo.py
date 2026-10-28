"""Unit tests for the cumulative Module 4 permissions demo."""

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from agent import ALL_TOOLS, build_instructions, handle_tool_call
from catalog import discover_skills
from data import USERS, fresh_incident
from permissions import (
    ROLE_PERMISSIONS,
    SUPPORT_ASSIGNED_PERMISSIONS,
    TOOL_PERMISSIONS,
    check_permission,
)
from scenario import load_scenario
from tools import TOOL_HANDLERS, execute_tool


BASE_DIR = Path(__file__).parent


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

    def test_malformed_identity_values_fail_closed(self) -> None:
        incident = fresh_incident()
        arguments = {"incident_id": "INC-2048"}
        invalid_users = [
            {"user_id": "", "role": "responder"},
            {"user_id": "   ", "role": "responder"},
            {"user_id": None, "role": "responder"},
            {"role": "responder"},
            {"user_id": "OPS-201", "role": ["responder"]},
            {"user_id": "OPS-201", "role": {"name": "responder"}},
            {"user_id": "OPS-201"},
        ]
        for user in invalid_users:
            with self.subTest(user=user):
                decision = check_permission(
                    user, "get_incident", arguments, incident
                )
                self.assertFalse(decision.allowed)
                self.assertEqual(
                    decision.reason, "Authenticated identity is invalid."
                )

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


class ScenarioTests(DemoTestCase):
    def test_every_scenario_references_trusted_users_and_skills(self) -> None:
        for path in (BASE_DIR / "scenarios").glob("*.json"):
            with self.subTest(scenario=path.stem):
                scenario = load_scenario(path)
                self.assertIn(scenario["authenticated_user"], USERS)
                self.assertTrue(scenario["expected_skills"])
                self.assertTrue(
                    all(name in self.catalog for name in scenario["expected_skills"])
                )


if __name__ == "__main__":
    unittest.main()
