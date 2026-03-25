#!/usr/bin/env python3
"""Example 01 — Simple box building → .ifc + .usda

A single-storey 10m × 8m box with four exterior walls, a slab, and a flat roof.
"""

from pathlib import Path

from promptbim.bim.ifc_generator import IFCGenerator
from promptbim.bim.usd_generator import USDGenerator
from promptbim.schemas.plan import (
    BuildingPlan,
    RoofPlan,
    SpaceDef,
    StoryPlan,
    WallDef,
)

OUTPUT_DIR = Path(__file__).parent / "output"


def make_simple_box() -> BuildingPlan:
    """Create a hardcoded 10×8 m single-storey box."""
    # Corners: (0,0) → (10,0) → (10,8) → (0,8)
    footprint = [(0, 0), (10, 0), (10, 8), (0, 8)]

    walls = [
        WallDef(start=(0, 0), end=(10, 0), wall_type="exterior"),
        WallDef(start=(10, 0), end=(10, 8), wall_type="exterior"),
        WallDef(start=(10, 8), end=(0, 8), wall_type="exterior"),
        WallDef(start=(0, 8), end=(0, 0), wall_type="exterior"),
    ]

    story = StoryPlan(
        name="1F",
        elevation_m=0.0,
        height_m=3.0,
        walls=walls,
        spaces=[
            SpaceDef(
                name="Main Room",
                boundary=footprint,
                space_type="office",
                area_sqm=80.0,
            )
        ],
        slab_boundary=footprint,
    )

    return BuildingPlan(
        name="Simple Box",
        building_footprint=footprint,
        stories=[story],
        roof=RoofPlan(roof_type="flat"),
    )


def main() -> None:
    plan = make_simple_box()

    ifc_gen = IFCGenerator()
    ifc_path = ifc_gen.generate(plan, OUTPUT_DIR / "simple_box.ifc")
    print(f"IFC written: {ifc_path}")

    usd_gen = USDGenerator()
    usd_path = usd_gen.generate(plan, OUTPUT_DIR / "simple_box.usda")
    print(f"USD written: {usd_path}")

    # Verify IFC can be re-read
    import ifcopenshell
    model = ifcopenshell.open(str(ifc_path))
    walls = model.by_type("IfcWall")
    slabs = model.by_type("IfcSlab")
    print(f"IFC verification: {len(walls)} walls, {len(slabs)} slabs")

    # Verify USD can be re-opened
    from pxr import Usd
    stage = Usd.Stage.Open(str(usd_path))
    prims = [p.GetPath().pathString for p in stage.Traverse()]
    print(f"USD verification: {len(prims)} prims")


if __name__ == "__main__":
    main()
