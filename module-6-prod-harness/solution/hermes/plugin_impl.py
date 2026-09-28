"""Hermes plugin that connects the exercise tools, skill, hooks, and policy."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from hermes.components.hooks import CompletionHook, RepeatedCallHook, RunTrace, SyntaxHook
from hermes.components.permissions import PermissionPolicy


PLUGIN_NAME = "xyz-api-harness"
TOOLSET_NAME = PLUGIN_NAME
FULL_TOOL_NAMES = {"read_file", "write_file", "http_get", "web_search", "run_tests"}


def get_json(url: str) -> dict[str, Any]:
    """Execute one JSON GET request for an already-authorized local URL."""

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
        "description": "Run the fixed supplied behavioral tests for the assigned client.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
}


class HermesHarnessPlugin:
    """Stateful native Hermes integration for one CLI process."""

    def __init__(
        self,
        *,
        mode: str,
        client_path: Path,
        trace: RunTrace,
        behavior_test: Path | None = None,
        test_result_file: Path | None = None,
    ) -> None:
        self.mode = mode
        self.client_path = client_path.resolve()
        self.trace = trace
        self._baseline_step = 0
        self._skill_loaded_recorded = False
        self.policy = PermissionPolicy(self.client_path)
        self.repeated_call_hook = RepeatedCallHook()
        self.syntax_hook = SyntaxHook()
        self.completion_hook = (
            CompletionHook(behavior_test, test_result_file)
            if behavior_test is not None and test_result_file is not None
            else None
        )

    @classmethod
    def from_environment(cls) -> "HermesHarnessPlugin":
        required = ["XYZ_HERMES_MODE", "XYZ_CLIENT_PATH", "XYZ_TRACE_FILE"]
        missing = [name for name in required if not os.environ.get(name)]
        if missing:
            raise RuntimeError(f"Missing Hermes exercise environment: {', '.join(missing)}")
        behavior = os.environ.get("XYZ_BEHAVIOR_TEST")
        result = os.environ.get("XYZ_TEST_RESULT_FILE")
        return cls(
            mode=os.environ["XYZ_HERMES_MODE"],
            client_path=Path(os.environ["XYZ_CLIENT_PATH"]),
            trace=RunTrace(Path(os.environ["XYZ_TRACE_FILE"])),
            behavior_test=Path(behavior) if behavior else None,
            test_result_file=Path(result) if result else None,
        )

    def register(self, ctx: Any) -> None:
        if self.mode == "smoke":
            self.trace.record("run_started", mode="smoke", client_path=str(self.client_path))
            self._register_tool(ctx, "read_file", self._read_file, override=True)
            self._register_tool(ctx, "http_get", self._http_get)
            return

        if self.mode != "fresh" or self.completion_hook is None:
            raise RuntimeError(f"Unsupported or incomplete Hermes exercise mode: {self.mode}")

        for name, handler in (
            ("read_file", self._read_file),
            ("write_file", self._write_file),
            ("http_get", self._http_get),
            ("web_search", self._web_search),
            ("run_tests", self._run_tests),
        ):
            self._register_tool(
                ctx,
                name,
                handler,
                override=name in {"read_file", "write_file", "web_search"},
            )

        skill_file = Path(__file__).resolve().parent / "components" / "skill" / "SKILL.md"
        ctx.register_skill(
            "xyz-api-client",
            skill_file,
            description="Discover the local XYZ API contract and implement its client.",
        )
        ctx.register_hook("pre_tool_call", self.before_tool)
        ctx.register_hook("post_tool_call", self.after_tool)
        ctx.register_hook("transform_tool_result", self.after_write)
        ctx.register_hook("pre_verify", self.before_completion)
        self.trace.record(
            "skill_registered",
            skill="xyz-api-harness:xyz-api-client",
            source="hermes/components/skill/SKILL.md",
        )
        ctx.register_hook("pre_llm_call", self.before_model_call)
        self.trace.record("run_started", mode="fresh", client_path=str(self.client_path))

    @staticmethod
    def _json_result(result: dict[str, Any]) -> str:
        return json.dumps(result, sort_keys=True, default=str)

    @staticmethod
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

    def _register_tool(
        self, ctx: Any, name: str, handler: Callable[..., str], *, override: bool = False
    ) -> None:
        ctx.register_tool(
            name=name,
            toolset=TOOLSET_NAME,
            schema=TOOL_SCHEMAS[name],
            handler=handler,
            override=override,
        )

    def before_tool(
        self, tool_name: str, args: dict[str, Any], **_: Any
    ) -> dict[str, str] | None:
        arguments = args if isinstance(args, dict) else {}
        decision = self.policy.decide(tool_name, arguments)
        self.trace.record(
            "permission_decision",
            requested_capability=tool_name,
            arguments=arguments,
            decision="allow" if decision.allowed else "deny",
            matching_rule=decision.rule,
            reason=decision.reason,
        )
        if not decision.allowed:
            result = {
                "status": "permission_denied",
                "executed": False,
                **decision.to_dict(),
            }
            return {"action": "block", "message": self._json_result(result)}

        repeated = self.repeated_call_hook.before_tool(tool_name, arguments)
        self.trace.record("hook", tool=tool_name, **repeated.to_dict())
        if not repeated.allowed:
            result = {
                "status": "hook_blocked",
                "executed": False,
                "tool": tool_name,
                "reason": repeated.reason,
            }
            return {"action": "block", "message": self._json_result(result)}
        return None

    def after_tool(
        self,
        tool_name: str,
        args: dict[str, Any],
        result: Any,
        **_: Any,
    ) -> None:
        arguments = args if isinstance(args, dict) else {}
        parsed = self._parsed_result(result)
        self.policy.observe_result(tool_name, arguments, parsed)
        self.trace.record(
            "tool_result", tool=tool_name, arguments=arguments, result=parsed
        )

    def after_write(
        self,
        tool_name: str,
        args: dict[str, Any],
        result: Any,
        **_: Any,
    ) -> str | None:
        del args
        parsed = self._parsed_result(result)
        if tool_name != "write_file" or parsed.get("executed") is not True:
            return None
        syntax = self.syntax_hook.after_write(self.client_path)
        self.trace.record("hook", tool=tool_name, **syntax.to_dict())
        parsed["syntax_check"] = syntax.to_dict()
        if not syntax.allowed:
            parsed["status"] = "hook_blocked"
            parsed["error"] = syntax.reason
        return self._json_result(parsed)

    def before_completion(self, **_: Any) -> dict[str, str] | None:
        if self.completion_hook is None:
            return None
        completion = self.completion_hook.check(self.client_path)
        self.trace.record("hook", **completion.to_dict())
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
                "Completion was blocked because the supplied behavioral tests failed. "
                "Correct the assigned client, rerun run_tests, and only then finish. "
                f"Test evidence: {compact}"
            ),
        }

    def before_model_call(self, **_: Any) -> None:
        """Record the native ``--skills`` preload at the first model boundary."""

        if self._skill_loaded_recorded:
            return
        self._skill_loaded_recorded = True
        self.trace.record(
            "skill_loaded",
            skill="xyz-api-harness:xyz-api-client",
            source="hermes_cli.--skills",
        )

    def _read_file(self, params: dict[str, Any], **_: Any) -> str:
        if self.mode == "smoke":
            if self._baseline_step != 0 or not self._requested_client(params.get("path")):
                return self._baseline_rejection("read_file", {"path": str(self.client_path)})
        result = {
            "status": "ok",
            "success": True,
            "executed": True,
            "tool": "read_file",
            "path": str(self.client_path),
            "content": self.client_path.read_text(encoding="utf-8"),
        }
        if self.mode == "smoke":
            self._record_baseline_operation("read_incomplete_client")
        return self._json_result(result)

    def _write_file(self, params: dict[str, Any], **_: Any) -> str:
        content = params["content"]
        self.client_path.write_text(content, encoding="utf-8")
        return self._json_result(
            {
                "status": "ok",
                "success": True,
                "executed": True,
                "tool": "write_file",
                "bytes_written": len(content.encode("utf-8")),
                "resolved_path": str(self.client_path),
            }
        )

    def _http_get(self, params: dict[str, Any], **_: Any) -> str:
        url = params.get("url")
        if self.mode == "smoke":
            expected = (
                PermissionPolicy.HEALTH_URL
                if self._baseline_step == 1
                else PermissionPolicy.DOCS_URL if self._baseline_step == 2 else None
            )
            if url != expected:
                return self._baseline_rejection("http_get", {"url": expected})
        result = get_json(str(url))
        if self.mode == "smoke" and result.get("status") == "ok":
            operation = "check_api_health" if self._baseline_step == 1 else "retrieve_api_docs"
            self._record_baseline_operation(operation)
        return self._json_result(result)

    def _web_search(self, params: dict[str, Any], **_: Any) -> str:
        del params
        return self._json_result(
            {
                "status": "permission_denied",
                "executed": False,
                "tool": "web_search",
                "reason": "Public web search is disabled for this exercise.",
            }
        )

    def _run_tests(self, params: dict[str, Any], **_: Any) -> str:
        del params
        if self.completion_hook is None:
            raise RuntimeError("Completion hook is not configured.")
        completion = self.completion_hook.check(self.client_path)
        self.trace.record("hook", tool="run_tests", **completion.to_dict())
        return self._json_result(
            {
                "status": "passed" if completion.allowed else "failed",
                "executed": True,
                "tool": "run_tests",
                "reason": completion.reason,
                "stdout": completion.details["stdout"],
                "stderr": completion.details["stderr"],
            }
        )

    def _requested_client(self, requested: Any) -> bool:
        return isinstance(requested, str) and Path(requested).expanduser().resolve() == self.client_path

    def _baseline_rejection(self, tool: str, expected: dict[str, Any]) -> str:
        return self._json_result(
            {
                "status": "rejected",
                "executed": False,
                "tool": tool,
                "expected_arguments": expected,
                "message": "Call the requested read-only tool with the exact target and in order.",
            }
        )

    def _record_baseline_operation(self, operation: str) -> None:
        self._baseline_step += 1
        self.trace.record("baseline_operation", operation=operation, accepted=True)


def register(ctx: Any) -> None:
    """Hermes plugin entry point."""

    HermesHarnessPlugin.from_environment().register(ctx)
