#!/usr/bin/env python3
"""Generate API documentation for PromptBIM using pdoc.

Usage:
    pip install pdoc
    python scripts/generate_api_docs.py
    python scripts/generate_api_docs.py --output docs/api
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

# Modules to document (exclude GUI/voice/web which need special deps)
MODULES = [
    "promptbim",
    "promptbim.schemas",
    "promptbim.bim.ifc_generator",
    "promptbim.bim.usd_generator",
    "promptbim.bim.geometry",
    "promptbim.bim.materials",
    "promptbim.bim.cost",
    "promptbim.bim.templates",
    "promptbim.bim.components",
    "promptbim.agents",
    "promptbim.codes",
    "promptbim.land",
    "promptbim.cache",
    "promptbim.config",
    "promptbim.debug",
]


def main():
    parser = argparse.ArgumentParser(description="Generate PromptBIM API docs")
    parser.add_argument("--output", "-o", default="docs/api", help="Output directory")
    parser.add_argument("--format", choices=["html", "markdown"], default="html")
    args = parser.parse_args()

    output_dir = ROOT / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set env to prevent GUI imports
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["PYTHONPATH"] = str(SRC) + os.pathsep + env.get("PYTHONPATH", "")

    print(f"Generating API docs → {output_dir}")

    cmd = [
        sys.executable,
        "-m",
        "pdoc",
        "--output-directory",
        str(output_dir),
    ]

    if args.format == "markdown":
        cmd.append("--format")
        cmd.append("markdown")

    cmd.extend(MODULES)

    result = subprocess.run(cmd, env=env, capture_output=True, text=True)

    if result.returncode == 0:
        # Count generated files
        count = sum(1 for _ in output_dir.rglob("*") if _.is_file())
        print(f"Generated {count} documentation files in {output_dir}")
    else:
        print("pdoc output:")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        print("\nNote: Install pdoc with: pip install pdoc")
        sys.exit(1)


if __name__ == "__main__":
    main()
