"""Tests for PolicyGate rules, Default-Deny, and approval routing."""

import pytest

from reality_lock.core.policy import PolicyGate
from reality_lock.core.receipt import ExecutionReceipt
from reality_lock.core.states import PolicyDecision, RiskLevel


def test_default_allow_for_low_risk():
    gate = PolicyGate(mode="auto_deny", require_approval_threshold=RiskLevel.EXTERNAL_MUTATION)
    receipt = ExecutionReceipt(
        intent="Read system configuration",
        action_name="read_config",
        risk_level=RiskLevel.READ_ONLY,
    )
    decision = gate.evaluate(receipt)
    assert decision == PolicyDecision.ALLOW


def test_require_approval_for_external_mutation():
    gate = PolicyGate(mode="auto_deny", require_approval_threshold=RiskLevel.EXTERNAL_MUTATION)
    receipt = ExecutionReceipt(
        intent="Send customer email notification",
        action_name="send_email",
        risk_level=RiskLevel.EXTERNAL_MUTATION,
    )
    decision = gate.evaluate(receipt)
    assert decision == PolicyDecision.REQUIRE_APPROVAL
    # In auto_deny mode, request_approval must return False
    assert gate.request_approval(receipt) is False


def test_deny_list_takes_precedence():
    gate = PolicyGate(
        mode="audit_only",
        denied_actions=["drop_database", "nuclear_wipe"],
    )
    receipt = ExecutionReceipt(
        intent="Drop database table",
        action_name="drop_database",
        risk_level=RiskLevel.READ_ONLY,
    )
    decision = gate.evaluate(receipt)
    assert decision == PolicyDecision.DENY


def test_allow_list_bypasses_approval():
    gate = PolicyGate(
        mode="auto_deny",
        allowed_actions=["safe_deploy"],
        require_approval_threshold=RiskLevel.EXTERNAL_MUTATION,
    )
    receipt = ExecutionReceipt(
        intent="Deploy to pre-approved canary",
        action_name="safe_deploy",
        risk_level=RiskLevel.EXTERNAL_MUTATION,
    )
    decision = gate.evaluate(receipt)
    assert decision == PolicyDecision.ALLOW


def test_callback_approval():
    def custom_evaluator(rcpt: ExecutionReceipt, ctx: dict) -> bool:
        return ctx.get("authorized_by_operator") is True

    gate = PolicyGate(mode="callback", approval_callback=custom_evaluator)
    receipt = ExecutionReceipt(
        intent="Execute payment",
        action_name="process_charge",
        risk_level=RiskLevel.CRITICAL_AUTH_FINANCE,
    )

    # Denied when not authorized
    assert gate.request_approval(receipt, context={"authorized_by_operator": False}) is False
    # Allowed when explicitly authorized
    assert gate.request_approval(receipt, context={"authorized_by_operator": True}) is True
