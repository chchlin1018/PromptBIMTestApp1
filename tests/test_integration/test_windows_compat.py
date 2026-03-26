"""P25 Windows compatibility tests — verify cross-platform path handling."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan, RoofPlan, SpaceDef, StoryPlan, WallDef


def _sample_plan() -> BuildingPlan:
    footprint = [(2, 2), (20, 2), (20, 20), (2, 20)]
    walls = [
        WallDef(start=(2, 2), end=(20, 2)),
        WallDef(start=(20, 2), end=(20, 20)),
        WallDef(start=(20, 20), end=(2, 20)),
        WallDef(start=(2, 20), end=(2, 2)),
    ]
    stories = [
        StoryPlan(
            name="1F",
            elevation_m=0.0,
            height_m=3.0,
            walls=walls,
            spaces=[SpaceDef(name="Room", boundary=footprint, space_type="living", area_sqm=324.0)],
            slab_boundary=footprint,
        )
    ]
    return BuildingPlan(
        name="Windows Test",
        land_boundary=[(0, 0), (30, 0), (30, 30), (0, 30)],
        buildable_area=[(0, 0), (30, 0), (30, 30), (0, 30)],
        building_footprint=footprint,
        building_bcr=0.36,
        building_far=0.36,
        stories=stories,
        roof=RoofPlan(roof_type="flat"),
    )


class TestWindowsCompat:
    """Cross-platform compatibility tests."""

    def test_path_with_spaces(self, tmp_path: Path):
        """Output paths with spaces should work on all platforms."""
        spaced = tmp_path / "path with spaces" / "sub dir"
        spaced.mkdir(parents=True)
        test_file = spaced / "test.txt"
        test_file.write_text("hello", encoding="utf-8")
        assert test_file.read_text(encoding="utf-8") == "hello"

    def test_ifc_output_path_handling(self, tmp_path: Path):
        """IFC generator should handle platform paths correctly."""
        from promptbim.bim.ifc_generator import IFCGenerator

        plan = _sample_plan()
        out = tmp_path / "output" / "building.ifc"
        result = IFCGenerator().generate(plan, out)
        assert result.exists()
        assert result.stat().st_size > 0

    def test_pathlib_consistency(self):
        """Verify Path works consistently across platforms."""
        p = Path("src") / "promptbim" / "__init__.py"
        assert p.parts[-1] == "__init__.py"
        assert str(Path("a/b/c")) == str(Path("a") / "b" / "c")

    def test_tempdir_creation(self):
        """Temporary directories should work cross-platform."""
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "subdir" / "test.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('{"ok": true}', encoding="utf-8")
            assert p.exists()
