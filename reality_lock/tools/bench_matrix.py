"""Matrix Benchmark Suite for Reality Lock.

Sweeps execution counts across in-memory and JSONL-persisted receipt ledgers
to measure 5-state verification overhead, receipt sealing speed, and throughput.
"""

from __future__ import annotations

import argparse
import json
import statistics
import tempfile
import time
from pathlib import Path
from typing import Any

from reality_lock.core.engine import RealityLockEngine
from reality_lock.core.states import RiskLevel


class BenchMatrixRunner:
    """Executes a multi-mode, multi-scale receipt verification benchmark matrix."""

    def __init__(
        self,
        action_counts: list[int] | None = None,
        modes: list[str] | None = None,
        reps: int = 2,
    ) -> None:
        self.action_counts = action_counts or [25, 100, 250]
        self.modes = modes or ["in_memory", "jsonl_ledger"]
        self.reps = reps

    def _run_once(self, mode: str, n_actions: int) -> float:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            ledger_path = Path(tmp) / "bench_ledger.jsonl" if mode == "jsonl_ledger" else None
            engine = RealityLockEngine(ledger_path=ledger_path, strict_mode=True)
            t0 = time.perf_counter()
            for i in range(n_actions):
                engine.execute(
                    intent=f"bench_action_{i}",
                    action_name="status_check",
                    func=lambda idx=i: {"idx": idx},
                    risk_level=RiskLevel.READ_ONLY,
                )
            return max(1e-6, time.perf_counter() - t0)

    def run_matrix(self) -> dict[str, Any]:
        """Run the benchmark sweep across all modes and action counts."""
        rows: list[dict[str, Any]] = []
        for mode in self.modes:
            for n in self.action_counts:
                samples = [self._run_once(mode, n) for _ in range(self.reps)]
                mean_s = statistics.mean(samples)
                rows.append(
                    {
                        "mode": mode,
                        "actions": n,
                        "total_ms": round(mean_s * 1000.0, 2),
                        "mean_action_ms": round((mean_s * 1000.0) / n, 4),
                        "receipts_per_sec": round(n / mean_s, 1),
                    }
                )
        return {
            "modes": self.modes,
            "action_counts": self.action_counts,
            "reps": self.reps,
            "matrix_results": rows,
            "timestamp": int(time.time()),
        }

    @staticmethod
    def format_markdown_table(data: dict[str, Any]) -> str:
        """Render a Markdown summary table from benchmark matrix results."""
        lines = [
            "# Reality Lock Benchmark Matrix",
            "",
            "| Mode | Actions | Total Time (ms) | Mean Action (ms) | Throughput (receipts/s) |",
            "|---|---:|---:|---:|---:|",
        ]
        for row in data.get("matrix_results", []):
            lines.append(
                f"| {row['mode']} | {row['actions']} | {row['total_ms']} | "
                f"{row['mean_action_ms']} | {row['receipts_per_sec']} |"
            )
        return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Reality Lock benchmark matrix.")
    parser.add_argument("--actions", type=int, nargs="+", default=[25, 100, 250], help="Action counts to sweep.")
    parser.add_argument("--reps", type=int, default=2, help="Repetitions per cell.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    runner = BenchMatrixRunner(action_counts=args.actions, reps=args.reps)
    data = runner.run_matrix()
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(runner.format_markdown_table(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
