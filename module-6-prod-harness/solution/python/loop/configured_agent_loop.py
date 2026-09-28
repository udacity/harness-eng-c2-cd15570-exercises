"""Configured copy of the hand-built Python loop used from Task 3 onward."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..components.hooks import CompletionHook, HookResult, RepeatedCallHook, SyntaxHook
from ..components.permissions import PermissionDecision, PermissionPolicy


MAX_CYCLES = 24

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "read_file",
        "description": (
            "Read the assigned Python client file. Use the assigned path from the task; "
            "the harness safely normalizes equivalent relative forms."
        ),
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "write_file",
        "description": (
            "Replace the assigned Python client file with the provided content. Use the "
            "assigned path from the task; the harness safely normalizes equivalent relative "
            "forms."
        ),
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
    {
        "type": "function",
        "name": "http_get",
        "description": "Make an allowlisted local HTTP GET request and return parsed JSON.",
        "parameters": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "web_search",
        "description": "Request a public web search. The harness may deny this capability.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "run_tests",
        "description": "Run the fixed supplied behavioral tests for the assigned client.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
]


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


class RunTrace:
    """Append structured harness evidence to a JSONL file."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path.resolve() if path is not None else None
        self.events: list[dict[str, Any]] = []
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: str, **fields: Any) -> dict[str, Any]:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "harness": "python",
            "event": event,
            **fields,
        }
        self.events.append(entry)
        if self.path is not None:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, sort_keys=True, default=str) + "\n")
        return entry


####################
# SKILL COMPONENT
# Adds the supplied workflow instructions to the model context.
####################
class SkillConnection:
    """Make one supplied skill available in the model context."""

    name = "xyz-api-client"
    description = "Guides the agent through local API discovery and client verification."
    source = "python/components/skill/SKILL.md"

    def __init__(self, instructions: str, trace: RunTrace) -> None:
        self.instructions = instructions
        self.trace = trace

    def add_to_context(self, base_instructions: str) -> str:
        self.trace.record(
            "skill_loaded",
            skill=self.name,
            description=self.description,
            source=self.source,
        )
        return f"{base_instructions}\n\nSUPPLIED SKILL\n{self.instructions}"


####################
# PERMISSION COMPONENT
# Controls which requested tool operations the loop may execute.
####################
class PermissionConnection:
    """Make the supplied permission policy available before every tool call."""

    description = "Default-deny policy for files, tests, and network destinations."

    def __init__(self, policy: PermissionPolicy, trace: RunTrace) -> None:
        self.policy = policy
        self.trace = trace

    def before_tool(
        self,
        tool: str,
        arguments: dict[str, Any],
        trace_arguments: dict[str, Any],
    ) -> PermissionDecision:
        decision = self.policy.decide(tool, arguments)
        self.trace.record(
            "permission_decision",
            requested_capability=tool,
            **trace_arguments,
            decision="allow" if decision.allowed else "deny",
            matching_rule=decision.rule,
            reason=decision.reason,
        )
        print(f"PERMISSION: {'ALLOWED' if decision.allowed else 'DENIED'}")
        print(f"Rule:       {decision.rule}")
        print(f"Reason:     {decision.reason}")
        return decision

    def after_tool(
        self, tool: str, arguments: dict[str, Any], result: dict[str, Any]
    ) -> None:
        self.policy.observe_result(tool, arguments, result)


####################
# HOOK COMPONENTS
# Attach behavior before tools, after writes, and before completion.
####################
class HookConnections:
    """Make the supplied lifecycle hooks available at loop boundaries."""

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
        self.client_path = client_path
        self.trace = trace

    def before_tool(self, tool: str, arguments: dict[str, Any]) -> HookResult:
        result = self.repeated_call.before_tool(tool, arguments)
        self.trace.record("hook", tool=tool, **result.to_dict())
        print(f"REPEATED-CALL HOOK: {'ALLOWED' if result.allowed else 'BLOCKED'}")
        return result

    def after_write(self, tool: str, result: dict[str, Any]) -> dict[str, Any]:
        if tool != "write_file" or result.get("executed") is not True:
            return result

        syntax = self.syntax.after_write(self.client_path)
        self.trace.record("hook", tool=tool, **syntax.to_dict())
        result["syntax_check"] = syntax.to_dict()
        print(f"SYNTAX HOOK: {'PASSED' if syntax.allowed else 'BLOCKED'}")
        if not syntax.allowed:
            result["status"] = "hook_blocked"
        return result

    def before_completion(
        self, *, cycle: int | None = None, tool: str | None = None
    ) -> HookResult:
        result = self.completion.check(self.client_path)
        trace_fields: dict[str, Any] = {}
        if cycle is not None:
            trace_fields["cycle"] = cycle
        if tool is not None:
            trace_fields["tool"] = tool
        self.trace.record("hook", **trace_fields, **result.to_dict())
        return result


