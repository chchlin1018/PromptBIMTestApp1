"""Task 24: Tests for demo data module."""

from promptbim.demo.demo_data import (
    get_demo_cost_estimate,
    get_demo_land,
    get_demo_plan,
    get_demo_result,
    get_demo_zoning,
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
