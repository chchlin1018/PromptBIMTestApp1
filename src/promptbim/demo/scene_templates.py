"""Scene templates for PromptBIM Demo-1 TSMC showcase.

Three pre-built scenes:
  S1 — 3-floor villa + pool (Residential)
  S2 — Semiconductor fab (TSMC-style, Industrial)
  S3 — Data center (Industrial)
"""

from __future__ import annotations

from dataclasses import dataclass

from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import (
    BuildingPlan,
    OpeningDef,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)
from promptbim.schemas.zoning import ZoningRules

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _shoelace(pts: list[tuple[float, float]]) -> float:
    n = len(pts)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += pts[i][0] * pts[j][1]
        area -= pts[j][0] * pts[i][1]
    return abs(area) / 2.0


def _perimeter(pts: list[tuple[float, float]]) -> float:
    n = len(pts)
    p = 0.0
    for i in range(n):
        j = (i + 1) % n
        dx = pts[j][0] - pts[i][0]
        dy = pts[j][1] - pts[i][1]
        p += (dx * dx + dy * dy) ** 0.5
    return p


def _rect_walls(width: float, depth: float) -> list[WallDef]:
    return [
        WallDef(start=(0.0, 0.0), end=(width, 0.0), thickness_m=0.25),
        WallDef(start=(width, 0.0), end=(width, depth), thickness_m=0.25),
        WallDef(start=(width, depth), end=(0.0, depth), thickness_m=0.25),
        WallDef(start=(0.0, depth), end=(0.0, 0.0), thickness_m=0.25),
    ]


def _rect_boundary(width: float, depth: float) -> list[tuple[float, float]]:
    return [(0.0, 0.0), (width, 0.0), (width, depth), (0.0, depth)]


@dataclass
class SceneMeta:
    scene_id: str
    title: str
    description: str
    tags: list[str]
    land: LandParcel
    zoning: ZoningRules
    plan: BuildingPlan


# ---------------------------------------------------------------------------
# Scene S1 — 3-Floor Villa + Pool (Residential)
# ---------------------------------------------------------------------------

def get_scene_s1() -> SceneMeta:
    """3-floor luxury villa with pool — 台北市大安區豪宅."""
    boundary = [(0.0, 0.0), (30.0, 0.0), (30.0, 40.0), (0.0, 40.0)]
    land = LandParcel(
        name="台北市大安區豪宅用地 (S1-Villa)",
        boundary=boundary,
        area_sqm=_shoelace(boundary),
        perimeter_m=_perimeter(boundary),
        crs="EPSG:3826",
        source_type="manual",
    )
    zoning = ZoningRules(
        zone_type="residential",
        far_limit=2.0,
        bcr_limit=0.5,
        height_limit_m=18.0,
        setback_front_m=6.0,
        setback_back_m=4.0,
        setback_side_m=2.0,
    )

    stories: list[StoryPlan] = []

    # B1 — pool
    stories.append(StoryPlan(
        name="B1-Pool",
        elevation_m=-2.0,
        height_m=2.0,
        walls=_rect_walls(10.0, 5.0),
        spaces=[SpaceDef(
            name="SwimmingPool",
            boundary=_rect_boundary(10.0, 5.0),
            space_type="recreation",
            area_sqm=50.0,
        )],
        openings=[],
        slab_boundary=_rect_boundary(10.0, 5.0),
    ))

    floor_names = ["1F", "2F", "3F"]
    space_names = [("LivingRoom", "Kitchen"), ("MasterBed", "Bathroom"), ("GuestBed", "Study")]
    space_types = [("living", "kitchen"), ("bedroom", "bathroom"), ("bedroom", "office")]
    floor_areas = [(180.0, 40.0), (120.0, 30.0), (100.0, 30.0)]

    for i in range(3):
        elev = i * 3.2
        sn1, sn2 = space_names[i]
        st1, st2 = space_types[i]
        a1, a2 = floor_areas[i]
        stories.append(StoryPlan(
            name=floor_names[i],
            elevation_m=elev,
            height_m=3.2,
            walls=_rect_walls(18.0, 28.0),
            spaces=[
                SpaceDef(name=sn1, boundary=_rect_boundary(12.0, 15.0), space_type=st1, area_sqm=a1),
                SpaceDef(name=sn2, boundary=_rect_boundary(6.0, 8.0), space_type=st2, area_sqm=a2),
            ],
            openings=[
                OpeningDef(wall_index=0, offset_m=5.0, width_m=2.4, height_m=2.4, sill_height_m=0.9, opening_type="window"),
                OpeningDef(wall_index=1, offset_m=8.0, width_m=1.2, height_m=2.4, opening_type="door"),
            ],
            slab_boundary=_rect_boundary(18.0, 28.0),
        ))

    plan = BuildingPlan(
        name="S1 Villa + Pool",
        stories=stories,
        building_bcr=0.45,
        building_far=1.35,
        roof=RoofPlan(roof_type="gable", slope_degrees=25.0, overhang_m=0.6),
    )
    return SceneMeta(
        scene_id="S1",
        title="3層別墅 + 泳池",
        description="台北市大安區 4 樓層（含地下泳池）豪宅，建坪 504 m²",
        tags=["villa", "pool", "residential", "taipei", "luxury"],
        land=land,
        zoning=zoning,
        plan=plan,
    )


# ---------------------------------------------------------------------------
# Scene S2 — Semiconductor Fab (TSMC-style)
# ---------------------------------------------------------------------------

