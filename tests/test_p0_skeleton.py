"""P0 Sprint tests — verify project skeleton is properly set up."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


class TestProjectStructure:
    """Verify all required directories and files exist."""

    @pytest.mark.parametrize(
        "path",
        [
            "src/promptbim/__init__.py",
            "src/promptbim/__main__.py",
            "src/promptbim/config.py",
            "src/promptbim/gui/__init__.py",
            "src/promptbim/gui/main_window.py",
            "src/promptbim/land/__init__.py",
            "src/promptbim/agents/__init__.py",
            "src/promptbim/bim/__init__.py",
            "src/promptbim/viz/__init__.py",
            "src/promptbim/voice/__init__.py",
            "src/promptbim/schemas/__init__.py",
            "src/promptbim/schemas/land.py",
            "src/promptbim/schemas/zoning.py",
            "src/promptbim/schemas/plan.py",
            "src/promptbim/schemas/requirement.py",
            "src/promptbim/schemas/result.py",
            "src/promptbim/land/parsers/__init__.py",
            "src/promptbim/bim/templates/__init__.py",
            "src/promptbim/codes/__init__.py",
            "src/promptbim/mcp/__init__.py",
            "pyproject.toml",
            ".env.example",
            "LICENSE",
        ],
    )
    def test_file_exists(self, path):
        assert (ROOT / path).exists(), f"Missing: {path}"

    def test_xcode_project_exists(self):
        assert (ROOT / "PromptBIMTestApp1.xcodeproj" / "project.pbxproj").exists()

    def test_swift_files_exist(self):
        swift_dir = ROOT / "PromptBIMTestApp1"
        assert (swift_dir / "PromptBIMTestApp1App.swift").exists()
        assert (swift_dir / "ContentView.swift").exists()
        assert (swift_dir / "PythonBridge.swift").exists()
        assert (swift_dir / "Info.plist").exists()
        assert (swift_dir / "PromptBIMTestApp1.entitlements").exists()
        assert (swift_dir / "Assets.xcassets").is_dir()


class TestPythonPackage:
    """Verify Python package imports work."""

    def test_import_promptbim(self):
        import promptbim

        assert hasattr(promptbim, "__version__")
        assert promptbim.__version__ == "2.6.0"

    def test_import_config(self):
        from promptbim.config import get_settings

        settings = get_settings()
        assert settings.log_level == "INFO"
        assert settings.claude_model == "claude-sonnet-4-20250514"

    def test_import_schemas(self):
        from promptbim.schemas.land import LandParcel
        from promptbim.schemas.plan import BuildingPlan
        from promptbim.schemas.zoning import ZoningRules

        # Test LandParcel creation
        parcel = LandParcel(
            boundary=[(0, 0), (30, 0), (30, 20), (0, 20)],
            area_sqm=600.0,
        )
        assert parcel.area_sqm == 600.0
        assert len(parcel.boundary) == 4

        # Test ZoningRules defaults
        zoning = ZoningRules()
        assert zoning.far_limit == 2.0
        assert zoning.bcr_limit == 0.6

        # Test BuildingPlan creation
        plan = BuildingPlan(name="Test Building")
        assert plan.name == "Test Building"
        assert len(plan.stories) == 0

    def test_cli_version(self):
        env = {**__import__("os").environ, "PYTHONPATH": str(ROOT / "src")}
        result = subprocess.run(
            [sys.executable, "-m", "promptbim", "--version"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            env=env,
        )
        assert result.returncode == 0
        assert "2.6.0" in result.stdout
