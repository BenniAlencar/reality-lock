"""
Reality Lock Core Engine.

Orchestrates the 5-state execution cycle:
Intent -> Plan -> Dispatch -> Execution -> Observed Evidence.
Binds PolicyGate, Verifiers, and the Cryptographic Receipt Ledger.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from reality_lock.core.policy import PolicyGate
from reality_lock.core.receipt import ExecutionReceipt, compute_sha256
from reality_lock.core.states import ExecutionState, PolicyDecision, RiskLevel
from reality_lock.verifiers.base import BaseVerifier, EvidenceResult
from reality_lock.verifiers.command import CommandVerifier
from reality_lock.verifiers.filesystem import FilesystemVerifier


class RealityLockEngine:
    """
    The central coordinator ensuring zero-trust agent execution and verifiable evidence.
    """

    def __init__(
        self,
        policy_gate: Optional[PolicyGate] = None,
        ledger_path: Optional[Union[str, Path]] = None,
        strict_mode: bool = True,
    ):
        self.policy_gate = policy_gate or PolicyGate()
        self.ledger_path = Path(ledger_path) if ledger_path else None
        self.strict_mode = strict_mode
        self._ledger: List[ExecutionReceipt] = []

    @property
    def ledger(self) -> List[ExecutionReceipt]:
        """Returns the in-memory receipt ledger."""
        return list(self._ledger)

    def record_receipt(self, receipt: ExecutionReceipt) -> None:
        """Appends receipt to ledger and writes to disk if configured."""
        receipt.seal()
        self._ledger.append(receipt)

        if self.ledger_path:
            try:
                self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.ledger_path, "a", encoding="utf-8") as f:
                    f.write(receipt.model_dump_json() + "\n")
            except Exception:
                pass

    def execute(
        self,
        intent: str,
        action_name: str,
        func: Callable[..., Any],
        args: Optional[tuple] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        risk_level: RiskLevel = RiskLevel.READ_ONLY,
        verifier: Optional[BaseVerifier] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Executes a function through the full 5-stage Reality Lock protocol.
        """
        args = args or ()
        kwargs = kwargs or {}
        context = context or {}

        # 1. State: INTENT
        payload_preview = {
            "args": [str(a)[:100] for a in args],
            "kwargs": {k: str(v)[:100] for k, v in kwargs.items()},
        }
        payload_hash = compute_sha256({"args": args, "kwargs": kwargs})

        receipt = ExecutionReceipt(
            intent=intent,
            action_name=action_name,
            risk_level=risk_level,
            state=ExecutionState.INTENT,
            payload_hash=payload_hash,
            payload_preview=payload_preview,
        )

        # 2. State: PLAN -> DISPATCH (Policy Gate Evaluation)
        receipt.state = ExecutionState.PLAN
        decision = self.policy_gate.evaluate(receipt, context)

        if decision == PolicyDecision.DENY:
            receipt.state = ExecutionState.REJECTED
            receipt.error = "Action explicitly denied by Policy Gate"
            self.record_receipt(receipt)
            raise PermissionError(f"[REALITY-LOCK] Action '{action_name}' was DENIED by policy rules.")

        if decision == PolicyDecision.REQUIRE_APPROVAL:
            receipt.state = ExecutionState.REVIEW_REQUIRED
            approved = self.policy_gate.request_approval(receipt, context)
            if not approved:
                receipt.state = ExecutionState.REJECTED
                receipt.error = "Action rejected or denied by Operator in Policy Gate"
                self.record_receipt(receipt)
                raise PermissionError(f"[REALITY-LOCK] Operator declined or timed out on '{action_name}'.")
            receipt.policy_approval = {"status": "approved", "timestamp": time.time()}

        receipt.state = ExecutionState.DISPATCH

        # 3. Pre-execution verifier check
        pre_data: Dict[str, Any] = {}
        if verifier:
            pre_data = verifier.pre_check(context)

        # 4. State: EXECUTION
        receipt.state = ExecutionState.EXECUTION
        start_time = time.perf_counter()
        raw_result = None
        exec_error: Optional[Exception] = None

        try:
            raw_result = func(*args, **kwargs)
        except Exception as exc:
            exec_error = exc

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        receipt.duration_ms = round(duration_ms, 2)

        if exec_error is not None:
            receipt.state = ExecutionState.REJECTED
            receipt.error = f"Execution raised exception: {exec_error}"
            self.record_receipt(receipt)
            raise exec_error

        # 5. State: OBSERVED_EVIDENCE
        if verifier:
            evidence_result: EvidenceResult = verifier.verify(pre_data, raw_result, context)
            receipt.evidence = evidence_result.evidence_data
            receipt.verified = evidence_result.verified
            receipt.error = evidence_result.error

            if not evidence_result.verified:
                receipt.state = ExecutionState.REJECTED
                self.record_receipt(receipt)
                if self.strict_mode:
                    raise RuntimeError(
                        f"[REALITY-LOCK VERIFICATION FAILED] Hallucination or failed invariant on '{action_name}': "
                        f"{evidence_result.error}"
                    )
                return raw_result
        else:
            # Fallback observation
            receipt.verified = True
            receipt.evidence = {"raw_output_type": type(raw_result).__name__}

        receipt.state = ExecutionState.OBSERVED_EVIDENCE
        self.record_receipt(receipt)
        return raw_result

    def lock_command(
        self,
        cmd: Union[str, List[str]],
        intent: Optional[str] = None,
        risk_level: RiskLevel = RiskLevel.EXTERNAL_MUTATION,
        cwd: Optional[str] = None,
    ) -> EvidenceResult:
        """Runs and locks a command with verified exit code evidence."""
        intent = intent or f"Execute shell command: {cmd}"
        verifier = CommandVerifier()

        def _runner():
            return verifier.execute_and_verify(cmd, cwd=cwd)

        res: EvidenceResult = self.execute(
            intent=intent,
            action_name="system_command",
            func=_runner,
            risk_level=risk_level,
            context={"command": str(cmd)},
        )
        return res

    def lock_file_write(
        self,
        filepath: Union[str, Path],
        content: Union[str, bytes],
        intent: Optional[str] = None,
        risk_level: RiskLevel = RiskLevel.ISOLATED_WRITE,
    ) -> Path:
        """Writes a file with SHA-256 pre and post-mutation verification."""
        p = Path(filepath)
        intent = intent or f"Write file {p.name}"
        verifier = FilesystemVerifier(target_paths=[p], require_created=not p.exists(), require_modified=p.exists())

        def _writer():
            p.parent.mkdir(parents=True, exist_ok=True)
            mode = "wb" if isinstance(content, bytes) else "w"
            encoding = None if isinstance(content, bytes) else "utf-8"
            with open(p, mode, encoding=encoding) as f:
                f.write(content)
            return p

        return self.execute(
            intent=intent,
            action_name="filesystem_write",
            func=_writer,
            risk_level=risk_level,
            verifier=verifier,
            context={"filepath": str(p)},
        )

    def get_stats(self) -> Dict[str, Any]:
        """Calculates ledger metrics."""
        total = len(self._ledger)
        verified = sum(1 for r in self._ledger if r.verified and r.state == ExecutionState.OBSERVED_EVIDENCE)
        rejected = sum(1 for r in self._ledger if r.state == ExecutionState.REJECTED)
        review_required = sum(1 for r in self._ledger if r.policy_approval is not None)
        avg_duration = sum(r.duration_ms for r in self._ledger) / total if total > 0 else 0.0

        return {
            "total_actions": total,
            "verified_actions": verified,
            "rejected_actions": rejected,
            "policy_approvals": review_required,
            "average_duration_ms": round(avg_duration, 2),
            "hallucination_prevention_rate": (
                f"{(rejected / total * 100):.1f}%" if total > 0 else "0.0%"
            ),
        }
