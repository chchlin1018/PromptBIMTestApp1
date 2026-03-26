"""Native C++ engine bridge for V1 backward compatibility.

Automatically selects the best available compliance / cost engine:
  1. C++ native (_native pybind11 module) — fastest
  2. Python fallback — always available

Usage (internal):
    from promptbim.codes._native_bridge import check_compliance_json, estimate_cost_json

These functions accept/return JSON strings to match the C++ ABI.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger("codes.native_bridge")

# Try to import the native C++ module built by libpromptbim/build_py*/
_NATIVE_MODULE = None
_USING_NATIVE = False

try:
    import importlib.util
    import pathlib
    import sys

    # Search for the compiled _native.cpython-*.so in known build locations
    _lib_root = pathlib.Path(__file__).parents[4] / "libpromptbim"
    _candidates = sorted(_lib_root.glob("build*/_native*.so")) + sorted(
        _lib_root.glob("build*/_native*.dylib")
    )
    if _candidates:
        _so_path = str(_candidates[0])
        spec = importlib.util.spec_from_file_location("_native", _so_path)
        _NATIVE_MODULE = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_NATIVE_MODULE)
        _USING_NATIVE = True
        logger.info("Using native C++ engine: %s (v%s)", _so_path, _NATIVE_MODULE.__version__)
    else:
        logger.debug("No _native.so found in libpromptbim/build* — using Python engine")
except Exception as exc:
    logger.debug("Failed to load native engine: %s — using Python fallback", exc)


def is_native_available() -> bool:
    """Return True if the C++ native engine is loaded."""
    return _USING_NATIVE


def check_compliance_json(plan_json: str, land_json: str, zoning_json: str) -> str:
    """Run compliance check. Returns JSON string with summary + per-rule results.

    Automatically uses C++ native engine when available; falls back to Python.
    """
    if _USING_NATIVE and _NATIVE_MODULE is not None:
        return _NATIVE_MODULE.check_compliance(plan_json, land_json, zoning_json)

    # Python fallback — call the existing Python compliance engine
    return _python_compliance_fallback(plan_json, land_json, zoning_json)


def estimate_cost_json(plan_json: str) -> str:
    """Estimate construction cost. Returns JSON string with CostEstimate.

    Automatically uses C++ native engine when available; falls back to Python.
    """
    if _USING_NATIVE and _NATIVE_MODULE is not None:
        return _NATIVE_MODULE.estimate_cost(plan_json)

    # Python fallback
    return _python_cost_fallback(plan_json)


# ---------------------------------------------------------------------------
# Python fallbacks
# ---------------------------------------------------------------------------

def _python_compliance_fallback(plan_json: str, land_json: str, zoning_json: str) -> str:
    """Python compliance engine — fallback when C++ is unavailable."""
    try:
        from promptbim.codes.registry import run_all_checks, get_compliance_summary
        from promptbim.schemas.plan import BuildingPlan
        from promptbim.schemas.land import LandParcel
        from promptbim.schemas.zoning import ZoningInfo

        plan   = BuildingPlan.model_validate_json(plan_json)
        land   = LandParcel.model_validate_json(land_json)
        zoning = ZoningInfo.model_validate_json(zoning_json)

        results = run_all_checks(plan, land, zoning)
        summary = get_compliance_summary(results)

        # Add per-rule results
        summary["results"] = [
            {
                "rule_id":      r.rule_id,
                "rule_name":    r.rule_name_zh,
                "law_reference":r.law_reference,
                "severity":     r.severity.value,
                "message":      r.message_zh,
                "actual_value": r.actual_value,
                "limit_value":  r.limit_value,
                "suggestion":   r.suggestion,
            }
            for r in results
        ]
        return json.dumps(summary)
    except Exception as exc:
        return json.dumps({"error": str(exc)})


def _python_cost_fallback(plan_json: str) -> str:
    """Python cost engine — fallback when C++ is unavailable."""
    try:
        from promptbim.bim.cost.estimator import CostEstimator
        from promptbim.schemas.plan import BuildingPlan

        plan      = BuildingPlan.model_validate_json(plan_json)
        estimator = CostEstimator()
        estimate  = estimator.estimate(plan)
        return json.dumps(estimate.to_dict())
    except Exception as exc:
        return json.dumps({"error": str(exc)})
