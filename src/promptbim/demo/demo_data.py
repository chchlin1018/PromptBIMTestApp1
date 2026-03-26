"""Built-in demo data for PromptBIM — Taipei Xinyi 3-story residential.

Provides ready-to-display BIM project data so the app doesn't start blank.
"""

from __future__ import annotations

import json
from pathlib import Path

from promptbim.schemas.land import LandParcel
from promptbim.schemas.plan import (
    BuildingPlan,
    OpeningDef,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)
from promptbim.schemas.result import GenerationResult
from promptbim.schemas.zoning import ZoningRules

DEMO_RESOURCES_DIR = Path(__file__).parent.parent.parent.parent / "resources" / "demo"


# ---------------------------------------------------------------------------
# Task 16: Demo Land Data
# ---------------------------------------------------------------------------

def get_demo_land() -> LandParcel:
    """Return a demo land parcel — Taipei Xinyi District (~500 sqm trapezoid)."""
    # Trapezoid roughly 20m x 25m with slight angle
    boundary = [
        (0.0, 0.0),
        (22.0, 0.0),
        (20.0, 24.0),
        (2.0, 25.0),
    ]
    # Shoelace area for this trapezoid
    area = _shoelace(boundary)
    perim = _perimeter(boundary)
    return LandParcel(
        name="台北市信義區住宅用地 (Demo)",
        boundary=boundary,
        area_sqm=area,
        perimeter_m=perim,
        crs="EPSG:3826",
        source_type="manual",
    )


def get_demo_zoning() -> ZoningRules:
    """Return Xinyi District residential zoning rules."""
    return ZoningRules(
        zone_type="residential",
        far_limit=2.4,
        bcr_limit=0.6,
        height_limit_m=21.0,
        setback_front_m=5.0,
        setback_back_m=3.0,
        setback_left_m=2.0,
        setback_right_m=2.0,
        min_parking_per_unit=1.0,
    )


# ---------------------------------------------------------------------------
# Task 17: Demo Building Plan
# ---------------------------------------------------------------------------

def get_demo_plan() -> BuildingPlan:
    """Return a complete 3-story elevator residential building plan."""
    land = get_demo_land()
    zoning = get_demo_zoning()

    # Buildable area after setbacks (approx)
    footprint = [
        (5.0, 5.0),
        (18.0, 5.0),
        (17.0, 21.0),
        (5.0, 22.0),
    ]
    fp_area = _shoelace(footprint)
    land_area = land.area_sqm

    stories = [
        _make_1f(footprint),
        _make_2f(footprint),
        _make_3f(footprint),
    ]

    bcr = fp_area / land_area
    far = (fp_area * 3) / land_area

    return BuildingPlan(
        name="信義區住宅 Demo",
        land_boundary=land.boundary,
        buildable_area=footprint,
        building_footprint=footprint,
        building_bcr=round(bcr, 4),
        building_far=round(far, 4),
        stories=stories,
        roof=RoofPlan(roof_type="flat", slope_degrees=0.0, overhang_m=0.3),
    )


def _make_walls(footprint: list[tuple[float, float]]) -> list[WallDef]:
    """Create exterior walls from footprint."""
    walls = []
    n = len(footprint)
    for i in range(n):
        walls.append(WallDef(
            start=footprint[i],
            end=footprint[(i + 1) % n],
            thickness_m=0.2,
            wall_type="exterior",
        ))
    return walls


def _make_1f(footprint: list[tuple[float, float]]) -> StoryPlan:
    """1F: Lobby + parking + mechanical room."""
    walls = _make_walls(footprint)
    # Add interior partition
    walls.append(WallDef(start=(5.0, 12.0), end=(18.0, 12.0), thickness_m=0.15, wall_type="interior"))

    spaces = [
        SpaceDef(name="大廳", boundary=[(5, 5), (18, 5), (18, 12), (5, 12)],
                 space_type="corridor", area_sqm=91.0),
        SpaceDef(name="停車場", boundary=[(5, 12), (14, 12), (14, 22), (5, 22)],
                 space_type="parking", area_sqm=90.0),
        SpaceDef(name="機房", boundary=[(14, 12), (18, 12), (17, 21), (14, 22)],
                 space_type="mechanical", area_sqm=36.0),
    ]
    openings = [
        OpeningDef(wall_index=0, offset_m=4.0, width_m=2.0, height_m=2.4, opening_type="door"),
        OpeningDef(wall_index=0, offset_m=8.0, width_m=1.5, height_m=1.5,
                   sill_height_m=0.9, opening_type="window"),
    ]

    return StoryPlan(
        name="1F",
        elevation_m=0.0,
        height_m=3.6,
        walls=walls,
        spaces=spaces,
        openings=openings,
        slab_boundary=footprint,
        slab_thickness_m=0.2,
    )


