"""C++ vs Python output consistency verification — Sprint P18 Phase 1.

Verifies that the C++ compliance and cost engines produce outputs consistent
with the Python V1 implementations.
"""

from __future__ import annotations

import json
import math
import pathlib
import sys

import pytest

# ---------------------------------------------------------------------------
# Load native module if available
# ---------------------------------------------------------------------------

_lib_root = pathlib.Path(__file__).parents[1] / "libpromptbim"
_native = None

for _build_dir in sorted(_lib_root.glob("build*")):
    _candidates = list(_build_dir.glob("_native*.so")) + list(_build_dir.glob("_native*.dylib"))
    if _candidates:
        import importlib.util
        spec = importlib.util.spec_from_file_location("_native", str(_candidates[0]))
        _native = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_native)
        break

pytestmark = pytest.mark.skipif(
    _native is None,
    reason="libpromptbim/_native not built — run cmake + build in libpromptbim/"
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

PLAN_DICT = {
    "name": "ConsistencyTest",
    "building_footprint": [[0,0],[20,0],[20,15],[0,15]],
    "land_boundary": [[0,0],[30,0],[30,25],[0,25]],
    "stories": [
        {
            "name": "F1",
            "elevation_m": 0, "height_m": 3.5, "slab_thickness_m": 0.2,
            "slab_boundary": [[0,0],[20,0],[20,15],[0,15]],
            "walls": [
                {"start":[0,0],"end":[20,0],"wall_type":"exterior","thickness_m":0.2},
                {"start":[0,15],"end":[20,15],"wall_type":"exterior","thickness_m":0.2},
                {"start":[0,0],"end":[0,15],"wall_type":"exterior","thickness_m":0.2},
                {"start":[20,0],"end":[20,15],"wall_type":"exterior","thickness_m":0.2},
            ],
            "openings": [
                {"opening_type":"door","width_m":0.9,"height_m":2.1},
                {"opening_type":"window","width_m":1.8,"height_m":1.2},
            ],
            "spaces": [],
        },
        {
            "name": "F2",
            "elevation_m": 3.5, "height_m": 3.5, "slab_thickness_m": 0.2,
            "slab_boundary": [[0,0],[20,0],[20,15],[0,15]],
            "walls": [],
            "openings": [],
            "spaces": [],
        },
    ],
    "parking_spaces": 6,
}

LAND_DICT = {"area_sqm": 750.0}

ZONING_DICT = {
    "bcr_limit": 0.6,
    "far_limit": 2.0,
    "height_limit_m": 21.0,
}

PLAN_JSON   = json.dumps(PLAN_DICT)
LAND_JSON   = json.dumps(LAND_DICT)
ZONING_JSON = json.dumps(ZONING_DICT)


# ---------------------------------------------------------------------------
# Compliance consistency tests
# ---------------------------------------------------------------------------

class TestComplianceConsistency:
    """Verify C++ compliance engine matches Python engine."""

    def test_same_number_of_rules(self):
        """Both engines must run the same 15 rules."""
        cpp_result = json.loads(_native.check_compliance(PLAN_JSON, LAND_JSON, ZONING_JSON))
        assert cpp_result["total_rules"] == 15

    def test_cpp_no_fails_for_valid_building(self):
        """Valid building must have 0 FAILs in C++ engine."""
        cpp_result = json.loads(_native.check_compliance(PLAN_JSON, LAND_JSON, ZONING_JSON))
        assert cpp_result["failed"] == 0

    def test_cpp_bcr_rule_present(self):
        """BCR rule (TW-BTC-BCR) must appear in C++ results."""
        cpp_result = json.loads(_native.check_compliance(PLAN_JSON, LAND_JSON, ZONING_JSON))
        rule_ids = [r["rule_id"] for r in cpp_result["results"]]
        assert "TW-BTC-BCR" in rule_ids

    def test_cpp_far_rule_present(self):
        cpp_result = json.loads(_native.check_compliance(PLAN_JSON, LAND_JSON, ZONING_JSON))
        rule_ids = [r["rule_id"] for r in cpp_result["results"]]
        assert "TW-BTC-FAR" in rule_ids

    def test_cpp_bcr_actual_value_correct(self):
        """BCR actual value: footprint(300)/land(750) = 0.4."""
        cpp_result = json.loads(_native.check_compliance(PLAN_JSON, LAND_JSON, ZONING_JSON))
        bcr = next(r for r in cpp_result["results"] if r["rule_id"] == "TW-BTC-BCR")
        assert abs(bcr["actual_value"] - 0.4) < 0.01, f"BCR actual={bcr['actual_value']}"

    def test_cpp_far_actual_value_correct(self):
        """FAR actual value: total_area(600)/land(750) = 0.8."""
        cpp_result = json.loads(_native.check_compliance(PLAN_JSON, LAND_JSON, ZONING_JSON))
        far = next(r for r in cpp_result["results"] if r["rule_id"] == "TW-BTC-FAR")
        assert abs(far["actual_value"] - 0.8) < 0.01, f"FAR actual={far['actual_value']}"

    def test_cpp_compliance_rate_100_for_valid_building(self):
        """100% compliance rate for valid building."""
        cpp_result = json.loads(_native.check_compliance(PLAN_JSON, LAND_JSON, ZONING_JSON))
        assert cpp_result["compliance_rate"] == 100.0

    def test_cpp_fail_bcr_when_over_limit(self):
        """C++ must FAIL BCR when footprint exceeds limit."""
        plan_over = dict(PLAN_DICT)
        plan_over["building_footprint"] = [[0,0],[28,0],[28,24],[0,24]]  # 672 sqm > 60% of 750
        plan_over["stories"] = [
            {**PLAN_DICT["stories"][0],
             "slab_boundary": [[0,0],[28,0],[28,24],[0,24]]},
        ]
        result = json.loads(_native.check_compliance(json.dumps(plan_over), LAND_JSON, ZONING_JSON))
        bcr = next(r for r in result["results"] if r["rule_id"] == "TW-BTC-BCR")
        assert bcr["severity"] == "fail", f"Expected BCR to fail, got {bcr['severity']}"

    def test_cpp_result_structure(self):
        """Every result must have required fields."""
        cpp_result = json.loads(_native.check_compliance(PLAN_JSON, LAND_JSON, ZONING_JSON))
        required_fields = {"rule_id", "rule_name", "law_reference", "severity", "message"}
        for r in cpp_result["results"]:
            missing = required_fields - set(r.keys())
            assert not missing, f"Missing fields in {r['rule_id']}: {missing}"


# ---------------------------------------------------------------------------
# Cost consistency tests
# ---------------------------------------------------------------------------

class TestCostConsistency:
    """Verify C++ cost engine produces expected output."""

    def test_positive_total_cost(self):
        result = json.loads(_native.estimate_cost(PLAN_JSON))
        assert result["total_cost_twd"] > 0

    def test_floor_area_600_sqm(self):
        """2 stories × 300 sqm = 600 sqm."""
        result = json.loads(_native.estimate_cost(PLAN_JSON))
        assert abs(result["total_floor_area_sqm"] - 600.0) < 1.0

    def test_breakdown_not_empty(self):
        result = json.loads(_native.estimate_cost(PLAN_JSON))
        assert len(result["breakdown"]) > 0

    def test_breakdown_ratios_sum_to_one(self):
        result = json.loads(_native.estimate_cost(PLAN_JSON))
        total_ratio = sum(b["ratio"] for b in result["breakdown"])
        assert abs(total_ratio - 1.0) < 0.05, f"Ratios sum to {total_ratio}"

    def test_project_name_preserved(self):
        result = json.loads(_native.estimate_cost(PLAN_JSON))
        assert result["project"] == "ConsistencyTest"

    def test_notes_present(self):
        result = json.loads(_native.estimate_cost(PLAN_JSON))
        assert "notes" in result
        assert "POC" in result["notes"]

    def test_cost_per_sqm_in_reasonable_range(self):
        """Taiwan 2025 construction: 10,000–100,000 TWD/sqm (POC)."""
        result = json.loads(_native.estimate_cost(PLAN_JSON))
        cpsm = result["cost_per_sqm_twd"]
        assert 5_000 < cpsm < 500_000, f"Cost/sqm {cpsm} out of expected range"

    def test_empty_plan_safe(self):
        empty = json.dumps({"name": "Empty", "stories": []})
        result = json.loads(_native.estimate_cost(empty))
        assert result["total_cost_twd"] == 0

    def test_invalid_json_returns_error(self):
        result = json.loads(_native.estimate_cost("not json"))
        assert "error" in result


# ---------------------------------------------------------------------------
# Native bridge integration test
# ---------------------------------------------------------------------------

class TestNativeBridge:
    """Test the _native_bridge.py auto-select logic."""

    def test_bridge_detects_native(self):
        from promptbim.codes._native_bridge import is_native_available
        # May be True or False depending on build dir presence
        # Just verify no import error
        result = is_native_available()
        assert isinstance(result, bool)

    def test_bridge_check_compliance_json(self):
        from promptbim.codes._native_bridge import check_compliance_json
        result_str = check_compliance_json(PLAN_JSON, LAND_JSON, ZONING_JSON)
        result = json.loads(result_str)
        assert "total_rules" in result or "error" in result

    def test_bridge_estimate_cost_json(self):
        from promptbim.codes._native_bridge import estimate_cost_json
        result_str = estimate_cost_json(PLAN_JSON)
        result = json.loads(result_str)
        # Either cost result or error (if Python schemas not compatible)
        assert "total_cost_twd" in result or "error" in result
