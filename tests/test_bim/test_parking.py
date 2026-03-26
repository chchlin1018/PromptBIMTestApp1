"""P24 Task 14: Tests for auto-parking generation."""

from promptbim.bim.parking import generate_parking
from promptbim.demo.demo_data import get_demo_plan


class TestParkingGeneration:
    def test_generates_bays(self):
        plan = get_demo_plan()
        layout = generate_parking(plan)
        assert layout.total_bays > 0
        assert len(layout.bays) == layout.total_bays

    def test_has_accessible_bay(self):
        plan = get_demo_plan()
        layout = generate_parking(plan)
        assert layout.accessible_bays >= 1

    def test_has_aisle_and_ramp(self):
        plan = get_demo_plan()
        layout = generate_parking(plan)
        assert layout.aisle is not None
        assert layout.ramp is not None
        assert layout.aisle.space_type == "corridor"

    def test_empty_plan_returns_empty(self):
        from promptbim.schemas.plan import BuildingPlan, RoofPlan
        plan = BuildingPlan(name="Empty", stories=[], roof=RoofPlan(roof_type="flat"))
        layout = generate_parking(plan)
        assert layout.total_bays == 0
