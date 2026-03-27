"""Agent 5: Modifier — analyzes modification intent and applies incremental updates.

Parses natural language commands like "change to 9 stories" and returns
a :class:`ModificationIntent` plus computes the impact propagation.
Uses Claude to parse intent, but applies changes deterministically.
"""

from __future__ import annotations

from promptbim.agents.base import BaseAgent
from promptbim.bim.geometry import poly_area
from promptbim.debug import get_logger
from promptbim.schemas.modification import (
    ImpactItem,
    ImpactLevel,
    ModificationHistory,
    ModificationIntent,
    ModificationRecord,
    ModificationType,
)
from promptbim.schemas.plan import (
    BuildingPlan,
    RoofPlan,
    StoryPlan,
)
from promptbim.schemas.zoning import ZoningRules

logger = get_logger("agents.modifier")

# ---------------------------------------------------------------------------
# Impact propagation matrix
# ---------------------------------------------------------------------------

# When a modification type changes, these components are affected.
IMPACT_MATRIX: dict[ModificationType, list[tuple[str, ImpactLevel]]] = {
    ModificationType.STORIES: [
        ("structure", ImpactLevel.HIGH),
        ("elevator", ImpactLevel.HIGH),
        ("stairs", ImpactLevel.HIGH),
        ("FAR", ImpactLevel.HIGH),
        ("height", ImpactLevel.HIGH),
        ("cost", ImpactLevel.HIGH),
        ("MEP_vertical", ImpactLevel.MEDIUM),
        ("seismic", ImpactLevel.MEDIUM),
        ("fire_egress", ImpactLevel.MEDIUM),
        ("parking", ImpactLevel.LOW),
        ("roof", ImpactLevel.LOW),
    ],
    ModificationType.HEIGHT: [
        ("structure", ImpactLevel.MEDIUM),
        ("height_limit", ImpactLevel.HIGH),
        ("MEP_vertical", ImpactLevel.LOW),
        ("cost", ImpactLevel.LOW),
    ],
    ModificationType.FOOTPRINT: [
        ("BCR", ImpactLevel.HIGH),
        ("FAR", ImpactLevel.HIGH),
        ("structure", ImpactLevel.HIGH),
        ("setback", ImpactLevel.HIGH),
        ("cost", ImpactLevel.MEDIUM),
        ("parking", ImpactLevel.MEDIUM),
        ("MEP_horizontal", ImpactLevel.MEDIUM),
    ],
    ModificationType.ROOMS: [
        ("interior_walls", ImpactLevel.MEDIUM),
        ("openings", ImpactLevel.LOW),
        ("MEP_horizontal", ImpactLevel.LOW),
        ("cost", ImpactLevel.LOW),
    ],
    ModificationType.ROOF: [
        ("roof", ImpactLevel.HIGH),
        ("cost", ImpactLevel.LOW),
    ],
    ModificationType.MATERIALS: [
        ("facade", ImpactLevel.MEDIUM),
        ("cost", ImpactLevel.LOW),
    ],
    ModificationType.OPENINGS: [
        ("openings", ImpactLevel.MEDIUM),
        ("facade", ImpactLevel.LOW),
    ],
    ModificationType.GENERAL: [
        ("structure", ImpactLevel.MEDIUM),
        ("cost", ImpactLevel.MEDIUM),
    ],
}


def compute_impacts(
    mod_type: ModificationType,
    old_plan: BuildingPlan,
    new_plan: BuildingPlan,
) -> list[ImpactItem]:
    """Compute impact items by comparing old and new plans."""
    base_impacts = IMPACT_MATRIX.get(mod_type, IMPACT_MATRIX[ModificationType.GENERAL])
    items: list[ImpactItem] = []

    for component, level in base_impacts:
        before, after, desc = _diff_component(component, old_plan, new_plan)
        if before != after:
            items.append(
                ImpactItem(
                    component=component,
                    level=level,
                    description=desc,
                    before_value=str(before),
                    after_value=str(after),
                )
            )

    return items


