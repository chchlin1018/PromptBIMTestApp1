# Contributing to PromptBIM

Thank you for your interest in contributing to PromptBIM! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.11+
- conda (for ifcopenshell)
- Xcode (macOS only, for Swift/SwiftUI shell)
- CMake 3.20+ (for C++ library)

### Quick Start

**macOS:**
```bash
conda create -n promptbim python=3.11 -y
conda activate promptbim
conda install -c conda-forge ifcopenshell -y
pip install -e ".[dev]"
pip install usd-core qasync pytest-timeout
```

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_windows.ps1
```

### Environment Variables

```bash
export QT_QPA_PLATFORM=offscreen  # Required for headless testing
```

## Code Standards

- **Linter:** ruff (configured in `pyproject.toml`)
- **Line length:** 100 characters
- **Python:** 3.11+ (type hints, `from __future__ import annotations`)
- **Paths:** Always use `pathlib.Path`, never `os.path`
- **File I/O:** Always specify `encoding="utf-8"`

### Run lint

```bash
ruff check src/ tests/
```

## Testing

### Running Tests (Safe Mode)

```bash
export QT_QPA_PLATFORM=offscreen
pkill -f "python.*pytest" 2>/dev/null; sleep 1
python -m pytest tests/ \
    --timeout=10 \
    --ignore=tests/test_gui \
    --ignore=tests/test_mcp \
    --ignore=tests/test_e2e_integration.py \
    -x --tb=short -q
```

### Important Testing Rules

1. **Never run multiple pytest processes simultaneously** (16GB Mac Mini OOM risk)
2. **Always set `QT_QPA_PLATFORM=offscreen`** before running tests
3. **Always kill zombie pytest processes** before and after test runs
4. `tests/conftest.py` must have `os.environ["QT_QPA_PLATFORM"] = "offscreen"` at the very top

### Test Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.benchmark` | Performance benchmarks |
| `@pytest.mark.integration` | Requires real environment |
| `@pytest.mark.api` | Requires Claude API key |
| `@pytest.mark.slow` | Tests taking > 10 seconds |
| `@pytest.mark.macos_only` | macOS-only tests |
| `@pytest.mark.windows_only` | Windows-only tests |

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Ensure all tests pass (safe mode)
4. Run `ruff check src/ tests/`
5. Submit a PR with a clear description

## Project Structure

```
src/promptbim/
  agents/       # AI agent pipeline (orchestrator, planner, builder, etc.)
  bim/          # BIM generators (IFC, USD), geometry, materials, cost, MEP
  codes/        # Taiwan building code compliance
  land/         # Land parcel parsers (GeoJSON, SHP, DXF, KML, PDF, image)
  schemas/      # Pydantic data models
  gui/          # PySide6 desktop GUI
  cache/        # Plan caching
  startup/      # Health checks and auto-fix
tests/          # pytest test suite
scripts/        # Dev/ops scripts (benchmarks, setup, etc.)
libpromptbim/   # C++ core library
```

## Governance Files

- `CLAUDE.md` — Claude Code development guidelines (DO NOT MODIFY)
- `SKILL.md` — Sprint skill documentation (DO NOT MODIFY)

These files are maintained by the project lead and must not be modified by contributors.

---

*CONTRIBUTING.md v1.0 | 2026-03-27 | PromptBIM v2.12.0*
