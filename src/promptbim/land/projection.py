"""Coordinate projection utilities using pyproj."""

from __future__ import annotations

from pyproj import Transformer

from promptbim.debug import get_logger
from promptbim.schemas.land import LandParcel

logger = get_logger("land.projection")


def to_local_meters(parcel: LandParcel, target_crs: str = "EPSG:3826") -> LandParcel:
    """Convert parcel coordinates from WGS84 to a local meter-based CRS.

    Default target is EPSG:3826 (TWD97 / TM2 zone 121) for Taiwan.
    For other regions, pass appropriate projected CRS.

    Returns a new LandParcel with coordinates in meters and updated CRS.
    """
    logger.debug("Projecting: source=%s -> target=%s", parcel.crs, target_crs)
    if parcel.crs == target_crs or parcel.crs == "LOCAL":
        logger.debug("No projection needed (already %s)", parcel.crs)
        return parcel

    transformer = Transformer.from_crs(parcel.crs, target_crs, always_xy=True)

    transformed_coords = []
    for x, y in parcel.boundary:
        tx, ty = transformer.transform(x, y)
        transformed_coords.append((tx, ty))

    # Set local origin to the centroid of transformed coords
    if transformed_coords:
        cx = sum(p[0] for p in transformed_coords) / len(transformed_coords)
        cy = sum(p[1] for p in transformed_coords) / len(transformed_coords)
        local_coords = [(x - cx, y - cy) for x, y in transformed_coords]
        local_origin = (cx, cy)
    else:
        local_coords = transformed_coords
        local_origin = (0.0, 0.0)

    from shapely.geometry import Polygon

    poly = Polygon(local_coords)

    logger.debug(
        "Projected %d coords: before=(%.4f,%.4f), after=(%.4f,%.4f), origin=(%.2f,%.2f)",
        len(parcel.boundary),
        parcel.boundary[0][0], parcel.boundary[0][1],
        local_coords[0][0], local_coords[0][1],
        local_origin[0], local_origin[1],
    )

    return LandParcel(
        name=parcel.name,
        boundary=local_coords,
        area_sqm=poly.area,
        perimeter_m=poly.length,
        crs=target_crs,
        local_origin=local_origin,
        source_file=parcel.source_file,
        source_type=parcel.source_type,
    )


def reproject_coords(
    coords: list[tuple[float, float]],
    source_crs: str,
    target_crs: str,
) -> list[tuple[float, float]]:
    """Reproject a list of (x, y) coordinates between CRS."""
    if source_crs == target_crs:
        return coords

    transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    return [transformer.transform(x, y) for x, y in coords]
