"""Material definitions with dual IFC + USD mapping.

Each material has an IFC surface style name and a USD PBR preset.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MaterialDef:
    """A material usable by both IFC and USD generators."""

    name: str
    # Colour as (R, G, B) floats 0-1
    color: tuple[float, float, float] = (0.8, 0.8, 0.8)
    transparency: float = 0.0
    # PBR parameters (USD)
    roughness: float = 0.5
    metallic: float = 0.0
    # IFC surface style category
    ifc_surface_style: str = "NOTDEFINED"


# ---------------------------------------------------------------------------
# Built-in material catalogue
# ---------------------------------------------------------------------------

MATERIALS: dict[str, MaterialDef] = {
    "concrete": MaterialDef(
        name="Concrete",
        color=(0.75, 0.75, 0.72),
        roughness=0.8,
        ifc_surface_style="CONCRETE",
    ),
    "concrete_slab": MaterialDef(
        name="Concrete Slab",
        color=(0.70, 0.70, 0.68),
        roughness=0.85,
        ifc_surface_style="CONCRETE",
    ),
    "brick": MaterialDef(
        name="Brick",
        color=(0.72, 0.33, 0.22),
        roughness=0.9,
        ifc_surface_style="CONCRETE",
    ),
    "glass": MaterialDef(
        name="Glass",
        color=(0.6, 0.8, 0.9),
        transparency=0.6,
        roughness=0.05,
        ifc_surface_style="MIRROR",
    ),
    "wood": MaterialDef(
        name="Wood",
        color=(0.55, 0.35, 0.17),
        roughness=0.7,
        ifc_surface_style="NOTDEFINED",
    ),
    "steel": MaterialDef(
        name="Steel",
        color=(0.6, 0.6, 0.65),
        roughness=0.3,
        metallic=0.9,
        ifc_surface_style="METAL",
    ),
    "roof_tile": MaterialDef(
        name="Roof Tile",
        color=(0.55, 0.25, 0.15),
        roughness=0.8,
        ifc_surface_style="NOTDEFINED",
    ),
    "plaster_white": MaterialDef(
        name="White Plaster",
        color=(0.95, 0.95, 0.93),
        roughness=0.6,
        ifc_surface_style="PLASTERING",
    ),
    "partition": MaterialDef(
        name="Partition Wall",
        color=(0.9, 0.9, 0.88),
        roughness=0.7,
        ifc_surface_style="PLASTERING",
    ),
}


def get_material(name: str) -> MaterialDef:
    """Return a built-in material by key, falling back to concrete."""
    return MATERIALS.get(name, MATERIALS["concrete"])


def wall_material(wall_type: str) -> MaterialDef:
    """Choose a default material based on wall type."""
    mapping = {
        "exterior": "concrete",
        "interior": "plaster_white",
        "partition": "partition",
    }
    return get_material(mapping.get(wall_type, "concrete"))


def slab_material() -> MaterialDef:
    return get_material("concrete_slab")


def roof_material(roof_type: str) -> MaterialDef:
    if roof_type == "flat":
        return get_material("concrete_slab")
    return get_material("roof_tile")