def _make_2f(footprint: list[tuple[float, float]]) -> StoryPlan:
    """2F: 2 residential units (~55 sqm each)."""
    return _make_residential_floor("2F", 3.6, footprint)


def _make_3f(footprint: list[tuple[float, float]]) -> StoryPlan:
    """3F: 2 residential units (~55 sqm each)."""
    return _make_residential_floor("3F", 6.6, footprint)


def _make_residential_floor(
    name: str, elevation: float, footprint: list[tuple[float, float]]
) -> StoryPlan:
    """Create a residential floor with 2 units."""
    walls = _make_walls(footprint)
    # Central corridor wall
    walls.append(WallDef(start=(5.0, 13.0), end=(18.0, 13.0), thickness_m=0.15, wall_type="interior"))
    # Unit divider
    walls.append(WallDef(start=(11.5, 5.0), end=(11.5, 22.0), thickness_m=0.15, wall_type="interior"))

    spaces = [
        # Unit A
        SpaceDef(name="客廳A", boundary=[(5, 5), (11.5, 5), (11.5, 10), (5, 10)],
                 space_type="living", area_sqm=32.5),
        SpaceDef(name="臥室A", boundary=[(5, 10), (11.5, 10), (11.5, 13), (5, 13)],
                 space_type="bedroom", area_sqm=19.5),
        SpaceDef(name="廚房A", boundary=[(5, 13), (8, 13), (8, 17), (5, 17)],
                 space_type="kitchen", area_sqm=12.0),
        SpaceDef(name="廁所A", boundary=[(8, 13), (11.5, 13), (11.5, 17), (8, 17)],
                 space_type="bathroom", area_sqm=14.0),
        # Unit B
        SpaceDef(name="客廳B", boundary=[(11.5, 5), (18, 5), (18, 10), (11.5, 10)],
                 space_type="living", area_sqm=32.5),
        SpaceDef(name="臥室B", boundary=[(11.5, 10), (18, 10), (18, 13), (11.5, 13)],
                 space_type="bedroom", area_sqm=19.5),
        SpaceDef(name="廚房B", boundary=[(11.5, 13), (14.5, 13), (14.5, 17), (11.5, 17)],
                 space_type="kitchen", area_sqm=12.0),
        SpaceDef(name="廁所B", boundary=[(14.5, 13), (18, 13), (17.5, 17), (14.5, 17)],
                 space_type="bathroom", area_sqm=12.25),
    ]

    openings = [
        # Windows
        OpeningDef(wall_index=0, offset_m=2.0, width_m=1.8, height_m=1.5,
                   sill_height_m=0.9, opening_type="window"),
        OpeningDef(wall_index=0, offset_m=8.0, width_m=1.8, height_m=1.5,
                   sill_height_m=0.9, opening_type="window"),
        OpeningDef(wall_index=1, offset_m=3.0, width_m=1.2, height_m=1.5,
                   sill_height_m=0.9, opening_type="window"),
    ]

    return StoryPlan(
        name=name,
        elevation_m=elevation,
        height_m=3.0,
        walls=walls,
        spaces=spaces,
        openings=openings,
        slab_boundary=footprint,
        slab_thickness_m=0.2,
    )


# ---------------------------------------------------------------------------
# Task 18: Demo Result
# ---------------------------------------------------------------------------

