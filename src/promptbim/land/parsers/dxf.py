"""DXF land parcel parser."""

from __future__ import annotations

from pathlib import Path

from shapely.geometry import Polygon

from promptbim.debug import get_logger
from promptbim.schemas.land import LandParcel

logger = get_logger("land.dxf")


def parse_dxf(file_path: str | Path) -> list[LandParcel]:
    """Parse a DXF file and extract closed polylines as land parcels."""
    import ezdxf

    file_path = Path(file_path)
    logger.debug("Loading DXF: %s", file_path)
    doc = ezdxf.readfile(str(file_path))
    msp = doc.modelspace()
    parcels: list[LandParcel] = []

    layers = set()
    entity_types: dict[str, int] = {}
    for e in msp:
        layers.add(e.dxf.layer)
        entity_types[e.dxftype()] = entity_types.get(e.dxftype(), 0) + 1
    logger.debug("Layers: %s", sorted(layers))
    logger.debug("Entity types: %s", entity_types)

    idx = 0
    for entity in msp:
        coords: list[tuple[float, float]] = []

        if entity.dxftype() == "LWPOLYLINE":
            coords = [(p[0], p[1]) for p in entity.get_points(format="xy")]
            if entity.closed and len(coords) >= 3:
                pass  # already good
            elif len(coords) >= 3 and coords[0] == coords[-1]:
                coords = coords[:-1]
            else:
                continue
        elif entity.dxftype() == "POLYLINE":
            coords = [(v.dxf.location.x, v.dxf.location.y) for v in entity.vertices]
            if len(coords) >= 3 and coords[0] == coords[-1]:
                coords = coords[:-1]
            elif entity.is_closed and len(coords) >= 3:
                pass
            else:
                continue
        else:
            continue

        if len(coords) < 3:
            continue

        poly = Polygon(coords)
        if not poly.is_valid or poly.area == 0:
            continue

        idx += 1
        parcels.append(
            LandParcel(
                name=f"Parcel {idx}",
                boundary=coords,
                area_sqm=poly.area,
                perimeter_m=poly.length,
                crs="LOCAL",
                source_file=str(file_path),
                source_type="dxf",
            )
        )

    logger.debug("Parsed %d parcel(s) from DXF", len(parcels))
    return parcels
