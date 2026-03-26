"""Auto-generate structural elements (columns, beams, foundation) from BuildingPlan.

Places RC columns on a regular grid, connects them with beams, and adds
a strip foundation under each ground-floor column.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from promptbim.debug import get_logger
from promptbim.schemas.plan import BuildingPlan

_logger = get_logger("bim.structural")


@dataclass
class StructuralElement:
    """A single structural member."""

    element_type: str  # column, beam, foundation
    start: tuple[float, float, float]  # (x, y, z)
    end: tuple[float, float, float] | None = None  # for beams
    width_m: float = 0.5
    depth_m: float = 0.5
    height_m: float = 3.0
    material: str = "concrete"


@dataclass
class StructuralLayout:
    """Complete structural system for a building."""

    columns: list[StructuralElement] = field(default_factory=list)
    beams: list[StructuralElement] = field(default_factory=list)
    foundations: list[StructuralElement] = field(default_factory=list)
    grid_spacing_x: float = 0.0
    grid_spacing_y: float = 0.0


# Default structural parameters
COLUMN_SIZE = 0.5  # metres
BEAM_WIDTH = 0.3
BEAM_DEPTH = 0.5
GRID_SPACING = 6.0  # typical grid spacing
FOUNDATION_WIDTH = 0.8
FOUNDATION_DEPTH = 1.0


def generate_structural(plan: BuildingPlan) -> StructuralLayout:
    """Generate columns, beams, and foundations for the building."""
    boundary = plan.building_footprint
    if not boundary or len(boundary) < 3:
        return StructuralLayout()

    xs = [p[0] for p in boundary]
    ys = [p[1] for p in boundary]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x
    depth = max_y - min_y

    # Determine grid
    nx = max(2, round(width / GRID_SPACING) + 1)
    ny = max(2, round(depth / GRID_SPACING) + 1)
    dx = width / (nx - 1) if nx > 1 else width
    dy = depth / (ny - 1) if ny > 1 else depth

    layout = StructuralLayout(grid_spacing_x=round(dx, 2), grid_spacing_y=round(dy, 2))

    # Generate column grid for each story
    grid_points = []
    for ix in range(nx):
        for iy in range(ny):
            gx = min_x + ix * dx
            gy = min_y + iy * dy
            grid_points.append((gx, gy))

    for story in plan.stories:
        h = story.height_m
        z = story.elevation_m
        for gx, gy in grid_points:
            layout.columns.append(StructuralElement(
                element_type="column",
                start=(gx, gy, z),
                width_m=COLUMN_SIZE,
                depth_m=COLUMN_SIZE,
                height_m=h,
            ))

        # Beams along X (connect columns in X direction)
        for iy in range(ny):
            for ix in range(nx - 1):
                x0 = min_x + ix * dx
                x1 = min_x + (ix + 1) * dx
                gy = min_y + iy * dy
                beam_z = z + h  # top of story
                layout.beams.append(StructuralElement(
                    element_type="beam",
                    start=(x0, gy, beam_z),
                    end=(x1, gy, beam_z),
                    width_m=BEAM_WIDTH,
                    depth_m=BEAM_DEPTH,
                ))

        # Beams along Y
        for ix in range(nx):
            for iy in range(ny - 1):
                gx = min_x + ix * dx
                y0 = min_y + iy * dy
                y1 = min_y + (iy + 1) * dy
                beam_z = z + h
                layout.beams.append(StructuralElement(
                    element_type="beam",
                    start=(gx, y0, beam_z),
                    end=(gx, y1, beam_z),
                    width_m=BEAM_WIDTH,
                    depth_m=BEAM_DEPTH,
                ))

    # Foundations under ground-floor columns
    for gx, gy in grid_points:
        layout.foundations.append(StructuralElement(
            element_type="foundation",
            start=(gx, gy, -FOUNDATION_DEPTH),
            width_m=FOUNDATION_WIDTH,
            depth_m=FOUNDATION_WIDTH,
            height_m=FOUNDATION_DEPTH,
        ))

    _logger.info(
        "Structural: %d columns, %d beams, %d foundations (grid %dx%d @ %.1fm)",
        len(layout.columns),
        len(layout.beams),
        len(layout.foundations),
        nx,
        ny,
        dx,
    )
    return layout
