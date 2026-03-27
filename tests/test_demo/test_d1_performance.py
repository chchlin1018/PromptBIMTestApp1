"""D1-S2 Performance benchmarks — full pipeline < 3 minutes.

Tests verify each stage completes within its time budget:
  - Scene load:     < 1s
  - Mesh build:     < 10s per scene
  - Cost estimate:  < 2s
  - Schedule gen:   < 2s
  - Code checks:    < 1s
  - Export:         < 2s
  Total per scene:  < 20s
  All 3 scenes:     < 60s  (3-minute total with GUI headroom)
"""

from __future__ import annotations

import os
import time

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_SCENE_LOAD_LIMIT_S = 1.0
_MESH_BUILD_LIMIT_S = 10.0
_COST_LIMIT_S = 2.0
_SCHED_LIMIT_S = 2.0
_CODE_LIMIT_S = 1.0
_EXPORT_LIMIT_S = 2.0


@pytest.mark.parametrize("scene_id", ["S1", "S2", "S3"])
class TestScenePerformance:
    def test_scene_load_time(self, scene_id, tmp_path):
        from promptbim.demo.scene_templates import get_scene, SCENE_REGISTRY
        # Clear cache to force fresh load
        SCENE_REGISTRY[scene_id] = None
        t0 = time.perf_counter()
        scene = get_scene(scene_id)
        elapsed = time.perf_counter() - t0
        assert elapsed < _SCENE_LOAD_LIMIT_S, (
            f"Scene {scene_id} load took {elapsed:.3f}s (limit {_SCENE_LOAD_LIMIT_S}s)"
        )

    def test_mesh_build_time(self, scene_id, tmp_path):
        from promptbim.demo.scene_templates import get_scene
        from promptbim.viz.model_3d import build_model
        scene = get_scene(scene_id)
        t0 = time.perf_counter()
        meshes = build_model(scene.plan)
        elapsed = time.perf_counter() - t0
        assert elapsed < _MESH_BUILD_LIMIT_S, (
            f"Scene {scene_id} mesh build took {elapsed:.3f}s (limit {_MESH_BUILD_LIMIT_S}s)"
        )
        assert len(meshes) > 0

    def test_cost_estimate_time(self, scene_id, tmp_path):
        from promptbim.bim.cost.estimator import CostEstimator
        from promptbim.demo.scene_templates import get_scene
        scene = get_scene(scene_id)
        estimator = CostEstimator()
        t0 = time.perf_counter()
        est = estimator.estimate(scene.plan)
        elapsed = time.perf_counter() - t0
        assert elapsed < _COST_LIMIT_S, (
            f"Scene {scene_id} cost estimate took {elapsed:.3f}s (limit {_COST_LIMIT_S}s)"
        )
        assert est.total_cost_twd > 0

    def test_schedule_gen_time(self, scene_id, tmp_path):
        from promptbim.bim.simulation.scheduler import generate_schedule
        from promptbim.demo.scene_templates import get_scene
        from promptbim.viz.model_3d import build_model
        scene = get_scene(scene_id)
        meshes = build_model(scene.plan)
        labels = [l for _, _, l in meshes]
        t0 = time.perf_counter()
        sched = generate_schedule(labels, total_days=360, num_stories=len(scene.plan.stories))
        elapsed = time.perf_counter() - t0
        assert elapsed < _SCHED_LIMIT_S, (
            f"Scene {scene_id} schedule took {elapsed:.3f}s (limit {_SCHED_LIMIT_S}s)"
        )
        assert sched.total_days > 0

    def test_code_check_time(self, scene_id, tmp_path):
        from promptbim.codes.tw_industrial_code import run_industrial_checks
        from promptbim.demo.scene_templates import get_scene
        scene = get_scene(scene_id)
        t0 = time.perf_counter()
        results = run_industrial_checks(scene.plan)
        elapsed = time.perf_counter() - t0
        assert elapsed < _CODE_LIMIT_S, (
            f"Scene {scene_id} code checks took {elapsed:.3f}s (limit {_CODE_LIMIT_S}s)"
        )
        assert len(results) == 4

    def test_export_time(self, scene_id, tmp_path):
        from promptbim.bim.export import export_demo_package
        from promptbim.demo.scene_templates import get_scene
        scene = get_scene(scene_id)
        t0 = time.perf_counter()
        result = export_demo_package(scene.plan, scene_id, tmp_path)
        elapsed = time.perf_counter() - t0
        assert elapsed < _EXPORT_LIMIT_S, (
            f"Scene {scene_id} export took {elapsed:.3f}s (limit {_EXPORT_LIMIT_S}s)"
        )
        assert "plan" in result


class TestFullPipelineTiming:
    """End-to-end timing: all 3 scenes complete within 60s."""

    def test_all_scenes_under_60s(self, tmp_path):
        from promptbim.bim.cost.estimator import CostEstimator
        from promptbim.bim.export import export_demo_package
        from promptbim.bim.simulation.scheduler import generate_schedule
        from promptbim.codes.tw_industrial_code import run_industrial_checks
        from promptbim.demo.scene_templates import get_scene, SCENE_REGISTRY
        from promptbim.viz.model_3d import build_model

        estimator = CostEstimator()
        total_t0 = time.perf_counter()

        for sid in ("S1", "S2", "S3"):
            SCENE_REGISTRY[sid] = None  # force fresh load
            scene = get_scene(sid)
            meshes = build_model(scene.plan)
            labels = [l for _, _, l in meshes]
            _ = estimator.estimate(scene.plan)
            _ = generate_schedule(labels, 360, len(scene.plan.stories))
            _ = run_industrial_checks(scene.plan)
            _ = export_demo_package(scene.plan, sid, tmp_path / sid)

        total_elapsed = time.perf_counter() - total_t0
        assert total_elapsed < 60.0, (
            f"All 3 scenes pipeline took {total_elapsed:.1f}s (limit 60s for headless mode)"
        )
        print(f"\n✅ Full pipeline: {total_elapsed:.2f}s for 3 scenes")
