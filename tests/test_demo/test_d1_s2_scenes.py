"""D1-S2 Demo-1 three-scene E2E tests.

Tests cover:
  - Scene S1 Villa + Pool: land, zoning, plan validity, cost estimate, 4D schedule
  - Scene S2 Semiconductor Fab: industrial code checks, fab geometry
  - Scene S3 Data Center: DC code checks, plan structure
  - GPU render config detection
  - Asset browser (24 assets, 3 categories, search filter)
  - Export package (plan JSON)
  - Delta panel computation
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path

import pytest

# Force offscreen mode for GUI-less tests
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


# ---------------------------------------------------------------------------
# Scene template tests
# ---------------------------------------------------------------------------

class TestSceneS1:
    def test_load(self):
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S1")
        assert s.scene_id == "S1"
        assert "villa" in s.tags
        assert len(s.plan.stories) >= 3

    def test_land_area(self):
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S1")
        assert s.land.area_sqm > 500, "Villa land should be > 500 m²"

    def test_pool_story(self):
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S1")
        pool_stories = [st for st in s.plan.stories if st.elevation_m < 0]
        assert len(pool_stories) >= 1, "S1 should have at least 1 underground (pool) story"
        pool_spaces = [sp for st in pool_stories for sp in st.spaces]
        assert any("pool" in sp.name.lower() or "swim" in sp.name.lower() for sp in pool_spaces)

    def test_zoning_residential(self):
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S1")
        assert s.zoning.zone_type == "residential"

    def test_cost_estimate(self):
        from promptbim.bim.cost.estimator import CostEstimator
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S1")
        estimator = CostEstimator()
        est = estimator.estimate(s.plan)
        assert est.total_cost_twd > 0
        cost_m = est.total_cost_twd / 1_000_000
        assert 1 < cost_m < 5000, f"Cost {cost_m:.1f}M NT$ out of range"

    def test_4d_schedule(self):
        from promptbim.bim.simulation.scheduler import generate_schedule
        from promptbim.demo.scene_templates import get_scene
        from promptbim.viz.model_3d import build_model
        s = get_scene("S1")
        meshes = build_model(s.plan)
        labels = [label for _, _, label in meshes]
        sched = generate_schedule(labels, total_days=300, num_stories=len(s.plan.stories))
        assert sched.total_days > 0
        assert len(sched.phases) > 0


class TestSceneS2:
    def test_load(self):
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S2")
        assert s.scene_id == "S2"
        assert "tsmc" in s.tags

    def test_land_area_industrial(self):
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S2")
        assert s.land.area_sqm > 5000, f"Fab land should be > 5000 m², got {s.land.area_sqm}"

    def test_industrial_code_checks(self):
        from promptbim.codes.tw_industrial_code import run_industrial_checks, Severity
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S2")
        results = run_industrial_checks(s.plan)
        assert len(results) == 4
        fails = [r for r in results if r.severity == Severity.FAIL]
        assert not fails, f"S2 fab has failing checks: {[r.message_zh for r in fails]}"

    def test_fab_floor_height(self):
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S2")
        fab = next((st for st in s.plan.stories if "fab" in st.name.lower()), None)
        assert fab is not None, "S2 should have a fab floor story"
        assert fab.height_m >= 8.0, f"Fab floor height {fab.height_m}m should be >= 8m"


class TestSceneS3:
    def test_load(self):
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S3")
        assert s.scene_id == "S3"
        assert "datacenter" in s.tags

    def test_dc_cooling_check(self):
        from promptbim.codes.tw_industrial_code import run_industrial_checks, Severity
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S3")
        results = run_industrial_checks(s.plan)
        dc_cool = next((r for r in results if r.rule_id == "TW-IND-004"), None)
        assert dc_cool is not None
        assert dc_cool.severity == Severity.PASS, f"DC cooling: {dc_cool.message_zh}"

    def test_stories_count(self):
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S3")
        assert len(s.plan.stories) >= 4


class TestAllScenes:
    def test_list_scenes(self):
        from promptbim.demo.scene_templates import list_scenes
        scenes = list_scenes()
        assert len(scenes) == 3
        ids = {s.scene_id for s in scenes}
        assert ids == {"S1", "S2", "S3"}

    def test_all_plans_valid(self):
        from promptbim.demo.scene_templates import list_scenes
        for scene in list_scenes():
            assert scene.plan.name, f"Scene {scene.scene_id} plan has no name"
            assert len(scene.plan.stories) > 0


# ---------------------------------------------------------------------------
# GPU render config tests
# ---------------------------------------------------------------------------

class TestGPURender:
    def test_detect_gpu(self):
        from promptbim.gpu_render import detect_gpu
        gpu = detect_gpu()
        assert gpu.name  # at least has a name

    def test_active_config_offscreen(self):
        from promptbim.gpu_render import active_render_config
        cfg = active_render_config()
        assert cfg["gpu_name"] == "Offscreen"
        assert cfg["raytracing"] is False

    def test_rtx4090_preset(self):
        from promptbim.gpu_render import RTX4090_CONFIG
        assert RTX4090_CONFIG["vram_gb"] == 24.0
        assert RTX4090_CONFIG["rtx"] is True
        assert RTX4090_CONFIG["max_instances"] == 500_000


# ---------------------------------------------------------------------------
# Asset browser tests
# ---------------------------------------------------------------------------

class TestAssetBrowser:
    def test_library_size(self):
        from promptbim.gui.asset_browser import ASSET_LIBRARY
        assert len(ASSET_LIBRARY) >= 20, "Should have at least 20 assets"

    def test_three_categories(self):
        from promptbim.gui.asset_browser import ASSET_LIBRARY
        cats = {a.category for a in ASSET_LIBRARY}
        assert "structural" in cats
        assert "mep" in cats
        assert "finish" in cats

    def test_search_filter(self):
        from promptbim.gui.asset_browser import ASSET_LIBRARY
        hvac = [a for a in ASSET_LIBRARY if "hvac" in a.tags]
        assert len(hvac) > 0

    def test_asset_spec_fields(self):
        from promptbim.gui.asset_browser import ASSET_LIBRARY
        for a in ASSET_LIBRARY:
            assert a.asset_id
            assert a.name
            assert a.unit_cost_twd > 0


# ---------------------------------------------------------------------------
# Export tests
# ---------------------------------------------------------------------------

class TestExport:
    def test_plan_json_export(self, tmp_path):
        from promptbim.bim.export import export_plan_json
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S1")
        out = export_plan_json(s.plan, tmp_path / "s1_plan.json")
        assert out.exists()
        data = json.loads(out.read_text())
        assert data["name"] == "S1 Villa + Pool"
        assert len(data["stories"]) == len(s.plan.stories)

    def test_demo_package(self, tmp_path):
        from promptbim.bim.export import export_demo_package
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S2")
        result = export_demo_package(s.plan, "S2", tmp_path)
        assert "plan" in result
        assert result["plan"].exists()


# ---------------------------------------------------------------------------
# Delta panel tests
# ---------------------------------------------------------------------------

class TestDeltaPanel:
    def test_compute_delta_same_plan(self):
        from promptbim.gui.delta_panel import compute_plan_delta
        from promptbim.demo.scene_templates import get_scene
        s = get_scene("S1")
        delta = compute_plan_delta(s.plan, s.plan, command="no change")
        assert len(delta.records) == 0

    def test_compute_delta_different_plans(self):
        from promptbim.gui.delta_panel import compute_plan_delta
        from promptbim.demo.scene_templates import get_scene
        s1 = get_scene("S1")
        s2 = get_scene("S2")
        delta = compute_plan_delta(s1.plan, s2.plan, command="switch to fab")
        assert len(delta.records) > 0, "S1→S2 should have at least one delta record"
        # BCR or GFA must differ significantly between villa (BCR=0.45) and fab (BCR=0.65)
        gfa_change = next((r for r in delta.records if r.field == "GFA (m²)"), None)
        assert gfa_change is not None, f"GFA delta should be present; got {[r.field for r in delta.records]}"


# ---------------------------------------------------------------------------
# Workflow controller tests
# ---------------------------------------------------------------------------

class TestWorkflowController:
    def test_import(self):
        from promptbim.gui.workflow_controller import WorkflowController, WorkflowProgressBar, DEMO1_STEPS
        assert len(DEMO1_STEPS) > 0

    def test_progress_bar_steps(self):
        from promptbim.gui.workflow_controller import WorkflowProgressBar
        # Just import — headless test
        assert WorkflowProgressBar is not None
