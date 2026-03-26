"""Shared pytest fixtures for PromptBIM tests."""

# P24e MANDATORY: Set QT_QPA_PLATFORM before any PySide6 import to prevent OOM
import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("DISPLAY", ":99")

from __future__ import annotations

import sys

import pytest

# Cross-platform skip markers
macos_only = pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
windows_only = pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
unix_only = pytest.mark.skipif(sys.platform == "win32", reason="Unix only")

from promptbim.bim.components.registry import ComponentRegistry
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import (
    BuildingPlan,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)
from promptbim.schemas.zoning import ZoningRules


@pytest.fixture(autouse=True)
def _reset_component_registry():
    """Reset ComponentRegistry between tests to prevent cross-pollution (H-2)."""
    yield
    ComponentRegistry.reset()


@pytest.fixture
def sample_land():
    """A 30x30 m test land parcel (900 sqm)."""
    return LandParcel(
        name="Test Parcel",
        boundary=[(0, 0), (30, 0), (30, 30), (0, 30)],
        area_sqm=900.0,
    )


@pytest.fixture
def sample_zoning():
    """Default zoning rules for Taipei."""
    return ZoningRules()


@pytest.fixture
def sample_plan():
    """A 3-story test building plan on 30x30 land."""
    return _make_plan(stories=3, land_size=30.0)


@pytest.fixture
def tmp_output(tmp_path):
    """Temporary output directory for test file generation."""
    out = tmp_path / "output"
    out.mkdir()
    return out


def _make_plan(stories: int = 3, land_size: float = 30.0) -> BuildingPlan:
    """Create a minimal BuildingPlan for testing."""
    footprint = [(2, 2), (20, 2), (20, 20), (2, 20)]
    story_plans = []
    for i in range(stories):
        story_plans.append(
            StoryPlan(
                name=f"{i + 1}F",
                elevation_m=i * 3.0,
                height_m=3.0,
                walls=[
                    WallDef(start=(2, 2), end=(20, 2)),
                    WallDef(start=(20, 2), end=(20, 20)),
                    WallDef(start=(20, 20), end=(2, 20)),
                    WallDef(start=(2, 20), end=(2, 2)),
                ],
                spaces=[
                    SpaceDef(
                        name=f"Room {i + 1}",
                        boundary=[(2, 2), (20, 2), (20, 20), (2, 20)],
                        space_type="living",
                        area_sqm=324.0,
                    )
                ],
                slab_boundary=footprint,
            )
        )

    land_boundary = [(0, 0), (land_size, 0), (land_size, land_size), (0, land_size)]
    footprint_area = 18.0 * 18.0
    land_area = land_size * land_size

    return BuildingPlan(
        name="Test Villa",
        land_boundary=land_boundary,
        buildable_area=land_boundary,
        building_footprint=footprint,
        building_bcr=footprint_area / land_area,
        building_far=(footprint_area * stories) / land_area,
        stories=story_plans,
        roof=RoofPlan(roof_type="flat"),
    )
