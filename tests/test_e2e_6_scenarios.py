"""E2E: 3 scenes x 2 modifications = 6 scenarios.

Validates the full pipeline for each demo scene (Villa, TSMC Fab, Data Center)
with both generate and modify operations.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from promptbim.schemas.plan import (
    BuildingPlan,
    StoryPlan,
    WallDef,
    SpaceDef,
    OpeningDef,
    RoofPlan,
)
from mesh_serializer import serialize_plan_to_mesh


def _make_walls(w, d, thickness=0.2, wall_type="exterior"):
    return [
        WallDef(start=(0, 0), end=(w, 0), thickness_m=thickness, wall_type=wall_type),
        WallDef(start=(w, 0), end=(w, d), thickness_m=thickness, wall_type=wall_type),
        WallDef(start=(w, d), end=(0, d), thickness_m=thickness, wall_type=wall_type),
        WallDef(start=(0, d), end=(0, 0), thickness_m=thickness, wall_type=wall_type),
    ]


def _make_boundary(w, d):
    return [(0, 0), (w, 0), (w, d), (0, d)]


# ── Scene Fixtures ──


@pytest.fixture
def villa_plan():
    """S1: Villa with Pool — 30x40m, 2 stories."""
    stories = []
    for i, name in enumerate(["1F", "2F"]):
        stories.append(StoryPlan(
            name=name,
            elevation_m=i * 3.2,
            height_m=3.2,
            walls=_make_walls(30, 40),
            spaces=[
                SpaceDef(name="Living", boundary=_make_boundary(15, 20), space_type="living", area_sqm=300),
                SpaceDef(name="Kitchen", boundary=[(15, 0), (30, 0), (30, 20), (15, 20)], space_type="kitchen", area_sqm=300),
            ],
            openings=[
                OpeningDef(wall_index=0, offset_m=5, width_m=2.4, height_m=1.5, sill_height_m=0.9, opening_type="window"),
                OpeningDef(wall_index=0, offset_m=12, width_m=1.2, height_m=2.1, sill_height_m=0.0, opening_type="door"),
            ],
            slab_boundary=_make_boundary(30, 40),
            slab_thickness_m=0.2,
        ))
    return BuildingPlan(
        name="S1 Villa",
        stories=stories,
        building_footprint=_make_boundary(30, 40),
        building_bcr=0.45,
        building_far=0.9,
        roof=RoofPlan(roof_type="flat", overhang_m=0.5),
    )


@pytest.fixture
def fab_plan():
    """S2: TSMC Fab — 120x80m, 4 stories."""
    stories = []
    for i, (name, h) in enumerate([("B1F", 5.0), ("1F", 6.0), ("2F", 5.0), ("3F", 4.5)]):
        stories.append(StoryPlan(
            name=name,
            elevation_m=sum(s[1] for s in [("B1F", 5.0), ("1F", 6.0), ("2F", 5.0), ("3F", 4.5)][:i]),
            height_m=h,
            walls=_make_walls(120, 80, thickness=0.3),
            spaces=[
                SpaceDef(name=f"Cleanroom_{name}", boundary=[(10, 10), (110, 10), (110, 70), (10, 70)], space_type="cleanroom", area_sqm=6000),
            ],
            openings=[],
            slab_boundary=_make_boundary(120, 80),
            slab_thickness_m=0.3,
        ))
    return BuildingPlan(
        name="S2 TSMC Fab",
        stories=stories,
        building_footprint=_make_boundary(120, 80),
        building_bcr=0.6,
        building_far=2.4,
        roof=RoofPlan(roof_type="flat", overhang_m=0.0),
    )


@pytest.fixture
def dc_plan():
    """S3: Data Center — 80x60m, 3 stories."""
    stories = []
    for i, name in enumerate(["1F", "2F", "3F"]):
        stories.append(StoryPlan(
            name=name,
            elevation_m=i * 4.5,
            height_m=4.5,
            walls=_make_walls(80, 60, thickness=0.25),
            spaces=[
                SpaceDef(name=f"ServerHall_{name}", boundary=[(5, 5), (75, 5), (75, 55), (5, 55)], space_type="server_room", area_sqm=3500),
            ],
            openings=[],
            slab_boundary=_make_boundary(80, 60),
            slab_thickness_m=0.25,
        ))
    return BuildingPlan(
        name="S3 Data Center",
        stories=stories,
        building_footprint=_make_boundary(80, 60),
        building_bcr=0.55,
        building_far=1.65,
        roof=RoofPlan(roof_type="flat", overhang_m=0.3),
    )


def _validate_mesh(result, min_elements=1):
    """Common mesh validation."""
    assert "elements" in result
    assert "element_count" in result
    assert result["element_count"] >= min_elements
    for elem in result["elements"]:
        assert "id" in elem
        assert "type" in elem
        assert "material" in elem
        assert "vertices" in elem
        assert "indices" in elem
        assert len(elem["vertices"]) > 0
        assert len(elem["indices"]) > 0

    json_str = json.dumps(result)
    parsed = json.loads(json_str)
    assert parsed["element_count"] == result["element_count"]


def _simulate_modify(plan, modification):
    """Simulate a modification by adjusting the plan and re-serializing."""
    if modification == "add_story":
        last = plan.stories[-1]
        new_story = StoryPlan(
            name=f"{len(plan.stories)+1}F",
            elevation_m=last.elevation_m + last.height_m,
            height_m=last.height_m,
            walls=last.walls[:],
            spaces=last.spaces[:],
            openings=[],
            slab_boundary=last.slab_boundary,
            slab_thickness_m=last.slab_thickness_m,
        )
        plan.stories.append(new_story)
    elif modification == "remove_wall":
        if plan.stories and len(plan.stories[0].walls) > 1:
            plan.stories[0].walls.pop()
    return serialize_plan_to_mesh(plan)


# ── Scenario 1: S1 Villa Generate ──

def test_s1_villa_generate(villa_plan):
    result = serialize_plan_to_mesh(villa_plan)
    _validate_mesh(result, min_elements=4)
    assert result["stories"] == 2
    wall_elems = [e for e in result["elements"] if e["type"] == "wall"]
    assert len(wall_elems) >= 4


# ── Scenario 2: S1 Villa Modify (add story) ──

def test_s1_villa_modify(villa_plan):
    original = serialize_plan_to_mesh(villa_plan)
    modified = _simulate_modify(villa_plan, "add_story")
    _validate_mesh(modified)
    assert modified["stories"] == 3
    assert modified["element_count"] > original["element_count"]


# ── Scenario 3: S2 TSMC Fab Generate ──

def test_s2_fab_generate(fab_plan):
    result = serialize_plan_to_mesh(fab_plan)
    _validate_mesh(result, min_elements=10)
    assert result["stories"] == 4


# ── Scenario 4: S2 TSMC Fab Modify (add story) ──

def test_s2_fab_modify(fab_plan):
    original = serialize_plan_to_mesh(fab_plan)
    modified = _simulate_modify(fab_plan, "add_story")
    _validate_mesh(modified)
    assert modified["stories"] == 5
    assert modified["element_count"] > original["element_count"]


# ── Scenario 5: S3 Data Center Generate ──

def test_s3_dc_generate(dc_plan):
    result = serialize_plan_to_mesh(dc_plan)
    _validate_mesh(result, min_elements=6)
    assert result["stories"] == 3


# ── Scenario 6: S3 Data Center Modify (remove wall) ──

def test_s3_dc_modify(dc_plan):
    original = serialize_plan_to_mesh(dc_plan)
    modified = _simulate_modify(dc_plan, "remove_wall")
    _validate_mesh(modified)
    assert modified["element_count"] < original["element_count"]
