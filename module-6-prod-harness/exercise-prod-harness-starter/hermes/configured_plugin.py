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
# STUDENT TASK: COMPONENT CONNECTIONS
#
# Implement these three adapters. The component behavior itself is supplied
# under hermes/components/; this file only makes it available to Hermes.
####################
class SkillConnection:
    """TODO: Register and preload the supplied skill through Hermes."""

    # TODO: Add the skill name, qualified name, description, and source.

    def __init__(self, skill_file: Path, trace: RunTrace) -> None:
        # TODO: Retain the supplied skill path and trace, and track whether the
        # preload has already been recorded.
        raise NotImplementedError("Connect the supplied skill to Hermes")

    def register(self, ctx: Any) -> None:
        """TODO: Register the skill and its pre_llm_call preload hook."""

        raise NotImplementedError("Register the supplied skill with Hermes")

    def before_model_call(self, **_: Any) -> None:
        """TODO: Record skill_loaded exactly once."""

        raise NotImplementedError("Record the Hermes skill preload")


class PermissionConnection:
    """TODO: Apply the supplied permission policy at Hermes tool boundaries."""

    def __init__(self, policy: PermissionPolicy, trace: RunTrace) -> None:
        # TODO: Retain the supplied policy and trace.
        raise NotImplementedError("Connect the supplied permission policy")

    def before_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        trace_arguments: dict[str, Any],
    ) -> dict[str, str] | None:
        """TODO: Trace the decision and block denied operations."""

        raise NotImplementedError("Run permissions before Hermes tool execution")

    def after_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        result: Any,
        trace_arguments: dict[str, Any],
    ) -> None:
        """TODO: Observe and trace trusted tool results."""

        raise NotImplementedError("Return trusted Hermes results to the policy")


class HookConnections:
    """TODO: Attach the supplied hooks to native Hermes lifecycle events."""

    # TODO: Describe the repeated-call, syntax, and completion hooks.
    descriptions: dict[str, str] = {}

    def __init__(
        self,
        *,
        repeated_call: RepeatedCallHook,
        syntax: SyntaxHook,
        completion: CompletionHook,
        client_path: Path,
        trace: RunTrace,
    ) -> None:
        # TODO: Retain the supplied hooks, assigned client path, and trace.
        raise NotImplementedError("Connect the supplied lifecycle hooks")

    def before_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, str] | None:
        """TODO: Run repeated-call protection before execution."""

        raise NotImplementedError("Run the repeated-call hook in Hermes")

    def after_write(
        self,
        tool_name: str,
        args: dict[str, Any],
        result: Any,
        **_: Any,
    ) -> str | None:
        """TODO: Transform write results with the syntax-hook outcome."""

        raise NotImplementedError("Run the syntax hook after Hermes writes")

    def check_completion(self, *, tool: str | None = None) -> HookResult:
        """TODO: Run and trace the fixed behavioral completion test."""

        raise NotImplementedError("Run the Hermes completion test")

    def before_completion(self, **_: Any) -> dict[str, str] | None:
        """TODO: Block final verification until the completion test passes."""

        raise NotImplementedError("Guard Hermes final verification")


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
        # TODO: CONNECT THE THREE COMPONENT TYPES TO HERMES
        ####################
        # Construct and expose:
        #   self.skill = SkillConnection(...)
        #   self.permissions = PermissionConnection(...)
        #   self.hooks = HookConnections(...)
        #
        # Use the supplied skill file, policy, hooks, behavior test, result
        # path, client path, and trace. Do not reimplement component behavior.
        self.skill: SkillConnection | None = None
        self.permissions: PermissionConnection | None = None
        self.hooks: HookConnections | None = None

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
        # The five scoped tool implementations are supplied.
        self._register_tools(ctx)

        ####################
        # TODO: CONNECT COMPONENTS TO NATIVE HERMES LIFECYCLE EVENTS
        ####################
        # Register the skill, pre_tool_call, post_tool_call,
        # transform_tool_result, and pre_verify integrations described in the
        # README. Record run_started only after registration succeeds.
        raise NotImplementedError("Register the supplied components with Hermes")

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
        """TODO: Normalize arguments, enforce permission, then run the hook."""

        raise NotImplementedError("Connect the Hermes pre_tool_call pipeline")

    def after_tool(
        self,
        tool_name: str,
        args: dict[str, Any],
        result: Any,
        **_: Any,
    ) -> None:
        """TODO: Normalize arguments and pass trusted results to permissions."""

        raise NotImplementedError("Connect the Hermes post_tool_call pipeline")

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
