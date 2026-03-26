#!/usr/bin/env python3
"""Memory Benchmark — Detect leaks in PromptBIM pipeline stages.

Measures RSS memory before/after each pipeline stage to detect leaks.
Optionally writes JSON for CI (``--json <path>``).

Usage:
    python scripts/benchmark_memory.py
    python scripts/benchmark_memory.py --json results/memory.json
"""

from __future__ import annotations

import gc
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Prevent PySide6 GUI init
os.environ["QT_QPA_PLATFORM"] = "offscreen"

LEAK_THRESHOLD_MB = 50.0


def get_rss_mb() -> float:
    """Get current process RSS in MB (cross-platform)."""
    try:
        import resource

        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)
    except ImportError:
        pass
    # Fallback: read /proc on Linux or use psutil
    try:
        import psutil

        return psutil.Process().memory_info().rss / (1024 * 1024)
    except ImportError:
        return 0.0


def measure_stage(name: str, fn) -> dict:
    """Run fn() and measure memory delta."""
    gc.collect()
    before = get_rss_mb()
    t0 = time.monotonic()
    fn()
    elapsed = time.monotonic() - t0
    gc.collect()
    after = get_rss_mb()
    delta = after - before
    print(f"  {name:<30} {before:>7.1f} -> {after:>7.1f} MB  (Δ{delta:+.1f} MB, {elapsed:.2f}s)")
    return {"before_mb": round(before, 1), "after_mb": round(after, 1), "delta_mb": round(delta, 1), "seconds": round(elapsed, 3)}


def main():
    import argparse

    parser = argparse.ArgumentParser(description="PromptBIM Memory Benchmark")
    parser.add_argument("--json", type=str, help="Write JSON results to path")
    parser.add_argument("--threshold", type=float, default=LEAK_THRESHOLD_MB, help="Max delta MB per stage")
    args = parser.parse_args()

    print("PromptBIM Memory Benchmark")
    print("=" * 70)
    print(f"  {'Stage':<30} {'Before':>7}    {'After':>7}        {'Delta':>7}")
    print("-" * 70)

    results = {}

    # Stage 1: Import
    def _import():
        import promptbim  # noqa: F401

    results["import"] = measure_stage("Module import", _import)

    # Stage 2: Schema creation
    def _schema():
        from promptbim.schemas.land import LandParcel

        for _ in range(100):
            LandParcel(name="P", boundary=[(0, 0), (20, 0), (20, 15), (0, 15)], area_sqm=300.0)

    results["schema_100x"] = measure_stage("Schema create (100x)", _schema)

    # Stage 3: Geometry
    def _geometry():
        from promptbim.bim.geometry import poly_area

        for _ in range(10000):
            poly_area([(0, 0), (20, 0), (20, 15), (0, 15)])

    results["geometry_10k"] = measure_stage("Geometry (10k iterations)", _geometry)

    # Stage 4: Template generation
    def _template():
        from promptbim.bim.templates import generate_from_template

        land = [(0, 0), (40, 0), (40, 30), (0, 30)]
        buildable = [(5, 5), (35, 5), (35, 25), (5, 25)]
        for _ in range(10):
            generate_from_template("school", land, buildable, num_stories=3)

    results["template_10x"] = measure_stage("Template gen (10x)", _template)

    # Stage 5: Cost estimation
    def _cost():
        from promptbim.bim.cost.estimator import CostEstimator
        from promptbim.bim.templates import generate_from_template

        land = [(0, 0), (40, 0), (40, 30), (0, 30)]
        buildable = [(5, 5), (35, 5), (35, 25), (5, 25)]
        plan = generate_from_template("school", land, buildable)
        est = CostEstimator()
        for _ in range(10):
            est.estimate(plan)

    results["cost_10x"] = measure_stage("Cost estimation (10x)", _cost)

    print()
    # Check for leaks
    leaks = []
    for stage, data in results.items():
        if data["delta_mb"] > args.threshold:
            leaks.append(f"{stage}: +{data['delta_mb']}MB")

    if leaks:
        print(f"WARNING: Potential memory leaks detected (>{args.threshold}MB):")
        for leak in leaks:
            print(f"  - {leak}")
    else:
        print(f"OK: No memory leaks detected (all stages <{args.threshold}MB delta)")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "stages": results,
            "threshold_mb": args.threshold,
            "leaks_detected": len(leaks) > 0,
        }
        out.write_text(json.dumps(payload, indent=2))
        print(f"Results written to {out}")

    sys.exit(1 if leaks else 0)


if __name__ == "__main__":
    main()
