"""Agent 2: Building Planner.

Takes a :class:`BuildingRequirement` plus land/zoning context and produces
a :class:`BuildingPlan` JSON via Claude API.  This is the most critical
agent — it must place a valid building on the real land parcel.
"""

from __future__ import annotations

import json

from promptbim.agents.base import AgentResponse, BaseAgent
from promptbim.codes.tw_seismic_code import get_min_column_cm, get_seismic_params
from promptbim.debug import get_logger
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan
from promptbim.schemas.requirement import BuildingRequirement
from promptbim.schemas.zoning import ZoningRules

logger = get_logger("agents.planner")

PLANNER_SYSTEM_PROMPT = """\
You are an expert architect and urban planner. Your task is to generate a
BuildingPlan JSON that places a building on a real land parcel.

## INPUT
You will receive:
1. LandParcel: boundary coordinates, area, shape
2. ZoningRules: FAR limit, BCR limit, height limit, setbacks
3. BuildingRequirement: user's building description (enhanced by Agent 1)
4. Buildable area: the polygon after setback is applied

## CONSTRAINTS (MUST follow)
- Building footprint MUST fit inside the buildable area (land minus setbacks)
- BCR (building footprint area / land area) MUST NOT exceed bcr_limit
- FAR (total floor area / land area) MUST NOT exceed far_limit
- Building height MUST NOT exceed height_limit_m
- All coordinates are in METERS, relative to land's local origin
- Walls must form closed polygons per floor
- Every space must be bounded by walls
- Corridors minimum 1.2m width
- Doors minimum 0.9m width, 2.1m height
- Windows minimum 0.6m width, sill height 0.9m for non-ground floors

## OUTPUT FORMAT
Return a valid JSON matching this schema exactly:
{
  "name": "<building name>",
  "land_boundary": [[x,y], ...],
  "buildable_area": [[x,y], ...],
  "building_footprint": [[x,y], ...],
  "building_bcr": <float>,
  "building_far": <float>,
  "stories": [
    {
      "name": "1F",
      "elevation_m": 0.0,
      "height_m": 3.0,
      "walls": [
        {"start": [x,y], "end": [x,y], "thickness_m": 0.2, "wall_type": "exterior"},
        ...
      ],
      "spaces": [
        {"name": "Room", "boundary": [[x,y],...], "space_type": "office", "area_sqm": 30.0},
        ...
      ],
      "openings": [
        {"wall_index": 0, "offset_m": 1.0, "width_m": 1.2, "height_m": 2.1, "sill_height_m": 0.0, "opening_type": "door"},
        ...
      ],
      "slab_boundary": [[x,y], ...],
      "slab_thickness_m": 0.2
    }
  ],
  "roof": {
    "roof_type": "flat",
    "slope_degrees": 0.0,
    "overhang_m": 0.3
  }
}

All coordinates must be precise to 0.01m.
Return ONLY the JSON, no extra text.
"""


