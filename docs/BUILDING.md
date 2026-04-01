# BUILDING.md — PromptBIM Build Guide

## Prerequisites

### All Platforms
- CMake 3.25+
- C++20 compiler
- Python 3.11+ (for pybind11 bindings)
- Git

### Windows
- Visual Studio 2022 (v17.14+) with C++ Desktop workload
- pybind11: `pip install pybind11`

### macOS
- Xcode Command Line Tools or Clang 15+
- pybind11: `pip install pybind11`

---

## Quick Build

### Windows (MSVC)

```powershell
# Configure
cmake -B build-win -G "Visual Studio 17 2022" -A x64 ^
  -Dpybind11_DIR=$(python -c "import pybind11; print(pybind11.get_cmake_dir())")

# Build
cmake --build build-win --config Release

# Test
cd build-win && ctest -C Release --output-on-failure
```

### macOS (Clang)

```bash
# Configure
cmake -B build -G "Unix Makefiles" \
  -Dpybind11_DIR=$(python3 -c "import pybind11; print(pybind11.get_cmake_dir())")

# Build
cmake --build build --config Release

# Test
cd build && ctest --output-on-failure
```

---

## Build Targets

| Target | Description | Output |
|--------|-------------|--------|
| `promptbim_core` | Compliance + Cost engines | `.lib` / `.a` |
| `bim_core_static` | BIM core (Entity, SceneGraph, Agent, Geometry, Property, Cost) | `.lib` / `.a` |
| `bim_core` | pybind11 Python module | `.pyd` / `.so` |
| `promptbim_tests` | GoogleTest (Compliance + Cost) | executable |
| `bim_core_tests` | GoogleTest (Entity, SceneGraph, Agent, Binding, TSMC Demo) | executable |

## CMake Options

| Option | Default | Description |
|--------|---------|-------------|
| `BUILD_TESTS` | ON | Build GoogleTest unit tests |
| `BUILD_PYTHON_BINDINGS` | ON | Build pybind11 Python bindings |

## Python Binding Usage

```python
import sys
sys.path.insert(0, "build-win/cpp/binding/Release")  # Windows
# sys.path.insert(0, "build/cpp/binding")             # macOS

import bim_core

sg = bim_core.BIMSceneGraph()
bridge = bim_core.AgentBridge(sg)
result = bridge.execute_json('{"action":"get_scene_info"}')
```

---

*BUILDING.md | PromptBIM v3.1.0 | 2026-04-01*
