"""Deterministic Hermes lifecycle hooks and structured trace evidence."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


MUTATION_TOOLS = {"rollback_deployment", "update_incident_status"}


@dataclass(frozen=True, slots=True)
class HookDecision:
    hook: str
    allowed: bool
    reason: str
    codes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["codes"] = list(self.codes)
        return value


class RepeatedCallHook:
    def __init__(self, allowed_repeats: int = 5) -> None:
        self.allowed_repeats = allowed_repeats
        self._counts: dict[str, int] = {}

    def check(self, tool: str, arguments: dict[str, Any]) -> HookDecision:
        normalized = json.dumps(
            {"tool": tool, "arguments": arguments},
            sort_keys=True,
            separators=(",", ":"),
        )
        fingerprint = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        count = self._counts.get(fingerprint, 0) + 1
        self._counts[fingerprint] = count
        allowed = count <= self.allowed_repeats
        return HookDecision(
            "repeated_call",
            allowed,
            (
                f"Equivalent call {count} of {self.allowed_repeats} allowed."
                if allowed
                else "Equivalent call limit exceeded."
            ),
            () if allowed else ("repeated_call_limit",),
        )


class SafetyHook:
    def check(
        self,
        tool: str,
        arguments: dict[str, Any],
        incident: dict[str, Any],
        evidence: dict[str, bool],
    ) -> HookDecision:
        if tool not in MUTATION_TOOLS:
            return HookDecision("mutation_safety", True, "Not a mutation.")
        codes: list[str] = []
        reasons: list[str] = []
        if evidence.get("health_checked") is not True:
            codes.append("missing_fresh_health")
            reasons.append("Fresh service-health evidence is required.")
        if tool == "rollback_deployment":
            target = arguments.get("target_version")
            matching = [
                deployment
                for deployment in incident["deployment_history"]
                if deployment.get("version") == target
            ]
            if not matching:
                codes.append("rollback_target_missing")
                reasons.append("The rollback target is absent from deployment history.")
            elif matching[0].get("last_known_good") is not True:
                codes.append("rollback_target_not_last_known_good")
                reasons.append("The rollback target is not last-known-good.")
        if (
            tool == "update_incident_status"
            and arguments.get("status") == "RESOLVED"
            and not (
                incident.get("service_health") == "HEALTHY"
                and incident.get("recovery_confirmed") is True
            )
        ):
            codes.append("premature_resolution")
            reasons.append("Recovery is not confirmed.")
        return HookDecision(
            "mutation_safety",
            not codes,
            "All deterministic mutation checks passed."
            if not codes
            else " ".join(reasons),
            tuple(codes),
        )


class CompletionHook:
    def check(
        self,
        scenario: dict[str, Any],
        incident: dict[str, Any],
        events: list[dict[str, Any]],
    ) -> HookDecision:
        target = scenario["target_version"]
        expected = scenario["expected_boundary"]
        if expected == "executed":
            passed = (
                incident.get("current_deployment") == target
                and incident.get("rollback_performed") is True
            )
        elif expected == "permission_denied":
            passed = incident.get("current_deployment") == "checkout-v42" and any(
                event.get("event") == "permission_decision"
                and event.get("tool") == "rollback_deployment"
                and event.get("decision") == "deny"
                for event in events
            )
        elif expected == "hook_blocked":
            passed = incident.get("current_deployment") == "checkout-v42" and any(
                event.get("event") == "hook_decision"
                and event.get("tool") == "rollback_deployment"
                and event.get("allowed") is False
                for event in events
            )
        else:
            passed = False
        return HookDecision(
            "completion_verification",
            passed,
            (
                "The scenario's authoritative outcome is present."
                if passed
                else "The requested rollback has not reached its expected boundary outcome."
            ),
            () if passed else ("scenario_incomplete",),
        )


class RunTrace:
    def __init__(self, path: Path) -> None:
        self.path = path.resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.events: list[dict[str, Any]] = []

    def record(self, event: str, **fields: Any) -> dict[str, Any]:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "harness": "hermes",
            "event": event,
            **fields,
        }
        self.events.append(entry)
        with self.path.open("a", encoding="utf-8") as target:
            target.write(json.dumps(entry, sort_keys=True, default=str) + "\n")
        return entry

