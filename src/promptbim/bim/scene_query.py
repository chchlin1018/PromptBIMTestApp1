"""Scene Query API — GAP-F001.

Provides spatial queries over a BuildingPlan:
- query_scene(): list all entities with types
- get_entity_position(): get centroid of an entity by ID
- find_nearby_entities(): spatial proximity search
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from promptbim.bim.entity_registry import EntityRecord, EntityRegistry
from promptbim.debug import get_logger
from promptbim.schemas.plan import BuildingPlan

logger = get_logger("bim.scene_query")


@dataclass
class QueryResult:
    """Result of a scene query."""
    entities: list[EntityRecord] = field(default_factory=list)
    count: int = 0


def query_scene(
    plan: BuildingPlan,
    entity_type: str | None = None,
    story_name: str | None = None,
) -> QueryResult:
    """Query all entities in the scene, optionally filtered by type or story.

    Args:
        plan: The BuildingPlan to query.
        entity_type: Optional filter (e.g. "wall", "space", "opening").
        story_name: Optional filter by story name.

    Returns:
        QueryResult with matching entities.
    """
    registry = EntityRegistry.from_plan(plan)
    entities = registry.list_all()

    if entity_type:
        entities = [e for e in entities if e.entity_type == entity_type]
    if story_name:
        entities = [e for e in entities if e.story_name == story_name]

    return QueryResult(entities=entities, count=len(entities))


def get_entity_position(
    plan: BuildingPlan,
    entity_id: str,
) -> tuple[float, float, float] | None:
    """Get the centroid position of an entity by its ID.

    Returns (x, y, z) or None if not found.
    """
    registry = EntityRegistry.from_plan(plan)
    record = registry.get(entity_id)
    if record is None:
        logger.warning("Entity not found: %s", entity_id)
        return None
    return record.position


def find_nearby_entities(
    plan: BuildingPlan,
    position: tuple[float, float, float],
    radius: float = 5.0,
    entity_type: str | None = None,
) -> QueryResult:
    """Find entities within a radius of a given position.

    Args:
        plan: The BuildingPlan to search.
        position: Center point (x, y, z).
        radius: Search radius in metres.
        entity_type: Optional type filter.

    Returns:
        QueryResult with nearby entities, sorted by distance.
    """
    registry = EntityRegistry.from_plan(plan)
    candidates = registry.list_all()

    if entity_type:
        candidates = [e for e in candidates if e.entity_type == entity_type]

    nearby = []
    for entity in candidates:
        dx = entity.position[0] - position[0]
        dy = entity.position[1] - position[1]
        dz = entity.position[2] - position[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dist <= radius:
            entity.metadata["distance"] = round(dist, 3)
            nearby.append(entity)

    nearby.sort(key=lambda e: e.metadata.get("distance", 0))
    return QueryResult(entities=nearby, count=len(nearby))
