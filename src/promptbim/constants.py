"""Project-wide named constants — replaces magic numbers (AuditReport M-1)."""

from __future__ import annotations

# Building defaults
DEFAULT_STORY_HEIGHT_M: float = 3.0
DEFAULT_WALL_THICKNESS_M: float = 0.2
DEFAULT_SLAB_THICKNESS_M: float = 0.2

# API token limits
API_MAX_TOKENS_DEFAULT: int = 4096
API_MAX_TOKENS_PLANNER: int = 8192

# GUI
GUI_STARTUP_DELAY_S: float = 1.0
