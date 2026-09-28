"""Exact allowlist for model-requested tools in the Hermes harness."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PermissionDecision:
    tool: str
    allowed: bool
    rule: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PermissionPolicy:
    """Authorize only capabilities required by the XYZ client task."""

    HEALTH_URL = "http://localhost:8080/health"
    DOCS_URL = "http://localhost:8080/api-docs"

    def __init__(self, client_path: Path) -> None:
        self.client_path = client_path.resolve()
        self._docs_retrieved = False

    def decide(self, tool: str, arguments: dict[str, Any]) -> PermissionDecision:
        if tool in {"read_file", "write_file"}:
            requested = arguments.get("path")
            if not isinstance(requested, str):
                return self._deny(tool, "file.path_required", "A string path is required.")
            try:
                resolved = Path(requested).expanduser().resolve()
            except (OSError, RuntimeError) as error:
                return self._deny(tool, "file.invalid_path", f"Invalid path: {error}")
            if resolved != self.client_path:
                return self._deny(
                    tool,
                    "file.assigned_client_only",
                    "Only the assigned run's xyz_api_client.py may be read or written.",
                )
            if tool == "write_file" and not isinstance(arguments.get("content"), str):
                return self._deny(
                    tool, "file.content_required", "write_file requires string content."
                )
            if tool == "write_file" and not self._docs_retrieved:
                return self._deny(
                    tool,
                    "workflow.docs_before_write",
                    "Retrieve the local API contract successfully before editing the client.",
                )
            return self._allow(
                tool,
                f"file.{tool}.assigned_client",
                "The request targets the assigned client file.",
            )

        if tool == "http_get":
            url = arguments.get("url")
            if url == self.HEALTH_URL:
                return self._allow(tool, "network.local_health", "Local health URL allowed.")
            if url == self.DOCS_URL:
                return self._allow(
                    tool, "network.local_api_docs", "Local documentation URL allowed."
                )
            return self._deny(
                tool,
                "network.local_get_allowlist",
                "Only the exact local health and API documentation URLs are allowed.",
            )

        if tool == "run_tests":
            if arguments:
                return self._deny(
                    tool,
                    "tests.fixed_command_only",
                    "The supplied test command does not accept model-controlled arguments.",
                )
            return self._allow(
                tool, "tests.supplied_behavioral_suite", "The fixed supplied tests are allowed."
            )

        if tool == "web_search":
            return self._deny(
                tool,
                "network.public_web_denied",
                "The fictional API has no public documentation; use the local /api-docs endpoint.",
            )

        return self._deny(
            tool,
            "default_deny",
            "Unknown tools and unspecified capabilities are denied by default.",
        )

    def observe_result(
        self, tool: str, arguments: dict[str, Any], result: dict[str, Any]
    ) -> None:
        """Advance trusted state only after a successful documentation request."""

        if (
            tool == "http_get"
            and arguments.get("url") == self.DOCS_URL
            and result.get("executed") is True
            and result.get("http_status") == 200
            and result.get("status") == "ok"
        ):
            self._docs_retrieved = True

    @staticmethod
    def _allow(tool: str, rule: str, reason: str) -> PermissionDecision:
        return PermissionDecision(tool=tool, allowed=True, rule=rule, reason=reason)

    @staticmethod
    def _deny(tool: str, rule: str, reason: str) -> PermissionDecision:
        return PermissionDecision(tool=tool, allowed=False, rule=rule, reason=reason)
