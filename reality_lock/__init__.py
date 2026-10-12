"""
Reality Lock — The Deterministic Zero-Trust & Evidence Engine for AI Agents & MCP.

Built on the Sovereign AI Doctrine of Benni Master OS v9.4.
Separating Intent, Plan, Dispatch, Execution, and Observed Evidence.
"""

from reality_lock.adapters import (
    McpToolGate,
    RealityLockCallbackHandler,
    get_default_engine,
    lock_crewai_tool,
    reality_locked,
    set_default_engine,
)
from reality_lock.core import (
    ExecutionReceipt,
    ExecutionState,
    PolicyDecision,
    PolicyGate,
    RiskLevel,
    compute_sha256,
)
from reality_lock.core.engine import RealityLockEngine
from reality_lock.verifiers import (
    BaseVerifier,
    CommandVerifier,
    EvidenceResult,
    FilesystemVerifier,
    HttpVerifier,
)
from reality_lock.version import __version__

__all__ = [
    "__version__",
    "RealityLockEngine",
    "ExecutionReceipt",
    "ExecutionState",
    "RiskLevel",
    "PolicyDecision",
    "PolicyGate",
    "compute_sha256",
    "BaseVerifier",
    "EvidenceResult",
    "CommandVerifier",
    "FilesystemVerifier",
    "HttpVerifier",
    "reality_locked",
    "get_default_engine",
    "set_default_engine",
    "McpToolGate",
    "RealityLockCallbackHandler",
    "lock_crewai_tool",
]
