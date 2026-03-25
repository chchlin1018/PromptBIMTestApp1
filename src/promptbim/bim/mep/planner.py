"""MEP Planner — deterministic equipment + terminal positioning and route planning.

Given a BuildingPlan, the planner:
1. Determines equipment locations (risers, panels, AHU)
2. Computes terminal positions per room (sprinkler heads, outlets, grilles)
3. Routes pipes/ducts between equipment and terminals using A* pathfinding
4. Returns a complete MEPPlan with all four systems

No LLM is used — this is a pure algorithmic planner (Builder pattern).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from promptbim.debug import get_logger
from promptbim.bim.mep.pathfinder import MEPPathfinder, RoutePath
from promptbim.bim.mep.systems import (
    CEILING_LAYER_Z_OFFSET,
    MEPSystemTemplate,
    get_template,
)
from promptbim.schemas.plan import BuildingPlan, SpaceDef, StoryPlan

_logger = get_logger("mep.planner")


@dataclass
class MEPTerminal:
    """A terminal device (sprinkler head, outlet, grille, fixture)."""

    system: str
    terminal_type: str
    position: tuple[float, float, float]
    floor: str


@dataclass
class MEPEquipment:
    """Major equipment (AHU, panel, riser, pump)."""

    system: str
    equipment_type: str
    position: tuple[float, float, float]
    floor: str


@dataclass
class MEPRoute:
    """A routed pipe/duct run."""

    system: str
    route_type: str  # "main" or "branch"
    diameter_mm: float
    path: RoutePath
    floor: str


@dataclass
class MEPPlan:
    """Complete MEP plan for a building."""

    equipment: list[MEPEquipment] = field(default_factory=list)
    terminals: list[MEPTerminal] = field(default_factory=list)
    routes: list[MEPRoute] = field(default_factory=list)


class MEPPlanner:
    """Deterministic MEP planner — positions equipment and routes pipes."""

    def __init__(self, grid_size: float = 0.3) -> None:
        self.grid_size = grid_size

    def plan(self, building: BuildingPlan, building_type: str = "office") -> MEPPlan:
        """Generate a complete MEP plan for the building."""
        template = get_template(building_type)
        result = MEPPlan()

        if not building.stories:
            return result

        # Find building centroid and a suitable riser position
        footprint = building.building_footprint or (
            building.stories[0].slab_boundary if building.stories else []
        )
        if not footprint:
            return result

        centroid = _polygon_centroid(footprint)
        riser_pos = _find_riser_position(footprint, centroid)

        for story in building.stories:
            z_base = story.elevation_m
            z_ceiling = z_base + story.height_m

            # Equipment per floor
            equip = self._place_equipment(story, template, riser_pos, z_ceiling)
            result.equipment.extend(equip)

            # Terminals per floor
            terminals = self._place_terminals(story, template, z_ceiling)
            result.terminals.extend(terminals)

            # Routes: connect equipment to terminals
            pathfinder = MEPPathfinder(grid_size=self.grid_size)
            self._add_building_obstacles(pathfinder, story)

            routes = self._route_system(
                story, template, pathfinder, equip, terminals, riser_pos, z_ceiling
            )
            result.routes.extend(routes)

        _logger.debug(
            "MEP plan: %d equipment, %d terminals, %d routes",
            len(result.equipment), len(result.terminals), len(result.routes),
        )
        return result

    # ---- equipment placement ----

    def _place_equipment(
        self,
        story: StoryPlan,
        template: MEPSystemTemplate,
        riser_pos: tuple[float, float],
        z_ceiling: float,
    ) -> list[MEPEquipment]:
        equip: list[MEPEquipment] = []
        rx, ry = riser_pos

        # Plumbing riser
        equip.append(MEPEquipment(
            system="plumbing",
            equipment_type="riser",
            position=(rx, ry, z_ceiling + CEILING_LAYER_Z_OFFSET["plumbing"]),
            floor=story.name,
        ))
        # Electrical panel
        equip.append(MEPEquipment(
            system="electrical",
            equipment_type="panel",
            position=(rx + 0.5, ry, z_ceiling + CEILING_LAYER_Z_OFFSET["electrical"]),
            floor=story.name,
        ))
        # HVAC AHU connection
        equip.append(MEPEquipment(
            system="hvac",
            equipment_type="ahu_connection",
            position=(rx, ry + 0.5, z_ceiling + CEILING_LAYER_Z_OFFSET["hvac"]),
            floor=story.name,
        ))
        # Fire protection riser
        equip.append(MEPEquipment(
            system="fire_protection",
            equipment_type="riser",
            position=(rx - 0.3, ry, z_ceiling + CEILING_LAYER_Z_OFFSET["fire_protection"]),
            floor=story.name,
        ))

        return equip

    # ---- terminal placement ----

    def _place_terminals(
        self,
        story: StoryPlan,
        template: MEPSystemTemplate,
        z_ceiling: float,
    ) -> list[MEPTerminal]:
        terminals: list[MEPTerminal] = []

        for space in story.spaces:
            center = _polygon_centroid(space.boundary)
            area = space.area_sqm

            # HVAC supply grilles
            n_grilles = max(1, int(area / 100 * template.hvac.terminals_per_100sqm))
            grille_positions = _distribute_points(space.boundary, n_grilles)
            for pos in grille_positions:
                terminals.append(MEPTerminal(
                    system="hvac",
                    terminal_type="supply_grille",
                    position=(pos[0], pos[1], z_ceiling + CEILING_LAYER_Z_OFFSET["hvac"]),
                    floor=story.name,
                ))

            # Fire protection sprinkler heads
            n_heads = max(1, int(area * template.fire_protection.heads_per_sqm))
            head_positions = _distribute_points(space.boundary, n_heads)
            for pos in head_positions:
                terminals.append(MEPTerminal(
                    system="fire_protection",
                    terminal_type="sprinkler_head",
                    position=(pos[0], pos[1], z_ceiling + CEILING_LAYER_Z_OFFSET["fire_protection"]),
                    floor=story.name,
                ))

            # Electrical outlets (distribute around perimeter — placed at ceiling for routing)
            n_outlets = max(1, int(area / 100 * template.electrical.outlets_per_100sqm))
            outlet_positions = _distribute_points(space.boundary, min(n_outlets, 4))
            for pos in outlet_positions:
                terminals.append(MEPTerminal(
                    system="electrical",
                    terminal_type="outlet",
                    position=(pos[0], pos[1], z_ceiling + CEILING_LAYER_Z_OFFSET["electrical"]),
                    floor=story.name,
                ))

            # Plumbing — only for bathrooms/kitchens
            if space.space_type in ("bathroom", "kitchen", "restroom"):
                terminals.append(MEPTerminal(
                    system="plumbing",
                    terminal_type="fixture",
                    position=(center[0], center[1], z_ceiling + CEILING_LAYER_Z_OFFSET["plumbing"]),
                    floor=story.name,
                ))

        return terminals

    # ---- routing ----

    def _add_building_obstacles(self, pathfinder: MEPPathfinder, story: StoryPlan) -> None:
        """Add wall/slab obstacles to the pathfinder grid."""
        walls = [
            {"start": w.start, "end": w.end, "thickness": w.thickness_m}
            for w in story.walls
        ]
        pathfinder.add_obstacles_from_walls(walls, story.elevation_m, story.height_m)

    def _route_system(
        self,
        story: StoryPlan,
        template: MEPSystemTemplate,
        pathfinder: MEPPathfinder,
        equipment: list[MEPEquipment],
        terminals: list[MEPTerminal],
        riser_pos: tuple[float, float],
        z_ceiling: float,
    ) -> list[MEPRoute]:
        routes: list[MEPRoute] = []

        for system_name in ("hvac", "plumbing", "electrical", "fire_protection"):
            sys_equip = [e for e in equipment if e.system == system_name]
            sys_terms = [t for t in terminals if t.system == system_name]

            if not sys_equip or not sys_terms:
                continue

            origin = sys_equip[0].position
            diameter = self._get_main_diameter(system_name, template)

            for term in sys_terms:
                path = pathfinder.find_path(origin, term.position, turn_penalty=2.0)
                if path.waypoints:
                    routes.append(MEPRoute(
                        system=system_name,
                        route_type="branch",
                        diameter_mm=diameter,
                        path=path,
                        floor=story.name,
                    ))

        return routes

    @staticmethod
    def _get_main_diameter(system: str, template: MEPSystemTemplate) -> float:
        if system == "hvac":
            return template.hvac.main_duct_mm[0]
        elif system == "plumbing":
            return template.plumbing.cold_water_main_mm
        elif system == "electrical":
            return template.electrical.main_tray_mm[0]
        elif system == "fire_protection":
            return template.fire_protection.sprinkler_main_mm
        return 50.0


# ---- geometry helpers ----

def _polygon_centroid(boundary: list[tuple[float, float]]) -> tuple[float, float]:
    if not boundary:
        return (0.0, 0.0)
    xs = [p[0] for p in boundary]
    ys = [p[1] for p in boundary]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def _find_riser_position(
    footprint: list[tuple[float, float]],
    centroid: tuple[float, float],
) -> tuple[float, float]:
    """Place the riser near the centroid but slightly offset toward the nearest edge."""
    if not footprint:
        return centroid
    pts = np.array(footprint)
    cx, cy = centroid
    # Find closest edge midpoint
    n = len(footprint)
    best_dist = float("inf")
    best_mid = centroid
    for i in range(n):
        j = (i + 1) % n
        mx = (pts[i, 0] + pts[j, 0]) / 2
        my = (pts[i, 1] + pts[j, 1]) / 2
        d = (mx - cx) ** 2 + (my - cy) ** 2
        if d < best_dist:
            best_dist = d
            best_mid = (float(mx), float(my))
    # Place riser 70% from centroid toward nearest edge
    rx = cx + 0.3 * (best_mid[0] - cx)
    ry = cy + 0.3 * (best_mid[1] - cy)
    return (rx, ry)


def _distribute_points(
    boundary: list[tuple[float, float]],
    count: int,
) -> list[tuple[float, float]]:
    """Distribute *count* points roughly evenly inside a polygon boundary."""
    if count <= 0 or not boundary:
        return []
    cx, cy = _polygon_centroid(boundary)
    if count == 1:
        return [(cx, cy)]

    pts = np.array(boundary)
    min_xy = pts.min(axis=0)
    max_xy = pts.max(axis=0)
    dx = max_xy[0] - min_xy[0]
    dy = max_xy[1] - min_xy[1]

    # Grid distribution within bounding box
    n_cols = max(1, int(np.ceil(np.sqrt(count * dx / max(dy, 0.1)))))
    n_rows = max(1, int(np.ceil(count / n_cols)))
    result: list[tuple[float, float]] = []
    for r in range(n_rows):
        for c in range(n_cols):
            if len(result) >= count:
                break
            x = min_xy[0] + dx * (c + 0.5) / n_cols
            y = min_xy[1] + dy * (r + 0.5) / n_rows
            result.append((float(x), float(y)))
    return result[:count]
