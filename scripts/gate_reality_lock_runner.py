#!/usr/bin/env python3
"""Reality Lock Evidence Gate Runner — fail-closed verification of Skill 62 invariants.

Verifies:
  1. Default-Deny PolicyGate blocks unapproved EXTERNAL_MUTATION actions.
  2. Read-only execution yields OBSERVED_EVIDENCE and a valid SHA-256 receipt.
  3. FilesystemVerifier detects missing files (blocks hallucinated writes).
  4. ExecutionReceipt.is_tampered() detects post-seal mutation.

Usage:
    python scripts/gate_reality_lock_runner.py
    python scripts/gate_reality_lock_runner.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from reality_lock.core.engine import RealityLockEngine
from reality_lock.core.policy import PolicyGate
from reality_lock.core.receipt import ExecutionReceipt
from reality_lock.core.states import ExecutionState, PolicyDecision, RiskLevel
from reality_lock.verifiers.filesystem import FilesystemVerifier


@dataclass(frozen=True)
class GateCheck:
    name: str
    passed: bool
    detail: str


def run_gate() -> dict[str, Any]:
    """Run all fail-closed Reality Lock zero-trust and evidence gates."""
    checks: list[GateCheck] = []

    # 1. Default-Deny PolicyGate
    gate = PolicyGate(mode="auto_deny")
    probe_rcpt = ExecutionReceipt(
        intent="gate_policy_probe",
        action_name="drop_table",
        risk_level=RiskLevel.EXTERNAL_MUTATION,
    )
    decision = gate.evaluate(probe_rcpt)
    checks.append(
        GateCheck(
            "default_deny_policy_gate",
            decision == PolicyDecision.REQUIRE_APPROVAL and not gate.request_approval(probe_rcpt),
            "Unapproved external mutation denied",
        )
    )

    # 2. Read-only execution + SHA-256 receipt
    engine = RealityLockEngine(strict_mode=True)
    engine.execute(
        intent="gate_probe",
        action_name="status_check",
        func=lambda: {"status": "ok"},
        risk_level=RiskLevel.READ_ONLY,
    )
    receipt = engine.ledger[-1]
    checks.append(
        GateCheck(
            "observed_evidence_receipt",
            receipt.state == ExecutionState.OBSERVED_EVIDENCE and receipt.verified and not receipt.is_tampered(),
            "Read-only action sealed with OBSERVED_EVIDENCE",
        )
    )

    # 3. FilesystemVerifier detects missing file (hallucination guard)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        missing = Path(tmp) / "never_written.txt"
        v_missing = FilesystemVerifier(target_paths=[missing], require_created=True)
        pre_missing = v_missing.pre_check()
        ev_missing = v_missing.verify(pre_missing, raw_result=missing)
        checks.append(
            GateCheck("hallucinated_file_rejected", not ev_missing.verified, "Missing disk file fails verification")
        )

        present = Path(tmp) / "real_file.txt"
        v_present = FilesystemVerifier(target_paths=[present], require_created=True)
        pre_present = v_present.pre_check()
        present.write_text("verified", encoding="utf-8")
        ev_present = v_present.verify(pre_present, raw_result=present)
        checks.append(
            GateCheck("physical_disk_sha256_verified", ev_present.verified and "files" in ev_present.evidence_data, "Disk SHA-256 captured")
        )

    # 4. Receipt tamper detection
    receipt.intent = "tampered_intent"
    checks.append(GateCheck("receipt_tamper_detection", receipt.is_tampered(), "Post-seal mutation detected"))

    approved = all(c.passed for c in checks)
    return {
        "status": "approved" if approved else "rejected",
        "approved": approved,
        "checks": [asdict(c) for c in checks],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Reality Lock fail-closed evidence gate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(argv)

    result = run_gate()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Gate Status: {result['status'].upper()}")
        for c in result["checks"]:
            mark = "PASS" if c["passed"] else "FAIL"
            print(f"  [{mark}] {c['name']}: {c['detail']}")
    return 0 if result["approved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
