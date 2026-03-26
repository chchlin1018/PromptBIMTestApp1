"""Generation result data models."""

from pathlib import Path

from pydantic import BaseModel, Field


class GenerationResult(BaseModel):
    """Result of a building generation pipeline run."""

    schema_version: str = Field(default="2.4.0", description="Schema version for compatibility checks")
    success: bool = Field(default=False)
    building_name: str = Field(default="")
    ifc_path: Path | None = Field(default=None, description="Path to generated .ifc file")
    usd_path: Path | None = Field(default=None, description="Path to generated .usda file")
    summary: dict = Field(default_factory=dict, description="Building summary data")
    compliance_report: dict = Field(
        default_factory=dict, description="Taiwan building code compliance report"
    )
    compliance_text: str = Field(default="", description="Human-readable compliance report")
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}
