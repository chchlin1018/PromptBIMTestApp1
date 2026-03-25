"""Performance and edge case tests."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan
from promptbim.bim.templates import generate_from_template


# Standard test land
LAND = [(0, 0), (100, 0), (100, 80), (0, 80)]
BUILDABLE = [(5, 5), (95, 5), (95, 75), (5, 75)]


class TestPerformance:
    """Performance benchmarks — ensure key operations complete within time limits."""

    @pytest.mark.benchmark
    def test_template_generation_speed(self):
        """All templates should generate plans in under 1 second."""
        for key in ["school", "hospital", "factory"]:
            start = time.monotonic()
            plan = generate_from_template(key, LAND, BUILDABLE)
            elapsed = time.monotonic() - start
            assert elapsed < 1.0, f"{key} template took {elapsed:.2f}s"
            assert len(plan.stories) > 0

    @pytest.mark.benchmark
    def test_ifc_generation_speed(self, tmp_path: Path):
        """IFC generation for a 5-story building should complete in under 3 seconds."""
        plan = generate_from_template("hospital", LAND, BUILDABLE, num_stories=5)

        from promptbim.bim.ifc_generator import IFCGenerator

        start = time.monotonic()
        IFCGenerator().generate(plan, tmp_path / "perf.ifc")
        elapsed = time.monotonic() - start
        assert elapsed < 3.0, f"IFC generation took {elapsed:.2f}s"

    @pytest.mark.benchmark
    def test_usd_generation_speed(self, tmp_path: Path):
        """USD generation should complete in under 3 seconds."""
        plan = generate_from_template("school", LAND, BUILDABLE, num_stories=4)

        from promptbim.bim.usd_generator import USDGenerator

        start = time.monotonic()
        USDGenerator().generate(plan, tmp_path / "perf.usda")
        elapsed = time.monotonic() - start
        assert elapsed < 3.0, f"USD generation took {elapsed:.2f}s"

    @pytest.mark.benchmark
    def test_compliance_check_speed(self):
        """Compliance check (run_all_checks) should complete in under 1 second."""
        from promptbim.schemas.zoning import ZoningRules
        from promptbim.codes.registry import run_all_checks

        plan = generate_from_template("school", LAND, BUILDABLE)

        start = time.monotonic()
        results = run_all_checks(
            plan,
            LandParcel(name="P", boundary=LAND, area_sqm=8000.0),
            ZoningRules(),
        )
        elapsed = time.monotonic() - start
        assert elapsed < 1.0, f"Compliance check took {elapsed:.2f}s"

    @pytest.mark.benchmark
    def test_cost_estimation_speed(self):
        """Cost estimation should complete in under 1 second."""
        from promptbim.bim.cost.estimator import CostEstimator

        plan = generate_from_template("hospital", LAND, BUILDABLE, num_stories=5)

        start = time.monotonic()
        estimate = CostEstimator().estimate(plan)
        elapsed = time.monotonic() - start
        assert elapsed < 1.0, f"Cost estimation took {elapsed:.2f}s"
        assert estimate.total_cost_twd > 0

    @pytest.mark.benchmark
    def test_schedule_generation_speed(self, tmp_path: Path):
        """Schedule generation should complete in under 2 seconds."""
        from promptbim.bim.simulation.scheduler import generate_schedule
        from promptbim.bim.ifc_generator import IFCGenerator
        import ifcopenshell

        plan = generate_from_template("school", LAND, BUILDABLE, num_stories=3)
        ifc_path = tmp_path / "sched.ifc"
        IFCGenerator().generate(plan, ifc_path)
        model = ifcopenshell.open(str(ifc_path))
        labels = [e.is_a() for e in model.by_type("IfcProduct")]

        start = time.monotonic()
        schedule = generate_schedule(labels, num_stories=len(plan.stories))
        elapsed = time.monotonic() - start
        assert elapsed < 2.0, f"Schedule generation took {elapsed:.2f}s"
        assert len(schedule.phases) > 0

    @pytest.mark.benchmark
    def test_full_pipeline_speed(self, tmp_path: Path):
        """Full pipeline (template -> IFC -> USD -> cost -> compliance) with mock AI < 5s."""
        from promptbim.bim.ifc_generator import IFCGenerator
        from promptbim.bim.usd_generator import USDGenerator
        from promptbim.bim.cost.estimator import CostEstimator
        from promptbim.codes.registry import run_all_checks
        from promptbim.schemas.zoning import ZoningRules

        start = time.monotonic()

        plan = generate_from_template("hospital", LAND, BUILDABLE, num_stories=3)
        IFCGenerator().generate(plan, tmp_path / "pipe.ifc")
        USDGenerator().generate(plan, tmp_path / "pipe.usda")
        CostEstimator().estimate(plan)
        run_all_checks(
            plan,
            LandParcel(name="P", boundary=LAND, area_sqm=8000.0),
            ZoningRules(),
        )

        elapsed = time.monotonic() - start
        assert elapsed < 5.0, f"Full pipeline took {elapsed:.2f}s"


class TestEdgeCases:
    """Edge case handling."""

    def test_very_small_land(self):
        """Templates should handle very small land parcels without crashing."""
        small_land = [(0, 0), (5, 0), (5, 5), (0, 5)]
        small_buildable = [(1, 1), (4, 1), (4, 4), (1, 4)]
        for key in ["school", "hospital", "factory"]:
            plan = generate_from_template(key, small_land, small_buildable)
            assert isinstance(plan, BuildingPlan)
            assert len(plan.stories) > 0

    def test_large_story_count(self):
        """Generate a 20-story hospital."""
        plan = generate_from_template("hospital", LAND, BUILDABLE, num_stories=20)
        assert len(plan.stories) == 20

    def test_single_story_factory(self):
        plan = generate_from_template("factory", LAND, BUILDABLE, num_stories=1)
        assert len(plan.stories) == 1

    def test_irregular_land_shape(self):
        """L-shaped land parcel."""
        l_land = [(0, 0), (60, 0), (60, 30), (30, 30), (30, 60), (0, 60)]
        l_buildable = [(5, 5), (55, 5), (55, 25), (25, 25), (25, 55), (5, 55)]
        plan = generate_from_template("school", l_land, l_buildable)
        assert isinstance(plan, BuildingPlan)

    def test_empty_buildable_area(self):
        """When buildable area is empty, should still produce a plan."""
        plan = generate_from_template("school", LAND, [])
        assert isinstance(plan, BuildingPlan)
        assert len(plan.stories) > 0

    def test_plan_json_roundtrip(self):
        """Serialization roundtrip for all templates."""
        import json

        for key in ["school", "hospital", "factory"]:
            plan = generate_from_template(key, LAND, BUILDABLE)
            data = json.loads(plan.model_dump_json())
            restored = BuildingPlan.model_validate(data)
            assert restored.name == plan.name
            assert len(restored.stories) == len(plan.stories)

    def test_zero_area_wall_handled(self):
        """Wall with zero length should produce empty mesh."""
        from promptbim.bim.geometry import wall_mesh

        mesh = wall_mesh((5.0, 5.0), (5.0, 5.0), height=3.0)
        assert len(mesh.vertices) == 0

    def test_kml_no_polygon(self, tmp_path: Path):
        """KML with only Point geometry should return empty list."""
        kml = """\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>A Point</name>
      <Point><coordinates>121.5,25.0,0</coordinates></Point>
    </Placemark>
  </Document>
</kml>
"""
        p = tmp_path / "point.kml"
        p.write_text(kml, encoding="utf-8")
        from promptbim.land.parsers.kml import parse_kml

        parcels = parse_kml(p)
        assert parcels == []
