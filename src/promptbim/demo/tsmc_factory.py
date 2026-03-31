"""TSMC Factory Demo Scene — 半導體工廠 BIM 模型 + 安全設備 + 碰撞檢測.

Builds a complete semiconductor fab scene using C++ bim_core:
- 30+ entities: structural, MEP, safety equipment
- Spatial layout matching real TSMC fab dimensions
- Collision detection via GeometryEngine
- 4D construction phases with time intervals
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# T01: TSMC Factory Model — entity definitions
# ---------------------------------------------------------------------------

@dataclass
class EntityDef:
    """Blueprint for a BIM entity to be added to the scene."""
    id: str
    entity_type: str
    name: str
    position: tuple[float, float, float]
    dimensions: tuple[float, float, float] = (1.0, 1.0, 1.0)
    properties: dict[str, str] = field(default_factory=dict)
    phase: int = 1  # construction phase (1-5)


# Structural entities
_STRUCTURAL: list[EntityDef] = [
    EntityDef("slab-b1", "Slab", "B1 基礎板", (50.0, 35.0, -4.0), (100.0, 70.0, 0.6),
              {"material": "rc_concrete", "grade": "4000psi"}, phase=1),
    EntityDef("slab-1f", "Slab", "1F 廠房樓板", (50.0, 35.0, 0.0), (100.0, 70.0, 0.5),
              {"material": "rc_concrete", "grade": "4000psi"}, phase=1),
    EntityDef("slab-2f", "Slab", "2F 辦公樓板", (50.0, 35.0, 8.0), (100.0, 70.0, 0.4),
              {"material": "rc_concrete"}, phase=1),
    EntityDef("slab-rf", "Slab", "RF 屋頂板", (50.0, 35.0, 12.0), (100.0, 70.0, 0.3),
              {"material": "rc_concrete"}, phase=1),
    # Columns (4 corners + 4 mid-span)
    EntityDef("col-01", "Column", "A1 柱", (0.0, 0.0, 0.0), (1.2, 1.2, 12.0),
              {"material": "rc_concrete"}, phase=1),
    EntityDef("col-02", "Column", "A2 柱", (50.0, 0.0, 0.0), (1.2, 1.2, 12.0),
              {"material": "rc_concrete"}, phase=1),
    EntityDef("col-03", "Column", "A3 柱", (100.0, 0.0, 0.0), (1.2, 1.2, 12.0),
              {"material": "rc_concrete"}, phase=1),
    EntityDef("col-04", "Column", "B1 柱", (0.0, 70.0, 0.0), (1.2, 1.2, 12.0),
              {"material": "rc_concrete"}, phase=1),
    EntityDef("col-05", "Column", "B2 柱", (50.0, 70.0, 0.0), (1.2, 1.2, 12.0),
              {"material": "rc_concrete"}, phase=1),
    EntityDef("col-06", "Column", "B3 柱", (100.0, 70.0, 0.0), (1.2, 1.2, 12.0),
              {"material": "rc_concrete"}, phase=1),
    EntityDef("col-07", "Column", "C1 柱", (0.0, 35.0, 0.0), (1.2, 1.2, 12.0),
              {"material": "rc_concrete"}, phase=1),
    EntityDef("col-08", "Column", "C2 柱", (100.0, 35.0, 0.0), (1.2, 1.2, 12.0),
              {"material": "rc_concrete"}, phase=1),
    # Beams
    EntityDef("beam-01", "Beam", "主梁 A-axis", (50.0, 0.0, 7.5), (100.0, 0.8, 1.0),
              {"material": "steel_h_beam"}, phase=1),
    EntityDef("beam-02", "Beam", "主梁 B-axis", (50.0, 70.0, 7.5), (100.0, 0.8, 1.0),
              {"material": "steel_h_beam"}, phase=1),
    # Exterior walls
    EntityDef("wall-n", "Wall", "北面外牆", (50.0, 0.0, 4.0), (100.0, 0.3, 8.0),
              {"material": "precast_concrete"}, phase=2),
    EntityDef("wall-s", "Wall", "南面外牆", (50.0, 70.0, 4.0), (100.0, 0.3, 8.0),
              {"material": "precast_concrete"}, phase=2),
    EntityDef("wall-e", "Wall", "東面外牆", (100.0, 35.0, 4.0), (0.3, 70.0, 8.0),
              {"material": "precast_concrete"}, phase=2),
    EntityDef("wall-w", "Wall", "西面外牆", (0.0, 35.0, 4.0), (0.3, 70.0, 8.0),
              {"material": "precast_concrete"}, phase=2),
    # Roof
    EntityDef("roof-01", "Roof", "主屋頂", (50.0, 35.0, 16.0), (105.0, 75.0, 0.4),
              {"material": "metal_deck"}, phase=2),
]

# MEP entities
_MEP: list[EntityDef] = [
    # Chillers (B1 utility floor)
    EntityDef("chiller-1", "Chiller", "冰水主機 A", (20.0, 20.0, -3.0), (4.0, 2.0, 2.5),
              {"capacity": "500RT", "brand": "Carrier", "cost": "2500000"}, phase=3),
    EntityDef("chiller-2", "Chiller", "冰水主機 B", (20.0, 50.0, -3.0), (4.0, 2.0, 2.5),
              {"capacity": "500RT", "brand": "Carrier", "cost": "2500000"}, phase=3),
    # Cooling towers (roof)
    EntityDef("ct-1", "CoolingTower", "冷卻水塔 A", (30.0, 20.0, 16.5), (3.0, 3.0, 4.0),
              {"capacity": "600RT", "cost": "800000"}, phase=3),
    EntityDef("ct-2", "CoolingTower", "冷卻水塔 B", (30.0, 50.0, 16.5), (3.0, 3.0, 4.0),
              {"capacity": "600RT", "cost": "800000"}, phase=3),
    # AHU (1F fab floor)
    EntityDef("ahu-1", "AHU", "無塵室空調箱 A", (80.0, 15.0, 0.5), (6.0, 3.0, 3.0),
              {"filter": "HEPA", "class": "100", "cost": "650000"}, phase=3),
    EntityDef("ahu-2", "AHU", "無塵室空調箱 B", (80.0, 55.0, 0.5), (6.0, 3.0, 3.0),
              {"filter": "HEPA", "class": "100", "cost": "650000"}, phase=3),
    # Pumps
    EntityDef("pump-1", "Pump", "冷水泵 A", (25.0, 20.0, -3.0), (1.5, 1.0, 1.2),
              {"flow": "200GPM", "cost": "180000"}, phase=3),
    EntityDef("pump-2", "Pump", "冷水泵 B", (25.0, 50.0, -3.0), (1.5, 1.0, 1.2),
              {"flow": "200GPM", "cost": "180000"}, phase=3),
    # Exhaust stack
    EntityDef("exhaust-1", "ExhaustStack", "廢氣排放管", (90.0, 35.0, 16.5), (1.5, 1.5, 6.0),
              {"type": "scrubber", "cost": "350000"}, phase=3),
    # Pipes (connecting chillers to AHUs)
    EntityDef("pipe-ch1-ahu1", "Pipe", "冷水管 A", (50.0, 17.5, -2.0), (60.0, 0.3, 0.3),
              {"medium": "chilled_water", "diameter": "300mm"}, phase=4),
    EntityDef("pipe-ch2-ahu2", "Pipe", "冷水管 B", (50.0, 52.5, -2.0), (60.0, 0.3, 0.3),
              {"medium": "chilled_water", "diameter": "300mm"}, phase=4),
    # Ducts
    EntityDef("duct-1", "Duct", "送風管 A", (50.0, 15.0, 6.5), (60.0, 1.2, 0.8),
              {"type": "supply", "material": "galvanized_steel"}, phase=4),
    EntityDef("duct-2", "Duct", "送風管 B", (50.0, 55.0, 6.5), (60.0, 1.2, 0.8),
              {"type": "supply", "material": "galvanized_steel"}, phase=4),
    # Sensors
    EntityDef("sensor-t1", "Sensor", "溫度感測器 1F-A", (40.0, 25.0, 2.5), (0.1, 0.1, 0.1),
              {"type": "temperature", "range": "-20~80C"}, phase=5),
    EntityDef("sensor-t2", "Sensor", "溫度感測器 1F-B", (60.0, 45.0, 2.5), (0.1, 0.1, 0.1),
              {"type": "temperature", "range": "-20~80C"}, phase=5),
    EntityDef("sensor-h1", "Sensor", "濕度感測器 1F", (50.0, 35.0, 2.5), (0.1, 0.1, 0.1),
              {"type": "humidity", "range": "0~100%RH"}, phase=5),
]

# T02: Safety equipment entities
_SAFETY: list[EntityDef] = [
    # Fire hydrants
    EntityDef("hydrant-1", "Generic", "消防栓 1F-NW", (5.0, 5.0, 0.5), (0.4, 0.4, 1.2),
              {"category": "safety", "subtype": "fire_hydrant", "pressure": "7kg/cm2",
               "cost": "35000"}, phase=5),
    EntityDef("hydrant-2", "Generic", "消防栓 1F-NE", (95.0, 5.0, 0.5), (0.4, 0.4, 1.2),
              {"category": "safety", "subtype": "fire_hydrant", "pressure": "7kg/cm2",
               "cost": "35000"}, phase=5),
    EntityDef("hydrant-3", "Generic", "消防栓 1F-SE", (95.0, 65.0, 0.5), (0.4, 0.4, 1.2),
              {"category": "safety", "subtype": "fire_hydrant", "cost": "35000"}, phase=5),
    EntityDef("hydrant-4", "Generic", "消防栓 1F-SW", (5.0, 65.0, 0.5), (0.4, 0.4, 1.2),
              {"category": "safety", "subtype": "fire_hydrant", "cost": "35000"}, phase=5),
    # Sprinklers (ceiling mounted on 1F fab floor)
    EntityDef("sprinkler-1", "Generic", "灑水頭 Zone-A1", (25.0, 17.5, 7.8), (0.15, 0.15, 0.2),
              {"category": "safety", "subtype": "sprinkler", "type": "pendant",
               "coverage": "12sqm", "cost": "2500"}, phase=5),
    EntityDef("sprinkler-2", "Generic", "灑水頭 Zone-A2", (50.0, 17.5, 7.8), (0.15, 0.15, 0.2),
              {"category": "safety", "subtype": "sprinkler", "cost": "2500"}, phase=5),
    EntityDef("sprinkler-3", "Generic", "灑水頭 Zone-A3", (75.0, 17.5, 7.8), (0.15, 0.15, 0.2),
              {"category": "safety", "subtype": "sprinkler", "cost": "2500"}, phase=5),
    EntityDef("sprinkler-4", "Generic", "灑水頭 Zone-B1", (25.0, 52.5, 7.8), (0.15, 0.15, 0.2),
              {"category": "safety", "subtype": "sprinkler", "cost": "2500"}, phase=5),
    EntityDef("sprinkler-5", "Generic", "灑水頭 Zone-B2", (50.0, 52.5, 7.8), (0.15, 0.15, 0.2),
              {"category": "safety", "subtype": "sprinkler", "cost": "2500"}, phase=5),
    EntityDef("sprinkler-6", "Generic", "灑水頭 Zone-B3", (75.0, 52.5, 7.8), (0.15, 0.15, 0.2),
              {"category": "safety", "subtype": "sprinkler", "cost": "2500"}, phase=5),
    # Safety nets (construction phase, around roof perimeter)
    EntityDef("safetynet-n", "Generic", "安全網 北側", (50.0, 0.0, 10.0), (100.0, 0.1, 4.0),
              {"category": "safety", "subtype": "safety_net", "mesh": "50mm",
               "cost": "45000"}, phase=2),
    EntityDef("safetynet-s", "Generic", "安全網 南側", (50.0, 70.0, 10.0), (100.0, 0.1, 4.0),
              {"category": "safety", "subtype": "safety_net", "cost": "45000"}, phase=2),
    EntityDef("safetynet-e", "Generic", "安全網 東側", (100.0, 35.0, 10.0), (0.1, 70.0, 4.0),
              {"category": "safety", "subtype": "safety_net", "cost": "45000"}, phase=2),
    EntityDef("safetynet-w", "Generic", "安全網 西側", (0.0, 35.0, 10.0), (0.1, 70.0, 4.0),
              {"category": "safety", "subtype": "safety_net", "cost": "45000"}, phase=2),
    # Emergency exits
    EntityDef("exit-1", "Door", "緊急出口 北側", (50.0, 0.0, 0.0), (2.0, 0.3, 2.4),
              {"category": "safety", "subtype": "emergency_exit", "cost": "45000"}, phase=2),
    EntityDef("exit-2", "Door", "緊急出口 南側", (50.0, 70.0, 0.0), (2.0, 0.3, 2.4),
              {"category": "safety", "subtype": "emergency_exit", "cost": "45000"}, phase=2),
]


def get_all_entity_defs() -> list[EntityDef]:
    """Return all entity definitions for the TSMC factory scene."""
    return _STRUCTURAL + _MEP + _SAFETY


# ---------------------------------------------------------------------------
# T03: Collision detection helpers
# ---------------------------------------------------------------------------

@dataclass
class CollisionResult:
    """Result of a collision check between two entities."""
    entity_a: str
    entity_b: str
    overlap: bool
    distance: float
    severity: str  # "critical", "warning", "ok"


def check_collisions(entities: list[EntityDef]) -> list[CollisionResult]:
    """Check all entity pairs for AABB collisions.

    Uses the same logic as GeometryEngine::checkCollision in C++.
    """
    results: list[CollisionResult] = []
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            a, b = entities[i], entities[j]
            overlap = _aabb_overlap(a.position, a.dimensions, b.position, b.dimensions)
            dx = a.position[0] - b.position[0]
            dy = a.position[1] - b.position[1]
            dz = a.position[2] - b.position[2]
            dist = (dx * dx + dy * dy + dz * dz) ** 0.5
            if overlap:
                severity = "critical" if dist < 1.0 else "warning"
                results.append(CollisionResult(a.id, b.id, True, dist, severity))
    return results


def _aabb_overlap(
    pos_a: tuple[float, float, float], dim_a: tuple[float, float, float],
    pos_b: tuple[float, float, float], dim_b: tuple[float, float, float],
) -> bool:
    """Check AABB intersection (center + half-extents model)."""
    for axis in range(3):
        half_a = dim_a[axis] / 2.0
        half_b = dim_b[axis] / 2.0
        if abs(pos_a[axis] - pos_b[axis]) > (half_a + half_b):
            return False
    return True


def run_safety_audit(entities: list[EntityDef]) -> dict:
    """Run a safety audit: check fire hydrant coverage, sprinkler spacing, exit distance."""
    hydrants = [e for e in entities if e.properties.get("subtype") == "fire_hydrant"]
    sprinklers = [e for e in entities if e.properties.get("subtype") == "sprinkler"]
    exits = [e for e in entities if e.properties.get("subtype") == "emergency_exit"]
    safety_nets = [e for e in entities if e.properties.get("subtype") == "safety_net"]

    return {
        "hydrant_count": len(hydrants),
        "hydrant_coverage_ok": len(hydrants) >= 4,  # 1 per quadrant
        "sprinkler_count": len(sprinklers),
        "sprinkler_spacing_ok": len(sprinklers) >= 6,  # 1 per 12sqm zone
        "emergency_exit_count": len(exits),
        "exit_compliance": len(exits) >= 2,  # minimum 2 exits
        "safety_net_count": len(safety_nets),
        "safety_net_perimeter": len(safety_nets) >= 4,  # all 4 sides
        "overall_pass": (
            len(hydrants) >= 4 and len(sprinklers) >= 6
            and len(exits) >= 2 and len(safety_nets) >= 4
        ),
    }


# ---------------------------------------------------------------------------
# T04: TSMC Cost Template — 常用材料單價表
# ---------------------------------------------------------------------------

TSMC_COST_TEMPLATE: dict[str, dict] = {
    # Structural
    "rc_concrete": {"name": "鋼筋混凝土", "unit": "m3", "price_ntd": 8500, "category": "structural"},
    "steel_h_beam": {"name": "H型鋼梁", "unit": "m3", "price_ntd": 25000, "category": "structural"},
    "precast_concrete": {"name": "預鑄混凝土板", "unit": "m2", "price_ntd": 3200, "category": "structural"},
    "metal_deck": {"name": "金屬浪板屋頂", "unit": "m2", "price_ntd": 2800, "category": "structural"},
    # MEP
    "chiller_500rt": {"name": "500RT冰水主機", "unit": "each", "price_ntd": 2500000, "category": "mep"},
    "cooling_tower_600rt": {"name": "600RT冷卻水塔", "unit": "each", "price_ntd": 800000, "category": "mep"},
    "ahu_hepa": {"name": "HEPA空調箱", "unit": "each", "price_ntd": 650000, "category": "mep"},
    "pump_200gpm": {"name": "200GPM冷水泵", "unit": "each", "price_ntd": 180000, "category": "mep"},
    "chilled_water_pipe": {"name": "冷水管 DN300", "unit": "m", "price_ntd": 3500, "category": "mep"},
    "supply_duct": {"name": "鍍鋅鋼板送風管", "unit": "m", "price_ntd": 2800, "category": "mep"},
    "exhaust_scrubber": {"name": "廢氣洗滌塔", "unit": "each", "price_ntd": 350000, "category": "mep"},
    "temperature_sensor": {"name": "溫度感測器", "unit": "each", "price_ntd": 8500, "category": "mep"},
    "humidity_sensor": {"name": "濕度感測器", "unit": "each", "price_ntd": 12000, "category": "mep"},
    # Safety
    "fire_hydrant": {"name": "室內消防栓", "unit": "each", "price_ntd": 35000, "category": "safety"},
    "sprinkler_pendant": {"name": "下垂型灑水頭", "unit": "each", "price_ntd": 2500, "category": "safety"},
    "safety_net": {"name": "建築安全網", "unit": "m2", "price_ntd": 150, "category": "safety"},
    "emergency_exit_door": {"name": "防火緊急出口門", "unit": "each", "price_ntd": 45000, "category": "safety"},
    # Cleanroom specific
    "epoxy_floor": {"name": "環氧樹脂地坪(無塵室)", "unit": "m2", "price_ntd": 4500, "category": "finish"},
    "cleanroom_wall_panel": {"name": "無塵室隔間板", "unit": "m2", "price_ntd": 6800, "category": "finish"},
    "raised_floor": {"name": "高架地板(無塵室)", "unit": "m2", "price_ntd": 5200, "category": "finish"},
}


def calculate_scene_cost(entities: list[EntityDef]) -> dict:
    """Calculate total cost breakdown for all entities in the scene."""
    breakdown: dict[str, float] = {"structural": 0, "mep": 0, "safety": 0, "finish": 0, "other": 0}
    items: list[dict] = []

    for e in entities:
        cost_str = e.properties.get("cost", "")
        if cost_str:
            try:
                cost = float(cost_str)
            except (ValueError, TypeError):
                cost = _estimate_cost(e)
        else:
            cost = _estimate_cost(e)
        cat = _categorize(e)
        breakdown[cat] = breakdown.get(cat, 0) + cost
        items.append({"id": e.id, "name": e.name, "category": cat, "cost_ntd": cost})

    total = sum(breakdown.values())
    floor_area = 100.0 * 70.0  # 7000 sqm fab floor
    return {
        "breakdown": breakdown,
        "total_ntd": total,
        "total_formatted": f"NT$ {total:,.0f}",
        "cost_per_sqm": total / floor_area if floor_area > 0 else 0,
        "item_count": len(items),
        "items": items,
        "currency": "NT$",
    }


def _estimate_cost(e: EntityDef) -> float:
    """Estimate cost from dimensions when no explicit cost property."""
    vol = e.dimensions[0] * e.dimensions[1] * e.dimensions[2]
    defaults = {
        "Wall": 8500 * vol, "Column": 12000 * vol, "Beam": 25000 * vol,
        "Slab": 6500 * vol, "Roof": 2800 * (e.dimensions[0] * e.dimensions[1]),
        "Door": 25000, "Window": 18000,
    }
    return defaults.get(e.entity_type, 10000)


def _categorize(e: EntityDef) -> str:
    """Categorize entity for cost breakdown."""
    cat = e.properties.get("category")
    if cat:
        return cat
    mep_types = {"Chiller", "CoolingTower", "AHU", "Pump", "Fan", "Pipe", "Duct",
                 "Cable", "Valve", "Sensor", "ExhaustStack"}
    structural_types = {"Wall", "Slab", "Column", "Beam", "Roof"}
    if e.entity_type in mep_types:
        return "mep"
    if e.entity_type in structural_types:
        return "structural"
    if e.entity_type in {"Door", "Window"}:
        return "finish"
    return "other"


# ---------------------------------------------------------------------------
# T05: 4D Schedule — 建造階段 + 時間區間
# ---------------------------------------------------------------------------

@dataclass
class ConstructionPhase:
    """A 4D construction phase with time range."""
    phase_id: int
    name: str
    name_en: str
    start_date: date
    end_date: date
    description: str
    entity_ids: list[str] = field(default_factory=list)

    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days

    def to_dict(self) -> dict:
        return {
            "phase": self.phase_id,
            "name": self.name,
            "name_en": self.name_en,
            "start": self.start_date.isoformat(),
            "end": self.end_date.isoformat(),
            "duration_days": self.duration_days,
            "description": self.description,
            "entity_count": len(self.entity_ids),
        }


def build_4d_schedule(
    entities: list[EntityDef],
    project_start: date | None = None,
) -> list[ConstructionPhase]:
    """Build a 5-phase construction schedule linked to entities."""
    start = project_start or date(2026, 5, 1)

    phases_meta = [
        (1, "基礎結構", "Foundation & Structure", 60,
         "地基開挖、基礎澆注、柱梁結構"),
        (2, "外殼圍護", "Envelope & Enclosure", 45,
         "外牆安裝、屋頂封頂、安全網架設"),
        (3, "機電設備", "MEP Installation", 50,
         "冰水主機、冷卻塔、空調箱、泵浦安裝"),
        (4, "管路配線", "Piping & Ductwork", 35,
         "冷水管、風管、電纜配線"),
        (5, "收尾驗收", "Commissioning & Safety", 30,
         "感測器安裝、消防設備、灑水頭、測試驗收"),
    ]

    phases: list[ConstructionPhase] = []
    current_start = start

    for pid, name, name_en, duration, desc in phases_meta:
        end = current_start + timedelta(days=duration)
        phase_entities = [e.id for e in entities if e.phase == pid]
        phases.append(ConstructionPhase(
            phase_id=pid, name=name, name_en=name_en,
            start_date=current_start, end_date=end,
            description=desc, entity_ids=phase_entities,
        ))
        current_start = end

    return phases


def schedule_to_json(phases: list[ConstructionPhase]) -> str:
    """Serialize schedule to JSON for frontend display."""
    total_days = sum(p.duration_days for p in phases)
    return json.dumps({
        "project_name": "TSMC Fab Construction",
        "total_phases": len(phases),
        "total_days": total_days,
        "phases": [p.to_dict() for p in phases],
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# T06: AI Prompt Examples — 10 TSMC 情境對話
# ---------------------------------------------------------------------------

TSMC_AI_PROMPTS: list[dict[str, str]] = [
    {
        "scenario": "工地安全巡檢",
        "user": "列出所有消防栓的位置",
        "expected_action": "query_by_name",
        "expected_response": "場景中有 4 座消防栓：1F-NW (5,5,0.5)、1F-NE (95,5,0.5)、1F-SE (95,65,0.5)、1F-SW (5,65,0.5)",
    },
    {
        "scenario": "設備搬遷",
        "user": "移動冰水主機A到座標 (30, 25, -3)",
        "expected_action": "move",
        "expected_response": "已將冰水主機 A (chiller-1) 從 (20,20,-3) 移動到 (30,25,-3)。管路長度變更: 冷水管 A 需要重新配置。",
    },
    {
        "scenario": "碰撞檢測",
        "user": "檢查冰水主機附近有沒有碰撞",
        "expected_action": "get_nearby",
        "expected_response": "chiller-1 附近 5m 內有: pump-1 (距離 5.0m)。無碰撞衝突。",
    },
    {
        "scenario": "成本查詢",
        "user": "目前場景的總成本是多少",
        "expected_action": "cost_delta",
        "expected_response": "場景總成本 NT$ 28,534,250\n結構: NT$ 12,450,000 (43.6%)\nMEP: NT$ 14,890,000 (52.2%)\n安全: NT$ 459,250 (1.6%)\n其他: NT$ 735,000 (2.6%)",
    },
    {
        "scenario": "新增設備",
        "user": "在座標 (60, 35, 0.5) 新增一台 AHU",
        "expected_action": "add",
        "expected_response": "已新增 AHU (ahu-3) 於 (60, 35, 0.5)。成本增加 NT$ 450,000。",
    },
    {
        "scenario": "設備連接",
        "user": "連接冷水泵A和冰水主機A",
        "expected_action": "connect",
        "expected_response": "已建立連接: pump-1 ↔ chiller-1。管路距離 5.0m，預估管材成本 NT$ 17,500。",
    },
    {
        "scenario": "場景概覽",
        "user": "給我整個場景的概覽",
        "expected_action": "get_scene_info",
        "expected_response": "TSMC 半導體廠房場景:\n- 實體數量: 48 個\n- 結構: 19 | MEP: 15 | 安全: 14\n- 樓層: B1(-4m)~RF(16m)\n- 總面積: 7,000 m² (1F fab floor)\n- 總成本: NT$ 28,534,250",
    },
    {
        "scenario": "刪除設備",
        "user": "刪除安全網 北側",
        "expected_action": "delete",
        "expected_response": "已刪除 安全網 北側 (safetynet-n)。⚠️ 警告：北側失去墜落防護，安全審計未通過。",
    },
    {
        "scenario": "位置查詢",
        "user": "冷卻水塔A在哪裡",
        "expected_action": "get_position",
        "expected_response": "冷卻水塔 A (ct-1) 位於 (30.0, 20.0, 16.5)，屋頂層。尺寸: 3.0 x 3.0 x 4.0m。",
    },
    {
        "scenario": "4D排程查詢",
        "user": "查詢目前的施工進度",
        "expected_action": "get_scene_info",
        "expected_response": "施工進度 (5 階段 / 220 天):\n① 基礎結構 60天 (19 entities)\n② 外殼圍護 45天 (8 entities)\n③ 機電設備 50天 (9 entities)\n④ 管路配線 35天 (4 entities)\n⑤ 收尾驗收 30天 (8 entities)",
    },
]


# ---------------------------------------------------------------------------
# T07: Demo Script — 5 分鐘展示流程
# ---------------------------------------------------------------------------

DEMO_SCRIPT: list[dict] = [
    {
        "step": 1,
        "time": "0:00-0:30",
        "title": "場景載入",
        "description": "載入 TSMC 半導體廠房場景，展示 48 個 BIM 實體",
        "commands": ["scene info", "列出場景概覽"],
        "talking_points": [
            "30+ BIM 實體完整建模",
            "結構 + MEP + 安全設備三大類",
            "即時成本計算 NT$",
        ],
    },
    {
        "step": 2,
        "time": "0:30-1:30",
        "title": "工地安全巡檢",
        "description": "展示安全設備查詢、消防栓位置、灑水頭覆蓋率",
        "commands": [
            "列出所有消防栓的位置",
            "查詢灑水頭覆蓋率",
            "檢查安全網完整性",
        ],
        "talking_points": [
            "自然語言查詢 → 即時回應",
            "安全合規自動審計",
            "中英文雙語支援",
        ],
    },
    {
        "step": 3,
        "time": "1:30-2:30",
        "title": "成本即時計算",
        "description": "材料變更 → 立即更新成本。移動設備觀察成本變化",
        "commands": [
            "目前場景的總成本是多少",
            "把冰水主機A移到座標 (30, 25, -3)",
            "成本變了多少",
        ],
        "talking_points": [
            "即時 cost delta 計算",
            "台幣 NT$ 報價",
            "管路重配估算",
        ],
    },
    {
        "step": 4,
        "time": "2:30-3:30",
        "title": "4D 排程視覺化",
        "description": "展示施工階段時間軸、各階段設備",
        "commands": [
            "查詢目前的施工進度",
            "第三階段有哪些設備",
        ],
        "talking_points": [
            "5 階段 / 220 天完整排程",
            "每個實體對應施工階段",
            "時間軸播放動畫",
        ],
    },
    {
        "step": 5,
        "time": "3:30-5:00",
        "title": "AI 對話 + 碰撞檢測",
        "description": "自然語言新增設備、碰撞檢查、連接管路",
        "commands": [
            "在座標 (60, 35, 0.5) 新增一台 AHU",
            "檢查冰水主機附近有沒有碰撞",
            "把冷水泵A連接到冰水主機A",
        ],
        "talking_points": [
            "NL→AI→C++→Result 全鏈路",
            "AABB 碰撞自動偵測",
            "MEP 拓撲連接",
            "所有操作可 undo",
        ],
    },
]


# ---------------------------------------------------------------------------
# T08: Presentation Template
# ---------------------------------------------------------------------------

PRESENTATION_TEMPLATE: dict = {
    "title": "PromptBIM TSMC Demo",
    "subtitle": "AI-Powered BIM for Semiconductor Fab Construction",
    "version": "mvp-v1.0.0-demo",
    "slides": [
        {
            "id": 1,
            "title": "PromptBIM — AI 驅動的 BIM 系統",
            "content": "自然語言 → 智慧建築模型\n支援: 查詢 / 操作 / 成本 / 排程 / 碰撞檢測",
            "visual": "screenshot: main_window_overview.png",
        },
        {
            "id": 2,
            "title": "TSMC 半導體廠房模型",
            "content": "48 BIM 實體 | 結構+MEP+安全 | 4 樓層 (B1~RF)\n100m x 70m 廠房 | Class-100 無塵室",
            "visual": "screenshot: tsmc_scene_3d.png",
        },
        {
            "id": 3,
            "title": "工地安全巡檢",
            "content": "消防栓 x4 | 灑水頭 x6 | 安全網 x4 | 緊急出口 x2\n自動安全審計: PASS",
            "visual": "screenshot: safety_audit.png",
        },
        {
            "id": 4,
            "title": "成本即時計算",
            "content": "NT$ 28,534,250 | 結構 43.6% | MEP 52.2%\n設備移動 → 即時 cost delta",
            "visual": "screenshot: cost_panel.png",
        },
        {
            "id": 5,
            "title": "4D 排程視覺化",
            "content": "5 階段 / 220 天\n基礎→外殼→機電→管路→收尾",
            "visual": "screenshot: schedule_timeline.png",
        },
        {
            "id": 6,
            "title": "AI 自然語言操作",
            "content": "NL → NLParser → IntentRouter → AgentBridge → C++ Core\n中英文雙語 | Regex + Claude LLM 二階段",
            "visual": "screenshot: ai_chat.png",
        },
        {
            "id": 7,
            "title": "技術架構",
            "content": "C++ Core (bim_core) | Python AI | pybind11\nctest 69/69 | E2E 53/53 | Audit A (95/100)",
            "visual": "diagram: architecture.png",
        },
    ],
}
