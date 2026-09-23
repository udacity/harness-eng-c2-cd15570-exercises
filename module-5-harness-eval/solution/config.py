"""The six controlled harness configurations used by the ablation study."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HarnessConfig:
    """Switches for components that may be removed during an ablation."""

    skills: bool
    evaluator: bool
    hooks: bool
    permissions: bool

    @property
    def component_count(self) -> int:
        """Return the number of enabled optional harness components."""

        return sum((self.skills, self.evaluator, self.hooks, self.permissions))


CONFIGS: dict[str, HarnessConfig] = {
    "full": HarnessConfig(skills=True, evaluator=True, hooks=True, permissions=True),
    "no-skills": HarnessConfig(skills=False, evaluator=True, hooks=True, permissions=True),
    "no-evaluator": HarnessConfig(skills=True, evaluator=False, hooks=True, permissions=True),
    "no-hooks": HarnessConfig(skills=True, evaluator=True, hooks=False, permissions=True),
    "no-permissions": HarnessConfig(skills=True, evaluator=True, hooks=True, permissions=False),
    "bare": HarnessConfig(skills=False, evaluator=False, hooks=False, permissions=False),
}
