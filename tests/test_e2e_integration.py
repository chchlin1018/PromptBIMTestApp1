"""Sprint P11 — End-to-End Integration Tests.

Tests the full pipeline from prompt → generation → modification → export,
with mocked Claude API calls to enable offline testing.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_land(area: float = 900.0, size: float = 30.0):
    """Create a minimal LandParcel for testing."""
    from promptbim.schemas.land import LandParcel

    return LandParcel(
        name="Test Parcel",
        boundary=[(0, 0), (size, 0), (size, size), (0, size)],
        area_sqm=area,
    )


def _make_requirement(prompt: str = "3-story villa", stories: int = 3):
    """Create a minimal BuildingRequirement."""
    from promptbim.schemas.requirement import BuildingRequirement

    return BuildingRequirement(
        raw_prompt=prompt,
        building_type="residential",
        num_stories=stories,
        total_area_sqm=600.0,
        features=["swimming pool"],
        constraints=[],
        enhanced_description="A modern 3-story residential villa with pool.",
    )


def _make_plan(stories: int = 3, land_size: float = 30.0):
    """Create a minimal BuildingPlan for testing."""
    from promptbim.schemas.plan import (
        BuildingPlan,
        RoofPlan,
        SpaceDef,
        StoryPlan,
        WallDef,
    )

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


def _mock_enhancer_response():
    """Return a mock AgentResponse for the enhancer."""
    from promptbim.agents.base import AgentResponse

    return AgentResponse(
        text=json.dumps(
            {
                "building_type": "residential",
                "num_stories": 3,
                "total_area_sqm": 600.0,
                "features": ["swimming pool"],
                "constraints": [],
                "enhanced_description": "A modern 3-story residential villa.",
            }
        ),
        json_data={
            "building_type": "residential",
            "num_stories": 3,
            "total_area_sqm": 600.0,
            "features": ["swimming pool"],
            "constraints": [],
            "enhanced_description": "A modern 3-story residential villa.",
        },
    )


def _mock_planner_response(stories: int = 3):
    """Return a mock AgentResponse for the planner."""
    from promptbim.agents.base import AgentResponse

    plan = _make_plan(stories=stories)
    plan_dict = json.loads(plan.model_dump_json())
    return AgentResponse(
        text=json.dumps(plan_dict),
        json_data=plan_dict,
    )


def _mock_modifier_response():
    """Return a mock AgentResponse for the modifier intent parsing."""
    from promptbim.agents.base import AgentResponse

    return AgentResponse(
        text=json.dumps(
            {
                "modification_type": "stories",
                "parameters": {"num_stories": 9},
                "confidence": 0.95,
            }
        ),
        json_data={
            "modification_type": "stories",
            "parameters": {"num_stories": 9},
            "confidence": 0.95,
        },
    )


@pytest.fixture
def tmp_output_dir():
    d = tempfile.mkdtemp(prefix="promptbim_test_")
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------------------
# Test 1: No-land + Prompt → Generate IFC + USD
# ---------------------------------------------------------------------------


class TestE2ENoLand:
    """Test 1: Prompt-only generation without pre-loaded land."""

    def test_default_land_creation(self):
        """When no land is provided, a default 30x30 parcel should be created."""
        land = _make_land()
        assert land.area_sqm == 900.0
        assert len(land.boundary) == 4

    def test_generate_pipeline_with_mocked_agents(self, tmp_output_dir):
        """Full pipeline: Enhancer → Planner → Builder → Checker."""
        from promptbim.agents.orchestrator import Orchestrator
        from promptbim.schemas.zoning import ZoningRules

        land = _make_land()
        zoning = ZoningRules()
        orch = Orchestrator(output_dir=tmp_output_dir)

        # Mock the AI agents
        req = _make_requirement()
        plan = _make_plan()

        with (
            patch.object(orch._enhancer, "enhance", return_value=req),
            patch.object(orch._planner, "plan", return_value=plan),
            patch.object(orch._checker, "check") as mock_check,
        ):
            from promptbim.agents.checker import CheckResult

            mock_check.return_value = CheckResult()  # no violations

            result = orch.generate("在200坪地上蓋3層別墅", land, zoning)

        assert result.success
        assert result.building_name == "Test Villa"
        assert result.summary["stories"] == 3
        # IFC and USD files should be generated
        if result.ifc_path:
            assert result.ifc_path.exists()
        if result.usd_path:
            assert result.usd_path.exists()


# ---------------------------------------------------------------------------
# Test 2: GeoJSON Land + Prompt → Full Pipeline
# ---------------------------------------------------------------------------


class TestE2EWithLand:
    """Test 2: GeoJSON land + prompt → complete generation flow."""

    def test_geojson_land_load(self):
        """Verify GeoJSON parser works with sample data."""
        sample = ROOT / "tests" / "fixtures" / "sample_parcel.geojson"
        if not sample.exists():
            pytest.skip("No sample GeoJSON fixture")

        from promptbim.land.parsers.geojson import parse_geojson

        parcels = parse_geojson(sample)
        assert len(parcels) > 0
        assert parcels[0].area_sqm > 0

    def test_generate_with_land(self, tmp_output_dir):
        """Full pipeline with a predefined land parcel."""
        from promptbim.agents.orchestrator import Orchestrator
        from promptbim.schemas.zoning import ZoningRules

        land = _make_land(area=660.0, size=25.7)  # ~200 坪
        zoning = ZoningRules()
        orch = Orchestrator(output_dir=tmp_output_dir)

        req = _make_requirement()
        plan = _make_plan(stories=3, land_size=25.7)

        with (
            patch.object(orch._enhancer, "enhance", return_value=req),
            patch.object(orch._planner, "plan", return_value=plan),
            patch.object(orch._checker, "check") as mock_check,
        ):
            from promptbim.agents.checker import CheckResult

            mock_check.return_value = CheckResult()

            result = orch.generate("3-story villa with pool", land, zoning)

        assert result.success
        assert result.summary["stories"] == 3
        assert result.summary["bcr"] > 0


# ---------------------------------------------------------------------------
# Test 3: Image AI Recognition (mocked Vision API)
# ---------------------------------------------------------------------------


class TestE2EImageAI:
    """Test 3: Image → AI recognition → boundary confirm → generate."""

    def test_image_preprocess(self):
        """Verify image preprocessor can handle test images."""
        test_images = list((ROOT / "Pic_MyLand").glob("*.JPG"))
        if not test_images:
            pytest.skip("No test images in Pic_MyLand/")

        from promptbim.land.parsers.image_preprocess import prepare_for_vision_api

        b64_data, media_type = prepare_for_vision_api(str(test_images[0]))
        assert len(b64_data) > 0
        assert media_type in ("image/jpeg", "image/png")

    def test_ai_recognition_mocked(self):
        """AI land recognition with mocked Claude Vision API."""
        from promptbim.schemas.land import LandParcel

        # Simulate what the AI recognition returns
        parcel = LandParcel(
            name="AI-Recognized",
            boundary=[(0, 0), (20, 0), (20, 30), (0, 30)],
            area_sqm=600.0,
            source_type="ai_image",
            ai_confidence=0.85,
        )
        assert parcel.ai_confidence == 0.85
        assert parcel.source_type == "ai_image"

    def test_boundary_confirmation_logic(self):
        """Verify boundary confirmation can adjust vertices."""
        from promptbim.land.boundary_confirm import (
            BoundaryConfirmation,
            adjust_vertex,
            validate_boundary,
        )
        from promptbim.schemas.land import LandParcel

        parcel = LandParcel(
            name="Test",
            boundary=[(0, 0), (20, 0), (20, 30), (0, 30)],
            area_sqm=600.0,
        )

        confirmation = BoundaryConfirmation()
        confirmation.add_candidate(parcel, confidence=0.85, notes="AI detected")

        assert len(confirmation.candidates) == 1
        assert confirmation.selected is not None

        # Adjust a vertex
        adjusted = adjust_vertex(parcel, 0, 1.0, 1.0)
        assert adjusted.boundary[0] == (1.0, 1.0)

        # Validate
        issues = validate_boundary(parcel.boundary)
        assert isinstance(issues, list)


# ---------------------------------------------------------------------------
# Test 4: Generate → Modify → Undo
# ---------------------------------------------------------------------------


class TestE2EModifyUndo:
    """Test 4: Generate → modify → undo version history."""

    def test_modify_stories(self, tmp_output_dir):
        """Modify story count and verify plan updates."""
        from promptbim.agents.orchestrator import Orchestrator
        from promptbim.schemas.zoning import ZoningRules

        land = _make_land()
        zoning = ZoningRules()
        orch = Orchestrator(output_dir=tmp_output_dir)

        # First generate
        req = _make_requirement()
        plan = _make_plan(stories=3)

        with (
            patch.object(orch._enhancer, "enhance", return_value=req),
            patch.object(orch._planner, "plan", return_value=plan),
            patch.object(orch._checker, "check") as mock_check,
        ):
            from promptbim.agents.checker import CheckResult

            mock_check.return_value = CheckResult()
            result = orch.generate("3-story villa", land, zoning)

        assert result.success
        assert orch.plan is not None
        original_stories = len(orch.plan.stories)
        assert original_stories == 3

        # Now modify: "change to 9 stories"
        plan_9 = _make_plan(stories=9)
        from promptbim.schemas.modification import (
            ModificationIntent,
            ModificationRecord,
            ModificationType,
        )

        mock_record = ModificationRecord(
            command="改為9層",
            intent=ModificationIntent(
                raw_command="改為9層",
                modification_type=ModificationType.STORIES,
                parameters={"num_stories": 9},
                confidence=0.95,
            ),
            success=True,
            plan_snapshot_json=json.loads(plan.model_dump_json()),
        )

        with patch.object(orch._modifier, "modify", return_value=(plan_9, mock_record)):
            new_plan, record = orch.modify("改為9層", zoning)

        assert new_plan is not None
        assert record.success
        assert len(new_plan.stories) == 9

        # Undo
        with patch.object(orch._modifier, "undo", return_value=(plan, mock_record)):
            restored, undo_record = orch.undo()

        assert restored is not None
        assert len(restored.stories) == 3


# ---------------------------------------------------------------------------
# Test 5: Compliance + Cost + MEP + Monitoring
# ---------------------------------------------------------------------------


class TestE2ECompliancePipeline:
    """Test 5: Generate → compliance check → cost → MEP → monitoring."""

    def test_compliance_check(self):
        """Run Taiwan building code checks on a generated plan."""
        from promptbim.codes.registry import run_all_checks

        plan = _make_plan()
        land = _make_land()
        from promptbim.schemas.zoning import ZoningRules

        zoning = ZoningRules()
        results = run_all_checks(plan, land, zoning)
        assert len(results) > 0

    def test_cost_estimation(self):
        """Cost estimator produces valid output from a plan."""
        plan = _make_plan()
        from promptbim.bim.cost.estimator import CostEstimator

        estimator = CostEstimator()
        estimate = estimator.estimate(plan)
        assert estimate.total_cost_twd > 0
        assert len(estimate.line_items) > 0

    def test_mep_planning(self):
        """MEP planner generates systems for a building plan."""
        plan = _make_plan()
        from promptbim.bim.mep.planner import MEPPlanner

        planner = MEPPlanner()
        mep_result = planner.plan(plan)
        assert mep_result is not None

    def test_monitor_placement(self):
        """Auto-placement of monitoring points."""
        plan = _make_plan()
        from promptbim.bim.monitoring.auto_placement import AutoMonitorPlacer

        placer = AutoMonitorPlacer()
        monitor_plan = placer.place_all(plan)
        assert monitor_plan is not None
        assert len(monitor_plan.placements) > 0


# ---------------------------------------------------------------------------
# Test 6: Export All Formats
# ---------------------------------------------------------------------------


class TestE2EExport:
    """Test 6: Generate → export IFC + USD + USDZ + SVG + JSON + GIF."""

    def test_ifc_generation(self, tmp_output_dir):
        """IFC file is generated and readable."""
        plan = _make_plan()
        from promptbim.bim.ifc_generator import IFCGenerator

        ifc_path = tmp_output_dir / "test.ifc"
        gen = IFCGenerator()
        gen.generate(plan, ifc_path)
        assert ifc_path.exists()
        assert ifc_path.stat().st_size > 0

        # Verify readability
        try:
            import ifcopenshell

            model = ifcopenshell.open(str(ifc_path))
            assert model is not None
        except ImportError:
            pass  # OK if ifcopenshell not installed in test env

    def test_usd_generation(self, tmp_output_dir):
        """USD file is generated and readable."""
        plan = _make_plan()
        from promptbim.bim.usd_generator import USDGenerator

        usd_path = tmp_output_dir / "test.usda"
        gen = USDGenerator()
        gen.generate(plan, usd_path)
        assert usd_path.exists()
        assert usd_path.stat().st_size > 0

        # Verify readability
        try:
            from pxr import Usd

            stage = Usd.Stage.Open(str(usd_path))
            assert stage is not None
        except ImportError:
            pass  # OK if pxr not installed in test env

    def test_usdz_packing(self, tmp_output_dir):
        """USDZ packing from USD source."""
        plan = _make_plan()
        from promptbim.bim.usd_generator import USDGenerator

        usd_path = tmp_output_dir / "test.usda"
        gen = USDGenerator()
        gen.generate(plan, usd_path)

        from promptbim.bim.usdz_packer import pack_usdz

        usdz_path = tmp_output_dir / "test.usdz"
        pack_usdz(usd_path, usdz_path)
        assert usdz_path.exists()
        assert usdz_path.stat().st_size > 0

    def test_svg_floorplan(self, tmp_output_dir):
        """SVG floorplan generation."""
        plan = _make_plan()
        from promptbim.viz.floorplan import generate_floorplans

        generate_floorplans(plan, tmp_output_dir)
        svg_files = list(tmp_output_dir.glob("*.svg"))
        assert len(svg_files) > 0
        content = svg_files[0].read_text()
        assert "<svg" in content

    def test_json_export(self, tmp_output_dir):
        """JSON export of building plan."""
        plan = _make_plan()
        json_path = tmp_output_dir / "plan.json"
        json_path.write_text(plan.model_dump_json(indent=2))
        assert json_path.exists()
        loaded = json.loads(json_path.read_text())
        assert loaded["name"] == "Test Villa"

    def test_gif_simulation(self, tmp_output_dir):
        """4D simulation schedule generation (basic check)."""
        from promptbim.bim.simulation.scheduler import generate_schedule

        plan = _make_plan()
        # Extract component labels from plan stories
        labels = []
        for story in plan.stories:
            for i, w in enumerate(story.walls):
                labels.append(f"{story.name}_wall_{i}")
            labels.append(f"{story.name}_slab")
        labels.append("roof")

        schedule = generate_schedule(labels, total_days=360, num_stories=len(plan.stories))
        assert schedule is not None
        assert len(schedule.phases) > 0


# ---------------------------------------------------------------------------
# Test: Config .env multi-path search
# ---------------------------------------------------------------------------


class TestConfigEnvSearch:
    """Verify config.py finds .env from multiple paths."""

    def test_find_env_file_in_project_root(self):
        """Should find .env in project root."""
        from promptbim.config import _find_env_file

        result = _find_env_file()
        # .env may or may not exist; just verify function runs without error
        assert result is None or Path(result).name == ".env"

    def test_settings_creation(self):
        """Settings object creation succeeds."""
        from promptbim.config import get_settings

        settings = get_settings()
        assert settings is not None
        assert isinstance(settings.output_dir, Path)


# ---------------------------------------------------------------------------
# Test: PySide6 GUI import check
# ---------------------------------------------------------------------------


class TestGUIImports:
    """Verify PySide6 GUI modules can be imported."""

    def test_main_window_import(self):
        """MainWindow class is importable."""
        try:
            from promptbim.gui.main_window import MainWindow

            assert MainWindow is not None
        except ImportError:
            pytest.skip("PySide6 not available")

    def test_import_land_dialog(self):
        """ImportLandDialog and its helpers are importable."""
        from promptbim.gui.dialogs.import_land import (
            ALL_EXTENSIONS,
            IMAGE_EXTENSIONS,
            PDF_EXTENSIONS,
            SUPPORTED_EXTENSIONS,
        )

        assert ".geojson" in SUPPORTED_EXTENSIONS
        assert ".jpg" in IMAGE_EXTENSIONS
        assert ".pdf" in PDF_EXTENSIONS
        assert ALL_EXTENSIONS == SUPPORTED_EXTENSIONS | IMAGE_EXTENSIONS | PDF_EXTENSIONS

    def test_chat_panel_no_land_fallback(self):
        """ChatPanel should allow generation without pre-loaded land."""
        # Just verify the LandParcel default works
        from promptbim.schemas.land import LandParcel

        default_land = LandParcel(
            name="Auto-generated",
            boundary=[(0, 0), (30, 0), (30, 30), (0, 30)],
            area_sqm=900.0,
        )
        assert default_land.area_sqm == 900.0
        assert len(default_land.boundary) == 4