def get_demo_result() -> GenerationResult:
    """Return a complete demo GenerationResult with pre-computed data."""
    plan = get_demo_plan()
    land = get_demo_land()
    zoning = get_demo_zoning()
    fp_area = _shoelace(plan.building_footprint)

    compliance_report = {
        "bcr": {"limit": zoning.bcr_limit, "actual": plan.building_bcr, "pass": plan.building_bcr <= zoning.bcr_limit},
        "far": {"limit": zoning.far_limit, "actual": plan.building_far, "pass": plan.building_far <= zoning.far_limit},
        "height": {"limit_m": zoning.height_limit_m, "actual_m": 9.6, "pass": 9.6 <= zoning.height_limit_m},
        "setback_front": {"required_m": zoning.setback_front_m, "actual_m": 5.0, "pass": True},
    }

    cost_per_sqm = 85000  # NT$/sqm for residential
    total_area = fp_area * 3
    total_cost = total_area * cost_per_sqm

    return GenerationResult(
        success=True,
        building_name=plan.name,
        summary={
            "stories": len(plan.stories),
            "bcr": plan.building_bcr,
            "far": plan.building_far,
            "footprint_area": round(fp_area, 2),
            "total_floor_area": round(total_area, 2),
            "estimated_cost_twd": round(total_cost, 0),
            "cost_per_sqm_twd": cost_per_sqm,
        },
        compliance_report=compliance_report,
        compliance_text="All checks passed. BCR, FAR, height, and setbacks within limits.",
    )


def get_demo_cost_estimate() -> dict:
    """Return pre-computed cost estimate JSON."""
    plan = get_demo_plan()
    fp_area = _shoelace(plan.building_footprint)
    total_area = fp_area * 3

    return {
        "total_cost_twd": round(total_area * 85000, 0),
        "cost_per_sqm_twd": 85000,
        "breakdown": [
            {"category": "structure", "cost_twd": round(total_area * 30000, 0), "pct": 35.3},
            {"category": "finishing", "cost_twd": round(total_area * 20000, 0), "pct": 23.5},
            {"category": "mep", "cost_twd": round(total_area * 15000, 0), "pct": 17.6},
            {"category": "exterior", "cost_twd": round(total_area * 10000, 0), "pct": 11.8},
            {"category": "site", "cost_twd": round(total_area * 10000, 0), "pct": 11.8},
        ],
        "currency": "TWD",
    }


def save_demo_resources() -> dict[str, Path]:
    """Save demo resource files to resources/demo/. Returns paths dict."""
    DEMO_RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}

    # Cost estimate
    cost_path = DEMO_RESOURCES_DIR / "cost_estimate.json"
    cost_path.write_text(json.dumps(get_demo_cost_estimate(), ensure_ascii=False, indent=2))
    paths["cost_estimate"] = cost_path

    # Compliance report
    result = get_demo_result()
    compliance_path = DEMO_RESOURCES_DIR / "compliance_report.json"
    compliance_path.write_text(json.dumps(result.compliance_report, ensure_ascii=False, indent=2))
    paths["compliance_report"] = compliance_path

    # Plan JSON
    plan_path = DEMO_RESOURCES_DIR / "plan.json"
    plan_path.write_text(get_demo_plan().model_dump_json(indent=2))
    paths["plan"] = plan_path

    return paths


# ---------------------------------------------------------------------------
# Task P24-1: Generate Demo IFC
# ---------------------------------------------------------------------------


def generate_demo_ifc(output_dir: Path = DEMO_RESOURCES_DIR) -> Path:
    """Generate an IFC file from the demo BuildingPlan using IFCGenerator."""
    from promptbim.bim.ifc_generator import IFCGenerator

    output_dir.mkdir(parents=True, exist_ok=True)
    plan = get_demo_plan()
    gen = IFCGenerator()
    ifc_path = output_dir / "demo_building.ifc"
    gen.generate(plan, str(ifc_path))
    return ifc_path


# ---------------------------------------------------------------------------
# Task P24-2: Generate Demo USDA
# ---------------------------------------------------------------------------


def generate_demo_usda(output_dir: Path = DEMO_RESOURCES_DIR) -> Path:
    """Generate a USDA file from the demo BuildingPlan using USDGenerator."""
    from promptbim.bim.usd_generator import USDGenerator

    output_dir.mkdir(parents=True, exist_ok=True)
    plan = get_demo_plan()
    gen = USDGenerator()
    usda_path = output_dir / "demo_building.usda"
    gen.generate(plan, str(usda_path))
    return usda_path


# ---------------------------------------------------------------------------
# Task P24-3: Generate Demo SVG floor plans + site plan
# ---------------------------------------------------------------------------


