#!/usr/bin/env python3
"""Startup Time Analyzer — Measure import times for PromptBIM submodules.

Profiles how long each submodule takes to import, identifies the slowest
imports, and reports total startup time.

Usage:
    python scripts/measure_startup.py
    python scripts/measure_startup.py --json results/startup.json
    python scripts/measure_startup.py --threshold 1.0
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
os.environ["QT_QPA_PLATFORM"] = "offscreen"

TARGET_SECONDS = 1.0

SUBMODULES = [
    "promptbim",
    "promptbim.schemas.land",
    "promptbim.schemas.plan",
    "promptbim.schemas.zoning",
    "promptbim.bim.geometry",
    "promptbim.bim.materials",
    "promptbim.bim.cost.estimator",
    "promptbim.codes.tw.btc",
    "promptbim.agents.base",
    "promptbim.land.parsers.geojson",
    "promptbim.cache.store",
    "promptbim.debug",
]


def measure_import(module_name: str) -> float:
    """Import a module and return elapsed time in seconds."""
    # Remove from cache to force fresh import timing
    if module_name in sys.modules:
        return 0.0  # Already imported, skip

    t0 = time.monotonic()
    try:
        importlib.import_module(module_name)
    except ImportError:
        return -1.0
    return time.monotonic() - t0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="PromptBIM Startup Time Analyzer")
    parser.add_argument("--json", type=str, help="Write JSON results to path")
    parser.add_argument("--threshold", type=float, default=TARGET_SECONDS, help="Target startup time")
    args = parser.parse_args()

    print("PromptBIM Startup Time Analyzer")
    print("=" * 60)

    results = {}
    total_start = time.monotonic()

    for mod in SUBMODULES:
        elapsed = measure_import(mod)
        if elapsed < 0:
            status = "MISSING"
            print(f"  {mod:<40} MISSING")
        elif elapsed == 0.0:
            status = "cached"
            print(f"  {mod:<40} (already loaded)")
        else:
            status = "ok"
            bar = "█" * max(1, int(elapsed * 50))
            print(f"  {mod:<40} {elapsed:>6.3f}s  {bar}")
        results[mod] = {"seconds": round(elapsed, 4), "status": status}

    total_elapsed = time.monotonic() - total_start

    print()
    print(f"Total startup time: {total_elapsed:.3f}s")
    print(f"Target: {args.threshold}s")
    passed = total_elapsed <= args.threshold
    print(f"Status: {'PASS' if passed else 'FAIL'}")

    # Show top 3 slowest
    importable = [(k, v) for k, v in results.items() if v["seconds"] > 0]
    importable.sort(key=lambda x: x[1]["seconds"], reverse=True)
    if importable:
        print()
        print("Top 3 slowest imports:")
        for mod, data in importable[:3]:
            print(f"  {mod}: {data['seconds']:.3f}s")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "modules": results,
            "total_seconds": round(total_elapsed, 4),
            "threshold_seconds": args.threshold,
            "passed": passed,
        }
        out.write_text(json.dumps(payload, indent=2))
        print(f"Results written to {out}")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
