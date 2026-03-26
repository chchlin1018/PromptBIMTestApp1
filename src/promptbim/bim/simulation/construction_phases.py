"""Construction phase templates for 4D BIM simulation.

Defines standard construction phases with IFC class mappings and
duration ratios for scheduling.
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
