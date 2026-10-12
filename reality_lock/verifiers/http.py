"""
HTTP Boundary and Network Response Verifier.

Verifies status codes, observed latency, and response integrity.
Redacts Authorization headers and sensitive auth tokens.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from reality_lock.verifiers.base import BaseVerifier, EvidenceResult


class HttpVerifier(BaseVerifier):
    """
    Verifies that HTTP requests yielded expected status codes.
    Prevents agents from claiming successful API calls when receiving 4xx or 5xx.
    """

    def __init__(
        self,
        allowed_status_codes: Optional[List[int]] = None,
        max_latency_ms: Optional[float] = None,
    ):
        self.allowed_status_codes = allowed_status_codes or list(range(200, 400))
        self.max_latency_ms = max_latency_ms

    def verify(
        self,
        pre_data: Dict[str, Any],
        raw_result: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> EvidenceResult:
        """Inspects response status code and returns evidence."""
        status_code: Optional[int] = None
        latency_ms: Optional[float] = None
        headers: Dict[str, Any] = {}

        # Handle requests/httpx Response objects
        if hasattr(raw_result, "status_code"):
            status_code = getattr(raw_result, "status_code")
            if hasattr(raw_result, "elapsed"):
                latency_ms = raw_result.elapsed.total_seconds() * 1000.0
            if hasattr(raw_result, "headers"):
                # Redact sensitive headers
                headers = {
                    k: ("[REDACTED]" if k.lower() in ("authorization", "cookie", "set-cookie", "x-api-key") else v)
                    for k, v in dict(raw_result.headers).items()
                }
        elif isinstance(raw_result, dict):
            status_code = raw_result.get("status_code", raw_result.get("status"))
            latency_ms = raw_result.get("latency_ms")
        elif isinstance(raw_result, int):
            status_code = raw_result

        if status_code is None:
            return EvidenceResult(
                verified=False,
                evidence_data={"raw_result": str(raw_result)},
                error="Could not extract HTTP status code from result",
            )

        evidence_data = {
            "status_code": status_code,
            "latency_ms": latency_ms,
            "safe_headers": headers,
        }

        if status_code not in self.allowed_status_codes:
            return EvidenceResult(
                verified=False,
                evidence_data=evidence_data,
                error=f"HTTP request returned status {status_code}, expected one of {self.allowed_status_codes}",
            )

        if self.max_latency_ms and latency_ms and latency_ms > self.max_latency_ms:
            return EvidenceResult(
                verified=False,
                evidence_data=evidence_data,
                error=f"Latency {latency_ms:.1f}ms exceeded limit of {self.max_latency_ms}ms",
            )

        return EvidenceResult(
            verified=True,
            evidence_data=evidence_data,
            error=None,
        )
