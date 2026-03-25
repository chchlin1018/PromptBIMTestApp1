"""Building Templates: Office, Residential, School, Hospital, Factory.

Provides pre-built plan generators for common building types.
Each template takes a land boundary + buildable area and returns a BuildingPlan.
"""

from __future__ import annotations

from typing import Callable

from promptbim.schemas.plan import BuildingPlan

from promptbim.bim.templates.school import generate_school_plan
from promptbim.bim.templates.hospital import generate_hospital_plan
from promptbim.bim.templates.factory import generate_factory_plan

# Template registry: name -> (generator_func, default_stories, description)
BUILDING_TEMPLATES: dict[str, dict] = {
    "school": {
        "name": "School",
        "generator": generate_school_plan,
        "default_stories": 3,
        "description": "School building with classrooms, corridors, offices, and library",
    },
    "hospital": {
        "name": "Hospital",
        "generator": generate_hospital_plan,
        "default_stories": 5,
        "description": "Hospital with ER, wards, radiology, and pharmacy",
    },
    "factory": {
        "name": "Factory",
        "generator": generate_factory_plan,
        "default_stories": 1,
        "description": "Industrial factory with production hall and office wing",
    },
}


def list_templates() -> list[str]:
    """Return list of available template keys."""
    return list(BUILDING_TEMPLATES.keys())


def get_template_info(key: str) -> dict | None:
    """Return template metadata by key."""
    return BUILDING_TEMPLATES.get(key)


def generate_from_template(
    template_key: str,
    land_boundary: list[tuple[float, float]],
    buildable_area: list[tuple[float, float]],
    num_stories: int | None = None,
    name: str | None = None,
) -> BuildingPlan:
    """Generate a BuildingPlan from a template.

    Args:
        template_key: One of the registered template keys.
        land_boundary: Land parcel boundary coordinates.
        buildable_area: Buildable area coordinates (after setback).
        num_stories: Number of stories (uses template default if None).
        name: Building name (uses template default if None).

    Returns:
        A complete BuildingPlan.

    Raises:
        KeyError: If template_key is not found.
    """
    tmpl = BUILDING_TEMPLATES.get(template_key)
    if tmpl is None:
        raise KeyError(f"Unknown template: {template_key}. Available: {list_templates()}")

    gen_func = tmpl["generator"]
    stories = num_stories if num_stories is not None else tmpl["default_stories"]
    bldg_name = name or f"{tmpl['name']} Building"

    return gen_func(
        land_boundary=land_boundary,
        buildable_area=buildable_area,
        num_stories=stories,
        name=bldg_name,
    )


__all__ = [
    "BUILDING_TEMPLATES",
    "list_templates",
    "get_template_info",
    "generate_from_template",
    "generate_school_plan",
    "generate_hospital_plan",
    "generate_factory_plan",
]
