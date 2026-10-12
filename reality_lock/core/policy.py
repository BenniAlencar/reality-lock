"""
Zero-Trust Policy Gate & Human-in-the-Loop Safeguards.

Implements the Default-Deny principle from Benni Master OS v9.4 Doctrine.
Every side-effecting action is scrutinized before execution.
"""

from __future__ import annotations

import sys
from typing import Any, Callable, Dict, List, Optional, Set

from reality_lock.core.receipt import ExecutionReceipt
from reality_lock.core.states import PolicyDecision, RiskLevel


class PolicyGate:
    """
    Evaluates proposed actions against security, risk, and authorization rules.
    Default-Deny: If authorization is uncertain, action is blocked or paused.
    """

    def __init__(
        self,
        mode: str = "interactive",  # "interactive", "callback", "auto_deny", "audit_only"
        approval_callback: Optional[Callable[[ExecutionReceipt, Dict[str, Any]], bool]] = None,
        require_approval_threshold: RiskLevel = RiskLevel.EXTERNAL_MUTATION,
        allowed_actions: Optional[List[str]] = None,
        denied_actions: Optional[List[str]] = None,
    ):
        self.mode = mode
        self.approval_callback = approval_callback
        self.require_approval_threshold = require_approval_threshold
        self.allowed_actions: Set[str] = set(allowed_actions or [])
        self.denied_actions: Set[str] = set(denied_actions or [])

    def should_require_approval(self, risk: RiskLevel) -> bool:
        """Determines if risk exceeds or equals threshold."""
        levels = [
            RiskLevel.READ_ONLY,
            RiskLevel.ISOLATED_WRITE,
            RiskLevel.EXTERNAL_MUTATION,
            RiskLevel.CRITICAL_AUTH_FINANCE,
        ]
        threshold_idx = levels.index(self.require_approval_threshold)
        current_idx = levels.index(risk)
        return current_idx >= threshold_idx

    def evaluate(self, receipt: ExecutionReceipt, context: Optional[Dict[str, Any]] = None) -> PolicyDecision:
        """Evaluates whether to allow, require approval, or deny the action."""
        context = context or {}

        # 1. Deny list check
        if receipt.action_name in self.denied_actions:
            return PolicyDecision.DENY

        # 2. Allow list check
        if receipt.action_name in self.allowed_actions:
            return PolicyDecision.ALLOW

        # 3. Audit only mode
        if self.mode == "audit_only":
            return PolicyDecision.ALLOW

        # 4. Check if risk level requires approval
        if self.should_require_approval(receipt.risk_level):
            return PolicyDecision.REQUIRE_APPROVAL

        return PolicyDecision.ALLOW

    def request_approval(self, receipt: ExecutionReceipt, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Executes the approval request according to the configured mode.
        Returns True if explicitly approved by human/system, False otherwise.
        """
        context = context or {}

        if self.mode == "auto_deny":
            return False

        if self.mode == "audit_only":
            return True

        if self.mode == "callback":
            if self.approval_callback:
                try:
                    return bool(self.approval_callback(receipt, context))
                except Exception as exc:
                    receipt.error = f"Policy callback failed: {exc}"
                    return False
            return False

        if self.mode == "interactive":
            return self._terminal_prompt(receipt)

        return False

    def _terminal_prompt(self, receipt: ExecutionReceipt) -> bool:
        """Presents an interactive prompt on the terminal."""
        prompt_text = (
            f"\n[REALITY-LOCK POLICY GATE] Human approval required!\n"
            f"Action: {receipt.action_name}\n"
            f"Risk Level: {receipt.risk_level.value}\n"
            f"Intent: {receipt.intent}\n"
            f"Approve this execution? [y/N]: "
        )
        try:
            if not sys.stdin.isatty():
                # Non-interactive environment, fallback to deny for safety
                return False
            
            response = input(prompt_text).strip().lower()
            return response in ("y", "yes")
        except Exception:
            return False
