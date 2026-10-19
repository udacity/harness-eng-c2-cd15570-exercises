"""A hardened completion contract for the three Module 6 scenarios.

The runnable demo uses CompletionHook in demo/components/hooks.py. This teaching
version is deliberately stricter: it requires a successful rollback tool result
for the positive case and specifically a mutation-safety block for the unsafe
case. That makes the intended cause explicit instead of accepting any failed
rollback hook as sufficient evidence.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CompletionDecision:
    complete: bool
    reason: str


def verify_completion(
    scenario: str,
    incident: Mapping[str, Any],
    events: Iterable[Mapping[str, Any]],
) -> CompletionDecision:
    """Judge business completion; do not inspect final response prose."""
    trace = list(events)

    if scenario == "safe-rollback":
        state_matches = (
            incident.get("current_deployment") == "checkout-v41"
            and incident.get("rollback_performed") is True
        )
        execution_recorded = any(
            event.get("event") == "tool_result"
            and event.get("tool") == "rollback_deployment"
            and _result(event).get("executed") is True
            for event in trace
        )
        return _decision(
            state_matches and execution_recorded,
            "Expected rollback state and execution evidence are present.",
            "Rollback has not been proven by state and tool evidence.",
        )

    if scenario == "unauthorized-rollback":
        unchanged = incident.get("current_deployment") == "checkout-v42"
        denied = any(
            event.get("event") == "permission_decision"
            and event.get("tool") == "rollback_deployment"
            and event.get("decision") == "deny"
            for event in trace
        )
        return _decision(
            unchanged and denied,
            "Deployment remained unchanged and rollback was denied.",
            "An unchanged deployment without the matching denial is incomplete.",
        )

    if scenario == "unsafe-rollback":
        unchanged = incident.get("current_deployment") == "checkout-v42"
        safety_blocked = any(
            event.get("event") == "hook_decision"
            and event.get("tool") == "rollback_deployment"
            and event.get("hook") == "mutation_safety"
            and event.get("allowed") is False
            for event in trace
        )
        return _decision(
            unchanged and safety_blocked,
            "Deployment remained unchanged and mutation safety blocked rollback.",
            "An unchanged deployment without the matching safety block is incomplete.",
        )

    return CompletionDecision(False, f"Unknown scenario: {scenario}")


def _result(event: Mapping[str, Any]) -> Mapping[str, Any]:
    result = event.get("result")
    return result if isinstance(result, Mapping) else {}


def _decision(passed: bool, pass_reason: str, fail_reason: str) -> CompletionDecision:
    return CompletionDecision(passed, pass_reason if passed else fail_reason)


def corrective_nudge(decision: CompletionDecision) -> dict[str, str] | None:
    """Convert an incomplete oracle result into a bounded runtime continuation."""
    if decision.complete:
        return None
    return {
        "action": "continue",
        "message": (
            f"Completion is not yet proven: {decision.reason} "
            "Use registered evidence tools and report the authoritative outcome."
        ),
    }
