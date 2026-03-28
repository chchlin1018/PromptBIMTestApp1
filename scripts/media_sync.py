#!/usr/bin/env python3
"""Zigma Media Sync — scan ~/ZigmaMedia and update media/manifest.json.

Usage:
    python scripts/media_sync.py
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

MEDIA_ROOT = Path.home() / "ZigmaMedia"
MANIFEST_PATH = Path(__file__).resolve().parent.parent / "media" / "manifest.json"


def scan_media(root: Path) -> dict:
    """Scan ZigmaMedia directory and build manifest."""
    files = []
    total_size = 0

    if not root.exists():
        print(f"  Warning: {root} does not exist")
        return {"files": [], "total_files": 0, "total_size_mb": 0}

    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        if path.name.startswith("."):
            continue

        rel = path.relative_to(root)
        size = path.stat().st_size
        total_size += size

        category = rel.parts[0] if len(rel.parts) > 1 else "root"
        files.append({
            "path": str(rel),
            "category": category,
            "size_bytes": size,
            "size_kb": round(size / 1024, 1),
        })

    return {
        "version": "1.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "media_root": str(root),
        "total_files": len(files),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "categories": _summarize_categories(files),
        "files": files,
    }


def _summarize_categories(files: list[dict]) -> dict:
    cats: dict[str, dict] = {}
    for f in files:
        c = f["category"]
        if c not in cats:
            cats[c] = {"count": 0, "size_mb": 0.0}
        cats[c]["count"] += 1
        cats[c]["size_mb"] = round(cats[c]["size_mb"] + f["size_bytes"] / (1024 * 1024), 2)
    return cats


def main():
    print(f"Scanning {MEDIA_ROOT} ...")
    manifest = scan_media(MEDIA_ROOT)

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Manifest written: {MANIFEST_PATH}")
    print(f"  Total files: {manifest['total_files']}")
    print(f"  Total size: {manifest['total_size_mb']} MB")
    for cat, info in manifest.get("categories", {}).items():
        print(f"  {cat}: {info['count']} files, {info['size_mb']} MB")


if __name__ == "__main__":
    main()
