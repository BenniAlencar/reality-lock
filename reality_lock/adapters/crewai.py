"""
CrewAI Tool Adapter for Reality Lock.

Enables seamless wrapping of CrewAI Tools or BaseTool subclasses
with strict zero-trust reality verification and risk policies.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from reality_lock.adapters.decorator import reality_locked
from reality_lock.core.engine import RealityLockEngine
from reality_lock.core.states import RiskLevel


def lock_crewai_tool(
    tool_or_func: Any,
    risk: RiskLevel = RiskLevel.EXTERNAL_MUTATION,
    intent: Optional[str] = None,
    engine: Optional[RealityLockEngine] = None,
) -> Any:
    """
    Wraps a CrewAI tool instance or tool function with Reality Lock guards.
    """
    if hasattr(tool_or_func, "func") and callable(tool_or_func.func):
        # CrewAI Tool instance with .func attribute
        orig_func = tool_or_func.func
        name = getattr(tool_or_func, "name", orig_func.__name__)
        wrapped = reality_locked(
            risk=risk,
            intent=intent or f"CrewAI tool: {name}",
            action_name=name,
            engine=engine,
        )(orig_func)
        tool_or_func.func = wrapped
        return tool_or_func

    if callable(tool_or_func):
        return reality_locked(risk=risk, intent=intent, engine=engine)(tool_or_func)

    return tool_or_func
