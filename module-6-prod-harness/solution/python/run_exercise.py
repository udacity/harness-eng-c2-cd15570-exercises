"""Run the hand-built Python harness for the XYZ API client exercise."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Any


PYTHON_DIR = Path(__file__).resolve().parent
SOLUTION_DIR = PYTHON_DIR.parent
if str(SOLUTION_DIR) not in sys.path:
    sys.path.insert(0, str(SOLUTION_DIR))

from python.loop.baseline_agent_loop import BaselineAgentLoop


TASK_TEMPLATE = SOLUTION_DIR / "task" / "src" / "xyz_api_client.py"
SKILL_FILE = PYTHON_DIR / "components" / "skill" / "SKILL.md"
RUNS_DIR = PYTHON_DIR / "runs"
CLIENT_FILE = RUNS_DIR / "src" / "xyz_api_client.py"
TRACE_FILE = RUNS_DIR / "run.jsonl"
TEST_RESULT_FILE = RUNS_DIR / "test-results.json"
SMOKE_FILE = RUNS_DIR / "smoke.json"
BEHAVIOR_TEST = PYTHON_DIR / "tests" / "test_generated_client.py"

TASK = """Complete connect_to_xyz_api() in the assigned client file.

The local API contract is intentionally omitted from this prompt. Follow the
supplied skill, use the available tools to discover the current local contract,
implement the client, and run the supplied tests. Do not modify any other file.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run the live read-only multi-cycle baseline and save python/runs/smoke.json.",
    )
    mode.add_argument(
        "--fresh",
        action="store_true",
        help="Reset the run client and execute the complete configured harness.",
    )
    return parser.parse_args()


def create_model_client() -> tuple[Any, str]:
    try:
        from dotenv import load_dotenv
        from openai import OpenAI
    except ImportError as error:
        raise SystemExit(
            "Install the Python harness dependencies with "
            "`python3 -m pip install -r python/requirements.txt`."
        ) from error

    load_dotenv(PYTHON_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            f"Set OPENAI_API_KEY in the environment or in {PYTHON_DIR / '.env'}."
        )
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
    base_url = os.getenv("OPENAI_BASE_URL", "https://openai.vocareum.com/v1").strip()
    return OpenAI(base_url=base_url, api_key=api_key), model


def run_smoke_test(client: Any, model: str) -> None:
    result = BaselineAgentLoop(
        client=client, model=model, client_path=TASK_TEMPLATE
    ).run()
    passed = (
        result["status"] == "completed"
        and result["completed_operations"]
        == ["read_incomplete_client", "check_api_health", "retrieve_api_docs"]
        and result["cycles"] >= 4
    )
    record = {"harness": "python", "model": model, "passed": passed, **result}
    SMOKE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SMOKE_FILE.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit(f"Smoke test failed: {json.dumps(record, indent=2)}")
    print("HARNESS_OK")


def prepare_fresh_workspace() -> None:
    CLIENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TASK_TEMPLATE, CLIENT_FILE)
    TRACE_FILE.write_text("", encoding="utf-8")
    TEST_RESULT_FILE.write_text("", encoding="utf-8")


def run_fresh(client: Any, model: str) -> None:
    from python.components.hooks import CompletionHook, RepeatedCallHook, SyntaxHook
    from python.components.permissions import PermissionPolicy
    from python.loop.configured_agent_loop import HandBuiltAgentLoop, RunTrace

    prepare_fresh_workspace()
    completion_hook = CompletionHook(BEHAVIOR_TEST, TEST_RESULT_FILE)
    loop = HandBuiltAgentLoop(
        client=client,
        model=model,
        client_path=CLIENT_FILE,
        skill_text=SKILL_FILE.read_text(encoding="utf-8"),
        permission_policy=PermissionPolicy(CLIENT_FILE),
        repeated_call_hook=RepeatedCallHook(),
        syntax_hook=SyntaxHook(),
        completion_hook=completion_hook,
        trace=RunTrace(TRACE_FILE),
    )
    result = loop.run(TASK)
    print(json.dumps({key: value for key, value in result.items() if key != "events"}, indent=2))
    if result["status"] != "completed":
        raise SystemExit(1)


def main() -> None:
    args = parse_args()
    client, model = create_model_client()
    if args.smoke_test:
        run_smoke_test(client, model)
    else:
        run_fresh(client, model)


if __name__ == "__main__":
    main()
