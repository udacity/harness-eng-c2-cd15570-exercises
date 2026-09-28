"""Baseline and configured copies of the hand-built Python loop."""

__all__ = ["BaselineAgentLoop", "HandBuiltAgentLoop", "RunTrace", "TOOL_DEFINITIONS"]


def __getattr__(name):
    if name == "BaselineAgentLoop":
        from .baseline_agent_loop import BaselineAgentLoop

        return BaselineAgentLoop
    if name in {"HandBuiltAgentLoop", "RunTrace", "TOOL_DEFINITIONS"}:
        from .configured_agent_loop import HandBuiltAgentLoop, RunTrace, TOOL_DEFINITIONS

        return {
            "HandBuiltAgentLoop": HandBuiltAgentLoop,
            "RunTrace": RunTrace,
            "TOOL_DEFINITIONS": TOOL_DEFINITIONS,
        }[name]
    raise AttributeError(name)
