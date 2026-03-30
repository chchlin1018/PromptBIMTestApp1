"""Entity Registry & Indexing — GAP-F003.

Provides a unified registry for all BIM entities in a BuildingPlan,
with index-based lookup and search capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from promptbim.debug import get_logger

logger = get_logger("bim.entity_registry")


@dataclass
class EntityRecord:
    """A single entity record in the registry."""
    entity_id: str
    entity_type: str  # "wall", "space", "opening", "slab", "roof"
    name: str
    story_name: str
    position: tuple[float, float, float]  # centroid (x, y, z)
    metadata: dict = field(default_factory=dict)


class EntityRegistry:
    """Central registry for BIM entities with indexing.

    Supports lookup by ID, search by type, and spatial indexing.
    """

    def __init__(self) -> None:
        self._by_id: dict[str, EntityRecord] = {}
        self._by_type: dict[str, list[EntityRecord]] = {}
        self._by_story: dict[str, list[EntityRecord]] = {}

    def register(self, record: EntityRecord) -> None:
        """Register an entity record."""
        self._by_id[record.entity_id] = record
        self._by_type.setdefault(record.entity_type, []).append(record)
        self._by_story.setdefault(record.story_name, []).append(record)

    def get(self, entity_id: str) -> EntityRecord | None:
        """Look up an entity by ID."""
        return self._by_id.get(entity_id)

    def search(self, entity_type: str | None = None, story_name: str | None = None) -> list[EntityRecord]:
        """Search entities by type and/or story."""
        if entity_type and story_name:
            return [
                e for e in self._by_type.get(entity_type, [])
                if e.story_name == story_name
            ]
        if entity_type:
            return list(self._by_type.get(entity_type, []))
        if story_name:
            return list(self._by_story.get(story_name, []))
        return list(self._by_id.values())

    def list_all(self) -> list[EntityRecord]:
        """Return all registered entities."""
        return list(self._by_id.values())

    @property
    def count(self) -> int:
        return len(self._by_id)

    @classmethod
    def from_plan(cls, plan: "BuildingPlan") -> EntityRegistry:
        """Build an EntityRegistry from a BuildingPlan.

        Indexes all walls, spaces, openings, and slabs with centroid positions.
        """
        registry = cls()
        story_z = 0.0
        floor_height = 3.0  # default floor height in metres

        for story_idx, story in enumerate(plan.stories):
            story_name = story.name or f"Story_{story_idx}"

            # Register walls
            for wall_idx, wall in enumerate(story.walls):
                mid_x = (wall.start[0] + wall.end[0]) / 2
                mid_y = (wall.start[1] + wall.end[1]) / 2
                mid_z = story_z + floor_height / 2
                wall_id = f"{story_name}_wall_{wall_idx}"
                registry.register(EntityRecord(
                    entity_id=wall_id,
                    entity_type="wall",
                    name=f"Wall {wall_idx}",
                    story_name=story_name,
                    position=(mid_x, mid_y, mid_z),
                    metadata={"thickness": wall.thickness, "index": wall_idx},
                ))

            # Register spaces
            for space_idx, space in enumerate(story.spaces):
                if space.boundary:
                    cx = sum(p[0] for p in space.boundary) / len(space.boundary)
                    cy = sum(p[1] for p in space.boundary) / len(space.boundary)
                else:
                    cx, cy = 0.0, 0.0
                space_id = f"{story_name}_space_{space_idx}"
                registry.register(EntityRecord(
                    entity_id=space_id,
                    entity_type="space",
                    name=space.name or f"Space {space_idx}",
                    story_name=story_name,
                    position=(cx, cy, story_z + floor_height / 2),
                    metadata={"space_type": space.space_type, "index": space_idx},
                ))

            # Register openings
            for open_idx, opening in enumerate(story.openings):
                # Approximate position from wall reference
                opening_id = f"{story_name}_opening_{open_idx}"
                registry.register(EntityRecord(
                    entity_id=opening_id,
                    entity_type="opening",
                    name=f"{opening.opening_type.capitalize()} {open_idx}",
                    story_name=story_name,
                    position=(opening.offset_along_wall, 0.0, story_z + 1.0),
                    metadata={"opening_type": opening.opening_type, "index": open_idx},
                ))

            # Register slab as single entity
            if story.slab:
                slab_id = f"{story_name}_slab"
                if story.slab.boundary:
                    sx = sum(p[0] for p in story.slab.boundary) / len(story.slab.boundary)
                    sy = sum(p[1] for p in story.slab.boundary) / len(story.slab.boundary)
                else:
                    sx, sy = 0.0, 0.0
                registry.register(EntityRecord(
                    entity_id=slab_id,
                    entity_type="slab",
                    name=f"Slab {story_name}",
                    story_name=story_name,
                    position=(sx, sy, story_z),
                    metadata={"thickness": story.slab.thickness},
                ))

            story_z += floor_height

        logger.debug("EntityRegistry built: %d entities from %d stories", registry.count, len(plan.stories))
        return registry
