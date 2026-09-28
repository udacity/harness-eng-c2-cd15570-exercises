"""Read-only hand-built Python loop preserved from the Task 2 baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASELINE_TOOL_DEFINITIONS = {
    "read_file": {
        "type": "function",
        "name": "read_file",
        "description": "Read the assigned incomplete Python client.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    "http_get": {
        "type": "function",
        "name": "http_get",
        "description": "Make the requested read-only local HTTP GET request.",
        "parameters": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
            "additionalProperties": False,
        },
    },
}


def get_json(url: str) -> dict[str, Any]:
    """Execute one JSON GET request for an expected baseline URL."""

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


class BaselineAgentLoop:
    """Exercise the unconfigured loop with safe, task-relevant read operations."""

    HEALTH_URL = "http://localhost:8080/health"
    DOCS_URL = "http://localhost:8080/api-docs"

    def __init__(
        self, *, client: Any, model: str, client_path: Path, max_cycles: int = 12
    ) -> None:
        self.client = client
        self.model = model
        self.client_path = client_path.resolve()
        self.max_cycles = max_cycles

    def run(self) -> dict[str, Any]:
        instructions = (
            "You are checking that a Python agent loop works before production controls are "
            "connected. Perform these read-only operations in order, one tool call per turn: "
            "read the assigned incomplete client, check the local API health URL, then retrieve "
            "the local API documentation URL. Read each tool result before continuing. After all "
            "three operations succeed, reply exactly HARNESS_OK. Do not write any file."
        )
        operations = [
            {
                "label": "read_incomplete_client",
                "tool": "read_file",
                "arguments": {"path": str(self.client_path)},
            },
            {
                "label": "check_api_health",
                "tool": "http_get",
                "arguments": {"url": self.HEALTH_URL},
            },
            {
                "label": "retrieve_api_docs",
                "tool": "http_get",
                "arguments": {"url": self.DOCS_URL},
            },
        ]
        model_input: Any = (
            f"Assigned incomplete client: {self.client_path}\n"
            f"Health URL: {self.HEALTH_URL}\n"
            f"Documentation URL: {self.DOCS_URL}\n"
            "Begin the read-only baseline check."
        )
        previous_response_id: str | None = None
        completed_operations: list[str] = []
        events: list[dict[str, Any]] = []

        print("\n==================================================")
        print("HAND-BUILT PYTHON LOOP — LIVE BASELINE")
        print("==================================================")
        print(f"Model: {self.model}")
        print(f"Client: {self.client_path}")
        print("Required sequence: read client -> GET /health -> GET /api-docs -> final response")

        for cycle in range(1, self.max_cycles + 1):
            print(f"\n--- BASELINE CYCLE {cycle} ---")
            operations_complete = len(completed_operations) == len(operations)
            expected = None if operations_complete else operations[len(completed_operations)]
            kwargs: dict[str, Any] = {
                "model": self.model,
                "instructions": instructions,
                "input": model_input,
            }
            if expected is not None:
                kwargs["tools"] = [BASELINE_TOOL_DEFINITIONS[expected["tool"]]]
                kwargs["parallel_tool_calls"] = False
                kwargs["tool_choice"] = "required"
            if previous_response_id is not None:
                kwargs["previous_response_id"] = previous_response_id
            response = self.client.responses.create(**kwargs)
            calls = [item for item in response.output if item.type == "function_call"]
            response_text = response.output_text.strip()
            if response_text:
                print("AGENT TEXT:")
                print(response_text)

            if not operations_complete:
                outputs = []
                accepted_this_cycle = False
                for item in calls:
                    arguments = self._parse_arguments(getattr(item, "arguments", ""))
                    print(f"AGENT REQUESTED TOOL: {getattr(item, 'name', '(unknown)')}")
                    print(f"TOOL ARGUMENTS: {getattr(item, 'arguments', '')}")
                    accepted = (
                        not accepted_this_cycle
                        and item.name == expected["tool"]
                        and self._arguments_match(expected, arguments)
                    )
                    if accepted:
                        accepted_this_cycle = True
                        result = self._execute_read_operation(expected)
                        if result.get("status") == "ok":
                            completed_operations.append(expected["label"])
                        else:
                            accepted = False
                    else:
                        result = {
                            "status": "rejected",
                            "expected_tool": expected["tool"],
                            "expected_arguments": expected["arguments"],
                            "message": "Call the requested read-only tool with the exact target.",
                        }
                    print("TOOL RESULT:")
                    print(json.dumps(result, indent=2))
                    events.append(
                        {
                            "cycle": cycle,
                            "tool": getattr(item, "name", "(unknown)"),
                            "arguments": arguments,
                            "operation": expected["label"],
                            "accepted": accepted,
                        }
                    )
                    outputs.append(self._tool_output(item.call_id, result))

                if not outputs:
                    print("NO TOOL CALL: asking the model for the required operation")
                    model_input = (
                        f"Call {expected['tool']} with exactly: "
                        f"{json.dumps(expected['arguments'])}"
                    )
                else:
                    model_input = outputs
                previous_response_id = response.id
                continue

            if response_text:
                print("\n================ BASELINE SUMMARY ================")
                print(f"Model cycles:   {cycle}")
                print(f"Operations:     {completed_operations}")
                print("Status:         COMPLETED")
                return {
                    "status": "completed",
                    "cycles": cycle,
                    "completed_operations": completed_operations,
                    "final_text": response_text,
                    "events": events,
                }
            model_input = "All three read-only operations succeeded. Reply exactly HARNESS_OK."
            previous_response_id = response.id

        return {
            "status": "max_cycles",
            "cycles": self.max_cycles,
            "completed_operations": completed_operations,
            "final_text": "",
            "events": events,
        }

    @staticmethod
    def _parse_arguments(raw: str) -> dict[str, Any]:
        try:
            value = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}
        return value if isinstance(value, dict) else {}

    def _arguments_match(
        self, expected: dict[str, Any], arguments: dict[str, Any]
    ) -> bool:
        if expected["tool"] == "read_file":
            path = arguments.get("path")
            return isinstance(path, str) and Path(path).expanduser().resolve() == self.client_path
        return arguments == expected["arguments"]

    def _execute_read_operation(self, operation: dict[str, Any]) -> dict[str, Any]:
        if operation["tool"] == "read_file":
            return {
                "status": "ok",
                "executed": True,
                "tool": "read_file",
                "content": self.client_path.read_text(encoding="utf-8"),
            }
        return get_json(operation["arguments"]["url"])

    @staticmethod
    def _tool_output(call_id: str, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "function_call_output",
            "call_id": call_id,
            "output": json.dumps(result),
        }
