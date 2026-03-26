"""School building template — generates a school BuildingPlan on a given land parcel."""

from __future__ import annotations

from promptbim.schemas.plan import (
    BuildingPlan,
    OpeningDef,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)


def generate_school_plan(
    land_boundary: list[tuple[float, float]],
    buildable_area: list[tuple[float, float]],
    num_stories: int = 3,
    name: str = "School Building",
) -> BuildingPlan:
    """Generate a school building plan with classrooms, corridors, and offices.

    Typical school layout:
    - L-shaped or rectangular
    - Central corridor with classrooms on both sides
    - Ground floor: offices, lobby, library
    - Upper floors: classrooms
    """
    # Calculate buildable extents
    xs = [p[0] for p in buildable_area] if buildable_area else [p[0] for p in land_boundary]
    ys = [p[1] for p in buildable_area] if buildable_area else [p[1] for p in land_boundary]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # School uses ~40% of buildable width, ~80% of depth
    width = (max_x - min_x) * 0.8
    depth = (max_y - min_y) * 0.4
    width = min(width, 60.0)  # cap at 60m
    depth = min(depth, 15.0)  # cap at 15m

    ox = min_x + ((max_x - min_x) - width) / 2
    oy = min_y + ((max_y - min_y) - depth) / 2

    footprint = [(ox, oy), (ox + width, oy), (ox + width, oy + depth), (ox, oy + depth)]

    stories: list[StoryPlan] = []
    corridor_width = 2.5
    story_height = 3.5

    for i in range(num_stories):
        floor_name = f"{i + 1}F"
        elevation = i * story_height

        walls: list[WallDef] = []
        spaces: list[SpaceDef] = []
        openings: list[OpeningDef] = []

        # Exterior walls
        ext_walls = [
            WallDef(start=(ox, oy), end=(ox + width, oy), wall_type="exterior"),
            WallDef(start=(ox + width, oy), end=(ox + width, oy + depth), wall_type="exterior"),
            WallDef(start=(ox + width, oy + depth), end=(ox, oy + depth), wall_type="exterior"),
            WallDef(start=(ox, oy + depth), end=(ox, oy), wall_type="exterior"),
        ]
        walls.extend(ext_walls)

        # Central corridor wall (divides building into two rows)
        corridor_y = oy + (depth - corridor_width) / 2
        walls.append(
            WallDef(start=(ox, corridor_y), end=(ox + width, corridor_y), wall_type="interior")
        )
        walls.append(
            WallDef(
                start=(ox, corridor_y + corridor_width),
                end=(ox + width, corridor_y + corridor_width),
                wall_type="interior",
            )
        )

        # Corridor space
        spaces.append(
            SpaceDef(
                name=f"Corridor {floor_name}",
                boundary=[
                    (ox, corridor_y),
                    (ox + width, corridor_y),
                    (ox + width, corridor_y + corridor_width),
                    (ox, corridor_y + corridor_width),
                ],
                space_type="corridor",
                area_sqm=width * corridor_width,
            )
        )

        # Rooms on each side
        room_depth_south = corridor_y - oy
        room_depth_north = oy + depth - (corridor_y + corridor_width)
        num_rooms = max(2, int(width // 8))
        room_width = width / num_rooms

        for r in range(num_rooms):
            rx = ox + r * room_width

            if i == 0 and r == 0:
                space_type = "office"
                room_name = f"Office {floor_name}"
            elif i == 0 and r == num_rooms - 1:
                space_type = "office"
                room_name = f"Library {floor_name}"
            else:
                space_type = "office"
                room_name = f"Classroom {floor_name}-{r + 1}"

            # South side room
            spaces.append(
                SpaceDef(
                    name=f"{room_name}S",
                    boundary=[
                        (rx, oy),
                        (rx + room_width, oy),
                        (rx + room_width, corridor_y),
                        (rx, corridor_y),
                    ],
                    space_type=space_type,
                    area_sqm=room_width * room_depth_south,
                )
            )

            # North side room
            spaces.append(
                SpaceDef(
                    name=f"{room_name}N",
                    boundary=[
                        (rx, corridor_y + corridor_width),
                        (rx + room_width, corridor_y + corridor_width),
                        (rx + room_width, oy + depth),
                        (rx, oy + depth),
                    ],
                    space_type=space_type,
                    area_sqm=room_width * room_depth_north,
                )
            )

            # Partition walls between rooms
            if r > 0:
                walls.append(WallDef(start=(rx, oy), end=(rx, corridor_y), wall_type="partition"))
                walls.append(
                    WallDef(
                        start=(rx, corridor_y + corridor_width),
                        end=(rx, oy + depth),
                        wall_type="partition",
                    )
                )

            # Windows on exterior walls (south and north)
            openings.append(
                OpeningDef(
                    wall_index=0,
                    offset_m=rx - ox + 1.0,
                    width_m=2.0,
                    height_m=1.5,
                    sill_height_m=0.9,
                    opening_type="window",
                )
            )
            openings.append(
                OpeningDef(
                    wall_index=2,
                    offset_m=rx - ox + 1.0,
                    width_m=2.0,
                    height_m=1.5,
                    sill_height_m=0.9,
                    opening_type="window",
                )
            )

        stories.append(
            StoryPlan(
                name=floor_name,
                elevation_m=elevation,
                height_m=story_height,
                walls=walls,
                spaces=spaces,
                openings=openings,
                slab_boundary=footprint,
            )
        )

    return BuildingPlan(
        name=name,
        land_boundary=land_boundary,
        buildable_area=buildable_area,
        building_footprint=footprint,
        stories=stories,
        roof=RoofPlan(roof_type="flat", slope_degrees=0.0),
    )
