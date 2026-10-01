"""Run one controlled harness trial and keep serving cost separate from judging."""

from copy import deepcopy
from time import perf_counter
from typing import Any, Callable

from agent import public_tool_trace, run_agent
from config import CONFIGS
from data import USERS, fresh_incident
from evaluator import evaluate_response, revise_response_once
from metrics import QUALITY_THRESHOLD, build_failures, score_deterministic
from tasks import public_agent_input


class PauseController:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled
        self.wait_seconds = 0.0

    def __call__(self) -> None:
        if not self.enabled:
            return
        started = perf_counter()
        input("\nCycle complete. Press Return to continue...")
        self.wait_seconds += perf_counter() - started


def _usage_totals(calls: list[dict[str, Any]]) -> dict[str, Any]:
    def total(key: str) -> int | None:
        values = [call.get(key) for call in calls]
        return sum(values) if all(isinstance(value, int) for value in values) else None

    return {
        "input_tokens": total("input_tokens"),
        "output_tokens": total("output_tokens"),
        "total_tokens": total("total_tokens"),
        "model_seconds": round(
            sum(float(call.get("model_seconds", 0.0)) for call in calls), 3
        ),
    }


def run_trial(
    client: Any,
    model: str,
    *,
    config_name: str,
    scenario: dict[str, Any],
    trial_number: int,
    catalog: dict,
    pause: PauseController | None = None,
    emit: Callable[[str], None] = print,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict, dict]:
    if config_name not in CONFIGS:
        raise ValueError(f"Unknown configuration: {config_name}")
    config = CONFIGS[config_name]
    user = dict(USERS[scenario["authenticated_user"]])
    incident = fresh_incident()
    initial_incident = deepcopy(incident)
    pause_callback = pause if pause is not None else PauseController(False)
    run_id = f"{config_name}-{scenario['task_id']}-trial-{trial_number}"

    emit("\n============================================================")
    emit(f"RUN: {run_id}")
    emit(f"TASK: {scenario['name']}")
    emit(f"AUTHENTICATED USER: {user['name']} ({user['role']})")
    emit("REQUEST: " + scenario["request"])
    started = perf_counter()
    run = run_agent(
        client,
        model,
        config_name=config_name,
        config=config,
        authenticated_user=user,
        model_input=public_agent_input(scenario, user),
        incident=incident,
        catalog=catalog,
        emit=emit,
        pause=pause_callback,
    )
    serving_calls = list(run["call_metrics"])
    trace = public_tool_trace(run["events"])
    critic_before = None
    critic_after = None
    revision_occurred = False

    if config.evaluator:
        emit("\n--- ONLINE CRITIC ---")
        critic_before, metric, error = evaluate_response(
            client,
            model,
            candidate=run["final_text"],
            request=scenario["request"],
            trace=trace,
            expected_behavior="Be correct, grounded, clear, and give a useful next step.",
            blind=False,
        )
        serving_calls.append(metric)
        if error:
            emit("ONLINE CRITIC ERROR: " + error)
        elif critic_before is not None:
            emit(f"ONLINE CRITIC SCORE: {critic_before.overall:.2f}/5")
            if critic_before.overall < QUALITY_THRESHOLD:
                emit("\n--- TEXT-ONLY REVISION (MAXIMUM ONE) ---")
                revised, revision_metric = revise_response_once(
                    client,
                    model,
                    candidate=run["final_text"],
                    request=scenario["request"],
                    trace=trace,
                    score=critic_before,
                )
                serving_calls.append(revision_metric)
                run["final_text"] = revised
                revision_occurred = True
                emit("REVISED RESPONSE:\n" + revised)
                critic_after, after_metric, after_error = evaluate_response(
                    client,
                    model,
                    candidate=revised,
                    request=scenario["request"],
                    trace=trace,
                    expected_behavior="Be correct, grounded, clear, and give a useful next step.",
                    blind=False,
                )
                serving_calls.append(after_metric)
                if after_error:
                    emit("SECOND CRITIC ERROR: " + after_error)
                elif critic_after is not None:
                    emit(f"REVISED CRITIC SCORE: {critic_after.overall:.2f}/5")

    emit("\n--- BLIND OFFLINE JUDGE ---")
    judge, benchmark_metric, benchmark_error = evaluate_response(
        client,
        model,
        candidate=run["final_text"],
        request=scenario["request"],
        trace=trace,
        expected_behavior=str(scenario["oracle"]),
        blind=True,
    )
    if benchmark_error:
        emit("BLIND JUDGE ERROR: " + benchmark_error)
    elif judge is not None:
        emit(f"BLIND QUALITY SCORE: {judge.overall:.2f}/5")
    emit("Blind-judge cost is experiment overhead, excluded from serving metrics.")

    wait_seconds = pause.wait_seconds if pause is not None else 0.0
    runtime = round(max(0.0, perf_counter() - started - wait_seconds), 3)
    serving = _usage_totals(serving_calls)
    benchmark = _usage_totals([benchmark_metric])
    permission_events = [
        event
        for event in run["events"]
        if event.get("permission_check") in {"ALLOWED", "DENIED"}
    ]
    hook_events = [
        event
        for event in run["events"]
        if event.get("hook_check") in {"ALLOWED", "BLOCKED"}
    ]
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
        "total_runtime_seconds": runtime,
        "model_calls": len(serving_calls),
        "generator_calls": run["generator_calls"],
        "evaluator_calls": sum(
            call.get("purpose") == "online_evaluator" for call in serving_calls
        ),
        "revision_calls": sum(
            call.get("purpose") == "revision" for call in serving_calls
        ),
        "benchmark_calls": 1,
        "benchmark_input_tokens": benchmark["input_tokens"],
        "benchmark_output_tokens": benchmark["output_tokens"],
        "benchmark_total_tokens": benchmark["total_tokens"],
        "benchmark_seconds": benchmark["model_seconds"],
        "tool_calls": run["tool_calls"],
        "business_tool_calls": run["business_tool_calls"],
        "skill_calls": run["skill_calls"],
        "skills_loaded": run["skills_loaded"],
        "permission_checks": len(permission_events) if config.permissions else None,
        "permission_denials": (
            sum(event["permission_check"] == "DENIED" for event in permission_events)
            if config.permissions
            else None
        ),
        "hook_checks": len(hook_events) if config.hooks else None,
        "hook_blocks": (
            sum(event["hook_check"] == "BLOCKED" for event in hook_events)
            if config.hooks
            else None
        ),
        "revision_occurred": revision_occurred,
        "critic_score_before": critic_before.overall if critic_before else None,
        "critic_score_after": critic_after.overall if critic_after else None,
        "quality_correctness": judge.correctness if judge else None,
        "quality_clarity": judge.clarity if judge else None,
        "quality_next_step": judge.next_step if judge else None,
        "quality_claim_support": judge.claim_support if judge else None,
        "quality_tool_consistency": judge.tool_consistency if judge else None,
        "quality_score": judge.overall if judge else None,
        "quality_notes": judge.notes if judge else None,
        "benchmark_error": benchmark_error,
        "candidate_response": run["candidate_text"],
        "final_response": run["final_text"],
        "run_error": None,
    }
    result.update(score_deterministic(run, scenario, incident))
    failures = build_failures(result)
    run["initial_incident"] = initial_incident
    run["final_incident"] = deepcopy(incident)
    run["serving_calls"] = serving_calls
    return result, failures, incident, run


def failed_trial_result(
    model: str,
    config_name: str,
    scenario: dict[str, Any],
    trial_number: int,
    error: Exception,
) -> dict[str, Any]:
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
        "quality_score": None,
        "total_tokens": None,
        "model_seconds": None,
        "invalid_action_executed": None,
        "unauthorized_action": None,
        "task_success": False,
        "run_error": f"{type(error).__name__}: {error}",
    }
