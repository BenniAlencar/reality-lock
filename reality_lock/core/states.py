"""
Strict Finite-State Machine Definitions for Reality Lock.

In accordance with Benni Master OS v9.4 Doctrine:
Separates Intent, Plan, Dispatch, Execution, and Observed Evidence.
"""

from enum import Enum


class ExecutionState(str, Enum):
    """
    The canonical finite states of an AI agent action cycle.
    No action is considered successful until it reaches OBSERVED_EVIDENCE.
    """
    INTENT = "intent"
    PLAN = "plan"
    DISPATCH = "dispatch"
    EXECUTION = "execution"
    OBSERVED_EVIDENCE = "observed_evidence"
    REVIEW_REQUIRED = "review_required"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


class RiskLevel(str, Enum):
    """
    Risk taxonomy for agent capabilities and side-effects.
    Governed by the Default-Deny principle.
    """
    READ_ONLY = "read_only"
    ISOLATED_WRITE = "isolated_write"
    EXTERNAL_MUTATION = "external_mutation"
    CRITICAL_AUTH_FINANCE = "critical_auth_finance"


class PolicyDecision(str, Enum):
    """
    Outcome of an evaluation by the Policy Gate.
    """
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"