class HandBuiltAgentLoop:
    """Call a model, authorize its tool proposals, and enforce lifecycle hooks."""

    def __init__(
        self,
        *,
        client: Any,
        model: str,
        client_path: Path,
        skill_text: str,
        permission_policy: PermissionPolicy,
        repeated_call_hook: RepeatedCallHook,
        syntax_hook: SyntaxHook,
        completion_hook: CompletionHook,
        trace: RunTrace,
        max_cycles: int = MAX_CYCLES,
    ) -> None:
        self.client = client
        self.model = model
        self.client_path = client_path.resolve()
        self.max_cycles = max_cycles
        self.trace = trace

        ####################
        # CONNECT THE THREE TASK 3 COMPONENT TYPES TO THE LOOP
        ####################
        self.skill = SkillConnection(skill_text, trace)
        self.permissions = PermissionConnection(permission_policy, trace)
        self.hooks = HookConnections(
            repeated_call=repeated_call_hook,
            syntax=syntax_hook,
            completion=completion_hook,
            client_path=self.client_path,
            trace=trace,
        )

    ####################
    # AGENT LOOP
    ####################
    def run(self, task: str) -> dict[str, Any]:
        base_instructions = (
            "You are a coding agent operating inside a restricted hand-built harness. "
            "Tool requests are proposals; trust each returned permission decision. "
            "Do not claim a file change or test result unless its tool result confirms it."
        )

        # The skill becomes available to the model here.
        instructions = self.skill.add_to_context(base_instructions)
        model_input: Any = (
            f"ASSIGNED CLIENT FILE\n{self.client_path}\n\nTASK\n{task}"
        )
        previous_response_id: str | None = None
        responses: list[Any] = []
        tool_events: list[dict[str, Any]] = []
        model_seconds = 0.0

        self.trace.record(
            "run_started", client_path=str(self.client_path), model=self.model
        )
        print("\n==================================================")
        print("HAND-BUILT PYTHON LOOP — XYZ API CLIENT TASK")
        print("==================================================")
        print(f"Model:       {self.model}")
        print(f"Client file: {self.client_path}")

        for cycle in range(1, self.max_cycles + 1):
            print(f"\n--- PYTHON HARNESS CYCLE {cycle} ---")
            self.trace.record("model_call", cycle=cycle)
            started = perf_counter()
            kwargs: dict[str, Any] = {
                "model": self.model,
                "instructions": instructions,
                "input": model_input,
                "tools": TOOL_DEFINITIONS,
                "parallel_tool_calls": False,
            }
            if previous_response_id is not None:
                kwargs["previous_response_id"] = previous_response_id
            response = self.client.responses.create(**kwargs)
            model_seconds += perf_counter() - started
            responses.append(response)

            calls = [item for item in response.output if item.type == "function_call"]
            response_text = response.output_text.strip()
            if response_text:
                print("AGENT TEXT:")
                print(response_text)
            if calls:
                outputs = []
                for item in calls:
                    event, output = self._handle_tool_call(item)
                    tool_events.append(event)
                    outputs.append(output)
                model_input = outputs
                previous_response_id = response.id
                continue

            if response_text:
                # The completion hook becomes available to the loop here.
                completion = self.hooks.before_completion(cycle=cycle)
                print(f"COMPLETION HOOK: {'PASSED' if completion.allowed else 'BLOCKED'}")
                print(f"Reason: {completion.reason}")
                if completion.allowed:
                    self.trace.record("completion", status="completed", cycle=cycle)
                    print("\n================ EXECUTION SUMMARY ================")
                    print(f"Model cycles: {cycle}")
                    print(f"Tool calls:   {len(tool_events)}")
                    print("Status:       COMPLETED")
                    return self._result(
                        "completed",
                        response_text,
                        responses,
                        tool_events,
                        model_seconds,
                    )
                model_input = (
                    "Completion was blocked because the supplied behavioral tests failed. "
                    "Use the test output below, correct the assigned client, rerun the tests, "
                    "and only then finish.\n\n"
                    + self._compact_hook_output(completion.details)
                )
                previous_response_id = response.id
                continue

            model_input = "Continue the task by calling a tool or provide a final answer."
            previous_response_id = response.id

        self.trace.record("completion", status="max_cycles", cycles=self.max_cycles)
        return self._result(
            "max_cycles", "", responses, tool_events, model_seconds
        )

    ####################
    # TOOL REQUEST PIPELINE
    # Permission -> repeated-call hook -> tool -> syntax hook -> trace
    ####################
    def _handle_tool_call(self, item: Any) -> tuple[dict[str, Any], dict[str, Any]]:
        tool = getattr(item, "name", "(unknown)")
        call_id = getattr(item, "call_id", "missing-call-id")
        print(f"AGENT REQUESTED TOOL: {tool}")
        try:
            requested_arguments = json.loads(item.arguments)
            if not isinstance(requested_arguments, dict):
                raise ValueError("Tool arguments must be a JSON object.")
        except (AttributeError, TypeError, ValueError, json.JSONDecodeError) as error:
            result = {
                "status": "tool_error",
                "executed": False,
                "tool": tool,
                "message": f"Invalid tool arguments: {error}",
            }
            event = {"tool": tool, "arguments": None, "result": result}
            self.trace.record("tool_result", **event)
            print(f"TOOL ERROR: {result['message']}")
            return event, self._tool_output(call_id, result)

        print("TOOL ARGUMENTS:")
        print(json.dumps(requested_arguments, indent=2))

        arguments = self._normalize_tool_arguments(tool, requested_arguments)
        if arguments != requested_arguments:
            print("NORMALIZED TOOL ARGUMENTS:")
            print(json.dumps(arguments, indent=2))

        trace_arguments: dict[str, Any] = {"arguments": arguments}
        if arguments != requested_arguments:
            trace_arguments["requested_arguments"] = requested_arguments

        # Permissions become available to the loop here, before execution.
        decision = self.permissions.before_tool(tool, arguments, trace_arguments)
        if not decision.allowed:
            result = {
                "status": "permission_denied",
                "executed": False,
                **decision.to_dict(),
            }
            event = {"tool": tool, **trace_arguments, "result": result}
            self.trace.record("tool_result", **event)
            print("TOOL EXECUTED: NO")
            return event, self._tool_output(call_id, result)

        # The before-tool hook becomes available after permission is granted.
        repeated = self.hooks.before_tool(tool, arguments)
        if not repeated.allowed:
            result = {
                "status": "hook_blocked",
                "executed": False,
                "tool": tool,
                "reason": repeated.reason,
            }
            event = {"tool": tool, **trace_arguments, "result": result}
            self.trace.record("tool_result", **event)
            print("TOOL EXECUTED: NO")
            return event, self._tool_output(call_id, result)

        try:
            result = self._execute_tool(tool, arguments)
        except (OSError, ValueError, TimeoutError) as error:
            result = {
                "status": "tool_error",
                "executed": False,
                "tool": tool,
                "message": str(error),
            }

        self.permissions.after_tool(tool, arguments, result)

        # The after-write hook becomes available after tool execution.
        result = self.hooks.after_write(tool, result)

        event = {"tool": tool, **trace_arguments, "result": result}
        self.trace.record("tool_result", **event)
        print(f"TOOL EXECUTED: {'YES' if result.get('executed') else 'NO'}")
        print(f"TOOL STATUS:   {result.get('status', 'unknown')}")
        return event, self._tool_output(call_id, result)

    ####################
    # EXISTING TOOL IMPLEMENTATIONS
    ####################
    def _execute_tool(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if tool == "read_file":
            return {
                "status": "ok",
                "executed": True,
                "tool": tool,
                "content": self.client_path.read_text(encoding="utf-8"),
            }
        if tool == "write_file":
            content = arguments["content"]
            self.client_path.write_text(content, encoding="utf-8")
            return {
                "status": "ok",
                "executed": True,
                "tool": tool,
                "bytes_written": len(content.encode("utf-8")),
            }
        if tool == "http_get":
            return self._http_get(arguments["url"])
        if tool == "run_tests":
            completion = self.hooks.before_completion(tool=tool)
            return {
                "status": "passed" if completion.allowed else "failed",
                "executed": True,
                "tool": tool,
                "reason": completion.reason,
                "stdout": completion.details["stdout"],
                "stderr": completion.details["stderr"],
            }
        raise ValueError(f"Unsupported tool: {tool}")

    def _normalize_tool_arguments(
        self, tool: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Canonicalize safe aliases for the one file this loop can access."""

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
            # Resolve the relative aliases a model is likely to use.
            roots = {Path.cwd().resolve(), self.client_path.parent}
            roots.update(list(self.client_path.parents)[2:4])
            candidates = [root / requested_path for root in roots]

        targets_assigned_client = False
        for candidate in candidates:
            try:
                if candidate.resolve() == self.client_path:
                    targets_assigned_client = True
                    break
            except (OSError, RuntimeError):
                continue

        if targets_assigned_client:
            normalized["path"] = str(self.client_path)
        return normalized

    @staticmethod
    def _http_get(url: str) -> dict[str, Any]:
        return get_json(url)

    @staticmethod
    def _tool_output(call_id: str, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "function_call_output",
            "call_id": call_id,
            "output": json.dumps(result, default=str),
        }

    @staticmethod
    def _compact_hook_output(details: dict[str, Any]) -> str:
        return json.dumps(
            {
                "returncode": details.get("returncode"),
                "stdout": details.get("stdout"),
                "stderr": details.get("stderr"),
            }
        )

    @staticmethod
    def _token_totals(responses: list[Any]) -> tuple[int | None, int | None]:
        input_total = 0
        output_total = 0
        for response in responses:
            usage = getattr(response, "usage", None)
            input_tokens = getattr(usage, "input_tokens", None)
            output_tokens = getattr(usage, "output_tokens", None)
            if input_tokens is None or output_tokens is None:
                return None, None
            input_total += input_tokens
            output_total += output_tokens
        return input_total, output_total

    def _result(
        self,
        status: str,
        final_text: str,
        responses: list[Any],
        tool_events: list[dict[str, Any]],
        model_seconds: float,
    ) -> dict[str, Any]:
        input_tokens, output_tokens = self._token_totals(responses)
        return {
            "status": status,
            "final_text": final_text,
            "cycles": len(responses),
            "tool_calls": len(tool_events),
            "model_seconds": round(model_seconds, 3),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "events": tool_events,
        }
