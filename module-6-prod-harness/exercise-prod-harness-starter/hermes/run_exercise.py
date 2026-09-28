"""Run the Hermes production harness for the XYZ API client exercise."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable, Iterator

HERMES_DIR = Path(__file__).resolve().parent
SOLUTION_DIR = HERMES_DIR.parent
if str(SOLUTION_DIR) not in sys.path:
    sys.path.insert(0, str(SOLUTION_DIR))

TASK_TEMPLATE = SOLUTION_DIR / "task" / "src" / "xyz_api_client.py"
PROFILE_TEMPLATE = HERMES_DIR / ".hermes"
PLUGIN_TEMPLATE = PROFILE_TEMPLATE / "plugins" / "xyz-api-harness"
RUNS_DIR = HERMES_DIR / "runs"
CLIENT_FILE = RUNS_DIR / "src" / "xyz_api_client.py"
TRACE_FILE = RUNS_DIR / "run.jsonl"
SMOKE_TRACE_FILE = RUNS_DIR / "smoke.jsonl"
TEST_RESULT_FILE = RUNS_DIR / "test-results.json"
SMOKE_FILE = RUNS_DIR / "smoke.json"
BEHAVIOR_TEST = HERMES_DIR / "tests" / "test_generated_client.py"
DEFAULT_HERMES_BIN = Path.home() / ".local" / "bin" / "hermes"

TASK = """Complete connect_to_xyz_api() in the assigned client file.

The local API contract is intentionally omitted from this prompt. Follow the
preloaded xyz-api-client skill, use the available tools to discover the current
local contract, implement the client, and run the supplied tests. Do not modify
any other file.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run the live read-only multi-cycle baseline and save hermes/runs/smoke.json.",
    )
    mode.add_argument(
        "--fresh",
        action="store_true",
        help="Reset the run client and execute the complete configured Hermes harness.",
    )
    parser.add_argument("--model", help="Override the model for this Hermes invocation.")
    parser.add_argument("--provider", help="Override the provider for this Hermes invocation.")
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Maximum seconds allowed for the Hermes one-shot run (default: 300).",
    )
    return parser.parse_args()


def hermes_binary() -> Path:
    configured = os.environ.get("HERMES_CLI", "").strip()
    binary = Path(configured).expanduser() if configured else DEFAULT_HERMES_BIN
    if not binary.is_file():
        raise SystemExit(
            f"Hermes CLI not found at {binary}. Set HERMES_CLI to the executable path."
        )
    return binary.resolve()


def source_hermes_home() -> Path:
    configured = (
        os.environ.get("HERMES_SOURCE_HOME", "").strip()
        or os.environ.get("HERMES_HOME", "").strip()
    )
    return Path(configured).expanduser().resolve() if configured else Path.home() / ".hermes"


def resolve_model_settings(
    binary: Path, *, model_override: str | None, provider_override: str | None
) -> dict[str, str]:
    """Read non-secret routing data from the usable source Hermes profile."""

    environment = os.environ.copy()
    environment["HERMES_HOME"] = str(source_hermes_home())
    completed = subprocess.run(
        [str(binary), "config", "get", "model", "--json"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        env=environment,
    )
    configured: dict[str, Any] = {}
    if completed.returncode == 0:
        try:
            candidate = json.loads(completed.stdout)
            if isinstance(candidate, dict):
                configured = candidate
        except json.JSONDecodeError:
            configured = {}

    model = (
        model_override
        or os.environ.get("HERMES_EXERCISE_MODEL", "").strip()
        or str(configured.get("default") or "").strip()
    )
    provider = (
        provider_override
        or os.environ.get("HERMES_EXERCISE_PROVIDER", "").strip()
        or str(configured.get("provider") or "").strip()
    )
    if not model or not provider:
        diagnostic = completed.stderr.strip() or completed.stdout.strip()
        raise SystemExit(
            "Could not resolve a Hermes model and provider. Configure the source Hermes profile "
            "or pass both --model and --provider."
            + (f" Hermes reported: {diagnostic}" if diagnostic else "")
        )

    settings = {"model": model, "provider": provider}
    if not provider_override:
        for key in ("base_url", "api_mode"):
            value = configured.get(key)
            if isinstance(value, str) and value.strip():
                settings[key] = value.strip()
    return settings


def _yaml_string(value: str) -> str:
    """JSON strings are valid YAML strings and avoid hand-written escaping."""

    return json.dumps(value)


def _profile_config(model: dict[str, str]) -> str:
    base = (PROFILE_TEMPLATE / "config.yaml").read_text(encoding="utf-8").rstrip()
    lines = [base, "", "model:", f"  provider: {_yaml_string(model['provider'])}",
             f"  default: {_yaml_string(model['model'])}"]
    if model.get("base_url"):
        lines.append(f"  base_url: {_yaml_string(model['base_url'])}")
    if model.get("api_mode"):
        lines.append(f"  api_mode: {_yaml_string(model['api_mode'])}")
    return "\n".join(lines) + "\n"


def _copy_profile_credentials(source: Path, destination: Path) -> None:
    """Copy only credential inputs into an ephemeral profile that is deleted after the run."""

    relative_files = (
        ".env",
        "auth.json",
        ".anthropic_oauth.json",
        "shared/nous_auth.json",
    )
    for relative in relative_files:
        source_file = source / relative
        if not source_file.is_file():
            continue
        destination_file = destination / relative
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination_file)
        destination_file.chmod(0o600)


