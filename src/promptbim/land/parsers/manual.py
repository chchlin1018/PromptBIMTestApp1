"""Manual coordinate input parser."""

from __future__ import annotations

from shapely.geometry import Polygon

from promptbim.schemas.land import LandParcel


def parse_manual(
    coordinates: list[tuple[float, float]],
    name: str = "Manual Parcel",
    crs: str = "LOCAL",
) -> LandParcel:
    """Create a LandParcel from manually provided coordinates.

    Args:
        coordinates: List of (x, y) tuples defining the parcel boundary.
                     Must have at least 3 points. If the polygon is closed
                     (first == last), the closing point is removed.
        name: Name for the parcel.
        crs: Coordinate reference system string.
    """
    if len(coordinates) < 3:
        raise ValueError("At least 3 coordinate points are required")

    # Remove closing point if present
    if coordinates[0] == coordinates[-1]:
        coordinates = coordinates[:-1]

    if len(coordinates) < 3:
        raise ValueError("At least 3 unique coordinate points are required")

    poly = Polygon(coordinates)
    if not poly.is_valid:
        raise ValueError(f"Invalid polygon: {poly}")

    return LandParcel(
        name=name,
        boundary=coordinates,
        area_sqm=poly.area,
        perimeter_m=poly.length,
        crs=crs,
        source_type="manual",
    )
