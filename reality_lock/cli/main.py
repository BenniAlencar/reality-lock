"""
Reality Lock CLI Interface.

Provides terminal audit tables, command verification, and policy configuration.
Built with Click and Rich for exceptional developer experience.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows consoles to prevent charmap errors
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import click
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from reality_lock.core.engine import RealityLockEngine
from reality_lock.core.receipt import compute_sha256
from reality_lock.core.states import RiskLevel
from reality_lock.version import __author__, __system__, __version__

console = Console(legacy_windows=False)


def _print_branding():
    banner = (
        f"[bold cyan]🔒 Reality Lock Engine[/bold cyan] [bold white]v{__version__}[/bold white]\n"
        f"[dim]The Zero-Trust & Verifiable Evidence Framework for AI Agents & MCP[/dim]\n"
        f"[dim green]Doctrine: {__system__} • Maintained by {__author__}[/dim green]"
    )
    console.print(Panel(banner, border_style="cyan", expand=False))


@click.group()
@click.version_option(version=__version__, prog_name="reality-lock")
def cli():
    """Reality Lock — Zero-Trust & Verifiable Evidence Engine for AI Agents."""
    pass


@cli.command("info")
def info():
    """Displays system information, doctrine, and enterprise gateway links."""
    _print_branding()
    rprint("\n[bold]Core Principles:[/bold]")
    rprint("  1. [cyan]Finite-State Integrity[/cyan]: Intent → Plan → Dispatch → Execution → Observed Evidence")
    rprint("  2. [green]Default-Deny Policy Gate[/green]: No side-effects without explicit human authorization")
    rprint("  3. [yellow]Cryptographic Receipts[/yellow]: SHA-256 sealed proof of real execution\n")
    rprint("[bold]Community & Enterprise Gateway:[/bold]")
    rprint("  • GitHub: [blue]https://github.com/benni-os/reality-lock[/blue]")
    rprint("  • Benni Master OS: [blue]https://bennios.dev[/blue]")
    rprint("  • Docs & Patterns: [blue]https://docs.bennios.dev[/blue]\n")


@cli.command("verify-cmd")
@click.argument("command")
@click.option("--cwd", default=None, help="Working directory for the command.")
@click.option("--risk", default="external_mutation", help="Risk level: read_only, isolated_write, external_mutation, critical_auth_finance.")
def verify_cmd(command: str, cwd: Optional[str], risk: str):
    """Executes a command under Reality Lock and inspects the evidence receipt."""
    _print_branding()
    risk_level = RiskLevel(risk.lower())
    engine = RealityLockEngine(strict_mode=False)

    console.print(f"[bold yellow]Executing and locking command:[/bold yellow] [dim]{command}[/dim]\n")
    evidence = engine.lock_command(cmd=command, cwd=cwd, risk_level=risk_level)

    receipt = engine.ledger[-1]
    table = Table(title="Execution Evidence Receipt", border_style="cyan")
    table.add_column("Property", style="bold white")
    table.add_column("Value", style="green")

    table.add_row("Receipt ID", receipt.receipt_id)
    table.add_row("State", receipt.state.value)
    table.add_row("Verified Evidence?", "✅ YES" if receipt.verified else "❌ NO (Hallucination Detected)")
    table.add_row("Exit Code", str(evidence.evidence_data.get("exit_code", "N/A")))
    table.add_row("Duration", f"{receipt.duration_ms:.2f} ms")
    table.add_row("Payload SHA-256", receipt.payload_hash[:16] + "...")
    table.add_row("Receipt Seal SHA-256", (receipt.receipt_hash or "")[:16] + "...")

    console.print(table)
    if not receipt.verified:
        console.print(f"\n[bold red]Error / Invariant Violation:[/bold red] {receipt.error}")


@cli.command("audit")
@click.argument("ledger_file", type=click.Path(), required=False, default=".reality_ledger.jsonl")
def audit(ledger_file: str):
    """Reads a receipt ledger file and prints an executive audit dashboard."""
    _print_branding()
    p = Path(ledger_file)
    if not p.exists():
        console.print(f"[yellow]No ledger file found at {p}. Run some locked actions first![/yellow]")
        return

    receipts = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    receipts.append(json.loads(line))
                except Exception:
                    pass

    total = len(receipts)
    verified = sum(1 for r in receipts if r.get("verified", False))
    rejected = sum(1 for r in receipts if r.get("state") == "rejected")
    tampered = sum(1 for r in receipts if not r.get("receipt_hash"))

    table = Table(title=f"Reality Lock Audit Summary — {p.name}", border_style="green")
    table.add_column("Metric", style="bold white")
    table.add_column("Count", justify="right", style="cyan")

    table.add_row("Total Actions Intercepted", str(total))
    table.add_row("Verified Evidences", f"[green]{verified}[/green]")
    table.add_row("Hallucinations / Blocked Actions", f"[red]{rejected}[/red]")
    table.add_row("Unsealed / Tampered Receipts", f"[yellow]{tampered}[/yellow]")
    table.add_row("Integrity Enforcement Rate", f"{(verified / total * 100):.1f}%" if total > 0 else "0.0%")

    console.print(table)
    console.print("\n[dim]To unlock sovereign multi-agent swarm telemetry, inspect Benni OS.[/dim]")


@cli.command("init")
def init():
    """Generates a default reality_lock.config.json in the current working directory."""
    _print_branding()
    config = {
        "$schema": "https://bennios.dev/schemas/reality-lock-v1.json",
        "system": "Benni Master OS Reality Lock",
        "version": "1.0.0",
        "policy": {
            "default_deny": True,
            "mode": "interactive",
            "require_approval_threshold": "external_mutation",
            "allowed_actions": ["status_check", "read_logs", "list_directory"],
            "denied_actions": ["drop_database", "delete_all", "export_private_keys"],
        },
        "verifiers": {
            "command": {"expected_exit_code": 0, "timeout_seconds": 30.0},
            "filesystem": {"track_sha256": True},
            "http": {"allowed_status_codes": [200, 201, 202, 204]},
        },
        "ledger": {
            "path": ".reality_ledger.jsonl",
            "persist": True,
        },
    }
    target = Path("reality_lock.config.json")
    if target.exists():
        console.print("[yellow]reality_lock.config.json already exists in current directory.[/yellow]")
        return

    with open(target, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    console.print(f"[bold green]✔ Initialized configuration at[/bold green] [cyan]{target.resolve()}[/cyan]")


if __name__ == "__main__":
    cli()
