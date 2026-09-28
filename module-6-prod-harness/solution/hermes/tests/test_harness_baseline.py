"""Live baseline check for the Hermes model/tool loop."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile

from hermes.baseline_plugin import DOCS_URL, HEALTH_URL, HermesBaselinePlugin
from hermes.run_exercise import hermes_binary, resolve_model_settings, run_smoke_test


class FakePluginContext:
    def __init__(self) -> None:
        self.tools: dict[str, dict] = {}

    def register_tool(self, **kwargs) -> None:
        self.tools[kwargs["name"]] = kwargs


def test_baseline_adapter_exposes_only_read_only_tools(monkeypatch) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        directory = Path(temp_dir)
        client = directory / "xyz_api_client.py"
        trace = directory / "smoke.jsonl"
        client.write_text("def connect_to_xyz_api():\n    raise NotImplementedError\n", encoding="utf-8")
        plugin = HermesBaselinePlugin(client, trace)
        context = FakePluginContext()
        plugin.register(context)

        responses = iter(
            [
                {"status": "ok", "executed": True, "http_status": 200, "body": {"status": "ok"}},
                {"status": "ok", "executed": True, "http_status": 200, "body": {"endpoint": "/v2/data-sync"}},
            ]
        )
        monkeypatch.setattr("hermes.baseline_plugin._get_json", lambda _url: next(responses))
        read_result = json.loads(
            context.tools["read_file"]["handler"]({"path": str(client)})
        )
        health_result = json.loads(
            context.tools["http_get"]["handler"]({"url": HEALTH_URL})
        )
        docs_result = json.loads(
            context.tools["http_get"]["handler"]({"url": DOCS_URL})
        )

    assert set(context.tools) == {"read_file", "http_get"}
    assert read_result["status"] == "ok"
    assert health_result["status"] == "ok"
    assert docs_result["status"] == "ok"


def test_real_model_completes_task_relevant_read_only_cycles(capsys) -> None:
    with capsys.disabled():
        binary = hermes_binary()
        model = resolve_model_settings(
            binary, model_override=None, provider_override=None
        )
        result = run_smoke_test(binary=binary, model=model)

    assert result["status"] == "completed", result
    assert result["completed_operations"] == [
        "read_incomplete_client",
        "check_api_health",
        "retrieve_api_docs",
    ], result
    assert result["cycles"] >= 4, result
    assert result["final_text"], result
