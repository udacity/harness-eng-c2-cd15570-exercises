"""Small result structures shared by the incident-response harness."""

from dataclasses import dataclass, field


@dataclass
class HookResult:
    """The safety decision made before a proposed mutation executes."""

    allowed: bool
    violations: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class PermissionResult:
    """A deterministic authorization decision for one proposed tool call."""

    allowed: bool
    required_permission: str | None
    reason: str
    resource_id: str | None = None
    ownership: str = "not_applicable"
