"""P24 Task 20: CI/CD + infrastructure tests."""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestVersionSync:
    """Ensure version numbers are consistent across files."""

    def _get_pyproject_version(self):
        text = (PROJECT_ROOT / "pyproject.toml").read_text()
        m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
        return m.group(1) if m else None

    def _get_init_version(self):
        text = (PROJECT_ROOT / "src" / "promptbim" / "__init__.py").read_text()
        m = re.search(r'__version__\s*=\s*"([^"]+)"', text)
        return m.group(1) if m else None

    def test_pyproject_has_version(self):
        assert self._get_pyproject_version() is not None

    def test_init_has_version(self):
        assert self._get_init_version() is not None

    def test_versions_match(self):
        assert self._get_pyproject_version() == self._get_init_version()


class TestCIWorkflow:
    """Ensure CI workflow file is valid."""

    def test_ci_yml_exists(self):
        ci = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        assert ci.exists()

    def test_ci_has_lint_and_test(self):
        text = (PROJECT_ROOT / ".github" / "workflows" / "ci.yml").read_text()
        assert "ruff check" in text
        assert "pytest" in text


class TestScriptsExist:
    """Ensure dev scripts are in place."""

    def test_sync_version_script(self):
        assert (PROJECT_ROOT / "scripts" / "sync_version.sh").exists()

    def test_dev_setup_script(self):
        assert (PROJECT_ROOT / "scripts" / "dev_setup.sh").exists()
