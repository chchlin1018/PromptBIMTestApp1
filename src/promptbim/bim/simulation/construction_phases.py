"""Construction phase templates for 4D BIM simulation.

Defines standard construction phases with IFC class mappings and
duration ratios for scheduling.
"""

from __future__ import annotations

from dataclasses import dataclass, field


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
        "P01", "Site Preparation",
        ["IfcSite"],
        0.05, "Grading and excavation",
        color=(0.6, 0.4, 0.2),
    ),
    ConstructionPhase(
        "P02", "Foundation",
        ["IfcFooting", "IfcPile"],
        0.10, "Footings, piles, grade beams",
        color=(0.5, 0.5, 0.5),
    ),
    ConstructionPhase(
        "P03", "Substructure",
        ["IfcWall:basement", "IfcSlab:basement"],
        0.08, "Basement walls and slabs",
        color=(0.6, 0.6, 0.6),
    ),
    ConstructionPhase(
        "P04", "Columns",
        ["IfcColumn"],
        0.10, "Structural columns",
        color=(0.7, 0.7, 0.7),
    ),
    ConstructionPhase(
        "P05", "Beams",
        ["IfcBeam"],
        0.08, "Structural beams",
        color=(0.65, 0.65, 0.65),
    ),
    ConstructionPhase(
        "P06", "Floor Slabs",
        ["IfcSlab:floor", "IfcSlab"],
        0.08, "Floor slabs",
        color=(0.75, 0.75, 0.75),
    ),
    ConstructionPhase(
        "P07", "Shear Walls / Core",
        ["IfcWall:shear"],
        0.05, "Shear walls and core structure",
        color=(0.55, 0.55, 0.6),
    ),
    ConstructionPhase(
        "P08", "Roof",
        ["IfcRoof"],
        0.04, "Roof structure and waterproofing",
        color=(0.6, 0.3, 0.3),
    ),
    ConstructionPhase(
        "P09", "Exterior Walls",
        ["IfcWall:exterior", "IfcCurtainWall"],
        0.08, "Exterior walls and curtain walls",
        color=(0.8, 0.8, 0.7),
    ),
    ConstructionPhase(
        "P10", "Doors & Windows",
        ["IfcDoor", "IfcWindow"],
        0.05, "Door and window installation",
        color=(0.4, 0.6, 0.8),
    ),
    ConstructionPhase(
        "P11", "MEP Rough-in",
        ["IfcDuctSegment", "IfcPipeSegment", "IfcCableCarrierSegment"],
        0.08, "Mechanical, electrical, plumbing rough-in",
        color=(0.3, 0.7, 0.3),
    ),
    ConstructionPhase(
        "P12", "Partition Walls",
        ["IfcWall:partition", "IfcWall:interior"],
        0.05, "Interior partition walls",
        color=(0.85, 0.85, 0.8),
    ),
    ConstructionPhase(
        "P13", "Elevators",
        ["IfcTransportElement"],
        0.04, "Elevator and escalator installation",
        color=(0.4, 0.4, 0.6),
    ),
    ConstructionPhase(
        "P14", "Ceiling & Flooring",
        ["IfcCovering"],
        0.05, "Ceiling and floor finishes",
        color=(0.9, 0.85, 0.75),
    ),
    ConstructionPhase(
        "P15", "Fixtures & Equipment",
        ["IfcSanitaryTerminal", "IfcFurniture"],
        0.04, "Sanitary fixtures and furniture",
        color=(0.5, 0.7, 0.9),
    ),
    ConstructionPhase(
        "P16", "MEP Finish",
        ["IfcLightFixture", "IfcFireSuppression"],
        0.03, "Lighting, fire suppression, final MEP",
        color=(0.8, 0.8, 0.3),
    ),
]


def get_phase_by_id(phase_id: str) -> ConstructionPhase | None:
    """Look up a phase by its ID."""
    for p in STANDARD_PHASES:
        if p.phase_id == phase_id:
            return p
    return None


def classify_component(label: str) -> str | None:
    """Map a building component label to a phase ID.

    Uses simple heuristic matching against component label strings
    (e.g. '1F_wall_0', 'ground_slab', 'roof').
    """
    label_lower = label.lower()

    if "roof" in label_lower:
        return "P08"
    if "ground_slab" in label_lower:
        return "P02"
    if "slab" in label_lower:
        return "P06"
    if "wall" in label_lower:
        # Distinguish wall types
        if "partition" in label_lower or "interior" in label_lower:
            return "P12"
        return "P09"  # default to exterior walls
    if "column" in label_lower:
        return "P04"
    if "beam" in label_lower:
        return "P05"
    if "door" in label_lower or "window" in label_lower:
        return "P10"
    if "duct" in label_lower or "pipe" in label_lower or "cable" in label_lower:
        return "P11"
    if "elevator" in label_lower or "escalator" in label_lower:
        return "P13"
    if "ceiling" in label_lower or "floor" in label_lower or "covering" in label_lower:
        return "P14"
    if "sanitary" in label_lower or "furniture" in label_lower:
        return "P15"
    if "light" in label_lower or "fire" in label_lower or "sprinkler" in label_lower:
        return "P16"

    return None
