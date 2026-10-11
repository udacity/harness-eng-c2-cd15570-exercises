"""Deterministic tests for the cumulative Module 5 harness-evaluation demo."""

import csv
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from agent import public_tool_trace
from catalog import discover_skills
from clients import ScriptedClient, STAKEHOLDER_POOR, STAKEHOLDER_REVISED
from config import CONFIGS, HarnessConfig
from data import fresh_incident
from experiment import run_trial
from metrics import (
    _study_readiness,
    aggregate_by_task,
    aggregate_results,
    qualifying_configs,
    render_report,
    score_deterministic,
    write_artifacts,
)
from tasks import CORE_TASK_IDS, load_core_scenarios, load_scenario
from tools import execute_tool


BASE_DIR = Path(__file__).resolve().parent
MODEL = "scripted-fixture"


class DemoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = discover_skills(BASE_DIR / "skills")
        cls.scenarios = load_core_scenarios()
        cls.results = []
        cls.failures = []
        cls.runs = {}
        expected_tasks = [scenario["task_id"] for scenario in cls.scenarios]
        for config_name, config in CONFIGS.items():
            for scenario in cls.scenarios:
                result, failures, _, run = run_trial(
                    ScriptedClient(scenario, config),
                    MODEL,
                    config_name=config_name,
                    scenario=scenario,
                    trial_number=1,
                    catalog=cls.catalog,
                    emit=lambda _message: None,
                )
                result.update(
                    study_expected_configurations=list(CONFIGS),
                    study_expected_tasks=expected_tasks,
                    study_expected_runs=1,
                    study_expected_trials=len(CONFIGS) * len(cls.scenarios),
                )
                cls.results.append(result)
                cls.failures.extend(failures)
                cls.runs[(config_name, scenario["task_id"])] = run

    def row(self, config_name: str, task_id: str) -> dict:
        return next(
            row
            for row in self.results
            if row["configuration"] == config_name and row["task_id"] == task_id
        )


class ConfigurationTests(DemoTestCase):
    def test_exact_six_configuration_matrix(self) -> None:
        self.assertEqual(
            CONFIGS,
            {
                "full": HarnessConfig(True, True, True, True),
                "no-skills": HarnessConfig(False, True, True, True),
                "no-evaluator": HarnessConfig(True, False, True, True),
                "no-hooks": HarnessConfig(True, True, False, True),
                "no-permissions": HarnessConfig(True, True, True, False),
                "bare": HarnessConfig(False, False, False, False),
            },
        )

    def test_each_named_ablation_changes_one_full_switch(self) -> None:
        full = CONFIGS["full"]
        for name in ("no-skills", "no-evaluator", "no-hooks", "no-permissions"):
            removed = CONFIGS[name]
            differences = [
                field
                for field in ("skills", "evaluator", "hooks", "permissions")
                if getattr(full, field) != getattr(removed, field)
            ]
            self.assertEqual(differences, [name.removeprefix("no-")])
            self.assertEqual(removed.component_count, 3)

    def test_five_core_tasks_are_loaded_once(self) -> None:
        task_ids = [scenario["task_id"] for scenario in self.scenarios]
        self.assertEqual(set(task_ids), CORE_TASK_IDS)
        self.assertEqual(len(task_ids), len(set(task_ids)))


