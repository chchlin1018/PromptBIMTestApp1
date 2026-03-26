"""PromptBIM MCP Server — Claude Desktop integration.

Exposes PromptBIM functionality as MCP tools and resources so that
Claude Desktop can generate buildings, check compliance, estimate costs,
and query project state through the Model Context Protocol.

Usage (standalone):
    python -m promptbim.mcp.server

Usage (Claude Desktop config):
    Add to claude_desktop_config.json:
    {
        "mcpServers": {
            "promptbim": {
                "command": "python",
                "args": ["-m", "promptbim.mcp.server"],
                "env": {"ANTHROPIC_API_KEY": "sk-..."}
            }
        }
    }
"""

from __future__ import annotations

import asyncio
import json
import tempfile
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from promptbim.bim.geometry import poly_area
from promptbim.debug import get_logger

logger = get_logger("mcp.server")

# Task 20: Default timeout for long-running operations
MCP_TIMEOUT_SECONDS = 120

mcp = FastMCP(
    "PromptBIM",
    instructions="AI-Powered BIM Building Generator — generate buildings from natural language on real land parcels",
)

# --------------------------------------------------------------------------
# Shared state (per-server-session)
# --------------------------------------------------------------------------
_state: dict = {
    "land": None,  # LandParcel dict
    "zoning": None,  # ZoningRules dict
    "plan": None,  # BuildingPlan dict
    "result": None,  # GenerationResult dict
    "output_dir": None,  # Path string
}


def _get_orchestrator():
    """Lazy-create an Orchestrator instance."""
    from promptbim.agents.orchestrator import Orchestrator

    output_dir = _state.get("output_dir") or str(Path(tempfile.gettempdir()) / "promptbim_mcp")
    return Orchestrator(output_dir=output_dir)


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------


@mcp.tool()
def import_land(
    boundary: list[list[float]],
    name: str = "MCP Parcel",
    area_sqm: float | None = None,
) -> str:
    """Import a land parcel by specifying boundary coordinates.

    Args:
        boundary: List of [x, y] coordinate pairs in metres (local coords).
        name: Optional name for the parcel.
        area_sqm: Optional area override. Computed from boundary if omitted.
    """
    from promptbim.schemas.land import LandParcel

    logger.debug(
        "import_land called: name=%s, vertices=%d, area_sqm=%s", name, len(boundary), area_sqm
    )
    t0 = time.monotonic()

    coords = [(pt[0], pt[1]) for pt in boundary]

    if area_sqm is None:
        area_sqm = poly_area(coords)

    parcel = LandParcel(
        name=name,
        boundary=coords,
        area_sqm=area_sqm,
        source_type="mcp",
    )
    _state["land"] = parcel.model_dump()
    logger.debug(
        "import_land completed in %.3fs: area=%.1f m²", time.monotonic() - t0, parcel.area_sqm
    )
    return json.dumps(
        {
            "status": "ok",
            "name": parcel.name,
            "area_sqm": parcel.area_sqm,
            "vertices": len(coords),
        }
    )


@mcp.tool()
def set_zoning(
    zone_type: str = "residential",
    far_limit: float = 2.0,
    bcr_limit: float = 0.6,
    height_limit_m: float = 15.0,
    setback_front_m: float = 5.0,
    setback_back_m: float = 3.0,
    setback_left_m: float = 2.0,
    setback_right_m: float = 2.0,
) -> str:
    """Set zoning rules for the current land parcel.

    Args:
        zone_type: Land use type (residential/commercial/industrial).
        far_limit: Floor Area Ratio limit.
        bcr_limit: Building Coverage Ratio limit.
        height_limit_m: Maximum building height in metres.
        setback_front_m: Front setback distance in metres.
        setback_back_m: Back setback distance in metres.
        setback_left_m: Left setback distance in metres.
        setback_right_m: Right setback distance in metres.
    """
    from promptbim.schemas.zoning import ZoningRules

    logger.debug(
        "set_zoning called: type=%s, FAR=%.2f, BCR=%.2f, height=%.1fm",
        zone_type,
        far_limit,
        bcr_limit,
        height_limit_m,
    )
    t0 = time.monotonic()

    zoning = ZoningRules(
        zone_type=zone_type,
        far_limit=far_limit,
        bcr_limit=bcr_limit,
        height_limit_m=height_limit_m,
        setback_front_m=setback_front_m,
        setback_back_m=setback_back_m,
        setback_left_m=setback_left_m,
        setback_right_m=setback_right_m,
    )
    _state["zoning"] = zoning.model_dump()
    logger.debug("set_zoning completed in %.3fs", time.monotonic() - t0)
    return json.dumps({"status": "ok", "zoning": _state["zoning"]})


