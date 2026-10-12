"""
Cryptographic and Deterministic Execution Receipts for AI Actions.

Every action in Reality Lock yields an immutable Receipt.
Without an observed receipt, no claim of completion is valid.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from reality_lock.core.states import ExecutionState, RiskLevel


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute_sha256(data: Any) -> str:
    """Computes a deterministic SHA-256 hash for any serializable data."""
    if isinstance(data, bytes):
        payload = data
    elif isinstance(data, str):
        payload = data.encode("utf-8")
    else:
        try:
            payload = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        except Exception:
            payload = str(data).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class ExecutionReceipt(BaseModel):
    """
    Immutable cryptographic receipt proving real-world execution.
    Contains timestamp, execution duration, payload digests, and observed evidence.
    """
    receipt_id: str = Field(default_factory=lambda: f"rcpt_{uuid.uuid4().hex[:12]}")
    intent: str
    action_name: str
    risk_level: RiskLevel = RiskLevel.READ_ONLY
    state: ExecutionState = ExecutionState.INTENT
    started_at: str = Field(default_factory=_iso_now)
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    payload_hash: str = ""
    payload_preview: Dict[str, Any] = Field(default_factory=dict)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    verified: bool = False
    policy_approval: Optional[Dict[str, Any]] = None
    rollback_ref: Optional[str] = None
    error: Optional[str] = None
    receipt_hash: Optional[str] = None

    def seal(self) -> ExecutionReceipt:
        """
        Finalizes the receipt timestamp and computes the cryptographic receipt_hash.
        Once sealed, any tampering alters the digest.
        """
        if not self.completed_at:
            self.completed_at = _iso_now()
        
        # Calculate digest over all deterministic fields except receipt_hash itself
        data_to_hash = {
            "receipt_id": self.receipt_id,
            "intent": self.intent,
            "action_name": self.action_name,
            "risk_level": self.risk_level.value,
            "state": self.state.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "payload_hash": self.payload_hash,
            "evidence": self.evidence,
            "verified": self.verified,
            "policy_approval": self.policy_approval,
            "rollback_ref": self.rollback_ref,
            "error": self.error,
        }
        self.receipt_hash = compute_sha256(data_to_hash)
        return self

    def is_tampered(self) -> bool:
        """Verifies if the receipt has been modified post-sealing."""
        if not self.receipt_hash:
            return True
        current_hash = self.receipt_hash
        data_to_hash = {
            "receipt_id": self.receipt_id,
            "intent": self.intent,
            "action_name": self.action_name,
            "risk_level": self.risk_level.value,
            "state": self.state.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "payload_hash": self.payload_hash,
            "evidence": self.evidence,
            "verified": self.verified,
            "policy_approval": self.policy_approval,
            "rollback_ref": self.rollback_ref,
            "error": self.error,
        }
        return compute_sha256(data_to_hash) != current_hash
