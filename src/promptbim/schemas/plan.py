"""Building plan data models — Agent 2 (Planner) output."""

from pydantic import BaseModel, Field


class WallDef(BaseModel):
    """A wall segment defined by start/end points."""

    start: tuple[float, float]
    end: tuple[float, float]
    thickness_m: float = 0.2
    wall_type: str = Field(default="exterior", description="exterior/interior/partition")


class SpaceDef(BaseModel):
    """A named space/room within a story."""

    name: str
    boundary: list[tuple[float, float]]
    space_type: str = Field(description="living/bedroom/office/meeting/corridor/bathroom")
    area_sqm: float


class OpeningDef(BaseModel):
    """A door or window opening in a wall."""

    wall_index: int
    offset_m: float = Field(description="Offset along wall from start point")
    width_m: float
    height_m: float
    sill_height_m: float = Field(default=0.0, description="Sill height (door=0, window=0.9)")
    opening_type: str = Field(default="door", description="door/window")


class RoofPlan(BaseModel):
    """Roof configuration."""

    roof_type: str = Field(default="flat", description="flat/gable/hip")
    slope_degrees: float = Field(default=0.0)
    overhang_m: float = Field(default=0.3)


class StoryPlan(BaseModel):
    """A single story/floor plan."""

    name: str = Field(description="Floor name: 1F, 2F, B1, etc.")
    elevation_m: float = Field(description="Floor elevation above ground")
    height_m: float = Field(default=3.0, description="Story height")
    walls: list[WallDef] = Field(default_factory=list)
    spaces: list[SpaceDef] = Field(default_factory=list)
    openings: list[OpeningDef] = Field(default_factory=list)
    slab_boundary: list[tuple[float, float]] = Field(default_factory=list)


class BuildingPlan(BaseModel):
    """Complete building plan placed on a land parcel."""

    name: str
    land_boundary: list[tuple[float, float]] = Field(default_factory=list)
    buildable_area: list[tuple[float, float]] = Field(default_factory=list)
    building_footprint: list[tuple[float, float]] = Field(default_factory=list)
    building_bcr: float = Field(default=0.0, description="Actual BCR")
    building_far: float = Field(default=0.0, description="Actual FAR")
    stories: list[StoryPlan] = Field(default_factory=list)
    roof: RoofPlan = Field(default_factory=RoofPlan)
