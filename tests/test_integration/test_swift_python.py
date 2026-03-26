"""P24 Task 23: Swift ↔ Python integration tests.

Tests the Python-side interfaces that the Swift app calls via subprocess/bridge.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestSwiftPythonBridge:
    """Test Python interfaces used by Swift PythonBridge."""

    def test_demo_plan_json_serializable(self):
        """BuildingPlan from demo_data can be serialized to JSON for Swift."""
        from promptbim.demo.demo_data import get_demo_plan

        plan = get_demo_plan()
        json_str = plan.model_dump_json()
        data = json.loads(json_str)
        assert "stories" in data
        assert len(data["stories"]) == 3
        # Verify Swift-compatible field names
        for story in data["stories"]:
            assert "name" in story
            assert "height_m" in story
            assert "elevation_m" in story

    def test_demo_result_json_for_swift(self):
        """GenerationResult JSON is compatible with Swift NativeBIMBridge."""
        from promptbim.demo.demo_data import get_demo_result

        result = get_demo_result()
        data = json.loads(result.model_dump_json())
        assert data["success"] is True
        assert "summary" in data
        assert "compliance_report" in data

    def test_cli_version_output(self):
        """Python CLI returns version string (Swift calls this to check)."""
        result = subprocess.run(
            [sys.executable, "-c", "from promptbim import __version__; print(__version__)"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        version = result.stdout.strip()
        assert len(version.split(".")) >= 2  # semver-like

    def test_demo_resources_generate_for_swift(self):
        """generate_all_demo_resources produces files Swift SceneKit can load."""
        from promptbim.demo.demo_data import generate_demo_svg

        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paths = generate_demo_svg(output_dir=tmp_path)
            assert len(paths) >= 4
            # SVGs should be valid XML for Swift WebView
            for p in paths:
                content = p.read_text()
                assert content.startswith("<svg") or "xmlns" in content
