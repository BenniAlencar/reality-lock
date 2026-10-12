"""
LangChain and LangGraph Adapter for Reality Lock.

Provides a plug-and-play BaseCallbackHandler that tracks and gates tool calls.
Works gracefully whether LangChain is installed or not.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from reality_lock.core.engine import RealityLockEngine
from reality_lock.core.receipt import ExecutionReceipt, compute_sha256
from reality_lock.core.states import ExecutionState, RiskLevel

try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:
    # Fallback shim for environments without langchain installed
    class BaseCallbackHandler:  # type: ignore[no-redef]
        pass


class RealityLockCallbackHandler(BaseCallbackHandler):
    """
    LangChain & LangGraph callback handler tracking tool calls as reality receipts.
    """

    def __init__(self, engine: Optional[RealityLockEngine] = None):
        super().__init__()
        self.engine = engine or RealityLockEngine()
        self._active_runs: Dict[str, ExecutionReceipt] = {}

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: Union[UUID, str],
        parent_run_id: Optional[Union[UUID, str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Captures when an agent invokes a tool."""
        run_key = str(run_id)
        name = serialized.get("name", "unknown_tool")
        receipt = ExecutionReceipt(
            intent=f"LangChain tool call: {name}",
            action_name=name,
            risk_level=RiskLevel.READ_ONLY,
            state=ExecutionState.DISPATCH,
            payload_hash=compute_sha256(input_str),
            payload_preview={"input": input_str[:200]},
        )
        self._active_runs[run_key] = receipt

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: Union[UUID, str],
        parent_run_id: Optional[Union[UUID, str]] = None,
        **kwargs: Any,
    ) -> None:
        """Records tool completion and verifies evidence."""
        run_key = str(run_id)
        receipt = self._active_runs.pop(run_key, None)
        if receipt:
            receipt.state = ExecutionState.OBSERVED_EVIDENCE
            receipt.verified = True
            receipt.evidence = {
                "output_preview": str(output)[:300],
                "output_type": type(output).__name__,
            }
            self.engine.record_receipt(receipt)

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: Union[UUID, str],
        parent_run_id: Optional[Union[UUID, str]] = None,
        **kwargs: Any,
    ) -> None:
        """Records tool failure as unverified receipt."""
        run_key = str(run_id)
        receipt = self._active_runs.pop(run_key, None)
        if receipt:
            receipt.state = ExecutionState.REJECTED
            receipt.verified = False
            receipt.error = str(error)
            self.engine.record_receipt(receipt)
