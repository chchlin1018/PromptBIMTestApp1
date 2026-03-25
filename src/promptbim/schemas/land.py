"""Land parcel data models."""

from pydantic import BaseModel, Field


class LandParcel(BaseModel):
    """A single land parcel with boundary and metadata."""

    name: str = "Untitled Parcel"
    boundary: list[tuple[float, float]] = Field(
        description="Land boundary coordinates [(x,y), ...] in meters"
    )
    area_sqm: float = Field(description="Area in square meters")
    perimeter_m: float = Field(default=0.0, description="Perimeter in meters")
    crs: str = Field(default="EPSG:4326", description="Coordinate reference system")
    local_origin: tuple[float, float] = Field(
        default=(0.0, 0.0), description="Local coordinate origin"
    )
    source_file: str | None = Field(default=None, description="Source file path")
    source_type: str = Field(
        default="manual",
        description="Source type: shapefile/geojson/kml/dxf/pdf/manual",
    )

    model_config = {"arbitrary_types_allowed": True}
