"""Shapefile land parcel parser."""

from __future__ import annotations

from pathlib import Path

from shapely.geometry import Polygon, shape

from promptbim.debug import get_logger
from promptbim.schemas.land import LandParcel

logger = get_logger("land.shapefile")


def parse_shapefile(file_path: str | Path) -> list[LandParcel]:
    """Parse a Shapefile (.shp) and return list of LandParcel objects."""
    import fiona

    file_path = Path(file_path)
    logger.debug("Loading Shapefile: %s", file_path)
    parcels: list[LandParcel] = []

    with fiona.open(file_path) as src:
        crs = src.crs.get("init", "EPSG:4326") if src.crs else "EPSG:4326"
        field_names = [f for f in src.schema.get("properties", {}).keys()]
        logger.debug(
            "Fields: %s, geometry_type=%s, CRS=%s", field_names, src.schema.get("geometry"), crs
        )

        for i, feature in enumerate(src):
            geom = shape(feature["geometry"])
            if not isinstance(geom, Polygon):
                continue

            props = feature.get("properties", {}) or {}
            coords = list(geom.exterior.coords[:-1])

            parcel = LandParcel(
                name=props.get("name", props.get("NAME", f"Parcel {i + 1}")),
                boundary=coords,
                area_sqm=geom.area,
                perimeter_m=geom.length,
                crs=crs,
                source_file=str(file_path),
                source_type="shapefile",
            )
            parcels.append(parcel)

    logger.debug("Parsed %d parcel(s) from Shapefile", len(parcels))
    return parcels
