"""USD file generator using pxr (OpenUSD).

Only ``pxr.Usd``, ``pxr.UsdGeom``, and ``pxr.UsdShade`` are used.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, Vt

from promptbim.debug import get_logger
from promptbim.bim.geometry import (
    Mesh,
    flat_roof_mesh,
    gable_roof_mesh,
    slab_mesh,
    wall_mesh,
)
from promptbim.bim.materials import (
    MaterialDef,
    roof_material,
    slab_material,
    wall_material,
)
from promptbim.schemas.plan import BuildingPlan, StoryPlan, WallDef

_logger = get_logger("bim.usd")


class USDGenerator:
    """Build an OpenUSD stage from a :class:`BuildingPlan`."""

    def __init__(self) -> None:
        self._stage: Usd.Stage | None = None
        self._material_cache: dict[str, UsdShade.Material] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, plan: BuildingPlan, output_path: str | Path) -> Path:
        """Generate a ``.usda`` file from *plan*."""
        import time as _time
        _t0 = _time.time()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._stage = Usd.Stage.CreateNew(str(output_path))
        self._material_cache.clear()

        UsdGeom.SetStageUpAxis(self._stage, UsdGeom.Tokens.z)
        UsdGeom.SetStageMetersPerUnit(self._stage, 1.0)

        root = UsdGeom.Xform.Define(self._stage, "/Building")
        root.GetPrim().SetMetadata("kind", "assembly")

        for story in plan.stories:
            self._add_story(story, plan)

        # Roof
        if plan.stories:
            top = plan.stories[-1]
            roof_z = top.elevation_m + top.height_m
            boundary = plan.building_footprint or top.slab_boundary
            if boundary:
                self._add_roof(plan.roof.roof_type, boundary, roof_z)

        self._stage.GetRootLayer().Save()
        _elapsed = _time.time() - _t0

        # Count prims and materials
        prim_count = sum(1 for _ in self._stage.TraverseAll())
        mat_count = len(self._material_cache)
        file_size = output_path.stat().st_size / 1024
        _logger.debug(
            "USD written: %s (%d prims, %d materials, %.0f KB, %.2fs)",
            output_path, prim_count, mat_count, file_size, _elapsed,
        )
        return output_path

    # ------------------------------------------------------------------
    # Story
    # ------------------------------------------------------------------

    def _add_story(self, story: StoryPlan, plan: BuildingPlan) -> None:
        story_path = f"/Building/{_safe_name(story.name)}"
        UsdGeom.Xform.Define(self._stage, story_path)

        # Walls
        for idx, wall_def in enumerate(story.walls):
            self._add_wall(wall_def, story, story_path, idx)

        # Slab
        slab_boundary = story.slab_boundary or plan.building_footprint
        if slab_boundary:
            self._add_slab(slab_boundary, story, story_path)

    # ------------------------------------------------------------------
    # Wall
    # ------------------------------------------------------------------

    def _add_wall(
        self, wall_def: WallDef, story: StoryPlan, parent_path: str, idx: int
    ) -> None:
        mesh_data = wall_mesh(
            start=wall_def.start,
            end=wall_def.end,
            height=story.height_m,
            thickness=wall_def.thickness_m,
            base_z=story.elevation_m,
        )
        if len(mesh_data.vertices) == 0:
            return

        prim_path = f"{parent_path}/Wall_{idx:03d}"
        self._create_mesh_prim(prim_path, mesh_data)

        mat_def = wall_material(wall_def.wall_type)
        usd_mat = self._get_or_create_material(mat_def)
        UsdShade.MaterialBindingAPI(
            self._stage.GetPrimAtPath(prim_path)
        ).Bind(usd_mat)

    # ------------------------------------------------------------------
    # Slab
    # ------------------------------------------------------------------

    def _add_slab(
        self,
        boundary: list[tuple[float, float]],
        story: StoryPlan,
        parent_path: str,
    ) -> None:
        mesh_data = slab_mesh(boundary, thickness=story.slab_thickness_m, base_z=story.elevation_m)
        if len(mesh_data.vertices) == 0:
            return

        prim_path = f"{parent_path}/Slab"
        self._create_mesh_prim(prim_path, mesh_data)

        mat_def = slab_material()
        usd_mat = self._get_or_create_material(mat_def)
        UsdShade.MaterialBindingAPI(
            self._stage.GetPrimAtPath(prim_path)
        ).Bind(usd_mat)

    # ------------------------------------------------------------------
    # Roof
    # ------------------------------------------------------------------

    def _add_roof(
        self,
        roof_type: str,
        boundary: list[tuple[float, float]],
        base_z: float,
    ) -> None:
        if roof_type == "gable":
            mesh_data = gable_roof_mesh(boundary, ridge_height=2.0, base_z=base_z)
        else:
            mesh_data = flat_roof_mesh(boundary, thickness=0.15, base_z=base_z)

        if len(mesh_data.vertices) == 0:
            return

        prim_path = "/Building/Roof"
        self._create_mesh_prim(prim_path, mesh_data)

        mat_def = roof_material(roof_type)
        usd_mat = self._get_or_create_material(mat_def)
        UsdShade.MaterialBindingAPI(
            self._stage.GetPrimAtPath(prim_path)
        ).Bind(usd_mat)

    # ------------------------------------------------------------------
    # Mesh helper
    # ------------------------------------------------------------------

    def _create_mesh_prim(self, prim_path: str, mesh_data: Mesh) -> UsdGeom.Mesh:
        usd_mesh = UsdGeom.Mesh.Define(self._stage, prim_path)

        points = [Gf.Vec3f(*v) for v in mesh_data.vertices]
        usd_mesh.GetPointsAttr().Set(Vt.Vec3fArray(points))

        # Each face is a triangle (3 vertices)
        face_counts = [3] * len(mesh_data.faces)
        usd_mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray(face_counts))

        indices = [int(i) for tri in mesh_data.faces for i in tri]
        usd_mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray(indices))

        # Compute and set face normals (flat shading)
        normals = _compute_face_normals(mesh_data)
        if normals:
            usd_mesh.GetNormalsAttr().Set(Vt.Vec3fArray(normals))
            usd_mesh.SetNormalsInterpolation(UsdGeom.Tokens.faceVarying)

        return usd_mesh

    # ------------------------------------------------------------------
    # Material
    # ------------------------------------------------------------------

    def _get_or_create_material(self, mat_def: MaterialDef) -> UsdShade.Material:
        safe = _safe_name(mat_def.name)
        if safe in self._material_cache:
            return self._material_cache[safe]

        mat_path = f"/Building/Materials/{safe}"
        usd_mat = UsdShade.Material.Define(self._stage, mat_path)

        shader_path = f"{mat_path}/PBRShader"
        shader = UsdShade.Shader.Define(self._stage, shader_path)
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
            Gf.Vec3f(*mat_def.color)
        )
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(
            mat_def.roughness
        )
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(
            mat_def.metallic
        )
        if mat_def.transparency > 0:
            shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(
                1.0 - mat_def.transparency
            )

        usd_mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")

        self._material_cache[safe] = usd_mat
        return usd_mat


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _compute_face_normals(mesh_data: Mesh) -> list[Gf.Vec3f]:
    """Compute per-face normals for a triangle mesh (flat shading)."""
    normals: list[Gf.Vec3f] = []
    for tri in mesh_data.faces:
        v0, v1, v2 = mesh_data.vertices[tri[0]], mesh_data.vertices[tri[1]], mesh_data.vertices[tri[2]]
        e1 = v1 - v0
        e2 = v2 - v0
        n = np.cross(e1, e2)
        length = np.linalg.norm(n)
        if length > 1e-10:
            n = n / length
        normal = Gf.Vec3f(float(n[0]), float(n[1]), float(n[2]))
        normals.extend([normal] * 3)  # one per vertex of the face (faceVarying)
    return normals


def _safe_name(name: str) -> str:
    """Convert a display name to a valid USD prim name."""
    result = name.replace(" ", "_").replace("-", "_").replace("/", "_")
    # USD prim names cannot start with a digit
    if result and result[0].isdigit():
        result = "F" + result
    return result
