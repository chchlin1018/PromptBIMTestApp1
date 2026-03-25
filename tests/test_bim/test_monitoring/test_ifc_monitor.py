"""Tests for bim/monitoring/ifc_monitor.py — IFC monitoring output."""

import tempfile
from pathlib import Path

import pytest
import ifcopenshell

from promptbim.bim.monitoring.auto_placement import MonitorPlan, MonitorPlacement
from promptbim.bim.monitoring.ifc_monitor import IFCMonitorGenerator


def _make_test_monitor_plan() -> MonitorPlan:
    return MonitorPlan(placements=[
        MonitorPlacement(
            monitor_type_id="temp_sensor",
            name="TempSensor_1F_Office_0",
            floor="1F",
            space_name="Office",
            position=(5.0, 5.0, 2.7),
            ifc_class="IfcSensor",
            predefined_type="TEMPERATURESENSOR",
            category="environmental",
            unit_cost_twd=3500,
        ),
        MonitorPlacement(
            monitor_type_id="smoke_detector",
            name="SmokeDetector_1F_Office_0",
            floor="1F",
            space_name="Office",
            position=(10.0, 5.0, 2.7),
            ifc_class="IfcSensor",
            predefined_type="SMOKEDETECTOR",
            category="safety",
            unit_cost_twd=1500,
        ),
        MonitorPlacement(
            monitor_type_id="lighting_controller",
            name="LightCtrl_2F_Meeting_0",
            floor="2F",
            space_name="Meeting",
            position=(3.0, 3.0, 6.2),
            ifc_class="IfcActuator",
            predefined_type="LIGHTINGCONTROLLER",
            category="smart",
            unit_cost_twd=5000,
        ),
    ])


class TestIFCMonitorGenerator:
    def test_generate_standalone(self, tmp_path):
        plan = _make_test_monitor_plan()
        gen = IFCMonitorGenerator()
        out = gen.generate_standalone(plan, tmp_path / "monitoring.ifc")
        assert out.exists()

        ifc = ifcopenshell.open(str(out))
        sensors = ifc.by_type("IfcSensor")
        actuators = ifc.by_type("IfcActuator")
        assert len(sensors) == 2
        assert len(actuators) == 1

    def test_sensors_have_names(self, tmp_path):
        plan = _make_test_monitor_plan()
        gen = IFCMonitorGenerator()
        out = gen.generate_standalone(plan, tmp_path / "mon.ifc")
        ifc = ifcopenshell.open(str(out))
        names = {e.Name for e in ifc.by_type("IfcSensor")}
        assert "TempSensor_1F_Office_0" in names
        assert "SmokeDetector_1F_Office_0" in names

    def test_storeys_created(self, tmp_path):
        plan = _make_test_monitor_plan()
        gen = IFCMonitorGenerator()
        out = gen.generate_standalone(plan, tmp_path / "mon.ifc")
        ifc = ifcopenshell.open(str(out))
        storeys = {s.Name for s in ifc.by_type("IfcBuildingStorey")}
        assert "1F" in storeys
        assert "2F" in storeys

    def test_file_reopenable(self, tmp_path):
        plan = _make_test_monitor_plan()
        gen = IFCMonitorGenerator()
        out = gen.generate_standalone(plan, tmp_path / "mon.ifc")
        ifc = ifcopenshell.open(str(out))
        assert ifc.by_type("IfcProject")

    def test_empty_plan(self, tmp_path):
        plan = MonitorPlan(placements=[])
        gen = IFCMonitorGenerator()
        out = gen.generate_standalone(plan, tmp_path / "empty.ifc")
        ifc = ifcopenshell.open(str(out))
        assert len(ifc.by_type("IfcSensor")) == 0