class BoundaryTests(DemoTestCase):
    def test_tools_remain_permissive_without_harness_boundaries(self) -> None:
        incident = fresh_incident()
        execute_tool(
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v40"},
            incident,
        )
        self.assertEqual(incident["current_deployment"], "checkout-v40")

    def test_hook_ablation_exposes_invalid_execution(self) -> None:
        protected = self.row("full", "unsafe_rollback")
        ablated = self.row("no-hooks", "unsafe_rollback")
        self.assertTrue(protected["hook_probe_exercised"])
        self.assertTrue(ablated["hook_probe_exercised"])
        self.assertFalse(protected["invalid_action_executed"])
        self.assertEqual(
            self.runs[("full", "unsafe_rollback")]["final_incident"]["current_deployment"],
            "checkout-v42",
        )
        self.assertTrue(ablated["invalid_action_executed"])
        self.assertEqual(
            self.runs[("no-hooks", "unsafe_rollback")]["final_incident"]["current_deployment"],
            "checkout-v40",
        )

    def test_permission_ablation_exposes_unauthorized_execution(self) -> None:
        protected = self.row("full", "permission_boundary")
        ablated = self.row("no-permissions", "permission_boundary")
        self.assertTrue(protected["permission_probe_exercised"])
        self.assertTrue(ablated["permission_probe_exercised"])
        self.assertFalse(protected["unauthorized_action"])
        self.assertTrue(ablated["unauthorized_action"])
        self.assertEqual(
            self.runs[("no-permissions", "permission_boundary")]["final_incident"]["current_deployment"],
            "checkout-v41",
        )

    def test_disabled_boundaries_are_observed_but_not_reported_as_enforced(self) -> None:
        no_hooks = self.row("no-hooks", "unsafe_rollback")
        no_permissions = self.row("no-permissions", "permission_boundary")
        self.assertIsNone(no_hooks["hook_checks"])
        self.assertIsNone(no_permissions["permission_checks"])
        hook_event = self.runs[("no-hooks", "unsafe_rollback")]["events"][-1]
        permission_event = self.runs[("no-permissions", "permission_boundary")]["events"][-1]
        self.assertFalse(hook_event["audit_hook_allowed"])
        self.assertFalse(permission_event["audit_permission_allowed"])

    def test_blind_trace_hides_configuration_and_shadow_labels(self) -> None:
        events = self.runs[("no-hooks", "unsafe_rollback")]["events"]
        serialized = json.dumps(public_tool_trace(events))
        self.assertNotIn("no-hooks", serialized)
        self.assertNotIn("audit_hook", serialized)
        self.assertNotIn("permission_check", serialized)

    def test_model_refusal_does_not_count_as_an_exercised_hook_probe(self) -> None:
        run = deepcopy(self.runs[("full", "unsafe_rollback")])
        run["events"] = [
            event
            for event in run["events"]
            if event.get("tool") != "rollback_deployment"
        ]
        result = score_deterministic(
            run,
            load_scenario("unsafe_rollback"),
            fresh_incident(),
        )
        self.assertFalse(result["hook_probe_exercised"])
        self.assertFalse(result["task_success"])


class ComponentEffectTests(DemoTestCase):
    def test_skills_change_specialized_task_behavior(self) -> None:
        full = self.row("full", "specialized_diagnosis")
        removed = self.row("no-skills", "specialized_diagnosis")
        self.assertTrue(full["task_success"])
        self.assertEqual(
            set(full["skills_loaded"]),
            {"checkout_service_runbook"},
        )
        self.assertTrue(full["required_response_terms_present"])
        self.assertFalse(removed["task_success"])
        self.assertFalse(removed["required_response_terms_present"])
        self.assertEqual(removed["skills_loaded"], [])

    def test_online_evaluator_performs_one_text_only_revision(self) -> None:
        full = self.row("full", "stakeholder_update")
        removed = self.row("no-evaluator", "stakeholder_update")
        self.assertEqual(full["candidate_response"], STAKEHOLDER_POOR)
        self.assertEqual(full["final_response"], STAKEHOLDER_REVISED)
        self.assertTrue(full["revision_occurred"])
        self.assertEqual(full["evaluator_calls"], 2)
        self.assertEqual(full["revision_calls"], 1)
        self.assertEqual(removed["candidate_response"], removed["final_response"])
        self.assertFalse(removed["revision_occurred"])
        self.assertTrue(full["response_policy_passed"])
        self.assertFalse(removed["response_policy_passed"])
        self.assertEqual(removed["evaluator_calls"], 0)
        self.assertEqual(
            self.runs[("full", "stakeholder_update")]["final_incident"],
            self.runs[("no-evaluator", "stakeholder_update")]["final_incident"],
        )

    def test_benchmark_cost_is_not_counted_as_serving_cost(self) -> None:
        row = self.row("full", "routine_triage")
        serving_from_calls = sum(
            call["total_tokens"]
            for call in self.runs[("full", "routine_triage")]["serving_calls"]
        )
        self.assertEqual(row["total_tokens"], serving_from_calls)
        self.assertGreater(row["benchmark_total_tokens"], 0)
        self.assertEqual(row["benchmark_calls"], 1)

    def test_blind_judge_can_use_a_separate_model(self) -> None:
        scenario = load_scenario("routine_triage")
        client = ScriptedClient(scenario, CONFIGS["full"])
        result, _, _, _ = run_trial(
            client,
            MODEL,
            config_name="full",
            scenario=scenario,
            trial_number=1,
            catalog=self.catalog,
            judge_model="independent-judge",
            emit=lambda _message: None,
        )
        judge_calls = [
            call
            for call in client.responses.calls
            if "blind offline incident-response judge"
            in str(call.get("instructions", ""))
        ]
        self.assertEqual(result["model"], MODEL)
        self.assertEqual(result["judge_model"], "independent-judge")
        self.assertEqual(len(judge_calls), 1)
        self.assertEqual(judge_calls[0]["model"], "independent-judge")

    def test_every_trial_starts_from_pristine_state(self) -> None:
        mutated = self.runs[("no-hooks", "unsafe_rollback")]["final_incident"]
        later = self.runs[("no-permissions", "routine_triage")]["initial_incident"]
        self.assertEqual(mutated["current_deployment"], "checkout-v40")
        self.assertEqual(later, fresh_incident())


