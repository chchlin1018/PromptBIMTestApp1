"""Tests for gui/model_view.py — 3D model viewer widget."""

import pytest

from promptbim.schemas.plan import (
    BuildingPlan,
    RoofPlan,
    StoryPlan,
    WallDef,
)


def _simple_plan() -> BuildingPlan:
    footprint = [(0, 0), (10, 0), (10, 8), (0, 8)]
    return BuildingPlan(
        name="Test Building",
        building_footprint=footprint,
        building_bcr=0.5,
        building_far=1.0,
        stories=[
            StoryPlan(
                name="1F",
                elevation_m=0.0,
                height_m=3.0,
                walls=[
                    WallDef(start=(0, 0), end=(10, 0)),
                    WallDef(start=(10, 0), end=(10, 8)),
                    WallDef(start=(10, 8), end=(0, 8)),
                    WallDef(start=(0, 8), end=(0, 0)),
                ],
                slab_boundary=footprint,
            ),
        ],
        roof=RoofPlan(roof_type="flat"),
    )


class TestModelViewImport:
    def test_import_model_view(self):
        """ModelView can be imported without error."""
        from promptbim.gui.model_view import ModelView
        assert ModelView is not None

    def test_import_build_model(self):
        """build_model function is accessible."""
        from promptbim.viz.model_3d import build_model
        plan = _simple_plan()
        meshes = build_model(plan)
        assert len(meshes) > 0
