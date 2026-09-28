"""Small structures shared by the permitting harness."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionResult:
    """A deterministic authorization decision for one proposed tool call."""

    allowed: bool
    required_permission: str | None
    reason: str
    resource_id: str | None = None
    ownership: str = "not_applicable"
