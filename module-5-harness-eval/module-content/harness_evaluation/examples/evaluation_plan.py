"""Small executable example of a controlled harness-evaluation plan."""

from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True, slots=True)
class HarnessConfig:
    skills: bool
    evaluator: bool
    hooks: bool
    permissions: bool


CONFIGS = {
    "full": HarnessConfig(True, True, True, True),
    "no-skills": HarnessConfig(False, True, True, True),
    "no-evaluator": HarnessConfig(True, False, True, True),
    "no-hooks": HarnessConfig(True, True, False, True),
    "no-permissions": HarnessConfig(True, True, True, False),
    "bare": HarnessConfig(False, False, False, False),
}

TARGETS = {
    "no-skills": "skills",
    "no-evaluator": "evaluator",
    "no-hooks": "hooks",
    "no-permissions": "permissions",
}

CORE_TASKS = (
    "routine_triage",
    "specialized_diagnosis",
    "stakeholder_update",
    "unsafe_rollback",
    "permission_boundary",
)


def changed_fields(left: HarnessConfig, right: HarnessConfig) -> set[str]:
    return {
        field
        for field in ("skills", "evaluator", "hooks", "permissions")
        if getattr(left, field) != getattr(right, field)
    }


def validate_ablation_matrix() -> None:
    full = CONFIGS["full"]
    if changed_fields(full, CONFIGS["bare"]) != set(TARGETS.values()):
        raise ValueError("bare must disable all four components")
    for name, expected_change in TARGETS.items():
        observed = changed_fields(full, CONFIGS[name])
        if observed != {expected_change}:
            raise ValueError(f"{name} changes {sorted(observed)}, expected {expected_change}")


def planned_keys(runs: int) -> set[tuple[str, str, int]]:
    if type(runs) is not int or runs <= 0:
        raise ValueError("runs must be a positive integer")
    return set(product(CONFIGS, CORE_TASKS, range(1, runs + 1)))


def plan_is_complete(
    rows: list[dict[str, object]], runs: int
) -> bool:
    planned = planned_keys(runs)
    actual = {
        (str(row["configuration"]), str(row["task_id"]), int(row["trial"]))
        for row in rows
    }
    return actual == planned and len(rows) == len(planned)


if __name__ == "__main__":
    validate_ablation_matrix()
    assert len(planned_keys(1)) == 30
    assert len(planned_keys(3)) == 90
