"""A scripted Responses API double and a timing wrapper for live clients."""

from __future__ import annotations

import time
from types import SimpleNamespace
from typing import Any


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
    "INC-2048 remains open. Confirmed facts show checkout-api is DEGRADED with "
    "an 18% error rate while checkout-v42 remains deployed. No restart or "
    "rollback has occurred, and recovery is not confirmed. Next, inspect current "
    "health, deployment history, and service logs before an authorized responder "
    "selects remediation. Tell stakeholders that checkout impact continues and "
    "that the investigation remains active until evidence confirms recovery."
)


def _self_review(passed: bool) -> str:
    feedback = (
        "The update is complete and ready to send."
        if passed
        else "Correct the unsupported claims and exact word count."
    )
    word_count = "PASS" if passed else "FAIL"
    incident_id = "PASS"
    inferential = "PASS" if passed else "FAIL"
    verdict = "PASS" if passed else "FAIL"
    return "\n".join(
        [
            f"WORD_COUNT: {word_count}",
            f"INCIDENT_ID: {incident_id}",
            f"FACTUAL_GROUNDING: {inferential}",
            f"USEFUL_NEXT_STEP: {inferential}",
            f"VERDICT: {verdict}",
            f"FEEDBACK: {feedback}",
        ]
    )


SCRIPTED_EXTERNAL_FAIL = "\n".join(
    [
        "FACTUAL_GROUNDING: FAIL",
        "USEFUL_NEXT_STEP: FAIL",
        "FEEDBACK: No rollback or recovery is confirmed; keep the incident open and inspect health, deployments, and logs.",
    ]
)

SCRIPTED_EXTERNAL_PASS = "\n".join(
    [
        "FACTUAL_GROUNDING: PASS",
        "USEFUL_NEXT_STEP: PASS",
        "FEEDBACK: The update is grounded and gives safe diagnostics.",
    ]
)


class ScriptedResponses:
    """Mimic `client.responses.create` for a repeatable classroom run."""

    def __init__(self, self_verdicts: list[bool] | None = None) -> None:
        self.calls: list[dict[str, Any]] = []
        self._counter = 0
        self._self_verdicts = list(self_verdicts or [])

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(dict(kwargs))
        self._counter += 1
        instructions = str(kwargs.get("instructions", ""))
        input_text = str(kwargs.get("input", ""))

        if "independent incident-response evaluator" in instructions:
            output = (
                SCRIPTED_EXTERNAL_PASS
                if SCRIPTED_REVISED in input_text
                else SCRIPTED_EXTERNAL_FAIL
            )
        elif "Review the incident update you just wrote" in instructions:
            verdict = self._self_verdicts.pop(0) if self._self_verdicts else True
            output = _self_review(verdict)
        elif "Revise the previous" in instructions:
            output = SCRIPTED_REVISED
        elif "Rewrite your previous incident update" in input_text:
            output = SCRIPTED_CLARIFIED
        else:
            output = SCRIPTED_INITIAL

        return SimpleNamespace(
            id=f"scripted-{self._counter}",
            output_text=output,
            usage=SimpleNamespace(input_tokens=0, output_tokens=0),
        )


class ScriptedClient:
    """OpenAI-client-shaped object used by the default demo path."""

    def __init__(self, self_verdicts: list[bool] | None = None) -> None:
        self.responses = ScriptedResponses(self_verdicts)
        self.response_seconds: dict[str, float] = {}


class TimedResponses:
    """Preserve the normal Responses API while recording elapsed call time."""

    def __init__(self, responses: Any, timings: dict[str, float]) -> None:
        self._responses = responses
        self._timings = timings

    def create(self, **kwargs: Any) -> Any:
        started = time.perf_counter()
        response = self._responses.create(**kwargs)
        self._timings[str(response.id)] = time.perf_counter() - started
        return response


class TimedClient:
    """Client adapter that adds measurements without changing loop calls."""

    def __init__(self, client: Any) -> None:
        self.response_seconds: dict[str, float] = {}
        self.responses = TimedResponses(client.responses, self.response_seconds)
