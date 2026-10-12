"""
Base Verifier Contracts for Reality Lock.

A Verifier inspects real physical execution artifacts (files, processes, network)
and proves whether the stated intent actually manifested in reality.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EvidenceResult(BaseModel):
    """Result of an evidence verification probe."""
    verified: bool
    evidence_data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class BaseVerifier(ABC):
    """Abstract base class for all reality verifiers."""

    def pre_check(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Captures baseline state before action runs."""
        return {}

    @abstractmethod
    def verify(
        self,
        pre_data: Dict[str, Any],
        raw_result: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> EvidenceResult:
        """Inspects post-execution state and produces EvidenceResult."""
        pass
