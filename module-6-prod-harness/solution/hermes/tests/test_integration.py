"""Integration tests for Hermes plugin, skill, policy, hooks, and runner wiring."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile

from hermes.components.hooks import CompletionHook, RepeatedCallHook, RunTrace, SyntaxHook
from hermes.components.permissions import PermissionPolicy
from hermes.plugin_impl import FULL_TOOL_NAMES, HermesHarnessPlugin, TOOL_SCHEMAS
from hermes.run_exercise import (
    HERMES_DIR,
    PROFILE_TEMPLATE,
    TASK_TEMPLATE,
    _profile_config,
    hermes_binary,
    source_hermes_home,
    temporary_profile,
)


class FakePluginContext:
    def __init__(self) -> None:
        self.tools: dict[str, dict] = {}
        self.hooks: dict[str, object] = {}
        self.skills: dict[str, Path] = {}

    def register_tool(self, **kwargs):
        self.tools[kwargs["name"]] = kwargs

    def register_hook(self, name, callback):
        self.hooks[name] = callback

    def register_skill(self, name, path, **_):
        self.skills[name] = Path(path)


def make_plugin(directory: Path) -> tuple[HermesHarnessPlugin, Path, Path]:
    client = directory / "xyz_api_client.py"
    client.write_text(
        "def connect_to_xyz_api():\n    raise NotImplementedError\n", encoding="utf-8"
    )
    behavior = directory / "behavior_test.py"
    behavior.write_text(
        "import os\n"
        "from pathlib import Path\n"
        "source = Path(os.environ['XYZ_CLIENT_PATH']).read_text()\n"
        "assert \"'status': 'synced'\" in source\n",
        encoding="utf-8",
    )
    result_file = directory / "test-results.json"
    plugin = HermesHarnessPlugin(
        mode="fresh",
        client_path=client,
        trace=RunTrace(),
        behavior_test=behavior,
        test_result_file=result_file,
    )
    return plugin, client, result_file


def test_configured_plugin_exposes_only_five_scoped_tools() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        plugin, _, _ = make_plugin(Path(temp_dir))
        context = FakePluginContext()
        plugin.register(context)

    assert set(context.tools) == FULL_TOOL_NAMES
    assert set(TOOL_SCHEMAS) == FULL_TOOL_NAMES
    assert all(
        schema["parameters"].get("additionalProperties") is False
        for schema in TOOL_SCHEMAS.values()
    )
    assert context.tools["read_file"]["override"] is True
    assert context.tools["write_file"]["override"] is True
    assert context.tools["web_search"]["override"] is True


def test_native_lifecycle_boundaries_and_skill_are_registered() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        plugin, _, _ = make_plugin(Path(temp_dir))
        context = FakePluginContext()
        plugin.register(context)

    assert set(context.hooks) == {
        "pre_tool_call",
        "post_tool_call",
        "transform_tool_result",
        "pre_verify",
        "pre_llm_call",
    }
    assert set(context.skills) == {"xyz-api-client"}
    assert context.skills["xyz-api-client"].is_file()
    context.hooks["pre_llm_call"]()
    context.hooks["pre_llm_call"]()
    assert sum(event["event"] == "skill_loaded" for event in plugin.trace.events) == 1


def test_permission_denial_returns_to_hermes_without_execution() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        plugin, _, _ = make_plugin(Path(temp_dir))
        context = FakePluginContext()
        plugin.register(context)

        directive = context.hooks["pre_tool_call"](
            tool_name="web_search", args={"query": "2026 XYZ API"}
        )

    assert directive["action"] == "block"
    result = json.loads(directive["message"])
    assert result["status"] == "permission_denied"
    assert result["executed"] is False
    assert result["rule"] == "network.public_web_denied"


def test_docs_unlock_write_and_syntax_result_is_returned_to_model() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        plugin, client, _ = make_plugin(Path(temp_dir))
        context = FakePluginContext()
        plugin.register(context)
        write_args = {"path": str(client), "content": "def broken(:\n"}

        blocked = context.hooks["pre_tool_call"](
            tool_name="write_file", args=write_args
        )
        assert json.loads(blocked["message"])["rule"] == "workflow.docs_before_write"

        docs_args = {"url": "http://localhost:8080/api-docs"}
        context.hooks["post_tool_call"](
            tool_name="http_get",
            args=docs_args,
            result=json.dumps(
                {"status": "ok", "executed": True, "http_status": 200, "body": {}}
            ),
        )
        assert context.hooks["pre_tool_call"](
            tool_name="write_file", args=write_args
        ) is None
        raw_result = context.tools["write_file"]["handler"](write_args)
        transformed = context.hooks["transform_tool_result"](
            tool_name="write_file", args=write_args, result=raw_result
        )

    result = json.loads(transformed)
    assert result["status"] == "hook_blocked"
    assert result["syntax_check"]["allowed"] is False


def test_repeated_call_hook_blocks_sixth_equivalent_allowed_call() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        plugin, client, _ = make_plugin(Path(temp_dir))
        context = FakePluginContext()
        plugin.register(context)
        directives = [
            context.hooks["pre_tool_call"](
                tool_name="read_file", args={"path": str(client)}
            )
            for _ in range(6)
        ]

    assert all(directive is None for directive in directives[:5])
    assert json.loads(directives[5]["message"])["status"] == "hook_blocked"


def test_pre_verify_blocks_failed_tests_and_accepts_passing_tests() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        plugin, client, result_file = make_plugin(Path(temp_dir))
        context = FakePluginContext()
        plugin.register(context)

        blocked = context.hooks["pre_verify"]()
        assert blocked["action"] == "continue"

        client.write_text(
            "def connect_to_xyz_api():\n    return {'status': 'synced'}\n",
            encoding="utf-8",
        )
        accepted = context.hooks["pre_verify"]()
        evidence = json.loads(result_file.read_text(encoding="utf-8"))

    assert accepted is None
    assert evidence["passed"] is True


def test_components_match_python_harness_contracts() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        directory = Path(temp_dir)
        client = directory / "xyz_api_client.py"
        other = directory / "server.py"
        client.write_text("value = 1\n", encoding="utf-8")
        policy = PermissionPolicy(client)

        assert policy.decide("read_file", {"path": str(client)}).allowed
        assert not policy.decide("read_file", {"path": str(other)}).allowed
        assert not policy.decide("shell", {"command": "ls"}).allowed
        assert not policy.decide("http_get", {"url": "https://example.com"}).allowed

        repeated = RepeatedCallHook()
        decisions = [repeated.before_tool("read_file", {"path": str(client)}) for _ in range(6)]
        assert all(decision.allowed for decision in decisions[:5])
        assert not decisions[5].allowed

        client.write_text("def broken(:\n", encoding="utf-8")
        assert not SyntaxHook().after_write(client).allowed


def test_completion_hook_writes_fixed_test_evidence() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        directory = Path(temp_dir)
        client = directory / "xyz_api_client.py"
        client.write_text("value = 1\n", encoding="utf-8")
        test_file = directory / "behavior_test.py"
        test_file.write_text(
            "import os\n"
            "from pathlib import Path\n"
            "assert Path(os.environ['XYZ_CLIENT_PATH']).read_text() == 'value = 1\\n'\n",
            encoding="utf-8",
        )
        result_file = directory / "test-results.json"

        decision = CompletionHook(test_file, result_file).check(client)
        evidence = json.loads(result_file.read_text(encoding="utf-8"))

    assert decision.allowed
    assert evidence["passed"] is True


def test_runtime_config_enables_only_the_exercise_plugin_toolset() -> None:
    config = (PROFILE_TEMPLATE / "config.yaml").read_text(encoding="utf-8")
    rendered = _profile_config(
        {"provider": "openrouter", "model": "openai/gpt-4o", "base_url": "https://example.test/v1"}
    )

    assert "xyz-api-harness" in config
    assert "allow_tool_override: true" in config
    assert "max_verify_nudges: 5" in config
    assert 'provider: "openrouter"' in rendered
    assert 'default: "openai/gpt-4o"' in rendered


def test_installed_hermes_loads_plugin_offline() -> None:
    binary = hermes_binary()
    runtime_root = source_hermes_home() / "hermes-agent"
    runtime_python = runtime_root / "venv" / "bin" / "python"
    with tempfile.TemporaryDirectory() as temp_dir:
        trace_file = Path(temp_dir) / "trace.jsonl"
        with temporary_profile(
            mode="fresh",
            client_path=TASK_TEMPLATE,
            trace_file=trace_file,
            model={"provider": "openrouter", "model": "offline-validation"},
        ) as (_, environment, _):
            plugins = subprocess.run(
                [str(binary), "plugins", "list", "--enabled", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                env=environment,
                cwd=HERMES_DIR,
            )
            prompt_size = subprocess.run(
                [str(binary), "prompt-size", "--platform", "cli", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                env=environment,
                cwd=HERMES_DIR,
            )
            preload = subprocess.run(
                [
                    str(runtime_python),
                    "-c",
                    (
                        "import json; "
                        "from hermes_cli.plugins import discover_plugins; "
                        "discover_plugins(); "
                        "from agent.skill_commands import build_preloaded_skills_prompt; "
                        "prompt, loaded, missing = build_preloaded_skills_prompt("
                        "['xyz-api-harness:xyz-api-client']); "
                        "from model_tools import handle_function_call; "
                        f"read_result = handle_function_call('read_file', "
                        f"{{'path': {str(TASK_TEMPLATE)!r}}}, "
                        "enabled_toolsets=['xyz-api-harness']); "
                        "denied_result = handle_function_call('web_search', "
                        "{'query': 'XYZ API'}, enabled_toolsets=['xyz-api-harness']); "
                        "print(json.dumps({'has_prompt': bool(prompt), "
                        "'loaded': loaded, 'missing': missing, "
                        "'read_result': read_result, 'denied_result': denied_result}))"
                    ),
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
                env=environment,
                cwd=runtime_root,
            )
            trace_events = [
                json.loads(line)
                for line in trace_file.read_text(encoding="utf-8").splitlines()
            ]

    assert plugins.returncode == 0, plugins.stderr
    assert "xyz-api-harness" in plugins.stdout
    assert prompt_size.returncode == 0, prompt_size.stderr
    assert "xyz-api-harness" not in prompt_size.stderr
    assert preload.returncode == 0, preload.stderr
    preload_result = json.loads(preload.stdout.strip().splitlines()[-1])
    assert preload_result["has_prompt"] is True
    assert preload_result["loaded"] == ["xyz-api-harness:xyz-api-client"]
    assert preload_result["missing"] == []
    assert "connect_to_xyz_api" in preload_result["read_result"]
    assert "permission_denied" in preload_result["denied_result"]
    assert "network.public_web_denied" in preload_result["denied_result"]
    assert any(event.get("event") == "run_started" for event in trace_events)
    assert any(event.get("event") == "skill_registered" for event in trace_events)
    assert any(
        event.get("event") == "permission_decision"
        and event.get("requested_capability") == "web_search"
        and event.get("decision") == "deny"
        for event in trace_events
    )
