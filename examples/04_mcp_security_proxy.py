"""
Example 04: Model Context Protocol (MCP) Tool Gate.

Demonstrates sandboxing and policy gating of MCP tools.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reality_lock import McpToolGate, PolicyGate, RealityLockEngine, RiskLevel


# Mock MCP tool function
def delete_s3_bucket(bucket_name: str) -> dict:
    return {"status": "deleted", "bucket": bucket_name}


if __name__ == "__main__":
    # Configure auto-deny for mutations unless approved
    policy = PolicyGate(mode="auto_deny", require_approval_threshold=RiskLevel.EXTERNAL_MUTATION)
    engine = RealityLockEngine(policy_gate=policy)
    gate = McpToolGate(engine=engine)

    print("--- Simulating MCP tools/call for 'delete_s3_bucket' ---")
    response = gate.handle_call(
        tool_name="delete_s3_bucket",
        arguments={"bucket_name": "corp-production-backups"},
        tool_implementation=delete_s3_bucket,
    )

    print("\nMCP Response Payload:")
    print("isError:", response["isError"])
    print("Content:", response["content"][0]["text"])
    print("Reality Lock Metadata:", response["_reality_lock"])
