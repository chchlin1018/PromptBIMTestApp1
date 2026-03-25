"""Tests for gui/dialogs/export_dialog.py — export functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from promptbim.schemas.plan import (
    BuildingPlan,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)
from promptbim.schemas.result import GenerationResult
from promptbim.gui.dialogs.export_dialog import _ExportWorker


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _sample_plan() -> BuildingPlan:
    footprint = [(0, 0), (10, 0), (10, 8), (0, 8)]
    return BuildingPlan(
        name="TestBuilding",
        building_footprint=footprint,
        building_bcr=0.50,
        building_far=1.0,
        stories=[
            StoryPlan(
                name="1F",
                elevation_m=0.0,
                height_m=3.0,
                slab_boundary=footprint,
                walls=[
                    WallDef(start=(0, 0), end=(10, 0), wall_type="exterior"),
                    WallDef(start=(10, 0), end=(10, 8), wall_type="exterior"),
                    WallDef(start=(10, 8), end=(0, 8), wall_type="exterior"),
                    WallDef(start=(0, 8), end=(0, 0), wall_type="exterior"),
                ],
                spaces=[
                    SpaceDef(
                        name="Office",
                        boundary=footprint,
                        space_type="office",
                        area_sqm=80.0,
                    ),
                ],
            ),
        ],
        roof=RoofPlan(roof_type="flat"),
    )


def _sample_result(plan: BuildingPlan) -> GenerationResult:
    return GenerationResult(
        success=True,
        building_name=plan.name,
        compliance_report={"status": "pass", "checks": []},
    )


# ---------------------------------------------------------------------------
# _ExportWorker tests (non-GUI)
# ---------------------------------------------------------------------------

class TestExportWorkerSvg:
    def test_export_svg_only(self):
        plan = _sample_plan()
        with tempfile.TemporaryDirectory() as tmpdir:
            worker = _ExportWorker(
                plan=plan,
                result=None,
                output_dir=Path(tmpdir),
                export_ifc=False,
                export_usd=False,
                export_svg=True,
                export_json=False,
                export_report=False,
            )
            worker.run()
            svg_dir = Path(tmpdir) / "floorplans"
            assert svg_dir.exists()
            svgs = list(svg_dir.glob("*.svg"))
            assert len(svgs) == 1
            assert "1F" in svgs[0].name


class TestExportWorkerJson:
    def test_export_json_only(self):
        plan = _sample_plan()
        with tempfile.TemporaryDirectory() as tmpdir:
            worker = _ExportWorker(
                plan=plan,
                result=None,
                output_dir=Path(tmpdir),
                export_ifc=False,
                export_usd=False,
                export_svg=False,
                export_json=True,
                export_report=False,
            )
            worker.run()
            json_files = list(Path(tmpdir).glob("*_plan.json"))
            assert len(json_files) == 1
            data = json.loads(json_files[0].read_text())
            assert data["name"] == "TestBuilding"
            assert len(data["stories"]) == 1


class TestExportWorkerReport:
    def test_export_report(self):
        plan = _sample_plan()
        result = _sample_result(plan)
        with tempfile.TemporaryDirectory() as tmpdir:
            worker = _ExportWorker(
                plan=plan,
                result=result,
                output_dir=Path(tmpdir),
                export_ifc=False,
                export_usd=False,
                export_svg=False,
                export_json=False,
                export_report=True,
            )
            worker.run()
            rpt_files = list(Path(tmpdir).glob("*_compliance.json"))
            assert len(rpt_files) == 1
            data = json.loads(rpt_files[0].read_text())
            assert data["status"] == "pass"

    def test_no_report_when_empty(self):
        plan = _sample_plan()
        result = GenerationResult(success=True, building_name="Test")
        with tempfile.TemporaryDirectory() as tmpdir:
            worker = _ExportWorker(
                plan=plan,
                result=result,
                output_dir=Path(tmpdir),
                export_ifc=False,
                export_usd=False,
                export_svg=False,
                export_json=False,
                export_report=True,
            )
            worker.run()
            rpt_files = list(Path(tmpdir).glob("*_compliance.json"))
            assert len(rpt_files) == 0


class TestExportWorkerAll:
    def test_export_svg_and_json(self):
        plan = _sample_plan()
        result = _sample_result(plan)
        with tempfile.TemporaryDirectory() as tmpdir:
            worker = _ExportWorker(
                plan=plan,
                result=result,
                output_dir=Path(tmpdir),
                export_ifc=False,
                export_usd=False,
                export_svg=True,
                export_json=True,
                export_report=True,
            )
            worker.run()
            assert (Path(tmpdir) / "floorplans").exists()
            assert len(list(Path(tmpdir).glob("*_plan.json"))) == 1
            assert len(list(Path(tmpdir).glob("*_compliance.json"))) == 1
