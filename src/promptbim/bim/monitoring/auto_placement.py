"""Automatic monitoring point placement algorithm.

Reads a BuildingPlan, applies placement rules, and outputs a MonitorPlan
with concrete XYZ positions for each sensor/actuator.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from promptbim.bim.monitoring.monitor_types import (
    MONITOR_TYPES,
    MonitorType,
    get_types_for_space,
)
from promptbim.bim.monitoring.rules_engine import PLACEMENT_RULES, RulesEngine
from promptbim.schemas.plan import BuildingPlan, SpaceDef, StoryPlan


@dataclass
class MonitorPlacement:
    """A single placed monitoring point with XYZ position."""

    monitor_type_id: str
    name: str
    floor: str
    space_name: str
    position: tuple[float, float, float]
    ifc_class: str
    predefined_type: str
    category: str
    unit_cost_twd: float = 0


@dataclass
class MonitorPlan:
    """Complete monitoring placement plan for a building."""

    placements: list[MonitorPlacement] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        return len(self.placements)

    @property
    def total_cost_twd(self) -> float:
        return sum(p.unit_cost_twd for p in self.placements)

    def by_floor(self) -> dict[str, list[MonitorPlacement]]:
        result: dict[str, list[MonitorPlacement]] = {}
        for p in self.placements:
            result.setdefault(p.floor, []).append(p)
        return result

    def by_category(self) -> dict[str, list[MonitorPlacement]]:
        result: dict[str, list[MonitorPlacement]] = {}
        for p in self.placements:
            result.setdefault(p.category, []).append(p)
        return result

    def by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for p in self.placements:
            counts[p.monitor_type_id] = counts.get(p.monitor_type_id, 0) + 1
        return counts


class AutoMonitorPlacer:
    """Automatically place monitoring points on a BuildingPlan."""

    def __init__(self, rules_engine: RulesEngine | None = None) -> None:
        self._engine = rules_engine or RulesEngine()

    def place_all(self, plan: BuildingPlan) -> MonitorPlan:
        """Run auto-placement for the entire building."""
        placements: list[MonitorPlacement] = []
        num_floors = len(plan.stories)

        for story in plan.stories:
            # Per-space placements
            for space in story.spaces:
                applicable = get_types_for_space(space.space_type)
                for mt in applicable:
                    count = self._engine.compute_count(mt.id, space.area_sqm)
                    if count <= 0:
                        continue
                    positions = self._distribute_in_space(space, story, count)
                    for i, pos in enumerate(positions):
                        placements.append(MonitorPlacement(
                            monitor_type_id=mt.id,
                            name=f"{mt.name}_{story.name}_{space.name}_{i}",
                            floor=story.name,
                            space_name=space.name,
                            position=pos,
                            ifc_class=mt.ifc_class,
                            predefined_type=mt.predefined_type,
                            category=mt.category.value,
                            unit_cost_twd=mt.unit_cost_twd,
                        ))

            # Per-floor placements (for types with per_floor rules)
            placements.extend(self._per_floor_placements(story))

        # Per-building placements
        placements.extend(self._per_building_placements(plan))

        return MonitorPlan(placements=placements)

    def _distribute_in_space(
        self,
        space: SpaceDef,
        story: StoryPlan,
        count: int,
    ) -> list[tuple[float, float, float]]:
        """Distribute *count* points evenly within a space boundary."""
        if not space.boundary:
            return []

        cx, cy = self._centroid(space.boundary)
        z = story.elevation_m + story.height_m - 0.3  # ceiling mount

        if count == 1:
            return [(cx, cy, z)]

        # Distribute in a circle pattern around centroid
        radius = min(math.sqrt(space.area_sqm) * 0.2, 2.0)
        positions: list[tuple[float, float, float]] = []
        for i in range(count):
            angle = 2 * math.pi * i / count
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            positions.append((round(x, 3), round(y, 3), round(z, 3)))
        return positions

    def _per_floor_placements(self, story: StoryPlan) -> list[MonitorPlacement]:
        """Place monitors with per_floor rules on corridor/mechanical spaces."""
        placements: list[MonitorPlacement] = []
        rules = PLACEMENT_RULES

        for type_id, rule in rules.items():
            if rule.mode != "per_floor":
                continue
            mt = MONITOR_TYPES.get(type_id)
            if mt is None:
                continue

            count = max(1, int(rule.density + 0.5))

            # Find a suitable space or use slab centroid
            z = story.elevation_m + story.height_m - 0.3
            positions = self._floor_positions(story, count)
            for i, (x, y) in enumerate(positions):
                placements.append(MonitorPlacement(
                    monitor_type_id=type_id,
                    name=f"{mt.name}_{story.name}_floor_{i}",
                    floor=story.name,
                    space_name="floor_level",
                    position=(round(x, 3), round(y, 3), round(z, 3)),
                    ifc_class=mt.ifc_class,
                    predefined_type=mt.predefined_type,
                    category=mt.category.value,
                    unit_cost_twd=mt.unit_cost_twd,
                ))
        return placements

    def _per_building_placements(self, plan: BuildingPlan) -> list[MonitorPlacement]:
        """Place monitors with per_building rules."""
        placements: list[MonitorPlacement] = []
        rules = PLACEMENT_RULES

        # Use top floor for roof-mounted, bottom floor for basement
        top_story = plan.stories[-1] if plan.stories else None
        bottom_story = plan.stories[0] if plan.stories else None
        if not top_story or not bottom_story:
            return placements

        for type_id, rule in rules.items():
            if rule.mode != "per_building":
                continue
            mt = MONITOR_TYPES.get(type_id)
            if mt is None:
                continue

            count = max(1, int(rule.density + 0.5))

            # Roof sensors go on top; structural on bottom
            if "roof" in mt.applicable_spaces or mt.category.value == "energy":
                story = top_story
            elif mt.category.value == "structural":
                story = bottom_story
            else:
                story = bottom_story

            z = story.elevation_m + story.height_m - 0.3
            positions = self._floor_positions(story, count)
            for i, (x, y) in enumerate(positions):
                placements.append(MonitorPlacement(
                    monitor_type_id=type_id,
                    name=f"{mt.name}_{story.name}_bldg_{i}",
                    floor=story.name,
                    space_name="building_level",
                    position=(round(x, 3), round(y, 3), round(z, 3)),
                    ifc_class=mt.ifc_class,
                    predefined_type=mt.predefined_type,
                    category=mt.category.value,
                    unit_cost_twd=mt.unit_cost_twd,
                ))
        return placements

    def _floor_positions(
        self, story: StoryPlan, count: int
    ) -> list[tuple[float, float]]:
        """Get *count* positions distributed on a floor's slab."""
        if story.slab_boundary:
            cx, cy = self._centroid(story.slab_boundary)
        elif story.spaces:
            # Fallback: average of space centroids
            xs = [self._centroid(s.boundary)[0] for s in story.spaces if s.boundary]
            ys = [self._centroid(s.boundary)[1] for s in story.spaces if s.boundary]
            cx = sum(xs) / len(xs) if xs else 5.0
            cy = sum(ys) / len(ys) if ys else 5.0
        else:
            cx, cy = 5.0, 5.0

        if count == 1:
            return [(cx, cy)]

        radius = 2.0
        positions: list[tuple[float, float]] = []
        for i in range(count):
            angle = 2 * math.pi * i / count
            positions.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        return positions

    @staticmethod
    def _centroid(boundary: list[tuple[float, float]]) -> tuple[float, float]:
        if not boundary:
            return (0.0, 0.0)
        cx = sum(p[0] for p in boundary) / len(boundary)
        cy = sum(p[1] for p in boundary) / len(boundary)
        return (cx, cy)
