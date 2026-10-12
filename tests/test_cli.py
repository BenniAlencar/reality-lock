"""Tests for the Reality Lock CLI commands."""

import sys
from click.testing import CliRunner

from reality_lock.cli.main import cli


def test_cli_info():
    runner = CliRunner()
    result = runner.invoke(cli, ["info"])
    assert result.exit_code == 0
    assert "Reality Lock Engine" in result.output
    assert "Benni Master OS" in result.output


def test_cli_init():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0
        assert "Initialized configuration at" in result.output

        # Running again warns about existing file
        result_again = runner.invoke(cli, ["init"])
        assert "already exists" in result_again.output


def test_cli_verify_cmd():
    runner = CliRunner()
    cmd = f"{sys.executable} -c \"print('cli-verified')\""
    result = runner.invoke(cli, ["verify-cmd", cmd, "--risk", "read_only"])
    assert result.exit_code == 0
    assert "Execution Evidence Receipt" in result.output
    assert "YES" in result.output


def test_cli_audit():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # First when no ledger exists
        res = runner.invoke(cli, ["audit", "missing.jsonl"])
        assert res.exit_code == 0
        assert "No ledger file found" in res.output
