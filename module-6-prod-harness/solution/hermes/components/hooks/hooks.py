"""Lifecycle hooks and structured evidence for the Hermes harness."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


@dataclass(frozen=True)
class HookResult:
    """A serializable hook decision."""

    hook: str
    allowed: bool
    reason: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RepeatedCallHook:
    """Block the sixth equivalent tool request in one Hermes run."""

    def __init__(self, allowed_repeats: int = 5) -> None:
        self.allowed_repeats = allowed_repeats
        self._counts: dict[str, int] = {}

    @staticmethod
    def _fingerprint(tool: str, arguments: dict[str, Any]) -> str:
        normalized = json.dumps(
            {"tool": tool, "arguments": arguments},
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def before_tool(self, tool: str, arguments: dict[str, Any]) -> HookResult:
        fingerprint = self._fingerprint(tool, arguments)
        count = self._counts.get(fingerprint, 0) + 1
        self._counts[fingerprint] = count
        allowed = count <= self.allowed_repeats
        reason = (
            f"Equivalent call {count} of {self.allowed_repeats} allowed."
            if allowed
            else f"Equivalent call blocked after {self.allowed_repeats} allowed attempts."
        )
        return HookResult(
            hook="repeated_call",
            allowed=allowed,
            reason=reason,
            details={"fingerprint": fingerprint, "count": count},
        )


class SyntaxHook:
    """Compile the assigned client after a successful Hermes write."""

    def after_write(self, client_path: Path) -> HookResult:
        try:
            source = client_path.read_text(encoding="utf-8")
            compile(source, str(client_path), "exec")
        except (OSError, SyntaxError) as error:
            return HookResult(
                hook="syntax_check",
                allowed=False,
                reason=f"Python syntax check failed: {error}",
                details={"path": str(client_path)},
            )
        return HookResult(
            hook="syntax_check",
            allowed=True,
            reason="Python syntax check passed.",
            details={"path": str(client_path)},
        )


class CompletionHook:
    """Run the fixed Hermes behavioral test before accepting completion."""

    def __init__(self, test_file: Path, result_file: Path) -> None:
        self.test_file = test_file.resolve()
        self.result_file = result_file.resolve()

    def check(self, client_path: Path) -> HookResult:
        environment = os.environ.copy()
        environment["XYZ_CLIENT_PATH"] = str(client_path.resolve())
        started = datetime.now(timezone.utc)
        command = [sys.executable, str(self.test_file)]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                env=environment,
                timeout=30,
                check=False,
            )
            returncode = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as error:
            returncode = 124
            stdout = error.stdout or ""
            stderr = (error.stderr or "") + "\nBehavioral tests exceeded the 30-second limit."
        finished = datetime.now(timezone.utc)
        record = {
            "command": command,
            "client_path": str(client_path.resolve()),
            "started_at": started.isoformat(),
            "finished_at": finished.isoformat(),
            "returncode": returncode,
            "passed": returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
        }
        self.result_file.parent.mkdir(parents=True, exist_ok=True)
        self.result_file.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        return HookResult(
            hook="completion_test",
            allowed=returncode == 0,
            reason=(
                "Behavioral tests passed."
                if returncode == 0
                else "Behavioral tests failed; the agent must continue."
            ),
            details=record,
        )


class RunTrace:
    """Append structured Hermes evidence to a JSONL file."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path.resolve() if path is not None else None
        self.events: list[dict[str, Any]] = []
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: str, **fields: Any) -> dict[str, Any]:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "harness": "hermes",
            "event": event,
            **fields,
        }
        self.events.append(entry)
        if self.path is not None:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, sort_keys=True, default=str) + "\n")
        return entry
