"""Reality Lock Doctor — Environment, PolicyGate, and Physical Verifier Diagnostics.

Inspects Python runtime, dependencies, and executes live probes for:
  - 5-state execution & SHA-256 ExecutionReceipt sealing
  - Default-Deny PolicyGate enforcement
  - FilesystemVerifier physical disk hash verification
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from reality_lock.core.engine import RealityLockEngine
from reality_lock.core.policy import PolicyGate
from reality_lock.core.receipt import ExecutionReceipt
from reality_lock.core.states import ExecutionState, PolicyDecision, RiskLevel
from reality_lock.verifiers.filesystem import FilesystemVerifier
from reality_lock.version import __system__, __version__


@dataclass(frozen=True)
class DoctorReport:
    """Structured diagnostic report for Reality Lock."""

    version: str
    doctrine: str
    python_version: str
    platform: str
    dependencies: dict[str, bool]
    receipt_seal_probe_ok: bool
    policy_deny_probe_ok: bool
    filesystem_verifier_ok: bool
    probe_latency_ms: float
    healthy: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def probe_dependencies() -> dict[str, bool]:
    """Check availability of core and optional runtime dependencies."""
    packages = ("pydantic", "click", "rich", "mcp", "langchain_core", "pytest")
    return {pkg: importlib.util.find_spec(pkg) is not None for pkg in packages}


def run_doctor() -> DoctorReport:
    """Execute environment and zero-trust evidence self-checks."""
    deps = probe_dependencies()
    t0 = time.perf_counter()

    # 1. Read-only execution + SHA-256 receipt probe
    engine = RealityLockEngine(strict_mode=True)
    res = engine.execute(
        intent="doctor_probe",
        action_name="status_check",
        func=lambda: {"ok": True},
        risk_level=RiskLevel.READ_ONLY,
    )
    receipt = engine.ledger[-1]
    receipt_ok = (
        res == {"ok": True}
        and receipt.state == ExecutionState.OBSERVED_EVIDENCE
        and not receipt.is_tampered()
    )

    # 2. Default-Deny policy gate probe
    gate = PolicyGate(mode="auto_deny")
    probe_rcpt = ExecutionReceipt(
        intent="doctor_policy_probe",
        action_name="deploy_prod",
        risk_level=RiskLevel.EXTERNAL_MUTATION,
    )
    decision = gate.evaluate(probe_rcpt)
    policy_ok = decision == PolicyDecision.REQUIRE_APPROVAL and not gate.request_approval(probe_rcpt)

    # 3. FilesystemVerifier physical disk probe
    fs_ok = False
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        target = Path(tmp) / "probe.txt"
        verifier = FilesystemVerifier(target_paths=[target], require_created=True)
        pre_data = verifier.pre_check()
        target.write_text("reality-lock-probe", encoding="utf-8")
        ev = verifier.verify(pre_data, raw_result=target)
        fs_ok = ev.verified and "files" in ev.evidence_data

    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    healthy = (
        receipt_ok
        and policy_ok
        and fs_ok
        and all(deps[k] for k in ("pydantic", "click", "rich"))
    )

    return DoctorReport(
        version=__version__,
        doctrine=__system__,
        python_version=platform.python_version(),
        platform=f"{platform.system()} {platform.release()}",
        dependencies=deps,
        receipt_seal_probe_ok=receipt_ok,
        policy_deny_probe_ok=policy_ok,
        filesystem_verifier_ok=fs_ok,
        probe_latency_ms=latency_ms,
        healthy=healthy,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reality Lock environment diagnostics.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(argv)

    report = run_doctor()
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        status = "HEALTHY" if report.healthy else "DEGRADED"
        print(f"Reality Lock Doctor v{report.version} [{status}]")
        print(f"Python: {report.python_version} | OS: {report.platform}")
        print(
            f"Receipt Seal: {'OK' if report.receipt_seal_probe_ok else 'FAIL'} | "
            f"Policy Deny: {'OK' if report.policy_deny_probe_ok else 'FAIL'} | "
            f"FS Verifier: {'OK' if report.filesystem_verifier_ok else 'FAIL'} ({report.probe_latency_ms} ms)"
        )
    return 0 if report.healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())
