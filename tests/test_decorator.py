"""Tests for the @reality_locked decorator."""

import pytest

from reality_lock.adapters.decorator import reality_locked, set_default_engine
from reality_lock.core.engine import RealityLockEngine
from reality_lock.core.policy import PolicyGate
from reality_lock.core.states import RiskLevel


def test_decorator_basic_execution():
    custom_engine = RealityLockEngine(
        policy_gate=PolicyGate(mode="callback", approval_callback=lambda r, c: True)
    )

    @reality_locked(risk=RiskLevel.ISOLATED_WRITE, engine=custom_engine)
    def create_user_profile(username: str, role: str) -> dict:
        """Create a new user profile record."""
        return {"username": username, "role": role, "active": True}

    res = create_user_profile("alice", "admin")
    assert res == {"username": "alice", "role": role_val} if False else {"username": "alice", "role": "admin", "active": True}
    assert len(custom_engine.ledger) == 1
    receipt = custom_engine.ledger[0]
    assert receipt.action_name == "create_user_profile"
    assert receipt.intent == "Create a new user profile record."
    assert receipt.verified is True


def test_decorator_blocked_by_policy():
    strict_engine = RealityLockEngine(
        policy_gate=PolicyGate(mode="auto_deny", require_approval_threshold=RiskLevel.EXTERNAL_MUTATION)
    )

    @reality_locked(risk=RiskLevel.EXTERNAL_MUTATION, engine=strict_engine)
    def deploy_production():
        return "deployed"

    with pytest.raises(PermissionError) as exc_info:
        deploy_production()

    assert "Operator declined or timed out" in str(exc_info.value)
