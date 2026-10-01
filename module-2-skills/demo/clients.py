"""Deterministic Responses API double used by the classroom demo."""

import json
from types import SimpleNamespace
from typing import Any


DIAGNOSIS_RESPONSE = (
    "INC-2048 remains open. Confirmed facts show checkout-api is DEGRADED with "
    "an 18% error rate while checkout-v42 remains deployed. No restart or "
    "rollback has occurred, and recovery is not confirmed. Next, inspect current "
    "health, deployment history, and service logs before an authorized responder "
    "selects remediation. Tell stakeholders that checkout impact continues and "
    "that the investigation remains active until evidence confirms recovery."
)

STAKEHOLDER_RESPONSE = (
    "INC-2048 remains under investigation. The production checkout-api is "
    "DEGRADED, with an 18% checkout error rate while checkout-v42 remains "
    "deployed. No restart, rollback, or recovery is confirmed. Customers may "
    "still experience checkout failures. The team is reviewing current health, "
    "deployment history, and service logs. Stakeholders will receive another "
    "update after evidence clarifies the safest next action for this active "
    "production incident."
)

FULL_RESPONSE = (
    "INC-2048 remains open: production checkout-api is DEGRADED with an 18% "
    "error rate while checkout-v42 is active. No remediation or recovery is "
    "confirmed. Next, inspect health, deployment history, and logs to test the "
    "deployment hypothesis. An authorized responder should then choose one "
    "controlled action and verify health. Tell stakeholders that checkout impact "
    "and investigation continue until evidence confirms sustained service recovery."
)

RESPONSES = {
    "checkout_diagnosis": DIAGNOSIS_RESPONSE,
    "stakeholder_update": STAKEHOLDER_RESPONSE,
    "incident_response": FULL_RESPONSE,
}

EXPECTED_SKILLS = {
    "checkout_diagnosis": ["incident_triage", "checkout_service_runbook"],
    "stakeholder_update": ["incident_communications"],
    "incident_response": [
        "incident_triage",
        "checkout_service_runbook",
        "safe_remediation",
        "incident_communications",
    ],
}


def _request_id(text: str) -> str:
    for request_id in RESPONSES:
        if request_id in text:
            return request_id
    return "checkout_diagnosis"


class ScriptedResponses:
    """Implement the subset of `responses.create` used by this demo."""

    def __init__(self, forced_skills: list[str] | None = None) -> None:
        self.calls: list[dict[str, Any]] = []
        self._counter = 0
        self._forced_skills = forced_skills
        self._conversation_requests: dict[str, str] = {}

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(dict(kwargs))
        self._counter += 1
        response_id = f"scripted-{self._counter}"
        instructions = str(kwargs.get("instructions", ""))
        input_value = kwargs.get("input", "")
        input_text = json.dumps(input_value, sort_keys=True) if not isinstance(
            input_value, str
        ) else input_value
        previous_id = kwargs.get("previous_response_id")
        request_id = (
            self._conversation_requests.get(str(previous_id), "")
            if previous_id
            else _request_id(input_text)
        )
        output_items: list[Any] = []

        if "independent incident-response evaluator" in instructions:
            candidate = input_text.partition("CANDIDATE NOTE\n")[2]
            grounded = not any(
                phrase in candidate.lower()
                for phrase in ("is resolved", "we rolled", "restored healthy")
            )
            useful = any(
                phrase in candidate.lower()
                for phrase in ("next", "reviewing current health", "inspect health")
            )
            output_text = "\n".join(
                [
                    f"FACTUAL_GROUNDING: {'PASS' if grounded else 'FAIL'}",
                    f"USEFUL_NEXT_STEP: {'PASS' if useful else 'FAIL'}",
                    "FEEDBACK: The note is grounded and includes a useful next step."
                    if grounded and useful
                    else "FEEDBACK: Remove unsupported outcomes and add a diagnostic next step.",
                ]
            )
        elif kwargs.get("tools"):
            skills = (
                list(self._forced_skills)
                if self._forced_skills is not None
                else EXPECTED_SKILLS[request_id]
            )
            output_items = [
                SimpleNamespace(
                    type="function_call",
                    name="load_skill",
                    arguments=json.dumps({"skill_name": name}),
                    call_id=f"skill-{index}",
                )
                for index, name in enumerate(skills, start=1)
            ]
            output_text = ""
        else:
            output_text = RESPONSES[request_id]

        self._conversation_requests[response_id] = request_id
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
    def __init__(self, forced_skills: list[str] | None = None) -> None:
        self.responses = ScriptedResponses(forced_skills)
