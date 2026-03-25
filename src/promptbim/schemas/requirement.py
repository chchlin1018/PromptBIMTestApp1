"""Building requirement data models."""

from pydantic import BaseModel, Field


class BuildingRequirement(BaseModel):
    """User's building requirement, enhanced by Agent 1."""

    raw_prompt: str = Field(description="Original user prompt")
    building_type: str = Field(default="residential", description="Building type")
    num_stories: int = Field(default=1, description="Number of stories")
    total_area_sqm: float | None = Field(default=None, description="Target total area")
    features: list[str] = Field(default_factory=list, description="Requested features")
    constraints: list[str] = Field(default_factory=list, description="Design constraints")
    enhanced_description: str = Field(default="", description="AI-enhanced description")