class PlannerAgent(BaseAgent):
    """Agent 2 — generates a BuildingPlan placed on a land parcel."""

    SYSTEM_PROMPT = PLANNER_SYSTEM_PROMPT

    def __init__(self, **kwargs) -> None:
        super().__init__(max_tokens=8192, **kwargs)

    def plan(
        self,
        requirement: BuildingRequirement,
        land: LandParcel,
        zoning: ZoningRules,
        buildable_area: list[tuple[float, float]],
    ) -> BuildingPlan:
        """Generate a building plan from requirement + land context.

        Returns a :class:`BuildingPlan`. Falls back to a simple box if
        the API call fails.
        """
        logger.debug("Planning: land=%.1f sqm, buildable=%d pts, stories=%d", land.area_sqm, len(buildable_area), requirement.num_stories)
        user_msg = self._build_user_message(requirement, land, zoning, buildable_area)
        response = self.run(user_msg)
        plan = self._to_plan(response, land, zoning, buildable_area, requirement)
        total_walls = sum(len(s.walls) for s in plan.stories)
        logger.debug("Plan: %d stories, footprint=%d pts, %d walls", len(plan.stories), len(plan.building_footprint), total_walls)
        return plan

    def _build_user_message(
        self,
        req: BuildingRequirement,
        land: LandParcel,
        zoning: ZoningRules,
        buildable_area: list[tuple[float, float]],
    ) -> str:
        code_constraints = _get_code_constraints(land, zoning, req.num_stories)
        return (
            f"## Land Parcel\n"
            f"- Boundary: {land.boundary}\n"
            f"- Area: {land.area_sqm:.1f} m²\n\n"
            f"## Zoning Rules\n"
            f"- Zone type: {zoning.zone_type}\n"
            f"- FAR limit: {zoning.far_limit}\n"
            f"- BCR limit: {zoning.bcr_limit}\n"
            f"- Height limit: {zoning.height_limit_m} m\n"
            f"- Setbacks: front={zoning.setback_front_m}m, back={zoning.setback_back_m}m, "
            f"left={zoning.setback_left_m}m, right={zoning.setback_right_m}m\n\n"
            f"## Buildable Area (after setback)\n"
            f"- Polygon: {buildable_area}\n\n"
            f"{code_constraints}\n\n"
            f"## Building Requirement\n"
            f"- Type: {req.building_type}\n"
            f"- Stories: {req.num_stories}\n"
            f"- Target area: {req.total_area_sqm or 'auto'} m²\n"
            f"- Features: {req.features}\n"
            f"- Constraints: {req.constraints}\n"
            f"- Description: {req.enhanced_description}\n"
        )

    def _to_plan(
        self,
        response: AgentResponse,
        land: LandParcel,
        zoning: ZoningRules,
        buildable_area: list[tuple[float, float]],
        requirement: BuildingRequirement,
    ) -> BuildingPlan:
        if response.ok and response.json_data:
            try:
                plan = BuildingPlan.model_validate(response.json_data)
                # Ensure land_boundary and buildable_area are set
                if not plan.land_boundary:
                    plan.land_boundary = land.boundary
                if not plan.buildable_area:
                    plan.buildable_area = buildable_area
                return plan
            except Exception:
                logger.exception("Failed to parse Planner response as BuildingPlan")

        # Fallback: simple rectangular box
        logger.warning("Planner fallback — generating simple box")
        return _fallback_box(land, zoning, buildable_area, requirement)


