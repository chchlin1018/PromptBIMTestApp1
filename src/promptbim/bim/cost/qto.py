"""IFC Quantity Take-Off (QTO) — extract quantities from a BuildingPlan.

Instead of reading from an IFC file (which requires full geometry), this module
works directly from the in-memory ``BuildingPlan`` schema produced by the
Planner agent.  This keeps the cost estimation fast and dependency-light.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from promptbim.debug import get_logger

if TYPE_CHECKING:
    from promptbim.schemas.plan import BuildingPlan, StoryPlan, WallDef

logger = get_logger("cost.qto")


@dataclass
class QTOItem:
    """A single quantity take-off line item."""

    category: str
    ifc_class: str
    name: str
    unit: str
    quantity: float
    story: str = ""
    extra: dict = field(default_factory=dict)


class QuantityTakeOff:
    """Extract construction quantities from a BuildingPlan."""

    def extract(self, plan: BuildingPlan) -> list[QTOItem]:
        logger.debug("Extracting QTO from plan: %s (%d stories)", plan.name, len(plan.stories))
        items: list[QTOItem] = []
        total_floor_area = 0.0

        for story in plan.stories:
            items.extend(self._extract_walls(story))
            items.extend(self._extract_slab(story, plan))
            items.extend(self._extract_openings(story))
            slab_area = self._polygon_area(
                story.slab_boundary or plan.building_footprint
            )
            total_floor_area += slab_area

        # Roof
        if plan.stories:
            roof_area = self._polygon_area(plan.building_footprint)
            if roof_area > 0:
                items.append(QTOItem(
                    category="roof",
                    ifc_class="IfcRoof",
                    name="Roof",
                    unit="m2",
                    quantity=roof_area,
                    story="Roof",
                ))

        # MEP allowance (based on total floor area)
        if total_floor_area > 0:
            items.append(QTOItem(
                category="mep_hvac",
                ifc_class="IfcSystem",
                name="HVAC System",
                unit="m2",
                quantity=total_floor_area,
            ))
            items.append(QTOItem(
                category="mep_plumbing",
                ifc_class="IfcSystem",
                name="Plumbing System",
                unit="m2",
                quantity=total_floor_area,
            ))
            items.append(QTOItem(
                category="mep_electrical",
                ifc_class="IfcSystem",
                name="Electrical System",
                unit="m2",
                quantity=total_floor_area,
            ))
            items.append(QTOItem(
                category="mep_fire",
                ifc_class="IfcSystem",
                name="Fire Protection",
                unit="m2",
                quantity=total_floor_area,
            ))

        # Site work (based on land boundary)
        land_area = self._polygon_area(plan.land_boundary)
        footprint_area = self._polygon_area(plan.building_footprint)
        site_area = land_area - footprint_area if land_area > footprint_area else 0
        if site_area > 0:
            items.append(QTOItem(
                category="site_work",
                ifc_class="IfcSite",
                name="Site Work",
                unit="m2",
                quantity=site_area,
            ))

        for item in items:
            logger.debug("QTO: %s — %.2f %s", item.name, item.quantity, item.unit)
        logger.debug("QTO total: %d items", len(items))
        return items

    def _extract_walls(self, story: StoryPlan) -> list[QTOItem]:
        items: list[QTOItem] = []
        for i, w in enumerate(story.walls):
            length = _wall_length(w)
            area = length * story.height_m
            volume = area * w.thickness_m
            cat = "wall_exterior" if w.wall_type == "exterior" else "wall_interior"
            items.append(QTOItem(
                category=cat,
                ifc_class="IfcWall",
                name=f"Wall-{story.name}-{i}",
                unit="m2",
                quantity=area,
                story=story.name,
                extra={"length_m": length, "volume_m3": volume},
            ))
        return items

    def _extract_slab(self, story: StoryPlan, plan: BuildingPlan) -> list[QTOItem]:
        boundary = story.slab_boundary or plan.building_footprint
        area = self._polygon_area(boundary)
        if area <= 0:
            return []
        return [QTOItem(
            category="slab",
            ifc_class="IfcSlab",
            name=f"Slab-{story.name}",
            unit="m2",
            quantity=area,
            story=story.name,
            extra={"thickness_m": story.slab_thickness_m},
        )]

    def _extract_openings(self, story: StoryPlan) -> list[QTOItem]:
        items: list[QTOItem] = []
        for i, o in enumerate(story.openings):
            if o.opening_type == "door":
                items.append(QTOItem(
                    category="door",
                    ifc_class="IfcDoor",
                    name=f"Door-{story.name}-{i}",
                    unit="unit",
                    quantity=1,
                    story=story.name,
                    extra={"width_m": o.width_m, "height_m": o.height_m},
                ))
            else:
                area = o.width_m * o.height_m
                items.append(QTOItem(
                    category="window",
                    ifc_class="IfcWindow",
                    name=f"Window-{story.name}-{i}",
                    unit="m2",
                    quantity=area,
                    story=story.name,
                ))
        return items

    @staticmethod
    def _polygon_area(coords: list[tuple[float, float]]) -> float:
        """Shoelace formula for polygon area."""
        if len(coords) < 3:
            return 0.0
        n = len(coords)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]
        return abs(area) / 2.0


def _wall_length(w: WallDef) -> float:
    return math.hypot(w.end[0] - w.start[0], w.end[1] - w.start[1])
