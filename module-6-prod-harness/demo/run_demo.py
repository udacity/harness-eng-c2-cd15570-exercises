"""Launch the incident-response plugin through the real Hermes CLI."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
from typing import Any, Iterator
from urllib.parse import urlparse

from components.hooks import CompletionHook, HookDecision, RunTrace
from data import SCENARIOS, fresh_incident, scenario, task_prompt


BASE_DIR = Path(__file__).resolve().parent
PROFILE_TEMPLATE = BASE_DIR / ".hermes"
RUNS_DIR = BASE_DIR / "runs"
STATE_FILE = RUNS_DIR / "incident.json"
TRACE_FILE = RUNS_DIR / "run.jsonl"
USAGE_FILE = RUNS_DIR / "usage.json"
RESULT_FILE = RUNS_DIR / "run-result.json"
DEFAULT_HERMES_BIN = Path("/Users/peter/.local/bin/hermes")
VOCAREUM_HOST = "openai.vocareum.com"
VOCAREUM_MODEL = "gpt-4.1-mini"
VOCAREUM_API_MODE = "chat_completions"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scenario", choices=SCENARIOS, nargs="?", default="safe-rollback"
    )
    parser.add_argument("--model", help="Override the configured Hermes model.")
    parser.add_argument("--provider", help="Override the configured Hermes provider.")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved Hermes CLI command without making a model call.",
    )
    return parser.parse_args()


def hermes_binary() -> Path:
    configured = os.environ.get("HERMES_CLI", "").strip()
    discovered = shutil.which("hermes")
    candidate = (
        Path(configured).expanduser()
        if configured
        else Path(discovered)
        if discovered
        else DEFAULT_HERMES_BIN
    )
    if not candidate.is_file():
        raise SystemExit(
            "Hermes CLI was not found. Install Hermes or set HERMES_CLI to its executable."
        )
    return candidate.resolve()


def source_hermes_home() -> Path:
    configured = (
        os.environ.get("HERMES_SOURCE_HOME", "").strip()
        or os.environ.get("HERMES_HOME", "").strip()
    )
    return (
        Path(configured).expanduser().resolve()
        if configured
        else Path.home() / ".hermes"
    )


def resolve_model(
    binary: Path, model_override: str | None, provider_override: str | None
) -> dict[str, str]:
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
            value = json.loads(completed.stdout)
            if isinstance(value, dict):
                configured = value
        except json.JSONDecodeError:
            pass
    model = model_override or str(configured.get("default") or "").strip()
    provider = provider_override or str(configured.get("provider") or "").strip()
    if not model or not provider:
        raise SystemExit(
            "Configure a Hermes model/provider or pass both --model and --provider."
        )
    resolved = {"model": model, "provider": provider}
    if provider_override is None:
        for key in ("base_url", "api_mode"):
            if isinstance(configured.get(key), str) and configured[key].strip():
                resolved[key] = configured[key].strip()
    _validate_course_model_route(resolved)
    return resolved


def _validate_course_model_route(settings: dict[str, str]) -> None:
    """Reject the known-incompatible default wire mode before a provider call."""

    hostname = (urlparse(settings.get("base_url", "")).hostname or "").lower()
    model = settings.get("model", "").strip().lower().rsplit("/", 1)[-1]
    is_course_model = model == VOCAREUM_MODEL or model.startswith(
        f"{VOCAREUM_MODEL}-"
    )
    if (
        hostname == VOCAREUM_HOST
        and is_course_model
        and settings.get("api_mode", "").strip().lower() != VOCAREUM_API_MODE
    ):
        raise SystemExit(
            "The Vocareum gpt-4.1-mini route requires Hermes API mode "
            "chat_completions. Configure the source Hermes profile before "
            "running the demo:\n"
            "  hermes config set model.api_mode chat_completions\n"
            "Then verify it with:\n"
            "  hermes config get model --json"
        )


def _profile_config(model: dict[str, str]) -> str:
    base = (PROFILE_TEMPLATE / "config.yaml").read_text(encoding="utf-8").rstrip()
    lines = [
        base,
        "",
        "model:",
        f"  provider: {json.dumps(model['provider'])}",
        f"  default: {json.dumps(model['model'])}",
    ]
    if model.get("base_url"):
        lines.append(f"  base_url: {json.dumps(model['base_url'])}")
    if model.get("api_mode"):
        lines.append(f"  api_mode: {json.dumps(model['api_mode'])}")
    return "\n".join(lines) + "\n"


def _copy_credentials(source: Path, destination: Path) -> None:
    for relative in (
        ".env",
        "auth.json",
        ".anthropic_oauth.json",
        "shared/nous_auth.json",
    ):
        source_file = source / relative
        if not source_file.is_file():
            continue
        destination_file = destination / relative
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination_file)
        destination_file.chmod(0o600)


@contextmanager
def temporary_profile(model: dict[str, str]) -> Iterator[tuple[Path, dict[str, str]]]:
    with tempfile.TemporaryDirectory(prefix="incident-hermes-profile-") as directory:
        profile = Path(directory) / "profile"
        plugin_target = profile / "plugins" / "incident-response-demo"
        plugin_target.parent.mkdir(parents=True)
        shutil.copytree(
            PROFILE_TEMPLATE / "plugins" / "incident-response-demo", plugin_target
        )
        (profile / "config.yaml").write_text(
            _profile_config(model), encoding="utf-8"
        )
        (profile / ".no-bundled-skills").touch()
        _copy_credentials(source_hermes_home(), profile)
        environment = os.environ.copy()
        environment.update(
            {
                "HERMES_HOME": str(profile),
                "INCIDENT_DEMO_DIR": str(BASE_DIR),
                "INCIDENT_DEMO_STATE": str(STATE_FILE),
                "INCIDENT_DEMO_TRACE": str(TRACE_FILE),
            }
        )
        yield profile, environment


def build_command(
    binary: Path,
    *,
    prompt: str,
    model: dict[str, str],
    usage_file: Path = USAGE_FILE,
) -> list[str]:
    return [
        str(binary),
        "-z",
        prompt,
        "--usage-file",
        str(usage_file),
        "--in",
        str(BASE_DIR),
        "--model",
        model["model"],
        "--provider",
        model["provider"],
        "--toolsets",
        "incident-response-demo",
        "--skills",
        "incident-response-demo:incident_triage,incident-response-demo:safe_remediation",
    ]


def _prepare_run() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(fresh_incident(), indent=2) + "\n", encoding="utf-8")
    TRACE_FILE.write_text("", encoding="utf-8")
    USAGE_FILE.write_text("{}\n", encoding="utf-8")
    RESULT_FILE.write_text("{}\n", encoding="utf-8")


def _events(trace_file: Path = TRACE_FILE) -> list[dict[str, Any]]:
    events = []
    for line in trace_file.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events


def _postflight_decision(
    scenario_name: str,
    *,
    state_file: Path = STATE_FILE,
    trace_file: Path = TRACE_FILE,
) -> HookDecision:
    incident = json.loads(state_file.read_text(encoding="utf-8"))
    events = _events(trace_file)
    decision = CompletionHook().check(scenario(scenario_name), incident, events)
    trace = RunTrace(trace_file)
    trace.record("postflight_decision", source="runner", **decision.to_dict())
    if decision.allowed and not any(
        event.get("event") == "completion"
        and event.get("status") == "completed"
        for event in events
    ):
        trace.record(
            "completion",
            status="completed",
            source="runner_postflight",
            final_deployment=incident["current_deployment"],
        )
    return decision


def _effective_exit_code(hermes_returncode: int, completed: bool) -> int:
    if hermes_returncode != 0:
        return hermes_returncode
    return 0 if completed else 1


def _print_summary(
    scenario_name: str,
    hermes_returncode: int,
    demo_exit_code: int,
    decision: HookDecision,
) -> None:
    incident = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    events = _events()
    permission_denials = sum(
        event.get("event") == "permission_decision"
        and event.get("decision") == "deny"
        for event in events
    )
    hook_blocks = sum(
        event.get("event") == "hook_decision"
        and event.get("allowed") is False
        and event.get("hook") != "completion_verification"
        for event in events
    )
    record = {
        "scenario": scenario_name,
        "hermes_returncode": hermes_returncode,
        "demo_exit_code": demo_exit_code,
        "completed": decision.allowed,
        "completion_reason": decision.reason,
        "final_deployment": incident["current_deployment"],
        "permission_denials": permission_denials,
        "hook_blocks": hook_blocks,
        "trace_events": len(events),
    }
    RESULT_FILE.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("\n================ HERMES RUN SUMMARY ================")
    for key, value in record.items():
        print(f"{key:20} {value}")
    print(f"trace                {TRACE_FILE}")
    print(f"usage                {USAGE_FILE}")


def main() -> None:
    args = parse_args()
    if args.timeout <= 0:
        raise SystemExit("--timeout must be positive.")
    binary = hermes_binary()
    model = resolve_model(binary, args.model, args.provider)
    prompt = task_prompt(args.scenario)
    command = build_command(binary, prompt=prompt, model=model)
    display_command = list(command)
    display_command[2] = "<incident-task-prompt>"
    print("Hermes CLI command:")
    print(shlex.join(display_command))
    print(f"Scenario: {args.scenario}")
    print(f"Model: {model['model']} | Provider: {model['provider']}")
    if args.dry_run:
        return

    _prepare_run()
    with temporary_profile(model) as (_, environment):
        environment["INCIDENT_DEMO_SCENARIO"] = args.scenario
        try:
            completed = subprocess.run(
                command,
                env=environment,
                timeout=args.timeout,
                check=False,
            )
            returncode = completed.returncode
        except subprocess.TimeoutExpired:
            returncode = 124
            print(f"Hermes exceeded the {args.timeout}-second limit.")
    decision = _postflight_decision(args.scenario)
    exit_code = _effective_exit_code(returncode, decision.allowed)
    _print_summary(args.scenario, returncode, exit_code, decision)
    if exit_code != 0:
        raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
