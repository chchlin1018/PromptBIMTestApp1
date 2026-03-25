#!/usr/bin/env python3
"""Example 02 — L-shaped 2-storey office building → .ifc + .usda

Footprint is an L-shape formed by two rectangles:
  - Main wing:  16m × 10m
  - Side wing:  10m × 6m (attached to the east end)
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


def make_l_shaped_office() -> BuildingPlan:
    """Create a hardcoded L-shaped 2-storey office."""
    # L-shape boundary (counter-clockwise)
    #   (0,0)---(16,0)---(16,6)---(10,6)---(10,10)---(0,10)
    footprint = [
        (0, 0), (16, 0), (16, 6), (10, 6), (10, 10), (0, 10)
    ]

    def make_story(name: str, elev: float) -> StoryPlan:
        """Build one floor of the L-shaped office."""
        # Exterior walls follow footprint
        n = len(footprint)
        walls = [
            WallDef(
                start=footprint[i],
                end=footprint[(i + 1) % n],
                wall_type="exterior",
            )
            for i in range(n)
        ]
        # Interior partition: separate main wing from side wing at x=10
        walls.append(
            WallDef(start=(10, 0), end=(10, 6), wall_type="interior", thickness_m=0.15)
        )

        spaces = [
            SpaceDef(
                name="Main Wing",
                boundary=[(0, 0), (10, 0), (10, 10), (0, 10)],
                space_type="office",
                area_sqm=100.0,
            ),
            SpaceDef(
                name="Side Wing",
                boundary=[(10, 0), (16, 0), (16, 6), (10, 6)],
                space_type="meeting",
                area_sqm=36.0,
            ),
        ]

        return StoryPlan(
            name=name,
            elevation_m=elev,
            height_m=3.2,
            walls=walls,
            spaces=spaces,
            slab_boundary=footprint,
        )

    stories = [
        make_story("1F", 0.0),
        make_story("2F", 3.2),
    ]

    return BuildingPlan(
        name="L-Shaped Office",
        building_footprint=footprint,
        stories=stories,
        roof=RoofPlan(roof_type="flat"),
    )


def main() -> None:
    plan = make_l_shaped_office()

    ifc_gen = IFCGenerator()
    ifc_path = ifc_gen.generate(plan, OUTPUT_DIR / "l_shaped_office.ifc")
    print(f"IFC written: {ifc_path}")

    usd_gen = USDGenerator()
    usd_path = usd_gen.generate(plan, OUTPUT_DIR / "l_shaped_office.usda")
    print(f"USD written: {usd_path}")

    # Verify
    import ifcopenshell
    model = ifcopenshell.open(str(ifc_path))
    walls = model.by_type("IfcWall")
    slabs = model.by_type("IfcSlab")
    storeys = model.by_type("IfcBuildingStorey")
    print(f"IFC: {len(storeys)} storeys, {len(walls)} walls, {len(slabs)} slabs")

    from pxr import Usd
    stage = Usd.Stage.Open(str(usd_path))
    prims = [p.GetPath().pathString for p in stage.Traverse()]
    print(f"USD: {len(prims)} prims")


if __name__ == "__main__":
    main()
