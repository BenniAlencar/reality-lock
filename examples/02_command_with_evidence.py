"""
Example 02: System Command Execution with Evidence Receipt.

Shows how RealityLockEngine executes commands and yields cryptographic receipts.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reality_lock import RealityLockEngine, RiskLevel

if __name__ == "__main__":
    engine = RealityLockEngine()

    print("--- Running Command with Reality Lock ---")
    cmd = [sys.executable, "-c", "import sys; print('System version:', sys.version.split()[0])"]

    # Executes command, captures stdout digest, exit code, and seals receipt
    evidence = engine.lock_command(cmd, intent="Query Python interpreter version", risk_level=RiskLevel.READ_ONLY)

    print("\nVerified in physical reality?:", evidence.verified)
    print("Exit code observed:", evidence.evidence_data["exit_code"])
    print("Output captured:", evidence.evidence_data["stdout_snippet"].strip())

    receipt = engine.ledger[-1]
    print("\nSealed Receipt ID:", receipt.receipt_id)
    print("Receipt SHA-256 Digest:", receipt.receipt_hash)
