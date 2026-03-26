"""Tests for bim/monitoring/usd_monitor.py — USD monitoring output."""

from pxr import Usd, UsdGeom

from promptbim.bim.monitoring.auto_placement import MonitorPlacement, MonitorPlan
from promptbim.bim.monitoring.usd_monitor import USDMonitorGenerator


def _make_test_monitor_plan() -> MonitorPlan:
    return MonitorPlan(
        placements=[
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
                monitor_type_id="cctv_camera",
                name="CCTV_1F_Lobby_0",
                floor="1F",
                space_name="Lobby",
                position=(2.0, 3.0, 2.7),
                ifc_class="IfcSensor",
                predefined_type="VIDEOCAMERA",
                category="security",
                unit_cost_twd=12000,
            ),
        ]
    )


class TestUSDMonitorGenerator:
    def test_generate_standalone(self, tmp_path):
        plan = _make_test_monitor_plan()
        gen = USDMonitorGenerator()
        out = gen.generate_standalone(plan, tmp_path / "monitoring.usda")
        assert out.exists()

        stage = Usd.Stage.Open(str(out))
        assert stage is not None

    def test_monitor_namespace_attributes(self, tmp_path):
        plan = _make_test_monitor_plan()
        gen = USDMonitorGenerator()
        out = gen.generate_standalone(plan, tmp_path / "monitoring.usda")

        stage = Usd.Stage.Open(str(out))
        # Find any prim with monitor: attributes
        found = False
        for prim in stage.Traverse():
            attr = prim.GetAttribute("monitor:type_id")
            if attr and attr.IsValid():
                val = attr.Get()
                if val == "temp_sensor":
                    found = True
                    # Check other monitor: attributes
                    assert prim.GetAttribute("monitor:category").Get() == "environmental"
                    assert prim.GetAttribute("monitor:floor").Get() == "1F"
                    break
        assert found, "No prim with monitor:type_id='temp_sensor' found"

    def test_spheres_created(self, tmp_path):
        plan = _make_test_monitor_plan()
        gen = USDMonitorGenerator()
        out = gen.generate_standalone(plan, tmp_path / "monitoring.usda")

        stage = Usd.Stage.Open(str(out))
        spheres = [p for p in stage.Traverse() if p.GetTypeName() == "Sphere"]
        assert len(spheres) == 2

    def test_up_axis_z(self, tmp_path):
        plan = _make_test_monitor_plan()
        gen = USDMonitorGenerator()
        out = gen.generate_standalone(plan, tmp_path / "monitoring.usda")
        stage = Usd.Stage.Open(str(out))
        assert UsdGeom.GetStageUpAxis(stage) == UsdGeom.Tokens.z

    def test_empty_plan(self, tmp_path):
        plan = MonitorPlan(placements=[])
        gen = USDMonitorGenerator()
        out = gen.generate_standalone(plan, tmp_path / "empty.usda")
        stage = Usd.Stage.Open(str(out))
        assert stage is not None
