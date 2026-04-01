# PTB-FAR-WIN-001 — Windows Build Audit Report

> **Sprint:** S-PTB-WIN-BUILD | **Date:** 2026-04-01
> **Auditor:** Claude Code (Opus 4.6) | **Machine:** ProArt13 (Windows 11)
> **Version:** mvp-v1.0.0-win

---

## 1. Executive Summary

PromptBIM C++ core successfully compiled and tested on Windows 11 using
Visual Studio 2022 (MSVC v17.14) with CMake. All 90 C++ unit tests pass.
pybind11 Python binding builds and imports correctly. Demo flow verified
with 13/14 AgentBridge JSON actions passing.

**Overall Grade: A (94/100)**

---

## 2. Build Environment

| Item | Value |
|------|-------|
| OS | Windows 11 25H2 (Build 26200) |
| Compiler | MSVC 17.14.40 (Visual Studio 2022 Community) |
| Generator | Visual Studio 17 2022 (x64) |
| CMake | 3.25+ |
| C++ Standard | C++20 |
| Python | 3.11.15 (miniconda3/promptbim) |
| pybind11 | 3.0.3 |
| GoogleTest | v1.14.0 (FetchContent) |
| nlohmann/json | v3.11.3 (FetchContent) |

## 3. Compilation Results

### 3.1 Libraries

| Target | Type | Status |
|--------|------|--------|
| promptbim_core | Static lib (.lib) | PASS |
| bim_core_static | Static lib (.lib) | PASS |
| bim_core (pybind11) | Python module (.pyd) | PASS |

### 3.2 Test Executables

| Target | Status |
|--------|--------|
| promptbim_tests.exe | PASS |
| bim_core_tests.exe | PASS |

### 3.3 Windows-Specific Fixes

| Issue | File | Fix |
|-------|------|-----|
| `M_PI` undefined (MSVC) | `cpp/core/GeometryEngine.cpp` | `M_PI` → `std::numbers::pi` (C++20) |
| `M_PI` undefined (MSVC) | `cpp/tests/test_binding.cpp` | `M_PI` → `std::numbers::pi` (C++20) |

## 4. Test Results

### 4.1 ctest Summary — 90/90 PASS

| Suite | Tests | Status |
|-------|:-----:|:------:|
| ComplianceEngineTest | 8 | PASS |
| CostEngineTest | 6 | PASS |
| BIMEntityTest | 12 | PASS |
| Vec3Test | 1 | PASS |
| SceneGraphTest | 19 | PASS |
| AgentBridgeTest | 18 | PASS |
| BindingTest | 6 | PASS |
| TSMCDemoTest | 20 | PASS |
| **Total** | **90** | **ALL PASS** |

Total test time: 1.75 sec

### 4.2 pybind11 Import Test

```
>>> import bim_core
>>> dir(bim_core)
['ActionResult', 'AgentBridge', 'BIMEntity', 'BIMSceneGraph',
 'CostCalculator', 'CostSummary', 'EntityType', 'GeometryEngine',
 'MaterialSpec', 'PropertyManager', ...]
```

Status: PASS

### 4.3 Demo Flow Test (AgentBridge JSON)

| # | Action | Status |
|---|--------|:------:|
| 1 | Add Chiller | PASS |
| 2 | Add Column | PASS |
| 3 | Add Pump | PASS |
| 4 | Query by type | PASS |
| 5 | Query by name | PASS |
| 6 | Move entity | PASS |
| 7 | Get position | PASS |
| 8 | Get nearby | PASS |
| 9 | Resize entity | PASS |
| 10 | Connect entities | FAIL (no JSON mapping) |
| 11 | Cost delta | PASS |
| 12 | Get scene info | PASS |
| 13 | Delete entity | PASS |
| 14 | Scene after delete | PASS |

Result: **13/14 PASS** (connect only available via C++ API, not JSON dispatch)

## 5. Cross-Platform Parity

| Dimension | macOS (Mac Mini) | Windows (ProArt13) |
|-----------|:----------------:|:------------------:|
| CMake configure | PASS | PASS |
| CMake build | PASS | PASS |
| ctest count | 90/90 | 90/90 |
| pybind11 binding | PASS | PASS |
| Python import | PASS | PASS |
| Demo actions | 13/14 | 13/14 |
| C++ Standard | C++20 | C++20 |

**Parity: 100%** — identical test results on both platforms.

## 6. Scoring

| Dimension | Score | Notes |
|-----------|:-----:|-------|
| Build Correctness | 19/20 | Clean compile, 2 MSVC fixes needed |
| Test Coverage | 19/20 | 90/90 ctest, full suite |
| Cross-Platform | 20/20 | Mac/Win parity 100% |
| pybind11 Binding | 18/20 | Import OK, 13/14 JSON actions |
| Code Quality | 18/20 | C++20 std::numbers::pi > M_PI |
| **Total** | **94/100** | **Grade: A** |

## 7. Warnings (Non-blocking)

- C4819 warnings: source files contain characters outside cp950 (Chinese comments in UTF-8).
  These are cosmetic and do not affect compilation or runtime.
- CMP0148 policy warning from pybind11 3.0.3 — upstream issue, does not affect build.

## 8. Recommendations

1. Consider adding `/source-charset:utf-8` to CMake for MSVC to suppress C4819
2. Add `connect` JSON action mapping to AgentBridge for full parity
3. CI/CD: add Windows build matrix (GitHub Actions `windows-latest`)

---

*PTB-FAR-WIN-001 | S-PTB-WIN-BUILD | 2026-04-01 | ProArt13 Windows 11*
