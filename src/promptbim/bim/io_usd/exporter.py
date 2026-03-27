"""USD Exporter — writes mesh data + ILOS metadata to USD.

Output is compatible with Omniverse and other USD viewers.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


class USDExporter:
    """Export mesh data to USD format with ILOS metadata."""

    def export(
        self,
        elements: list[dict[str, Any]],
        output_path: str | Path,
        *,
        up_axis: str = "Y",
        meters_per_unit: float = 1.0,
    ) -> Path:
        """Export elements to a USD file.

        Args:
            elements: List of element dicts with vertices, indices, material, ilos data.
            output_path: Path for the output .usda/.usdc file.
            up_axis: Up axis ("Y" or "Z").
            meters_per_unit: Scale factor.

        Returns:
            Path to the created USD file.
        """
        from pxr import Usd, UsdGeom, Gf, Sdf, Vt

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        stage = Usd.Stage.CreateNew(str(output_path))
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y if up_axis == "Y" else UsdGeom.Tokens.z)
        UsdGeom.SetStageMetersPerUnit(stage, meters_per_unit)

        root_prim = stage.DefinePrim("/BIMModel", "Xform")
        stage.SetDefaultPrim(root_prim)

        for elem in elements:
            elem_name = elem.get("id", "element").replace(".", "_").replace("/", "_")
            prim_path = f"/BIMModel/{elem_name}"

            mesh_prim = UsdGeom.Mesh.Define(stage, prim_path)

            # Set vertices
            vertices = elem.get("vertices", [])
            if vertices:
                points = [Gf.Vec3f(*v) for v in vertices]
                mesh_prim.GetPointsAttr().Set(Vt.Vec3fArray(points))

            # Set face indices (all triangles)
            indices = elem.get("indices", [])
            if indices:
                face_vertex_counts = [3] * len(indices)
                face_vertex_indices = []
                for tri in indices:
                    face_vertex_indices.extend(tri)

                mesh_prim.GetFaceVertexCountsAttr().Set(Vt.IntArray(face_vertex_counts))
                mesh_prim.GetFaceVertexIndicesAttr().Set(Vt.IntArray(face_vertex_indices))

            # Set ILOS metadata as custom attributes
            prim = mesh_prim.GetPrim()
            ilos = elem.get("ilos", {})
            if isinstance(ilos, dict):
                for key, value in ilos.items():
                    if value:
                        attr = prim.CreateAttribute(f"ilos:{key}", Sdf.ValueTypeNames.String)
                        attr.Set(str(value))

            # Set material type
            material = elem.get("material", "")
            if material:
                attr = prim.CreateAttribute("ilos:material", Sdf.ValueTypeNames.String)
                attr.Set(material)

            # Set element type
            elem_type = elem.get("type", "")
            if elem_type:
                attr = prim.CreateAttribute("ilos:element_type", Sdf.ValueTypeNames.String)
                attr.Set(elem_type)

        stage.Save()
        return output_path
