"""
Example 05: LangChain & LangGraph Tool Callback Guard.

Shows how to attach the RealityLockCallbackHandler to any LangChain agent or run.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reality_lock import RealityLockCallbackHandler, RealityLockEngine

if __name__ == "__main__":
    engine = RealityLockEngine()
    handler = RealityLockCallbackHandler(engine=engine)

    print("--- Simulating LangChain Tool Callback Lifecycle ---")
    run_id = "test-run-1234"

    # Agent dispatches tool
    handler.on_tool_start(
        serialized={"name": "sql_query_executor"},
        input_str="SELECT count(*) FROM users WHERE status = 'active';",
        run_id=run_id,
    )

    # Tool finishes and returns output
    handler.on_tool_end(
        output={"count": 1420},
        run_id=run_id,
    )

    receipt = engine.ledger[-1]
    print("Action recorded in ledger:", receipt.action_name)
    print("State reached:", receipt.state.value)
    print("Verified evidence:", receipt.evidence)
    print("Receipt seal digest:", receipt.receipt_hash)
