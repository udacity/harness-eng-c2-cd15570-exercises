"""Read-only Hermes tools for the unconfigured Task 2 baseline."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


TOOLSET_NAME = "xyz-api-harness"
HEALTH_URL = "http://localhost:8080/health"
DOCS_URL = "http://localhost:8080/api-docs"

TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "read_file": {
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


class HermesBaselinePlugin:
    """Require the same four-cycle read-only sequence as ``BaselineAgentLoop``."""

    OPERATIONS = (
        ("read_incomplete_client", "read_file"),
        ("check_api_health", "http_get"),
        ("retrieve_api_docs", "http_get"),
    )

    def __init__(self, client_path: Path, trace_file: Path) -> None:
        self.client_path = client_path.resolve()
        self.trace_file = trace_file.resolve()
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)
        self._step = 0
        self._call_count = 0

    @classmethod
    def from_environment(cls) -> "HermesBaselinePlugin":
        if os.environ.get("XYZ_HERMES_MODE") != "smoke":
            raise RuntimeError("The baseline plugin is available only in smoke mode.")
        return cls(
            Path(os.environ["XYZ_CLIENT_PATH"]),
            Path(os.environ["XYZ_TRACE_FILE"]),
        )

    def register(self, ctx: Any) -> None:
        self._record("run_started", mode="smoke", client_path=str(self.client_path))
        self._register_tool(ctx, "read_file", self._read_file, override=True)
        self._register_tool(ctx, "http_get", self._http_get)

    @staticmethod
    def _json_result(result: dict[str, Any]) -> str:
        return json.dumps(result, sort_keys=True, default=str)

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

    def _read_file(self, params: dict[str, Any], **_: Any) -> str:
        arguments = {"path": params.get("path")}
        expected = {"path": str(self.client_path)}
        accepted = self._step == 0 and self._requested_client(params.get("path"))
        if not accepted:
            result = self._rejection_result("read_file", expected)
            self._record_call("read_file", arguments, result, accepted=False)
            return self._json_result(result)
        try:
            content = self.client_path.read_text(encoding="utf-8")
        except OSError as error:
            result = {
                "status": "error",
                "executed": True,
                "tool": "read_file",
                "error": str(error),
            }
            self._record_call("read_file", arguments, result, accepted=False)
            return self._json_result(result)
        result = {
                "status": "ok",
                "executed": True,
                "tool": "read_file",
                "path": str(self.client_path),
                "content": content,
        }
        self._record_call("read_file", arguments, result, accepted=True)
        self._step += 1
        return self._json_result(result)

    def _http_get(self, params: dict[str, Any], **_: Any) -> str:
        url = params.get("url")
        arguments = {"url": url}
        expected_url = HEALTH_URL if self._step == 1 else DOCS_URL if self._step == 2 else None
        if url != expected_url:
            result = self._rejection_result("http_get", {"url": expected_url})
            self._record_call("http_get", arguments, result, accepted=False)
            return self._json_result(result)
        result = _get_json(str(url))
        accepted = result.get("status") == "ok"
        self._record_call("http_get", arguments, result, accepted=accepted)
        if accepted:
            self._step += 1
        return self._json_result(result)

    def _requested_client(self, requested: Any) -> bool:
        return isinstance(requested, str) and Path(requested).expanduser().resolve() == self.client_path

    @staticmethod
    def _rejection_result(tool: str, expected: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "rejected",
            "executed": False,
            "tool": tool,
            "expected_arguments": expected,
            "message": "Call the requested read-only tool with the exact target and in order.",
        }

    def _record_call(
        self,
        tool: str,
        arguments: dict[str, Any],
        result: dict[str, Any],
        *,
        accepted: bool,
    ) -> None:
        self._call_count += 1
        operation = self.OPERATIONS[self._step][0] if self._step < len(self.OPERATIONS) else "complete"
        self._record(
            "baseline_call",
            cycle=self._call_count,
            tool=tool,
            arguments=arguments,
            operation=operation,
            accepted=accepted,
            result=result,
        )

    def _record(self, event: str, **fields: Any) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "harness": "hermes",
            "event": event,
            **fields,
        }
        with self.trace_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True, default=str) + "\n")


def register(ctx: Any) -> None:
    HermesBaselinePlugin.from_environment().register(ctx)
