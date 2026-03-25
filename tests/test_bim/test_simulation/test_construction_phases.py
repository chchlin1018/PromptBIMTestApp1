"""Tests for bim/simulation/construction_phases.py."""

import pytest

from promptbim.bim.simulation.construction_phases import (
    STANDARD_PHASES,
    ConstructionPhase,
    classify_component,
    get_phase_by_id,
)


class TestStandardPhases:
    def test_has_16_phases(self):
        assert len(STANDARD_PHASES) == 16

    def test_phase_ids_unique(self):
        ids = [p.phase_id for p in STANDARD_PHASES]
        assert len(ids) == len(set(ids))

    def test_phase_ids_sequential(self):
        for i, p in enumerate(STANDARD_PHASES, start=1):
            assert p.phase_id == f"P{i:02d}"

    def test_duration_ratios_sum_close_to_one(self):
        total = sum(p.duration_ratio for p in STANDARD_PHASES)
        assert abs(total - 1.0) < 0.01

    def test_all_phases_have_ifc_classes(self):
        for p in STANDARD_PHASES:
            assert len(p.ifc_classes) > 0

    def test_phase_has_color(self):
        for p in STANDARD_PHASES:
            assert len(p.color) == 3
            assert all(0.0 <= c <= 1.0 for c in p.color)


class TestGetPhaseById:
    def test_existing_phase(self):
        p = get_phase_by_id("P01")
        assert p is not None
        assert p.name == "Site Preparation"

    def test_last_phase(self):
        p = get_phase_by_id("P16")
        assert p is not None
        assert "MEP" in p.name

    def test_nonexistent_phase(self):
        assert get_phase_by_id("P99") is None


class TestClassifyComponent:
    @pytest.mark.parametrize("label,expected", [
        ("roof", "P08"),
        ("1F_roof_main", "P08"),
        ("ground_slab", "P02"),
        ("2F_slab", "P06"),
        ("1F_wall_0", "P09"),
        ("1F_wall_partition_3", "P12"),
        ("column_1", "P04"),
        ("beam_2", "P05"),
        ("door_main", "P10"),
        ("window_1", "P10"),
        ("duct_hvac", "P11"),
        ("pipe_water", "P11"),
        ("elevator_1", "P13"),
        ("ceiling_main", "P14"),
        ("furniture_desk", "P15"),
        ("light_fixture_1", "P16"),
    ])
    def test_classify(self, label, expected):
        assert classify_component(label) == expected

    def test_unknown_label(self):
        assert classify_component("unknown_xyz") is None
