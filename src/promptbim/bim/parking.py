"""Auto-generate 1F parking layout from BuildingPlan.

Lays out standard parking bays (2.5m x 5.5m) and a central drive aisle (6m)
within the ground floor slab boundary.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from promptbim.debug import get_logger
from promptbim.schemas.plan import BuildingPlan, SpaceDef

_logger = get_logger("bim.parking")


@dataclass
class ParkingLayout:
    """Result of an auto-parking computation."""

    bays: list[SpaceDef] = field(default_factory=list)
    aisle: SpaceDef | None = None
    ramp: SpaceDef | None = None
    total_bays: int = 0
    accessible_bays: int = 0


# Taiwan regulation constants
BAY_WIDTH = 2.5  # metres
BAY_LENGTH = 5.5
ACCESSIBLE_BAY_WIDTH = 3.5
AISLE_WIDTH = 6.0  # two-way drive aisle
RAMP_WIDTH = 3.5
RAMP_LENGTH = 8.0


def generate_parking(plan: BuildingPlan) -> ParkingLayout:
    """Generate a 1F parking layout within the ground-floor slab boundary."""
    if not plan.stories:
        return ParkingLayout()

    story_1f = plan.stories[0]
    boundary = story_1f.slab_boundary or plan.building_footprint
    if not boundary or len(boundary) < 3:
        return ParkingLayout()

    # Compute axis-aligned bounding box of the slab
    xs = [p[0] for p in boundary]
    ys = [p[1] for p in boundary]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x
    depth = max_y - min_y

    # Place aisle down the centre (along Y axis)
    aisle_x0 = min_x + (width - AISLE_WIDTH) / 2
    aisle_x1 = aisle_x0 + AISLE_WIDTH

    layout = ParkingLayout()

    # Aisle
    layout.aisle = SpaceDef(
        name="Drive Aisle",
        boundary=[
            (aisle_x0, min_y),
            (aisle_x1, min_y),
            (aisle_x1, max_y),
            (aisle_x0, max_y),
        ],
        space_type="corridor",
        area_sqm=round(AISLE_WIDTH * depth, 1),
    )

    # Park bays on both sides of aisle
    bay_id = 0
    for side_x0, direction in [(min_x, 1), (aisle_x1, 1)]:
        avail_width = (aisle_x0 - min_x) if side_x0 == min_x else (max_x - aisle_x1)
        if avail_width < BAY_WIDTH:
            continue
        cols = int(avail_width / BAY_WIDTH)
        rows = int((depth - RAMP_LENGTH) / BAY_LENGTH)

        for r in range(rows):
            for c in range(cols):
                bx = side_x0 + c * BAY_WIDTH
                by = min_y + r * BAY_LENGTH
                bay_id += 1
                is_accessible = bay_id == 1  # First bay is accessible
                w = ACCESSIBLE_BAY_WIDTH if is_accessible else BAY_WIDTH
                bay = SpaceDef(
                    name=f"P{bay_id:02d}" + (" ♿" if is_accessible else ""),
                    boundary=[
                        (bx, by),
                        (bx + min(w, avail_width - c * BAY_WIDTH), by),
                        (bx + min(w, avail_width - c * BAY_WIDTH), by + BAY_LENGTH),
                        (bx, by + BAY_LENGTH),
                    ],
                    space_type="parking",
                    area_sqm=round(w * BAY_LENGTH, 1),
                )
                layout.bays.append(bay)
                if is_accessible:
                    layout.accessible_bays += 1

    layout.total_bays = len(layout.bays)

    # Ramp at south end
    ramp_x = aisle_x0 + (AISLE_WIDTH - RAMP_WIDTH) / 2
    layout.ramp = SpaceDef(
        name="Vehicle Ramp",
        boundary=[
            (ramp_x, max_y - RAMP_LENGTH),
            (ramp_x + RAMP_WIDTH, max_y - RAMP_LENGTH),
            (ramp_x + RAMP_WIDTH, max_y),
            (ramp_x, max_y),
        ],
        space_type="corridor",
        area_sqm=round(RAMP_WIDTH * RAMP_LENGTH, 1),
    )

    _logger.info(
        "Parking layout: %d bays (%d accessible), 1 ramp",
        layout.total_bays,
        layout.accessible_bays,
    )
    return layout
