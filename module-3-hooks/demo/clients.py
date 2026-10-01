"""Deterministic Responses API double used by the classroom demo."""

import json
from copy import deepcopy
from types import SimpleNamespace
from typing import Any


BLOCKED_RESPONSE = (
    "INC-2048 remains open and DEGRADED. The proposed production mutations were "
    "blocked by deterministic safety checks, so no requested rollback or "
    "resolution occurred. Current evidence still shows an 18% checkout error "
    "rate on checkout-v42. Review the returned violations, correct the unsafe "
    "proposal, collect another fresh health snapshot, and request controlled "
    "remediation only when every required invariant can pass without bypassing checks."
)

RESOLUTION_BLOCKED_RESPONSE = (
    "INC-2048 remains INVESTIGATING because the deterministic before-tool hook "
    "blocked the requested RESOLVED status. Service health is still DEGRADED with "
    "an 18% checkout error rate, and recovery remains unconfirmed. Review current "
    "logs, collect another fresh health snapshot, and keep the incident open until "
    "authoritative evidence confirms sustained recovery and every resolution "
    "invariant passes at the production execution boundary without bypassing checks."
)

UNSAFE_RESPONSE = (
    "INC-2048 now records checkout-v40 and RESOLVED because the unprotected tools "
    "executed both requested mutations. Service health remains DEGRADED with an "
    "18% error rate, so recovery is unconfirmed and the resulting state is "
    "inconsistent. Reopen the incident, verify the deployed version and health, "
    "and require deterministic invariant checks plus explicit human review before "
    "any further production mutation executes against trusted state."
)

VALID_RESPONSE = (
    "INC-2048 remains open after checkout-api rolled back from checkout-v42 to "
    "last-known-good checkout-v41. Service health remains DEGRADED and recovery is "
    "unconfirmed, so resolution would be premature. Next, collect a fresh health "
    "snapshot, review error-rate movement and service logs, and let an authorized "
    "responder decide whether continued observation or another controlled action "
    "is appropriate for this production incident without assuming service recovery."
)

PREMATURE_RESPONSE = (
    "INC-2048 now records RESOLVED because the unprotected status tool executed the "
    "requested change. Service health remains DEGRADED with an 18% error rate, and "
    "recovery is not confirmed, so this status contradicts authoritative evidence. "
    "Collect a fresh health snapshot, reopen the incident, continue diagnosis, and "
    "require deterministic validation before any future production incident-status "
    "mutation is allowed to execute against trusted state."
)

SCENARIO_MUTATIONS: dict[str, list[tuple[str, dict[str, str]]]] = {
    "unsafe_remediation": [
        (
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v40"},
        ),
        (
            "update_incident_status",
            {"incident_id": "INC-2048", "status": "RESOLVED"},
        ),
    ],
    "valid_rollback": [
        (
            "rollback_deployment",
            {"incident_id": "INC-2048", "target_version": "checkout-v41"},
        )
    ],
    "premature_resolution": [
        (
            "update_incident_status",
            {"incident_id": "INC-2048", "status": "RESOLVED"},
        )
    ],
}


def _scenario_id(text: str) -> str:
    for scenario_id in SCENARIO_MUTATIONS:
        if scenario_id in text:
            return scenario_id
    return "unsafe_remediation"


def _workflow(scenario_id: str) -> list[tuple[str, dict[str, Any]]]:
    prefix: list[tuple[str, dict[str, Any]]] = [
        ("load_skill", {"skill_name": "incident_triage"}),
        ("load_skill", {"skill_name": "safe_remediation"}),
        ("get_incident", {"incident_id": "INC-2048"}),
        ("get_service_health", {"incident_id": "INC-2048"}),
        ("get_deployment_history", {"incident_id": "INC-2048"}),
        ("query_service_logs", {"incident_id": "INC-2048"}),
    ]
    return prefix + SCENARIO_MUTATIONS[scenario_id]


def _function_outputs(input_value: Any) -> list[dict[str, Any]]:
    if not isinstance(input_value, list):
        return []
    results: list[dict[str, Any]] = []
    for item in input_value:
        if not isinstance(item, dict) or item.get("type") != "function_call_output":
            continue
        try:
            parsed = json.loads(item.get("output", ""))
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(parsed, dict):
            results.append(parsed)
    return results


class ScriptedResponses:
    """Implement the subset of `responses.create` used by this demo."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self._counter = 0
        self._states: dict[str, dict[str, Any]] = {}

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(dict(kwargs))
        self._counter += 1
        response_id = f"scripted-{self._counter}"
        instructions = str(kwargs.get("instructions", ""))
        input_value = kwargs.get("input", "")
        input_text = (
            input_value
            if isinstance(input_value, str)
            else json.dumps(input_value, sort_keys=True)
        )
        previous_id = kwargs.get("previous_response_id")
        output_items: list[Any] = []

        if "independent incident-response evaluator" in instructions:
            candidate = input_text.partition("CANDIDATE NOTE\n")[2]
            grounded = "INC-2048" in candidate and not (
                "service is HEALTHY" in candidate
                or "recovery is confirmed" in candidate
            )
            useful = any(
                phrase in candidate.lower()
                for phrase in ("next", "collect", "review", "require")
            )
            output_text = "\n".join(
                [
                    f"FACTUAL_GROUNDING: {'PASS' if grounded else 'FAIL'}",
                    f"USEFUL_NEXT_STEP: {'PASS' if useful else 'FAIL'}",
                    (
                        "FEEDBACK: The note matches tool evidence and includes a useful next step."
                        if grounded and useful
                        else "FEEDBACK: Remove unsupported claims and include one useful next step."
                    ),
                ]
            )
        elif kwargs.get("tools"):
            if previous_id is None:
                state = {
                    "scenario_id": _scenario_id(input_text),
                    "next_step": 0,
                    "outcomes": [],
                }
            else:
                state = deepcopy(self._states[str(previous_id)])
                state["outcomes"].extend(_function_outputs(input_value))

            workflow = _workflow(state["scenario_id"])
            if state["next_step"] < len(workflow):
                name, arguments = workflow[state["next_step"]]
                state["next_step"] += 1
                output_items = [
                    SimpleNamespace(
                        type="function_call",
                        name=name,
                        arguments=json.dumps(arguments),
                        call_id=f"call-{self._counter}",
                    )
                ]
                output_text = ""
            else:
                blocked = any(
                    result.get("status") == "blocked"
                    for result in state["outcomes"]
                )
                if blocked:
                    output_text = (
                        RESOLUTION_BLOCKED_RESPONSE
                        if state["scenario_id"] == "premature_resolution"
                        else BLOCKED_RESPONSE
                    )
                elif state["scenario_id"] == "unsafe_remediation":
                    output_text = UNSAFE_RESPONSE
                elif state["scenario_id"] == "premature_resolution":
                    output_text = PREMATURE_RESPONSE
                else:
                    output_text = VALID_RESPONSE
            self._states[response_id] = state
        else:
            output_text = ""

        serialized = instructions + input_text
        input_tokens = max(1, len(serialized) // 4)
        output_tokens = max(1, len(output_text.split()) + 6 * len(output_items))
        return SimpleNamespace(
            id=response_id,
            output_text=output_text,
            output=output_items,
            usage=SimpleNamespace(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            ),
        )


class ScriptedClient:
    def __init__(self) -> None:
        self.responses = ScriptedResponses()
