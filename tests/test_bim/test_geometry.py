"""Tests for bim/geometry.py — mesh generation."""

import numpy as np
import pytest

from promptbim.bim.geometry import (
    Mesh,
    flat_roof_mesh,
    gable_roof_mesh,
    slab_mesh,
    wall_mesh,
)


class TestWallMesh:
    def test_basic_wall(self):
        m = wall_mesh((0, 0), (5, 0), height=3.0, thickness=0.2)
        assert m.vertices.shape == (8, 3)
        assert m.faces.shape[0] == 12  # 6 faces × 2 tris

    def test_zero_length_wall(self):
        m = wall_mesh((0, 0), (0, 0), height=3.0)
        assert len(m.vertices) == 0

    def test_angled_wall(self):
        m = wall_mesh((0, 0), (3, 4), height=2.5)
        assert m.vertices.shape == (8, 3)
        # Check z values: bottom at 0, top at 2.5
        assert np.allclose(m.vertices[:4, 2], 0.0)
        assert np.allclose(m.vertices[4:, 2], 2.5)

    def test_wall_base_z(self):
        m = wall_mesh((0, 0), (5, 0), height=3.0, base_z=6.0)
        assert np.allclose(m.vertices[:4, 2], 6.0)
        assert np.allclose(m.vertices[4:, 2], 9.0)


class TestSlabMesh:
    def test_rectangle_slab(self):
        boundary = [(0, 0), (10, 0), (10, 8), (0, 8)]
        m = slab_mesh(boundary, thickness=0.2)
        assert m.vertices.shape == (8, 3)  # 4 bottom + 4 top
        assert m.faces.shape[0] > 0

    def test_triangle_slab(self):
        boundary = [(0, 0), (5, 0), (2.5, 4)]
        m = slab_mesh(boundary, thickness=0.15)
        assert m.vertices.shape == (6, 3)

    def test_too_few_points(self):
        m = slab_mesh([(0, 0), (1, 0)], thickness=0.2)
        assert len(m.vertices) == 0

    def test_slab_elevation(self):
        boundary = [(0, 0), (10, 0), (10, 8), (0, 8)]
        m = slab_mesh(boundary, thickness=0.2, base_z=3.0)
        z_vals = set(m.vertices[:, 2])
        assert 3.0 in z_vals
        assert 3.2 in z_vals


class TestRoofMesh:
    def test_flat_roof(self):
        boundary = [(0, 0), (10, 0), (10, 8), (0, 8)]
        m = flat_roof_mesh(boundary, thickness=0.15, base_z=9.0)
        assert m.vertices.shape[0] > 0

    def test_gable_roof(self):
        boundary = [(0, 0), (10, 0), (10, 8), (0, 8)]
        m = gable_roof_mesh(boundary, ridge_height=2.0, base_z=9.0)
        assert m.vertices.shape == (6, 3)
        # Ridge should be above base
        max_z = m.vertices[:, 2].max()
        assert max_z == pytest.approx(11.0)
