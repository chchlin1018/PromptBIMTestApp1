"""End-to-end integration test: land input -> template -> BIM -> export.

Tests the full pipeline without requiring Claude API keys by using
the template-based generation path (deterministic, no LLM).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan
from promptbim.bim.templates import generate_from_template, list_templates


# --- Test land parcel (50m x 40m) ---
TEST_LAND = LandParcel(
    name="E2E Test Parcel",
    boundary=[(0, 0), (50, 0), (50, 40), (0, 40)],
    area_sqm=2000.0,
    perimeter_m=180.0,
    crs="local",
    source_type="manual",
)
TEST_BUILDABLE = [(5, 5), (45, 5), (45, 35), (5, 35)]


class TestE2EPipeline:
    """Test the full pipeline: land -> template -> IFC -> USD -> USDZ -> export."""

    @pytest.mark.parametrize("template_key", list_templates())
    def test_template_to_ifc(self, template_key: str, tmp_path: Path):
        """Generate from template -> produce IFC file."""
        plan = generate_from_template(
            template_key, TEST_LAND.boundary, TEST_BUILDABLE
        )
        assert isinstance(plan, BuildingPlan)
        assert len(plan.stories) > 0

        # Generate IFC
        from promptbim.bim.ifc_generator import IFCGenerator

        ifc_path = tmp_path / f"{template_key}.ifc"
        gen = IFCGenerator()
        gen.generate(plan, ifc_path)
        assert ifc_path.exists()
        assert ifc_path.stat().st_size > 0

        # Verify IFC can be re-read
        import ifcopenshell

        model = ifcopenshell.open(str(ifc_path))
        assert model is not None
        walls = model.by_type("IfcWall")
        assert len(walls) > 0

    @pytest.mark.parametrize("template_key", list_templates())
    def test_template_to_usd(self, template_key: str, tmp_path: Path):
        """Generate from template -> produce USD file."""
        plan = generate_from_template(
            template_key, TEST_LAND.boundary, TEST_BUILDABLE
        )

        from promptbim.bim.usd_generator import USDGenerator

        usd_path = tmp_path / f"{template_key}.usda"
        gen = USDGenerator()
        gen.generate(plan, usd_path)
        assert usd_path.exists()
        assert usd_path.stat().st_size > 0

        # Verify USD can be opened
        from pxr import Usd

        stage = Usd.Stage.Open(str(usd_path))
        assert stage is not None

    def test_template_to_usdz(self, tmp_path: Path):
        """Generate from template -> USD -> USDZ."""
        plan = generate_from_template(
            "school", TEST_LAND.boundary, TEST_BUILDABLE
        )

        from promptbim.bim.usd_generator import USDGenerator
        from promptbim.bim.usdz_packer import pack_usdz

        usd_path = tmp_path / "school.usda"
        USDGenerator().generate(plan, usd_path)

        usdz_path = pack_usdz(usd_path)
        assert usdz_path.exists()
        assert usdz_path.suffix == ".usdz"
        assert usdz_path.stat().st_size > 0

    def test_template_to_builder_agent(self, tmp_path: Path):
        """Test via BuilderAgent (the full Agent 3 path)."""
        plan = generate_from_template(
            "hospital", TEST_LAND.boundary, TEST_BUILDABLE, num_stories=3
        )

        from promptbim.agents.builder import BuilderAgent

        agent = BuilderAgent(output_dir=tmp_path)
        result = agent.build(plan)

        assert result.ok
        assert result.ifc_path is not None
        assert result.usd_path is not None
        assert result.ifc_path.exists()
        assert result.usd_path.exists()

    def test_template_to_compliance_check(self):
        """Template -> Compliance check with Taiwan building code."""
        from promptbim.schemas.zoning import ZoningRules

        plan = generate_from_template(
            "school", TEST_LAND.boundary, TEST_BUILDABLE
        )

        from promptbim.codes.registry import run_all_checks

        results = run_all_checks(plan, TEST_LAND, ZoningRules())
        assert len(results) > 0
        # Each result should have required fields
        for r in results:
            assert hasattr(r, "rule_id")
            assert hasattr(r, "severity")

    def test_template_to_cost_estimate(self):
        """Template -> Cost estimation."""
        plan = generate_from_template(
            "factory", TEST_LAND.boundary, TEST_BUILDABLE
        )

        from promptbim.bim.cost.estimator import CostEstimator

        estimator = CostEstimator()
        estimate = estimator.estimate(plan)
        assert estimate is not None
        assert estimate.total_cost_twd > 0

    def test_template_to_mep(self, tmp_path: Path):
        """Template -> MEP auto-routing."""
        plan = generate_from_template(
            "hospital", TEST_LAND.boundary, TEST_BUILDABLE, num_stories=2
        )

        from promptbim.bim.mep.planner import MEPPlanner

        planner = MEPPlanner()
        mep_result = planner.plan(plan)
        assert mep_result is not None
        # Should have routes or equipment
        assert len(mep_result.routes) > 0 or len(mep_result.equipment) > 0

    def test_template_to_simulation(self, tmp_path: Path):
        """Template -> Construction schedule."""
        plan = generate_from_template(
            "school", TEST_LAND.boundary, TEST_BUILDABLE
        )

        from promptbim.bim.ifc_generator import IFCGenerator

        ifc_path = tmp_path / "school.ifc"
        IFCGenerator().generate(plan, ifc_path)

        from promptbim.bim.simulation.scheduler import generate_schedule

        # Extract component labels from IFC
        import ifcopenshell
        model = ifcopenshell.open(str(ifc_path))
        labels = [e.is_a() for e in model.by_type("IfcProduct")]

        schedule = generate_schedule(labels, num_stories=len(plan.stories))
        assert schedule is not None
        assert len(schedule.phases) > 0

    def test_template_to_monitoring(self):
        """Template -> Auto monitoring placement."""
        plan = generate_from_template(
            "hospital", TEST_LAND.boundary, TEST_BUILDABLE, num_stories=2
        )

        from promptbim.bim.monitoring.auto_placement import AutoMonitorPlacer

        placer = AutoMonitorPlacer()
        monitor_plan = placer.place_all(plan)
        assert monitor_plan is not None
        assert len(monitor_plan.placements) > 0

    def test_template_json_roundtrip(self):
        """BuildingPlan JSON serialization roundtrip."""
        plan = generate_from_template(
            "school", TEST_LAND.boundary, TEST_BUILDABLE
        )

        # Serialize
        json_str = plan.model_dump_json()
        data = json.loads(json_str)

        # Deserialize
        restored = BuildingPlan.model_validate(data)
        assert restored.name == plan.name
        assert len(restored.stories) == len(plan.stories)

    def test_kml_to_parcel(self, tmp_path: Path):
        """KML import -> LandParcel."""
        kml_text = """\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Integration Test</name>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              121.5,25.0,0 121.502,25.0,0 121.502,25.002,0 121.5,25.002,0 121.5,25.0,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>
"""
        kml_file = tmp_path / "test.kml"
        kml_file.write_text(kml_text, encoding="utf-8")

        from promptbim.land.parsers.kml import parse_kml

        parcels = parse_kml(kml_file)
        assert len(parcels) == 1
        assert parcels[0].source_type == "kml"
        assert parcels[0].name == "Integration Test"
