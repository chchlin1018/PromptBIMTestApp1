"""Factory/industrial building template — generates a factory BuildingPlan on a given land parcel."""

from __future__ import annotations

from promptbim.schemas.plan import (
    BuildingPlan,
    OpeningDef,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)


def generate_factory_plan(
    land_boundary: list[tuple[float, float]],
    buildable_area: list[tuple[float, float]],
    num_stories: int = 1,
    name: str = "Factory Building",
) -> BuildingPlan:
    """Generate a factory/industrial building plan.

    Typical factory layout:
    - Single or two-storey
    - Large open production hall
    - Attached office wing
    - Loading dock area
    - Gable roof for the main hall
    """
    xs = [p[0] for p in buildable_area] if buildable_area else [p[0] for p in land_boundary]
    ys = [p[1] for p in buildable_area] if buildable_area else [p[1] for p in land_boundary]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Factory uses large footprint
    total_width = (max_x - min_x) * 0.85
    total_depth = (max_y - min_y) * 0.7
    total_width = min(total_width, 80.0)
    total_depth = min(total_depth, 40.0)

    ox = min_x + ((max_x - min_x) - total_width) / 2
    oy = min_y + ((max_y - min_y) - total_depth) / 2

    # Split: main hall (70%) + office wing (30%)
    hall_width = total_width * 0.7
    office_width = total_width * 0.3

    hall_footprint = [
        (ox, oy), (ox + hall_width, oy),
        (ox + hall_width, oy + total_depth), (ox, oy + total_depth),
    ]
    office_footprint = [
        (ox + hall_width, oy), (ox + total_width, oy),
        (ox + total_width, oy + total_depth), (ox + hall_width, oy + total_depth),
    ]
    full_footprint = [
        (ox, oy), (ox + total_width, oy),
        (ox + total_width, oy + total_depth), (ox, oy + total_depth),
    ]

    stories: list[StoryPlan] = []

    # Ground floor — main production hall + office
    hall_height = 6.0 if num_stories == 1 else 4.5
    walls: list[WallDef] = []
    spaces: list[SpaceDef] = []
    openings: list[OpeningDef] = []

    # Full exterior
    ext_walls = [
        WallDef(start=(ox, oy), end=(ox + total_width, oy), thickness_m=0.3, wall_type="exterior"),
        WallDef(start=(ox + total_width, oy), end=(ox + total_width, oy + total_depth), thickness_m=0.3, wall_type="exterior"),
        WallDef(start=(ox + total_width, oy + total_depth), end=(ox, oy + total_depth), thickness_m=0.3, wall_type="exterior"),
        WallDef(start=(ox, oy + total_depth), end=(ox, oy), thickness_m=0.3, wall_type="exterior"),
    ]
    walls.extend(ext_walls)

    # Dividing wall between hall and office
    walls.append(WallDef(
        start=(ox + hall_width, oy),
        end=(ox + hall_width, oy + total_depth),
        thickness_m=0.25,
        wall_type="interior",
    ))

    # Production hall
    spaces.append(SpaceDef(
        name="Production Hall",
        boundary=hall_footprint,
        space_type="office",  # closest generic type
        area_sqm=hall_width * total_depth,
    ))

    # Office rooms in the office wing
    office_rooms = 3
    office_room_depth = total_depth / office_rooms
    for r in range(office_rooms):
        ry = oy + r * office_room_depth
        room_name = ["Office", "Meeting Room", "Storage"][r]
        spaces.append(SpaceDef(
            name=f"{room_name} 1F",
            boundary=[
                (ox + hall_width, ry), (ox + total_width, ry),
                (ox + total_width, ry + office_room_depth), (ox + hall_width, ry + office_room_depth),
            ],
            space_type="office" if r < 2 else "corridor",
            area_sqm=office_width * office_room_depth,
        ))
        if r > 0:
            walls.append(WallDef(
                start=(ox + hall_width, ry),
                end=(ox + total_width, ry),
                wall_type="partition",
            ))

    # Large roller door on south wall
    openings.append(OpeningDef(
        wall_index=0, offset_m=hall_width * 0.3, width_m=5.0, height_m=4.0,
        sill_height_m=0.0, opening_type="door",
    ))
    # Windows on office wing
    for r in range(office_rooms):
        openings.append(OpeningDef(
            wall_index=1, offset_m=r * office_room_depth + 2.0, width_m=2.0, height_m=1.5,
            sill_height_m=0.9, opening_type="window",
        ))

    stories.append(StoryPlan(
        name="1F",
        elevation_m=0.0,
        height_m=hall_height,
        walls=walls,
        spaces=spaces,
        openings=openings,
        slab_boundary=full_footprint,
    ))

    # Optional second floor (office wing only)
    if num_stories >= 2:
        walls2: list[WallDef] = []
        spaces2: list[SpaceDef] = []
        openings2: list[OpeningDef] = []

        # Only the office wing has a second floor
        ext2 = [
            WallDef(start=(ox + hall_width, oy), end=(ox + total_width, oy), wall_type="exterior"),
            WallDef(start=(ox + total_width, oy), end=(ox + total_width, oy + total_depth), wall_type="exterior"),
            WallDef(start=(ox + total_width, oy + total_depth), end=(ox + hall_width, oy + total_depth), wall_type="exterior"),
            WallDef(start=(ox + hall_width, oy + total_depth), end=(ox + hall_width, oy), wall_type="exterior"),
        ]
        walls2.extend(ext2)

        spaces2.append(SpaceDef(
            name="Upper Office 2F",
            boundary=office_footprint,
            space_type="office",
            area_sqm=office_width * total_depth,
        ))

        stories.append(StoryPlan(
            name="2F",
            elevation_m=hall_height,
            height_m=3.2,
            walls=walls2,
            spaces=spaces2,
            openings=openings2,
            slab_boundary=office_footprint,
        ))

    return BuildingPlan(
        name=name,
        land_boundary=land_boundary,
        buildable_area=buildable_area,
        building_footprint=full_footprint,
        stories=stories,
        roof=RoofPlan(roof_type="gable", slope_degrees=15.0, overhang_m=0.5),
    )