def get_scene_s2() -> SceneMeta:
    """Semiconductor fab building — TSMC-style cleanroom fab."""
    boundary = [(0.0, 0.0), (120.0, 0.0), (120.0, 80.0), (0.0, 80.0)]
    land = LandParcel(
        name="台南市科學工業園區 (S2-Fab)",
        boundary=boundary,
        area_sqm=_shoelace(boundary),
        perimeter_m=_perimeter(boundary),
        crs="EPSG:3826",
        source_type="manual",
    )
    zoning = ZoningRules(
        zone_type="industrial",
        far_limit=1.5,
        bcr_limit=0.7,
        height_limit_m=50.0,
        setback_front_m=10.0,
        setback_back_m=8.0,
        setback_side_m=5.0,
    )

    fab_levels = [
        ("B1-Utility", -4.0, 4.0, "utility", 7000.0),
        ("1F-FabFloor", 0.0, 8.0, "production", 9600.0),
        ("2F-Office", 8.0, 4.0, "office", 4800.0),
        ("3F-Mech", 12.0, 4.0, "mechanical", 3200.0),
    ]
    stories = []
    for name, elev, ht, stype, sqm in fab_levels:
        stories.append(StoryPlan(
            name=name,
            elevation_m=elev,
            height_m=ht,
            walls=_rect_walls(100.0, 70.0),
            spaces=[SpaceDef(
                name=name,
                boundary=_rect_boundary(100.0, 70.0),
                space_type=stype,
                area_sqm=sqm,
            )],
            openings=[
                OpeningDef(wall_index=0, offset_m=5.0, width_m=4.0, height_m=4.0, opening_type="door"),
                OpeningDef(wall_index=0, offset_m=80.0, width_m=4.0, height_m=4.0, opening_type="door"),
            ],
            slab_boundary=_rect_boundary(100.0, 70.0),
        ))

    plan = BuildingPlan(
        name="S2 Semiconductor Fab",
        stories=stories,
        building_bcr=0.65,
        building_far=1.4,
        roof=RoofPlan(roof_type="flat", slope_degrees=0.0, overhang_m=0.0),
    )
    return SceneMeta(
        scene_id="S2",
        title="半導體廠房 (TSMC-style)",
        description="台南科學園區 4 層次半導體製造廠，含 Class-100 無塵室，建坪 24,600 m²",
        tags=["semiconductor", "fab", "tsmc", "cleanroom", "industrial", "tainan"],
        land=land,
        zoning=zoning,
        plan=plan,
    )


# ---------------------------------------------------------------------------
# Scene S3 — Data Center
# ---------------------------------------------------------------------------

def get_scene_s3() -> SceneMeta:
    """Hyperscale data center building."""
    boundary = [(0.0, 0.0), (80.0, 0.0), (80.0, 60.0), (0.0, 60.0)]
    land = LandParcel(
        name="桃園市航空城數據中心用地 (S3-DC)",
        boundary=boundary,
        area_sqm=_shoelace(boundary),
        perimeter_m=_perimeter(boundary),
        crs="EPSG:3826",
        source_type="manual",
    )
    zoning = ZoningRules(
        zone_type="industrial",
        far_limit=2.0,
        bcr_limit=0.65,
        height_limit_m=30.0,
        setback_front_m=8.0,
        setback_back_m=6.0,
        setback_side_m=4.0,
    )

    dc_levels = [
        ("B1-Power", -3.0, 3.0, "mechanical", 3200.0),
        ("1F-DataHall", 0.0, 5.0, "production", 4200.0),
        ("2F-DataHall", 5.0, 5.0, "production", 4200.0),
        ("3F-Network", 10.0, 4.0, "office", 2400.0),
        ("4F-Cooling", 14.0, 3.0, "mechanical", 1600.0),
    ]
    stories = []
    for name, elev, ht, stype, sqm in dc_levels:
        stories.append(StoryPlan(
            name=name,
            elevation_m=elev,
            height_m=ht,
            walls=_rect_walls(70.0, 50.0),
            spaces=[SpaceDef(
                name=name,
                boundary=_rect_boundary(70.0, 50.0),
                space_type=stype,
                area_sqm=sqm,
            )],
            openings=[
                OpeningDef(wall_index=0, offset_m=8.0, width_m=3.0, height_m=3.0, opening_type="door"),
                OpeningDef(wall_index=2, offset_m=50.0, width_m=3.0, height_m=3.0, opening_type="door"),
            ],
            slab_boundary=_rect_boundary(70.0, 50.0),
        ))

    plan = BuildingPlan(
        name="S3 Data Center",
        stories=stories,
        building_bcr=0.60,
        building_far=1.95,
        roof=RoofPlan(roof_type="flat", slope_degrees=0.0, overhang_m=0.0),
    )
    return SceneMeta(
        scene_id="S3",
        title="數據中心 (Hyperscale)",
        description="桃園航空城 Tier-IV 資料中心，5 層次，建坪 15,600 m²，PUE < 1.3",
        tags=["datacenter", "hyperscale", "tier4", "industrial", "taoyuan", "cloud"],
        land=land,
        zoning=zoning,
        plan=plan,
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

SCENE_REGISTRY: dict[str, "SceneMeta | None"] = {
    "S1": None,
    "S2": None,
    "S3": None,
}

_LOADERS = {
    "S1": get_scene_s1,
    "S2": get_scene_s2,
    "S3": get_scene_s3,
}


def get_scene(scene_id: str) -> SceneMeta:
    """Lazily load and return a scene by ID ('S1', 'S2', or 'S3')."""
    if SCENE_REGISTRY.get(scene_id) is None:
        loader = _LOADERS.get(scene_id)
        if loader is None:
            raise ValueError(f"Unknown scene_id: {scene_id!r}")
        SCENE_REGISTRY[scene_id] = loader()
    return SCENE_REGISTRY[scene_id]  # type: ignore[return-value]


def list_scenes() -> list[SceneMeta]:
    """Return all three scenes (loaded on demand)."""
    return [get_scene(sid) for sid in ("S1", "S2", "S3")]
