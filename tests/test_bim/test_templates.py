"""Tests for building templates (school, hospital, factory)."""

import pytest

from promptbim.bim.templates import (
    generate_factory_plan,
    generate_from_template,
    generate_hospital_plan,
    generate_school_plan,
    get_template_info,
    list_templates,
)
from promptbim.schemas.plan import BuildingPlan

# Standard test land parcel (40m x 30m rectangle)
LAND_BOUNDARY = [(0, 0), (40, 0), (40, 30), (0, 30)]
BUILDABLE_AREA = [(3, 3), (37, 3), (37, 27), (3, 27)]


class TestTemplateRegistry:
    def test_list_templates(self):
        templates = list_templates()
        assert "school" in templates
        assert "hospital" in templates
        assert "factory" in templates

    def test_get_template_info(self):
        info = get_template_info("school")
        assert info is not None
        assert info["name"] == "School"
        assert "generator" in info

    def test_get_template_info_unknown(self):
        assert get_template_info("spaceship") is None

    def test_generate_from_template_unknown(self):
        with pytest.raises(KeyError, match="spaceship"):
            generate_from_template("spaceship", LAND_BOUNDARY, BUILDABLE_AREA)


class TestSchoolTemplate:
    def test_generate_school(self):
        plan = generate_school_plan(LAND_BOUNDARY, BUILDABLE_AREA)
        assert isinstance(plan, BuildingPlan)
        assert len(plan.stories) == 3  # default
        assert plan.name == "School Building"

    def test_school_has_corridors(self):
        plan = generate_school_plan(LAND_BOUNDARY, BUILDABLE_AREA)
        for story in plan.stories:
            corridor_spaces = [s for s in story.spaces if s.space_type == "corridor"]
            assert len(corridor_spaces) >= 1

    def test_school_custom_stories(self):
        plan = generate_school_plan(LAND_BOUNDARY, BUILDABLE_AREA, num_stories=4)
        assert len(plan.stories) == 4

    def test_school_via_registry(self):
        plan = generate_from_template("school", LAND_BOUNDARY, BUILDABLE_AREA)
        assert isinstance(plan, BuildingPlan)
        assert len(plan.stories) == 3


class TestHospitalTemplate:
    def test_generate_hospital(self):
        plan = generate_hospital_plan(LAND_BOUNDARY, BUILDABLE_AREA)
        assert isinstance(plan, BuildingPlan)
        assert len(plan.stories) == 5
        assert plan.name == "Hospital Building"

    def test_hospital_ground_floor_has_er(self):
        plan = generate_hospital_plan(LAND_BOUNDARY, BUILDABLE_AREA)
        ground = plan.stories[0]
        space_names = [s.name for s in ground.spaces]
        assert any("Emergency" in n for n in space_names)

    def test_hospital_via_registry(self):
        plan = generate_from_template("hospital", LAND_BOUNDARY, BUILDABLE_AREA, num_stories=3)
        assert len(plan.stories) == 3


class TestFactoryTemplate:
    def test_generate_factory(self):
        plan = generate_factory_plan(LAND_BOUNDARY, BUILDABLE_AREA)
        assert isinstance(plan, BuildingPlan)
        assert len(plan.stories) == 1
        assert plan.name == "Factory Building"

    def test_factory_has_production_hall(self):
        plan = generate_factory_plan(LAND_BOUNDARY, BUILDABLE_AREA)
        ground = plan.stories[0]
        space_names = [s.name for s in ground.spaces]
        assert "Production Hall" in space_names

    def test_factory_gable_roof(self):
        plan = generate_factory_plan(LAND_BOUNDARY, BUILDABLE_AREA)
        assert plan.roof.roof_type == "gable"

    def test_factory_two_stories(self):
        plan = generate_factory_plan(LAND_BOUNDARY, BUILDABLE_AREA, num_stories=2)
        assert len(plan.stories) == 2

    def test_factory_via_registry(self):
        plan = generate_from_template("factory", LAND_BOUNDARY, BUILDABLE_AREA)
        assert isinstance(plan, BuildingPlan)


class TestAllTemplatesGenerateValidPlans:
    """Ensure all templates produce valid BuildingPlans with basic sanity checks."""

    @pytest.mark.parametrize("template_key", list_templates())
    def test_template_produces_valid_plan(self, template_key):
        plan = generate_from_template(template_key, LAND_BOUNDARY, BUILDABLE_AREA)
        assert isinstance(plan, BuildingPlan)
        assert len(plan.stories) > 0
        assert len(plan.building_footprint) >= 3
        assert plan.name

        # Each story should have walls and spaces
        for story in plan.stories:
            assert len(story.walls) > 0
            assert len(story.spaces) > 0
            assert story.height_m > 0

    @pytest.mark.parametrize("template_key", list_templates())
    def test_template_with_large_land(self, template_key):
        large_land = [(0, 0), (200, 0), (200, 150), (0, 150)]
        large_buildable = [(10, 10), (190, 10), (190, 140), (10, 140)]
        plan = generate_from_template(template_key, large_land, large_buildable)
        assert isinstance(plan, BuildingPlan)
        assert len(plan.stories) > 0
