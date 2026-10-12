"""Tests for state taxonomy, cryptographic receipts, and tamper-proofing."""

from reality_lock.core.receipt import ExecutionReceipt, compute_sha256
from reality_lock.core.states import ExecutionState, RiskLevel


def test_receipt_creation_and_sealing():
    receipt = ExecutionReceipt(
        intent="Check database migration status",
        action_name="db_status",
        risk_level=RiskLevel.READ_ONLY,
        state=ExecutionState.INTENT,
        payload_hash=compute_sha256({"env": "staging"}),
    )

    assert receipt.receipt_id.startswith("rcpt_")
    assert receipt.receipt_hash is None
    assert receipt.is_tampered() is True

    receipt.seal()
    assert receipt.receipt_hash is not None
    assert receipt.completed_at is not None
    assert receipt.is_tampered() is False


def test_tamper_detection():
    receipt = ExecutionReceipt(
        intent="Delete user records",
        action_name="purge_users",
        risk_level=RiskLevel.CRITICAL_AUTH_FINANCE,
        state=ExecutionState.EXECUTION,
    )
    receipt.seal()
    original_hash = receipt.receipt_hash

    # Tampering with state or evidence
    receipt.state = ExecutionState.OBSERVED_EVIDENCE
    assert receipt.is_tampered() is True
    assert receipt.receipt_hash == original_hash


def test_compute_sha256_determinism():
    data1 = {"b": 2, "a": 1}
    data2 = {"a": 1, "b": 2}
    # Key sorting ensures deterministic hash
    assert compute_sha256(data1) == compute_sha256(data2)
    assert compute_sha256("test") == compute_sha256(b"test")
