"""Tests for bim/monitoring/dashboard_data.py — JSON dashboard export."""

import json

import pytest

from promptbim.bim.monitoring.auto_placement import MonitorPlan, MonitorPlacement
from promptbim.bim.monitoring.dashboard_data import (
    export_dashboard_json,
    generate_dashboard_json,
)


def _make_test_plan() -> MonitorPlan:
    return MonitorPlan(placements=[
        MonitorPlacement(
            monitor_type_id="temp_sensor",
            name="Temp_1F_0",
            floor="1F",
            space_name="Office",
            position=(5.0, 5.0, 2.7),
            ifc_class="IfcSensor",
            predefined_type="TEMPERATURESENSOR",
            category="environmental",
            unit_cost_twd=3500,
        ),
        MonitorPlacement(
            monitor_type_id="temp_sensor",
            name="Temp_1F_1",
            floor="1F",
            space_name="Lobby",
            position=(2.0, 3.0, 2.7),
            ifc_class="IfcSensor",
            predefined_type="TEMPERATURESENSOR",
            category="environmental",
            unit_cost_twd=3500,
        ),
        MonitorPlacement(
            monitor_type_id="smoke_detector",
            name="Smoke_2F_0",
            floor="2F",
            space_name="Office",
            position=(5.0, 5.0, 6.2),
            ifc_class="IfcSensor",
            predefined_type="SMOKEDETECTOR",
            category="safety",
            unit_cost_twd=1500,
        ),
    ])


class TestDashboardData:
    def test_generate_json_structure(self):
        plan = _make_test_plan()
        data = generate_dashboard_json(plan, "Test Project")
        assert data["project"] == "Test Project"
        assert data["total_monitors"] == 3
        assert data["total_cost_twd"] == 8500

    def test_floor_summary(self):
        plan = _make_test_plan()
        data = generate_dashboard_json(plan)
        floors = {f["floor"]: f for f in data["floor_summary"]}
        assert floors["1F"]["count"] == 2
        assert floors["2F"]["count"] == 1

    def test_category_summary(self):
        plan = _make_test_plan()
        data = generate_dashboard_json(plan)
        cats = {c["category"]: c for c in data["category_summary"]}
        assert "environmental" in cats
        assert "safety" in cats
        assert cats["environmental"]["count"] == 2

    def test_type_detail(self):
        plan = _make_test_plan()
        data = generate_dashboard_json(plan)
        types = {t["type_id"]: t for t in data["type_detail"]}
        assert types["temp_sensor"]["count"] == 2
        assert types["smoke_detector"]["count"] == 1

    def test_sensor_list(self):
        plan = _make_test_plan()
        data = generate_dashboard_json(plan)
        assert len(data["sensors"]) == 3
        for s in data["sensors"]:
            assert "position" in s
            assert len(s["position"]) == 3

    def test_export_file(self, tmp_path):
        plan = _make_test_plan()
        out = export_dashboard_json(plan, tmp_path / "dashboard.json")
        assert out.exists()
        with open(out) as f:
            data = json.load(f)
        assert data["total_monitors"] == 3

    def test_empty_plan(self):
        plan = MonitorPlan(placements=[])
        data = generate_dashboard_json(plan)
        assert data["total_monitors"] == 0
        assert data["total_cost_twd"] == 0
