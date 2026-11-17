"""Offline tests for the Module 3 mutation hook and its run summary."""

import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from agent import run_agent
from catalog import discover_skills
from hooks import before_tool_call
from main import _block_reasons
from scenario import load_scenario


BASE_DIR = Path(__file__).resolve().parent


def call(name: str, arguments: dict, number: int) -> SimpleNamespace:
    return SimpleNamespace(
        type="function_call",
        name=name,
        arguments=json.dumps(arguments),
        call_id=f"call-{number}",
    )


class ScriptedResponses:
    """Return one fixed tool call per cycle, then a final note."""

    def __init__(self, calls: list[SimpleNamespace]) -> None:
        self.calls = calls
        self.count = 0

    def create(self, **_kwargs) -> SimpleNamespace:
        self.count += 1
        usage = SimpleNamespace(input_tokens=1, output_tokens=1)
        if self.calls:
            return SimpleNamespace(
                id=f"resp-{self.count}",
                output=[self.calls.pop(0)],
                output_text="",
                usage=usage,
            )
        return SimpleNamespace(
            id=f"resp-{self.count}", output=[], output_text="Final note.", usage=usage
        )


class HookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = load_scenario(BASE_DIR / "scenarios" / "valid_rollback.json")
        cls.incident = cls.scenario["incident"]

    def test_checks_that_do_not_apply_are_not_reported_as_pass(self) -> None:
        decision = before_tool_call(
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v41"},
            self.incident,
            {"health_checked": True},
            set(),
        )
        self.assertTrue(decision.allowed)
        self.assertIsNone(decision.checks["resolution_state_valid"])
        self.assertTrue(decision.checks["rollback_target_last_known_good"])

    def test_executed_rollback_is_not_hidden_by_an_earlier_block(self) -> None:
        rollback = {"incident_id": "INC-2048", "target_version": "checkout-v41"}
        client = SimpleNamespace(
            responses=ScriptedResponses(
                [
                    call("rollback_deployment", rollback, 1),
                    call("get_service_health", {"incident_id": "INC-2048"}, 2),
                    call("rollback_deployment", rollback, 3),
                ]
            )
        )
        run = run_agent(
            client,
            "scripted-fixture",
            self.scenario,
            "hooks",
            discover_skills(BASE_DIR / "skills"),
            emit=lambda _: None,
        )
        self.assertEqual(run["final_incident"]["current_deployment"], "checkout-v41")
        self.assertEqual(run["status"], "mutated_and_blocked")
        self.assertEqual(_block_reasons(run), "no fresh health check")


if __name__ == "__main__":
    unittest.main()