@contextmanager
def temporary_profile(
    *,
    mode: str,
    client_path: Path,
    trace_file: Path,
    model: dict[str, str],
    behavior_test: Path | None = None,
    test_result_file: Path | None = None,
) -> Iterator[tuple[Path, dict[str, str], Path]]:
    """Create an isolated Hermes profile without persisting copied credentials."""

    with tempfile.TemporaryDirectory(prefix="xyz-hermes-profile-") as temp_dir:
        profile = Path(temp_dir) / "profile"
        plugin_target = profile / "plugins" / "xyz-api-harness"
        plugin_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(PLUGIN_TEMPLATE, plugin_target)
        (profile / "config.yaml").write_text(_profile_config(model), encoding="utf-8")
        (profile / ".no-bundled-skills").touch()
        _copy_profile_credentials(source_hermes_home(), profile)

        usage_file = Path(temp_dir) / "usage.json"
        environment = os.environ.copy()
        environment.update(
            {
                "HERMES_HOME": str(profile),
                "HERMES_MAX_ITERATIONS": "24",
                "HERMES_VERIFY_ON_STOP": "0",
                "XYZ_HERMES_EXERCISE_DIR": str(HERMES_DIR),
                "XYZ_HERMES_MODE": mode,
                "XYZ_CLIENT_PATH": str(client_path.resolve()),
                "XYZ_TRACE_FILE": str(trace_file.resolve()),
            }
        )
        if mode == "fresh":
            selected_behavior_test = behavior_test or BEHAVIOR_TEST
            selected_result_file = test_result_file or TEST_RESULT_FILE
            environment.update(
                {
                    "XYZ_BEHAVIOR_TEST": str(selected_behavior_test.resolve()),
                    "XYZ_TEST_RESULT_FILE": str(selected_result_file.resolve()),
                }
            )
        yield profile, environment, usage_file


