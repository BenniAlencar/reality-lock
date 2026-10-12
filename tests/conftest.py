"""Shared pytest fixtures for Reality Lock tests."""

from pathlib import Path
import pytest

from reality_lock.core.engine import RealityLockEngine
from reality_lock.core.policy import PolicyGate
from reality_lock.core.states import RiskLevel


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def auto_approve_policy() -> PolicyGate:
    return PolicyGate(mode="callback", approval_callback=lambda r, c: True)


@pytest.fixture
def auto_deny_policy() -> PolicyGate:
    return PolicyGate(mode="auto_deny", require_approval_threshold=RiskLevel.EXTERNAL_MUTATION)


@pytest.fixture
def engine(auto_approve_policy: PolicyGate) -> RealityLockEngine:
    return RealityLockEngine(policy_gate=auto_approve_policy, strict_mode=True)