def generate_demo_svg(output_dir: Path = DEMO_RESOURCES_DIR) -> list[Path]:
    """Generate 2D floor plan SVGs and a site plan SVG for the demo project."""
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = get_demo_plan()
    land = get_demo_land()
    zoning = get_demo_zoning()
    paths: list[Path] = []

    # Per-floor SVGs
    for story in plan.stories:
        svg_path = output_dir / f"demo_floorplan_{story.name.lower()}.svg"
        svg_content = _render_floorplan_svg(story)
        svg_path.write_text(svg_content, encoding="utf-8")
        paths.append(svg_path)

    # Site plan SVG
    site_path = output_dir / "demo_site_plan.svg"
    site_svg = _render_site_plan_svg(land, plan, zoning)
    site_path.write_text(site_svg, encoding="utf-8")
    paths.append(site_path)

    return paths


def _render_floorplan_svg(story) -> str:
    """Render a single story as an SVG floor plan."""
    margin = 2
    # Determine bounding box from slab boundary
    if story.slab_boundary:
        xs = [p[0] for p in story.slab_boundary]
        ys = [p[1] for p in story.slab_boundary]
    else:
        xs, ys = [0, 20], [0, 25]
    min_x, max_x = min(xs) - margin, max(xs) + margin
    min_y, max_y = min(ys) - margin, max(ys) + margin
    w, h = max_x - min_x, max_y - min_y
    scale = 20  # px per metre

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{min_x * scale} {min_y * scale} {w * scale} {h * scale}" '
        f'width="{w * scale}" height="{h * scale}">',
        '<rect width="100%" height="100%" fill="#fafafa"/>',
    ]

    # Slab outline
    if story.slab_boundary:
        pts = " ".join(f"{x * scale},{y * scale}" for x, y in story.slab_boundary)
        lines.append(f'<polygon points="{pts}" fill="#e0e0e0" stroke="#333" stroke-width="1"/>')

    # Walls
    for wall in story.walls:
        sx, sy = wall.start
        ex, ey = wall.end
        sw = max(1, wall.thickness_m * scale)
        color = "#444" if wall.wall_type == "exterior" else "#999"
        lines.append(
            f'<line x1="{sx * scale}" y1="{sy * scale}" '
            f'x2="{ex * scale}" y2="{ey * scale}" '
            f'stroke="{color}" stroke-width="{sw}"/>'
        )

    # Space labels
    for space in story.spaces:
        if space.boundary:
            cx = sum(p[0] for p in space.boundary) / len(space.boundary)
            cy = sum(p[1] for p in space.boundary) / len(space.boundary)
            lines.append(
                f'<text x="{cx * scale}" y="{cy * scale}" '
                f'font-size="8" text-anchor="middle" fill="#555">'
                f'{space.name} ({space.area_sqm:.0f}m²)</text>'
            )

    lines.append(f'<text x="{(min_x + 1) * scale}" y="{(min_y + 1.5) * scale}" '
                 f'font-size="12" font-weight="bold" fill="#222">{story.name}</text>')
    lines.append("</svg>")
    return "\n".join(lines)


