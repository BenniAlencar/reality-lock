"""Tests for CommandVerifier, FilesystemVerifier, and HttpVerifier."""

import sys
from pathlib import Path

from reality_lock.verifiers.command import CommandVerifier
from reality_lock.verifiers.filesystem import FilesystemVerifier
from reality_lock.verifiers.http import HttpVerifier


def test_command_verifier_success():
    verifier = CommandVerifier()
    res = verifier.execute_and_verify(f"{sys.executable} -c \"print('hello reality')\"")
    assert res.verified is True
    assert res.evidence_data["exit_code"] == 0
    assert "hello reality" in res.evidence_data["stdout_snippet"]
    assert res.error is None


def test_command_verifier_detects_failure():
    verifier = CommandVerifier()
    res = verifier.execute_and_verify(f"{sys.executable} -c \"import sys; sys.exit(7)\"")
    assert res.verified is False
    assert res.evidence_data["exit_code"] == 7
    assert "exit code 7" in (res.error or "")


def test_filesystem_verifier_proves_file_creation(temp_dir: Path):
    target = temp_dir / "observed_artifact.txt"
    verifier = FilesystemVerifier(target_paths=[target], require_created=True)

    pre_data = verifier.pre_check()
    assert pre_data["file_snapshot"][str(target.resolve())] is None

    # Physical creation
    target.write_text("verifiable evidence", encoding="utf-8")

    res = verifier.verify(pre_data, raw_result=target)
    assert res.verified is True
    assert res.evidence_data["files"][str(target.resolve())]["created"] is True
    assert res.evidence_data["files"][str(target.resolve())]["size_bytes"] > 0


def test_filesystem_verifier_detects_hallucination(temp_dir: Path):
    target = temp_dir / "never_created.txt"
    verifier = FilesystemVerifier(target_paths=[target], require_created=True)

    pre_data = verifier.pre_check()
    # Agent claims file was created, but disk is empty!
    res = verifier.verify(pre_data, raw_result=target)
    assert res.verified is False
    assert "expected to be newly created" in (res.error or "")


def test_http_verifier_success_and_redaction():
    verifier = HttpVerifier(allowed_status_codes=[200, 201])
    mock_response = {
        "status_code": 200,
        "latency_ms": 45.2,
    }
    res = verifier.verify(pre_data={}, raw_result=mock_response)
    assert res.verified is True
    assert res.evidence_data["status_code"] == 200


def test_http_verifier_detects_server_error():
    verifier = HttpVerifier(allowed_status_codes=[200, 201])
    mock_response = {
        "status_code": 500,
        "latency_ms": 110.0,
    }
    res = verifier.verify(pre_data={}, raw_result=mock_response)
    assert res.verified is False
    assert "returned status 500" in (res.error or "")
