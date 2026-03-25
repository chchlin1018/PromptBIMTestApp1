"""Tests for bim/mep/ifc_mep.py — MEP IFC generation."""

import tempfile
from pathlib import Path

import pytest
import ifcopenshell

from promptbim.bim.mep.ifc_mep import IFCMEPGenerator
from promptbim.bim.mep.pathfinder import RoutePath
from promptbim.bim.mep.planner import MEPEquipment, MEPPlan, MEPRoute, MEPTerminal


def _make_simple_mep_plan() -> MEPPlan:
    return MEPPlan(
        routes=[
            MEPRoute(
                system="plumbing",
                route_type="branch",
                diameter_mm=65,
                path=RoutePath.from_waypoints(
                    [(1, 1, 2.5), (5, 1, 2.5), (5, 5, 2.5)], grid_size=0.3
                ),
                floor="1F",
            ),
            MEPRoute(
                system="hvac",
                route_type="branch",
                diameter_mm=400,
                path=RoutePath.from_waypoints(
                    [(1, 1, 2.9), (5, 1, 2.9)], grid_size=0.3
                ),
                floor="1F",
            ),
            MEPRoute(
                system="electrical",
                route_type="branch",
                diameter_mm=100,
                path=RoutePath.from_waypoints(
                    [(1, 1, 2.6), (3, 1, 2.6)], grid_size=0.3
                ),
                floor="1F",
            ),
            MEPRoute(
                system="fire_protection",
                route_type="branch",
                diameter_mm=25,
                path=RoutePath.from_waypoints(
                    [(1, 1, 2.7), (5, 1, 2.7), (5, 3, 2.7)], grid_size=0.3
                ),
                floor="1F",
            ),
        ],
    )


class TestIFCMEPGenerator:
    def test_generate_standalone(self, tmp_path):
        gen = IFCMEPGenerator()
        plan = _make_simple_mep_plan()
        out = gen.generate_standalone(plan, tmp_path / "mep.ifc", project_name="TestMEP")
        assert out.exists()

        # Verify IFC can be reopened
        model = ifcopenshell.open(str(out))
        assert model is not None

        # Should contain pipe/duct segments
        pipes = model.by_type("IfcPipeSegment")
        ducts = model.by_type("IfcDuctSegment")
        cables = model.by_type("IfcCableCarrierSegment")
        total = len(pipes) + len(ducts) + len(cables)
        assert total > 0

    def test_has_pipe_segments(self, tmp_path):
        gen = IFCMEPGenerator()
        plan = _make_simple_mep_plan()
        out = gen.generate_standalone(plan, tmp_path / "mep.ifc")
        model = ifcopenshell.open(str(out))
        pipes = model.by_type("IfcPipeSegment")
        assert len(pipes) >= 2  # plumbing + fire_protection

    def test_has_duct_segments(self, tmp_path):
        gen = IFCMEPGenerator()
        plan = _make_simple_mep_plan()
        out = gen.generate_standalone(plan, tmp_path / "mep.ifc")
        model = ifcopenshell.open(str(out))
        ducts = model.by_type("IfcDuctSegment")
        assert len(ducts) >= 1

    def test_has_cable_carrier_segments(self, tmp_path):
        gen = IFCMEPGenerator()
        plan = _make_simple_mep_plan()
        out = gen.generate_standalone(plan, tmp_path / "mep.ifc")
        model = ifcopenshell.open(str(out))
        cables = model.by_type("IfcCableCarrierSegment")
        assert len(cables) >= 1

    def test_empty_plan(self, tmp_path):
        gen = IFCMEPGenerator()
        plan = MEPPlan()
        out = gen.generate_standalone(plan, tmp_path / "empty.ifc")
        assert out.exists()
        model = ifcopenshell.open(str(out))
        assert model is not None