class EvaluationTests(DemoTestCase):
    def test_full_matrix_has_expected_measured_effects(self) -> None:
        aggregates = aggregate_results(self.results)
        expected = {
            "full": (1.0, 5.0, 0, 0),
            "no-skills": (0.8, 4.6, 0, 0),
            "no-evaluator": (0.8, 4.4, 0, 0),
            "no-hooks": (0.8, 4.6, 1, 0),
            "no-permissions": (0.8, 4.8, 0, 1),
            "bare": (0.2, 2.0, 2, 1),
        }
        for name, values in expected.items():
            observed = aggregates[name]
            self.assertEqual(
                (
                    observed["success_rate"],
                    observed["quality_mean"],
                    observed["invalid_actions"],
                    observed["unauthorized_actions"],
                ),
                values,
            )

    def test_target_task_ablation_pairs_isolate_each_component(self) -> None:
        by_task = aggregate_by_task(self.results)
        self.assertEqual(by_task[("no-skills", "specialized_diagnosis")]["success_rate"], 0)
        self.assertEqual(by_task[("no-evaluator", "stakeholder_update")]["quality_mean"], 2)
        self.assertEqual(by_task[("no-hooks", "unsafe_rollback")]["invalid_actions"], 1)
        self.assertEqual(by_task[("no-permissions", "permission_boundary")]["unauthorized_actions"], 1)

    def test_only_full_harness_qualifies(self) -> None:
        aggregates = aggregate_results(self.results)
        self.assertEqual(qualifying_configs(aggregates), ["full"])

    def test_complete_plan_is_ready_for_global_recommendation(self) -> None:
        readiness = _study_readiness(self.results)
        self.assertEqual(readiness["planned_trials"], 30)
        self.assertEqual(readiness["recorded_planned_trials"], 30)
        self.assertTrue(readiness["plan_complete"])
        self.assertTrue(readiness["core_scope"])
        self.assertTrue(readiness["target_probes_complete"])
        self.assertTrue(readiness["recommendation_ready"])

    def test_readiness_rejects_an_unexercised_target_probe(self) -> None:
        incomplete = deepcopy(self.results)
        target = next(
            row
            for row in incomplete
            if row["configuration"] == "full"
            and row["task_id"] == "unsafe_rollback"
        )
        target["hook_probe_exercised"] = False
        readiness = _study_readiness(incomplete)
        self.assertFalse(readiness["target_probes_complete"])
        self.assertFalse(readiness["recommendation_ready"])
        self.assertEqual(
            readiness["reason"],
            "one or more component-target probes were not exercised",
        )

    def test_readiness_rejects_filtered_duplicate_and_invalid_plans(self) -> None:
        filtered = [
            deepcopy(row)
            for row in self.results
            if row["configuration"] == "full"
        ]
        for row in filtered:
            row["study_expected_configurations"] = ["full"]
            row["study_expected_trials"] = 5
        self.assertTrue(_study_readiness(filtered)["plan_complete"])
        self.assertFalse(_study_readiness(filtered)["core_scope"])

        duplicate = [*self.results, deepcopy(self.results[0])]
        self.assertFalse(_study_readiness(duplicate)["plan_complete"])

        invalid = [deepcopy(self.results[0])]
        invalid[0]["study_expected_runs"] = True
        self.assertEqual(
            _study_readiness(invalid)["reason"],
            "study-plan metadata is unavailable",
        )

    def test_report_and_raw_artifacts_are_derived_from_rows(self) -> None:
        report = render_report(self.results, self.failures)
        self.assertIn("Minimum qualifying harness: `full`", report)
        self.assertIn("Component-target probes: complete", report)
        self.assertIn("| no-hooks | 3 | 5 | 80.0% | 4.60 | 3.00", report)
        with tempfile.TemporaryDirectory() as directory:
            paths = write_artifacts(
                self.results, self.failures, Path(directory)
            )
            self.assertEqual(set(paths), {"results", "failures", "report"})
            with paths["results"].open(newline="", encoding="utf-8") as source:
                self.assertEqual(len(list(csv.DictReader(source))), 30)
            self.assertIsInstance(
                json.loads(paths["failures"].read_text(encoding="utf-8")), list
            )


if __name__ == "__main__":
    unittest.main()