def _render_site_plan_svg(land, plan, zoning) -> str:
    """Render site plan SVG with land boundary, building footprint, and setback lines."""
    margin = 3
    xs = [p[0] for p in land.boundary]
    ys = [p[1] for p in land.boundary]
    min_x, max_x = min(xs) - margin, max(xs) + margin
    min_y, max_y = min(ys) - margin, max(ys) + margin
    w, h = max_x - min_x, max_y - min_y
    scale = 20

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{min_x * scale} {min_y * scale} {w * scale} {h * scale}" '
        f'width="{w * scale}" height="{h * scale}">',
        '<rect width="100%" height="100%" fill="#f5f5f0"/>',
    ]

    # Land boundary
    pts = " ".join(f"{x * scale},{y * scale}" for x, y in land.boundary)
    lines.append(f'<polygon points="{pts}" fill="#d4edda" stroke="#28a745" stroke-width="2"/>')

    # Setback lines (approximate inset)
    front, back = zoning.setback_front_m, zoning.setback_back_m
    left, right = zoning.setback_left_m, zoning.setback_right_m
    setback_boundary = [
        (land.boundary[0][0] + left, land.boundary[0][1] + front),
        (land.boundary[1][0] - right, land.boundary[1][1] + front),
        (land.boundary[2][0] - right, land.boundary[2][1] - back),
        (land.boundary[3][0] + left, land.boundary[3][1] - back),
    ]
    pts_s = " ".join(f"{x * scale},{y * scale}" for x, y in setback_boundary)
    lines.append(
        f'<polygon points="{pts_s}" fill="none" stroke="#fd7e14" '
        f'stroke-width="1" stroke-dasharray="6,3"/>'
    )

    # Building footprint
    if plan.building_footprint:
        pts_b = " ".join(f"{x * scale},{y * scale}" for x, y in plan.building_footprint)
        lines.append(
            f'<polygon points="{pts_b}" fill="rgba(0,123,255,0.2)" '
            f'stroke="#007bff" stroke-width="1.5"/>'
        )

    # Labels
    land_cx = sum(xs) / len(xs)
    land_cy = sum(ys) / len(ys)
    lines.append(
        f'<text x="{land_cx * scale}" y="{(min_y + 1.5) * scale}" '
        f'font-size="11" font-weight="bold" text-anchor="middle" fill="#222">'
        f'Site Plan — {land.name}</text>'
    )
    lines.append(
        f'<text x="{land_cx * scale}" y="{land_cy * scale}" '
        f'font-size="9" text-anchor="middle" fill="#007bff">'
        f'Building ({len(plan.stories)}F)</text>'
    )

    lines.append("</svg>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Task P24-4: Fallback sample IFC (generated procedurally if main gen fails)
# ---------------------------------------------------------------------------

SAMPLE_IFC_PATH = DEMO_RESOURCES_DIR / "sample_house.ifc"


def ensure_fallback_ifc(output_dir: Path = DEMO_RESOURCES_DIR) -> Path:
    """Ensure a fallback IFC exists — generates a simple box house if needed."""
    path = output_dir / "sample_house.ifc"
    if path.exists():
        return path
    # Generate a minimal single-story box house as fallback
    from promptbim.bim.ifc_generator import IFCGenerator
    from promptbim.schemas.plan import BuildingPlan, RoofPlan, StoryPlan, WallDef

    simple_fp = [(0, 0), (10, 0), (10, 8), (0, 8)]
    walls = [
        WallDef(start=simple_fp[i], end=simple_fp[(i + 1) % 4],
                thickness_m=0.2, wall_type="exterior")
        for i in range(4)
    ]
    story = StoryPlan(
        name="1F", elevation_m=0.0, height_m=3.0,
        walls=walls, slab_boundary=simple_fp, slab_thickness_m=0.2,
    )
    plan = BuildingPlan(
        name="Sample House (Fallback)",
        building_footprint=simple_fp,
        stories=[story],
        roof=RoofPlan(roof_type="flat"),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    gen = IFCGenerator()
    gen.generate(plan, str(path))
    return path


# ---------------------------------------------------------------------------
# Task P24-5: Generate all demo resources
# ---------------------------------------------------------------------------


def generate_all_demo_resources() -> dict[str, Path]:
    """Generate all demo resources: JSON + IFC + USDA + SVG."""
    paths = save_demo_resources()
    try:
        paths["ifc"] = generate_demo_ifc()
    except Exception:
        # Fallback to simple sample house
        try:
            paths["ifc"] = ensure_fallback_ifc()
        except Exception:
            paths["ifc"] = None
    try:
        paths["usda"] = generate_demo_usda()
    except Exception:
        paths["usda"] = None
    try:
        svg_paths = generate_demo_svg()
        paths["svg"] = svg_paths
    except Exception:
        paths["svg"] = None
    return paths


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _shoelace(coords: list[tuple[float, float]]) -> float:
    """Compute polygon area using the Shoelace formula."""
    n = len(coords)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    return abs(area) / 2.0


def _perimeter(coords: list[tuple[float, float]]) -> float:
    """Compute polygon perimeter."""
    import math
    n = len(coords)
    perim = 0.0
    for i in range(n):
        j = (i + 1) % n
        dx = coords[j][0] - coords[i][0]
        dy = coords[j][1] - coords[i][1]
        perim += math.sqrt(dx * dx + dy * dy)
    return round(perim, 2)
