"""Auto-generate stairs and elevator shafts based on building stories.

Places a U-shaped stairwell and an elevator shaft at a designated location
within the building footprint, spanning all floors.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from promptbim.debug import get_logger
from promptbim.schemas.plan import BuildingPlan

_logger = get_logger("bim.vertical")


@dataclass
class VerticalElement:
    """A single vertical transport element."""

    element_type: str  # stair_flight, stair_landing, elevator_shaft, elevator_car
    boundary: list[tuple[float, float]]
    base_z: float
    height_m: float
    name: str = ""


@dataclass
class VerticalLayout:
    """Complete vertical transport system for a building."""

    stairs: list[VerticalElement] = field(default_factory=list)
    elevators: list[VerticalElement] = field(default_factory=list)
    stairwell_boundary: list[tuple[float, float]] = field(default_factory=list)
    elevator_shaft_boundary: list[tuple[float, float]] = field(default_factory=list)
    num_stories: int = 0


# Design constants (Taiwan building code compliant)
STAIR_WIDTH = 1.2  # metres (min for safety stair)
STAIR_WELL_WIDTH = 2.8  # two runs + gap
STAIR_WELL_DEPTH = 4.0
LANDING_DEPTH = 1.2
ELEVATOR_SHAFT_WIDTH = 2.1
ELEVATOR_SHAFT_DEPTH = 2.4
RISER_HEIGHT = 0.17  # metres
TREAD_DEPTH = 0.27


def generate_vertical(plan: BuildingPlan) -> VerticalLayout:
    """Generate stairs and elevator shaft for all stories."""
    if not plan.stories or len(plan.stories) < 1:
        return VerticalLayout()

    boundary = plan.building_footprint
    if not boundary or len(boundary) < 3:
        return VerticalLayout()

    # Place stairwell and elevator near the building centroid
    xs = [p[0] for p in boundary]
    ys = [p[1] for p in boundary]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2

    layout = VerticalLayout(num_stories=len(plan.stories))

    # Stairwell position: left of centre
    sw_x0 = cx - STAIR_WELL_WIDTH - 0.5
    sw_y0 = cy - STAIR_WELL_DEPTH / 2
    layout.stairwell_boundary = [
        (sw_x0, sw_y0),
        (sw_x0 + STAIR_WELL_WIDTH, sw_y0),
        (sw_x0 + STAIR_WELL_WIDTH, sw_y0 + STAIR_WELL_DEPTH),
        (sw_x0, sw_y0 + STAIR_WELL_DEPTH),
    ]

    # Elevator shaft position: right of centre
    ev_x0 = cx + 0.5
    ev_y0 = cy - ELEVATOR_SHAFT_DEPTH / 2
    layout.elevator_shaft_boundary = [
        (ev_x0, ev_y0),
        (ev_x0 + ELEVATOR_SHAFT_WIDTH, ev_y0),
        (ev_x0 + ELEVATOR_SHAFT_WIDTH, ev_y0 + ELEVATOR_SHAFT_DEPTH),
        (ev_x0, ev_y0 + ELEVATOR_SHAFT_DEPTH),
    ]

    # Generate per-story elements
    for i, story in enumerate(plan.stories):
        z = story.elevation_m
        h = story.height_m

        # Stair flights (two runs per story in U-shape)
        half_h = h / 2
        # Run 1: lower half
        run1_boundary = [
            (sw_x0, sw_y0),
            (sw_x0 + STAIR_WIDTH, sw_y0),
            (sw_x0 + STAIR_WIDTH, sw_y0 + STAIR_WELL_DEPTH),
            (sw_x0, sw_y0 + STAIR_WELL_DEPTH),
        ]
        layout.stairs.append(VerticalElement(
            element_type="stair_flight",
            boundary=run1_boundary,
            base_z=z,
            height_m=half_h,
            name=f"Stair-{story.name}-Run1",
        ))

        # Landing at mid-level
        landing_boundary = [
            (sw_x0, sw_y0 + STAIR_WELL_DEPTH - LANDING_DEPTH),
            (sw_x0 + STAIR_WELL_WIDTH, sw_y0 + STAIR_WELL_DEPTH - LANDING_DEPTH),
            (sw_x0 + STAIR_WELL_WIDTH, sw_y0 + STAIR_WELL_DEPTH),
            (sw_x0, sw_y0 + STAIR_WELL_DEPTH),
        ]
        layout.stairs.append(VerticalElement(
            element_type="stair_landing",
            boundary=landing_boundary,
            base_z=z + half_h,
            height_m=0.2,
            name=f"Stair-{story.name}-Landing",
        ))

        # Run 2: upper half
        run2_boundary = [
            (sw_x0 + STAIR_WELL_WIDTH - STAIR_WIDTH, sw_y0),
            (sw_x0 + STAIR_WELL_WIDTH, sw_y0),
            (sw_x0 + STAIR_WELL_WIDTH, sw_y0 + STAIR_WELL_DEPTH),
            (sw_x0 + STAIR_WELL_WIDTH - STAIR_WIDTH, sw_y0 + STAIR_WELL_DEPTH),
        ]
        layout.stairs.append(VerticalElement(
            element_type="stair_flight",
            boundary=run2_boundary,
            base_z=z + half_h,
            height_m=half_h,
            name=f"Stair-{story.name}-Run2",
        ))

        # Elevator shaft (full-height per story)
        layout.elevators.append(VerticalElement(
            element_type="elevator_shaft",
            boundary=layout.elevator_shaft_boundary.copy(),
            base_z=z,
            height_m=h,
            name=f"Elevator-{story.name}",
        ))

    _logger.info(
        "Vertical transport: %d stair elements, %d elevator elements, %d stories",
        len(layout.stairs),
        len(layout.elevators),
        layout.num_stories,
    )
    return layout
