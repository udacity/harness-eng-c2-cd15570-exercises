"""
Hand-Built Permission Wrapper for The Offline API Connector

This module provides a Python wrapper around tool functions that enforces
permission boundaries by intercepting calls and returning controlled errors.

Usage:
  from handbuilt_permissions import PermissionGate

  gate = PermissionGate(allow_web=False)
  result = gate.call_tool("web_search", query="xyz api 2026")
  # Returns: {"error": "ERR: Internet Disconnected", "code": "PERMISSION_DENIED"}
"""

import functools
import json
from typing import Any, Callable, Optional
from enum import Enum


class ToolType(Enum):
    WEB_SEARCH = "web_search"
    WEB_FETCH = "webfetch"
    BASH = "bash"
    FILE_READ = "read"
    FILE_WRITE = "write"
    EDIT = "edit"


class PermissionGate:
    """
    Hand-built permission enforcement layer.

    Wraps tool functions and enforces permission boundaries by:
    1. Checking if the tool is allowed in current configuration
    2. Returning controlled error messages when denied
    3. Logging all permission checks for audit trail

    This gives tighter control over how the agent reacts to denied access
    compared to native CLI permission systems which may show raw errors.
    """

    def __init__(
        self,
        allow_web: bool = True,
        allow_network: bool = True,
        allow_file_write: bool = True,
        debug: bool = False
    ):
        self.allow_web = allow_web
        self.allow_network = allow_network
        self.allow_file_write = allow_file_write
        self.debug = debug
        self.permission_log = []
        self.denial_count = {"web": 0, "network": 0, "file_write": 0}

    def check_permission(self, tool_type: ToolType, **kwargs) -> tuple[bool, str]:
        """
        Check if a tool call is permitted.

        Returns:
            (allowed: bool, reason: str)
        """
        reason = ""

        if tool_type in (ToolType.WEB_SEARCH, ToolType.WEB_FETCH):
            if not self.allow_web:
                return False, "Internet access is disabled for this session"
            if not self.allow_network:
                return False, "Network access is disabled for this session"

        elif tool_type == ToolType.BASH:
            cmd_args = kwargs.get("args", kwargs.get("command", ""))
            cmd = cmd_args if isinstance(cmd_args, str) else " ".join(cmd_args[:1])

            if cmd.startswith(("curl ", "wget ", "git clone ")) and not self.allow_network:
                return False, "Network commands are blocked"

            if cmd.startswith("rm -rf ") or cmd.startswith("rm -rf"):
                return False, "Dangerous delete command blocked"

        elif tool_type in (ToolType.FILE_WRITE, ToolType.EDIT):
            if not self.allow_file_write:
                return False, "File write access is disabled"

        return True, reason

    def call_tool(self, tool_name: str, **kwargs) -> dict:
        """
        Call a tool through the permission gate.

        Returns either the tool result (if allowed) or a controlled error
        message (if denied). The error format is consistent so the agent
        can handle it programmatically.
        """
        tool_type = ToolType(tool_name.upper()) if tool_name.upper() in ToolType.__members__ else None

        if tool_type:
            allowed, reason = self.check_permission(tool_type, **kwargs)

            log_entry = {
                "tool": tool_name,
                "allowed": allowed,
                "reason": reason,
                "args": {k: str(v)[:100] for k, v in kwargs.items()}  # Truncate for log
            }
            self.permission_log.append(log_entry)

            if not allowed:
                error_response = {
                    "error": f"ERR: {reason}",
                    "code": "PERMISSION_DENIED",
                    "tool": tool_name,
                    "retryable": self._is_retryable_denial(reason)
                }

                if self.debug:
                    print(f"[PERMISSION DENIED] {tool_name}: {reason}")

                self._track_denial(tool_type)
                return error_response

        # Tool is allowed or unknown - pass through
        if self.debug and tool_type:
            print(f"[PERMISSION GRANTED] {tool_name}")
        return self._execute_tool(tool_name, **kwargs)

    def _execute_tool(self, tool_name: str, **kwargs) -> dict:
        """
        Execute the actual tool call.

        In a real implementation, this would dispatch to the actual CLI tools.
        For this exercise, we simulate tool execution.
        """
        # Simulate tool execution
        return {
            "tool": tool_name,
            "executed": True,
            "result": f"Tool {tool_name} executed with args: {kwargs}"
        }

    def _is_retryable_denial(self, reason: str) -> bool:
        """Determine if a denied tool call can be retried later."""
        non_retryable = ["Internet access is disabled", "File write access is disabled"]
        return not any(n in reason for n in non_retryable)

    def _track_denial(self, tool_type: ToolType):
        """Track denial counts for statistics."""
        if tool_type in (ToolType.WEB_SEARCH, ToolType.WEB_FETCH):
            self.denial_count["web"] += 1
        elif tool_type == ToolType.BASH:
            self.denial_count["network"] += 1
        elif tool_type in (ToolType.FILE_WRITE, ToolType.EDIT):
            self.denial_count["file_write"] += 1

    def get_stats(self) -> dict:
        """Get permission statistics."""
        return {
            "total_checks": len(self.permission_log),
            "denials": self.denial_count,
            "web_enabled": self.allow_web,
            "network_enabled": self.allow_network,
            "file_write_enabled": self.allow_file_write,
        }


