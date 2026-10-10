"""Deterministic tests for the Hermes CLI incident-response demo."""

import json
import tempfile
import unittest
from pathlib import Path

from components.hooks import CompletionHook, RepeatedCallHook, SafetyHook
from components.permissions import decide
from data import SCENARIOS, fresh_incident, scenario, trusted_user
from plugin_impl import IncidentResponsePlugin, SKILL_NAMES
from run_demo import build_command


BASE_DIR = Path(__file__).resolve().parent


class FakeContext:
    def __init__(self) -> None:
        self.tools = {}
        self.skills = {}
        self.hooks = {}

    def register_tool(self, **kwargs) -> None:
        self.tools[kwargs["name"]] = kwargs

    def register_skill(self, name, path, **kwargs) -> None:
        self.skills[name] = {"path": Path(path), **kwargs}

    def register_hook(self, event, handler) -> None:
        self.hooks.setdefault(event, []).append(handler)


class DemoTestCase(unittest.TestCase):
    def make_plugin(self, scenario_name: str):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        state_path = root / "incident.json"
        trace_path = root / "run.jsonl"
        state_path.write_text(
            json.dumps(fresh_incident(), indent=2) + "\n", encoding="utf-8"
        )
        trace_path.write_text("", encoding="utf-8")
        plugin = IncidentResponsePlugin(
            demo_dir=BASE_DIR,
            scenario_name=scenario_name,
            state_path=state_path,
            trace_path=trace_path,
        )
        context = FakeContext()
        plugin.register(context)
        self.addCleanup(temporary.cleanup)
        return plugin, context, state_path, trace_path

    @staticmethod
    def call(plugin, context, name: str, arguments: dict):
        block = plugin.before_tool(name, arguments)
        if block is not None:
            return json.loads(block["message"])
        result = context.tools[name]["handler"](arguments)
        plugin.after_tool(name, arguments, result)
        return json.loads(result)


