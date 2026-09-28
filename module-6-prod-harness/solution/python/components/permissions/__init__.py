"""Default-deny permission policy supplied to the Python harness."""

from .policy import PermissionDecision, PermissionPolicy

__all__ = ["PermissionDecision", "PermissionPolicy"]
