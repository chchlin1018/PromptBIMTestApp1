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
        description="Source type: shapefile/geojson/kml/dxf/pdf/manual/ai_image",
    )
    ai_confidence: float | None = Field(
        default=None, description="AI recognition confidence (0.0~1.0)"
    )
    original_image_path: str | None = Field(
        default=None, description="Path to original image (for ai_image source)"
    )
    ai_annotations: dict | None = Field(
        default=None, description="AI-extracted annotations (lot_number, dimensions, etc.)"
    )

    model_config = {"arbitrary_types_allowed": True}
