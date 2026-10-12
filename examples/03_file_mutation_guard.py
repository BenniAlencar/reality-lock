"""
Example 03: Filesystem Mutation Guard & Anti-Hallucination.

Shows how Reality Lock proves real disk changes and catches agent lies.
"""

import sys
from pathlib import Path
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reality_lock import RealityLockEngine

if __name__ == "__main__":
    engine = RealityLockEngine()

    with tempfile.TemporaryDirectory() as tmp_dir:
        target_file = Path(tmp_dir) / "config.yaml"
        content = "env: production\nsafe_mode: true\n"

        print(f"--- Writing file through Reality Lock ---")
        written_path = engine.lock_file_write(
            filepath=target_file,
            content=content,
            intent="Persist safe configuration file",
        )

        receipt = engine.ledger[-1]
        print("File created on disk:", written_path.exists())
        print("SHA-256 Digest in Receipt:", receipt.evidence["files"][str(written_path.resolve())]["post_hash"])
        print("Status:", receipt.state.value)
