"""
Model Context Protocol (MCP) Integration for Reality Lock.

Wraps and proxies MCP tools calls to enforce the Reality Lock protocol,
sandboxing side-effects and preventing unauthorized execution across MCP clients.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, Optional

from reality_lock.core.engine import RealityLockEngine
from reality_lock.core.states import RiskLevel
from reality_lock.verifiers.base import BaseVerifier


class McpToolGate:
    """
    Middleware/Proxy for Model Context Protocol (MCP) servers and clients.
    Intercepts 'tools/call' requests and enforces Reality Lock verification.
    """

    def __init__(
        self,
        engine: Optional[RealityLockEngine] = None,
        tool_risk_map: Optional[Dict[str, RiskLevel]] = None,
    ):
        self.engine = engine or RealityLockEngine()
        self.tool_risk_map = tool_risk_map or {}

    def get_tool_risk(self, tool_name: str) -> RiskLevel:
        """Infers or resolves risk level for an MCP tool."""
        if tool_name in self.tool_risk_map:
            return self.tool_risk_map[tool_name]

        # Heuristic risk classification based on common naming conventions
        lower_name = tool_name.lower()
        if any(w in lower_name for w in ("pay", "billing", "token", "secret", "credential", "auth")):
            return RiskLevel.CRITICAL_AUTH_FINANCE
        if any(w in lower_name for w in ("write", "create", "delete", "remove", "drop", "deploy", "send", "post", "patch")):
            return RiskLevel.EXTERNAL_MUTATION
        if any(w in lower_name for w in ("save", "temp", "cache", "export", "touch")):
            return RiskLevel.ISOLATED_WRITE
        return RiskLevel.READ_ONLY

    def handle_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        tool_implementation: Callable[..., Any],
        intent: Optional[str] = None,
        verifier: Optional[BaseVerifier] = None,
    ) -> Dict[str, Any]:
        """
        Intercepts and executes an MCP tool call within Reality Lock bounds.
        Returns standard MCP-compatible response dictionary.
        """
        risk = self.get_tool_risk(tool_name)
        call_intent = intent or f"MCP tool execution: {tool_name}"

        try:
            result = self.engine.execute(
                intent=call_intent,
                action_name=f"mcp::{tool_name}",
                func=tool_implementation,
                kwargs=arguments,
                risk_level=risk,
                verifier=verifier,
                context={"mcp_tool": tool_name, "arguments": arguments},
            )
            # Standard MCP tool response format
            text_repr = result if isinstance(result, str) else json.dumps(result, default=str)
            return {
                "content": [{"type": "text", "text": text_repr}],
                "isError": False,
                "_reality_lock": {
                    "verified": True,
                    "risk": risk.value,
                },
            }
        except Exception as exc:
            return {
                "content": [{"type": "text", "text": f"[REALITY-LOCK ERROR] {exc}"}],
                "isError": True,
                "_reality_lock": {
                    "verified": False,
                    "error": str(exc),
                },
            }
