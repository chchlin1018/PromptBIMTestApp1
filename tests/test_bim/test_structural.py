"""P24 Task 14: Tests for auto-structural generation."""

from promptbim.bim.structural import generate_structural
from promptbim.demo.demo_data import get_demo_plan


class TestStructuralGeneration:
    def test_generates_columns(self):
        plan = get_demo_plan()
        layout = generate_structural(plan)
        assert len(layout.columns) > 0
        assert all(c.element_type == "column" for c in layout.columns)

    def test_generates_beams(self):
        plan = get_demo_plan()
        layout = generate_structural(plan)
        assert len(layout.beams) > 0
        assert all(b.element_type == "beam" for b in layout.beams)
        assert all(b.end is not None for b in layout.beams)

    def test_generates_foundations(self):
        plan = get_demo_plan()
        layout = generate_structural(plan)
        assert len(layout.foundations) > 0
        assert all(f.start[2] < 0 for f in layout.foundations)  # below ground

    def test_grid_spacing_reasonable(self):
        plan = get_demo_plan()
        layout = generate_structural(plan)
        assert 3.0 <= layout.grid_spacing_x <= 10.0
        assert 3.0 <= layout.grid_spacing_y <= 10.0