def _diff_component(
    component: str,
    old: BuildingPlan,
    new: BuildingPlan,
) -> tuple[str, str, str]:
    """Return (before, after, description) for a component."""
    if component in ("structure", "elevator", "stairs", "height"):
        return (
            str(len(old.stories)),
            str(len(new.stories)),
            f"Stories: {len(old.stories)} → {len(new.stories)}",
        )
    if component == "FAR":
        return (
            f"{old.building_far:.2f}",
            f"{new.building_far:.2f}",
            f"FAR: {old.building_far:.2f} → {new.building_far:.2f}",
        )
    if component == "BCR":
        return (
            f"{old.building_bcr:.2f}",
            f"{new.building_bcr:.2f}",
            f"BCR: {old.building_bcr:.2f} → {new.building_bcr:.2f}",
        )
    if component == "height_limit":
        old_h = sum(s.height_m for s in old.stories)
        new_h = sum(s.height_m for s in new.stories)
        return (f"{old_h:.1f}m", f"{new_h:.1f}m", f"Total height: {old_h:.1f}m → {new_h:.1f}m")
    if component == "roof":
        return (
            old.roof.roof_type,
            new.roof.roof_type,
            f"Roof: {old.roof.roof_type} → {new.roof.roof_type}",
        )
    if component == "cost":
        old_area = sum(s.slab_boundary and poly_area(s.slab_boundary) or 0 for s in old.stories)
        new_area = sum(s.slab_boundary and poly_area(s.slab_boundary) or 0 for s in new.stories)
        return (
            f"{old_area:.0f}m²",
            f"{new_area:.0f}m²",
            f"Total area: {old_area:.0f} → {new_area:.0f} m²",
        )
    # Default: no meaningful diff
    return ("—", "—", component)


# _poly_area moved to bim.geometry.poly_area — keep backward compat alias
_poly_area = poly_area


# ---------------------------------------------------------------------------
# Modifier Agent (uses Claude to parse intent)
# ---------------------------------------------------------------------------

MODIFIER_SYSTEM_PROMPT = """\
You are a building modification intent parser. Given a user's modification
command about an existing building plan, extract the intent.

## INPUT
You receive:
1. The user's modification command (natural language)
2. Current building summary (stories, BCR, FAR, footprint area)

## OUTPUT
Return a JSON object:
{
  "modification_type": "stories" | "height" | "footprint" | "rooms" | "roof" | "materials" | "openings" | "general",
  "parameters": {
    // For "stories": {"target_stories": <int>}
    // For "height": {"story_height_m": <float>}
    // For "footprint": {"scale_factor": <float>} or {"target_area_sqm": <float>}
    // For "roof": {"roof_type": "flat"|"gable"|"hip", "slope_degrees": <float>}
    // For "rooms": {"add_rooms": [...], "remove_rooms": [...]}
    // For "general": free-form key-value pairs
  },
  "confidence": <float 0-1>
}

Return ONLY the JSON, no extra text.
"""


