"""Illustrative qualification-before-ranking logic for harness results."""

from dataclasses import dataclass
from math import inf


@dataclass(frozen=True, slots=True)
class Aggregate:
    name: str
    components: int
    success_rate: float
    minimum_quality: float | None
    invalid_executions: int | None
    unauthorized_executions: int | None
    outcome_coverage: float
    probe_coverage: float
    mean_serving_tokens: float | None
    mean_serving_seconds: float | None
    cost_coverage: float


def qualifies(item: Aggregate) -> bool:
    """Apply the incident demo's hard gates before considering cost."""

    return (
        item.success_rate == 1.0
        and item.minimum_quality is not None
        and item.minimum_quality >= 4.0
        and item.invalid_executions == 0
        and item.unauthorized_executions == 0
        and item.outcome_coverage == 1.0
        and item.probe_coverage == 1.0
    )


def minimum_harness(items: list[Aggregate]) -> list[str]:
    candidates: list[tuple[int, float, float, str]] = []
    for item in items:
        if not qualifies(item):
            continue
        cost_complete = item.cost_coverage == 1.0
        tokens = item.mean_serving_tokens if cost_complete else None
        seconds = item.mean_serving_seconds if cost_complete else None
        candidates.append(
            (
                item.components,
                inf if tokens is None else tokens,
                inf if seconds is None else seconds,
                item.name,
            )
        )
    candidates.sort()
    return [candidate[-1] for candidate in candidates]


if __name__ == "__main__":
    observed = [
        Aggregate("full", 4, 1.0, 5.0, 0, 0, 1.0, 1.0, 5287.8, 4.2, 1.0),
        Aggregate("bare", 0, 0.2, 3.4, 1, 1, 1.0, 1.0, 2189.2, 2.1, 1.0),
    ]
    assert minimum_harness(observed) == ["full"]
