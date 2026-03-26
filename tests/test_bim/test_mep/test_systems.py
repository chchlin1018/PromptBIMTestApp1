"""Tests for bim/mep/systems.py — MEP system templates."""

from promptbim.bim.mep.systems import (
    CEILING_LAYER_Z_OFFSET,
    SYSTEM_COLORS,
    SYSTEM_LABELS,
    get_template,
)


class TestMEPSystems:
    def test_office_template_exists(self):
        t = get_template("office")
        assert t.hvac.type == "central_air"
        assert t.plumbing.cold_water_main_mm == 65
        assert t.electrical.panel_per_floor == 1
        assert t.fire_protection.heads_per_sqm == 0.08

    def test_residential_template(self):
        t = get_template("residential")
        assert t.hvac.type == "split_unit"
        assert t.plumbing.cold_water_main_mm == 50

    def test_unknown_type_defaults_to_office(self):
        t = get_template("hospital")
        assert t.hvac.type == "central_air"

    def test_system_colors(self):
        assert len(SYSTEM_COLORS) == 4
        for color in SYSTEM_COLORS.values():
            assert len(color) == 3
            assert all(0 <= c <= 1 for c in color)

    def test_system_labels(self):
        assert "hvac" in SYSTEM_LABELS
        assert "plumbing" in SYSTEM_LABELS
        assert "electrical" in SYSTEM_LABELS
        assert "fire_protection" in SYSTEM_LABELS

    def test_ceiling_layer_offsets(self):
        assert len(CEILING_LAYER_Z_OFFSET) == 4
        # HVAC should be highest (closest to ceiling, least negative)
        assert CEILING_LAYER_Z_OFFSET["hvac"] > CEILING_LAYER_Z_OFFSET["plumbing"]
