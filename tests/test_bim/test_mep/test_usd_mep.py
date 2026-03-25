"""Tests for bim/mep/usd_mep.py — MEP USD generation."""

import pytest
from pxr import Usd, UsdGeom

from promptbim.bim.mep.pathfinder import RoutePath
from promptbim.bim.mep.planner import MEPPlan, MEPRoute
from promptbim.bim.mep.usd_mep import USDMEPGenerator


def _make_simple_mep_plan() -> MEPPlan:
    return MEPPlan(
        routes=[
            MEPRoute(
                system="plumbing",
                route_type="branch",
                diameter_mm=65,
                path=RoutePath.from_waypoints(
                    [(1, 1, 2.5), (5, 1, 2.5)], grid_size=0.3
                ),
                floor="F1",
            ),
            MEPRoute(
                system="hvac",
                route_type="branch",
                diameter_mm=400,
                path=RoutePath.from_waypoints(
                    [(1, 1, 2.9), (5, 1, 2.9)], grid_size=0.3
                ),
                floor="F1",
            ),
        ],
    )


class TestUSDMEPGenerator:
    def test_generate_standalone(self, tmp_path):
        gen = USDMEPGenerator()
        plan = _make_simple_mep_plan()
        out = gen.generate_standalone(plan, tmp_path / "mep.usda")
        assert out.exists()

        # Verify stage can be opened
        stage = Usd.Stage.Open(str(out))
        assert stage is not None

        # MEP root exists
        mep_prim = stage.GetPrimAtPath("/MEP")
        assert mep_prim.IsValid()

    def test_contains_system_prims(self, tmp_path):
        gen = USDMEPGenerator()
        plan = _make_simple_mep_plan()
        out = gen.generate_standalone(plan, tmp_path / "mep.usda")
        stage = Usd.Stage.Open(str(out))

        plumbing = stage.GetPrimAtPath("/MEP/plumbing")
        assert plumbing.IsValid()

        hvac = stage.GetPrimAtPath("/MEP/hvac")
        assert hvac.IsValid()

    def test_has_materials(self, tmp_path):
        gen = USDMEPGenerator()
        plan = _make_simple_mep_plan()
        out = gen.generate_standalone(plan, tmp_path / "mep.usda")
        stage = Usd.Stage.Open(str(out))

        mat = stage.GetPrimAtPath("/MEP/Materials/MEP_plumbing")
        assert mat.IsValid()

    def test_empty_plan(self, tmp_path):
        gen = USDMEPGenerator()
        plan = MEPPlan()
        out = gen.generate_standalone(plan, tmp_path / "empty.usda")
        assert out.exists()
        stage = Usd.Stage.Open(str(out))
        assert stage is not None

    def test_up_axis_is_z(self, tmp_path):
        gen = USDMEPGenerator()
        plan = _make_simple_mep_plan()
        out = gen.generate_standalone(plan, tmp_path / "mep.usda")
        stage = Usd.Stage.Open(str(out))
        assert UsdGeom.GetStageUpAxis(stage) == UsdGeom.Tokens.z
