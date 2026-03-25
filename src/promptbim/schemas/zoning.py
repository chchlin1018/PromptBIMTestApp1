"""Zoning rules data models."""

from pydantic import BaseModel, Field


class ZoningRules(BaseModel):
    """Land use zoning rules and constraints."""

    zone_type: str = Field(default="residential", description="residential/commercial/industrial")
    far_limit: float = Field(default=2.0, description="Floor Area Ratio limit")
    bcr_limit: float = Field(default=0.6, description="Building Coverage Ratio limit")
    height_limit_m: float = Field(default=15.0, description="Height limit in meters")
    setback_front_m: float = Field(default=5.0, description="Front setback in meters")
    setback_back_m: float = Field(default=3.0, description="Back setback in meters")
    setback_left_m: float = Field(default=2.0, description="Left setback in meters")
    setback_right_m: float = Field(default=2.0, description="Right setback in meters")
    min_parking_per_unit: float = Field(default=1.0, description="Minimum parking per unit")
