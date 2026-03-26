"""Native C++ engine bridge for V1 backward compatibility.

Automatically selects the best available engine (C++ native or Python fallback):
  1. C++ native (_native pybind11 module) — fastest
  2. Python fallback — always available

Supported engines:
  - Compliance Engine (check_compliance_json)
  - Cost Engine (estimate_cost_json)
  - MEP Engine (plan_mep_json) — v2.6.0+
  - Simulation Engine (generate_schedule_json) — v2.6.0+
  - IFC Generator (generate_ifc) — v2.7.0+
  - USD Generator (generate_usd) — v2.7.0+
  - USDZ Packer (package_usdz) — v2.7.0+
  - GIS Engine (parse_land_json) — v2.8.0+

Usage (internal):
    from promptbim.codes._native_bridge import (
        check_compliance_json, estimate_cost_json,
        plan_mep_json, generate_schedule_json,
    )

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


# ---------------------------------------------------------------------------
# MEP Engine (v2.6.0+)
# ---------------------------------------------------------------------------

def plan_mep_json(plan_json: str, config_json: str = "{}") -> str:
    """Generate MEP routes. Returns JSON string.

    Automatically uses C++ native engine when available; falls back to Python.
    """
    if _USING_NATIVE and _NATIVE_MODULE is not None:
        return _NATIVE_MODULE.plan_mep(plan_json, config_json)

    return _python_mep_fallback(plan_json, config_json)


def _python_mep_fallback(plan_json: str, config_json: str = "{}") -> str:
    """Python MEP engine — fallback when C++ is unavailable."""
    try:
        from promptbim.bim.mep.planner import MEPPlanner
        from promptbim.schemas.plan import BuildingPlan

        plan    = BuildingPlan.model_validate_json(plan_json)
        planner = MEPPlanner()
        result  = planner.plan(plan)
        return json.dumps(result.to_dict())
    except Exception as exc:
        return json.dumps({"error": str(exc)})


# ---------------------------------------------------------------------------
# Simulation Engine (v2.6.0+)
# ---------------------------------------------------------------------------

def generate_schedule_json(plan_json: str, total_days: int = 360) -> str:
    """Generate construction schedule. Returns JSON string.

    Automatically uses C++ native engine when available; falls back to Python.
    """
    if _USING_NATIVE and _NATIVE_MODULE is not None:
        return _NATIVE_MODULE.generate_schedule(plan_json, total_days)

    return _python_schedule_fallback(plan_json, total_days)


def _python_schedule_fallback(plan_json: str, total_days: int = 360) -> str:
    """Python simulation engine — fallback when C++ is unavailable."""
    try:
        from promptbim.bim.simulation.scheduler import generate_schedule
        from promptbim.schemas.plan import BuildingPlan

        plan   = BuildingPlan.model_validate_json(plan_json)
        labels = [c.label for c in (plan.components or [])]
        num_st = len(plan.stories) if plan.stories else 1
        sched  = generate_schedule(labels, total_days, num_st)
        return json.dumps(sched.to_dict())
    except Exception as exc:
        return json.dumps({"error": str(exc)})


# ---------------------------------------------------------------------------
# IFC Generator (v2.7.0+)
# ---------------------------------------------------------------------------

def generate_ifc(plan_json: str, output_path: str) -> int:
    """Generate IFC file. Returns 0 on success, -1 on error.

    Automatically uses C++ native engine when available; falls back to Python.
    """
    if _USING_NATIVE and _NATIVE_MODULE is not None:
        return _NATIVE_MODULE.generate_ifc(plan_json, output_path)

    return _python_ifc_fallback(plan_json, output_path)


def _python_ifc_fallback(plan_json: str, output_path: str) -> int:
    """Python IFC generator — fallback when C++ is unavailable."""
    try:
        from promptbim.bim.ifc_generator import IFCGenerator
        from promptbim.schemas.plan import BuildingPlan

        plan = BuildingPlan.model_validate_json(plan_json)
        gen  = IFCGenerator()
        gen.generate(plan, output_path)
        return 0
    except Exception as exc:
        logger.error("IFC generation failed: %s", exc)
        return -1


# ---------------------------------------------------------------------------
# USD Generator (v2.7.0+)
# ---------------------------------------------------------------------------

def generate_usd(plan_json: str, output_path: str) -> int:
    """Generate USD file. Returns 0 on success, -1 on error.

    Automatically uses C++ native engine when available; falls back to Python.
    """
    if _USING_NATIVE and _NATIVE_MODULE is not None:
        return _NATIVE_MODULE.generate_usd(plan_json, output_path)

    return _python_usd_fallback(plan_json, output_path)


def _python_usd_fallback(plan_json: str, output_path: str) -> int:
    """Python USD generator — fallback when C++ is unavailable."""
    try:
        from promptbim.bim.usd_generator import USDGenerator
        from promptbim.schemas.plan import BuildingPlan

        plan = BuildingPlan.model_validate_json(plan_json)
        gen  = USDGenerator()
        gen.generate(plan, output_path)
        return 0
    except Exception as exc:
        logger.error("USD generation failed: %s", exc)
        return -1


# ---------------------------------------------------------------------------
# USDZ Packer (v2.7.0+)
# ---------------------------------------------------------------------------

def package_usdz(usd_path: str, output_path: str) -> int:
    """Package USDA into USDZ. Returns 0 on success, -1 on error.

    Automatically uses C++ native engine when available; falls back to Python.
    """
    if _USING_NATIVE and _NATIVE_MODULE is not None:
        return _NATIVE_MODULE.package_usdz(usd_path, output_path)

    return _python_usdz_fallback(usd_path, output_path)


def _python_usdz_fallback(usd_path: str, output_path: str) -> int:
    """Python USDZ packer — fallback (simple zip archive)."""
    try:
        import zipfile

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_STORED) as zf:
            zf.write(usd_path, arcname="model.usda")
        return 0
    except Exception as exc:
        logger.error("USDZ packaging failed: %s", exc)
        return -1


# ---------------------------------------------------------------------------
# GIS Engine (v2.8.0+)
# ---------------------------------------------------------------------------

def parse_land_json(source: str, is_file: bool = True) -> str:
    """Parse land data from GeoJSON/Shapefile/DXF. Returns JSON string.

    Args:
        source: File path (if is_file=True) or GeoJSON string (if is_file=False)
        is_file: Whether source is a file path or a raw GeoJSON string

    Automatically uses C++ native engine when available; falls back to Python.
    """
    if _USING_NATIVE and _NATIVE_MODULE is not None:
        if is_file:
            return _NATIVE_MODULE.parse_land_file(source)
        return _NATIVE_MODULE.parse_land_geojson(source)

    return _python_gis_fallback(source, is_file)


def _python_gis_fallback(source: str, is_file: bool = True) -> str:
    """Python GIS engine — fallback when C++ is unavailable."""
    try:
        if not is_file:
            # Parse GeoJSON string
            import json as _json

            geojson = _json.loads(source)
            # Extract first polygon from GeoJSON
            geom = None
            props = {}
            gtype = geojson.get("type", "")
            if gtype == "FeatureCollection":
                feat = geojson.get("features", [{}])[0]
                geom = feat.get("geometry", {})
                props = feat.get("properties", {})
            elif gtype == "Feature":
                geom = geojson.get("geometry", {})
                props = geojson.get("properties", {})
            else:
                geom = geojson

            coords = []
            if geom and geom.get("type") == "Polygon":
                ring = geom["coordinates"][0]
                coords = [[c[0], c[1]] for c in ring]
                # Remove closing point
                if len(coords) > 1 and coords[0] == coords[-1]:
                    coords = coords[:-1]

            # Compute area (Shoelace)
            area = 0.0
            n = len(coords)
            for i in range(n):
                j = (i + 1) % n
                area += coords[i][0] * coords[j][1] - coords[j][0] * coords[i][1]
            area = abs(area) / 2.0

            result = {
                "name": props.get("name", ""),
                "boundary": coords,
                "area_sqm": area,
                "crs": "EPSG:4326",
                "properties": props,
            }
            return _json.dumps(result)

        # File-based parsing — use geopandas if available
        from promptbim.gis.parser import LandParser

        parser = LandParser()
        land = parser.parse(source)
        return json.dumps(land.model_dump())
    except Exception as exc:
        return json.dumps({"error": str(exc)})