class ModifierAgent(BaseAgent):
    """Agent 5 — parses modification intent and applies incremental changes.

    D1-S1 Enhancement: Multi-round cumulative change tracking.
    - batch_modify(): apply a list of commands sequentially
    - get_cumulative_delta(): summarize all changes vs. original baseline
    - _original_snapshot: baseline plan stored on first modify call
    """

    SYSTEM_PROMPT = MODIFIER_SYSTEM_PROMPT

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._history = ModificationHistory()
        self._original_snapshot: dict | None = None  # baseline for cumulative delta

    @property
    def history(self) -> ModificationHistory:
        return self._history

    def modify(
        self,
        command: str,
        current_plan: BuildingPlan,
        zoning: ZoningRules | None = None,
    ) -> tuple[BuildingPlan, ModificationRecord]:
        """Apply a modification command to *current_plan*.

        Returns (new_plan, record). The record contains impact analysis
        and a snapshot of the plan before the change (for undo).
        """
        if zoning is None:
            zoning = ZoningRules()

        # Store original baseline on first modify
        if self._original_snapshot is None:
            self._original_snapshot = current_plan.model_dump()

        # Snapshot before
        old_snapshot = current_plan.model_dump()

        # Parse intent via Claude
        logger.debug("Parsing modification: '%s'", command)
        intent = self._parse_intent(command, current_plan)
        logger.debug(
            "Intent: type=%s, params=%s, confidence=%.2f",
            intent.modification_type.value,
            intent.parameters,
            intent.confidence,
        )

        # Apply modification deterministically
        try:
            new_plan = self._apply(intent, current_plan, zoning)
            impacts = compute_impacts(intent.modification_type, current_plan, new_plan)
            record = ModificationRecord(
                command=command,
                intent=intent,
                impacts=impacts,
                plan_snapshot_json=old_snapshot,
                success=True,
            )
        except Exception as exc:
            logger.exception("Modification failed")
            new_plan = current_plan
            record = ModificationRecord(
                command=command,
                intent=intent,
                plan_snapshot_json=old_snapshot,
                success=False,
                error=str(exc),
            )

        self._history.add(record)
        return new_plan, record

    def batch_modify(
        self,
        commands: list[str],
        current_plan: BuildingPlan,
        zoning: ZoningRules | None = None,
    ) -> tuple[BuildingPlan, list[ModificationRecord]]:
        """Apply a sequence of modification commands cumulatively.

        D1-S1: Enables multi-round change accumulation — each command is
        applied on top of the result of the previous one.
        Returns (final_plan, list_of_records).
        """
        plan = current_plan
        records: list[ModificationRecord] = []
        for cmd in commands:
            plan, record = self.modify(cmd, plan, zoning)
            records.append(record)
        return plan, records

    def get_cumulative_delta(self, current_plan: BuildingPlan) -> dict:
        """Return a summary of all changes from the original baseline to current_plan.

        D1-S1: Provides a cumulative diff useful for cost delta and schedule delta.
        Returns a dict with keys: stories_delta, height_delta_m, area_delta_sqm,
        bcr_delta, far_delta, modification_count, commands.
        """
        if self._original_snapshot is None:
            return {
                "stories_delta": 0,
                "height_delta_m": 0.0,
                "area_delta_sqm": 0.0,
                "bcr_delta": 0.0,
                "far_delta": 0.0,
                "modification_count": 0,
                "commands": [],
            }
        orig = BuildingPlan.model_validate(self._original_snapshot)
        orig_stories = len(orig.stories)
        orig_height = sum(s.height_m for s in orig.stories)
        orig_area = sum(
            poly_area(s.slab_boundary) if s.slab_boundary else poly_area(orig.building_footprint)
            for s in orig.stories
        )
        curr_height = sum(s.height_m for s in current_plan.stories)
        curr_area = sum(
            poly_area(s.slab_boundary) if s.slab_boundary else poly_area(current_plan.building_footprint)
            for s in current_plan.stories
        )
        commands = [r.command for r in self._history.records]
        return {
            "stories_delta": len(current_plan.stories) - orig_stories,
            "height_delta_m": round(curr_height - orig_height, 2),
            "area_delta_sqm": round(curr_area - orig_area, 1),
            "bcr_delta": round(current_plan.building_bcr - orig.building_bcr, 4),
            "far_delta": round(current_plan.building_far - orig.building_far, 4),
            "modification_count": len(self._history.records),
            "commands": commands,
        }

    def reset_baseline(self, plan: BuildingPlan) -> None:
        """Reset the original baseline to the given plan (e.g. after regeneration)."""
        self._original_snapshot = plan.model_dump()
        self._history = ModificationHistory()

    def undo(
        self, current_plan: BuildingPlan
    ) -> tuple[BuildingPlan | None, ModificationRecord | None]:
        """Undo the last modification by restoring the snapshot."""
        record = self._history.pop_last()
        if record is None:
            return None, None
        restored = BuildingPlan.model_validate(record.plan_snapshot_json)
        return restored, record

    def _parse_intent(self, command: str, plan: BuildingPlan) -> ModificationIntent:
        """Use Claude to parse the modification intent."""
        summary = (
            f"Current building: {plan.name}\n"
            f"- Stories: {len(plan.stories)}\n"
            f"- BCR: {plan.building_bcr:.2f}\n"
            f"- FAR: {plan.building_far:.2f}\n"
            f"- Story height: {plan.stories[0].height_m if plan.stories else 3.0}m\n"
        )
        user_msg = f"Modification command: {command}\n\n{summary}"

        response = self.run(user_msg)
        if response.ok and response.json_data:
            data = response.json_data
            try:
                mod_type = ModificationType(data.get("modification_type", "general"))
            except ValueError:
                mod_type = ModificationType.GENERAL
            return ModificationIntent(
                raw_command=command,
                modification_type=mod_type,
                parameters=data.get("parameters", {}),
                confidence=data.get("confidence", 0.5),
            )

        # Fallback: simple keyword matching
        return self._fallback_parse(command)

    def _fallback_parse(self, command: str) -> ModificationIntent:
        """Keyword-based fallback parser when Claude is unavailable."""
        cmd_lower = command.lower()
        params: dict = {}
        mod_type = ModificationType.GENERAL

        # Story changes
        import re

        story_match = re.search(r"(\d+)\s*(?:層|layer|stor(?:y|ies)|floor)", cmd_lower)
        if story_match or "層" in cmd_lower or "story" in cmd_lower or "stories" in cmd_lower:
            mod_type = ModificationType.STORIES
            if story_match:
                params["target_stories"] = int(story_match.group(1))

        # Height changes
        height_match = re.search(
            r"(?:層高|story.?height|floor.?height)\s*[=:：]?\s*(\d+\.?\d*)", cmd_lower
        )
        if height_match:
            mod_type = ModificationType.HEIGHT
            params["story_height_m"] = float(height_match.group(1))

        # Roof changes
        for roof_type in ("flat", "gable", "hip", "平屋頂", "斜屋頂"):
            if roof_type in cmd_lower:
                mod_type = ModificationType.ROOF
                rt = {"平屋頂": "flat", "斜屋頂": "gable"}.get(roof_type, roof_type)
                params["roof_type"] = rt
                break

        return ModificationIntent(
            raw_command=command,
            modification_type=mod_type,
            parameters=params,
            confidence=0.3,
        )

    def _apply(
        self,
        intent: ModificationIntent,
        plan: BuildingPlan,
        zoning: ZoningRules,
    ) -> BuildingPlan:
        """Apply the modification intent to the plan deterministically."""
        new_plan = plan.model_copy(deep=True)

        if intent.modification_type == ModificationType.STORIES:
            new_plan = self._apply_stories(intent, new_plan, zoning)
        elif intent.modification_type == ModificationType.HEIGHT:
            new_plan = self._apply_height(intent, new_plan)
        elif intent.modification_type == ModificationType.ROOF:
            new_plan = self._apply_roof(intent, new_plan)
        elif intent.modification_type == ModificationType.FOOTPRINT:
            new_plan = self._apply_footprint(intent, new_plan, zoning)
        elif intent.modification_type == ModificationType.ROOMS:
            new_plan = self._apply_rooms(intent, new_plan)
        elif intent.modification_type == ModificationType.MATERIALS:
            new_plan = self._apply_materials(intent, new_plan)
        elif intent.modification_type == ModificationType.OPENINGS:
            new_plan = self._apply_openings(intent, new_plan)
        else:
            logger.warning("Unsupported modification type: %s", intent.modification_type)

        # Recalculate BCR/FAR
        new_plan = _recalculate_metrics(new_plan)
        return new_plan

    def _apply_stories(
        self,
        intent: ModificationIntent,
        plan: BuildingPlan,
        zoning: ZoningRules,
    ) -> BuildingPlan:
        """Change the number of stories."""
        target = intent.parameters.get("target_stories")
        if target is None:
            return plan

        target = int(target)
        current = len(plan.stories)
        if target == current:
            return plan

        # Enforce height limit
        from promptbim.constants import DEFAULT_STORY_HEIGHT_M

        max_stories = int(zoning.height_limit_m / DEFAULT_STORY_HEIGHT_M) if zoning.height_limit_m > 0 else 99
        target = min(target, max_stories)
        target = max(target, 1)

        if target > current:
            # Add stories by cloning the top floor
            template = plan.stories[-1] if plan.stories else StoryPlan(name="1F", elevation_m=0.0)
            for i in range(current, target):
                new_story = template.model_copy(deep=True)
                new_story.name = f"{i + 1}F"
                new_story.elevation_m = i * template.height_m
                plan.stories.append(new_story)
        else:
            # Remove stories from top
            plan.stories = plan.stories[:target]

        return plan

    def _apply_height(self, intent: ModificationIntent, plan: BuildingPlan) -> BuildingPlan:
        """Change story height."""
        new_height = intent.parameters.get("story_height_m")
        if new_height is None:
            return plan

        new_height = float(new_height)
        for i, story in enumerate(plan.stories):
            story.height_m = new_height
            story.elevation_m = i * new_height

        return plan

    def _apply_roof(self, intent: ModificationIntent, plan: BuildingPlan) -> BuildingPlan:
        """Change roof type."""
        roof_type = intent.parameters.get("roof_type", "flat")
        slope = intent.parameters.get("slope_degrees", 0.0)
        if roof_type == "gable":
            slope = slope or 30.0
        elif roof_type == "hip":
            slope = slope or 25.0

        plan.roof = RoofPlan(
            roof_type=roof_type,
            slope_degrees=slope,
            overhang_m=plan.roof.overhang_m,
        )
        return plan

    def _apply_footprint(
        self,
        intent: ModificationIntent,
        plan: BuildingPlan,
        zoning: ZoningRules,
    ) -> BuildingPlan:
        """Scale the footprint."""
        scale = intent.parameters.get("scale_factor")
        if scale is None:
            target_area = intent.parameters.get("target_area_sqm")
            if target_area and plan.building_footprint:
                current_area = _poly_area(plan.building_footprint)
                if current_area > 0:
                    scale = (float(target_area) / current_area) ** 0.5
        if scale is None:
            return plan

        scale = float(scale)

        # Scale footprint around centroid
        plan.building_footprint = _scale_polygon(plan.building_footprint, scale)

        # Scale each story's geometry
        for story in plan.stories:
            story.slab_boundary = _scale_polygon(story.slab_boundary, scale)
            for wall in story.walls:
                wall.start = _scale_point(wall.start, scale, plan.building_footprint)
                wall.end = _scale_point(wall.end, scale, plan.building_footprint)
            for space in story.spaces:
                space.boundary = _scale_polygon(space.boundary, scale)
                space.area_sqm *= scale * scale

        return plan


    def _apply_rooms(self, intent: ModificationIntent, plan: BuildingPlan) -> BuildingPlan:
        """Add/remove/rename rooms in specified stories (D1-S1 enhancement)."""
        from promptbim.schemas.plan import SpaceDef

        params = intent.parameters
        target_story = params.get("story", "all")
        add_rooms: list[dict] = params.get("add_rooms", [])
        remove_rooms: list[str] = params.get("remove_rooms", [])

        for story in plan.stories:
            if target_story != "all" and story.name != str(target_story):
                continue
            # Remove rooms by name
            if remove_rooms:
                story.spaces = [s for s in story.spaces if s.name not in remove_rooms]
            # Add rooms (append as small spaces; geometry is approximate)
            for room_def in add_rooms:
                room_name = room_def.get("name", "New Room")
                room_area = float(room_def.get("area_sqm", 20.0))
                room_type = room_def.get("space_type", "office")
                # Place new room at a nominal offset from footprint centroid
                if plan.building_footprint:
                    cx = sum(p[0] for p in plan.building_footprint) / len(plan.building_footprint)
                    cy = sum(p[1] for p in plan.building_footprint) / len(plan.building_footprint)
                    half = (room_area ** 0.5) / 2
                    boundary = [
                        (cx - half, cy - half), (cx + half, cy - half),
                        (cx + half, cy + half), (cx - half, cy + half),
                    ]
                else:
                    boundary = [(0, 0), (5, 0), (5, 4), (0, 4)]
                story.spaces.append(
                    SpaceDef(
                        name=room_name,
                        boundary=boundary,
                        space_type=room_type,
                        area_sqm=room_area,
                    )
                )
        return plan

    def _apply_materials(self, intent: ModificationIntent, plan: BuildingPlan) -> BuildingPlan:
        """Change wall types/materials for facade (D1-S1 enhancement)."""
        params = intent.parameters
        wall_type = params.get("wall_type")  # e.g. "curtain_wall", "brick", "concrete"
        target = params.get("target", "exterior")  # "exterior" | "all"
        if wall_type:
            for story in plan.stories:
                for wall in story.walls:
                    if target == "all" or wall.wall_type == "exterior":
                        wall.wall_type = wall_type
        return plan

    def _apply_openings(self, intent: ModificationIntent, plan: BuildingPlan) -> BuildingPlan:
        """Adjust window/door openings (D1-S1 enhancement)."""
        from promptbim.schemas.plan import OpeningDef

        params = intent.parameters
        action = params.get("action", "add")  # "add" | "resize" | "remove"
        target_story = params.get("story", "all")
        opening_type = params.get("opening_type", "window")
        width_m = float(params.get("width_m", 1.2))
        height_m = float(params.get("height_m", 1.5))

        for story in plan.stories:
            if target_story != "all" and story.name != str(target_story):
                continue
            if action == "add":
                for wall_idx in range(len(story.walls)):
                    story.openings.append(
                        OpeningDef(
                            wall_index=wall_idx,
                            offset_m=0.5,
                            width_m=width_m,
                            height_m=height_m,
                            sill_height_m=0.9 if opening_type == "window" else 0.0,
                            opening_type=opening_type,
                        )
                    )
            elif action == "resize":
                for opening in story.openings:
                    if opening.opening_type == opening_type:
                        opening.width_m = width_m
                        opening.height_m = height_m
            elif action == "remove":
                story.openings = [o for o in story.openings if o.opening_type != opening_type]
        return plan


