"""Tests for RealityLockEngine lifecycle, ledger, and anti-hallucination barriers."""

import sys
from pathlib import Path
import pytest

from reality_lock.core.engine import RealityLockEngine
from reality_lock.core.policy import PolicyGate
from reality_lock.core.states import ExecutionState, RiskLevel
from reality_lock.verifiers.base import BaseVerifier, EvidenceResult


class AlwaysFailsVerifier(BaseVerifier):
    def verify(self, pre_data, raw_result, context=None):
        return EvidenceResult(
            verified=False,
            evidence_data={"claimed": raw_result},
            error="Physical evidence missing or inconsistent",
        )


def test_engine_happy_path(engine: RealityLockEngine):
    def compute_sum(a: int, b: int) -> int:
        return a + b

    result = engine.execute(
        intent="Sum two numbers for unit test",
        action_name="math_sum",
        func=compute_sum,
        args=(10, 20),
        risk_level=RiskLevel.READ_ONLY,
    )

    assert result == 30
    assert len(engine.ledger) == 1
    receipt = engine.ledger[0]
    assert receipt.state == ExecutionState.OBSERVED_EVIDENCE
    assert receipt.verified is True
    assert receipt.receipt_hash is not None


def test_engine_blocks_hallucination_in_strict_mode(engine: RealityLockEngine):
    def hallucinating_action():
        return "I swear I fixed the bug!"

    with pytest.raises(RuntimeError) as exc_info:
        engine.execute(
            intent="Fix bug",
            action_name="fix_bug",
            func=hallucinating_action,
            risk_level=RiskLevel.ISOLATED_WRITE,
            verifier=AlwaysFailsVerifier(),
        )

    assert "Physical evidence missing or inconsistent" in str(exc_info.value)
    assert len(engine.ledger) == 1
    receipt = engine.ledger[0]
    assert receipt.state == ExecutionState.REJECTED
    assert receipt.verified is False


def test_lock_file_write(temp_dir: Path, engine: RealityLockEngine):
    target = temp_dir / "generated" / "sample.md"
    content = "# Sovereign AI Doctrine\nEvidence over claims."

    res_path = engine.lock_file_write(
        filepath=target,
        content=content,
        intent="Generate doctrine markdown file",
    )

    assert res_path.exists()
    assert res_path.read_text(encoding="utf-8") == content
    assert len(engine.ledger) == 1
    receipt = engine.ledger[0]
    assert receipt.verified is True
    assert receipt.evidence["files"][str(target.resolve())]["created"] is True


def test_lock_command(engine: RealityLockEngine):
    cmd = f"{sys.executable} -c \"print('evidence-first')\""
    evidence = engine.lock_command(cmd, intent="Print evidence string")

    assert evidence.verified is True
    receipt = engine.ledger[-1]
    assert receipt.action_name == "system_command"
    assert receipt.verified is True


def test_ledger_persistence(temp_dir: Path, auto_approve_policy: PolicyGate):
    ledger_file = temp_dir / "audit_ledger.jsonl"
    engine = RealityLockEngine(policy_gate=auto_approve_policy, ledger_path=ledger_file)

    engine.execute(
        intent="Audit trail test",
        action_name="noop",
        func=lambda: True,
    )

    assert ledger_file.exists()
    lines = ledger_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert "rcpt_" in lines[0]


def test_engine_stats(engine: RealityLockEngine):
    engine.execute(intent="Action 1", action_name="a1", func=lambda: 1)
    engine.execute(intent="Action 2", action_name="a2", func=lambda: 2)

    stats = engine.get_stats()
    assert stats["total_actions"] == 2
    assert stats["verified_actions"] == 2
    assert stats["rejected_actions"] == 0