@mcp.tool()
def generate_building(prompt: str) -> str:
    """Generate a building from a natural language description.

    Requires import_land() to be called first. Uses the AI pipeline:
    Enhancer -> Planner -> Builder -> Checker.

    Args:
        prompt: Natural language building description (e.g., "3-story office with rooftop garden").
    """
    logger.debug("generate_building called: prompt='%s'", prompt[:100])
    if _state["land"] is None:
        logger.warning("generate_building: no land imported")
        return json.dumps({"error": "No land imported. Call import_land() first."})

    t0 = time.monotonic()
    try:
        from promptbim.schemas.land import LandParcel
        from promptbim.schemas.zoning import ZoningRules

        land = LandParcel(**_state["land"])
        zoning = ZoningRules(**_state["zoning"]) if _state["zoning"] else ZoningRules()

        orch = _get_orchestrator()
        result = orch.generate(prompt, land, zoning)

        _state["plan"] = orch.plan.model_dump() if orch.plan else None
        _state["result"] = result.model_dump(mode="json") if result else None

        elapsed = time.monotonic() - t0
        logger.info(
            "generate_building completed in %.2fs: success=%s, name=%s",
            elapsed,
            result.success,
            result.building_name,
        )

        return json.dumps(
            {
                "status": "ok" if result.success else "error",
                "building_name": result.building_name,
                "stories": result.summary.get("stories", 0),
                "bcr": result.summary.get("bcr", 0),
                "far": result.summary.get("far", 0),
                "ifc_path": str(result.ifc_path) if result.ifc_path else None,
                "usd_path": str(result.usd_path) if result.usd_path else None,
                "warnings": result.warnings[:5],
                "errors": result.errors,
            }
        )
    except Exception as e:
        elapsed = time.monotonic() - t0
        logger.error("generate_building failed after %.2fs: %s", elapsed, e)
        return json.dumps({"error": f"Generation failed: {str(e)[:200]}"})


@mcp.tool()
def modify_building(command: str) -> str:
    """Modify the current building with a natural language command.

    Args:
        command: Modification instruction (e.g., "change to 5 stories", "add swimming pool").
    """
    logger.debug("modify_building called: command='%s'", command[:100])
    if _state["plan"] is None:
        logger.warning("modify_building: no building generated")
        return json.dumps({"error": "No building generated. Call generate_building() first."})

    t0 = time.monotonic()
    from promptbim.schemas.zoning import ZoningRules

    zoning = ZoningRules(**_state["zoning"]) if _state["zoning"] else None

    orch = _get_orchestrator()
    # Restore plan state
    from promptbim.schemas.plan import BuildingPlan

    orch.plan = BuildingPlan(**_state["plan"])

    new_plan, record = orch.modify(command, zoning)

    if new_plan:
        _state["plan"] = new_plan.model_dump()

    elapsed = time.monotonic() - t0
    logger.info(
        "modify_building completed in %.2fs: success=%s",
        elapsed,
        record.success if record else False,
    )

    return json.dumps(
        {
            "status": "ok" if record and record.success else "failed",
            "modification_type": record.modification_type if record else None,
            "impacts": [str(i) for i in (record.impacts if record else [])],
        }
    )


@mcp.tool()
def check_compliance() -> str:
    """Run Taiwan building code compliance check on the current building."""
    logger.debug("check_compliance called")
    if _state["plan"] is None:
        return json.dumps({"error": "No building generated."})
    if _state["land"] is None:
        return json.dumps({"error": "No land imported."})

    t0 = time.monotonic()
    from promptbim.agents.checker import CheckerAgent
    from promptbim.schemas.land import LandParcel
    from promptbim.schemas.plan import BuildingPlan
    from promptbim.schemas.zoning import ZoningRules

    plan = BuildingPlan(**_state["plan"])
    land = LandParcel(**_state["land"])
    zoning = ZoningRules(**_state["zoning"]) if _state["zoning"] else ZoningRules()

    checker = CheckerAgent()
    result = checker.check(plan, land, zoning)

    logger.info(
        "check_compliance completed in %.2fs: passed=%s, violations=%d",
        time.monotonic() - t0,
        result.passed,
        len(result.violations),
    )

    return json.dumps(
        {
            "passed": result.passed,
            "violations_count": len(result.violations),
            "violations": [
                {"rule": v.rule, "severity": v.severity, "message": v.message}
                for v in result.violations[:10]
            ],
            "suggestions": result.suggestions[:5],
            "report_text": result.report_text[:2000] if result.report_text else "",
        }
    )


@mcp.tool()
def estimate_cost() -> str:
    """Estimate construction cost for the current building (Taiwan market prices)."""
    logger.debug("estimate_cost called")
    if _state["plan"] is None:
        return json.dumps({"error": "No building generated."})

    t0 = time.monotonic()
    from promptbim.bim.cost.estimator import CostEstimator
    from promptbim.schemas.plan import BuildingPlan

    plan = BuildingPlan(**_state["plan"])
    estimator = CostEstimator()
    estimate = estimator.estimate(plan)

    result = estimate.to_dict()
    logger.info(
        "estimate_cost completed in %.2fs: total_twd=%s",
        time.monotonic() - t0,
        result.get("total_twd", 0),
    )
    return json.dumps(
        {
            "total_twd": result.get("total_twd", 0),
            "total_usd_approx": result.get("total_twd", 0) / 32,
            "cost_per_sqm_twd": result.get("cost_per_sqm_twd", 0),
            "categories": result.get("category_breakdown", {}),
        }
    )


