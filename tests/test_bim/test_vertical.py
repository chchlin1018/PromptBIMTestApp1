"""P24 Task 14: Tests for stairs/elevator auto-generation."""

from promptbim.bim.vertical import generate_vertical
from promptbim.demo.demo_data import get_demo_plan


class TestVerticalGeneration:
    def test_generates_stairs(self):
        plan = get_demo_plan()
        layout = generate_vertical(plan)
        assert len(layout.stairs) > 0
        flights = [s for s in layout.stairs if s.element_type == "stair_flight"]
        landings = [s for s in layout.stairs if s.element_type == "stair_landing"]
        assert len(flights) >= 2 * len(plan.stories)  # 2 runs per story
        assert len(landings) >= len(plan.stories)

    def test_generates_elevator_shaft(self):
        plan = get_demo_plan()
        layout = generate_vertical(plan)
        assert len(layout.elevators) == len(plan.stories)
        assert all(e.element_type == "elevator_shaft" for e in layout.elevators)

    def test_stairwell_boundary_valid(self):
        plan = get_demo_plan()
        layout = generate_vertical(plan)
        assert len(layout.stairwell_boundary) == 4
        assert len(layout.elevator_shaft_boundary) == 4

    def test_num_stories_matches(self):
        plan = get_demo_plan()
        layout = generate_vertical(plan)
        assert layout.num_stories == len(plan.stories)