def _scale_polygon(coords: list[tuple[float, float]], scale: float) -> list[tuple[float, float]]:
    """Scale polygon around its centroid."""
    if not coords:
        return coords
    cx = sum(p[0] for p in coords) / len(coords)
    cy = sum(p[1] for p in coords) / len(coords)
    return [(cx + (x - cx) * scale, cy + (y - cy) * scale) for x, y in coords]


def _scale_point(
    point: tuple[float, float],
    scale: float,
    reference: list[tuple[float, float]],
) -> tuple[float, float]:
    """Scale a point relative to the reference polygon's centroid."""
    if not reference:
        return point
    cx = sum(p[0] for p in reference) / len(reference)
    cy = sum(p[1] for p in reference) / len(reference)
    return (cx + (point[0] - cx) * scale, cy + (point[1] - cy) * scale)


def _recalculate_metrics(plan: BuildingPlan) -> BuildingPlan:
    """Recalculate BCR and FAR from current geometry."""
    footprint_area = _poly_area(plan.building_footprint)
    land_area = _poly_area(plan.land_boundary)

    if land_area > 0:
        plan.building_bcr = round(footprint_area / land_area, 4)
        total_floor_area = sum(
            poly_area(s.slab_boundary) if s.slab_boundary else footprint_area for s in plan.stories
        )
        plan.building_far = round(total_floor_area / land_area, 4)

    return plan
