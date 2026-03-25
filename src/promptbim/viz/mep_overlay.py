"""MEP 3D overlay — four-colour pipe/duct visualisation using PyVista.

Each MEP system is rendered in a distinct colour:
- Plumbing:        blue   (0.2, 0.4, 0.8)
- Electrical:      red    (0.8, 0.2, 0.2)
- HVAC:            green  (0.2, 0.8, 0.2)
- Fire Protection: yellow (0.8, 0.8, 0.0)
"""

from __future__ import annotations

import numpy as np
import pyvista as pv

from promptbim.bim.mep.planner import MEPPlan
from promptbim.bim.mep.systems import SYSTEM_COLORS


def _color_hex(rgb: tuple[float, float, float]) -> str:
    return f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"


def build_mep_meshes(
    mep_plan: MEPPlan,
) -> dict[str, list[tuple[pv.PolyData, str, str]]]:
    """Build PyVista meshes for all MEP routes, grouped by system.

    Returns dict: system_name -> list of (polydata, color_hex, label).
    """
    result: dict[str, list[tuple[pv.PolyData, str, str]]] = {
        "plumbing": [],
        "electrical": [],
        "hvac": [],
        "fire_protection": [],
    }

    seg_counter = 0
    for route in mep_plan.routes:
        if not route.path.segments:
            continue

        color = _color_hex(SYSTEM_COLORS.get(route.system, (0.5, 0.5, 0.5)))
        radius_m = route.diameter_mm / 2000.0

        for seg in route.path.segments:
            mesh = _segment_to_polydata(seg.start, seg.end, radius_m)
            if mesh is not None:
                label = f"mep_{route.system}_{seg_counter}"
                result.setdefault(route.system, []).append((mesh, color, label))
            seg_counter += 1

    return result


def build_mep_flat(mep_plan: MEPPlan) -> list[tuple[pv.PolyData, str, str]]:
    """Build MEP meshes as a flat list (for simple overlay)."""
    grouped = build_mep_meshes(mep_plan)
    flat: list[tuple[pv.PolyData, str, str]] = []
    for meshes in grouped.values():
        flat.extend(meshes)
    return flat


def _segment_to_polydata(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
) -> pv.PolyData | None:
    """Create a tube/box mesh for a single pipe segment."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = (dx ** 2 + dy ** 2 + dz ** 2) ** 0.5
    if length < 1e-6:
        return None

    # Create a line and tube it
    line = pv.Line(start, end)
    try:
        tube = line.tube(radius=max(radius, 0.02), n_sides=8)
        return tube
    except Exception:
        # Fallback: just return the line as-is
        return line
