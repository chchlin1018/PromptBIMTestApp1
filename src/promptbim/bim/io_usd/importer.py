"""USD Importer with ILOS metadata extraction.

Reads USD files and extracts:
- Mesh geometry (vertices, faces)
- ILOS attributes (category, part_number, manufacturer)
- Connection ports (/Connections/ prims)
- Instance transforms (final_xf = inst_xf × proto_inv × mesh_xf)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class ILOSMetadata:
    """ILOS-specific metadata from USD prim."""
    category: str = ""
    part_number: str = ""
    manufacturer: str = ""
    description: str = ""


@dataclass
class ConnectionPort:
    """ILOS connection port data."""
    name: str = ""
    port_type: str = ""
    port_medium: str = ""
    port_size_mm: float = 0.0
    port_direction: str = ""
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class USDElement:
    """A mesh element imported from USD."""
    path: str = ""
    name: str = ""
    vertices: np.ndarray = field(default_factory=lambda: np.empty((0, 3)))
    faces: np.ndarray = field(default_factory=lambda: np.empty((0, 3), dtype=np.int32))
    transform: np.ndarray = field(default_factory=lambda: np.eye(4))
    ilos: ILOSMetadata = field(default_factory=ILOSMetadata)
    connections: list[ConnectionPort] = field(default_factory=list)
    material: str = "default"

    def to_json(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict for C++ bridge."""
        return {
            "id": self.name,
            "path": self.path,
            "type": self.ilos.category or "mesh",
            "material": self.material,
            "vertices": self.vertices.tolist(),
            "indices": self.faces.tolist(),
            "ilos": {
                "category": self.ilos.category,
                "part_number": self.ilos.part_number,
                "manufacturer": self.ilos.manufacturer,
                "description": self.ilos.description,
            },
            "connections": [
                {
                    "name": c.name,
                    "port_type": c.port_type,
                    "port_medium": c.port_medium,
                    "port_size_mm": c.port_size_mm,
                    "port_direction": c.port_direction,
                }
                for c in self.connections
            ],
        }


class USDImporter:
    """Import USD files with ILOS metadata."""

    def __init__(self) -> None:
        self._elements: list[USDElement] = []

    @property
    def elements(self) -> list[USDElement]:
        return self._elements

    def load(self, usd_path: str | Path) -> list[USDElement]:
        """Load a USD file and extract all mesh elements with ILOS metadata."""
        from pxr import Usd, UsdGeom

        usd_path = Path(usd_path)
        if not usd_path.exists():
            raise FileNotFoundError(f"USD file not found: {usd_path}")

        stage = Usd.Stage.Open(str(usd_path))
        self._elements = []

        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                elem = self._extract_mesh(prim, stage)
                if elem:
                    self._elements.append(elem)

        return self._elements

    def _extract_mesh(self, prim, stage) -> USDElement | None:
        """Extract mesh data and metadata from a USD Mesh prim."""
        from pxr import UsdGeom, Gf

        mesh = UsdGeom.Mesh(prim)

        # Get points
        points_attr = mesh.GetPointsAttr()
        if not points_attr:
            return None
        points = points_attr.Get()
        if not points:
            return None

        vertices = np.array([[p[0], p[1], p[2]] for p in points], dtype=np.float64)

        # Get face indices
        face_counts = mesh.GetFaceVertexCountsAttr().Get() or []
        face_indices = mesh.GetFaceVertexIndicesAttr().Get() or []

        faces = []
        idx = 0
        for count in face_counts:
            if count == 3:
                faces.append([face_indices[idx], face_indices[idx + 1], face_indices[idx + 2]])
            elif count == 4:
                # Triangulate quad
                faces.append([face_indices[idx], face_indices[idx + 1], face_indices[idx + 2]])
                faces.append([face_indices[idx], face_indices[idx + 2], face_indices[idx + 3]])
            idx += count

        face_array = np.array(faces, dtype=np.int32) if faces else np.empty((0, 3), dtype=np.int32)

        # Get transform
        xformable = UsdGeom.Xformable(prim)
        xf_matrix = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
        transform = np.array(xf_matrix, dtype=np.float64)

        # Apply transform to vertices
        if not np.allclose(transform, np.eye(4)):
            ones = np.ones((vertices.shape[0], 1))
            homogeneous = np.hstack([vertices, ones])
            transformed = (transform @ homogeneous.T).T
            vertices = transformed[:, :3]

        # Extract ILOS metadata
        ilos = self._extract_ilos(prim)

        # Extract connections
        connections = self._extract_connections(prim)

        return USDElement(
            path=str(prim.GetPath()),
            name=prim.GetName(),
            vertices=vertices,
            faces=face_array,
            transform=transform,
            ilos=ilos,
            connections=connections,
        )

    def _extract_ilos(self, prim) -> ILOSMetadata:
        """Extract ILOS attributes (ilos:category, ilos:part_number, etc.)."""
        meta = ILOSMetadata()

        for attr in prim.GetAttributes():
            name = attr.GetName()
            if name.startswith("ilos:"):
                key = name[5:]  # strip "ilos:" prefix
                value = attr.Get()
                if value is None:
                    continue
                value = str(value)
                if key == "category":
                    meta.category = value
                elif key == "part_number":
                    meta.part_number = value
                elif key == "manufacturer":
                    meta.manufacturer = value
                elif key == "description":
                    meta.description = value

        return meta

    def _extract_connections(self, prim) -> list[ConnectionPort]:
        """Extract /Connections/ child prims for port data."""
        connections = []

        for child in prim.GetChildren():
            if "Connection" in child.GetName() or "port" in child.GetName().lower():
                port = ConnectionPort(name=child.GetName())

                for attr in child.GetAttributes():
                    name = attr.GetName()
                    value = attr.Get()
                    if value is None:
                        continue
                    if "port_type" in name:
                        port.port_type = str(value)
                    elif "port_medium" in name:
                        port.port_medium = str(value)
                    elif "port_size" in name:
                        port.port_size_mm = float(value)
                    elif "port_direction" in name:
                        port.port_direction = str(value)

                connections.append(port)

        return connections

    def to_json(self) -> dict:
        """Export all elements to JSON for C++ bridge."""
        return {
            "elements": [e.to_json() for e in self._elements],
            "element_count": len(self._elements),
        }
