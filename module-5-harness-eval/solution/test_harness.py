"""Deterministic, no-network tests for the complete harness-evaluation solution."""

from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

from agent import _business_call, run_agent
from catalog import discover_skills, load_skill
from config import CONFIGS
from data import USERS, fresh_store
from evaluator import EvaluationParseError, parse_evaluation_json
from experiment import PauseController, failed_trial_result, run_trial
from hooks import run_before_tool_hooks
from metrics import (
    aggregate_results,
    build_failures,
    qualifying_configs,
    render_report,
    score_deterministic,
    write_artifacts,
)
from permissions import check_permission
from tasks import load_scenario
from tools import execute_tool


BASE_DIR = Path(__file__).resolve().parent


def model_response(
    response_id: str,
    *,
    text: str = "",
    calls: list[SimpleNamespace] | None = None,
    input_tokens: int = 10,
    output_tokens: int = 5,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=response_id,
        output=calls or [],
        output_text=text,
        usage=SimpleNamespace(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        ),
    )


def function_call(name: str, arguments: dict, call_id: str) -> SimpleNamespace:
    return SimpleNamespace(
        type="function_call",
        name=name,
        arguments=json.dumps(arguments),
        call_id=call_id,
    )


def score_text(value: int = 5, notes: str = "Meets the rubric.") -> str:
    return json.dumps(
        {
            "correctness": value,
            "clarity": value,
            "next_step": value,
            "claim_support": value,
            "tool_consistency": value,
            "notes": notes,
        }
    )


class ScriptedClient:
    def __init__(self, responses: list[SimpleNamespace]) -> None:
        self.queue = list(responses)
        self.calls: list[dict] = []
        self.responses = SimpleNamespace(create=self.create)

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if not self.queue:
            raise AssertionError("Fake response queue is empty.")
        response = self.queue.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class ConfigAndStateTests(unittest.TestCase):
    def test_exact_controlled_ablation_matrix(self) -> None:
        self.assertEqual(
            {
                name: (value.skills, value.evaluator, value.hooks, value.permissions)
                for name, value in CONFIGS.items()
            },
            {
                "full": (True, True, True, True),
                "no-skills": (False, True, True, True),
                "no-evaluator": (True, False, True, True),
                "no-hooks": (True, True, False, True),
                "no-permissions": (True, True, True, False),
                "bare": (False, False, False, False),
            },
        )
        self.assertEqual(CONFIGS["full"].component_count, 4)
        self.assertEqual(CONFIGS["bare"].component_count, 0)

    def test_store_is_fresh_for_every_trial(self) -> None:
        first = fresh_store()
        second = fresh_store()
        first["orders"]["ORD-1001"]["refund_issued"] = True
        first["returns"]["RET-1003"]["status"] = "CLOSED"
        self.assertFalse(second["orders"]["ORD-1001"]["refund_issued"])
        self.assertEqual(second["returns"]["RET-1003"]["status"], "RECEIVED")

    def test_scenarios_match_trusted_data(self) -> None:
        store = fresh_store()
        for path in (BASE_DIR / "scenarios").glob("*.json"):
            scenario = load_scenario(path.stem)
            self.assertIn(scenario["authenticated_user"], USERS)
            self.assertIn(scenario["customer_id"], store["customers"])
            for order_id in scenario["order_ids"]:
                self.assertEqual(
                    store["orders"][order_id]["customer_id"],
                    scenario["customer_id"],
                )

    def test_skill_catalog_loads_only_exact_allowlisted_names(self) -> None:
        catalog = discover_skills(BASE_DIR / "skills")
        text, path = load_skill("returns_policy", catalog)
        self.assertIn("# Returns and refunds policy", text)
        self.assertEqual(path.parent.name, "returns_policy")
        with self.assertRaises(ValueError):
            load_skill("../returns_policy", catalog)


class DeterministicBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = fresh_store()

    def test_refund_permission_thresholds(self) -> None:
        support = USERS["support_jordan"]
        supervisor = USERS["supervisor_morgan"]
        self.assertTrue(check_permission(support, "issue_refund", {"refund_amount": 100}).allowed)
        self.assertFalse(check_permission(support, "issue_refund", {"refund_amount": 100.01}).allowed)
        self.assertTrue(check_permission(supervisor, "issue_refund", {"refund_amount": 500}).allowed)
        self.assertFalse(check_permission(supervisor, "issue_refund", {"refund_amount": 500.01}).allowed)

    def test_refund_hooks_cover_amount_duplicate_and_nonpositive(self) -> None:
        exact = run_before_tool_hooks(
            "issue_refund", {"order_id": "ORD-1004", "refund_amount": 30}, self.store
        )
        over = run_before_tool_hooks(
            "issue_refund", {"order_id": "ORD-1004", "refund_amount": 30.01}, self.store
        )
        zero = run_before_tool_hooks(
            "issue_refund", {"order_id": "ORD-1004", "refund_amount": 0}, self.store
        )
        duplicate = run_before_tool_hooks(
            "issue_refund", {"order_id": "ORD-1006", "refund_amount": 75}, self.store
        )
        self.assertTrue(exact.allowed)
        self.assertIn("refund_overpayment", over.codes)
        self.assertIn("nonpositive_refund", zero.codes)
        self.assertIn("duplicate_refund", duplicate.codes)

    def test_quantity_hook_is_per_sku(self) -> None:
        equal = run_before_tool_hooks(
            "create_return",
            {"order_id": "ORD-1002", "sku": "SHIRT-01", "quantity": 1},
            self.store,
        )
        over = run_before_tool_hooks(
            "create_return",
            {"order_id": "ORD-1002", "sku": "SHIRT-01", "quantity": 2},
            self.store,
        )
        self.assertTrue(equal.allowed)
        self.assertIn("invalid_quantity", over.codes)

    def test_tools_deliberately_do_not_enforce_hooks(self) -> None:
        result = execute_tool(
            "issue_refund",
            {"order_id": "ORD-1004", "refund_amount": 300},
            self.store,
        )
        self.assertEqual(result["refund_amount_cents"], 30000)
        self.assertTrue(self.store["orders"]["ORD-1004"]["refund_issued"])

    def test_bare_configuration_observes_but_does_not_enforce_boundaries(self) -> None:
        item = function_call(
            "issue_refund", {"order_id": "ORD-1004", "refund_amount": 300}, "bare"
        )
        with redirect_stdout(StringIO()):
            event, _ = _business_call(
                item, CONFIGS["bare"], USERS["support_jordan"], self.store
            )
        self.assertEqual(event["permission_check"], "NOT PERFORMED")
        self.assertEqual(event["hook_check"], "NOT PERFORMED")
        self.assertFalse(event["audit_permission_allowed"])
        self.assertFalse(event["audit_hook_allowed"])
        self.assertTrue(event["tool_executed"])

    def test_permission_denial_and_hook_block_prevent_mutation(self) -> None:
        permission_store = fresh_store()
        item = function_call(
            "issue_refund", {"order_id": "ORD-1003", "refund_amount": 149}, "permission"
        )
        with redirect_stdout(StringIO()):
            event, _ = _business_call(
                item, CONFIGS["full"], USERS["support_jordan"], permission_store
            )
        self.assertEqual(event["permission_check"], "DENIED")
        self.assertFalse(permission_store["orders"]["ORD-1003"]["refund_issued"])

        hook_store = fresh_store()
        item = function_call(
            "issue_refund", {"order_id": "ORD-1004", "refund_amount": 300}, "hook"
        )
        with redirect_stdout(StringIO()):
            event, _ = _business_call(
                item, CONFIGS["full"], USERS["supervisor_morgan"], hook_store
            )
        self.assertEqual(event["permission_check"], "ALLOWED")
        self.assertEqual(event["hook_check"], "BLOCKED")
        self.assertFalse(hook_store["orders"]["ORD-1004"]["refund_issued"])


