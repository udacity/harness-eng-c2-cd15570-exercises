"""Shared result structures for deterministic incident hooks."""

from dataclasses import dataclass, field


@dataclass
class HookResult:
    """The decision made before a proposed tool call executes."""

    allowed: bool
    violations: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)
