"""Scripted and live model providers for the evaluator demo."""

from __future__ import annotations

import time
from typing import Any, Protocol

from harness.models import ModelReply, Scenario
from harness.scenario import authoritative_context, requirements_context


GENERATOR_INSTRUCTIONS = """
You are an incident-response communications assistant. Draft an accurate update
using only the authoritative incident facts. Distinguish confirmed facts from
hypotheses, do not claim an action or recovery that has not occurred, and give
a useful next diagnostic step. Return only the incident update.
""".strip()

REVISION_INSTRUCTIONS = """
You are an incident-response communications assistant. Revise the previous
update using the supplied evaluation feedback and authoritative facts. Correct
every identified problem. Return only the revised incident update.
""".strip()

SELF_EVALUATOR_INSTRUCTIONS = """
Review the incident update you just wrote against the authoritative facts and
all response requirements. You are evaluating your own response in the same
conversation.

Return exactly these six lines:
INCIDENT_ID: PASS or FAIL
LENGTH: PASS or FAIL
FACTUAL_GROUNDING: PASS or FAIL
USEFUL_NEXT_STEP: PASS or FAIL
VERDICT: PASS or FAIL
FEEDBACK: one concise explanation of every failure
""".strip()

EXTERNAL_EVALUATOR_INSTRUCTIONS = """
You are an independent incident-response evaluator. You did not write the
candidate and must judge only the authoritative evidence in this request.

Return exactly these three lines:
FACTUAL_GROUNDING: PASS or FAIL
USEFUL_NEXT_STEP: PASS or FAIL
FEEDBACK: one concise explanation of every failure
""".strip()


SCRIPTED_INITIAL = (
    "INC-2048 is resolved. We rolled checkout-api back from checkout-v42 to "
    "checkout-v41, restored healthy operation, and eliminated the 18% checkout "
    "error rate. Customers can safely retry checkout now."
)

SCRIPTED_CLARIFIED = (
    "Incident INC-2048 is fully resolved. The checkout-api rollback from "
    "checkout-v42 to checkout-v41 restored healthy production service and "
    "removed the 18% error rate. Stakeholders can report recovery, and customers "
    "can safely resume checkout without further investigation."
)

SCRIPTED_REVISED = (
    "INC-2048 remains open. Confirmed facts: checkout-api is DEGRADED with an "
    "18% error rate while checkout-v42 is deployed. No restart or rollback has "
    "been executed, and recovery is not confirmed. Next, inspect current health, "
    "deployment history, and service logs before an authorized responder chooses "
    "remediation. Stakeholders should be told that checkout impact continues."
)


class Provider(Protocol):
    """Operations required by all three generator-evaluator loops."""

    name: str

    def generate_initial(self, scenario: Scenario) -> ModelReply: ...

    def clarify(self, candidate: ModelReply, scenario: Scenario) -> ModelReply: ...

    def self_review(self, candidate: ModelReply, scenario: Scenario) -> ModelReply: ...

    def external_review(
        self, candidate: ModelReply, scenario: Scenario
    ) -> ModelReply: ...

    def revise(
        self, candidate: ModelReply, scenario: Scenario, feedback: str
    ) -> ModelReply: ...


