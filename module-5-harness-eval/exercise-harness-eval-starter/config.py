"""The controlled harness configurations used by the ablation study."""

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


# TODO: Configure the complete system, the four single-component ablations,
# and the bare baseline. A valid single-component ablation differs from `full`
# in exactly one switch; `bare` disables all four optional components.
CONFIGS: dict[str, HarnessConfig] = {
    "full": HarnessConfig(skills=False, evaluator=False, hooks=False, permissions=False),
    "no-skills": HarnessConfig(skills=False, evaluator=False, hooks=False, permissions=False),
    "no-evaluator": HarnessConfig(skills=False, evaluator=False, hooks=False, permissions=False),
    "no-hooks": HarnessConfig(skills=False, evaluator=False, hooks=False, permissions=False),
    "no-permissions": HarnessConfig(skills=False, evaluator=False, hooks=False, permissions=False),
    "bare": HarnessConfig(skills=False, evaluator=False, hooks=False, permissions=False),
}
