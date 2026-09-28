"""Integration tests for Python skill, permission, hook, and dispatch wiring."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest
from urllib.error import URLError
from urllib.request import urlopen

from python.components.hooks import CompletionHook, RepeatedCallHook, SyntaxHook
from python.components.permissions import PermissionPolicy
from python.loop.configured_agent_loop import HandBuiltAgentLoop, RunTrace, TOOL_DEFINITIONS
from python.run_exercise import (
    SKILL_FILE,
    TASK_TEMPLATE,
    create_model_client,
)


COMPONENT_PROBE_TASK = """Exercise the configured harness components without implementing the client.

This is only an integration wiring probe, not the XYZ API client task. The
assigned client must remain incomplete and must still contain its existing
NotImplementedError when you finish.

Perform this exact sequence with the available tools:
1. Call http_get for http://localhost:8080/health.
2. Call http_get for http://localhost:8080/api-docs.
3. Read the assigned client file.
4. Write the exact same source back to that assigned file without changing it.
5. Call run_tests. This probe test passes only when the client remains incomplete.
6. Return a non-empty final response confirming the component probe is complete.

Do not implement connect_to_xyz_api and do not alter the file contents.
"""


def test_real_model_exercises_the_configured_component_boundaries(
    tmp_path: Path, capsys
) -> None:
    """Use a real model to exercise wiring without completing the Task 5 client."""

    try:
        with urlopen(PermissionPolicy.HEALTH_URL, timeout=2) as response:
            if response.status != 200:
                raise AssertionError(
                    f"XYZ API health check returned HTTP {response.status}."
                )
    except (OSError, URLError) as error:
        raise AssertionError(
            "The live integration test requires the XYZ API server. Start it in "
            "another terminal with `python3 api_server/server.py`."
        ) from error

    client_path = tmp_path / "python" / "runs" / "src" / "xyz_api_client.py"
    client_path.parent.mkdir(parents=True)
    shutil.copyfile(TASK_TEMPLATE, client_path)
    original_source = client_path.read_text(encoding="utf-8")
    trace_path = tmp_path / "run.jsonl"
    result_path = tmp_path / "test-results.json"
    probe_test = tmp_path / "test_client_remains_incomplete.py"
    probe_test.write_text(
        "import os\n"
        "from pathlib import Path\n"
        "source = Path(os.environ['XYZ_CLIENT_PATH']).read_text(encoding='utf-8')\n"
        "assert 'raise NotImplementedError' in source\n",
        encoding="utf-8",
    )
    trace = RunTrace(trace_path)
    client, model = create_model_client()
    loop = HandBuiltAgentLoop(
        client=client,
        model=model,
        client_path=client_path,
        skill_text=SKILL_FILE.read_text(encoding="utf-8"),
        permission_policy=PermissionPolicy(client_path),
        repeated_call_hook=RepeatedCallHook(),
        syntax_hook=SyntaxHook(),
        completion_hook=CompletionHook(probe_test, result_path),
        trace=trace,
    )

    # Keep the live model/tool transcript visible under normal pytest capture.
    with capsys.disabled():
        result = loop.run(COMPONENT_PROBE_TASK)

    assert result["status"] == "completed", result
    assert result["final_text"], result
    assert client_path.read_text(encoding="utf-8") == original_source
    assert "NotImplementedError" in original_source
    assert trace_path.is_file()
    evidence = json.loads(result_path.read_text(encoding="utf-8"))
    assert evidence["passed"] is True, evidence

    events = trace.events
    assert any(event["event"] == "skill_loaded" for event in events)

    permission_indices = [
        index for index, event in enumerate(events) if event["event"] == "permission_decision"
    ]
    tool_result_indices = [
        index for index, event in enumerate(events) if event["event"] == "tool_result"
    ]
    assert len(permission_indices) == len(tool_result_indices) > 0
    assert all(
        permission_index < result_index
        for permission_index, result_index in zip(permission_indices, tool_result_indices)
    )

    allowed_permissions = [
        event
        for event in events
        if event["event"] == "permission_decision" and event["decision"] == "allow"
    ]
    repeated_hooks = [
        event
        for event in events
        if event["event"] == "hook" and event.get("hook") == "repeated_call"
    ]
    assert len(repeated_hooks) == len(allowed_permissions)
    assert any(
        event["event"] == "hook" and event.get("hook") == "syntax_check"
        for event in events
    )
    assert any(
        event["event"] == "hook" and event.get("hook") == "completion_test"
        for event in events
    )
    assert any(
        event["event"] == "tool_result"
        and event["tool"] == "http_get"
        and event["arguments"].get("url") == PermissionPolicy.DOCS_URL
        and event["result"].get("status") == "ok"
        for event in events
    )
    completion_index = max(
        index for index, event in enumerate(events) if event["event"] == "completion"
    )
    completion_hook_index = max(
        index
        for index, event in enumerate(events)
        if event["event"] == "hook" and event.get("hook") == "completion_test"
    )
    assert completion_hook_index < completion_index


class IntegrationTests(unittest.TestCase):
    def test_configured_loop_exposes_only_the_five_scoped_tools(self) -> None:
        self.assertEqual(
            {tool["name"] for tool in TOOL_DEFINITIONS},
            {"read_file", "write_file", "http_get", "web_search", "run_tests"},
        )
        for tool in TOOL_DEFINITIONS:
            self.assertFalse(tool["parameters"].get("additionalProperties", True))

    def test_permission_policy_is_default_deny_and_path_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            assigned = Path(temp_dir) / "xyz_api_client.py"
            other = Path(temp_dir) / "server.py"
            policy = PermissionPolicy(assigned)

            self.assertTrue(policy.decide("read_file", {"path": str(assigned)}).allowed)
            self.assertFalse(
                policy.decide(
                    "write_file", {"path": str(assigned), "content": "valid = True\n"}
                ).allowed
            )
            policy.observe_result(
                "http_get",
                {"url": "http://localhost:8080/api-docs"},
                {"status": "ok", "executed": True, "http_status": 200},
            )
            self.assertTrue(
                policy.decide(
                    "write_file", {"path": str(assigned), "content": "valid = True\n"}
                ).allowed
            )
            self.assertFalse(policy.decide("read_file", {"path": str(other)}).allowed)
            self.assertFalse(policy.decide("shell", {"command": "ls"}).allowed)
            self.assertFalse(
                policy.decide("http_get", {"url": "https://example.com"}).allowed
            )

    def test_repeated_call_hook_blocks_the_sixth_equivalent_call(self) -> None:
        hook = RepeatedCallHook()
        decisions = [hook.before_tool("read_file", {"path": "client.py"}) for _ in range(6)]

        self.assertTrue(all(decision.allowed for decision in decisions[:5]))
        self.assertFalse(decisions[5].allowed)
        self.assertEqual(decisions[5].details["count"], 6)

    def test_syntax_hook_rejects_invalid_python(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            client_path = Path(temp_dir) / "xyz_api_client.py"
            client_path.write_text("def broken(:\n", encoding="utf-8")

            decision = SyntaxHook().after_write(client_path)

        self.assertFalse(decision.allowed)
        self.assertIn("syntax", decision.reason.lower())

    def test_completion_hook_runs_fixed_test_and_writes_result_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            client_path = directory / "xyz_api_client.py"
            client_path.write_text("value = 1\n", encoding="utf-8")
            test_file = directory / "behavior_test.py"
            test_file.write_text(
                "import os\n"
                "from pathlib import Path\n"
                "assert Path(os.environ['XYZ_CLIENT_PATH']).read_text() == 'value = 1\\n'\n",
                encoding="utf-8",
            )
            result_file = directory / "test-results.json"

            decision = CompletionHook(test_file, result_file).check(client_path)
            evidence = json.loads(result_file.read_text(encoding="utf-8"))

        self.assertTrue(decision.allowed)
        self.assertTrue(evidence["passed"])
        self.assertEqual(evidence["returncode"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
