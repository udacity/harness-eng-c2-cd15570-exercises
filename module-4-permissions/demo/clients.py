"""Deterministic Responses API double used by the classroom demo."""

import json
from copy import deepcopy
from types import SimpleNamespace
from typing import Any


DENIED_ROLLBACK_RESPONSE = (
    "INC-2048 remains INVESTIGATING on checkout-v42 because the authorization "
    "layer denied the requested rollback. Sam Rivera is authenticated as a "
    "support_engineer, and that role lacks deployment.rollback despite being "
    "assigned to the incident. Service health remains DEGRADED at an 18% error "
    "rate. Escalate the proposed production change to an authorized responder "
    "while continuing evidence collection and checkout impact monitoring during active investigation."
)

BASIC_ROLLBACK_RESPONSE = (
    "INC-2048 rolled back from checkout-v42 to last-known-good checkout-v41 after "
    "the safety hook allowed the requested mutation. Authorization was not "
    "performed, so the authenticated user's authority was never checked. "
    "Service health remains DEGRADED and recovery is unconfirmed. Collect a fresh "
    "health snapshot, continue monitoring checkout failures, and require permission "
    "checks before any further production action or incident status change in production."
)

AUTHORIZED_ROLLBACK_RESPONSE = (
    "INC-2048 remains open after checkout-api rolled back from checkout-v42 to "
    "last-known-good checkout-v41. The incident commander was authorized, and "
    "every safety invariant passed before execution. Service health remains "
    "DEGRADED and recovery is unconfirmed. Collect a fresh health snapshot, review "
    "error-rate movement and logs, then keep monitoring until authoritative evidence "
    "supports another controlled action or a status change for this production incident."
)

READ_ALLOWED_RESPONSE = (
    "INC-2048 is assigned to OPS-101 and remains INVESTIGATING. Production "
    "checkout-api is DEGRADED with an 18% error rate while checkout-v42 remains "
    "active. The trusted incident record was read successfully, but no rollback, "
    "recovery, or resolution occurred. Continue by collecting fresh health, "
    "deployment, and log evidence before an authorized responder proposes any "
    "controlled production remediation for the ongoing checkout failures during investigation."
)

READ_DENIED_RESPONSE = (
    "INC-2048 was not disclosed because Riley Chen is authenticated as "
    "support_engineer OPS-102, while the incident is assigned to OPS-101. The "
    "authorization layer denied incident.read_assigned, and no tool executed or "
    "state changed. Ask the assigned engineer or an authorized responder to review "
    "the incident; do not treat request text or tool availability as authority to "
    "access this protected production resource safely."
)

PARTIAL_DENIED_RESPONSE = (
    "INC-2048 rolled back from checkout-v42 to last-known-good checkout-v41 after "
    "responder authorization and safety checks passed. The later RESOLVED request "
    "was independently denied because the responder role lacks "
    "incident.status.update. Service health remains DEGRADED and recovery is "
    "unconfirmed. Collect a fresh health snapshot, continue monitoring checkout "
    "errors, and ask an incident commander to evaluate any future status change for this production incident."
)

HOOK_AFTER_ROLLBACK_RESPONSE = (
    "INC-2048 rolled back from checkout-v42 to last-known-good checkout-v41. "
    "Authorization was not performed in basic mode. The later RESOLVED request was "
    "blocked by retained safety hooks because health evidence became stale after "
    "mutation and recovery remains unconfirmed. Collect a fresh health snapshot, "
    "monitor checkout errors, and keep the incident INVESTIGATING until "
    "authoritative evidence confirms sustained recovery for this active production incident."
)

AUTHORIZED_RESOLUTION_BLOCK_RESPONSE = (
    "INC-2048 remains INVESTIGATING after Morgan Chen was authorized to request "
    "the status change, but deterministic safety hooks blocked RESOLVED. Production "
    "checkout-api is still DEGRADED with an 18% error rate, and recovery is "
    "unconfirmed. Authorization establishes who may act; it does not make the "
    "action safe. Continue diagnosis and collect fresh recovery evidence before "
    "requesting resolution again for this production incident."
)