class ScriptedProvider:
    """Deterministic classroom path that requires no model credentials."""

    name = "scripted"

    def __init__(self) -> None:
        self._counter = 0
        self.call_log: list[tuple[str, str]] = []

    def _reply(self, action: str, text: str, candidate: str = "") -> ModelReply:
        self._counter += 1
        self.call_log.append((action, candidate))
        return ModelReply(response_id=f"scripted-{self._counter}", text=text)

    def generate_initial(self, scenario: Scenario) -> ModelReply:
        return self._reply("generate_initial", SCRIPTED_INITIAL)

    def clarify(self, candidate: ModelReply, scenario: Scenario) -> ModelReply:
        return self._reply("clarify", SCRIPTED_CLARIFIED, candidate.text)

    def self_review(self, candidate: ModelReply, scenario: Scenario) -> ModelReply:
        # This intentionally reproduces a self-evaluation false positive. The
        # independent path evaluates the exact same candidate and catches it.
        review = "\n".join(
            [
                "INCIDENT_ID: PASS",
                "LENGTH: PASS",
                "FACTUAL_GROUNDING: PASS",
                "USEFUL_NEXT_STEP: PASS",
                "VERDICT: PASS",
                "FEEDBACK: The update is complete and ready to send.",
            ]
        )
        return self._reply("self_review", review, candidate.text)

    def external_review(
        self, candidate: ModelReply, scenario: Scenario
    ) -> ModelReply:
        if candidate.text == SCRIPTED_REVISED:
            review = "\n".join(
                [
                    "FACTUAL_GROUNDING: PASS",
                    "USEFUL_NEXT_STEP: PASS",
                    "FEEDBACK: The update is grounded and gives safe diagnostics.",
                ]
            )
        else:
            review = "\n".join(
                [
                    "FACTUAL_GROUNDING: FAIL",
                    "USEFUL_NEXT_STEP: FAIL",
                    "FEEDBACK: No rollback or recovery is confirmed; keep the incident open and inspect health, deployments, and logs.",
                ]
            )
        return self._reply("external_review", review, candidate.text)

    def revise(
        self, candidate: ModelReply, scenario: Scenario, feedback: str
    ) -> ModelReply:
        return self._reply("revise", SCRIPTED_REVISED, candidate.text)


class LiveProvider:
    """Thin adapter around an OpenAI-compatible Responses API client."""

    name = "live"

    def __init__(self, client: Any, model: str) -> None:
        self.client = client
        self.model = model

    def _call(self, **kwargs: Any) -> ModelReply:
        started = time.perf_counter()
        response = self.client.responses.create(model=self.model, **kwargs)
        elapsed = time.perf_counter() - started
        usage = getattr(response, "usage", None)
        input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
        output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
        return ModelReply(
            response_id=str(response.id),
            text=str(response.output_text).strip(),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model_seconds=elapsed,
        )

    @staticmethod
    def _generation_prompt(scenario: Scenario) -> str:
        return f"""
Write a stakeholder update for this incident.

AUTHORITATIVE INCIDENT FACTS
{authoritative_context(scenario)}

OPERATOR REQUEST
{scenario.request}

RESPONSE REQUIREMENTS
{requirements_context(scenario)}

Return only the incident update.
""".strip()

    def generate_initial(self, scenario: Scenario) -> ModelReply:
        return self._call(
            instructions=GENERATOR_INSTRUCTIONS,
            input=self._generation_prompt(scenario),
        )

    def clarify(self, candidate: ModelReply, scenario: Scenario) -> ModelReply:
        return self._call(
            instructions=GENERATOR_INSTRUCTIONS,
            previous_response_id=candidate.response_id,
            input=(
                "Rewrite your previous incident update so it is clearer and more "
                "concise. Return only the revised update."
            ),
        )

    def self_review(self, candidate: ModelReply, scenario: Scenario) -> ModelReply:
        return self._call(
            instructions=SELF_EVALUATOR_INSTRUCTIONS,
            previous_response_id=candidate.response_id,
            input=f"""
Evaluate your previous update against these authoritative inputs.

AUTHORITATIVE INCIDENT FACTS
{authoritative_context(scenario)}

RESPONSE REQUIREMENTS
{requirements_context(scenario)}
""".strip(),
        )

    def external_review(
        self, candidate: ModelReply, scenario: Scenario
    ) -> ModelReply:
        return self._call(
            instructions=EXTERNAL_EVALUATOR_INSTRUCTIONS,
            input=f"""
AUTHORITATIVE INCIDENT FACTS
{authoritative_context(scenario)}

RESPONSE REQUIREMENTS
{requirements_context(scenario)}

CANDIDATE UPDATE
{candidate.text}
""".strip(),
        )

    def revise(
        self, candidate: ModelReply, scenario: Scenario, feedback: str
    ) -> ModelReply:
        return self._call(
            instructions=REVISION_INSTRUCTIONS,
            previous_response_id=candidate.response_id,
            input=f"""
Revise the previous update so every requirement passes.

AUTHORITATIVE INCIDENT FACTS
{authoritative_context(scenario)}

EVALUATION FEEDBACK
{feedback}

Return only the revised incident update.
""".strip(),
        )
