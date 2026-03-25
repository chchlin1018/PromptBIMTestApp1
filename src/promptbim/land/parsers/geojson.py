"""GeoJSON land parcel parser."""

from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import shape, Polygon

from promptbim.debug import get_logger
from promptbim.schemas.land import LandParcel

logger = get_logger("land.geojson")


def parse_geojson(file_path: str | Path) -> list[LandParcel]:
    """Parse a GeoJSON file and return list of LandParcel objects.

    Supports both FeatureCollection and single Feature/Geometry.
    """
    file_path = Path(file_path)
    logger.debug("Loading GeoJSON: %s", file_path)

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    features = _extract_features(data)
    logger.debug("Found %d feature(s)", len(features))
    parcels: list[LandParcel] = []

    for i, feature in enumerate(features):
        geom = shape(feature.get("geometry", feature))
        if not isinstance(geom, Polygon):
            logger.debug("Feature %d: skipped (type=%s, not Polygon)", i, geom.geom_type)
            continue

        props = feature.get("properties", {}) or {}
        coords = list(geom.exterior.coords[:-1])  # remove closing duplicate

        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        logger.debug(
            "Feature %d: type=Polygon, vertices=%d, X[%.4f, %.4f] Y[%.4f, %.4f]",
            i, len(coords), min(xs), max(xs), min(ys), max(ys),
        )

        parcel = LandParcel(
            name=props.get("name", props.get("NAME", f"Parcel {i + 1}")),
            boundary=coords,
            area_sqm=geom.area,
            perimeter_m=geom.length,
            crs="EPSG:4326",
            source_file=str(file_path),
            source_type="geojson",
        )
        parcels.append(parcel)

    logger.debug("Parsed %d parcel(s) from GeoJSON", len(parcels))
    return parcels


def _extract_features(data: dict) -> list[dict]:
    """Extract feature list from various GeoJSON structures."""
    if data.get("type") == "FeatureCollection":
        return data.get("features", [])
    elif data.get("type") == "Feature":
        return [data]
    elif data.get("type") in ("Polygon", "MultiPolygon"):
        return [{"geometry": data, "properties": {}}]
    return []