def _fallback_box(
    land: LandParcel,
    zoning: ZoningRules,
    buildable_area: list[tuple[float, float]],
    requirement: BuildingRequirement,
) -> BuildingPlan:
    """Generate a simple rectangular building as a fallback."""
    from shapely.geometry import Polygon as ShapelyPolygon

    from promptbim.schemas.plan import (
        OpeningDef,
        RoofPlan,
        SpaceDef,
        StoryPlan,
        WallDef,
    )

    buildable_poly = ShapelyPolygon(buildable_area) if buildable_area else ShapelyPolygon(land.boundary)
    bounds = buildable_poly.bounds  # minx, miny, maxx, maxy
    minx, miny, maxx, maxy = bounds

    # Inset a bit from the buildable boundary
    margin = 0.5
    bx0 = minx + margin
    by0 = miny + margin
    bx1 = maxx - margin
    by1 = maxy - margin

    width = bx1 - bx0
    depth = by1 - by0

    if width <= 2 or depth <= 2:
        # Buildable area too small, use what we can
        bx0, by0 = minx, miny
        bx1, by1 = maxx, maxy
        width = bx1 - bx0
        depth = by1 - by0

    # Limit footprint to BCR
    max_footprint_area = land.area_sqm * zoning.bcr_limit
    actual_footprint_area = width * depth
    if actual_footprint_area > max_footprint_area:
        scale = (max_footprint_area / actual_footprint_area) ** 0.5
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        half_w = width * scale / 2
        half_d = depth * scale / 2
        bx0, by0 = cx - half_w, cy - half_d
        bx1, by1 = cx + half_w, cy + half_d
        width = bx1 - bx0
        depth = by1 - by0
        actual_footprint_area = width * depth

    footprint = [
        (bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1),
    ]

    bcr = actual_footprint_area / land.area_sqm if land.area_sqm > 0 else 0
    num_stories = max(1, requirement.num_stories)
    max_stories = int(zoning.height_limit_m / 3.0)
    num_stories = min(num_stories, max_stories)

    # Check FAR limit
    max_total_area = land.area_sqm * zoning.far_limit
    while num_stories * actual_footprint_area > max_total_area and num_stories > 1:
        num_stories -= 1

    far = (num_stories * actual_footprint_area) / land.area_sqm if land.area_sqm > 0 else 0

    stories = []
    for i in range(num_stories):
        floor_name = f"{i + 1}F"
        elevation = i * 3.0

        walls = [
            WallDef(start=(bx0, by0), end=(bx1, by0), wall_type="exterior"),
            WallDef(start=(bx1, by0), end=(bx1, by1), wall_type="exterior"),
            WallDef(start=(bx1, by1), end=(bx0, by1), wall_type="exterior"),
            WallDef(start=(bx0, by1), end=(bx0, by0), wall_type="exterior"),
        ]

        spaces = [
            SpaceDef(
                name=f"Room {floor_name}",
                boundary=footprint,
                space_type="office" if requirement.building_type == "commercial" else "living",
                area_sqm=actual_footprint_area,
            )
        ]

        # Add a door on the first floor front wall
        openings = []
        if i == 0:
            openings.append(
                OpeningDef(
                    wall_index=0,
                    offset_m=width / 2 - 0.5,
                    width_m=1.0,
                    height_m=2.1,
                    sill_height_m=0.0,
                    opening_type="door",
                )
            )

        stories.append(
            StoryPlan(
                name=floor_name,
                elevation_m=elevation,
                height_m=3.0,
                walls=walls,
                spaces=spaces,
                openings=openings,
                slab_boundary=footprint,
            )
        )

    return BuildingPlan(
        name=requirement.enhanced_description[:50] or "Fallback Building",
        land_boundary=land.boundary,
        buildable_area=buildable_area,
        building_footprint=footprint,
        building_bcr=round(bcr, 4),
        building_far=round(far, 4),
        stories=stories,
        roof=RoofPlan(roof_type="flat"),
    )


def _get_code_constraints(
    land: LandParcel,
    zoning: ZoningRules,
    num_stories: int = 3,
) -> str:
    """Generate Taiwan building code constraints for the Planner prompt."""
    city = getattr(land, "city", "") or ""
    seismic = get_seismic_params(city)
    min_col = get_min_column_cm(num_stories)

    return (
        f"## Taiwan Building Code Constraints (MUST comply)\n\n"
        f"### Volume Limits\n"
        f"- BCR limit: {zoning.bcr_limit:.0%} "
        f"(footprint <= {land.area_sqm * zoning.bcr_limit:.1f} m2)\n"
        f"- FAR limit: {zoning.far_limit:.0%} "
        f"(total floor area <= {land.area_sqm * zoning.far_limit:.1f} m2)\n"
        f"- Height limit: {zoning.height_limit_m:.1f}m\n"
        f"- Setbacks: front {zoning.setback_front_m}m, back {zoning.setback_back_m}m, "
        f"left {zoning.setback_left_m}m, right {zoning.setback_right_m}m\n\n"
        f"### Evacuation Safety\n"
        f"- Corridor width: double-side rooms >= 1.6m, single-side >= 1.2m\n"
        f"- Max egress distance to stair: <= 50m\n"
        f"- 6F+ with room area > 200m2: need 2 egress stairs\n"
        f"- Stair width >= 1.2m, riser <= 20cm, tread >= 24cm\n\n"
        f"### Equipment\n"
        f"- 6F+: elevator required (>= 8 persons)\n"
        f"- 10F+: >= 2 elevators (including emergency)\n"
        f"- Parking: office per 100m2, residential per 150m2\n\n"
        f"### Seismic (city: {city or 'default'})\n"
        f"- Ss={seismic['Ss']}, S1={seismic['S1']}\n"
        f"- RC column min: {min_col}cm x {min_col}cm\n\n"
        f"### Accessibility\n"
        f"- Public buildings: accessible ramp, elevator (>= 1.1m x 1.35m), "
        f"toilet (>= 4m2), parking (width >= 3.5m)\n"
    )
