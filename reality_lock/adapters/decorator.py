"""
Python Function Decorator for Reality Lock.

Allows zero-boilerplate protection on any function or agent tool:
@reality_locked(risk=RiskLevel.EXTERNAL_MUTATION)
"""

from __future__ import annotations

import functools
from typing import Any, Callable, Optional

from reality_lock.core.engine import RealityLockEngine
from reality_lock.core.states import RiskLevel
from reality_lock.verifiers.base import BaseVerifier

# Default global engine instance
_DEFAULT_ENGINE = RealityLockEngine()


def get_default_engine() -> RealityLockEngine:
    return _DEFAULT_ENGINE


def set_default_engine(engine: RealityLockEngine) -> None:
    global _DEFAULT_ENGINE
    _DEFAULT_ENGINE = engine


def reality_locked(
    risk: RiskLevel = RiskLevel.READ_ONLY,
    intent: Optional[str] = None,
    action_name: Optional[str] = None,
    verifier: Optional[BaseVerifier] = None,
    engine: Optional[RealityLockEngine] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator that wraps any function call with the Reality Lock 5-stage verification.
    """
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        target_name = action_name or fn.__name__
        target_intent = intent or (fn.__doc__.strip().split("\n")[0] if fn.__doc__ else f"Execute {target_name}")

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            active_engine = engine or get_default_engine()
            return active_engine.execute(
                intent=target_intent,
                action_name=target_name,
                func=fn,
                args=args,
                kwargs=kwargs,
                risk_level=risk,
                verifier=verifier,
                context={"args": args, "kwargs": kwargs},
            )

        # Attach engine reference to wrapper for inspection
        wrapper.__reality_locked__ = True  # type: ignore[attr-defined]
        wrapper.engine = engine or _DEFAULT_ENGINE  # type: ignore[attr-defined]
        return wrapper

    return decorator