class HandBuiltAgentLoop:
    """
    A hand-built agent loop that wraps around any CLI agent.

    This provides:
    1. Permission enforcement before tool calls
    2. Hook execution (syntax check, token tracking)
    3. Controlled error handling for denied access
    4. Loop termination on repeated failures

    Compare this with:
    - Pre-built: claude -p 'task' --allowedTools 'Read' --max-turns 10
    - Hand-built: python run_agent.py --no-web --max-iterations 10
    """

    def __init__(
        self,
        gate: PermissionGate,
        max_iterations: int = 10,
        max_retries: int = 3,
        hook_callback: Optional[Callable] = None,
        debug: bool = False
    ):
        self.gate = gate
        self.max_iterations = max_iterations
        self.max_retries = max_retries
        self.hook_callback = hook_callback
        self.debug = debug
        self.iteration = 0
        self.retry_count = 0
        self.tool_call_history = []

    def run(self, task: str, cli_command: str) -> dict:
        """
        Run an agent loop with hand-built permission enforcement.

        Args:
            task: The task description to pass to the CLI
            cli_command: The CLI command to execute (e.g., "claude -p")

        Returns:
            Run statistics and outcome
        """
        print(f"[HAND-BUILT LOOP] Starting task: {task}")
        print(f"  Permissions: web={self.gate.allow_web}, network={self.gate.allow_network}")

        # Log all tool calls for token usage tracking
        self._log_tool_call("start", task)

        while self.iteration < self.max_iterations:
            self.iteration += 1

            # Check for loop detection
            if self._detect_loop():
                print("[HAND-BUILT LOOP] Loop detected - terminating early")
                return self._finalize("loop_detected")

            # Here you would invoke the actual CLI agent
            # cli_result = self._invoke_cli(cli_command, task + self._build_context())

            # Simulate hook execution
            if self.hook_callback:
                hook_result = self.hook_callback(
                    iteration=self.iteration,
                    task=task,
                    gate_stats=self.gate.get_stats()
                )
                if hook_result.get("terminate"):
                    print(f"[HAND-BUILT LOOP] Terminated by hook: {hook_result.get('reason')}")
                    return self._finalize("hook_terminated")

            # Simulate completion
            if self.iteration >= 3:  # Simulate task completion
                print(f"[HAND-BUILT LOOP] Task completed after {self.iteration} iterations")
                return self._finalize("completed")

            if self.debug:
                print(f"  Iteration {self.iteration}/{self.max_iterations}")

        print("[HAND-BUILT LOOP] Max iterations reached")
        return self._finalize("max_iterations")

    def _log_tool_call(self, tool: str, input_str: str):
        """Log a tool call for loop detection."""
        import hashlib
        call_hash = hashlib.md5(input_str.encode()).hexdigest()[:8]
        self.tool_call_history.append({
            "iteration": self.iteration,
            "tool": tool,
            "hash": call_hash
        })

    def _detect_loop(self) -> bool:
        """Detect if agent is stuck repeating the same tool call."""
        if len(self.tool_call_history) < 6:
            return False

        recent = self.tool_call_history[-6:]
        hashes = [c["hash"] for c in recent]
        return len(set(hashes)) == 1  # Same hash 6 times = loop

    def _invoke_cli(self, command: str, message: str) -> dict:
        """Invoke a CLI command with the given message."""
        full_cmd = f'{command} "{message}"'
        if self.debug:
            print(f"  Executing: {full_cmd}")

        # In real implementation, this would run the actual CLI
        # result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=30)
        # return json.loads(result.stdout) if result.stdout else {"error": result.stderr}

        return {"simulated": True, "command": full_cmd}

    def _build_context(self) -> str:
        """Build context string from permission logs."""
        if not self.gate.permission_log:
            return ""

        recent_logs = self.gate.permission_log[-3:]
        context = "\nRecent denials:\n"
        for log in recent_logs:
            if not log["allowed"]:
                context += f"- {log['tool']}: {log['reason']}\n"
        return context

    def _finalize(self, status: str) -> dict:
        """Generate final run report."""
        return {
            "status": status,
            "iterations": self.iteration,
            "tool_calls": len(self.tool_call_history),
            "permission_stats": self.gate.get_stats(),
            "loop_detected": self._detect_loop()
        }