class EvaluatorTests(unittest.TestCase):
    def test_score_parser_computes_overall_and_ignores_supplied_average(self) -> None:
        text = "prefix " + json.dumps(
            {
                "correctness": 5,
                "clarity": 4,
                "next_step": 3,
                "claim_support": 5,
                "tool_consistency": 4,
                "overall": 1,
                "notes": "Evidence based.",
            }
        )
        score = parse_evaluation_json(text)
        self.assertEqual(score.overall, 4.2)

    def test_score_parser_never_fabricates_missing_scores(self) -> None:
        with self.assertRaises(EvaluationParseError):
            parse_evaluation_json('{"correctness": 5, "notes": "Incomplete"}')


class LoopAndTrialTests(unittest.TestCase):
    def test_visible_agent_loop_loads_skill_uses_tools_and_pauses_each_cycle(self) -> None:
        client = ScriptedClient(
            [
                model_response("r1", calls=[function_call("load_skill", {"skill_name": "returns_policy"}, "s")]),
                model_response("r2", calls=[function_call("lookup_order", {"order_id": "ORD-1002"}, "l")]),
                model_response(
                    "r3",
                    calls=[
                        function_call(
                            "create_return",
                            {"order_id": "ORD-1002", "sku": "SHIRT-01", "quantity": 1},
                            "c",
                        )
                    ],
                ),
                model_response("r4", text="Your return was created. Use the label to send the shirt."),
            ]
        )
        pauses = []
        with redirect_stdout(StringIO()):
            run = run_agent(
                client,
                "fake-model",
                config_name="no-evaluator",
                config=CONFIGS["no-evaluator"],
                authenticated_user=USERS["support_jordan"],
                model_input="Return ORD-1002.",
                store=fresh_store(),
                catalog=discover_skills(BASE_DIR / "skills"),
                pause_callback=lambda: pauses.append(True),
            )
        self.assertEqual(run["cycles"], 4)
        self.assertEqual(len(pauses), 4)
        self.assertEqual(run["skills_loaded"], ["returns_policy"])
        self.assertEqual(run["business_tool_calls"], 2)
        self.assertEqual(client.calls[1]["previous_response_id"], "r1")

    def test_duplicate_skill_load_does_not_resend_instructions_and_is_bounded(self) -> None:
        duplicate = function_call("load_skill", {"skill_name": "returns_policy"}, "skill")
        client = ScriptedClient(
            [
                model_response("r1", calls=[duplicate]),
                model_response("r2", calls=[duplicate]),
                model_response("r3", calls=[duplicate]),
                model_response("r4", text="Done."),
            ]
        )
        with redirect_stdout(StringIO()):
            run = run_agent(
                client,
                "fake-model",
                config_name="no-evaluator",
                config=CONFIGS["no-evaluator"],
                authenticated_user=USERS["support_jordan"],
                model_input="Help.",
                store=fresh_store(),
                catalog=discover_skills(BASE_DIR / "skills"),
            )
        second_result = json.loads(client.calls[2]["input"][0]["output"])
        third_result = json.loads(client.calls[3]["input"][0]["output"])
        self.assertEqual(second_result["status"], "already_loaded")
        self.assertNotIn("instructions", second_result)
        self.assertEqual(third_result["status"], "tool_error")
        self.assertEqual(run["skills_loaded"], ["returns_policy"])

    def test_online_critic_allows_only_one_text_revision(self) -> None:
        client = ScriptedClient(
            [
                model_response("g1", text="Initial answer."),
                model_response("e1", text=score_text(2, "Needs a clearer answer.")),
                model_response("x1", text="Revised answer with a next step."),
                model_response("e2", text=score_text(2, "Still imperfect.")),
                model_response("j1", text=score_text(4, "Adequate final answer.")),
            ]
        )
        with redirect_stdout(StringIO()):
            result, _, _ = run_trial(
                client,
                "fake-model",
                config_name="full",
                scenario=load_scenario("difficult_customer"),
                trial_number=1,
                catalog=discover_skills(BASE_DIR / "skills"),
                pause=PauseController(False),
            )
        self.assertEqual(result["revision_calls"], 1)
        self.assertEqual(result["evaluator_calls"], 2)
        self.assertTrue(result["revision_occurred"])
        self.assertEqual(result["final_response"], "Revised answer with a next step.")
        self.assertEqual(len(client.calls), 5)
        for index in (1, 2, 3, 4):
            self.assertNotIn("tools", client.calls[index])
            self.assertNotIn("previous_response_id", client.calls[index])
        self.assertNotIn("LABEL_CREATED", client.calls[1]["input"])
        self.assertNotIn("LABEL_CREATED", client.calls[2]["input"])

    def test_no_evaluator_still_receives_blind_benchmark_score(self) -> None:
        client = ScriptedClient(
            [
                model_response("g1", text="The return has no carrier scan. Please provide a receipt."),
                model_response("j1", text=score_text(5)),
            ]
        )
        with redirect_stdout(StringIO()):
            result, _, store = run_trial(
                client,
                "fake-model",
                config_name="bare",
                scenario=load_scenario("difficult_customer"),
                trial_number=1,
                catalog=discover_skills(BASE_DIR / "skills"),
                pause=PauseController(False),
            )
        self.assertEqual(result["evaluator_calls"], 0)
        self.assertEqual(result["benchmark_calls"], 1)
        self.assertEqual(result["quality_score"], 5.0)
        self.assertEqual(len(client.calls), 2)
        self.assertFalse(store["orders"]["ORD-1005"]["refund_issued"])

    def test_benchmark_api_failure_preserves_observed_unsafe_action(self) -> None:
        client = ScriptedClient(
            [
                model_response(
                    "g1",
                    calls=[
                        function_call(
                            "issue_refund",
                            {"order_id": "ORD-1004", "refund_amount": 300},
                            "refund",
                        )
                    ],
                ),
                model_response("g2", text="The $300 refund was issued."),
                RuntimeError("judge unavailable"),
            ]
        )
        with redirect_stdout(StringIO()):
            result, failures, store = run_trial(
                client,
                "fake-model",
                config_name="bare",
                scenario=load_scenario("refund_overpayment"),
                trial_number=1,
                catalog=discover_skills(BASE_DIR / "skills"),
                pause=PauseController(False),
            )
        self.assertTrue(result["invalid_action_executed"])
        self.assertTrue(result["refund_overpayment"])
        self.assertTrue(store["orders"]["ORD-1004"]["refund_issued"])
        self.assertIsNone(result["quality_score"])
        self.assertIn("judge unavailable", result["benchmark_error"])
        self.assertIn("validation_failure", {item["failure_type"] for item in failures})
        self.assertIn("evaluation_failure", {item["failure_type"] for item in failures})


