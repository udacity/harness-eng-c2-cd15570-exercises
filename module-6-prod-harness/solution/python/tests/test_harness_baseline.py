"""Live baseline check for the hand-built Python model/tool loop."""

from __future__ import annotations

import json
from types import SimpleNamespace

from python.loop import baseline_agent_loop
from python.loop.baseline_agent_loop import BASELINE_TOOL_DEFINITIONS, BaselineAgentLoop
from python.run_exercise import TASK_TEMPLATE, create_model_client


class FakeResponses:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return self.responses.pop(0)


def tool_response(response_id: str, call_id: str, name: str, arguments: dict):
    return SimpleNamespace(
        id=response_id,
        output=[
            SimpleNamespace(
                type="function_call",
                call_id=call_id,
                name=name,
                arguments=json.dumps(arguments),
            )
        ],
        output_text="",
    )


def test_preserved_baseline_copy_runs_only_the_read_only_sequence(
    tmp_path, monkeypatch
) -> None:
    client_path = tmp_path / "xyz_api_client.py"
    client_path.write_text(
        "def connect_to_xyz_api():\n    raise NotImplementedError\n", encoding="utf-8"
    )
    responses = FakeResponses(
        [
            tool_response("r1", "c1", "read_file", {"path": str(client_path)}),
            tool_response(
                "r2", "c2", "http_get", {"url": BaselineAgentLoop.HEALTH_URL}
            ),
            tool_response(
                "r3", "c3", "http_get", {"url": BaselineAgentLoop.DOCS_URL}
            ),
            SimpleNamespace(id="r4", output=[], output_text="HARNESS_OK"),
        ]
    )
    monkeypatch.setattr(
        baseline_agent_loop,
        "get_json",
        lambda _url: {"status": "ok", "executed": True, "http_status": 200},
    )

    result = BaselineAgentLoop(
        client=SimpleNamespace(responses=responses),
        model="test-model",
        client_path=client_path,
    ).run()

    assert result["status"] == "completed"
    assert result["completed_operations"] == [
        "read_incomplete_client",
        "check_api_health",
        "retrieve_api_docs",
    ]
    assert set(BASELINE_TOOL_DEFINITIONS) == {"read_file", "http_get"}
    assert [request["tools"][0]["name"] for request in responses.requests[:3]] == [
        "read_file",
        "http_get",
        "http_get",
    ]
    assert "tools" not in responses.requests[3]


def test_real_model_completes_task_relevant_read_only_cycles(capsys) -> None:
    # Show the live loop even when pytest's normal output capture is enabled.
    with capsys.disabled():
        client, model = create_model_client()
        result = BaselineAgentLoop(
            client=client, model=model, client_path=TASK_TEMPLATE
        ).run()

    assert result["status"] == "completed", result
    assert result["completed_operations"] == [
        "read_incomplete_client",
        "check_api_health",
        "retrieve_api_docs",
    ], result
    assert result["cycles"] >= 4, result
    assert result["final_text"], result
