"""Teaching pseudocode for a production plugin registration adapter.

This file is intentionally framework-shaped rather than directly executable.
It shows ownership and order without duplicating the complete demo plugin.
See demo/plugin_impl.py for the runnable implementation.
"""

from __future__ import annotations

from typing import Any, Callable


PLUGIN_NAME = "incident-response-demo"
MUTATIONS = {"rollback_deployment", "update_incident_status"}


class ProductionPlugin:
    """Connect domain policy to runtime-owned lifecycle events."""

    def __init__(
        self,
        *,
        tools: dict[str, Callable[..., str]],
        permission_policy: Any,
        repeated_call_hook: Any,
        safety_hook: Any,
        completion_oracle: Any,
        state: Any,
        trace: Any,
        trusted_identity: dict[str, str],
    ) -> None:
        self.tools = tools
        self.permission_policy = permission_policy
        self.repeated_call_hook = repeated_call_hook
        self.safety_hook = safety_hook
        self.completion_oracle = completion_oracle
        self.state = state
        self.trace = trace
        self.trusted_identity = trusted_identity
        self.evidence = {"health_checked": False}
        self._skills_recorded = False

    def register(self, runtime: Any) -> None:
        """Declare domain capabilities; do not implement a model loop here."""
        for name, handler in self.tools.items():
            runtime.register_tool(
                name=name,
                toolset=PLUGIN_NAME,
                schema=tool_schema(name),
                handler=handler,
            )

        runtime.register_skill("incident_triage", "skills/incident_triage/SKILL.md")
        runtime.register_skill("safe_remediation", "skills/safe_remediation/SKILL.md")

        runtime.register_hook("pre_llm_call", self.before_model)
        runtime.register_hook("pre_tool_call", self.before_tool)
        runtime.register_hook("post_tool_call", self.after_tool)
        runtime.register_hook("pre_verify", self.before_completion)

    def before_model(self, **_: Any) -> None:
        if not self._skills_recorded:
            self.trace.record("skills_preloaded")
            self._skills_recorded = True

    def before_tool(
        self, tool_name: str, args: dict[str, Any], **_: Any
    ) -> dict[str, str] | None:
        permission = self.permission_policy.decide(
            self.trusted_identity, tool_name, args, self.state
        )
        self.trace.record("permission_decision", decision=permission)
        if not permission.allowed:
            return block("permission_denied", tool_name, permission.reason)

        repeat = self.repeated_call_hook.check(tool_name, args)
        self.trace.record("hook_decision", decision=repeat)
        if not repeat.allowed:
            return block("hook_blocked", tool_name, repeat.reason)

        if tool_name in MUTATIONS:
            safety = self.safety_hook.check(
                tool_name, args, self.state, self.evidence
            )
            self.trace.record("hook_decision", decision=safety)
            if not safety.allowed:
                return block("hook_blocked", tool_name, safety.reason)

        return None  # The runtime may now dispatch the registered handler.

    def after_tool(
        self, tool_name: str, args: dict[str, Any], result: Any, **_: Any
    ) -> None:
        parsed = parse_authoritative_result(result)
        self.trace.record("tool_result", tool=tool_name, result=parsed)
        if tool_name == "get_service_health" and successful(parsed):
            self.evidence["health_checked"] = True
        if tool_name in MUTATIONS and parsed.get("executed") is True:
            self.evidence["health_checked"] = False

    def before_completion(self, **_: Any) -> dict[str, str] | None:
        decision = self.completion_oracle.check(self.state, self.trace.events)
        self.trace.record("hook_decision", decision=decision)
        if decision.allowed:
            self.trace.record("completion", status="completed")
            return None
        return {
            "action": "continue",
            "message": "Gather missing evidence and reach the requested boundary.",
        }


def block(status: str, tool: str, reason: str) -> dict[str, str]:
    """Return non-execution evidence to the runtime and model."""
    return {
        "action": "block",
        "message": repr(
            {"status": status, "executed": False, "tool": tool, "reason": reason}
        ),
    }


def tool_schema(_name: str) -> dict[str, Any]:
    raise NotImplementedError


def parse_authoritative_result(_result: Any) -> dict[str, Any]:
    raise NotImplementedError


def successful(result: dict[str, Any]) -> bool:
    return result.get("executed") is True and result.get("status") == "found"
