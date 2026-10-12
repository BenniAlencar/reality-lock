"""
Command and Process Execution Verifier.

Verifies process exit codes, stdout, stderr, and hashes.
Detects when an agent hallucinated success despite a non-zero exit code.
"""

from __future__ import annotations

import hashlib
import shlex
import subprocess
import time
from typing import Any, Dict, List, Optional, Union

from reality_lock.verifiers.base import BaseVerifier, EvidenceResult


class CommandVerifier(BaseVerifier):
    """
    Verifies that system commands executed correctly.
    Rejects any claimed success where exit_code != expected_exit_code.
    """

    def __init__(self, expected_exit_code: int = 0, timeout_seconds: float = 60.0):
        self.expected_exit_code = expected_exit_code
        self.timeout_seconds = timeout_seconds

    def execute_and_verify(
        self,
        cmd: Union[str, List[str]],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> EvidenceResult:
        """
        Safely executes a shell or binary command, capturing exit code and stdout.
        """
        import os

        if isinstance(cmd, str):
            is_shell = "|" in cmd or ">" in cmd or "<" in cmd
            if is_shell:
                cmd_args = cmd
            else:
                try:
                    if os.name == "nt":
                        tokens = shlex.split(cmd, posix=False)
                        cmd_args = [
                            t[1:-1] if (len(t) >= 2 and ((t[0] == '"' and t[-1] == '"') or (t[0] == "'" and t[-1] == "'"))) else t
                            for t in tokens
                        ]
                    else:
                        cmd_args = shlex.split(cmd, posix=True)
                except Exception:
                    cmd_args = cmd
                    is_shell = True
        else:
            cmd_args = cmd
            is_shell = False

        start_time = time.perf_counter()
        try:
            res = subprocess.run(
                cmd_args,
                cwd=cwd,
                env=env,
                shell=is_shell,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            stdout_hash = hashlib.sha256(res.stdout.encode("utf-8")).hexdigest()

            evidence_data = {
                "command": str(cmd),
                "exit_code": res.returncode,
                "stdout_snippet": res.stdout[:500] if res.stdout else "",
                "stderr_snippet": res.stderr[:500] if res.stderr else "",
                "stdout_sha256": stdout_hash,
                "duration_ms": round(duration_ms, 2),
            }

            if res.returncode != self.expected_exit_code:
                return EvidenceResult(
                    verified=False,
                    evidence_data=evidence_data,
                    error=f"Command failed with exit code {res.returncode}. Stderr: {res.stderr[:200]}",
                )

            return EvidenceResult(
                verified=True,
                evidence_data=evidence_data,
                error=None,
            )

        except subprocess.TimeoutExpired:
            return EvidenceResult(
                verified=False,
                evidence_data={"command": str(cmd), "timeout": True},
                error=f"Command timed out after {self.timeout_seconds} seconds",
            )
        except Exception as exc:
            return EvidenceResult(
                verified=False,
                evidence_data={"command": str(cmd), "error": str(exc)},
                error=f"Command execution error: {exc}",
            )

    def verify(
        self,
        pre_data: Dict[str, Any],
        raw_result: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> EvidenceResult:
        """
        Verifies an existing command execution result (dict, subprocess.CompletedProcess, or exit code).
        """
        if isinstance(raw_result, subprocess.CompletedProcess):
            exit_code = raw_result.returncode
            stdout = raw_result.stdout or ""
            stderr = raw_result.stderr or ""
        elif isinstance(raw_result, dict):
            exit_code = raw_result.get("exit_code", raw_result.get("returncode", 0))
            stdout = str(raw_result.get("stdout", ""))
            stderr = str(raw_result.get("stderr", ""))
        elif isinstance(raw_result, int):
            exit_code = raw_result
            stdout = ""
            stderr = ""
        else:
            return EvidenceResult(
                verified=False,
                evidence_data={"raw_result": str(raw_result)},
                error="Cannot verify unknown command result format",
            )

        evidence_data = {
            "exit_code": exit_code,
            "stdout_snippet": stdout[:500],
            "stderr_snippet": stderr[:500],
        }

        if exit_code != self.expected_exit_code:
            return EvidenceResult(
                verified=False,
                evidence_data=evidence_data,
                error=f"Process exited with code {exit_code} (expected {self.expected_exit_code})",
            )

        return EvidenceResult(
            verified=True,
            evidence_data=evidence_data,
        )
