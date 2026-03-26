"""P24 Tasks 21-23: Integration tests for P24 features.

- Task 21: E2E pipeline with parking, structural, vertical
- Task 22: MCP demo resource generation
- Task 23: Swift bridge compatibility (file-based)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Task 21: E2E Pipeline Integration
# ---------------------------------------------------------------------------


class TestE2EPipeline:
    """Full pipeline: demo data -> IFC/USDA/SVG + parking + structural + vertical."""

    def test_demo_to_ifc_pipeline(self, tmp_path):
        """Generate demo plan -> IFC file."""
        from promptbim.demo.demo_data import generate_demo_ifc
        ifc_path = generate_demo_ifc(output_dir=tmp_path)
        assert ifc_path.exists()
        assert ifc_path.stat().st_size > 500

    def test_demo_to_usda_pipeline(self, tmp_path):
        """Generate demo plan -> USDA file."""
        from promptbim.demo.demo_data import generate_demo_usda
        usda_path = generate_demo_usda(output_dir=tmp_path)
        assert usda_path.exists()
        assert usda_path.stat().st_size > 500

    def test_parking_from_demo(self):
        """Parking layout from demo plan."""
        from promptbim.bim.parking import generate_parking
        from promptbim.demo.demo_data import get_demo_plan
        plan = get_demo_plan()
        layout = generate_parking(plan)
        assert layout.total_bays > 0

    def test_structural_from_demo(self):
        """Structural system from demo plan."""
        from promptbim.bim.structural import generate_structural
        from promptbim.demo.demo_data import get_demo_plan
        plan = get_demo_plan()
        layout = generate_structural(plan)
        assert len(layout.columns) > 0
        assert len(layout.beams) > 0

    def test_vertical_from_demo(self):
        """Vertical transport from demo plan."""
        from promptbim.bim.vertical import generate_vertical
        from promptbim.demo.demo_data import get_demo_plan
        plan = get_demo_plan()
        layout = generate_vertical(plan)
        assert len(layout.stairs) > 0
        assert len(layout.elevators) > 0


# ---------------------------------------------------------------------------
# Task 22: MCP Server Integration
# ---------------------------------------------------------------------------


class TestMCPDemoIntegration:
    """MCP server should expose demo resources."""

    def test_mcp_server_importable(self):
        from promptbim.mcp import server
        assert hasattr(server, '_state')

    def test_demo_plan_json_serializable(self):
        from promptbim.demo.demo_data import get_demo_plan
        plan = get_demo_plan()
        data = json.loads(plan.model_dump_json())
        assert data["name"]
        assert len(data["stories"]) == 3

    def test_demo_result_json_serializable(self):
        from promptbim.demo.demo_data import get_demo_result
        result = get_demo_result()
        data = json.loads(result.model_dump_json())
        assert data["success"] is True


# ---------------------------------------------------------------------------
# Task 23: Swift ↔ Python Bridge Compatibility
# ---------------------------------------------------------------------------


class TestSwiftBridgeCompatibility:
    """Verify that Python outputs are compatible with Swift consumption."""

    def test_plan_json_has_required_swift_fields(self):
        """Swift BIMSceneBuilder expects stories with slab_boundary."""
        from promptbim.demo.demo_data import get_demo_plan
        plan = get_demo_plan()
        data = json.loads(plan.model_dump_json())
        for story in data["stories"]:
            assert "name" in story
            assert "height_m" in story
            assert "elevation_m" in story
            assert "slab_boundary" in story

    def test_usda_file_loadable_by_scenekit(self, tmp_path):
        """USDA output should be valid ASCII format."""
        from promptbim.demo.demo_data import generate_demo_usda
        usda_path = generate_demo_usda(output_dir=tmp_path)
        content = usda_path.read_text()
        # SceneKit expects valid USDA with proper header
        assert content.startswith("#usda")
        assert "Building" in content

    def test_demo_resources_dir_accessible(self):
        """Resources dir should be relative to project root."""
        from promptbim.demo.demo_data import DEMO_RESOURCES_DIR
        # The dir should be under resources/demo/
        assert "resources" in str(DEMO_RESOURCES_DIR)
        assert "demo" in str(DEMO_RESOURCES_DIR)

    def test_ifc_plan_roundtrip(self, tmp_path):
        """Plan -> IFC -> verify file is non-empty."""
        from promptbim.demo.demo_data import generate_demo_ifc
        ifc_path = generate_demo_ifc(output_dir=tmp_path)
        content = ifc_path.read_text(encoding="utf-8", errors="replace")
        assert len(content) > 100
        assert "IFC" in content.upper()
