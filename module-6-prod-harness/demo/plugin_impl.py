"""Incident-response tools and lifecycle connections for the Hermes CLI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from components.hooks import (
    CompletionHook,
    RepeatedCallHook,
    RunTrace,
    SafetyHook,
)
from components.permissions import decide
from data import scenario, trusted_user
from incident_tools import HANDLERS, TOOL_SCHEMAS, execute_tool


PLUGIN_NAME = "incident-response-demo"
TOOLSET_NAME = PLUGIN_NAME
SKILL_NAMES = ("incident_triage", "safe_remediation")


def _json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _parsed_result(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {"status": "unknown", "raw": value}
        if isinstance(parsed, dict):
            return parsed
    return {"status": "unknown", "raw": str(value)}


class IncidentResponsePlugin:
    """Connect the cumulative incident harness to native Hermes events."""

    def __init__(
        self,
        *,
        demo_dir: Path,
        scenario_name: str,
        state_path: Path,
        trace_path: Path,
    ) -> None:
        self.demo_dir = demo_dir.resolve()
        self.scenario_name = scenario_name
        self.scenario = scenario(scenario_name)
        self.user = trusted_user(self.scenario)
        self.state_path = state_path.resolve()
        self.incident = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.trace = RunTrace(trace_path)
        self.evidence = {"health_checked": False}
        self.repeated = RepeatedCallHook()
        self.safety = SafetyHook()
        self.completion = CompletionHook()
        self._skills_recorded = False

    @classmethod
    def from_environment(cls) -> "IncidentResponsePlugin":
        required = (
            "INCIDENT_DEMO_DIR",
            "INCIDENT_DEMO_SCENARIO",
            "INCIDENT_DEMO_STATE",
            "INCIDENT_DEMO_TRACE",
        )
        missing = [name for name in required if not os.environ.get(name)]
        if missing:
            raise RuntimeError(
                "Missing incident demo environment: " + ", ".join(missing)
            )
        return cls(
            demo_dir=Path(os.environ["INCIDENT_DEMO_DIR"]),
            scenario_name=os.environ["INCIDENT_DEMO_SCENARIO"],
            state_path=Path(os.environ["INCIDENT_DEMO_STATE"]),
            trace_path=Path(os.environ["INCIDENT_DEMO_TRACE"]),
        )

    def register(self, ctx: Any) -> None:
        for name in HANDLERS:
            ctx.register_tool(
                name=name,
                toolset=TOOLSET_NAME,
                schema=TOOL_SCHEMAS[name],
                handler=self._handler(name),
            )

        skills_root = self.demo_dir / "components" / "skills"
        for name in SKILL_NAMES:
            ctx.register_skill(
                name,
                skills_root / name / "SKILL.md",
                description=TOOL_SKILL_DESCRIPTIONS[name],
            )

        ctx.register_hook("pre_llm_call", self.before_model)
        ctx.register_hook("pre_tool_call", self.before_tool)
        ctx.register_hook("post_tool_call", self.after_tool)
        ctx.register_hook("pre_verify", self.before_completion)
        self.trace.record(
            "run_started",
            scenario=self.scenario_name,
            authenticated_user=self.user,
            initial_deployment=self.incident["current_deployment"],
        )
        for name in SKILL_NAMES:
            self.trace.record(
                "skill_registered",
                skill=f"{PLUGIN_NAME}:{name}",
                source=f"components/skills/{name}/SKILL.md",
            )

    def _handler(self, tool_name: str):
        def handle(params: dict[str, Any], **_: Any) -> str:
            try:
                result = execute_tool(tool_name, params, self.incident)
                result = {"executed": True, "tool": tool_name, **result}
                self._save_state()
            except (KeyError, TypeError, ValueError) as error:
                result = {
                    "status": "tool_error",
                    "executed": False,
                    "tool": tool_name,
                    "error": str(error),
                }
            return _json(result)

        return handle

    def before_model(self, **_: Any) -> None:
        if self._skills_recorded:
            return
        self._skills_recorded = True
        self.trace.record(
            "skills_preloaded",
            skills=[f"{PLUGIN_NAME}:{name}" for name in SKILL_NAMES],
            source="hermes_cli.--skills",
        )

    def before_tool(
        self, tool_name: str, args: dict[str, Any], **_: Any
    ) -> dict[str, str] | None:
        arguments = args if isinstance(args, dict) else {}
        permission = decide(self.user, tool_name, arguments, self.incident)
        self.trace.record(
            "permission_decision",
            tool=tool_name,
            arguments=arguments,
            decision="allow" if permission.allowed else "deny",
            **permission.to_dict(),
        )
        if not permission.allowed:
            return {
                "action": "block",
                "message": _json(
                    {
                        "status": "permission_denied",
                        "executed": False,
                        "tool": tool_name,
                        **permission.to_dict(),
                    }
                ),
            }

        repeated = self.repeated.check(tool_name, arguments)
        self.trace.record(
            "hook_decision", tool=tool_name, **repeated.to_dict()
        )
        if not repeated.allowed:
            return {
                "action": "block",
                "message": _json(
                    {
                        "status": "hook_blocked",
                        "executed": False,
                        "tool": tool_name,
                        **repeated.to_dict(),
                    }
                ),
            }

        if tool_name in {"rollback_deployment", "update_incident_status"}:
            safety = self.safety.check(
                tool_name, arguments, self.incident, self.evidence
            )
            self.trace.record(
                "hook_decision", tool=tool_name, **safety.to_dict()
            )
            if not safety.allowed:
                return {
                    "action": "block",
                    "message": _json(
                        {
                            "status": "hook_blocked",
                            "executed": False,
                            "tool": tool_name,
                            **safety.to_dict(),
                        }
                    ),
                }
        return None

    def after_tool(
        self,
        tool_name: str,
        args: dict[str, Any],
        result: Any,
        **_: Any,
    ) -> None:
        parsed = _parsed_result(result)
        if (
            tool_name == "get_service_health"
            and parsed.get("executed") is True
            and parsed.get("status") == "found"
        ):
            self.evidence["health_checked"] = True
        if tool_name in {"rollback_deployment", "update_incident_status"} and parsed.get(
            "executed"
        ) is True:
            self.evidence["health_checked"] = False
        self.trace.record(
            "tool_result",
            tool=tool_name,
            arguments=args if isinstance(args, dict) else {},
            result=parsed,
        )

    def before_completion(self, **_: Any) -> dict[str, str] | None:
        decision = self.completion.check(
            self.scenario, self.incident, self.trace.events
        )
        self.trace.record("hook_decision", **decision.to_dict())
        if decision.allowed:
            self.trace.record(
                "completion",
                status="completed",
                final_deployment=self.incident["current_deployment"],
            )
            return None
        return {
            "action": "continue",
            "message": (
                "Completion was blocked. Use the registered evidence tools and "
                "attempt the exact rollback requested by the operator. Then report "
                "the authoritative permission, hook, and execution outcome."
            ),
        }

    def _save_state(self) -> None:
        self.state_path.write_text(
            json.dumps(self.incident, indent=2) + "\n", encoding="utf-8"
        )


TOOL_SKILL_DESCRIPTIONS = {
    "incident_triage": "Gather trusted incident evidence before concluding or acting.",
    "safe_remediation": "Use enforced permission and safety boundaries for mutations.",
}


def register_for_validation(ctx: Any, demo_dir: Path) -> None:
    """Declare capabilities for Hermes's environment-free plugin probe."""

    def unavailable(_params: dict[str, Any], **_: Any) -> str:
        return _json(
            {
                "status": "unavailable",
                "executed": False,
                "reason": "The capability probe does not execute demo tools.",
            }
        )

    for name in HANDLERS:
        ctx.register_tool(
            name=name,
            toolset=TOOLSET_NAME,
            schema=TOOL_SCHEMAS[name],
            handler=unavailable,
        )
    skills_root = demo_dir / "components" / "skills"
    for name in SKILL_NAMES:
        ctx.register_skill(
            name,
            skills_root / name / "SKILL.md",
            description=TOOL_SKILL_DESCRIPTIONS[name],
        )
    for event in ("pre_llm_call", "pre_tool_call", "post_tool_call", "pre_verify"):
        ctx.register_hook(event, lambda **_: None)


def register(ctx: Any) -> None:
    IncidentResponsePlugin.from_environment().register(ctx)