@mcp.tool()
def auto_monitor() -> str:
    """Automatically place smart monitoring points on the current building."""
    logger.debug("auto_monitor called")
    if _state["plan"] is None:
        return json.dumps({"error": "No building generated."})

    t0 = time.monotonic()
    from promptbim.bim.monitoring.auto_placement import AutoPlacement
    from promptbim.schemas.plan import BuildingPlan

    plan = BuildingPlan(**_state["plan"])
    placer = AutoPlacement()
    monitor_plan = placer.place(plan)

    logger.info(
        "auto_monitor completed in %.2fs: total_monitors=%d",
        time.monotonic() - t0,
        monitor_plan.total_count,
    )

    return json.dumps(
        {
            "total_monitors": monitor_plan.total_count,
            "total_cost_twd": monitor_plan.total_cost_twd,
            "by_category": {cat: len(items) for cat, items in monitor_plan.by_category().items()},
        }
    )


# --------------------------------------------------------------------------
# Resources
# --------------------------------------------------------------------------


@mcp.resource("building://current")
def get_current_building() -> str:
    """Get the current building state (plan + result summary)."""
    if _state["plan"] is None:
        return json.dumps(
            {"status": "no_building", "message": "No building has been generated yet."}
        )

    plan = _state["plan"]
    result = _state["result"]

    return json.dumps(
        {
            "status": "ok",
            "building_name": plan.get("name", ""),
            "stories": len(plan.get("stories", [])),
            "bcr": plan.get("building_bcr", 0),
            "far": plan.get("building_far", 0),
            "has_ifc": bool(result and result.get("ifc_path")),
            "has_usd": bool(result and result.get("usd_path")),
            "land": _state["land"],
            "zoning": _state["zoning"],
        }
    )


@mcp.resource("building://land")
def get_current_land() -> str:
    """Get the current land parcel data."""
    if _state["land"] is None:
        return json.dumps({"status": "no_land", "message": "No land has been imported yet."})
    return json.dumps({"status": "ok", "land": _state["land"]})


# --------------------------------------------------------------------------
# Task 17: Async generate support
# --------------------------------------------------------------------------


@mcp.tool()
async def agenerate_building(prompt: str) -> str:
    """Generate a building asynchronously from a natural language description.

    Same as generate_building but runs in a background thread with timeout protection.

    Args:
        prompt: Natural language building description.
    """
    logger.debug("agenerate_building called: prompt='%s'", prompt[:100])
    if _state["land"] is None:
        return json.dumps({"error": "No land imported. Call import_land() first."})

    try:
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, lambda: _sync_generate(prompt)
            ),
            timeout=MCP_TIMEOUT_SECONDS,
        )
        return result
    except asyncio.TimeoutError:
        logger.error("agenerate_building timed out after %ds", MCP_TIMEOUT_SECONDS)
        return json.dumps(
            {"error": f"Generation timed out after {MCP_TIMEOUT_SECONDS}s. Try a simpler prompt."}
        )
    except Exception as e:
        logger.error("agenerate_building failed: %s", e)
        return json.dumps({"error": f"Generation failed: {str(e)[:200]}"})


def _sync_generate(prompt: str) -> str:
    """Synchronous building generation helper."""
    from promptbim.schemas.land import LandParcel
    from promptbim.schemas.zoning import ZoningRules

    t0 = time.monotonic()
    land = LandParcel(**_state["land"])
    zoning = ZoningRules(**_state["zoning"]) if _state["zoning"] else ZoningRules()

    orch = _get_orchestrator()
    result = orch.generate(prompt, land, zoning)

    _state["plan"] = orch.plan.model_dump() if orch.plan else None
    _state["result"] = result.model_dump(mode="json") if result else None

    elapsed = time.monotonic() - t0
    logger.info("agenerate_building completed in %.2fs", elapsed)

    return json.dumps(
        {
            "status": "ok" if result.success else "error",
            "building_name": result.building_name,
            "stories": result.summary.get("stories", 0),
            "elapsed_seconds": round(elapsed, 2),
        }
    )


# --------------------------------------------------------------------------
# Task 18: Cache tool
# --------------------------------------------------------------------------


@mcp.tool()
def clear_cache() -> str:
    """Clear the current session state (land, zoning, building plan)."""
    logger.debug("clear_cache called")
    _state["land"] = None
    _state["zoning"] = None
    _state["plan"] = None
    _state["result"] = None
    return json.dumps({"status": "ok", "message": "Session state cleared."})


@mcp.tool()
def get_session_info() -> str:
    """Get current session state summary."""
    return json.dumps(
        {
            "has_land": _state["land"] is not None,
            "has_zoning": _state["zoning"] is not None,
            "has_plan": _state["plan"] is not None,
            "has_result": _state["result"] is not None,
            "output_dir": _state.get("output_dir"),
        }
    )


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def main():
    """Run the MCP server via stdio transport."""
    logger.info("Starting PromptBIM MCP server (stdio transport)")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