def syntax_check_hook(file_path: str) -> bool:
    """
    Hand-built syntax check hook.

    Returns True if file passes syntax check, False otherwise.
    """
    import subprocess
    result = subprocess.run(
        ["python", "-m", "py_compile", file_path],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"[SYNTAX CHECK] Errors in {file_path}:")
        print(result.stderr)
        return False
    return True


def web_content_guard(content: str) -> bool:
    """
    Hand-built web content ingestion hook.

    Scans web search/browser output for malicious code snippets before
    the agent can read/process them.

    Returns True if content is safe, False if blocked.
    """
    dangerous_patterns = [
        r"exec\s*\(",
        r"eval\s*\(",
        r"__import__\s*\(",
        r"subprocess\.call.*shell\s*=\s*True",
        r"os\.system\s*\(",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            print(f"[WEB GUARD] Blocked content: pattern '{pattern}' detected")
            return False

    return True


# Need re import for web_content_guard
import re


if __name__ == "__main__":
    # Example usage:

    # 1. Create permission gate with web disabled
    gate = PermissionGate(allow_web=False, debug=True)

    # 2. Test web search denial
    result = gate.call_tool("web_search", query="xyz api 2026 documentation")
    print(f"Web search result: {result}")

    # 3. Test allowed tool
    result = gate.call_tool("read", path="solution/src/xyz_api_client_solution.py")
    print(f"Read result: {result}")

    # 4. Show stats
    print(f"\nPermission stats: {gate.get_stats()}")

    # 5. Example: Hand-built agent loop
    print("\n--- Hand-Built Agent Loop Example ---")

    def hook_callback(iteration, task, gate_stats):
        """Example hook that terminates if too many denials."""
        total_checks = gate_stats["total_checks"]
        total_denials = sum(gate_stats["denials"].values())
        if total_checks > 0 and (total_denials / total_checks) > 0.8:
            return {"terminate": True, "reason": "Too many permission denials (>80%)"}
        return {"terminate": False}

    loop = HandBuiltAgentLoop(
        gate=gate,
        max_iterations=5,
        hook_callback=hook_callback,
        debug=True
    )
    result = loop.run("Write Python XYZ API client", "claude -p")
    print(f"Loop result: {result}")
