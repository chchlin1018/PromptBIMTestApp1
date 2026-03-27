"""USD file generator using pxr (OpenUSD).

Only ``pxr.Usd``, ``pxr.UsdGeom``, and ``pxr.UsdShade`` are used.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, Vt

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
from promptbim.debug import get_logger
from promptbim.schemas.plan import BuildingPlan, StoryPlan, WallDef

_logger = get_logger("bim.usd")


class USDGenerator:
    """Build an OpenUSD stage from a :class:`BuildingPlan`.

    D1-S1 additions:
    - Phase tags: each prim receives ``custom:construction_phase_id`` and
      ``custom:construction_phase_name`` attributes when a schedule is provided.
    - MEP layer: pipes and ducts are generated under ``/Building/MEP/``.
    """

    def __init__(self) -> None:
        self._stage: Usd.Stage | None = None
        self._material_cache: dict[str, UsdShade.Material] = {}
        # D1-S1: phase mapping — prim_path → phase_id (built from schedule)
        self._phase_map: dict[str, tuple[str, str]] = {}  # prim_label → (phase_id, phase_name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        plan: BuildingPlan,
        output_path: str | Path,
        schedule=None,  # ConstructionSchedule | None (D1-S1)
        include_mep: bool = True,  # D1-S1
    ) -> Path:
        """Generate a ``.usda`` file from *plan*.

        Args:
            plan: BuildingPlan to convert.
            output_path: Destination .usda path.
            schedule: Optional ConstructionSchedule for phase tagging (D1-S1).
            include_mep: Whether to add MEP layer (D1-S1, default True).
        """
        import time as _time

        _t0 = _time.time()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self._stage = Usd.Stage.CreateNew(str(output_path))
        self._material_cache.clear()
        self._phase_map.clear()

        UsdGeom.SetStageUpAxis(self._stage, UsdGeom.Tokens.z)
        UsdGeom.SetStageMetersPerUnit(self._stage, 1.0)

        root = UsdGeom.Xform.Define(self._stage, "/Building")
        root.GetPrim().SetMetadata("kind", "assembly")

        # D1-S1: build phase map from schedule
        if schedule is not None:
            self._build_phase_map(schedule)

        # Pre-warm material cache to avoid per-element lookups
        self._prewarm_materials(plan)

        for story in plan.stories:
            self._add_story(story, plan)

        # Roof
        if plan.stories:
            top = plan.stories[-1]
            roof_z = top.elevation_m + top.height_m
            boundary = plan.building_footprint or top.slab_boundary
            if boundary:
                self._add_roof(plan.roof.roof_type, boundary, roof_z)

        # D1-S1: MEP layer
        if include_mep and plan.stories:
            self._add_mep_layer(plan)

        self._stage.GetRootLayer().Save()
        _elapsed = _time.time() - _t0

        mat_count = len(self._material_cache)
        file_size = output_path.stat().st_size / 1024
        _logger.debug(
            "USD written: %s (%d materials, %.0f KB, %.2fs)",
            output_path,
            mat_count,
            file_size,
            _elapsed,
        )
        return output_path

    # ------------------------------------------------------------------
    # D1-S1: Phase map + tagging helpers
    # ------------------------------------------------------------------

    def _build_phase_map(self, schedule) -> None:
        """Build label→(phase_id, phase_name) from a ConstructionSchedule."""
        for sp in schedule.phases:
            phase_id = sp.phase.phase_id
            phase_name = sp.phase.name
            for label in sp.components:
                self._phase_map[label] = (phase_id, phase_name)

    def _tag_phase(self, prim_path: str, label: str) -> None:
        """Attach construction phase custom attributes to a prim (D1-S1)."""
        if not self._phase_map or label not in self._phase_map:
            return
        phase_id, phase_name = self._phase_map[label]
        prim = self._stage.GetPrimAtPath(prim_path)
        if not prim:
            return
        prim.CreateAttribute("custom:construction_phase_id", Sdf.ValueTypeNames.String).Set(phase_id)
        prim.CreateAttribute("custom:construction_phase_name", Sdf.ValueTypeNames.String).Set(phase_name)

    # ------------------------------------------------------------------
    # D1-S1: MEP Layer
    # ------------------------------------------------------------------

    def _add_mep_layer(self, plan: BuildingPlan) -> None:
        """Add simplified MEP geometry layer under /Building/MEP.

        Creates:
        - /Building/MEP/HVAC: duct stubs (rectangular tubes along building spine)
        - /Building/MEP/Plumbing: pipe stubs (cylinders along service core)
        - /Building/MEP/Electrical: conduit stubs

        Geometry is schematic (not construction-level detail).
        """
        mep_path = "/Building/MEP"
        UsdGeom.Xform.Define(self._stage, mep_path)
        UsdGeom.Xform.Define(self._stage, f"{mep_path}/HVAC")
        UsdGeom.Xform.Define(self._stage, f"{mep_path}/Plumbing")
        UsdGeom.Xform.Define(self._stage, f"{mep_path}/Electrical")

        if not plan.building_footprint:
            return

        # Centroid of building footprint
        fp = plan.building_footprint
        cx = sum(p[0] for p in fp) / len(fp)
        cy = sum(p[1] for p in fp) / len(fp)

        for story in plan.stories:
            floor_z = story.elevation_m + story.height_m * 0.85  # near ceiling
            sn = _safe_name(story.name)

            # HVAC duct: a flat box spanning building width at ceiling level
            fp_pts = story.slab_boundary or plan.building_footprint
            if fp_pts:
                xs = [p[0] for p in fp_pts]
                ys = [p[1] for p in fp_pts]
                duct_x0, duct_x1 = min(xs), max(xs)
                duct_y = cy
                duct_w = duct_x1 - duct_x0
                duct_mesh = _box_mesh(
                    x=duct_x0, y=duct_y - 0.15, z=floor_z,
                    w=duct_w, d=0.3, h=0.25,
                )
                hvac_path = f"{mep_path}/HVAC/{sn}_MainDuct"
                self._create_mesh_prim(hvac_path, duct_mesh)
                p = self._stage.GetPrimAtPath(hvac_path)
                if p:
                    p.CreateAttribute("custom:mep_type", Sdf.ValueTypeNames.String).Set("HVAC_duct")
                    p.CreateAttribute("custom:story", Sdf.ValueTypeNames.String).Set(story.name)

                # Plumbing riser: vertical cylinder at service core
                riser_mesh = _cylinder_mesh(cx=cx, cy=cy, z0=story.elevation_m, z1=story.elevation_m + story.height_m, radius=0.05)
                plumb_path = f"{mep_path}/Plumbing/{sn}_Riser"
                self._create_mesh_prim(plumb_path, riser_mesh)
                p = self._stage.GetPrimAtPath(plumb_path)
                if p:
                    p.CreateAttribute("custom:mep_type", Sdf.ValueTypeNames.String).Set("plumbing_riser")
                    p.CreateAttribute("custom:story", Sdf.ValueTypeNames.String).Set(story.name)

                # Electrical conduit: thin horizontal line above duct
                conduit_mesh = _box_mesh(
                    x=duct_x0, y=duct_y - 0.03, z=floor_z + 0.3,
                    w=duct_w, d=0.06, h=0.06,
                )
                elec_path = f"{mep_path}/Electrical/{sn}_Conduit"
                self._create_mesh_prim(elec_path, conduit_mesh)
                p = self._stage.GetPrimAtPath(elec_path)
                if p:
                    p.CreateAttribute("custom:mep_type", Sdf.ValueTypeNames.String).Set("electrical_conduit")
                    p.CreateAttribute("custom:story", Sdf.ValueTypeNames.String).Set(story.name)

        _logger.debug("MEP layer added: HVAC + Plumbing + Electrical (%d stories)", len(plan.stories))

    def _prewarm_materials(self, plan: BuildingPlan) -> None:
        """Pre-create all materials used in the plan."""
        wall_types = {w.wall_type for s in plan.stories for w in s.walls}
        for wt in wall_types:
            self._get_or_create_material(wall_material(wt))
        self._get_or_create_material(slab_material())
        self._get_or_create_material(roof_material(plan.roof.roof_type))

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

    def _add_wall(self, wall_def: WallDef, story: StoryPlan, parent_path: str, idx: int) -> None:
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
        UsdShade.MaterialBindingAPI(self._stage.GetPrimAtPath(prim_path)).Bind(usd_mat)

        # D1-S1: phase tag
        label = f"{story.name}_wall_{idx}"
        self._tag_phase(prim_path, label)

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
        UsdShade.MaterialBindingAPI(self._stage.GetPrimAtPath(prim_path)).Bind(usd_mat)

        # D1-S1: phase tag
        label = f"{story.name}_slab_0"
        self._tag_phase(prim_path, label)

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
        UsdShade.MaterialBindingAPI(self._stage.GetPrimAtPath(prim_path)).Bind(usd_mat)

    # ------------------------------------------------------------------
    # Mesh helper
    # ------------------------------------------------------------------

    def _create_mesh_prim(self, prim_path: str, mesh_data: Mesh) -> UsdGeom.Mesh:
        usd_mesh = UsdGeom.Mesh.Define(self._stage, prim_path)

        points = [Gf.Vec3f(float(v[0]), float(v[1]), float(v[2])) for v in mesh_data.vertices]
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
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*mat_def.color))
        shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(mat_def.roughness)
        shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(mat_def.metallic)
        if mat_def.transparency > 0:
            shader.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(1.0 - mat_def.transparency)

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
        v0, v1, v2 = (
            mesh_data.vertices[tri[0]],
            mesh_data.vertices[tri[1]],
            mesh_data.vertices[tri[2]],
        )
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


def _box_mesh(x: float, y: float, z: float, w: float, d: float, h: float) -> Mesh:
    """Create a simple box mesh for MEP geometry (D1-S1).

    Args:
        x, y, z: corner origin
        w, d, h: width (x), depth (y), height (z)
    """
    verts = np.array([
        [x,     y,     z    ], [x + w, y,     z    ],
        [x + w, y + d, z    ], [x,     y + d, z    ],
        [x,     y,     z + h], [x + w, y,     z + h],
        [x + w, y + d, z + h], [x,     y + d, z + h],
    ], dtype=np.float32)
    faces = np.array([
        [0,1,2],[0,2,3],  # bottom
        [4,6,5],[4,7,6],  # top
        [0,5,1],[0,4,5],  # front
        [1,6,2],[1,5,6],  # right
        [2,7,3],[2,6,7],  # back
        [3,4,0],[3,7,4],  # left
    ], dtype=np.int32)
    return Mesh(vertices=verts, faces=faces)


def _cylinder_mesh(cx: float, cy: float, z0: float, z1: float, radius: float, segments: int = 8) -> Mesh:
    """Create a vertical cylinder mesh for plumbing risers (D1-S1)."""
    import math
    angles = [2 * math.pi * i / segments for i in range(segments)]
    bottom = [(cx + radius * math.cos(a), cy + radius * math.sin(a), z0) for a in angles]
    top = [(cx + radius * math.cos(a), cy + radius * math.sin(a), z1) for a in angles]

    verts = np.array(bottom + top, dtype=np.float32)
    faces = []
    for i in range(segments):
        j = (i + 1) % segments
        # Side quad → 2 tris
        faces.append([i, j, segments + j])
        faces.append([i, segments + j, segments + i])
    # Cap triangles (fan from center — add center verts)
    bc_idx = len(verts)
    tc_idx = bc_idx + 1
    verts = np.vstack([verts, [[cx, cy, z0], [cx, cy, z1]]])
    for i in range(segments):
        j = (i + 1) % segments
        faces.append([bc_idx, j, i])
        faces.append([tc_idx, segments + i, segments + j])

    return Mesh(vertices=verts, faces=np.array(faces, dtype=np.int32))
