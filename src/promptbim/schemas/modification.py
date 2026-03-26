"""Modification engine data models — version history and impact tracking."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ModificationType(str, Enum):
    """Types of modifications that can be applied to a building plan."""

    STORIES = "stories"
    HEIGHT = "height"
    FOOTPRINT = "footprint"
    ROOMS = "rooms"
    ROOF = "roof"
    MATERIALS = "materials"
    OPENINGS = "openings"
    GENERAL = "general"


class ImpactLevel(str, Enum):
    """How severely a component is affected by a modification."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ImpactItem(BaseModel):
    """A single affected component from a modification."""

    component: str = Field(description="Affected component name")
    level: ImpactLevel = Field(default=ImpactLevel.LOW)
    description: str = Field(default="", description="What changed")
    before_value: str = Field(default="")
    after_value: str = Field(default="")


class ModificationIntent(BaseModel):
    """Parsed modification intent from user's natural language command."""

    raw_command: str = Field(description="Original user command")
    modification_type: ModificationType = Field(default=ModificationType.GENERAL)
    parameters: dict = Field(default_factory=dict, description="Extracted parameters")
    confidence: float = Field(default=0.0, description="AI confidence 0-1")


class ModificationRecord(BaseModel):
    """A single modification event in the version history."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    command: str = Field(description="User's modification command")
    intent: ModificationIntent | None = Field(default=None)
    impacts: list[ImpactItem] = Field(default_factory=list)
    plan_snapshot_json: dict = Field(
        default_factory=dict, description="BuildingPlan JSON before this change"
    )
    success: bool = Field(default=True)
    error: str | None = Field(default=None)


class ModificationHistory(BaseModel):
    """Full version history of modifications to a building plan."""

    records: list[ModificationRecord] = Field(default_factory=list)

    @property
    def can_undo(self) -> bool:
        return len(self.records) > 0

    @property
    def latest(self) -> ModificationRecord | None:
        return self.records[-1] if self.records else None

    def add(self, record: ModificationRecord) -> None:
        self.records.append(record)

    def pop_last(self) -> ModificationRecord | None:
        """Remove and return the last record (for undo)."""
        if self.records:
            return self.records.pop()
        return None
