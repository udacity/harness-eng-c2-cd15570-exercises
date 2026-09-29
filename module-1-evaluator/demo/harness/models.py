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


@dataclass(slots=True)
class Attempt:
    """All evidence associated with one candidate response."""

    number: int
    candidate: Any
    self_evaluation: Any | None = None
    deterministic_results: list[str] = field(default_factory=list)
    external_evaluation: Any | None = None
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
