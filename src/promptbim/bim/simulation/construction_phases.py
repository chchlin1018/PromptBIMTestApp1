"""Construction phase templates for 4D BIM simulation.

Defines standard construction phases with IFC class mappings and
duration ratios for scheduling.

D1-S1 additions:
- EXCAVATION_PHASES: detailed earthwork + shoring phases
- STEEL_ERECTION_PHASES: steel frame erection sequence
- get_extended_phases(): combine standard + excavation + erection
- classify_component_extended(): handle excavation/erection labels
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass
class ConstructionPhase:
    """A single construction phase."""

    phase_id: str
    name: str
    ifc_classes: list[str]
    duration_ratio: float
    description: str = ""
    color: tuple[float, float, float] = (0.5, 0.5, 0.5)


# Standard 16-phase construction sequence
STANDARD_PHASES: list[ConstructionPhase] = [
    ConstructionPhase(
        "P01",
        "Site Preparation",
        ["IfcSite"],
        0.05,
        "Grading and excavation",
        color=(0.6, 0.4, 0.2),
    ),
    ConstructionPhase(
        "P02",
        "Foundation",
        ["IfcFooting", "IfcPile"],
        0.10,
        "Footings, piles, grade beams",
        color=(0.5, 0.5, 0.5),
    ),
    ConstructionPhase(
        "P03",
        "Substructure",
        ["IfcWall:basement", "IfcSlab:basement"],
        0.08,
        "Basement walls and slabs",
        color=(0.6, 0.6, 0.6),
    ),
    ConstructionPhase(
        "P04",
        "Columns",
        ["IfcColumn"],
        0.10,
        "Structural columns",
        color=(0.7, 0.7, 0.7),
    ),
    ConstructionPhase(
        "P05",
        "Beams",
        ["IfcBeam"],
        0.08,
        "Structural beams",
        color=(0.65, 0.65, 0.65),
    ),
    ConstructionPhase(
        "P06",
        "Floor Slabs",
        ["IfcSlab:floor", "IfcSlab"],
        0.08,
        "Floor slabs",
        color=(0.75, 0.75, 0.75),
    ),
    ConstructionPhase(
        "P07",
        "Shear Walls / Core",
        ["IfcWall:shear"],
        0.05,
        "Shear walls and core structure",
        color=(0.55, 0.55, 0.6),
    ),
    ConstructionPhase(
        "P08",
        "Roof",
        ["IfcRoof"],
        0.04,
        "Roof structure and waterproofing",
        color=(0.6, 0.3, 0.3),
    ),
    ConstructionPhase(
        "P09",
        "Exterior Walls",
        ["IfcWall:exterior", "IfcCurtainWall"],
        0.08,
        "Exterior walls and curtain walls",
        color=(0.8, 0.8, 0.7),
    ),
    ConstructionPhase(
        "P10",
        "Doors & Windows",
        ["IfcDoor", "IfcWindow"],
        0.05,
        "Door and window installation",
        color=(0.4, 0.6, 0.8),
    ),
    ConstructionPhase(
        "P11",
        "MEP Rough-in",
        ["IfcDuctSegment", "IfcPipeSegment", "IfcCableCarrierSegment"],
        0.08,
        "Mechanical, electrical, plumbing rough-in",
        color=(0.3, 0.7, 0.3),
    ),
    ConstructionPhase(
        "P12",
        "Partition Walls",
        ["IfcWall:partition", "IfcWall:interior"],
        0.05,
        "Interior partition walls",
        color=(0.85, 0.85, 0.8),
    ),
    ConstructionPhase(
        "P13",
        "Elevators",
        ["IfcTransportElement"],
        0.04,
        "Elevator and escalator installation",
        color=(0.4, 0.4, 0.6),
    ),
    ConstructionPhase(
        "P14",
        "Ceiling & Flooring",
        ["IfcCovering"],
        0.05,
        "Ceiling and floor finishes",
        color=(0.9, 0.85, 0.75),
    ),
    ConstructionPhase(
        "P15",
        "Fixtures & Equipment",
        ["IfcSanitaryTerminal", "IfcFurniture"],
        0.04,
        "Sanitary fixtures and furniture",
        color=(0.5, 0.7, 0.9),
    ),
    ConstructionPhase(
        "P16",
        "MEP Finish",
        ["IfcLightFixture", "IfcFireSuppression"],
        0.03,
        "Lighting, fire suppression, final MEP",
        color=(0.8, 0.8, 0.3),
    ),
]


def get_phase_by_id(phase_id: str) -> ConstructionPhase | None:
    """Look up a phase by its ID."""
    for p in STANDARD_PHASES:
        if p.phase_id == phase_id:
            return p
    return None


class ComponentType(Enum):
    """SIM-01 fix: Enum-based component classification to prevent misclassification."""
    ROOF = "P08"
    FOUNDATION = "P02"
    SLAB = "P06"
    WALL_PARTITION = "P12"
    WALL_EXTERIOR = "P09"
    COLUMN = "P04"
    BEAM = "P05"
    DOOR_WINDOW = "P10"
    MEP_ROUGHIN = "P11"
    ELEVATOR = "P13"
    FINISH = "P14"
    FIXTURE = "P15"
    MEP_FINISH = "P16"


# Keyword-to-enum mapping (ordered by specificity — more specific first)
_COMPONENT_KEYWORDS: list[tuple[list[str], ComponentType]] = [
    (["roof"], ComponentType.ROOF),
    (["ground_slab"], ComponentType.FOUNDATION),
    (["slab"], ComponentType.SLAB),
    (["wall_partition", "wall_interior", "partition_wall", "interior_wall"], ComponentType.WALL_PARTITION),
    (["wall"], ComponentType.WALL_EXTERIOR),
    (["column"], ComponentType.COLUMN),
    (["beam"], ComponentType.BEAM),
    (["door", "window"], ComponentType.DOOR_WINDOW),
    (["duct", "pipe", "cable"], ComponentType.MEP_ROUGHIN),
    (["elevator", "escalator"], ComponentType.ELEVATOR),
    (["ceiling", "floor_tile", "covering"], ComponentType.FINISH),
    (["sanitary", "furniture"], ComponentType.FIXTURE),
    (["light", "fire", "sprinkler"], ComponentType.MEP_FINISH),
]


# ============================================================
# D1-S1: Excavation phases (P-03 to P-01 — before P01)
# ============================================================

EXCAVATION_PHASES: list[ConstructionPhase] = [
    ConstructionPhase(
        "E01",
        "土地清理",
        ["IfcSite:clearing"],
        0.02,
        "Vegetation removal, site fencing, utility relocation",
        color=(0.5, 0.35, 0.1),
    ),
    ConstructionPhase(
        "E02",
        "開挖第一層 (地表)",
        ["IfcExcavation:L1"],
        0.03,
        "First cut excavation — topsoil to 2m depth",
        color=(0.55, 0.38, 0.12),
    ),
    ConstructionPhase(
        "E03",
        "擋土支撐 (地下連續壁/鋼板樁)",
        ["IfcPile:sheet", "IfcWall:retaining"],
        0.04,
        "Shoring: diaphragm wall, sheet pile, or soldier pile",
        color=(0.4, 0.4, 0.45),
    ),
    ConstructionPhase(
        "E04",
        "開挖第二層 (中層)",
        ["IfcExcavation:L2"],
        0.04,
        "Second cut excavation — 2m to basement depth",
        color=(0.58, 0.40, 0.14),
    ),
    ConstructionPhase(
        "E05",
        "底版澆置",
        ["IfcSlab:mat", "IfcFooting:mat"],
        0.05,
        "Mat foundation concrete pour",
        color=(0.6, 0.6, 0.6),
    ),
]

# ============================================================
# D1-S1: Steel erection phases (for steel frame buildings)
# ============================================================

STEEL_ERECTION_PHASES: list[ConstructionPhase] = [
    ConstructionPhase(
        "S01",
        "鋼柱安裝 (一二層)",
        ["IfcColumn:steel_L1"],
        0.06,
        "Steel column erection — floors 1-2",
        color=(0.5, 0.5, 0.7),
    ),
    ConstructionPhase(
        "S02",
        "鋼梁安裝 (一二層)",
        ["IfcBeam:steel_L1"],
        0.05,
        "Steel beam erection — floors 1-2",
        color=(0.55, 0.55, 0.72),
    ),
    ConstructionPhase(
        "S03",
        "鋼柱安裝 (三層以上)",
        ["IfcColumn:steel_upper"],
        0.07,
        "Steel column erection — floor 3 and above",
        color=(0.45, 0.45, 0.68),
    ),
    ConstructionPhase(
        "S04",
        "鋼梁安裝 (三層以上)",
        ["IfcBeam:steel_upper"],
        0.06,
        "Steel beam erection — floor 3 and above",
        color=(0.5, 0.5, 0.70),
    ),
    ConstructionPhase(
        "S05",
        "樓板鋪設 (鋼承板)",
        ["IfcSlab:steel_deck"],
        0.05,
        "Metal deck and composite slab",
        color=(0.7, 0.7, 0.65),
    ),
    ConstructionPhase(
        "S06",
        "防火被覆",
        ["IfcBuildingElementProxy:fireproofing"],
        0.04,
        "Spray fireproofing on structural steel",
        color=(0.8, 0.6, 0.4),
    ),
]


def get_extended_phases(include_excavation: bool = True, include_steel: bool = False) -> list[ConstructionPhase]:
    """Return standard phases optionally extended with excavation and/or steel erection.

    D1-S1: Enables more detailed 4D simulation sequences.
    """
    phases = []
    if include_excavation:
        phases.extend(EXCAVATION_PHASES)
    phases.extend(STANDARD_PHASES)
    if include_steel:
        # Insert steel phases after P02 (foundation)
        result = []
        for p in phases:
            result.append(p)
            if p.phase_id == "P02":
                result.extend(STEEL_ERECTION_PHASES)
        return result
    return phases


def classify_component_extended(label: str) -> str | None:
    """Extended component classifier that handles excavation and steel labels (D1-S1)."""
    label_lower = label.lower()
    # Excavation keywords
    if "excavat" in label_lower or "開挖" in label_lower or "cut" in label_lower:
        if "l2" in label_lower or "level2" in label_lower or "deep" in label_lower:
            return "E04"
        return "E02"
    if "shoring" in label_lower or "sheet_pile" in label_lower or "diaphragm" in label_lower:
        return "E03"
    if "mat_slab" in label_lower or "底版" in label_lower:
        return "E05"
    # Steel erection keywords
    if "steel_column" in label_lower or "鋼柱" in label_lower:
        if "upper" in label_lower or "l3" in label_lower:
            return "S03"
        return "S01"
    if "steel_beam" in label_lower or "鋼梁" in label_lower:
        if "upper" in label_lower or "l3" in label_lower:
            return "S04"
        return "S02"
    if "steel_deck" in label_lower or "鋼承板" in label_lower:
        return "S05"
    if "fireproof" in label_lower or "防火被覆" in label_lower:
        return "S06"
    # Fall back to standard classifier
    return classify_component(label)


def classify_component(label: str) -> str | None:
    """Map a building component label to a phase ID.

    Uses keyword matching with enum-based classification (SIM-01 fix).
    More specific compound keywords are checked first to prevent
    misclassification (e.g., 'wall_exterior_frame' won't match partition).
    """
    label_lower = label.lower()

    for keywords, comp_type in _COMPONENT_KEYWORDS:
        for kw in keywords:
            if kw in label_lower:
                # For wall classification, check compound keywords first
                if comp_type == ComponentType.WALL_EXTERIOR:
                    # Double-check it's not a partition/interior
                    if "partition" in label_lower or "interior" in label_lower:
                        return ComponentType.WALL_PARTITION.value
                return comp_type.value

    return None