def _read_usage(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def _read_trace(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    events = []
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def invoke_hermes(
    *,
    binary: Path,
    mode: str,
    prompt: str,
    client_path: Path,
    trace_file: Path,
    model: dict[str, str],
    timeout: int,
    behavior_test: Path | None = None,
    test_result_file: Path | None = None,
    event_callback: Callable[[dict[str, Any]], None] | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> dict[str, Any]:
    with temporary_profile(
        mode=mode,
        client_path=client_path,
        trace_file=trace_file,
        model=model,
        behavior_test=behavior_test,
        test_result_file=test_result_file,
    ) as (_, environment, usage_file):
        command = [
            str(binary),
            "-z",
            prompt,
            "--usage-file",
            str(usage_file),
            "--in",
            str(HERMES_DIR),
            "--model",
            model["model"],
            "--provider",
            model["provider"],
            "--toolsets",
            "xyz-api-harness",
        ]
        if mode == "fresh":
            command.extend(["--skills", "xyz-api-harness:xyz-api-client"])
        if event_callback is None:
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                    env=environment,
                )
                returncode = completed.returncode
                stdout = completed.stdout.strip()
                stderr = completed.stderr.strip()
            except subprocess.TimeoutExpired as error:
                returncode = 124
                stdout = (error.stdout or "").strip()
                stderr = (
                    (error.stderr or "")
                    + f"\nHermes exceeded the {timeout}-second limit."
                ).strip()
        else:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=environment,
            )
            seen_events = len(_read_trace(trace_file))
            started_at = time.monotonic()
            deadline = time.monotonic() + timeout
            next_progress_at = 10
            try:
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        process.kill()
                        raw_stdout, raw_stderr = process.communicate()
                        returncode = 124
                        stdout = raw_stdout.strip()
                        stderr = (
                            raw_stderr
                            + f"\nHermes exceeded the {timeout}-second limit."
                        ).strip()
                        break
                    try:
                        raw_stdout, raw_stderr = process.communicate(
                            timeout=min(0.25, remaining)
                        )
                        returncode = process.returncode
                        stdout = raw_stdout.strip()
                        stderr = raw_stderr.strip()
                        break
                    except subprocess.TimeoutExpired:
                        current_events = _read_trace(trace_file)
                        for event in current_events[seen_events:]:
                            event_callback(event)
                        seen_events = len(current_events)
                        elapsed = int(time.monotonic() - started_at)
                        if (
                            progress_callback is not None
                            and elapsed >= next_progress_at
                        ):
                            progress_callback(elapsed, timeout)
                            next_progress_at += 10
            except KeyboardInterrupt:
                process.terminate()
                try:
                    process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                raise

            current_events = _read_trace(trace_file)
            for event in current_events[seen_events:]:
                event_callback(event)
        usage = _read_usage(usage_file)
    return {
        "returncode": returncode,
        "final_text": stdout,
        "stderr": stderr,
        "usage": usage,
    }


def run_smoke_test(
    *,
    binary: Path,
    model: dict[str, str],
    timeout: int = 300,
) -> dict[str, Any]:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    SMOKE_TRACE_FILE.write_text("", encoding="utf-8")
    print("\n==================================================")
    print("HERMES — LIVE BASELINE")
    print("==================================================")
    print(f"Model: {model['model']}")
    print(f"Client: {TASK_TEMPLATE.resolve()}")
    print("Required sequence: read client -> GET /health -> GET /api-docs -> final response")
    prompt = (
        "Check that this Hermes model/tool loop works before production controls are connected. "
        "Perform these read-only operations in order, with exactly one tool call in each model "
        "response: (1) read_file on the assigned incomplete client at "
        f"{TASK_TEMPLATE.resolve()}, (2) http_get on http://localhost:8080/health, then "
        "(3) http_get on http://localhost:8080/api-docs. Read each result before continuing. "
        "After all three operations succeed, reply exactly HARNESS_OK. Do not write any file."
    )
    invocation = invoke_hermes(
        binary=binary,
        mode="smoke",
        prompt=prompt,
        client_path=TASK_TEMPLATE,
        trace_file=SMOKE_TRACE_FILE,
        model=model,
        timeout=timeout,
    )
    events = _read_trace(SMOKE_TRACE_FILE)
    baseline_events = [event for event in events if event.get("event") == "baseline_call"]
    operations = [event["operation"] for event in baseline_events if event.get("accepted") is True]
    cycles = invocation["usage"].get("api_calls")
    for event in baseline_events:
        print(f"\n--- BASELINE CYCLE {event['cycle']} ---")
        print(f"AGENT REQUESTED TOOL: {event['tool']}")
        print(f"TOOL ARGUMENTS: {json.dumps(event['arguments'], sort_keys=True)}")
        print("TOOL RESULT:")
        print(json.dumps(event["result"], indent=2, sort_keys=True))
    if invocation["final_text"]:
        print(f"\n--- BASELINE CYCLE {cycles} ---")
        print("AGENT TEXT:")
        print(invocation["final_text"])
    passed = (
        invocation["returncode"] == 0
        and bool(invocation["final_text"])
        and operations
        == ["read_incomplete_client", "check_api_health", "retrieve_api_docs"]
        and isinstance(cycles, int)
        and cycles >= 4
    )
    record = {
        "harness": "hermes",
        "model": model["model"],
        "provider": model["provider"],
        "passed": passed,
        "status": "completed" if passed else "failed",
        "cycles": cycles,
        "completed_operations": operations,
        "final_text": invocation["final_text"],
        "returncode": invocation["returncode"],
        "events": baseline_events,
        "usage": invocation["usage"],
    }
    if invocation["stderr"]:
        record["diagnostic"] = invocation["stderr"]
    SMOKE_FILE.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("\n================ BASELINE SUMMARY ================")
    print(f"Model cycles:   {cycles}")
    print(f"Operations:     {operations}")
    print(f"Status:         {'COMPLETED' if passed else 'FAILED'}")
    return record


def prepare_fresh_workspace() -> None:
    CLIENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TASK_TEMPLATE, CLIENT_FILE)
    TRACE_FILE.write_text("", encoding="utf-8")
    TEST_RESULT_FILE.write_text("", encoding="utf-8")


def _print_fresh_start(*, model: dict[str, str]) -> None:
    print("\n==================================================", flush=True)
    print("HERMES — CONFIGURED CLIENT IMPLEMENTATION RUN", flush=True)
    print("==================================================", flush=True)
    print(f"Model:           {model['model']}", flush=True)
    print(f"Provider:        {model['provider']}", flush=True)
    print(f"Assigned client: {CLIENT_FILE.resolve()}", flush=True)
    print("Waiting for the first Hermes model response...", flush=True)


