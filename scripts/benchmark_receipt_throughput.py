#!/usr/bin/env python3
"""Cryptographic Receipt Sealing & Verification Benchmark.

Measures in-memory vs JSONL-persisted 5-state execution throughput,
receipt sealing latency, and policy gate overhead.

Usage:
    python scripts/benchmark_receipt_throughput.py
    python scripts/benchmark_receipt_throughput.py --actions 25 100 250 --reps 2
    python scripts/benchmark_receipt_throughput.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from reality_lock.tools.bench_matrix import BenchMatrixRunner


def run_benchmark(actions: list[int] | None = None, reps: int = 2) -> dict[str, Any]:
    """Execute the Reality Lock receipt throughput matrix benchmark."""
    runner = BenchMatrixRunner(action_counts=actions or [25, 100, 250], reps=reps)
    return runner.run_matrix()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark Reality Lock receipt throughput.")
    parser.add_argument("--actions", type=int, nargs="+", default=[25, 100, 250], help="Action counts to sweep.")
    parser.add_argument("--reps", type=int, default=2, help="Repetitions per cell.")
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(argv)

    data = run_benchmark(actions=args.actions, reps=args.reps)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(BenchMatrixRunner.format_markdown_table(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
