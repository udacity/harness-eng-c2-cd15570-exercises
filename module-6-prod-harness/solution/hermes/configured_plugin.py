"""Configured Hermes adapter used from Task 4 onward."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from hermes.components.hooks import (
    CompletionHook,
    HookResult,
    RepeatedCallHook,
    RunTrace,
    SyntaxHook,
)
from hermes.components.permissions import PermissionPolicy


PLUGIN_NAME = "xyz-api-harness"
TOOLSET_NAME = PLUGIN_NAME
FULL_TOOL_NAMES = {"read_file", "write_file", "http_get", "web_search", "run_tests"}


TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "read_file": {
        "name": "read_file",
        "description": "Read the assigned Python client file.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    "write_file": {
        "name": "write_file",
        "description": "Replace the assigned Python client file with the provided content.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
    "http_get": {
        "name": "http_get",
        "description": "Make an allowlisted local HTTP GET request and return parsed JSON.",
        "parameters": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
            "additionalProperties": False,
        },
    },
    "web_search": {
        "name": "web_search",
        "description": "Request a public web search. The harness may deny this capability.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    "run_tests": {
        "name": "run_tests",
        "description": "Run the fixed supplied test for the assigned client.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
}


def _json_result(result: dict[str, Any]) -> str:
    return json.dumps(result, sort_keys=True, default=str)


def _parsed_result(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return result
    if isinstance(result, str):
        try:
            parsed = json.loads(result)
        except json.JSONDecodeError:
            return {"status": "unknown", "raw": result}
        if isinstance(parsed, dict):
            return parsed
    return {"status": "unknown", "raw": str(result)}


def _get_json(url: str) -> dict[str, Any]:
    request = Request(url, method="GET", headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=5) as response:
            return {
                "status": "ok",
                "executed": True,
                "tool": "http_get",
                "http_status": response.status,
                "body": json.load(response),
            }
    except HTTPError as error:
        try:
            body: Any = json.load(error)
        except (json.JSONDecodeError, OSError):
            body = {"error": str(error)}
        return {
            "status": "http_error",
            "executed": True,
            "tool": "http_get",
            "http_status": error.code,
            "body": body,
        }
    except URLError as error:
        return {
            "status": "connection_error",
            "executed": True,
            "tool": "http_get",
            "error": str(error.reason),
        }


####################
# SKILL COMPONENT
# Registers and preloads the supplied XYZ API workflow skill in Hermes.
####################
class SkillConnection:
    """Make the supplied skill available through Hermes skill registration."""

    name = "xyz-api-client"
    qualified_name = f"{PLUGIN_NAME}:{name}"
    description = "Guides local API discovery and client verification."

    def __init__(self, skill_file: Path, trace: RunTrace) -> None:
        self.skill_file = skill_file.resolve()
        self.trace = trace
        self._loaded_recorded = False

    def register(self, ctx: Any) -> None:
        ctx.register_skill(
            self.name,
            self.skill_file,
            description=self.description,
        )
        ctx.register_hook("pre_llm_call", self.before_model_call)
        self.trace.record(
            "skill_registered",
            skill=self.qualified_name,
            description=self.description,
            source="hermes/components/skill/SKILL.md",
        )

    def before_model_call(self, **_: Any) -> None:
        if self._loaded_recorded:
            return
        self._loaded_recorded = True
        self.trace.record(
            "skill_loaded",
            skill=self.qualified_name,
            source="hermes_cli.--skills",
        )


####################
# PERMISSION COMPONENT
# Applies the supplied policy before tools and observes trusted tool results.
####################
class PermissionConnection:
    """Make the supplied permission policy available at Hermes tool boundaries."""

    description = "Default-deny policy for files, tests, and network destinations."

    def __init__(self, policy: PermissionPolicy, trace: RunTrace) -> None:
        self.policy = policy
        self.trace = trace

    def before_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        trace_arguments: dict[str, Any],
    ) -> dict[str, str] | None:
        decision = self.policy.decide(tool_name, arguments)
        self.trace.record(
            "permission_decision",
            requested_capability=tool_name,
            **trace_arguments,
            decision="allow" if decision.allowed else "deny",
            matching_rule=decision.rule,
            reason=decision.reason,
        )
        if decision.allowed:
            return None
        result = {
            "status": "permission_denied",
            "executed": False,
            **decision.to_dict(),
        }
        return {"action": "block", "message": _json_result(result)}

    def after_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        result: Any,
        trace_arguments: dict[str, Any],
    ) -> None:
        parsed = _parsed_result(result)
        self.policy.observe_result(tool_name, arguments, parsed)
        self.trace.record(
            "tool_result",
            tool=tool_name,
            **trace_arguments,
            result=parsed,
        )


####################
# HOOK COMPONENTS
# Attach behavior before tools, after writes, and before completion.
####################
class HookConnections:
    """Make the supplied hooks available through native Hermes hook events."""

    descriptions = {
        "repeated_call": "Runs before permitted tools and blocks repeated requests.",
        "syntax": "Runs after client writes and rejects invalid Python.",
        "completion": "Runs before completion and requires the supplied tests to pass.",
    }

    def __init__(
        self,
        *,
        repeated_call: RepeatedCallHook,
        syntax: SyntaxHook,
        completion: CompletionHook,
        client_path: Path,
        trace: RunTrace,
    ) -> None:
        self.repeated_call = repeated_call
        self.syntax = syntax
        self.completion = completion
        self.client_path = client_path.resolve()
        self.trace = trace

    def before_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, str] | None:
        repeated = self.repeated_call.before_tool(tool_name, arguments)
        self.trace.record("hook", tool=tool_name, **repeated.to_dict())
        if repeated.allowed:
            return None
        result = {
            "status": "hook_blocked",
            "executed": False,
            "tool": tool_name,
            "reason": repeated.reason,
        }
        return {"action": "block", "message": _json_result(result)}

    def after_write(
        self,
        tool_name: str,
        args: dict[str, Any],
        result: Any,
        **_: Any,
    ) -> str | None:
        del args
        parsed = _parsed_result(result)
        if tool_name != "write_file" or parsed.get("executed") is not True:
            return None
        syntax = self.syntax.after_write(self.client_path)
        self.trace.record("hook", tool=tool_name, **syntax.to_dict())
        parsed["syntax_check"] = syntax.to_dict()
        if not syntax.allowed:
            parsed["status"] = "hook_blocked"
            parsed["error"] = syntax.reason
        return _json_result(parsed)

    def check_completion(self, *, tool: str | None = None) -> HookResult:
        completion = self.completion.check(self.client_path)
        fields = {"tool": tool} if tool is not None else {}
        self.trace.record("hook", **fields, **completion.to_dict())
        return completion

    def before_completion(self, **_: Any) -> dict[str, str] | None:
        completion = self.check_completion()
        if completion.allowed:
            self.trace.record("completion", status="completed")
            return None
        compact = json.dumps(
            {
                "returncode": completion.details.get("returncode"),
                "stdout": completion.details.get("stdout"),
                "stderr": completion.details.get("stderr"),
            }
        )
        return {
            "action": "continue",
            "message": (
                "Completion was blocked because the supplied tests failed. "
                "Correct the assigned client, rerun run_tests, and only then finish. "
                f"Test evidence: {compact}"
            ),
        }


class HermesConfiguredPlugin:
    """Connect the Task 4 components to native Hermes lifecycle events."""

    def __init__(
        self,
        *,
        client_path: Path,
        trace: RunTrace,
        behavior_test: Path,
        test_result_file: Path,
    ) -> None:
        self.client_path = client_path.resolve()
        self.trace = trace

        ####################
        # CONNECT THE THREE TASK 4 COMPONENT TYPES TO HERMES
        ####################
        skill_file = Path(__file__).resolve().parent / "components" / "skill" / "SKILL.md"
        self.skill = SkillConnection(skill_file, trace)
        self.permissions = PermissionConnection(PermissionPolicy(self.client_path), trace)
        self.hooks = HookConnections(
            repeated_call=RepeatedCallHook(),
            syntax=SyntaxHook(),
            completion=CompletionHook(behavior_test, test_result_file),
            client_path=self.client_path,
            trace=trace,
        )

    @classmethod
    def from_environment(cls) -> "HermesConfiguredPlugin":
        required = [
            "XYZ_HERMES_MODE",
            "XYZ_CLIENT_PATH",
            "XYZ_TRACE_FILE",
            "XYZ_BEHAVIOR_TEST",
            "XYZ_TEST_RESULT_FILE",
        ]
        missing = [name for name in required if not os.environ.get(name)]
        if missing:
            raise RuntimeError(f"Missing Hermes exercise environment: {', '.join(missing)}")
        if os.environ["XYZ_HERMES_MODE"] != "fresh":
            raise RuntimeError("The configured plugin is available only in fresh mode.")
        return cls(
            client_path=Path(os.environ["XYZ_CLIENT_PATH"]),
            trace=RunTrace(Path(os.environ["XYZ_TRACE_FILE"])),
            behavior_test=Path(os.environ["XYZ_BEHAVIOR_TEST"]),
            test_result_file=Path(os.environ["XYZ_TEST_RESULT_FILE"]),
        )

    def register(self, ctx: Any) -> None:
        self._register_tools(ctx)

        ####################
        # CONNECT THE COMPONENTS TO THE NATIVE HERMES LOOP
        ####################
        self.skill.register(ctx)

        # PermissionConnection and the repeated-call hook run before each tool.
        ctx.register_hook("pre_tool_call", self.before_tool)

        # PermissionConnection observes each trusted result after execution.
        ctx.register_hook("post_tool_call", self.after_tool)

        # The syntax hook checks the assigned client after a successful write.
        ctx.register_hook("transform_tool_result", self.hooks.after_write)

        # The completion hook must approve the client before Hermes can finish.
        ctx.register_hook("pre_verify", self.hooks.before_completion)

        self.trace.record("run_started", mode="fresh", client_path=str(self.client_path))

    def _register_tools(self, ctx: Any) -> None:
        for name, handler in (
            ("read_file", self._read_file),
            ("write_file", self._write_file),
            ("http_get", self._http_get),
            ("web_search", self._web_search),
            ("run_tests", self._run_tests),
        ):
            ctx.register_tool(
                name=name,
                toolset=TOOLSET_NAME,
                schema=TOOL_SCHEMAS[name],
                handler=handler,
                override=name in {"read_file", "write_file", "web_search"},
            )

    def before_tool(
        self, tool_name: str, args: dict[str, Any], **_: Any
    ) -> dict[str, str] | None:
        requested_arguments = args if isinstance(args, dict) else {}
        arguments = self._normalize_tool_arguments(tool_name, requested_arguments)
        trace_arguments: dict[str, Any] = {"arguments": arguments}
        if arguments != requested_arguments:
            trace_arguments["requested_arguments"] = requested_arguments

        permission = self.permissions.before_tool(
            tool_name, arguments, trace_arguments
        )
        if permission is not None:
            return permission
        return self.hooks.before_tool(tool_name, arguments)

    def after_tool(
        self,
        tool_name: str,
        args: dict[str, Any],
        result: Any,
        **_: Any,
    ) -> None:
        requested_arguments = args if isinstance(args, dict) else {}
        arguments = self._normalize_tool_arguments(tool_name, requested_arguments)
        trace_arguments: dict[str, Any] = {"arguments": arguments}
        if arguments != requested_arguments:
            trace_arguments["requested_arguments"] = requested_arguments
        self.permissions.after_tool(
            tool_name, arguments, result, trace_arguments
        )

    def _read_file(self, params: dict[str, Any], **_: Any) -> str:
        return _json_result(
            {
                "status": "ok",
                "success": True,
                "executed": True,
                "tool": "read_file",
                "path": str(self.client_path),
                "content": self.client_path.read_text(encoding="utf-8"),
            }
        )

    def _write_file(self, params: dict[str, Any], **_: Any) -> str:
        content = params["content"]
        self.client_path.write_text(content, encoding="utf-8")
        return _json_result(
            {
                "status": "ok",
                "success": True,
                "executed": True,
                "tool": "write_file",
                "bytes_written": len(content.encode("utf-8")),
                "resolved_path": str(self.client_path),
            }
        )

    @staticmethod
    def _http_get(params: dict[str, Any], **_: Any) -> str:
        return _json_result(_get_json(str(params.get("url"))))

    @staticmethod
    def _web_search(params: dict[str, Any], **_: Any) -> str:
        del params
        return _json_result(
            {
                "status": "permission_denied",
                "executed": False,
                "tool": "web_search",
                "reason": "Public web search is disabled for this exercise.",
            }
        )

    def _run_tests(self, params: dict[str, Any], **_: Any) -> str:
        del params
        completion = self.hooks.check_completion(tool="run_tests")
        return _json_result(
            {
                "status": "passed" if completion.allowed else "failed",
                "executed": True,
                "tool": "run_tests",
                "reason": completion.reason,
                "stdout": completion.details["stdout"],
                "stderr": completion.details["stderr"],
            }
        )

    def _normalize_tool_arguments(
        self, tool: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        normalized = dict(arguments)
        if tool not in {"read_file", "write_file"}:
            return normalized
        requested = normalized.get("path")
        if not isinstance(requested, str):
            return normalized

        requested_path = Path(requested).expanduser()
        if requested_path.is_absolute():
            candidates = [requested_path]
        else:
            roots = {Path.cwd().resolve(), self.client_path.parent}
            roots.update(list(self.client_path.parents)[2:4])
            candidates = [root / requested_path for root in roots]

        for candidate in candidates:
            try:
                if candidate.resolve() == self.client_path:
                    normalized["path"] = str(self.client_path)
                    break
            except (OSError, RuntimeError):
                continue
        return normalized


def register(ctx: Any) -> None:
    """Hermes plugin entry point for the configured Task 4 adapter."""

    HermesConfiguredPlugin.from_environment().register(ctx)
