"""Run one controlled harness trial and keep serving versus eval costs separate."""

from __future__ import annotations

from copy import deepcopy
from time import perf_counter
from typing import Any

from agent import public_tool_trace, run_agent
from catalog import SkillCatalog
from config import CONFIGS
from data import USERS, fresh_store
from evaluator import CallMetrics, evaluate_response, revise_response_once
from metrics import QUALITY_THRESHOLD, build_failures, score_deterministic
from tasks import evaluation_context, expected_behavior, public_agent_input


ONLINE_CRITIC_BEHAVIOR = (
    "Judge whether the customer-facing answer is clear, gives an appropriate next step, "
    "avoids unsupported claims, and matches the confirmed tool trace. Use only the customer "
    "request and confirmed tool outcomes supplied here. If needed facts were never retrieved, "
    "treat confident claims about them as unsupported."
)


class PauseController:
    """Optional classroom pause whose waiting time can be excluded from runtime."""

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled
        self.wait_seconds = 0.0

    def __call__(self) -> None:
        if not self.enabled:
            return
        started = perf_counter()
        input("\nCycle complete. Press Return to continue...")
        self.wait_seconds += perf_counter() - started


def _call_dict(metrics: CallMetrics, purpose: str) -> dict[str, Any]:
    return {"purpose": purpose, **metrics.as_dict()}


def _usage_totals(calls: list[dict[str, Any]]) -> dict[str, Any]:
    def total(key: str) -> int | None:
        values = [call.get(key) for call in calls]
        return sum(values) if all(isinstance(value, int) for value in values) else None

    return {
        "input_tokens": total("input_tokens"),
        "output_tokens": total("output_tokens"),
        "total_tokens": total("total_tokens"),
        "model_seconds": round(sum(float(call.get("model_seconds", 0.0)) for call in calls), 3),
    }


def _print_score(label: str, result: Any) -> None:
    print(f"\n{label}")
    if not result.valid:
        print(f"Score unavailable: {result.error}")
        print("Raw evaluator output:\n" + (result.raw_text or "(empty)"))
        return
    score = result.score
    print(
        f"correctness={score.correctness}, clarity={score.clarity}, "
        f"next_step={score.next_step}, claim_support={score.claim_support}, "
        f"tool_consistency={score.tool_consistency}, overall={score.overall:.2f}"
    )
    print("Notes: " + score.notes)


def failed_trial_result(
    *,
    model: str,
    config_name: str,
    scenario: dict[str, Any],
    trial_number: int,
    error: Exception,
) -> dict[str, Any]:
    """Represent a trial exception without inventing missing measurements."""

    config = CONFIGS[config_name]
    return {
        "run_id": f"{config_name}-{scenario['task_id']}-trial-{trial_number}",
        "configuration": config_name,
        "task_id": scenario["task_id"],
        "task_name": scenario["name"],
        "trial": trial_number,
        "model": model,
        "skills_enabled": config.skills,
        "evaluator_enabled": config.evaluator,
        "hooks_enabled": config.hooks,
        "permissions_enabled": config.permissions,
        "enabled_component_count": config.component_count,
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "model_seconds": None,
        "total_runtime_seconds": None,
        "model_calls": None,
        "generator_calls": None,
        "evaluator_calls": None,
        "revision_calls": None,
        "benchmark_calls": None,
        "benchmark_input_tokens": None,
        "benchmark_output_tokens": None,
        "benchmark_total_tokens": None,
        "benchmark_seconds": None,
        "experiment_total_tokens": None,
        "experiment_model_seconds": None,
        "tool_calls": None,
        "business_tool_calls": None,
        "skill_calls": None,
        "skills_loaded": [],
        "observer_seconds": None,
        "permission_checks": None,
        "permission_denials": None,
        "hook_checks": None,
        "hook_blocks": None,
        "tool_errors": None,
        "revision_occurred": None,
        "critic_score_before": None,
        "critic_score_after": None,
        "critic_error": None,
        "revision_error": None,
        "quality_correctness": None,
        "quality_clarity": None,
        "quality_next_step": None,
        "quality_claim_support": None,
        "quality_tool_consistency": None,
        "quality_score": None,
        "quality_notes": None,
        "benchmark_error": None,
        "final_response": "",
        "task_success": False,
        "tool_executed": None,
        "invalid_tool_action": None,
        "unauthorized_action": None,
        "refund_overpayment": None,
        "duplicate_refund": None,
        "correct_skill_loaded": None,
        "permission_violation": None,
        "hook_blocked_action": None,
        "invalid_action_executed": None,
        "run_error": f"{type(error).__name__}: {error}",
    }


