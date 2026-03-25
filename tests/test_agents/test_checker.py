"""Tests for agents/checker.py — CheckerAgent (Taiwan building code engine)."""

import pytest

from promptbim.agents.checker import CheckerAgent, CheckResult, CheckViolation
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan, SpaceDef, StoryPlan, WallDef, RoofPlan
from promptbim.schemas.zoning import ZoningRules


@pytest.fixture
def sample_land():
    return LandParcel(
        name="Test Parcel",
        boundary=[(0, 0), (30, 0), (30, 20), (0, 20)],
        area_sqm=600.0,
    )


@pytest.fixture
def sample_zoning():
    return ZoningRules(
        far_limit=2.0,
        bcr_limit=0.6,
        height_limit_m=15.0,
    )


@pytest.fixture
def compliant_plan():
    footprint = [(2, 3), (20, 3), (20, 17), (2, 17)]
    fp_area = 18 * 14  # 252 sqm
    return BuildingPlan(
        name="Compliant Building",
        building_footprint=footprint,
        buildable_area=[(2, 3), (28, 3), (28, 17), (2, 17)],
        building_bcr=0.42,
        building_far=0.84,
        stories=[
            StoryPlan(
                name="1F",
                elevation_m=0.0,
                height_m=3.0,
                walls=[
                    WallDef(start=(2, 3), end=(20, 3)),
                    WallDef(start=(20, 3), end=(20, 17)),
                    WallDef(start=(20, 17), end=(2, 17)),
                    WallDef(start=(2, 17), end=(2, 3)),
                ],
                spaces=[SpaceDef(name="Room 1F", boundary=footprint, space_type="office", area_sqm=fp_area)],
                slab_boundary=footprint,
            ),
            StoryPlan(
                name="2F",
                elevation_m=3.0,
                height_m=3.0,
                walls=[
                    WallDef(start=(2, 3), end=(20, 3)),
                    WallDef(start=(20, 3), end=(20, 17)),
                    WallDef(start=(20, 17), end=(2, 17)),
                    WallDef(start=(2, 17), end=(2, 3)),
                ],
                spaces=[SpaceDef(name="Room 2F", boundary=footprint, space_type="office", area_sqm=fp_area)],
                slab_boundary=footprint,
            ),
        ],
        roof=RoofPlan(roof_type="flat"),
    )


class TestCheckerRules:
    def test_compliant_plan_passes(self, compliant_plan, sample_land, sample_zoning):
        checker = CheckerAgent.__new__(CheckerAgent)
        result = checker.check(compliant_plan, sample_land, sample_zoning)
        errors = [v for v in result.violations if v.severity == "error"]
        assert len(errors) == 0

    def test_bcr_violation(self, sample_land, sample_zoning):
        # 25x20 = 500 sqm footprint on 600 sqm land = 83% BCR > 60%
        fp = [(0, 0), (25, 0), (25, 20), (0, 20)]
        plan = BuildingPlan(
            name="Over BCR",
            building_footprint=fp,
            building_bcr=0.83,
            building_far=0.83,
            stories=[StoryPlan(
                name="1F", elevation_m=0.0, height_m=3.0,
                spaces=[SpaceDef(name="Room", boundary=fp, space_type="office", area_sqm=500)],
                slab_boundary=fp,
            )],
        )
        checker = CheckerAgent.__new__(CheckerAgent)
        result = checker.check(plan, sample_land, sample_zoning)
        assert any("BCR" in v.rule for v in result.violations if v.severity == "error")

    def test_far_violation(self, sample_land, sample_zoning):
        # 20x20=400 sqm x 4 stories = 1600/600 = 2.67 FAR > 2.0
        fp = [(0, 0), (20, 0), (20, 20), (0, 20)]
        plan = BuildingPlan(
            name="Over FAR",
            building_footprint=fp,
            building_bcr=0.67,
            building_far=2.67,
            stories=[
                StoryPlan(
                    name=f"{i+1}F", elevation_m=i * 3.0, height_m=3.0,
                    spaces=[SpaceDef(name=f"Room {i+1}F", boundary=fp, space_type="office", area_sqm=400)],
                    slab_boundary=fp,
                )
                for i in range(4)
            ],
        )
        checker = CheckerAgent.__new__(CheckerAgent)
        result = checker.check(plan, sample_land, sample_zoning)
        assert any("FAR" in v.rule for v in result.violations if v.severity == "error")

    def test_height_violation(self, sample_land, sample_zoning):
        fp = [(0, 0), (10, 0), (10, 10), (0, 10)]
        plan = BuildingPlan(
            name="Too Tall",
            building_footprint=fp,
            building_bcr=0.17,
            building_far=1.0,
            stories=[
                StoryPlan(
                    name=f"{i+1}F", elevation_m=i * 3.0, height_m=3.0,
                    spaces=[SpaceDef(name=f"Room {i+1}F", boundary=fp, space_type="office", area_sqm=100)],
                    slab_boundary=fp,
                )
                for i in range(6)  # 18m > 15m limit
            ],
        )
        checker = CheckerAgent.__new__(CheckerAgent)
        result = checker.check(plan, sample_land, sample_zoning)
        assert any("24-1" in v.rule or "Height" in v.rule for v in result.violations if v.severity == "error")

    def test_ceiling_height_violation(self, sample_land, sample_zoning):
        fp = [(0, 0), (10, 0), (10, 10), (0, 10)]
        plan = BuildingPlan(
            name="Low Ceiling",
            building_footprint=fp,
            building_bcr=0.17,
            building_far=0.17,
            stories=[StoryPlan(
                name="1F", elevation_m=0.0, height_m=2.2,
                spaces=[SpaceDef(name="Room", boundary=fp, space_type="office", area_sqm=100)],
                slab_boundary=fp,
            )],
        )
        checker = CheckerAgent.__new__(CheckerAgent)
        result = checker.check(plan, sample_land, sample_zoning)
        # Ceiling height 2.2 - 0.2 slab = 2.0m < 2.1m min
        assert any("26" in v.rule for v in result.violations if v.severity == "error")


class TestCheckerIntegration:
    def test_compliance_summary_in_result(self, compliant_plan, sample_land, sample_zoning):
        checker = CheckerAgent.__new__(CheckerAgent)
        result = checker.check(compliant_plan, sample_land, sample_zoning)
        assert result.compliance_summary
        assert "total_rules" in result.compliance_summary
        assert "compliance_rate" in result.compliance_summary

    def test_report_text_generated(self, compliant_plan, sample_land, sample_zoning):
        checker = CheckerAgent.__new__(CheckerAgent)
        result = checker.check(compliant_plan, sample_land, sample_zoning)
        assert "合規檢查報告" in result.report_text

    def test_code_results_populated(self, compliant_plan, sample_land, sample_zoning):
        checker = CheckerAgent.__new__(CheckerAgent)
        result = checker.check(compliant_plan, sample_land, sample_zoning)
        assert len(result.code_results) >= 15


class TestCheckResult:
    def test_passed_when_no_errors(self):
        result = CheckResult(violations=[
            CheckViolation(rule="Test", message="ok", severity="warning")
        ])
        assert result.passed is True

    def test_not_passed_when_errors(self):
        result = CheckResult(violations=[
            CheckViolation(rule="BCR", message="exceeded", severity="error")
        ])
        assert result.passed is False
