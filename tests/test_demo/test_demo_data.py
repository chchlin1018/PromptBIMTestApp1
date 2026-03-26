"""Task 24: Tests for demo data module + P24 3D generation tests."""

import pytest

from promptbim.demo.demo_data import (
    generate_all_demo_resources,
    generate_demo_ifc,
    generate_demo_svg,
    generate_demo_usda,
    get_demo_cost_estimate,
    get_demo_land,
    get_demo_plan,
    get_demo_result,
    get_demo_zoning,
    save_demo_resources,
)


class TestDemoLand:
    def test_demo_land_valid(self):
        land = get_demo_land()
        assert land.name.startswith("台北市")
        assert land.area_sqm > 400
        assert len(land.boundary) >= 3
        assert land.perimeter_m > 0

    def test_demo_zoning_xinyi(self):
        zoning = get_demo_zoning()
        assert zoning.zone_type == "residential"
        assert zoning.far_limit == 2.4
        assert zoning.bcr_limit == 0.6
        assert zoning.height_limit_m == 21.0


class TestDemoPlan:
    def test_demo_plan_structure(self):
        plan = get_demo_plan()
        assert plan.name
        assert len(plan.stories) == 3
        assert plan.stories[0].name == "1F"
        assert plan.stories[1].name == "2F"
        assert plan.stories[2].name == "3F"
        assert plan.building_bcr > 0
        assert plan.building_far > 0
        assert len(plan.building_footprint) >= 3

    def test_demo_plan_compliance(self):
        plan = get_demo_plan()
        zoning = get_demo_zoning()
        assert plan.building_bcr <= zoning.bcr_limit
        assert plan.building_far <= zoning.far_limit


class TestDemoResult:
    def test_demo_result_success(self):
        result = get_demo_result()
        assert result.success is True
        assert result.building_name
        assert "stories" in result.summary
        assert result.summary["stories"] == 3
        assert result.compliance_report
        assert result.compliance_text

    def test_demo_cost_estimate(self):
        cost = get_demo_cost_estimate()
        assert cost["total_cost_twd"] > 0
        assert cost["cost_per_sqm_twd"] == 85000
        assert len(cost["breakdown"]) == 5
        assert cost["currency"] == "TWD"


# ---------------------------------------------------------------------------
# P24 Task 8: Demo 3D generation tests
# ---------------------------------------------------------------------------


class TestDemoIFCGeneration:
    """Test IFC file generation from demo plan."""

    def test_generate_demo_ifc_produces_file(self, tmp_path):
        path = generate_demo_ifc(output_dir=tmp_path)
        assert path.exists()
        assert path.suffix == ".ifc"
        assert path.stat().st_size > 100  # non-trivial content

    def test_generate_demo_ifc_valid_content(self, tmp_path):
        path = generate_demo_ifc(output_dir=tmp_path)
        content = path.read_text(encoding="utf-8", errors="replace")
        assert "IFC" in content
        assert "IfcProject" in content or "IFCPROJECT" in content


class TestDemoUSDGeneration:
    """Test USDA file generation from demo plan."""

    def test_generate_demo_usda_produces_file(self, tmp_path):
        path = generate_demo_usda(output_dir=tmp_path)
        assert path.exists()
        assert path.suffix == ".usda"
        assert path.stat().st_size > 100

    def test_generate_demo_usda_valid_content(self, tmp_path):
        path = generate_demo_usda(output_dir=tmp_path)
        content = path.read_text(encoding="utf-8")
        assert "Building" in content
        assert "UsdPreviewSurface" in content or "Mesh" in content


class TestDemoSVGGeneration:
    """Test SVG floor plan generation."""

    def test_generate_demo_svg_produces_files(self, tmp_path):
        paths = generate_demo_svg(output_dir=tmp_path)
        assert len(paths) >= 4  # 3 floors + 1 site plan
        for p in paths:
            assert p.exists()
            assert p.suffix == ".svg"
            content = p.read_text()
            assert "<svg" in content


class TestGenerateAllDemoResources:
    """Test the integration function that generates everything."""

    def test_generate_all_produces_expected_keys(self, tmp_path, monkeypatch):
        # Redirect DEMO_RESOURCES_DIR to tmp
        import promptbim.demo.demo_data as dd
        monkeypatch.setattr(dd, "DEMO_RESOURCES_DIR", tmp_path)
        paths = generate_all_demo_resources()
        assert "plan" in paths
        assert "cost_estimate" in paths

    def test_save_demo_resources_json(self, tmp_path, monkeypatch):
        import promptbim.demo.demo_data as dd
        monkeypatch.setattr(dd, "DEMO_RESOURCES_DIR", tmp_path)
        paths = save_demo_resources()
        assert paths["plan"].exists()
        assert paths["cost_estimate"].exists()
        assert paths["compliance_report"].exists()
