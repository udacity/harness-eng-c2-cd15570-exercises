"""Minimal, executable-style pseudocode for a bounded evaluation loop.

The interfaces stand in for API calls. Production code also needs persistence,
timeouts, cancellation, privacy controls, and provider-specific error handling.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class Finding:
    criterion: str
    passed: bool
    evidence: str
    feedback: str = ""


@dataclass(frozen=True)
class ModelResponse:
    text: str
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class AttemptRecord:
    number: int
    candidate: str
    findings: list[Finding]
    tokens: int


@dataclass
class LoopResult:
    status: str
    accepted: bool
    final_candidate: str
    stop_reason: str
    attempts: list[AttemptRecord] = field(default_factory=list)


class Generator(Protocol):
    def generate(self, request: str, evidence: dict[str, Any]) -> ModelResponse: ...

    def revise(
        self,
        candidate: str,
        feedback: list[str],
        request: str,
        evidence: dict[str, Any],
    ) -> ModelResponse: ...


class Evaluator(Protocol):
    def evaluate(
        self,
        request: str,
        evidence: dict[str, Any],
        candidate: str,
    ) -> tuple[list[Finding], ModelResponse]: ...


def deterministic_checks(
    candidate: str,
    *,
    required_words: int,
    required_incident_id: str,
) -> list[Finding]:
    """Compute exact criteria without a model call."""

    words = len(candidate.split())
    return [
        Finding(
            criterion="word_count",
            passed=words == required_words,
            evidence=f"observed={words}; expected={required_words}",
            feedback=(
                ""
                if words == required_words
                else f"Revise to exactly {required_words} words."
            ),
        ),
        Finding(
            criterion="incident_id",
            passed=required_incident_id in candidate,
            evidence=f"required={required_incident_id}",
            feedback=(
                ""
                if required_incident_id in candidate
                else f"Include the exact identifier {required_incident_id}."
            ),
        ),
    ]


def all_passed(findings: list[Finding]) -> bool:
    return bool(findings) and all(item.passed for item in findings)


def run_loop(
    generator: Generator,
    evaluator: Evaluator,
    *,
    request: str,
    evidence: dict[str, Any],
    max_attempts: int = 3,
    token_budget: int = 8_000,
) -> LoopResult:
    """Generate, independently evaluate, revise, and stop with evidence."""

    if max_attempts <= 0 or token_budget <= 0:
        raise ValueError("Attempts and token budget must be positive.")

    response = generator.generate(request, evidence)
    total_tokens = response.total_tokens
    records: list[AttemptRecord] = []

    for attempt_number in range(1, max_attempts + 1):
        exact = deterministic_checks(
            response.text,
            required_words=60,
            required_incident_id="INC-2048",
        )

        # A product may bypass inferential evaluation when exact checks fail.
        # This teaching version runs both so one record contains every criterion.
        semantic, evaluation_response = evaluator.evaluate(
            request,
            evidence,
            response.text,
        )
        total_tokens += evaluation_response.total_tokens
        findings = [*exact, *semantic]
        records.append(
            AttemptRecord(
                number=attempt_number,
                candidate=response.text,
                findings=findings,
                tokens=total_tokens,
            )
        )

        if all_passed(findings):
            return LoopResult(
                status="accepted",
                accepted=True,
                final_candidate=response.text,
                stop_reason="all required criteria passed",
                attempts=records,
            )

        if total_tokens >= token_budget:
            return LoopResult(
                status="failed",
                accepted=False,
                final_candidate=response.text,
                stop_reason="token budget exhausted",
                attempts=records,
            )

        if attempt_number == max_attempts:
            return LoopResult(
                status="failed",
                accepted=False,
                final_candidate=response.text,
                stop_reason="maximum attempts reached with unresolved criteria",
                attempts=records,
            )

        feedback = [item.feedback for item in findings if not item.passed]
        response = generator.revise(response.text, feedback, request, evidence)
        total_tokens += response.total_tokens

    raise AssertionError("The bounded loop exited without a terminal result.")
