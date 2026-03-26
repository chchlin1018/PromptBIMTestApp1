"""Tests for the rule registry and report generation."""

import json

from promptbim.codes.base import Severity
from promptbim.codes.registry import ALL_RULES, get_compliance_summary, run_all_checks
from promptbim.codes.report import (
    generate_report_json,
    generate_report_table,
    report_to_json_string,
)
from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import BuildingPlan, RoofPlan, SpaceDef, StoryPlan, WallDef
from promptbim.schemas.zoning import ZoningRules


def _land(area: float = 500.0) -> LandParcel:
    side = area**0.5
    return LandParcel(
        boundary=[(0, 0), (side, 0), (side, side), (0, side)],
        area_sqm=area,
    )


def _zoning(**kwargs) -> ZoningRules:
    defaults = dict(bcr_limit=0.6, far_limit=2.0, height_limit_m=15.0)
    defaults.update(kwargs)
    return ZoningRules(**defaults)


def _plan(
    footprint_side: float = 15.0,
    num_stories: int = 3,
    story_height: float = 3.0,
) -> BuildingPlan:
    fp = [(0, 0), (footprint_side, 0), (footprint_side, footprint_side), (0, footprint_side)]
    stories = []
    for i in range(num_stories):
        stories.append(
            StoryPlan(
                name=f"{i + 1}F",
                elevation_m=i * story_height,
                height_m=story_height,
                walls=[
                    WallDef(start=(0, 0), end=(footprint_side, 0)),
                    WallDef(start=(footprint_side, 0), end=(footprint_side, footprint_side)),
                    WallDef(start=(footprint_side, footprint_side), end=(0, footprint_side)),
                    WallDef(start=(0, footprint_side), end=(0, 0)),
                ],
                spaces=[
                    SpaceDef(
                        name=f"Room {i + 1}F",
                        boundary=fp,
                        space_type="office",
                        area_sqm=footprint_side**2,
                    )
                ],
                slab_boundary=fp,
            )
        )
    return BuildingPlan(
        name="Test Building",
        building_footprint=fp,
        building_bcr=footprint_side**2 / 500,
        building_far=footprint_side**2 * num_stories / 500,
        stories=stories,
        roof=RoofPlan(),
    )


class TestRegistry:
    def test_all_rules_count(self):
        assert len(ALL_RULES) >= 15

    def test_run_all_checks_returns_results(self):
        results = run_all_checks(_plan(), _land(), _zoning())
        assert len(results) >= 15

    def test_compliance_summary(self):
        results = run_all_checks(_plan(), _land(), _zoning())
        summary = get_compliance_summary(results)
        assert "total_rules" in summary
        assert "passed" in summary
        assert "failed" in summary
        assert "compliance_rate" in summary
        assert summary["total_rules"] == len(results)

    def test_compliant_building_passes(self):
        # 15x15 = 225 sqm footprint, BCR=0.45, 3 stories, 9m height
        results = run_all_checks(_plan(), _land(), _zoning())
        fails = [r for r in results if r.severity == Severity.FAIL]
        assert len(fails) == 0

    def test_violating_building_detected(self):
        # 20x20 = 400 sqm footprint, BCR=0.80 > 0.60
        plan = _plan(footprint_side=20.0)
        results = run_all_checks(plan, _land(), _zoning(bcr_limit=0.6))
        fails = [r for r in results if r.severity == Severity.FAIL]
        assert len(fails) >= 1
        assert any("BCR" in r.rule_id for r in fails)


class TestReport:
    def test_generate_report_json(self):
        results = run_all_checks(_plan(), _land(), _zoning())
        report = generate_report_json(
            results, project_name="Test", location="台北市", zoning_name="商三"
        )
        assert report["project"] == "Test"
        assert report["location"] == "台北市"
        assert "results" in report
        assert len(report["results"]) >= 15
        assert "disclaimer" in report

    def test_generate_report_table(self):
        results = run_all_checks(_plan(), _land(), _zoning())
        table = generate_report_table(results)
        assert "台灣建築法規合規檢查報告" in table
        assert "合規率" in table

    def test_report_to_json_string(self):
        results = run_all_checks(_plan(), _land(), _zoning())
        s = report_to_json_string(results, project_name="Test")
        parsed = json.loads(s)
        assert parsed["project"] == "Test"
