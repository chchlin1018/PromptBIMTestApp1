"""P25 Documentation tests — verify docs integrity and code examples."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent


class TestDocumentation:
    """Documentation integrity tests."""

    def test_key_docs_exist(self):
        """All required documentation files must exist."""
        required = [
            "docs/API.md",
            "docs/DEMO_SCRIPT.md",
            "docs/architecture/v3_system_design.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "CLAUDE.md",
            "SKILL.md",
        ]
        for doc in required:
            path = ROOT / doc
            assert path.exists(), f"Missing required doc: {doc}"
            assert path.stat().st_size > 100, f"Doc too small: {doc}"

    def test_api_doc_version_current(self):
        """API.md should reference the current version."""
        api_md = (ROOT / "docs" / "API.md").read_text(encoding="utf-8")
        assert "v2.12.0" in api_md, "API.md not updated to v2.12.0"

    def test_no_broken_internal_references(self):
        """Check that referenced scripts exist."""
        scripts = [
            "scripts/benchmark_pipeline.py",
            "scripts/benchmark_memory.py",
            "scripts/measure_startup.py",
            "scripts/generate_api_docs.py",
            "scripts/setup_windows.ps1",
        ]
        for script in scripts:
            path = ROOT / script
            assert path.exists(), f"Referenced script missing: {script}"
