"""Tests for agents/checker.py — CheckerAgent (deterministic rules)."""

import pytest

from promptbim.agents.checker import CheckerAgent, CheckResult, CheckViolation
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan, StoryPlan, WallDef, RoofPlan
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
                slab_boundary=footprint,
            ),
        ],
        roof=RoofPlan(roof_type="flat"),
    )


class TestCheckerRules:
    def test_compliant_plan_passes(self, compliant_plan, sample_land, sample_zoning):
        checker = CheckerAgent.__new__(CheckerAgent)
        violations = checker._check_rules(compliant_plan, sample_land, sample_zoning)
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) == 0

    def test_bcr_violation(self, sample_land, sample_zoning):
        plan = BuildingPlan(
            name="Over BCR",
            building_bcr=0.9,  # exceeds 0.6 limit
            building_far=0.9,
            stories=[StoryPlan(name="1F", elevation_m=0.0, height_m=3.0)],
        )
        checker = CheckerAgent.__new__(CheckerAgent)
        violations = checker._check_rules(plan, sample_land, sample_zoning)
        assert any(v.rule == "BCR" for v in violations)

    def test_far_violation(self, sample_land, sample_zoning):
        plan = BuildingPlan(
            name="Over FAR",
            building_bcr=0.5,
            building_far=3.0,  # exceeds 2.0 limit
            stories=[StoryPlan(name="1F", elevation_m=0.0, height_m=3.0)],
        )
        checker = CheckerAgent.__new__(CheckerAgent)
        violations = checker._check_rules(plan, sample_land, sample_zoning)
        assert any(v.rule == "FAR" for v in violations)

    def test_height_violation(self, sample_land, sample_zoning):
        plan = BuildingPlan(
            name="Too Tall",
            building_bcr=0.3,
            building_far=1.5,
            stories=[
                StoryPlan(name=f"{i+1}F", elevation_m=i * 3.0, height_m=3.0)
                for i in range(6)  # 18m > 15m limit
            ],
        )
        checker = CheckerAgent.__new__(CheckerAgent)
        violations = checker._check_rules(plan, sample_land, sample_zoning)
        assert any(v.rule == "Height" for v in violations)

    def test_min_height_warning(self, sample_land, sample_zoning):
        plan = BuildingPlan(
            name="Low Ceiling",
            building_bcr=0.3,
            building_far=0.3,
            stories=[StoryPlan(name="1F", elevation_m=0.0, height_m=2.0)],
        )
        checker = CheckerAgent.__new__(CheckerAgent)
        violations = checker._check_rules(plan, sample_land, sample_zoning)
        assert any(v.rule == "MinHeight" and v.severity == "warning" for v in violations)


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
