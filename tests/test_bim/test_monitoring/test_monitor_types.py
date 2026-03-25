"""Tests for bim/monitoring/monitor_types.py — 48 sensor/actuator definitions."""

import pytest

from promptbim.bim.monitoring.monitor_types import (
    MONITOR_CATEGORIES,
    MONITOR_TYPES,
    MonitorCategory,
    MonitorType,
    get_types_for_space,
)


class TestMonitorTypes:
    def test_exactly_48_types(self):
        assert len(MONITOR_TYPES) == 48

    def test_all_types_have_required_fields(self):
        for mt in MONITOR_TYPES.values():
            assert mt.id
            assert mt.name
            assert isinstance(mt.category, MonitorCategory)
            assert mt.ifc_class in ("IfcSensor", "IfcActuator")
            assert mt.predefined_type
            assert mt.unit_cost_twd > 0

    def test_all_categories_represented(self):
        cats = {mt.category for mt in MONITOR_TYPES.values()}
        for cat in MonitorCategory:
            assert cat in cats, f"Category {cat} has no monitor types"

    def test_category_registry(self):
        assert len(MONITOR_CATEGORIES) == len(MonitorCategory)
        total = sum(len(v) for v in MONITOR_CATEGORIES.values())
        assert total == 48

    def test_get_types_for_office(self):
        types = get_types_for_space("office")
        assert len(types) > 5
        type_ids = {t.id for t in types}
        assert "temp_sensor" in type_ids
        assert "co2_sensor" in type_ids

    def test_get_types_for_parking(self):
        types = get_types_for_space("parking")
        type_ids = {t.id for t in types}
        assert "parking_sensor" in type_ids
        assert "cctv_camera" in type_ids

    def test_get_types_for_unknown_space(self):
        types = get_types_for_space("nonexistent_space")
        assert types == []

    def test_unique_ids(self):
        ids = [mt.id for mt in MONITOR_TYPES.values()]
        assert len(ids) == len(set(ids))

    def test_color_rgb_range(self):
        for mt in MONITOR_TYPES.values():
            for c in mt.color_rgb:
                assert 0.0 <= c <= 1.0


class TestMonitorCategory:
    def test_all_values_are_strings(self):
        for cat in MonitorCategory:
            assert isinstance(cat.value, str)

    def test_expected_categories(self):
        expected = {
            "environmental", "safety", "security", "energy",
            "structural", "mep", "smart", "accessibility",
        }
        actual = {cat.value for cat in MonitorCategory}
        assert actual == expected