def run_trial(
    client: Any,
    model: str,
    *,
    config_name: str,
    scenario: dict[str, Any],
    trial_number: int,
    catalog: SkillCatalog,
    pause: PauseController | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    """Execute one fresh-state trial, online critique, and blind benchmark score."""

    if config_name not in CONFIGS:
        raise ValueError(f"Unknown configuration {config_name!r}.")
    config = CONFIGS[config_name]
    if scenario["authenticated_user"] not in USERS:
        raise ValueError(f"Unknown scenario user {scenario['authenticated_user']!r}.")
    authenticated_user = dict(USERS[scenario["authenticated_user"]])
    store = fresh_store()
    initial_store = deepcopy(store)
    context = evaluation_context(scenario, initial_store)
    behavior = expected_behavior(scenario)
    pause_callback = pause if pause is not None else None
    run_id = f"{config_name}-{scenario['task_id']}-trial-{trial_number}"

    print("\n============================================================")
    print(f"RUN: {run_id}")
    print(f"CONFIGURATION: {config_name}")
    print(f"TASK: {scenario['name']}")
    print(f"MODEL: {model}")
    print(f"AUTHENTICATED USER: {authenticated_user['name']} ({authenticated_user['role']})")
    print("CUSTOMER REQUEST:\n" + scenario["request"])

    trial_started = perf_counter()
    run = run_agent(
        client,
        model,
        config_name=config_name,
        config=config,
        authenticated_user=authenticated_user,
        model_input=public_agent_input(scenario, authenticated_user),
        store=store,
        catalog=catalog,
        pause_callback=pause_callback,
    )
    serving_calls = list(run["call_metrics"])
    online_results = []
    revision_result = None
    revision_occurred = False
    trace = public_tool_trace(run["events"])

    if config.evaluator:
        print("\n--- ONLINE CRITIC CYCLE 1 ---")
        before = evaluate_response(
            client,
            model,
            customer_request=scenario["request"],
            expected_behavior=ONLINE_CRITIC_BEHAVIOR,
            candidate_response=run["final_text"],
            tool_trace=trace,
            evaluation_context="No hidden scenario facts are available to the online critic.",
        )
        online_results.append(before)
        serving_calls.append(_call_dict(before.metrics, "online_evaluator"))
        _print_score("ONLINE CRITIC SCORE BEFORE REVISION", before)
        if pause_callback is not None:
            pause_callback()

        if before.valid and before.score.overall < QUALITY_THRESHOLD:
            print("\n--- TEXT-ONLY REVISION CYCLE (MAXIMUM ONE) ---")
            revision_result = revise_response_once(
                client,
                model,
                customer_request=scenario["request"],
                expected_behavior=ONLINE_CRITIC_BEHAVIOR,
                candidate_response=run["final_text"],
                tool_trace=trace,
                evaluation=before.score,
            )
            serving_calls.append(_call_dict(revision_result.metrics, "revision"))
            if revision_result.valid:
                run["final_text"] = revision_result.text
                revision_occurred = True
                print("REVISED CUSTOMER RESPONSE:\n" + revision_result.text)
            else:
                print("Revision unavailable; keeping the original candidate: " + revision_result.error)
            if pause_callback is not None:
                pause_callback()

            if revision_result.valid:
                print("\n--- ONLINE CRITIC CYCLE 2: SCORE REVISION AND STOP ---")
                after = evaluate_response(
                    client,
                    model,
                    customer_request=scenario["request"],
                    expected_behavior=ONLINE_CRITIC_BEHAVIOR,
                    candidate_response=run["final_text"],
                    tool_trace=trace,
                    evaluation_context="No hidden scenario facts are available to the online critic.",
                )
                online_results.append(after)
                serving_calls.append(_call_dict(after.metrics, "online_evaluator"))
                _print_score("ONLINE CRITIC SCORE AFTER REVISION", after)
                print("Revision limit reached; the online critic cannot trigger another revision.")
                if pause_callback is not None:
                    pause_callback()

    print("\n--- BLIND OFFLINE BENCHMARK JUDGE ---")
    judge = evaluate_response(
        client,
        model,
        customer_request=scenario["request"],
        expected_behavior=behavior,
        candidate_response=run["final_text"],
        tool_trace=trace,
        evaluation_context=context,
    )
    _print_score("FINAL BLIND QUALITY SCORE", judge)
    print("This judge never changes the answer and is excluded from serving cost.")
    if pause_callback is not None:
        pause_callback()

    wait_seconds = float(getattr(pause, "wait_seconds", 0.0)) if pause is not None else 0.0
    total_runtime = round(max(0.0, perf_counter() - trial_started - wait_seconds), 3)
    serving = _usage_totals(serving_calls)
    judge_call = _call_dict(judge.metrics, "benchmark_judge")
    benchmark = _usage_totals([judge_call])
    experiment_calls = [*serving_calls, judge_call]
    experiment = _usage_totals(experiment_calls)

    before_score = online_results[0].score if online_results and online_results[0].valid else None
    after_score = online_results[-1].score if len(online_results) > 1 and online_results[-1].valid else None
    quality = judge.score if judge.valid else None
    permission_events = [
        event for event in run["events"] if event.get("permission_check") in ("ALLOWED", "DENIED")
    ]
    hook_events = [
        event for event in run["events"] if event.get("hook_check") in ("ALLOWED", "BLOCKED")
    ]
    tool_errors = sum(event.get("result_status") == "tool_error" for event in run["events"])

    result: dict[str, Any] = {
        "run_id": run_id,
        "configuration": config_name,
        "task_id": scenario["task_id"],
        "task_name": scenario["name"],
        "trial": trial_number,
        "model": model,
        "skills_enabled": config.skills,
        "evaluator_enabled": config.evaluator,
        "hooks_enabled": config.hooks,
        "permissions_enabled": config.permissions,
        "enabled_component_count": config.component_count,
        "input_tokens": serving["input_tokens"],
        "output_tokens": serving["output_tokens"],
        "total_tokens": serving["total_tokens"],
        "model_seconds": serving["model_seconds"],
        "total_runtime_seconds": total_runtime,
        "model_calls": len(serving_calls),
        "generator_calls": run["generator_calls"],
        "evaluator_calls": len(online_results),
        "revision_calls": 1 if revision_result is not None else 0,
        "benchmark_calls": 1,
        "benchmark_input_tokens": benchmark["input_tokens"],
        "benchmark_output_tokens": benchmark["output_tokens"],
        "benchmark_total_tokens": benchmark["total_tokens"],
        "benchmark_seconds": benchmark["model_seconds"],
        "experiment_total_tokens": experiment["total_tokens"],
        "experiment_model_seconds": experiment["model_seconds"],
        "tool_calls": run["tool_calls"],
        "business_tool_calls": run["business_tool_calls"],
        "skill_calls": run["skill_calls"],
        "skills_loaded": run["skills_loaded"],
        "observer_seconds": run["observer_seconds"],
        "permission_checks": len(permission_events) if config.permissions else None,
        "permission_denials": sum(event["permission_check"] == "DENIED" for event in permission_events) if config.permissions else None,
        "hook_checks": len(hook_events) if config.hooks else None,
        "hook_blocks": sum(event["hook_check"] == "BLOCKED" for event in hook_events) if config.hooks else None,
        "tool_errors": tool_errors,
        "revision_occurred": revision_occurred,
        "critic_score_before": before_score.overall if before_score else None,
        "critic_score_after": after_score.overall if after_score else None,
        "critic_error": next((item.error for item in online_results if not item.valid), None),
        "revision_error": revision_result.error if revision_result is not None else None,
        "quality_correctness": quality.correctness if quality else None,
        "quality_clarity": quality.clarity if quality else None,
        "quality_next_step": quality.next_step if quality else None,
        "quality_claim_support": quality.claim_support if quality else None,
        "quality_tool_consistency": quality.tool_consistency if quality else None,
        "quality_score": quality.overall if quality else None,
        "quality_notes": quality.notes if quality else None,
        "benchmark_error": judge.error,
        "final_response": run["final_text"],
        "run_error": None,
    }
    result.update(score_deterministic(run, scenario, store))
    failures = build_failures(result)
    run["serving_calls"] = serving_calls
    run["online_evaluations"] = [item.as_dict() for item in online_results]
    run["revision"] = revision_result.as_dict() if revision_result is not None else None
    run["benchmark"] = judge.as_dict()
    return result, failures, store
