"""Agent 1: Requirement Enhancer.

Takes a raw user prompt and enriches it into a structured
:class:`BuildingRequirement` with inferred building type, story count,
features, and constraints.
"""

from __future__ import annotations

import json
import logging

from promptbim.agents.base import AgentResponse, BaseAgent
from promptbim.schemas.land import LandParcel
from promptbim.schemas.requirement import BuildingRequirement
from promptbim.schemas.zoning import ZoningRules

logger = logging.getLogger(__name__)

ENHANCER_SYSTEM_PROMPT = """\
You are an expert architecture consultant. Your job is to take a user's
brief building description and enhance it into a detailed, structured
building requirement.

## INPUT
You receive:
1. User's raw prompt (could be vague, e.g. "3-story house with pool")
2. Land area in square meters
3. Zoning rules (FAR limit, BCR limit, height limit, setbacks)

## OUTPUT
Return a JSON object with exactly these fields:
{
  "building_type": "residential" | "commercial" | "industrial" | "mixed",
  "num_stories": <integer>,
  "total_area_sqm": <estimated total floor area>,
  "features": ["feature1", "feature2", ...],
  "constraints": ["constraint1", "constraint2", ...],
  "enhanced_description": "<detailed architectural description>"
}

## RULES
- Infer reasonable defaults for anything not specified
- num_stories must respect height_limit (assume 3m per story)
- total_area_sqm must not exceed land_area * FAR limit
- features should list specific architectural elements mentioned or implied
- constraints should include regulatory limits
- enhanced_description should be 2-4 sentences expanding the user's intent
- Return ONLY the JSON, no extra text
"""


class EnhancerAgent(BaseAgent):
    """Agent 1 — enriches a raw user prompt into a BuildingRequirement."""

    SYSTEM_PROMPT = ENHANCER_SYSTEM_PROMPT

    def enhance(
        self,
        raw_prompt: str,
        land: LandParcel | None = None,
        zoning: ZoningRules | None = None,
    ) -> BuildingRequirement:
        """Enhance *raw_prompt* using land/zoning context.

        Returns a :class:`BuildingRequirement`. Falls back to a basic
        requirement if the API call fails.
        """
        land_area = land.area_sqm if land else 500.0
        if zoning is None:
            zoning = ZoningRules()

        user_msg = (
            f"User prompt: {raw_prompt}\n\n"
            f"Land area: {land_area:.1f} m²\n"
            f"Zoning: FAR limit={zoning.far_limit}, BCR limit={zoning.bcr_limit}, "
            f"height limit={zoning.height_limit_m}m, "
            f"setbacks: front={zoning.setback_front_m}m, back={zoning.setback_back_m}m, "
            f"left={zoning.setback_left_m}m, right={zoning.setback_right_m}m"
        )

        response = self.run(user_msg)
        return self._to_requirement(raw_prompt, response, land_area, zoning)

    def _to_requirement(
        self,
        raw_prompt: str,
        response: AgentResponse,
        land_area: float,
        zoning: ZoningRules,
    ) -> BuildingRequirement:
        if response.ok and response.json_data:
            data = response.json_data
            max_stories = int(zoning.height_limit_m / 3.0)
            num_stories = min(data.get("num_stories", 1), max_stories)
            max_area = land_area * zoning.far_limit
            total_area = data.get("total_area_sqm")
            if total_area and total_area > max_area:
                total_area = max_area

            return BuildingRequirement(
                raw_prompt=raw_prompt,
                building_type=data.get("building_type", "residential"),
                num_stories=num_stories,
                total_area_sqm=total_area,
                features=data.get("features", []),
                constraints=data.get("constraints", []),
                enhanced_description=data.get("enhanced_description", raw_prompt),
            )

        # Fallback: basic requirement
        logger.warning("Enhancer fallback — using basic requirement")
        return BuildingRequirement(
            raw_prompt=raw_prompt,
            enhanced_description=raw_prompt,
        )
