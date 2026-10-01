"""The six controlled harness configurations used by the ablation study."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HarnessConfig:
    skills: bool
    evaluator: bool
    hooks: bool
    permissions: bool

    @property
    def component_count(self) -> int:
        return sum((self.skills, self.evaluator, self.hooks, self.permissions))


CONFIGS: dict[str, HarnessConfig] = {
    "full": HarnessConfig(True, True, True, True),
    "no-skills": HarnessConfig(False, True, True, True),
    "no-evaluator": HarnessConfig(True, False, True, True),
    "no-hooks": HarnessConfig(True, True, False, True),
    "no-permissions": HarnessConfig(True, True, True, False),
    "bare": HarnessConfig(False, False, False, False),
}