def _print_fresh_event(event: dict[str, Any]) -> None:
    event_name = event.get("event")
    if event_name == "skill_registered":
        print("\nSKILL REGISTERED", flush=True)
        print(f"Name:        {event.get('skill')}", flush=True)
        print(f"Description: {event.get('description')}", flush=True)
    elif event_name == "skill_loaded":
        print("\nSKILL LOADED INTO MODEL CONTEXT", flush=True)
        print(f"Name:   {event.get('skill')}", flush=True)
        print(f"Source: {event.get('source')}", flush=True)
    elif event_name == "permission_decision":
        print("\n--- HERMES TOOL REQUEST ---", flush=True)
        print(f"Tool: {event.get('requested_capability')}", flush=True)
        print("Arguments:", flush=True)
        print(
            json.dumps(event.get("arguments", {}), indent=2, sort_keys=True),
            flush=True,
        )
        print(f"Permission: {str(event.get('decision', '')).upper()}", flush=True)
        print(f"Rule:       {event.get('matching_rule')}", flush=True)
        print(f"Reason:     {event.get('reason')}", flush=True)
    elif event_name == "hook":
        print(f"HOOK: {event.get('hook')}", flush=True)
        print(
            f"Result: {'PASSED' if event.get('allowed') else 'BLOCKED'}",
            flush=True,
        )
        print(f"Reason: {event.get('reason')}", flush=True)
    elif event_name == "tool_result":
        result = event.get("result", {})
        executed = result.get("executed") if isinstance(result, dict) else None
        if executed is True:
            label = "TOOL EXECUTED"
        elif executed is False:
            label = "TOOL NOT EXECUTED"
        else:
            label = "TOOL RESULT RETURNED"
        status = "not reported"
        if isinstance(result, dict):
            status = result.get("status") or result.get("action") or status
        print(f"{label}: {event.get('tool')}", flush=True)
        print(f"Status: {status}", flush=True)
    elif event_name == "completion":
        print("\n--- HERMES COMPLETION CHECK ---", flush=True)
        print(f"Status: {str(event.get('status', '')).upper()}", flush=True)


def _print_fresh_wait(elapsed: int, timeout: int) -> None:
    print(
        f"WAITING FOR MODEL: {elapsed}s elapsed; timeout is {timeout}s",
        flush=True,
    )


def run_fresh(
    *,
    binary: Path,
    model: dict[str, str],
    timeout: int = 300,
) -> dict[str, Any]:
    from hermes.components.hooks import CompletionHook, RunTrace

    prepare_fresh_workspace()
    _print_fresh_start(model=model)
    invocation = invoke_hermes(
        binary=binary,
        mode="fresh",
        prompt=f"ASSIGNED CLIENT FILE\n{CLIENT_FILE.resolve()}\n\nTASK\n{TASK}",
        client_path=CLIENT_FILE,
        trace_file=TRACE_FILE,
        model=model,
        timeout=timeout,
        event_callback=_print_fresh_event,
        progress_callback=_print_fresh_wait,
    )
    completion = CompletionHook(BEHAVIOR_TEST, TEST_RESULT_FILE).check(CLIENT_FILE)
    trace = RunTrace(TRACE_FILE)
    trace.record("usage", usage=invocation["usage"])
    passed = (
        invocation["returncode"] == 0
        and bool(invocation["final_text"])
        and completion.allowed
    )
    trace.record(
        "completion",
        status="completed" if passed else "failed",
        source="runner_final_check",
        reason=completion.reason,
    )
    return {
        "status": "completed" if passed else "failed",
        "final_text": invocation["final_text"],
        "returncode": invocation["returncode"],
        "model": model["model"],
        "provider": model["provider"],
        "usage": invocation["usage"],
        "tests_passed": completion.allowed,
        "diagnostic": invocation["stderr"],
    }


def main() -> None:
    args = parse_args()
    binary = hermes_binary()
    model = resolve_model_settings(
        binary,
        model_override=args.model,
        provider_override=args.provider,
    )
    if args.smoke_test:
        result = run_smoke_test(binary=binary, model=model, timeout=args.timeout)
        if not result["passed"]:
            raise SystemExit(f"Hermes smoke test failed: {json.dumps(result, indent=2)}")
        print("HARNESS_OK")
        return

    result = run_fresh(binary=binary, model=model, timeout=args.timeout)
    print("\n================ FRESH RUN SUMMARY ================")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key != "diagnostic"},
            indent=2,
        )
    )
    if result["status"] != "completed":
        if result["diagnostic"]:
            print(result["diagnostic"])
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(
            "\nHermes run interrupted. No result was accepted. "
            "Rerun with --fresh to start again.",
            file=sys.stderr,
        )
        raise SystemExit(130)
