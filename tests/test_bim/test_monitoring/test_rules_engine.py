"""Tests for bim/monitoring/rules_engine.py — placement density rules."""

import pytest

from promptbim.bim.monitoring.rules_engine import (
    PLACEMENT_RULES,
    PlacementRule,
    RulesEngine,
)
from promptbim.bim.monitoring.monitor_types import MONITOR_TYPES


class TestPlacementRules:
    def test_all_types_have_rules(self):
        for type_id in MONITOR_TYPES:
            assert type_id in PLACEMENT_RULES, f"Missing rule for {type_id}"

    def test_rule_modes_valid(self):
        valid_modes = {"per_sqm", "per_space", "per_floor", "per_building"}
        for rule in PLACEMENT_RULES.values():
            assert rule.mode in valid_modes

    def test_density_positive(self):
        for rule in PLACEMENT_RULES.values():
            assert rule.density > 0


class TestRulesEngine:
    def setup_method(self):
        self.engine = RulesEngine()

    def test_per_sqm_count(self):
        # temp_sensor: density=0.02, min=1, max=4
        count = self.engine.compute_count("temp_sensor", area_sqm=100)
        assert 1 <= count <= 4

    def test_per_sqm_small_area(self):
        count = self.engine.compute_count("temp_sensor", area_sqm=5)
        assert count >= 1  # min_per_space=1

    def test_per_space_count(self):
        count = self.engine.compute_count("heat_detector", area_sqm=50)
        assert count >= 1

    def test_per_floor_count(self):
        count = self.engine.compute_count("power_meter", area_sqm=200)
        assert count >= 1

    def test_per_building_count(self):
        count = self.engine.compute_count("seismic_sensor", area_sqm=500)
        assert count >= 1

    def test_min_area_filter(self):
        # pm25_sensor: min_area_sqm=30
        count = self.engine.compute_count("pm25_sensor", area_sqm=10)
        assert count == 0

    def test_min_area_pass(self):
        count = self.engine.compute_count("pm25_sensor", area_sqm=50)
        assert count >= 1

    def test_unknown_type(self):
        count = self.engine.compute_count("nonexistent_type", area_sqm=100)
        assert count == 1  # default

    def test_max_per_space_respected(self):
        # smoke_detector: density=0.04, max=10
        count = self.engine.compute_count("smoke_detector", area_sqm=10000)
        assert count <= 10
