#!/usr/bin/env python3
"""Pipeline Benchmark Script — Measure PromptBIM pipeline latency.

Runs the core pipeline stages (parse, plan, generate, check, cost) with
sample data and reports per-stage timing.  Optionally writes JSON output
for CI consumption (``--json <path>``).

Usage:
    python scripts/benchmark_pipeline.py
    python scripts/benchmark_pipeline.py --json results/benchmark.json
    python scripts/benchmark_pipeline.py --threshold 5.0
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

TARGET_SECONDS = 5.0


def timed(label: str):
    """Context manager that prints elapsed time."""

    class Timer:
        def __init__(self):
            self.elapsed = 0.0

        def __enter__(self):
            self.start = time.monotonic()
            return self

        def __exit__(self, *args):
            self.elapsed = time.monotonic() - self.start
            print(f"  {label}: {self.elapsed:.3f}s")

    return Timer()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="PromptBIM Pipeline Benchmark")
    parser.add_argument("--json", type=str, help="Write JSON results to this path")
    parser.add_argument(
        "--threshold",
        type=float,
        default=TARGET_SECONDS,
        help=f"Fail if total exceeds this (default {TARGET_SECONDS}s)",
    )
    args = parser.parse_args()

    print("PromptBIM Pipeline Benchmark")
    print("=" * 50)

    results = {}

    # Stage 1: Import time
    with timed("Module import") as t:
        import promptbim  # noqa: F401
    results["import"] = t.elapsed

    # Stage 2: Schema validation
    with timed("Schema parse") as t:
        from promptbim.schemas.land import LandParcel

        land = LandParcel(
            name="Benchmark Plot",
            boundary=[(0, 0), (20, 0), (20, 15), (0, 15)],
            area_sqm=300.0,
            source_type="manual",
        )
        assert land.area_sqm == 300.0
    results["schema"] = t.elapsed

    # Stage 3: Geometry
    with timed("Geometry (poly_area)") as t:
        from promptbim.bim.geometry import poly_area

        for _ in range(1000):
            poly_area([(0, 0), (20, 0), (20, 15), (0, 15)])
    results["geometry_1k"] = t.elapsed

    # Stage 4: Cost estimator init
    with timed("Cost estimator init") as t:
        from promptbim.bim.cost.estimator import CostEstimator

        estimator = CostEstimator()
        assert estimator is not None
    results["cost_init"] = t.elapsed

    # Stage 5: Compliance engine init
    with timed("Compliance engine init") as t:
        from promptbim.codes.tw.btc import TWBuildingTechCode

        engine = TWBuildingTechCode()
        assert engine is not None
    results["compliance_init"] = t.elapsed

    print()
    print("Summary")
    print("-" * 50)
    total = sum(results.values())
    for stage, elapsed in results.items():
        pct = elapsed / total * 100 if total > 0 else 0
        bar = "#" * int(pct / 2)
        print(f"  {stage:<20} {elapsed:>7.3f}s  {pct:>5.1f}%  {bar}")
    print(f"  {'TOTAL':<20} {total:>7.3f}s")
    print()

    passed = total <= args.threshold
    if passed:
        print(f"OK: Pipeline startup within {args.threshold}s target.")
    else:
        print(f"FAIL: Pipeline startup {total:.2f}s exceeds {args.threshold}s target!")

    # JSON output for CI
    if args.json:
        out_path = Path(args.json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "stages": {k: round(v, 4) for k, v in results.items()},
            "total_seconds": round(total, 4),
            "threshold_seconds": args.threshold,
            "passed": passed,
        }
        out_path.write_text(json.dumps(payload, indent=2))
        print(f"Results written to {out_path}")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
