"""Tests for Model Context Protocol (MCP) adapter."""

from reality_lock.adapters.mcp import McpToolGate
from reality_lock.core.engine import RealityLockEngine
from reality_lock.core.policy import PolicyGate
from reality_lock.core.states import RiskLevel


def test_mcp_risk_inference():
    gate = McpToolGate()
    assert gate.get_tool_risk("read_file") == RiskLevel.READ_ONLY
    assert gate.get_tool_risk("save_snapshot") == RiskLevel.ISOLATED_WRITE
    assert gate.get_tool_risk("delete_database") == RiskLevel.EXTERNAL_MUTATION
    assert gate.get_tool_risk("process_payment") == RiskLevel.CRITICAL_AUTH_FINANCE


def test_mcp_handle_call_success():
    engine = RealityLockEngine(
        policy_gate=PolicyGate(mode="callback", approval_callback=lambda r, c: True)
    )
    gate = McpToolGate(engine=engine)

    def mock_tool(path: str) -> dict:
        return {"status": "ok", "path": path}

    response = gate.handle_call(
        tool_name="inspect_directory",
        arguments={"path": "/workspace"},
        tool_implementation=mock_tool,
    )

    assert response["isError"] is False
    assert len(response["content"]) == 1
    assert "status" in response["content"][0]["text"]
    assert response["_reality_lock"]["verified"] is True


def test_mcp_handle_call_blocked_by_policy():
    strict_engine = RealityLockEngine(
        policy_gate=PolicyGate(mode="auto_deny", require_approval_threshold=RiskLevel.EXTERNAL_MUTATION)
    )
    gate = McpToolGate(engine=strict_engine)

    def dangerous_tool():
        return "wiped"

    response = gate.handle_call(
        tool_name="delete_production_cluster",
        arguments={},
        tool_implementation=dangerous_tool,
    )

    assert response["isError"] is True
    assert "REALITY-LOCK ERROR" in response["content"][0]["text"]
    assert response["_reality_lock"]["verified"] is False
