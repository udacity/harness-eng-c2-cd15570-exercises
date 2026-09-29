"""Small shared structures for the incident-response evaluator demo."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Scenario:
    """Authoritative incident state and the response task."""

    scenario_id: str
    request: str
    authenticated_user: dict[str, str]
    incident: dict[str, Any]
    response_requirements: dict[str, Any]

    @property
    def incident_id(self) -> str:
        return str(self.incident["incident_id"])


@dataclass(frozen=True, slots=True)
class ModelReply:
    """Provider-neutral text response and measured API usage."""

    response_id: str
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    model_seconds: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True, slots=True)
class CheckResult:
    """One deterministic evaluation result."""

    name: str
    passed: bool
    detail: str


@dataclass(frozen=True, slots=True)
class Review:
    """Parsed model-evaluator output."""

    criteria: dict[str, bool]
    verdict: bool
    feedback: str
    raw_text: str


@dataclass(slots=True)
class Attempt:
    """All evidence associated with one candidate response."""

    number: int
    candidate: ModelReply
    self_reply: ModelReply | None = None
    self_review: Review | None = None
    deterministic_checks: list[CheckResult] = field(default_factory=list)
    external_reply: ModelReply | None = None
    external_review: Review | None = None
    independent_passed: bool | None = None


@dataclass(frozen=True, slots=True)
class RunResult:
    """Structured outcome returned by one harness mode."""

    mode: str
    attempts: tuple[Attempt, ...]
    final_response: str
    stop_reason: str
    accepted: bool | None
    false_positive_observed: bool
    input_tokens: int
    output_tokens: int
    model_seconds: float

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