class RegistrationTests(DemoTestCase):
    def test_plugin_registers_six_tools_two_skills_and_four_hooks(self) -> None:
        _, context, _, _ = self.make_plugin("safe-rollback")
        self.assertEqual(
            set(context.tools),
            {
                "get_incident",
                "get_service_health",
                "get_deployment_history",
                "query_service_logs",
                "rollback_deployment",
                "update_incident_status",
            },
        )
        self.assertEqual(set(context.skills), set(SKILL_NAMES))
        self.assertEqual(
            set(context.hooks),
            {"pre_llm_call", "pre_tool_call", "post_tool_call", "pre_verify"},
        )
        self.assertTrue(
            all(value["path"].is_file() for value in context.skills.values())
        )

    def test_plugin_manifest_and_profile_enable_the_toolset(self) -> None:
        manifest = (
            BASE_DIR
            / ".hermes"
            / "plugins"
            / "incident-response-demo"
            / "plugin.yaml"
        ).read_text(encoding="utf-8")
        config = (BASE_DIR / ".hermes" / "config.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("name: incident-response-demo", manifest)
        self.assertIn("- incident-response-demo", config)
        self.assertIn("platform_toolsets:", config)

    def test_first_model_hook_records_cli_preloaded_skills_once(self) -> None:
        plugin, _, _, _ = self.make_plugin("safe-rollback")
        plugin.before_model()
        plugin.before_model()
        events = [
            event for event in plugin.trace.events if event["event"] == "skills_preloaded"
        ]
        self.assertEqual(len(events), 1)
        self.assertEqual(len(events[0]["skills"]), 2)


class BoundaryTests(DemoTestCase):
    def test_safe_authorized_rollback_executes_and_verifies(self) -> None:
        plugin, context, state_path, _ = self.make_plugin("safe-rollback")
        self.assertEqual(
            self.call(
                plugin,
                context,
                "get_service_health",
                {"incident_id": "INC-2048"},
            )["status"],
            "found",
        )
        self.call(
            plugin,
            context,
            "get_deployment_history",
            {"incident_id": "INC-2048"},
        )
        result = self.call(
            plugin,
            context,
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v41"},
        )
        self.assertEqual(result["status"], "rolled_back")
        self.assertEqual(
            json.loads(state_path.read_text(encoding="utf-8"))["current_deployment"],
            "checkout-v41",
        )
        self.assertIsNone(plugin.before_completion())

    def test_support_engineer_rollback_is_denied_before_execution(self) -> None:
        plugin, context, state_path, _ = self.make_plugin("unauthorized-rollback")
        self.call(
            plugin,
            context,
            "get_service_health",
            {"incident_id": "INC-2048"},
        )
        result = self.call(
            plugin,
            context,
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v41"},
        )
        self.assertEqual(result["status"], "permission_denied")
        self.assertFalse(result["executed"])
        self.assertEqual(
            json.loads(state_path.read_text(encoding="utf-8"))["current_deployment"],
            "checkout-v42",
        )
        self.assertIsNone(plugin.before_completion())

    def test_non_last_known_good_rollback_is_blocked_by_hook(self) -> None:
        plugin, context, state_path, _ = self.make_plugin("unsafe-rollback")
        self.call(
            plugin,
            context,
            "get_service_health",
            {"incident_id": "INC-2048"},
        )
        result = self.call(
            plugin,
            context,
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v40"},
        )
        self.assertEqual(result["status"], "hook_blocked")
        self.assertIn("rollback_target_not_last_known_good", result["codes"])
        self.assertEqual(
            json.loads(state_path.read_text(encoding="utf-8"))["current_deployment"],
            "checkout-v42",
        )
        self.assertIsNone(plugin.before_completion())

    def test_completion_hook_nudges_until_expected_boundary_is_observed(self) -> None:
        plugin, _, _, _ = self.make_plugin("safe-rollback")
        result = plugin.before_completion()
        self.assertEqual(result["action"], "continue")
        self.assertTrue(
            any(
                event.get("hook") == "completion_verification"
                and event.get("allowed") is False
                for event in plugin.trace.events
            )
        )

    def test_trace_records_permission_hook_tool_and_completion_evidence(self) -> None:
        plugin, context, _, trace_path = self.make_plugin("safe-rollback")
        self.call(
            plugin,
            context,
            "get_service_health",
            {"incident_id": "INC-2048"},
        )
        self.call(
            plugin,
            context,
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v41"},
        )
        plugin.before_completion()
        events = [
            json.loads(line)
            for line in trace_path.read_text(encoding="utf-8").splitlines()
        ]
        event_names = {event["event"] for event in events}
        self.assertTrue(
            {"permission_decision", "hook_decision", "tool_result", "completion"}
            <= event_names
        )
        self.assertTrue(all(event["harness"] == "hermes" for event in events))


class ComponentTests(unittest.TestCase):
    def test_permissions_use_trusted_role_and_assignment(self) -> None:
        incident = fresh_incident()
        selected = scenario("unauthorized-rollback")
        support = trusted_user(selected)
        read = decide(
            support, "get_incident", {"incident_id": "INC-2048"}, incident
        )
        rollback = decide(
            support,
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v41"},
            incident,
        )
        self.assertTrue(read.allowed)
        self.assertFalse(rollback.allowed)

    def test_safety_hook_requires_fresh_health_and_last_known_good(self) -> None:
        hook = SafetyHook()
        arguments = {"incident_id": "INC-2048", "target_version": "checkout-v40"}
        decision = hook.check(
            "rollback_deployment", arguments, fresh_incident(), {"health_checked": False}
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(
            set(decision.codes),
            {"missing_fresh_health", "rollback_target_not_last_known_good"},
        )

    def test_sixth_equivalent_call_is_blocked(self) -> None:
        hook = RepeatedCallHook()
        decisions = [
            hook.check("get_incident", {"incident_id": "INC-2048"})
            for _ in range(6)
        ]
        self.assertTrue(all(item.allowed for item in decisions[:5]))
        self.assertFalse(decisions[5].allowed)

    def test_completion_oracles_cover_all_three_scenarios(self) -> None:
        hook = CompletionHook()
        for name in SCENARIOS:
            decision = hook.check(scenario(name), fresh_incident(), [])
            self.assertFalse(decision.allowed, name)


class CliTests(unittest.TestCase):
    def test_command_uses_hermes_oneshot_toolset_skills_and_usage_file(self) -> None:
        command = build_command(
            Path("/opt/hermes"),
            prompt="task",
            model={"model": "demo-model", "provider": "demo-provider"},
            usage_file=Path("usage.json"),
        )
        self.assertEqual(command[0:3], ["/opt/hermes", "-z", "task"])
        self.assertIn("--usage-file", command)
        self.assertIn("--in", command)
        self.assertEqual(
            command[command.index("--toolsets") + 1], "incident-response-demo"
        )
        skills = command[command.index("--skills") + 1]
        self.assertIn("incident-response-demo:incident_triage", skills)
        self.assertIn("incident-response-demo:safe_remediation", skills)


if __name__ == "__main__":
    unittest.main()

