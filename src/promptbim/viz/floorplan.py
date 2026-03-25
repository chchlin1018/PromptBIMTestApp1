"""Per-floor SVG plan generation.

Generates clean 2D floor-plan SVGs from a :class:`BuildingPlan`, one
SVG per story.  Walls are drawn as thick lines, spaces are labelled,
and openings (doors/windows) are marked.
"""

from __future__ import annotations

import logging
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from promptbim.schemas.plan import BuildingPlan, OpeningDef, StoryPlan, WallDef

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SVG_NS = "http://www.w3.org/2000/svg"
_SCALE = 50.0  # pixels per metre
_WALL_COLOR = "#333333"
_EXT_WALL_WIDTH = 4.0  # px
_INT_WALL_WIDTH = 2.0
_SPACE_FILL = "#F5F5F5"
_SPACE_STROKE = "#CCCCCC"
_DOOR_COLOR = "#2196F3"
_WINDOW_COLOR = "#4CAF50"
_LABEL_FONT = "Arial, Helvetica, sans-serif"
_LABEL_SIZE = 10
_MARGIN = 40  # px


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bounds(points: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    """Return (min_x, min_y, max_x, max_y) of a point list."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def _polygon_centroid(pts: list[tuple[float, float]]) -> tuple[float, float]:
    """Compute centroid of a simple polygon."""
    n = len(pts)
    if n == 0:
        return (0.0, 0.0)
    cx = sum(p[0] for p in pts) / n
    cy = sum(p[1] for p in pts) / n
    return cx, cy


def _to_svg_coords(
    x: float, y: float, ox: float, oy: float
) -> tuple[float, float]:
    """Convert model coords to SVG pixel coords (Y-flipped)."""
    sx = (x - ox) * _SCALE + _MARGIN
    sy = -(y - oy) * _SCALE + _MARGIN  # flip Y
    return sx, sy


# ---------------------------------------------------------------------------
# SVG generation for a single story
# ---------------------------------------------------------------------------

def _story_svg(story: StoryPlan, footprint: list[tuple[float, float]]) -> str:
    """Generate an SVG string for one story."""
    # Gather all points to compute bounding box
    all_pts: list[tuple[float, float]] = []
    all_pts.extend(footprint)
    for w in story.walls:
        all_pts.append(w.start)
        all_pts.append(w.end)
    for s in story.spaces:
        all_pts.extend(s.boundary)
    if story.slab_boundary:
        all_pts.extend(story.slab_boundary)

    if not all_pts:
        # Empty story — return minimal SVG
        return _empty_svg(story.name)

    min_x, min_y, max_x, max_y = _bounds(all_pts)

    width = (max_x - min_x) * _SCALE + 2 * _MARGIN
    height = (max_y - min_y) * _SCALE + 2 * _MARGIN

    # Build SVG
    root = ET.Element("svg", {
        "xmlns": _SVG_NS,
        "width": f"{width:.0f}",
        "height": f"{height:.0f}",
        "viewBox": f"0 0 {width:.0f} {height:.0f}",
    })

    # Background
    ET.SubElement(root, "rect", {
        "width": "100%",
        "height": "100%",
        "fill": "white",
    })

    # Title
    title = ET.SubElement(root, "text", {
        "x": str(_MARGIN),
        "y": "20",
        "font-family": _LABEL_FONT,
        "font-size": "14",
        "font-weight": "bold",
        "fill": "#333",
    })
    title.text = f"Floor Plan — {story.name} (elev {story.elevation_m:.1f}m)"

    # Draw slab / footprint outline
    outline = story.slab_boundary if story.slab_boundary else footprint
    if outline:
        pts_str = " ".join(
            f"{_to_svg_coords(p[0], p[1], min_x, max_y)[0]:.1f},"
            f"{_to_svg_coords(p[0], p[1], min_x, max_y)[1]:.1f}"
            for p in outline
        )
        ET.SubElement(root, "polygon", {
            "points": pts_str,
            "fill": "#FAFAFA",
            "stroke": "#999",
            "stroke-width": "1",
        })

    # Draw spaces
    for space in story.spaces:
        if not space.boundary:
            continue
        pts_str = " ".join(
            f"{_to_svg_coords(p[0], p[1], min_x, max_y)[0]:.1f},"
            f"{_to_svg_coords(p[0], p[1], min_x, max_y)[1]:.1f}"
            for p in space.boundary
        )
        ET.SubElement(root, "polygon", {
            "points": pts_str,
            "fill": _SPACE_FILL,
            "stroke": _SPACE_STROKE,
            "stroke-width": "1",
            "opacity": "0.6",
        })
        # Space label
        cx, cy = _polygon_centroid(space.boundary)
        sx, sy = _to_svg_coords(cx, cy, min_x, max_y)
        lbl = ET.SubElement(root, "text", {
            "x": f"{sx:.1f}",
            "y": f"{sy:.1f}",
            "font-family": _LABEL_FONT,
            "font-size": str(_LABEL_SIZE),
            "text-anchor": "middle",
            "dominant-baseline": "central",
            "fill": "#666",
        })
        lbl.text = f"{space.name}\n{space.area_sqm:.1f}m²"

    # Draw walls
    for wall in story.walls:
        x1, y1 = _to_svg_coords(wall.start[0], wall.start[1], min_x, max_y)
        x2, y2 = _to_svg_coords(wall.end[0], wall.end[1], min_x, max_y)
        stroke_w = _EXT_WALL_WIDTH if wall.wall_type == "exterior" else _INT_WALL_WIDTH
        ET.SubElement(root, "line", {
            "x1": f"{x1:.1f}",
            "y1": f"{y1:.1f}",
            "x2": f"{x2:.1f}",
            "y2": f"{y2:.1f}",
            "stroke": _WALL_COLOR,
            "stroke-width": f"{stroke_w:.1f}",
            "stroke-linecap": "round",
        })

    # Draw openings
    for opening in story.openings:
        if opening.wall_index >= len(story.walls):
            continue
        wall = story.walls[opening.wall_index]
        dx = wall.end[0] - wall.start[0]
        dy = wall.end[1] - wall.start[1]
        wall_len = math.sqrt(dx * dx + dy * dy)
        if wall_len < 1e-6:
            continue
        ux, uy = dx / wall_len, dy / wall_len
        # Opening centre
        t = opening.offset_m + opening.width_m / 2
        cx = wall.start[0] + ux * t
        cy = wall.start[1] + uy * t
        sx, sy = _to_svg_coords(cx, cy, min_x, max_y)

        # Draw as a coloured rectangle mark
        color = _DOOR_COLOR if opening.opening_type == "door" else _WINDOW_COLOR
        half_w = opening.width_m * _SCALE / 2
        ET.SubElement(root, "rect", {
            "x": f"{sx - half_w:.1f}",
            "y": f"{sy - 3:.1f}",
            "width": f"{2 * half_w:.1f}",
            "height": "6",
            "fill": color,
            "opacity": "0.7",
            "rx": "2",
        })

    # Compass indicator (N arrow)
    arrow_x = width - _MARGIN
    arrow_y = _MARGIN + 10
    ET.SubElement(root, "line", {
        "x1": f"{arrow_x:.0f}",
        "y1": f"{arrow_y + 20:.0f}",
        "x2": f"{arrow_x:.0f}",
        "y2": f"{arrow_y:.0f}",
        "stroke": "#999",
        "stroke-width": "2",
        "marker-end": "",
    })
    n_lbl = ET.SubElement(root, "text", {
        "x": f"{arrow_x:.0f}",
        "y": f"{arrow_y - 4:.0f}",
        "font-family": _LABEL_FONT,
        "font-size": "10",
        "text-anchor": "middle",
        "fill": "#999",
    })
    n_lbl.text = "N"

    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def _empty_svg(name: str) -> str:
    """Return a placeholder SVG for an empty story."""
    root = ET.Element("svg", {
        "xmlns": _SVG_NS,
        "width": "200",
        "height": "100",
        "viewBox": "0 0 200 100",
    })
    ET.SubElement(root, "rect", {"width": "100%", "height": "100%", "fill": "white"})
    txt = ET.SubElement(root, "text", {
        "x": "100",
        "y": "50",
        "text-anchor": "middle",
        "font-family": _LABEL_FONT,
        "font-size": "12",
        "fill": "#999",
    })
    txt.text = f"{name} — no geometry"
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_floorplans(
    plan: BuildingPlan,
    output_dir: str | Path,
) -> list[Path]:
    """Generate one SVG per story, return list of paths.

    Files are named ``floorplan_{story.name}.svg``.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for story in plan.stories:
        svg_content = _story_svg(story, plan.building_footprint)
        # Sanitize filename
        safe_name = story.name.replace("/", "_").replace(" ", "_")
        out_path = output_dir / f"floorplan_{safe_name}.svg"
        out_path.write_text(svg_content, encoding="utf-8")
        paths.append(out_path)
        logger.info("Generated floor plan: %s", out_path)

    return paths


def generate_floorplan_svg_strings(
    plan: BuildingPlan,
) -> dict[str, str]:
    """Generate SVG strings keyed by story name (no file I/O)."""
    result: dict[str, str] = {}
    for story in plan.stories:
        svg_content = _story_svg(story, plan.building_footprint)
        result[story.name] = svg_content
    return result
