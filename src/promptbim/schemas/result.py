"""Generation result data models."""

from pathlib import Path

from pydantic import BaseModel, Field


class GenerationResult(BaseModel):
    """Result of a building generation pipeline run."""

    success: bool = Field(default=False)
    building_name: str = Field(default="")
    ifc_path: Path | None = Field(default=None, description="Path to generated .ifc file")
    usd_path: Path | None = Field(default=None, description="Path to generated .usda file")
    summary: dict = Field(default_factory=dict, description="Building summary data")
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}
