"""P25 Performance tests — 5 new benchmark tests for pipeline throughput."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from promptbim.bim.geometry import poly_area, wall_mesh, slab_mesh
from promptbim.bim.templates import generate_from_template
from promptbim.schemas.land import LandParcel

LAND = [(0, 0), (100, 0), (100, 80), (0, 80)]
BUILDABLE = [(5, 5), (95, 5), (95, 75), (5, 75)]


class TestP25Performance:
    """P25 performance benchmarks."""

    @pytest.mark.benchmark
    def test_geometry_batch_throughput(self):
        """poly_area should handle 10k calls in under 0.5s."""
        boundary = [(0, 0), (20, 0), (20, 15), (0, 15)]
        start = time.monotonic()
        for _ in range(10000):
            poly_area(boundary)
        elapsed = time.monotonic() - start
        assert elapsed < 0.5, f"10k poly_area took {elapsed:.2f}s"

    @pytest.mark.benchmark
    def test_wall_mesh_batch(self):
        """1000 wall_mesh calls should complete in under 1s."""
        start = time.monotonic()
        for i in range(1000):
            wall_mesh(start=(0.0, 0.0), end=(10.0, 0.0), height=3.0, thickness=0.2, base_z=0.0)
        elapsed = time.monotonic() - start
        assert elapsed < 1.0, f"1000 wall_mesh took {elapsed:.2f}s"

    @pytest.mark.benchmark
    def test_slab_mesh_batch(self):
        """500 slab_mesh calls should complete in under 1s."""
        boundary = [(0, 0), (20, 0), (20, 15), (0, 15)]
        start = time.monotonic()
        for _ in range(500):
            slab_mesh(boundary, thickness=0.15, base_z=0.0)
        elapsed = time.monotonic() - start
        assert elapsed < 1.0, f"500 slab_mesh took {elapsed:.2f}s"

    @pytest.mark.benchmark
    def test_template_all_types_speed(self):
        """All 3 template types should generate in under 2s total."""
        start = time.monotonic()
        for key in ["school", "hospital", "factory"]:
            plan = generate_from_template(key, LAND, BUILDABLE, num_stories=3)
            assert len(plan.stories) == 3
        elapsed = time.monotonic() - start
        assert elapsed < 2.0, f"All templates took {elapsed:.2f}s"

    @pytest.mark.benchmark
    def test_ifc_3story_under_2s(self, tmp_path: Path):
        """IFC generation for 3-story building must complete in under 2s."""
        plan = generate_from_template("school", LAND, BUILDABLE, num_stories=3)
        from promptbim.bim.ifc_generator import IFCGenerator

        start = time.monotonic()
        result = IFCGenerator().generate(plan, tmp_path / "p25_perf.ifc")
        elapsed = time.monotonic() - start
        assert result.exists()
        assert elapsed < 2.0, f"IFC 3-story took {elapsed:.2f}s"
