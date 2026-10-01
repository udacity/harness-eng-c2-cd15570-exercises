"""Shared deterministic decision structures."""

from dataclasses import dataclass, field


@dataclass
class HookResult:
    allowed: bool
    violations: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)
    codes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PermissionResult:
    allowed: bool
    required_permission: str | None
    reason: str
    resource_id: str | None = None
    ownership: str = "not_applicable"
