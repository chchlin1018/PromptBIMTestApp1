#!/usr/bin/env python3
"""Zigma Demo-1 Asset Downloader v1.0

Automates download of PBR textures and HDRI from Poly Haven (CC0).
Prints manual download instructions for Sketchfab GLB models.

Usage:
    cd ~/Documents/MyProjects/PromptBIMTestApp1
    conda activate promptbim
    python scripts/download_assets.py                    # red priority only
    python scripts/download_assets.py --priority all     # everything
    python scripts/download_assets.py --dry-run          # list only
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

# ============================================================
# Sketchfab models (manual download — needs login for GLB)
# ============================================================
SKETCHFAB_MODELS = {
    "CE-001": {
        "name": "Construction Equipment LowPoly Pack (7+ machines)",
        "author": "GOGA (@gigabate)",
        "url": "https://sketchfab.com/3d-models/construction-equipment-lowpoly-free-3d-models-dcd9c8edd2cd4ed3bee650a82e3f091d",
        "license": "CC-BY-4.0",
        "priority": "red",
        "category": "construction",
        "output": "assets/models/construction/CE-001_construction_pack.glb",
    },
    "CE-006": {
        "name": "Tower Crane HD",
        "author": "Chamod1999",
        "url": "https://sketchfab.com/3d-models/tower-crane-49851dc7a51b43bda6aea06856c26a85",
        "license": "CC-BY-4.0",
        "priority": "yellow",
        "category": "construction",
        "output": "assets/models/construction/CE-006_tower_crane_hd.glb",
    },
    "CE-007": {
        "name": "Mobile Crane",
        "author": "(pick from search)",
        "url": "https://sketchfab.com/search?q=mobile+crane&type=models&downloadable=true&sort_by=-likeCount",
        "license": "CC-BY-4.0",
        "priority": "red",
        "category": "construction",
        "output": "assets/models/construction/CE-007_mobile_crane.glb",
    },
    "CE-008": {
        "name": "Dump Truck",
        "author": "(pick from search)",
        "url": "https://sketchfab.com/search?q=dump+truck+construction&type=models&downloadable=true&sort_by=-likeCount",
        "license": "CC-BY-4.0",
        "priority": "red",
        "category": "construction",
        "output": "assets/models/construction/CE-008_dump_truck.glb",
    },
    "IE-001": {
        "name": "Air-Cooled Chiller",
        "author": "chillerkirala",
        "url": "https://sketchfab.com/3d-models/chiller-air-cooled-industrial-unit-cc833e9118aa4f35a8d5f9964809fd73",
        "license": "CC-BY-4.0",
        "priority": "red",
        "category": "industrial",
        "output": "assets/models/industrial/IE-001_chiller.glb",
    },
    "IE-002": {
        "name": "Cooling Tower",
        "author": "(pick from search)",
        "url": "https://sketchfab.com/search?q=cooling+tower+industrial&type=models&downloadable=true&sort_by=-likeCount",
        "license": "CC-BY-4.0",
        "priority": "red",
        "category": "industrial",
        "output": "assets/models/industrial/IE-002_cooling_tower.glb",
    },
    "IE-003": {
        "name": "Chiller Plant System",
        "author": "geppettomaster",
        "url": "https://sketchfab.com/3d-models/chiller-plant-system-design-sample-vii-8bf1ced3ddc7434ba03005e76dfacc00",
        "license": "CC-BY-4.0",
        "priority": "yellow",
        "category": "industrial",
        "output": "assets/models/industrial/IE-003_chiller_plant.glb",
    },
    "IE-004": {
        "name": "Rooftop AHU",
        "author": "(pick from search)",
        "url": "https://sketchfab.com/search?q=rooftop+AHU+HVAC&type=models&downloadable=true&sort_by=-likeCount",
        "license": "CC-BY-4.0",
        "priority": "red",
        "category": "industrial",
        "output": "assets/models/industrial/IE-004_ahu.glb",
    },
    "IE-006": {
        "name": "Transformer",
        "author": "(pick from search)",
        "url": "https://sketchfab.com/search?q=electrical+transformer&type=models&downloadable=true&sort_by=-likeCount",
        "license": "CC-BY-4.0",
        "priority": "yellow",
        "category": "industrial",
        "output": "assets/models/industrial/IE-006_transformer.glb",
    },
    "IE-007": {
        "name": "Generator",
        "author": "(pick from search)",
        "url": "https://sketchfab.com/search?q=diesel+generator+industrial&type=models&downloadable=true&sort_by=-likeCount",
        "license": "CC-BY-4.0",
        "priority": "yellow",
        "category": "industrial",
        "output": "assets/models/industrial/IE-007_generator.glb",
    },
    "IE-009": {
        "name": "Cleanroom FFU",
        "author": "(pick from search)",
        "url": "https://sketchfab.com/search?q=cleanroom+fan+filter+unit&type=models&downloadable=true",
        "license": "CC-BY-4.0",
        "priority": "red",
        "category": "industrial",
        "output": "assets/models/industrial/IE-009_ffu.glb",
    },
    "IE-010": {
        "name": "Overhead Crane (Factory)",
        "author": "(pick from search)",
        "url": "https://sketchfab.com/search?q=overhead+crane+industrial+factory&type=models&downloadable=true&sort_by=-likeCount",
        "license": "CC-BY-4.0",
        "priority": "red",
        "category": "industrial",
        "output": "assets/models/industrial/IE-010_overhead_crane.glb",
    },
    "BR-001": {
        "name": "Elevator",
        "author": "(pick from search)",
        "url": "https://sketchfab.com/search?q=elevator+lift+building&type=models&downloadable=true&sort_by=-likeCount",
        "license": "CC-BY-4.0",
        "priority": "yellow",
        "category": "building",
        "output": "assets/models/building/BR-001_elevator.glb",
    },
    "BR-003": {
        "name": "Toilet",
        "author": "(pick from search)",
        "url": "https://sketchfab.com/search?q=toilet+bathroom&type=models&downloadable=true&sort_by=-likeCount",
        "license": "CC0",
        "priority": "yellow",
        "category": "building",
        "output": "assets/models/building/BR-003_toilet.glb",
    },
    "BR-010": {
        "name": "Door",
        "author": "(pick from search)",
        "url": "https://sketchfab.com/search?q=door+architectural&type=models&downloadable=true&sort_by=-likeCount",
        "license": "CC0",
        "priority": "yellow",
        "category": "building",
        "output": "assets/models/building/BR-010_door.glb",
    },
    "BR-011": {
        "name": "Window",
        "author": "(pick from search)",
        "url": "https://sketchfab.com/search?q=window+architectural&type=models&downloadable=true&sort_by=-likeCount",
        "license": "CC0",
        "priority": "yellow",
        "category": "building",
        "output": "assets/models/building/BR-011_window.glb",
    },
}

# ============================================================
# Poly Haven textures (auto-downloadable via API)
# ============================================================
POLYHAVEN_TEXTURES = {
    "TX-001": {"slug": "concrete_wall_008", "name": "Concrete Wall", "priority": "red"},
    "TX-002": {"slug": "concrete_floor_02", "name": "Concrete Floor", "priority": "red"},
    "TX-003": {"slug": "metal_plate", "name": "Metal Plate", "priority": "red"},
    "TX-004": {"slug": "corrugated_iron", "name": "Corrugated Steel", "priority": "red"},
    "TX-005": {"slug": "glass_window_002", "name": "Glass Window", "priority": "yellow"},
    "TX-006": {"slug": "wood_floor_deck", "name": "Wood Floor", "priority": "yellow"},
    "TX-007": {"slug": "white_plaster", "name": "White Plaster", "priority": "yellow"},
    "TX-008": {"slug": "large_square_tiles", "name": "Ceramic Tiles", "priority": "yellow"},
    "TX-009": {"slug": "asphalt_04", "name": "Asphalt", "priority": "yellow"},
    "TX-010": {"slug": "grass_path_2", "name": "Grass", "priority": "green"},
}

POLYHAVEN_HDRI = {
    "HD-001": {"slug": "industrial_sunset_02_puresky", "name": "Industrial Sunset", "priority": "red"},
    "HD-002": {"slug": "kloofendal_48d_partly_cloudy_puresky", "name": "Partly Cloudy", "priority": "red"},
    "HD-003": {"slug": "photo_studio_loft_hall", "name": "Studio Loft", "priority": "yellow"},
}

RESOLUTION = "1k"


def download_polyhaven_texture(slug: str, output_dir: Path) -> bool:
    """Download Poly Haven PBR texture set."""
    api_url = f"https://api.polyhaven.com/files/{slug}"
    try:
        with urllib.request.urlopen(api_url, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  \u274c API failed: {e}")
        return False

    tex_dir = output_dir / slug
    tex_dir.mkdir(parents=True, exist_ok=True)
    maps = ["Diffuse", "Color", "Normal", "Roughness", "AO", "Displacement"]
    ok = 0
    for m in maps:
        if m not in data:
            continue
        res = data[m].get(RESOLUTION, data[m].get("1k"))
        if not res:
            continue
        fmt = "png" if "png" in res else next(iter(res), None)
        if not fmt or fmt not in res:
            continue
        url = res[fmt].get("url")
        if not url:
            continue
        out = tex_dir / f"{slug}_{m.lower()}.{fmt}"
        if out.exists():
            print(f"  \u2713 {out.name} (exists)")
            ok += 1
            continue
        print(f"  \u2b07\ufe0f  {m} -> {out.name} ...")
        try:
            urllib.request.urlretrieve(url, str(out))
            print(f"  \u2705 {out.name} ({out.stat().st_size // 1024}KB)")
            ok += 1
        except Exception as e:
            print(f"  \u274c {m}: {e}")
    return ok > 0


def download_polyhaven_hdri(slug: str, output_dir: Path) -> bool:
    """Download Poly Haven HDRI."""
    api_url = f"https://api.polyhaven.com/files/{slug}"
    try:
        with urllib.request.urlopen(api_url, timeout=30) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  \u274c API failed: {e}")
        return False
    if "hdri" not in data:
        print(f"  \u26a0\ufe0f {slug} no hdri data")
        return False
    res = data["hdri"].get(RESOLUTION, data["hdri"].get("1k"))
    if not res or "hdr" not in res:
        return False
    url = res["hdr"].get("url")
    if not url:
        return False
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / f"{slug}_{RESOLUTION}.hdr"
    if out.exists():
        print(f"  \u2713 {out.name} (exists)")
        return True
    print(f"  \u2b07\ufe0f  HDRI -> {out.name} ...")
    try:
        urllib.request.urlretrieve(url, str(out))
        print(f"  \u2705 {out.name} ({out.stat().st_size // 1024}KB)")
        return True
    except Exception as e:
        print(f"  \u274c {e}")
        return False


def main():
    p = argparse.ArgumentParser(description="Zigma Demo-1 Asset Downloader")
    p.add_argument("--priority", choices=["red", "yellow", "green", "all"], default="red")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--output-dir", default="assets")
    args = p.parse_args()

    base = Path(args.output_dir)
    for d in ["models/construction", "models/industrial", "models/building", "textures", "hdri"]:
        (base / d).mkdir(parents=True, exist_ok=True)

    print("\U0001f3d7\ufe0f  Zigma Demo-1 Asset Downloader v1.0")
    print(f"\U0001f4c1 Output: {base.resolve()}")
    print(f"\U0001f3af Priority: {args.priority}\n")

    stats = {"auto": 0, "fail": 0, "manual": 0}

    # Poly Haven Textures
    print("=" * 50)
    print("\U0001f3a8 PBR Textures (Poly Haven CC0)")
    print("=" * 50)
    for tid, info in POLYHAVEN_TEXTURES.items():
        if args.priority != "all" and info["priority"] != args.priority:
            continue
        e = {"red": "\U0001f534", "yellow": "\U0001f7e1", "green": "\U0001f7e2"}.get(info["priority"], "")
        print(f"\n{e} {tid}: {info['name']} ({info['slug']})")
        if args.dry_run:
            continue
        if download_polyhaven_texture(info["slug"], base / "textures"):
            stats["auto"] += 1
        else:
            stats["fail"] += 1

    # Poly Haven HDRI
    print("\n" + "=" * 50)
    print("\U0001f305 HDRI (Poly Haven CC0)")
    print("=" * 50)
    for hid, info in POLYHAVEN_HDRI.items():
        if args.priority != "all" and info["priority"] != args.priority:
            continue
        e = {"red": "\U0001f534", "yellow": "\U0001f7e1"}.get(info["priority"], "")
        print(f"\n{e} {hid}: {info['name']} ({info['slug']})")
        if args.dry_run:
            continue
        if download_polyhaven_hdri(info["slug"], base / "hdri"):
            stats["auto"] += 1
        else:
            stats["fail"] += 1

    # Sketchfab (manual)
    print("\n" + "=" * 50)
    print("\U0001f4e6 Sketchfab GLB Models (manual download)")
    print("=" * 50)
    print("Login to Sketchfab -> Download glTF -> save to path:\n")
    for mid, info in SKETCHFAB_MODELS.items():
        if args.priority != "all" and info["priority"] != args.priority:
            continue
        e = {"red": "\U0001f534", "yellow": "\U0001f7e1", "green": "\U0001f7e2"}.get(info["priority"], "")
        exists = "\u2705" if Path(info["output"]).exists() else "\u2b1c"
        print(f"  {e} {exists} {mid}: {info['name']}")
        print(f"     URL: {info['url']}")
        print(f"     Save: {info['output']}")
        print()
        stats["manual"] += 1

    # Summary
    print("=" * 50)
    print("\U0001f4ca Summary")
    print("=" * 50)
    print(f"  \u2705 Auto-downloaded: {stats['auto']}")
    print(f"  \u274c Failed: {stats['fail']}")
    print(f"  \U0001f464 Manual (Sketchfab): {stats['manual']}")


if __name__ == "__main__":
    main()
