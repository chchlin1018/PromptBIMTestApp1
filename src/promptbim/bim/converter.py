"""BIM model converter: IFC/FBX → USD.

D1-S1 Task 5: Bridge external BIM files into the PromptBIM USD pipeline.

Supported conversions:
- IFC → BuildingPlan (via ifcopenshell parsing) → USD
- FBX → USD  (via pxr UsdUtils / FBX SDK stub — requires usdFbx plugin)
- USD/USDA → pass-through (already in native format)

Usage::

    from promptbim.bim.converter import BIMConverter
    converter = BIMConverter(output_dir="./outputs")
    usd_path = converter.ifc_to_usd("building.ifc")
    usd_path = converter.fbx_to_usd("building.fbx")
    plan = converter.ifc_to_plan("building.ifc")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger("bim.converter")


@dataclass
class ConversionResult:
    """Result of a BIM file conversion."""

    success: bool
    input_path: str = ""
    output_path: str = ""
    format_in: str = ""
    format_out: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)  # element_count, story_count, etc.


class BIMConverter:
    """Convert external BIM files into PromptBIM-native USD format.

    D1-S1: Enables importing real project IFC/FBX models for 4D simulation,
    cost estimation, and design change analysis.
    """

    def __init__(self, output_dir: str | Path = ".") -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # IFC → BuildingPlan
    # ------------------------------------------------------------------ #

    def ifc_to_plan(self, ifc_path: str | Path) -> "tuple[BuildingPlan | None, ConversionResult]":
        """Parse an IFC file and extract a PromptBIM BuildingPlan.

        Extracts walls, slabs, spaces and stories from the IFC model using
        ifcopenshell. Falls back gracefully if ifcopenshell is not installed.
        """
        from promptbim.schemas.plan import (
            BuildingPlan, RoofPlan, SpaceDef, StoryPlan, WallDef,
        )

        ifc_path = Path(ifc_path)
        result = ConversionResult(
            input_path=str(ifc_path),
            format_in="IFC",
            format_out="BuildingPlan",
        )

        if not ifc_path.exists():
            result.errors.append(f"IFC file not found: {ifc_path}")
            return None, result

        try:
            import ifcopenshell  # noqa: F401
        except ImportError:
            result.errors.append("ifcopenshell not installed; pip install ifcopenshell")
            return None, result

        try:
            import ifcopenshell

            model = ifcopenshell.open(str(ifc_path))
            stories_data = _extract_ifc_stories(model)
            building_name = _get_ifc_building_name(model) or ifc_path.stem

            stories: list[StoryPlan] = []
            all_footprints: list[list] = []

            for s_data in stories_data:
                elevation = s_data.get("elevation_m", len(stories) * 3.0)
                height = s_data.get("height_m", 3.0)
                walls = [WallDef(**w) for w in s_data.get("walls", [])]
                spaces = [SpaceDef(**sp) for sp in s_data.get("spaces", [])]
                footprint = s_data.get("footprint", [])
                if footprint:
                    all_footprints.append(footprint)

                stories.append(StoryPlan(
                    name=s_data.get("name", f"{len(stories)+1}F"),
                    elevation_m=elevation,
                    height_m=height,
                    walls=walls,
                    spaces=spaces,
                    openings=[],
                    slab_boundary=footprint or [],
                ))

            # Use first-floor footprint as building footprint
            building_footprint = all_footprints[0] if all_footprints else []

            # Estimate BCR/FAR
            from promptbim.bim.geometry import poly_area
            fp_area = poly_area(building_footprint) if building_footprint else 0
            land_area = max(fp_area * 1.5, 1)  # estimate if unknown
            bcr = fp_area / land_area if land_area > 0 else 0
            total_floor_area = sum(
                poly_area(s.slab_boundary) if s.slab_boundary else fp_area
                for s in stories
            )
            far = total_floor_area / land_area if land_area > 0 else 0

            plan = BuildingPlan(
                name=building_name,
                land_boundary=building_footprint,
                buildable_area=building_footprint,
                building_footprint=building_footprint,
                building_bcr=round(bcr, 4),
                building_far=round(far, 4),
                stories=stories,
                roof=RoofPlan(roof_type="flat"),
            )

            result.success = True
            result.stats = {
                "story_count": len(stories),
                "wall_count": sum(len(s.walls) for s in stories),
                "space_count": sum(len(s.spaces) for s in stories),
            }
            logger.info("IFC → BuildingPlan: %s (%d stories)", building_name, len(stories))
            return plan, result

        except Exception as exc:
            logger.exception("IFC parsing failed")
            result.errors.append(str(exc))
            return None, result

    # ------------------------------------------------------------------ #
    # IFC → USD (via BuildingPlan intermediate)
    # ------------------------------------------------------------------ #

    def ifc_to_usd(
        self,
        ifc_path: str | Path,
        output_name: str | None = None,
        include_mep: bool = True,
    ) -> ConversionResult:
        """Convert IFC → BuildingPlan → USD.

        This is the main integration path: parse IFC geometry, build a
        PromptBIM BuildingPlan, then generate a USD file with phase tags
        and MEP layers.
        """
        ifc_path = Path(ifc_path)
        output_name = output_name or (ifc_path.stem + ".usda")
        output_path = self._output_dir / output_name

        plan, conv_result = self.ifc_to_plan(ifc_path)
        conv_result.format_out = "USD"
        conv_result.output_path = str(output_path)

        if plan is None:
            return conv_result

        try:
            from promptbim.bim.usd_generator import USDGenerator
            gen = USDGenerator()
            gen.generate(plan, output_path, include_mep=include_mep)
            conv_result.success = True
            conv_result.stats["usd_size_kb"] = output_path.stat().st_size // 1024
            logger.info("IFC → USD: %s → %s", ifc_path.name, output_path.name)
        except Exception as exc:
            logger.exception("USD generation from IFC plan failed")
            conv_result.errors.append(f"USD generation: {exc}")
            conv_result.success = False

        return conv_result

    # ------------------------------------------------------------------ #
    # FBX → USD
    # ------------------------------------------------------------------ #

    def fbx_to_usd(
        self,
        fbx_path: str | Path,
        output_name: str | None = None,
    ) -> ConversionResult:
        """Convert FBX → USD using pxr FBX plugin or usd_from_file.

        Requires the USD FBX plugin (usdFbx). Falls back to a stub result
        with instructions if the plugin is unavailable.
        """
        fbx_path = Path(fbx_path)
        output_name = output_name or (fbx_path.stem + ".usda")
        output_path = self._output_dir / output_name

        result = ConversionResult(
            input_path=str(fbx_path),
            output_path=str(output_path),
            format_in="FBX",
            format_out="USD",
        )

        if not fbx_path.exists():
            result.errors.append(f"FBX file not found: {fbx_path}")
            return result

        # Try usdARKit / usdFbx command-line tool
        converted = self._try_usdconvert(fbx_path, output_path)
        if converted:
            result.success = True
            result.stats["usd_size_kb"] = output_path.stat().st_size // 1024
            return result

        # Try pxr.UsdUtils (if available)
        try:
            from pxr import UsdUtils
            UsdUtils.CoalesceRelatedFiles(str(fbx_path), str(output_path))
            result.success = True
            result.stats["method"] = "UsdUtils"
            return result
        except Exception:
            pass

        result.warnings.append(
            "FBX → USD conversion requires the usdFbx plugin. "
            "Install via Pixar USD or NVIDIA Omniverse. "
            "Alternative: export FBX as .obj then use usdview."
        )
        result.success = False
        return result

    # ------------------------------------------------------------------ #
    # USD pass-through / USDZ unpack
    # ------------------------------------------------------------------ #

    def usd_to_usda(self, usd_path: str | Path, output_name: str | None = None) -> ConversionResult:
        """Convert binary USD → ASCII USDA for inspection."""
        usd_path = Path(usd_path)
        output_name = output_name or (usd_path.stem + ".usda")
        output_path = self._output_dir / output_name

        result = ConversionResult(
            input_path=str(usd_path),
            output_path=str(output_path),
            format_in=usd_path.suffix.upper().lstrip("."),
            format_out="USDA",
        )

        if not usd_path.exists():
            result.errors.append(f"USD file not found: {usd_path}")
            return result

        try:
            from pxr import Usd
            stage = Usd.Stage.Open(str(usd_path))
            stage.Export(str(output_path))
            result.success = True
            logger.info("USD → USDA: %s → %s", usd_path.name, output_path.name)
        except Exception as exc:
            result.errors.append(str(exc))

        return result

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _try_usdconvert(self, src: Path, dst: Path) -> bool:
        """Attempt FBX conversion via usdconvert CLI tool."""
        import shutil
        import subprocess

        for tool in ("usdconvert", "UsdConverter"):
            if shutil.which(tool):
                try:
                    subprocess.run(
                        [tool, str(src), str(dst)],
                        check=True, capture_output=True, timeout=120,
                    )
                    return dst.exists()
                except Exception:
                    pass
        return False


# ---------------------------------------------------------------------------
# IFC parsing helpers
# ---------------------------------------------------------------------------


def _get_ifc_building_name(model) -> str:
    """Extract building name from IFC model."""
    try:
        buildings = model.by_type("IfcBuilding")
        if buildings:
            return buildings[0].Name or ""
    except Exception:
        pass
    return ""


def _extract_ifc_stories(model) -> list[dict]:
    """Extract story data from an IFC model.

    Returns a list of dicts with keys:
      name, elevation_m, height_m, walls, spaces, footprint
    """
    stories_data: list[dict] = []
    try:
        storeys = model.by_type("IfcBuildingStorey")
    except Exception:
        return stories_data

    for storey in sorted(storeys, key=lambda s: getattr(s, "Elevation", 0) or 0):
        elevation = float(getattr(storey, "Elevation", 0) or 0)
        story_dict: dict = {
            "name": storey.Name or f"{len(stories_data)+1}F",
            "elevation_m": elevation / 1000.0 if elevation > 100 else elevation,  # mm → m
            "height_m": 3.0,
            "walls": [],
            "spaces": [],
            "footprint": [],
        }

        # Extract walls in this storey
        try:
            walls = _get_storey_elements(model, storey, "IfcWall")
            for wall in walls:
                w = _ifc_wall_to_walldef(wall)
                if w:
                    story_dict["walls"].append(w)
        except Exception:
            pass

        # Extract spaces
        try:
            spaces = _get_storey_elements(model, storey, "IfcSpace")
            for space in spaces:
                sp = _ifc_space_to_spacedef(space)
                if sp:
                    story_dict["spaces"].append(sp)
        except Exception:
            pass

        stories_data.append(story_dict)

    return stories_data


def _get_storey_elements(model, storey, ifc_class: str) -> list:
    """Get IFC elements of a given class in a building storey."""
    try:
        elements = []
        for rel in storey.ContainsElements or []:
            for elem in rel.RelatedElements or []:
                if elem.is_a(ifc_class):
                    elements.append(elem)
        return elements
    except Exception:
        return []


def _ifc_wall_to_walldef(wall) -> dict | None:
    """Convert an IfcWall to a WallDef dict (approximate geometry)."""
    try:
        # Extract placement for approximate start/end
        placement = wall.ObjectPlacement
        if placement is None:
            return None
        loc = placement.RelativePlacement.Location.Coordinates
        x, y = float(loc[0]) / 1000.0, float(loc[1]) / 1000.0
        # Use OverallWidth as length
        length = 5.0
        try:
            length = float(wall.Representation.Representations[0].Items[0].SweptArea.XDim) / 1000.0
        except Exception:
            pass
        return {
            "start": [x, y],
            "end": [x + length, y],
            "thickness_m": 0.2,
            "wall_type": "exterior",
        }
    except Exception:
        return None


def _ifc_space_to_spacedef(space) -> dict | None:
    """Convert an IfcSpace to a SpaceDef dict."""
    try:
        name = space.Name or "Space"
        area = 0.0
        try:
            for prop_set in space.IsDefinedBy or []:
                for prop in getattr(prop_set, "RelatingPropertyDefinition", {}).HasProperties or []:
                    if prop.Name in ("NetFloorArea", "GrossFloorArea"):
                        area = float(prop.NominalValue.wrappedValue) / 1_000_000  # mm² → m²
                        break
        except Exception:
            area = 20.0
        return {
            "name": name,
            "boundary": [[0, 0], [4, 0], [4, 5], [0, 5]],  # approximate
            "space_type": "office",
            "area_sqm": area or 20.0,
        }
    except Exception:
        return None
