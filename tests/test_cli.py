"""Tests for CLI commands — version, generate, check."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

PYTHON = sys.executable
FIXTURES = Path(__file__).parent / "fixtures"


def _run_cli(*args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run `python -m promptbim <args>` and capture output."""
    return subprocess.run(
        [PYTHON, "-m", "promptbim", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(Path(__file__).parent.parent),
    )


class TestVersionOutput:
    def test_version_flag(self):
        result = _run_cli("--version")
        assert result.returncode == 0
        assert "promptbim" in result.stdout

    def test_version_contains_number(self):
        result = _run_cli("--version")
        import re

        assert re.search(r"\d+\.\d+\.\d+", result.stdout)


class TestGenerateCommand:
    @pytest.mark.api
    @pytest.mark.slow
    def test_generate_no_land(self, tmp_path):
        """Generate with default 30x30 land parcel."""
        outdir = str(tmp_path / "gen_out")
        result = _run_cli("generate", "3-story villa", "-o", outdir, timeout=120)
        assert result.returncode == 0
        assert (Path(outdir) / "result.json").exists()

    @pytest.mark.api
    @pytest.mark.slow
    def test_generate_with_geojson(self, tmp_path):
        """Generate with a GeoJSON land file."""
        geojson = FIXTURES / "sample_parcel.geojson"
        if not geojson.exists():
            pytest.skip("sample_parcel.geojson fixture not found")
        outdir = str(tmp_path / "geo_out")
        result = _run_cli(
            "generate", "simple office", "--land", str(geojson), "-o", outdir, timeout=120
        )
        assert result.returncode == 0
        assert (Path(outdir) / "result.json").exists()

    @pytest.mark.api
    @pytest.mark.slow
    def test_generate_result_json_valid(self, tmp_path):
        """Verify result.json is valid JSON with expected fields."""
        outdir = str(tmp_path / "json_out")
        result = _run_cli("generate", "2-story house", "-o", outdir, timeout=120)
        assert result.returncode == 0
        result_json = Path(outdir) / "result.json"
        assert result_json.exists()
        data = json.loads(result_json.read_text())
        assert data["success"] is True
        assert "building_name" in data
        assert "summary" in data

    @pytest.mark.api
    @pytest.mark.slow
    def test_generate_output_shows_stories(self, tmp_path):
        """CLI output should mention number of stories."""
        outdir = str(tmp_path / "story_out")
        result = _run_cli("generate", "single story box", "-o", outdir, timeout=120)
        assert result.returncode == 0
        assert "Stories:" in result.stdout

    def test_generate_bad_land_file(self, tmp_path):
        """Should fail gracefully with non-existent land file."""
        result = _run_cli(
            "generate", "house", "--land", "/nonexistent/file.geojson", "-o", str(tmp_path)
        )
        assert result.returncode != 0

    @pytest.mark.api
    @pytest.mark.slow
    def test_generate_city_option(self, tmp_path):
        """--city option should be accepted."""
        outdir = str(tmp_path / "city_out")
        result = _run_cli("generate", "house", "-o", outdir, "--city", "Kaohsiung", timeout=120)
        assert result.returncode == 0

    @pytest.mark.api
    @pytest.mark.slow
    def test_generate_format_option(self, tmp_path):
        """--format option should be accepted."""
        outdir = str(tmp_path / "fmt_out")
        result = _run_cli("generate", "house", "-o", outdir, "--format", "both", timeout=120)
        assert result.returncode == 0


class TestGenerateUnit:
    """Unit tests for generate-related functions (no subprocess/API)."""

    def test_load_land_file_nonexistent(self):
        """_load_land_file should call sys.exit for missing files."""
        from promptbim.__main__ import _load_land_file

        with pytest.raises(SystemExit):
            _load_land_file("/nonexistent/file.geojson")

    def test_cli_status_callback(self, capsys):
        """_cli_status should print progress."""
        from promptbim.__main__ import _cli_status
        from promptbim.agents.orchestrator import PipelineStatus

        _cli_status(PipelineStatus(stage="builder", message="Building...", progress=0.5))
        captured = capsys.readouterr()
        assert "builder" in captured.out
        assert "50%" in captured.out

    def test_generate_parser_accepts_options(self):
        """Verify argparse accepts all generate options."""
        # Just verify --help works (no API call)
        result = _run_cli("generate", "--help")
        assert "--land" in result.stdout
        assert "--format" in result.stdout
        assert "--city" in result.stdout
        assert "--template" in result.stdout


class TestCheckCommand:
    def test_check_runs(self):
        """Health check should run without crashing."""
        result = _run_cli("check")
        assert "PromptBIM" in result.stdout or result.returncode in (0, 1)

    def test_check_json(self):
        """--json flag should produce valid JSON output."""
        result = _run_cli("check", "--json")
        if result.returncode in (0, 1):
            data = json.loads(result.stdout)
            assert "summary" in data
            assert "results" in data


class TestHelpOutput:
    def test_no_args_shows_help(self):
        result = _run_cli()
        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "promptbim" in result.stdout.lower()

    def test_generate_help(self):
        result = _run_cli("generate", "--help")
        assert result.returncode == 0
        assert "prompt" in result.stdout.lower()
