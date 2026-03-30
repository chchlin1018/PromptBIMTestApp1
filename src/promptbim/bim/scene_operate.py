"""Per-entity Scene Operate API — GAP-F002.

Provides individual entity manipulation operations:
- move_entity(): translate an entity
- rotate_entity(): rotate an entity
- operate_entity(): generic operation dispatcher
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass

from promptbim.debug import get_logger
from promptbim.schemas.plan import BuildingPlan

logger = get_logger("bim.scene_operate")


@dataclass
class OperateResult:
    """Result of a scene operation."""
    success: bool
    entity_id: str
    operation: str
    message: str
    plan: BuildingPlan | None = None


def move_entity(
    plan: BuildingPlan,
    entity_id: str,
    dx: float = 0.0,
    dy: float = 0.0,
    dz: float = 0.0,
) -> OperateResult:
    """Move an entity by a delta offset.

    Modifies the plan in-place and returns the result.
    Supports wall, space, and opening entities.
    """
    new_plan = copy.deepcopy(plan)
    parts = entity_id.split("_")

    # Parse entity_id format: "{story_name}_{type}_{index}"
    if len(parts) < 3:
        return OperateResult(False, entity_id, "move", f"Invalid entity_id format: {entity_id}")

    entity_type = parts[-2]
    try:
        idx = int(parts[-1])
    except ValueError:
        return OperateResult(False, entity_id, "move", f"Invalid index in entity_id: {entity_id}")

    story_name = "_".join(parts[:-2])

    # Find the story
    target_story = None
    for story in new_plan.stories:
        if story.name == story_name:
            target_story = story
            break

    if target_story is None:
        return OperateResult(False, entity_id, "move", f"Story not found: {story_name}")

    if entity_type == "wall":
        if idx >= len(target_story.walls):
            return OperateResult(False, entity_id, "move", f"Wall index out of range: {idx}")
        wall = target_story.walls[idx]
        wall.start = (wall.start[0] + dx, wall.start[1] + dy)
        wall.end = (wall.end[0] + dx, wall.end[1] + dy)
        logger.info("Moved wall %s by (%.2f, %.2f)", entity_id, dx, dy)

    elif entity_type == "space":
        if idx >= len(target_story.spaces):
            return OperateResult(False, entity_id, "move", f"Space index out of range: {idx}")
        space = target_story.spaces[idx]
        space.boundary = [(p[0] + dx, p[1] + dy) for p in space.boundary]
        logger.info("Moved space %s by (%.2f, %.2f)", entity_id, dx, dy)

    elif entity_type == "opening":
        if idx >= len(target_story.openings):
            return OperateResult(False, entity_id, "move", f"Opening index out of range: {idx}")
        opening = target_story.openings[idx]
        opening.offset_along_wall += dx
        logger.info("Moved opening %s by offset %.2f", entity_id, dx)

    else:
        return OperateResult(False, entity_id, "move", f"Unsupported entity type: {entity_type}")

    return OperateResult(True, entity_id, "move", f"Moved {entity_id} by ({dx}, {dy}, {dz})", new_plan)


def rotate_entity(
    plan: BuildingPlan,
    entity_id: str,
    angle_degrees: float,
    pivot: tuple[float, float] | None = None,
) -> OperateResult:
    """Rotate an entity around a pivot point.

    Args:
        plan: BuildingPlan to modify.
        entity_id: ID of the entity to rotate.
        angle_degrees: Rotation angle in degrees (counter-clockwise).
        pivot: Optional pivot point (x, y). Defaults to entity centroid.
    """
    new_plan = copy.deepcopy(plan)
    parts = entity_id.split("_")

    if len(parts) < 3:
        return OperateResult(False, entity_id, "rotate", f"Invalid entity_id: {entity_id}")

    entity_type = parts[-2]
    try:
        idx = int(parts[-1])
    except ValueError:
        return OperateResult(False, entity_id, "rotate", f"Invalid index: {entity_id}")

    story_name = "_".join(parts[:-2])
    target_story = None
    for story in new_plan.stories:
        if story.name == story_name:
            target_story = story
            break

    if target_story is None:
        return OperateResult(False, entity_id, "rotate", f"Story not found: {story_name}")

    rad = math.radians(angle_degrees)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    def _rotate_point(x: float, y: float, cx: float, cy: float) -> tuple[float, float]:
        nx = cos_a * (x - cx) - sin_a * (y - cy) + cx
        ny = sin_a * (x - cx) + cos_a * (y - cy) + cy
        return (round(nx, 6), round(ny, 6))

    if entity_type == "wall":
        if idx >= len(target_story.walls):
            return OperateResult(False, entity_id, "rotate", f"Wall index out of range: {idx}")
        wall = target_story.walls[idx]
        if pivot is None:
            pivot = ((wall.start[0] + wall.end[0]) / 2, (wall.start[1] + wall.end[1]) / 2)
        wall.start = _rotate_point(wall.start[0], wall.start[1], pivot[0], pivot[1])
        wall.end = _rotate_point(wall.end[0], wall.end[1], pivot[0], pivot[1])
        logger.info("Rotated wall %s by %.1f°", entity_id, angle_degrees)

    elif entity_type == "space":
        if idx >= len(target_story.spaces):
            return OperateResult(False, entity_id, "rotate", f"Space index out of range: {idx}")
        space = target_story.spaces[idx]
        if pivot is None and space.boundary:
            cx = sum(p[0] for p in space.boundary) / len(space.boundary)
            cy = sum(p[1] for p in space.boundary) / len(space.boundary)
            pivot = (cx, cy)
        elif pivot is None:
            pivot = (0.0, 0.0)
        space.boundary = [_rotate_point(p[0], p[1], pivot[0], pivot[1]) for p in space.boundary]
        logger.info("Rotated space %s by %.1f°", entity_id, angle_degrees)

    else:
        return OperateResult(False, entity_id, "rotate", f"Unsupported entity type for rotate: {entity_type}")

    return OperateResult(True, entity_id, "rotate", f"Rotated {entity_id} by {angle_degrees}°", new_plan)


def operate_entity(
    plan: BuildingPlan,
    entity_id: str,
    operation: str,
    **kwargs,
) -> OperateResult:
    """Generic operation dispatcher for entity manipulation.

    Args:
        plan: BuildingPlan to modify.
        entity_id: Target entity ID.
        operation: "move", "rotate".
        **kwargs: Operation-specific parameters.
    """
    if operation == "move":
        return move_entity(plan, entity_id, **kwargs)
    elif operation == "rotate":
        return rotate_entity(plan, entity_id, **kwargs)
    else:
        return OperateResult(False, entity_id, operation, f"Unknown operation: {operation}")
