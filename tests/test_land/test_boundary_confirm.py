"""Tests for boundary confirmation logic."""

from promptbim.land.boundary_confirm import (
    BoundaryConfirmation,
    adjust_vertex,
    validate_boundary,
)
from promptbim.schemas.land import LandParcel


def _make_parcel(boundary=None, area=100.0):
    if boundary is None:
        boundary = [(0, 0), (10, 0), (10, 10), (0, 10)]
    return LandParcel(
        name="Test",
        boundary=boundary,
        area_sqm=area,
        perimeter_m=40.0,
        source_type="ai_image",
    )


class TestBoundaryConfirmation:
    def test_empty(self):
        bc = BoundaryConfirmation()
        assert bc.selected is None
        assert bc.selected_parcel is None

    def test_add_candidate(self):
        bc = BoundaryConfirmation()
        bc.add_candidate(_make_parcel(), confidence=0.8, notes="good")
        assert len(bc.candidates) == 1
        assert bc.selected is not None
        assert bc.selected.confidence == 0.8

    def test_multiple_candidates_select(self):
        bc = BoundaryConfirmation()
        bc.add_candidate(_make_parcel(), confidence=0.8)
        bc.add_candidate(_make_parcel(area=200.0), confidence=0.6)
        assert bc.selected_index == 0
        bc.select(1)
        assert bc.selected_index == 1
        assert bc.selected.confidence == 0.6

    def test_sort_by_confidence(self):
        bc = BoundaryConfirmation()
        bc.add_candidate(_make_parcel(), confidence=0.3)
        bc.add_candidate(_make_parcel(), confidence=0.9)
        bc.add_candidate(_make_parcel(), confidence=0.6)
        bc.sort_by_confidence()
        assert bc.candidates[0].confidence == 0.9
        assert bc.candidates[2].confidence == 0.3
        assert bc.selected_index == 0

    def test_invalid_select(self):
        bc = BoundaryConfirmation()
        bc.add_candidate(_make_parcel(), confidence=0.5)
        bc.select(99)
        assert bc.selected_index == 0  # unchanged


class TestAdjustVertex:
    def test_adjust_vertex(self):
        parcel = _make_parcel([(0, 0), (10, 0), (10, 10), (0, 10)])
        new_parcel = adjust_vertex(parcel, 2, 12.0, 12.0)
        assert new_parcel.boundary[2] == (12.0, 12.0)
        assert new_parcel.area_sqm != parcel.area_sqm

    def test_adjust_first_vertex(self):
        parcel = _make_parcel([(0, 0), (10, 0), (10, 10), (0, 10)])
        new_parcel = adjust_vertex(parcel, 0, 1.0, 1.0)
        assert new_parcel.boundary[0] == (1.0, 1.0)

    def test_invalid_index(self):
        parcel = _make_parcel()
        result = adjust_vertex(parcel, 99, 5.0, 5.0)
        assert result.boundary == parcel.boundary

    def test_area_recalculated(self):
        parcel = _make_parcel([(0, 0), (10, 0), (10, 10), (0, 10)])
        new_parcel = adjust_vertex(parcel, 2, 20.0, 20.0)
        # Area should change from 100 to something larger
        assert new_parcel.area_sqm > 100.0

    def test_perimeter_recalculated(self):
        parcel = _make_parcel([(0, 0), (10, 0), (10, 10), (0, 10)])
        new_parcel = adjust_vertex(parcel, 2, 20.0, 20.0)
        assert new_parcel.perimeter_m != parcel.perimeter_m


class TestValidateBoundary:
    def test_valid_square(self):
        issues = validate_boundary([(0, 0), (10, 0), (10, 10), (0, 10)])
        assert len(issues) == 0

    def test_too_few_vertices(self):
        issues = validate_boundary([(0, 0), (10, 0)])
        assert len(issues) > 0
        assert "at least 3" in issues[0]

    def test_degenerate_area(self):
        issues = validate_boundary([(0, 0), (0.001, 0), (0, 0.001)])
        assert any("too small" in i.lower() for i in issues)

    def test_self_intersection(self):
        # Bowtie shape
        issues = validate_boundary([(0, 0), (10, 10), (10, 0), (0, 10)])
        assert any("self-intersection" in i.lower() for i in issues)

    def test_valid_triangle(self):
        issues = validate_boundary([(0, 0), (10, 0), (5, 8)])
        assert len(issues) == 0

    def test_valid_pentagon(self):
        import math

        boundary = [
            (5 * math.cos(2 * math.pi * i / 5), 5 * math.sin(2 * math.pi * i / 5)) for i in range(5)
        ]
        issues = validate_boundary(boundary)
        assert len(issues) == 0