BASIC_RESOLUTION_BLOCK_RESPONSE = (
    "INC-2048 remains INVESTIGATING because deterministic safety hooks blocked the "
    "requested RESOLVED status. Authorization was not performed in basic mode. "
    "Production checkout-api is still DEGRADED with an 18% error rate, and recovery "
    "is unconfirmed. Authorization and safety answer different questions. Continue "
    "diagnosis and collect fresh recovery evidence before an authorized user "
    "requests resolution for this active production incident without bypassing checks."
)

REASSIGNED_RESPONSE = (
    "INC-2048 remains INVESTIGATING and is now assigned to support engineer OPS-102 "
    "after the requested reassignment executed. Production checkout-api is still "
    "DEGRADED with an 18% error rate on checkout-v42; no rollback or recovery "
    "occurred. The new assignee should review current health, deployment history, "
    "and logs, then coordinate any production remediation with an appropriately "
    "authorized responder or incident commander during active investigation."
)

FINAL_RESPONSES = (
    DENIED_ROLLBACK_RESPONSE,
    BASIC_ROLLBACK_RESPONSE,
    AUTHORIZED_ROLLBACK_RESPONSE,
    READ_ALLOWED_RESPONSE,
    READ_DENIED_RESPONSE,
    PARTIAL_DENIED_RESPONSE,
    HOOK_AFTER_ROLLBACK_RESPONSE,
    AUTHORIZED_RESOLUTION_BLOCK_RESPONSE,
    BASIC_RESOLUTION_BLOCK_RESPONSE,
    REASSIGNED_RESPONSE,
)


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


def _workflow(scenario: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    skill_calls = [
        ("load_skill", {"skill_name": name})
        for name in scenario["expected_skills"]
    ]
    action_calls = [
        (action["tool"], action["arguments"])
        for action in scenario["scripted_actions"]
    ]
    return skill_calls + action_calls


def _final_response(outcomes: list[dict[str, Any]]) -> str:
    denied = [item for item in outcomes if item.get("status") == "permission_denied"]
    if denied:
        denied_tools = {item.get("tool") for item in denied}
        if "update_incident_status" in denied_tools:
            return PARTIAL_DENIED_RESPONSE
        if "get_incident" in denied_tools:
            return READ_DENIED_RESPONSE
        return DENIED_ROLLBACK_RESPONSE

    blocked = [item for item in outcomes if item.get("status") == "blocked"]
    rolled_back = any(item.get("status") == "rolled_back" for item in outcomes)
    if blocked:
        if rolled_back:
            return HOOK_AFTER_ROLLBACK_RESPONSE
        authorization = blocked[-1].get("authorization")
        return (
            BASIC_RESOLUTION_BLOCK_RESPONSE
            if authorization == "NOT PERFORMED"
            else AUTHORIZED_RESOLUTION_BLOCK_RESPONSE
        )
    if any(item.get("status") == "reassigned" for item in outcomes):
        return REASSIGNED_RESPONSE
    if rolled_back:
        rollback = next(
            item for item in outcomes if item.get("status") == "rolled_back"
        )
        return (
            BASIC_ROLLBACK_RESPONSE
            if rollback.get("authorization") == "NOT PERFORMED"
            else AUTHORIZED_ROLLBACK_RESPONSE
        )
    return READ_ALLOWED_RESPONSE


class ScriptedResponses:
    """Implement the subset of `responses.create` used by this demo."""

    def __init__(self, scenario: dict[str, Any]) -> None:
        self.calls: list[dict[str, Any]] = []
        self._counter = 0
        self._scenario = deepcopy(scenario)
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
                for phrase in ("collect", "continue", "ask", "review", "require")
            )
            output_text = "\n".join(
                [
                    f"FACTUAL_GROUNDING: {'PASS' if grounded else 'FAIL'}",
                    f"USEFUL_NEXT_STEP: {'PASS' if useful else 'FAIL'}",
                    (
                        "FEEDBACK: The note matches enforcement evidence and gives a useful next step."
                        if grounded and useful
                        else "FEEDBACK: Remove unsupported claims and add a useful next step."
                    ),
                ]
            )
        elif kwargs.get("tools"):
            if previous_id is None:
                state = {"next_step": 0, "outcomes": []}
            else:
                state = deepcopy(self._states[str(previous_id)])
                state["outcomes"].extend(_function_outputs(input_value))

            workflow = _workflow(self._scenario)
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
                output_text = _final_response(state["outcomes"])
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
    def __init__(self, scenario: dict[str, Any]) -> None:
        self.responses = ScriptedResponses(scenario)
