"""Cache key computation using SHA-256."""

from __future__ import annotations

import hashlib
import json


def compute_cache_key(prompt: str, land, zoning) -> str:
    """Compute a SHA-256 cache key from prompt + land + zoning.

    Normalizes inputs for consistent hashing.
    """
    parts = {
        "prompt": prompt.strip().lower(),
        "land_boundary": _normalize_coords(land.boundary) if land else [],
        "land_area": round(land.area_sqm, 2) if land else 0,
        "zoning": {
            "far": zoning.far_limit if zoning else 2.0,
            "bcr": zoning.bcr_limit if zoning else 0.6,
            "height": zoning.height_limit_m if zoning else 15.0,
        },
    }
    raw = json.dumps(parts, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _normalize_coords(coords: list) -> list:
    """Round coordinates to avoid floating point noise."""
    return [(round(x, 4), round(y, 4)) for x, y in coords]
