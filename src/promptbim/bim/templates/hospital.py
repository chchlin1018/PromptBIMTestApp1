"""Hospital building template — generates a hospital BuildingPlan on a given land parcel."""

from __future__ import annotations

from promptbim.schemas.plan import (
    BuildingPlan,
    OpeningDef,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)


def generate_hospital_plan(
    land_boundary: list[tuple[float, float]],
    buildable_area: list[tuple[float, float]],
    num_stories: int = 5,
    name: str = "Hospital Building",
) -> BuildingPlan:
    """Generate a hospital building plan.

    Typical hospital layout:
    - H-shaped or cross-shaped footprint
    - Ground floor: ER, lobby, radiology
    - Upper floors: wards (patient rooms along corridors)
    - Central core with elevators + stairs
    """
    xs = [p[0] for p in buildable_area] if buildable_area else [p[0] for p in land_boundary]
    ys = [p[1] for p in buildable_area] if buildable_area else [p[1] for p in land_boundary]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Hospital — use more of the site
    width = (max_x - min_x) * 0.7
    depth = (max_y - min_y) * 0.6
    width = min(width, 50.0)
    depth = min(depth, 30.0)

    ox = min_x + ((max_x - min_x) - width) / 2
    oy = min_y + ((max_y - min_y) - depth) / 2

    footprint = [(ox, oy), (ox + width, oy), (ox + width, oy + depth), (ox, oy + depth)]

    stories: list[StoryPlan] = []
    corridor_width = 2.8
    story_height = 3.6

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

        # Central corridor
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

        spaces.append(
            SpaceDef(
                name=f"Main Corridor {floor_name}",
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

        # Rooms
        room_depth_south = corridor_y - oy
        room_depth_north = oy + depth - (corridor_y + corridor_width)

        if i == 0:
            # Ground floor: ER, Lobby, Radiology, Pharmacy
            room_names = ["Emergency Room", "Main Lobby", "Radiology", "Pharmacy"]
        else:
            # Upper floors: patient wards
            room_names = [f"Ward {floor_name}-{j + 1}" for j in range(4)]

        num_rooms = len(room_names)
        room_width = width / num_rooms

        for r in range(num_rooms):
            rx = ox + r * room_width

            # South rooms
            spaces.append(
                SpaceDef(
                    name=f"{room_names[r]} S",
                    boundary=[
                        (rx, oy),
                        (rx + room_width, oy),
                        (rx + room_width, corridor_y),
                        (rx, corridor_y),
                    ],
                    space_type="office" if i == 0 else "bedroom",
                    area_sqm=room_width * room_depth_south,
                )
            )

            # North rooms
            spaces.append(
                SpaceDef(
                    name=f"{room_names[r]} N",
                    boundary=[
                        (rx, corridor_y + corridor_width),
                        (rx + room_width, corridor_y + corridor_width),
                        (rx + room_width, oy + depth),
                        (rx, oy + depth),
                    ],
                    space_type="office" if i == 0 else "bedroom",
                    area_sqm=room_width * room_depth_north,
                )
            )

            if r > 0:
                walls.append(WallDef(start=(rx, oy), end=(rx, corridor_y), wall_type="partition"))
                walls.append(
                    WallDef(
                        start=(rx, corridor_y + corridor_width),
                        end=(rx, oy + depth),
                        wall_type="partition",
                    )
                )

            # Windows
            openings.append(
                OpeningDef(
                    wall_index=0,
                    offset_m=rx - ox + 1.5,
                    width_m=1.8,
                    height_m=1.5,
                    sill_height_m=0.9,
                    opening_type="window",
                )
            )
            openings.append(
                OpeningDef(
                    wall_index=2,
                    offset_m=rx - ox + 1.5,
                    width_m=1.8,
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
