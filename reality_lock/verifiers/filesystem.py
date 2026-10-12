"""
Filesystem Mutation Verifier.

Captures SHA-256 snapshots before and after execution to prove file existence,
modifications, or deletions in the physical environment.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from reality_lock.verifiers.base import BaseVerifier, EvidenceResult


def _hash_file(filepath: Union[str, Path]) -> Optional[str]:
    p = Path(filepath)
    if not p.is_file():
        return None
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


class FilesystemVerifier(BaseVerifier):
    """
    Verifies that file operations actually resulted in real disk changes.
    Proves creation, modification, or content integrity.
    """

    def __init__(
        self,
        target_paths: Optional[List[Union[str, Path]]] = None,
        require_created: bool = False,
        require_modified: bool = False,
    ):
        self.target_paths = [Path(p) for p in (target_paths or [])]
        self.require_created = require_created
        self.require_modified = require_modified

    def pre_check(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Snapshots the target files before tool invocation."""
        paths = list(self.target_paths)
        if context and "filepath" in context:
            paths.append(Path(context["filepath"]))
        if context and "target_file" in context:
            paths.append(Path(context["target_file"]))

        snapshot: Dict[str, Optional[str]] = {}
        for p in paths:
            snapshot[str(p.resolve())] = _hash_file(p)
        return {"file_snapshot": snapshot}

    def verify(
        self,
        pre_data: Dict[str, Any],
        raw_result: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> EvidenceResult:
        """Compares post-execution state with pre-execution snapshot."""
        pre_snapshot = pre_data.get("file_snapshot", {})
        post_snapshot: Dict[str, Optional[str]] = {}
        file_evidences: Dict[str, Any] = {}

        paths = list(self.target_paths)
        if context and "filepath" in context:
            paths.append(Path(context["filepath"]))
        if context and "target_file" in context:
            paths.append(Path(context["target_file"]))

        # Check all tracked paths
        all_resolved = set(pre_snapshot.keys()).union(str(p.resolve()) for p in paths)

        for p_str in all_resolved:
            p = Path(p_str)
            pre_hash = pre_snapshot.get(p_str)
            post_hash = _hash_file(p)
            post_snapshot[p_str] = post_hash

            exists = p.is_file()
            size = p.stat().st_size if exists else 0

            file_evidences[p_str] = {
                "exists": exists,
                "size_bytes": size,
                "pre_hash": pre_hash,
                "post_hash": post_hash,
                "modified": (pre_hash is not None and post_hash is not None and pre_hash != post_hash),
                "created": (pre_hash is None and post_hash is not None),
                "deleted": (pre_hash is not None and post_hash is None),
            }

            if self.require_created and not file_evidences[p_str]["created"]:
                return EvidenceResult(
                    verified=False,
                    evidence_data={"files": file_evidences},
                    error=f"File was expected to be newly created, but was not: {p_str}",
                )

            if self.require_modified and not file_evidences[p_str]["modified"]:
                return EvidenceResult(
                    verified=False,
                    evidence_data={"files": file_evidences},
                    error=f"File was expected to be modified, but content did not change: {p_str}",
                )

            if not exists and not file_evidences[p_str]["deleted"]:
                return EvidenceResult(
                    verified=False,
                    evidence_data={"files": file_evidences},
                    error=f"Expected file does not exist on disk: {p_str}",
                )

        return EvidenceResult(
            verified=True,
            evidence_data={"files": file_evidences},
            error=None,
        )