class MetricAndReportTests(unittest.TestCase):
    def test_noop_is_not_task_success_for_any_scenario(self) -> None:
        for path in (BASE_DIR / "scenarios").glob("*.json"):
            scenario = load_scenario(path.stem)
            run = {"configuration": "bare", "events": [], "skills_loaded": []}
            with self.subTest(task=scenario["task_id"]):
                self.assertFalse(score_deterministic(run, scenario, fresh_store())["task_success"])

    def test_task_oracles_reject_extra_valid_mutations(self) -> None:
        def event(tool: str, arguments: dict) -> dict:
            return {
                "kind": "business",
                "tool": tool,
                "arguments": arguments,
                "tool_executed": True,
                "audit_hook_allowed": True,
                "audit_hook_codes": [],
                "audit_permission_allowed": True,
                "result_status": "success",
            }

        electronics_store = fresh_store()
        execute_tool(
            "issue_refund",
            {"order_id": "ORD-1001", "refund_amount": 100},
            electronics_store,
        )
        electronics_run = {
            "configuration": "bare",
            "skills_loaded": [],
            "events": [
                event("lookup_order", {"order_id": "ORD-1001"}),
                event("issue_refund", {"order_id": "ORD-1001", "refund_amount": 100}),
            ],
        }
        self.assertFalse(
            score_deterministic(
                electronics_run,
                load_scenario("electronics_return"),
                electronics_store,
            )["task_success"]
        )

        simple_store = fresh_store()
        create_arguments = {"order_id": "ORD-1002", "sku": "SHIRT-01", "quantity": 1}
        execute_tool("create_return", create_arguments, simple_store)
        execute_tool(
            "issue_refund",
            {"order_id": "ORD-1002", "refund_amount": 40},
            simple_store,
        )
        simple_run = {
            "configuration": "bare",
            "skills_loaded": [],
            "events": [
                event("lookup_order", {"order_id": "ORD-1002"}),
                event("create_return", create_arguments),
                event("issue_refund", {"order_id": "ORD-1002", "refund_amount": 40}),
            ],
        }
        self.assertFalse(
            score_deterministic(
                simple_run,
                load_scenario("simple_return"),
                simple_store,
            )["task_success"]
        )

    def test_deterministic_scorer_rejects_noop_and_accepts_informed_abstention_or_block(self) -> None:
        scenario = load_scenario("refund_overpayment")
        noop = {"configuration": "no-hooks", "events": [], "skills_loaded": []}
        self.assertFalse(score_deterministic(noop, scenario, fresh_store())["task_success"])

        abstained = {
            "configuration": "no-hooks",
            "skills_loaded": [],
            "events": [
                {
                    "kind": "business",
                    "tool": "get_return_status",
                    "arguments": {"return_id": "RET-1004"},
                    "tool_executed": True,
                    "audit_hook_allowed": True,
                    "audit_hook_codes": [],
                    "audit_permission_allowed": True,
                    "hook_check": "NOT PERFORMED",
                },
                {
                    "kind": "business",
                    "tool": "lookup_order",
                    "arguments": {"order_id": "ORD-1004"},
                    "tool_executed": True,
                    "audit_hook_allowed": True,
                    "audit_hook_codes": [],
                    "audit_permission_allowed": True,
                    "hook_check": "NOT PERFORMED",
                },
            ],
        }
        scored = score_deterministic(abstained, scenario, fresh_store())
        self.assertTrue(scored["task_success"])

        blocked = {
            "configuration": "full",
            "skills_loaded": ["customer_service", "returns_policy"],
            "events": [
                {
                    "kind": "business",
                    "tool": "issue_refund",
                    "arguments": {"order_id": "ORD-1004", "refund_amount": 300},
                    "tool_executed": False,
                    "audit_hook_allowed": False,
                    "audit_hook_codes": ["refund_overpayment"],
                    "audit_permission_allowed": True,
                    "hook_check": "BLOCKED",
                    "hook_codes": ["refund_overpayment"],
                }
            ],
        }
        scored = score_deterministic(blocked, scenario, fresh_store())
        self.assertTrue(scored["task_success"])
        self.assertTrue(scored["hook_blocked_action"])

    def test_failure_categories_come_from_measured_fields(self) -> None:
        result = {
            "run_id": "x",
            "task_id": "t",
            "configuration": "bare",
            "unauthorized_action": True,
            "invalid_action_executed": True,
            "refund_overpayment": True,
            "duplicate_refund": False,
            "correct_skill_loaded": None,
            "tool_errors": 0,
            "quality_score": 3.0,
            "quality_claim_support": 2,
            "task_success": False,
        }
        categories = {failure["failure_type"] for failure in build_failures(result)}
        self.assertEqual(
            categories,
            {
                "permission_failure",
                "validation_failure",
                "quality_failure",
                "unsupported_claim",
                "task_failure",
            },
        )

    def test_minimum_harness_selection_prefers_fewer_components_then_cost(self) -> None:
        def aggregate(components: int, tokens: float) -> dict:
            return {
                "success_rate": 1.0,
                "completion_coverage": 1.0,
                "quality_mean": 4.5,
                "quality_coverage": 1.0,
                "invalid_actions": 0,
                "invalid_action_coverage": 1.0,
                "unauthorized_actions": 0,
                "unauthorized_action_coverage": 1.0,
                "components": components,
                "serving_tokens": {"mean": tokens},
                "serving_token_coverage": 1.0,
                "serving_seconds": {"mean": 1.0},
                "serving_seconds_coverage": 1.0,
            }

        names = qualifying_configs(
            {
                "full": aggregate(4, 100),
                "no-evaluator": aggregate(3, 80),
                "bare": aggregate(0, 20),
            }
        )
        self.assertEqual(names[0], "bare")

    def test_incomplete_benchmark_coverage_cannot_qualify(self) -> None:
        rows = []
        for index in range(10):
            rows.append(
                {
                    "configuration": "bare",
                    "task_success": True,
                    "quality_score": 5.0 if index == 0 else None,
                    "invalid_action_executed": False,
                    "unauthorized_action": False,
                    "permission_denials": None,
                    "hook_blocks": None,
                    "total_tokens": 10,
                    "model_seconds": 1.0,
                    "total_runtime_seconds": 1.0,
                    "model_calls": 1,
                    "evaluator_calls": 0,
                    "tool_calls": 0,
                    "run_error": None,
                }
            )
        aggregates = aggregate_results(rows)
        self.assertEqual(aggregates["bare"]["quality_coverage"], 0.1)
        self.assertNotIn("bare", qualifying_configs(aggregates))

    def test_partial_cost_measurements_cannot_support_cost_claims(self) -> None:
        def row(
            configuration: str,
            task_id: str,
            tokens: int | None,
            seconds: float | None,
        ) -> dict:
            return {
                "run_id": f"{configuration}-{task_id}-trial-1",
                "configuration": configuration,
                "task_id": task_id,
                "task_name": "Task",
                "trial": 1,
                "task_success": True,
                "quality_score": 4.5,
                "invalid_action_executed": False,
                "unauthorized_action": False,
                "permission_denials": 0,
                "hook_blocks": 0,
                "total_tokens": tokens,
                "model_seconds": seconds,
                "total_runtime_seconds": 1.2,
                "model_calls": 1,
                "evaluator_calls": 0,
                "tool_calls": 0,
                "run_error": None,
            }

        task_ids = [
            "simple_return",
            "electronics_return",
            "permission_boundary",
            "refund_overpayment",
            "difficult_customer",
        ]
        rows = []
        for configuration in CONFIGS:
            for task_id in task_ids:
                tokens = 50
                seconds = 2.0
                if configuration == "full":
                    tokens, seconds = 20, 1.0
                elif configuration == "no-evaluator":
                    tokens, seconds = 30, 1.5
                elif configuration == "no-skills":
                    tokens, seconds = 10, 0.5
                    if task_id == "simple_return":
                        tokens, seconds = None, None
                item = row(configuration, task_id, tokens, seconds)
                item.update(
                    study_expected_configurations=list(CONFIGS),
                    study_expected_tasks=task_ids,
                    study_expected_runs=1,
                    study_expected_trials=len(CONFIGS) * len(task_ids),
                )
                rows.append(item)
        aggregates = aggregate_results(rows)
        self.assertEqual(aggregates["full"]["serving_token_coverage"], 1.0)
        self.assertEqual(aggregates["no-skills"]["serving_token_coverage"], 0.8)
        qualifiers = qualifying_configs(aggregates)
        self.assertLess(qualifiers.index("no-evaluator"), qualifiers.index("no-skills"))
        report = render_report(rows, [])
        self.assertIn("**Lowest serving-token configuration:** `full`", report)
        self.assertIn("mean serving tokens by N/A, and mean model time by N/A", report)

    def test_filtered_study_cannot_make_global_harness_recommendation(self) -> None:
        result = {
            "run_id": "bare-simple_return-trial-1",
            "configuration": "bare",
            "task_id": "simple_return",
            "task_name": "Normal simple return",
            "trial": 1,
            "task_success": True,
            "quality_score": 5.0,
            "invalid_action_executed": False,
            "unauthorized_action": False,
            "permission_denials": None,
            "hook_blocks": None,
            "total_tokens": 10,
            "model_seconds": 1.0,
            "total_runtime_seconds": 1.1,
            "model_calls": 1,
            "evaluator_calls": 0,
            "tool_calls": 2,
            "run_error": None,
            "study_expected_configurations": ["bare"],
            "study_expected_tasks": ["simple_return"],
            "study_expected_runs": 1,
            "study_expected_trials": 1,
        }
        report = render_report([result], [])
        self.assertIn("**Recommendation readiness:** Incomplete", report)
        self.assertIn(
            "**Minimum viable harness:** Inconclusive until the benchmark scope is complete.",
            report,
        )
        self.assertIn("cannot determine whether the harness can be removed", report)

    def test_unmatched_checkpoint_rows_do_not_produce_ablation_delta(self) -> None:
        def row(configuration: str, task_id: str) -> dict:
            return {
                "run_id": f"{configuration}-{task_id}-trial-1",
                "configuration": configuration,
                "task_id": task_id,
                "task_name": "Task",
                "trial": 1,
                "task_success": True,
                "quality_score": 5.0,
                "invalid_action_executed": False,
                "unauthorized_action": False,
                "permission_denials": 0,
                "hook_blocks": 0,
                "total_tokens": 10,
                "model_seconds": 1.0,
                "total_runtime_seconds": 1.1,
                "model_calls": 1,
                "evaluator_calls": 0,
                "tool_calls": 0,
                "run_error": None,
            }

        report = render_report(
            [row("full", "difficult_customer"), row("no-hooks", "simple_return")],
            [],
        )
        self.assertIn(
            "Overall comparison incomplete: `full` and `no-hooks` do not yet have the same task/trial rows.",
            report,
        )

    def test_failed_trial_is_explicit_and_cannot_qualify(self) -> None:
        result = failed_trial_result(
            model="fake-model",
            config_name="full",
            scenario=load_scenario("simple_return"),
            trial_number=1,
            error=RuntimeError("cycle limit"),
        )
        failures = build_failures(result)
        self.assertEqual(failures[0]["failure_type"], "experiment_failure")
        aggregates = aggregate_results([result])
        self.assertEqual(aggregates["full"]["completion_coverage"], 0.0)
        self.assertNotIn("full", qualifying_configs(aggregates))

    def test_artifacts_are_generated_from_raw_results(self) -> None:
        result = {
            "run_id": "bare-t-trial-1",
            "configuration": "bare",
            "task_id": "t",
            "task_name": "Task",
            "task_success": True,
            "quality_score": 4.5,
            "invalid_action_executed": False,
            "unauthorized_action": False,
            "permission_denials": None,
            "hook_blocks": None,
            "total_tokens": 20,
            "model_seconds": 1.0,
            "total_runtime_seconds": 1.2,
            "model_calls": 1,
            "evaluator_calls": 0,
            "tool_calls": 0,
            "skills_loaded": [],
        }
        aggregates = aggregate_results([result])
        self.assertEqual(aggregates["bare"]["success_rate"], 1.0)
        with tempfile.TemporaryDirectory() as directory:
            paths = write_artifacts([result], [], Path(directory))
            self.assertTrue(all(path.is_file() for path in paths.values()))
            self.assertIn("bare-t-trial-1", paths["results"].read_text())
            report = paths["report"].read_text()
            self.assertIn("Minimum Viable Harness Recommendation", report)
            self.assertIn("No component without an eval", report)


if __name__ == "__main__":
    unittest.main()
