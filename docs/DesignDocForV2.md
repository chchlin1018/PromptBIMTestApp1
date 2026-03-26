# PromptBIM V2 — 架構設計文件

> 文件版本: v1.0.0
> 建立日期: 2026-03-26
> 作者: Michael Lin (林志錚) / Claude Opus 4.6
> 狀態: Draft — 待分析後建立 Sprint Tasks
> 組織: Reality Matrix Inc.

---

## 1. 背景與動機

### 1.1 V1 (POC) 現狀

PromptBIMTestApp1 v1.4.0 作為 POC 驗證了完整的 AI-driven BIM 生成能力：

- **18 個 Sprint**，**675+ tests**，**50+ Python 模組**
- 功能鏈：土地匯入 → AI 生成 → 法規檢查 → 成本估算 → MEP → 施工模擬 → 監控點
- 輸出：IFC + USD + USDZ
- 介面：PySide6 GUI + SwiftUI Splash + Streamlit Web + MCP Server

### 1.2 為什麼需要 V2

| 限制 | 影響 |
|------|------|
| Python-only 後端 | 啟動慢（模組載入）、部署需 conda 環境 |
| macOS-only GUI (PySide6 + SwiftUI) | 無法在 Windows 上執行 |
| 無 Web 部署能力（Streamlit 僅 demo 用）| 無法提供 SaaS 服務 |
| 依賴 Python binding 呼叫 C++ 庫 | 多一層 overhead、安裝複雜 |

### 1.3 V2 目標

1. **跨平台** — macOS + Windows (Win11/VS Compiler) + Web
2. **效能** — 核心引擎直接使用 C++ 原生庫，去除 Python binding 層
3. **部署彈性** — Desktop app + Web app + CLI 三種形態
4. **AI 靈活性** — AI 層保持快速迭代能力
5. **漸進遷移** — 不重寫，逐步將 POC 代碼轉為產品級架構

---

## 2. 架構方案評估

### 2.1 方案比較

| 方案 | 跨平台 | 效能 | AI 開發效率 | 工程量 | 結論 |
|------|:------:|:----:|:----------:|:------:|:----:|
| A: 全部轉 Swift | ❌ 不支援 Windows | ⭐⭐⭐ | ⭐⭐ | 極高 | 不可行 |
| B: 全部轉 C++ | ✅ | ⭐⭐⭐⭐ | ⭐ | 極高 | 代價過高 |
| C: Python 保持現狀 | ⚠️ 需 conda | ⭐⭐ | ⭐⭐⭐⭐ | 低 | POC 可以，產品不足 |
| **D: 混合架構（推薦）** | **✅** | **⭐⭐⭐⭐** | **⭐⭐⭐⭐** | **中** | **最佳平衡** |

### 2.2 選擇方案 D 的理由

- **BIM/GIS 核心**：ifcopenshell、USD、GDAL/GEOS 本來就是 C++ 庫的 Python binding，「轉回 C++」不是重寫，而是去掉包裝層
- **AI 層**：Prompt engineering、JSON 解析、API 呼叫在 Python/TypeScript 中的開發效率是 C++ 的 5 倍以上，且變動最頻繁
- **UI 層**：各平台有最佳原生方案（SwiftUI / WinUI 3 / Web），強用單一技術只會降低體驗

---

## 3. V2 目標架構

```
┌─────────────────────────────────────────────────────────────────┐
│                      Platform UI Layer                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   macOS       │  │   Windows    │  │   Web Browser        │  │
│  │   SwiftUI +   │  │   WinUI 3    │  │   React/Vue +        │  │
│  │   SceneKit /  │  │   or Qt C++  │  │   Three.js / WASM    │  │
│  │   RealityKit  │  │              │  │                      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                  │                      │             │
└─────────┼──────────────────┼──────────────────────┼─────────────┘
          │   C ABI / FFI    │   C ABI / FFI        │  REST/gRPC
          │                  │                      │  + WASM
┌─────────┴──────────────────┴──────────────────────┴─────────────┐
│                                                                 │
│              C++ Core Library (libpromptbim)                     │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ BIM Engine   │  │ GIS Engine  │  │ Compliance Engine       │ │
│  │ IFC生成      │  │ GDAL/OGR    │  │ 台灣法規15+規則        │ │
│  │ USD生成      │  │ GEOS        │  │ (純邏輯,最易轉)        │ │
│  │ USDZ打包     │  │ 座標投影    │  │                        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Cost Engine  │  │ MEP Engine  │  │ Simulation Engine       │ │
│  │ QTO + 估算   │  │ A* 尋路     │  │ 4D排程 + GIF動畫       │ │
│  │ (純邏輯)     │  │ (效能敏感)  │  │                        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                 │
│  Build: CMake + vcpkg (macOS/Windows/WASM)                      │
│  Language: C++17, C ABI exports for FFI                         │
│  Test: GoogleTest / Catch2                                      │
│                                                                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │  HTTP REST / gRPC / IPC
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                                                                 │
│                   AI Service Layer                               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Agent Orchestrator (Python or Node.js)                    │   │
│  │                                                           │   │
│  │  EnhancerAgent ─→ PlannerAgent ─→ BuilderAgent            │   │
│  │       │                                    │              │   │
│  │       ↓                                    ↓              │   │
│  │  CheckerAgent ←─ ModifierAgent    LandReaderAgent         │   │
│  │                                   (Vision API)            │   │
│  │                                                           │   │
│  │  - Claude API client                                      │   │
│  │  - Prompt 模板管理                                        │   │
│  │  - JSON 解析 + fallback 邏輯                              │   │
│  │  - 版本歷史 + undo                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Runtime: Python 3.11+ / Node.js 20+                            │
│  Deployment: Embedded process / Standalone microservice          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. 各層詳細設計

### 4.1 C++ Core Library (libpromptbim)

#### 4.1.1 建構系統

```
libpromptbim/
├── CMakeLists.txt              # 頂層 CMake
├── vcpkg.json                  # C++ 套件管理
├── include/
│   └── promptbim/
│       ├── promptbim.h          # C ABI public header
│       ├── bim_engine.h
│       ├── gis_engine.h
│       ├── compliance_engine.h
│       ├── cost_engine.h
│       ├── mep_engine.h
│       └── simulation_engine.h
├── src/
│   ├── bim/                     # IFC + USD + USDZ
│   ├── gis/                     # GDAL + GEOS
│   ├── compliance/              # 法規引擎
│   ├── cost/                    # QTO + 估算
│   ├── mep/                     # A* pathfinding
│   └── simulation/              # 4D scheduler
├── bindings/
│   ├── python/                  # pybind11 binding (向下相容 V1)
│   ├── swift/                   # Swift C interop
│   └── wasm/                    # Emscripten binding
└── tests/
    └── ...                      # GoogleTest
```

#### 4.1.2 C ABI 設計

```c
// include/promptbim/promptbim.h
#pragma once

#ifdef __cplusplus
extern "C" {
#endif

// --- BIM Engine ---
typedef struct PBPlan PBPlan;
typedef struct PBGenerateResult PBGenerateResult;

PBPlan* pb_plan_from_json(const char* json_str);
void    pb_plan_free(PBPlan* plan);
char*   pb_plan_to_json(const PBPlan* plan);

int     pb_generate_ifc(const PBPlan* plan, const char* output_path);
int     pb_generate_usd(const PBPlan* plan, const char* output_path);
int     pb_generate_usdz(const char* usd_path, const char* output_path);

// --- GIS Engine ---
typedef struct PBLandParcel PBLandParcel;

PBLandParcel* pb_land_from_geojson(const char* path);
PBLandParcel* pb_land_from_shapefile(const char* path);
PBLandParcel* pb_land_from_dxf(const char* path);
void          pb_land_free(PBLandParcel* parcel);

// --- Compliance Engine ---
typedef struct PBComplianceResult PBComplianceResult;

PBComplianceResult* pb_check_compliance(const PBPlan* plan,
                                         const PBLandParcel* land,
                                         const char* zoning_json);
char* pb_compliance_to_json(const PBComplianceResult* result);
void  pb_compliance_free(PBComplianceResult* result);

// --- Cost Engine ---
char* pb_estimate_cost(const PBPlan* plan);  // returns JSON

// --- MEP Engine ---
char* pb_plan_mep(const PBPlan* plan, const char* config_json);

// --- Simulation Engine ---
char* pb_generate_schedule(const PBPlan* plan, int total_days);

// --- Utility ---
void pb_free_string(char* str);  // free JSON strings
const char* pb_version(void);

#ifdef __cplusplus
}
#endif
```

#### 4.1.3 核心依賴（全部原生 C/C++）

| 模組 | C++ 依賴 | vcpkg 套件 | 說明 |
|------|----------|-----------|------|
| BIM | IfcOpenShell C++ | `ifcopenshell` | 直接呼叫 C++ API，去除 Python binding |
| BIM | Pixar USD C++ | `usd` | 直接呼叫 pxr:: namespace |
| GIS | GDAL/OGR | `gdal` | 取代 geopandas/fiona |
| GIS | GEOS | `geos` | 取代 shapely |
| GIS | PROJ | `proj` | 取代 pyproj |
| Geometry | earcut.hpp | `earcut` | 取代 mapbox-earcut Python |
| JSON | nlohmann/json | `nlohmann-json` | 取代 Python json |
| Test | GoogleTest | `gtest` | C++ 測試框架 |

#### 4.1.4 遷移優先順序

| 優先級 | 模組 | 原因 | 難度 |
|:------:|------|------|:----:|
| 1 | Compliance Engine | 純邏輯無外部依賴，最易轉換 | ⭐ |
| 2 | Cost Engine | 純邏輯 + 簡單數學 | ⭐ |
| 3 | MEP Engine (A*) | 效能敏感，C++ 提升最明顯 | ⭐⭐ |
| 4 | Simulation Engine | 純邏輯 + 排程算法 | ⭐⭐ |
| 5 | BIM Engine (IFC) | 已是 C++ binding，去包裝 | ⭐⭐⭐ |
| 6 | BIM Engine (USD) | 已是 C++ binding，去包裝 | ⭐⭐⭐ |
| 7 | GIS Engine | GDAL API 較複雜 | ⭐⭐⭐⭐ |

---

### 4.2 AI Service Layer

#### 4.2.1 為什麼保留 Python/Node.js

| 因素 | 說明 |
|------|------|
| Prompt 工程 | 字串模板頻繁修改，Python 開發效率 5x |
| JSON 解析 | 非結構化 AI 回應需要彈性解析 |
| SDK 支援 | Anthropic 官方 SDK 只有 Python / TypeScript |
| 變動頻率 | AI 模型更新、prompt 調整是最頻繁的變更 |
| 測試迭代 | Mock API + 快速 pytest 驗證 |

#### 4.2.2 部署模式

**模式 A: Embedded Process**（Desktop App 使用）
```
Desktop App → spawn → Python/Node.js AI service → IPC/stdin/stdout → C++ Core
```
- 類似 V1 的 PythonBridge 模式
- 優點：離線可用、延遲最低
- 缺點：需要安裝 Python/Node.js runtime

**模式 B: Standalone Microservice**（Web / Cloud 使用）
```
Web Client → HTTPS → AI Service (FastAPI/Express) → libpromptbim (FFI) → Response
```
- 優點：無需用戶安裝 runtime
- 缺點：需要網路連接

**模式 C: Hybrid**（推薦）
- Desktop: 優先 Embedded，fallback 到 Cloud
- Web: 永遠走 Cloud

---

### 4.3 Platform UI Layer

#### 4.3.1 macOS

| 技術 | 用途 |
|------|------|
| SwiftUI | UI 框架 |
| SceneKit / RealityKit | 3D 預覽（取代 PyVista）|
| Metal | GPU 加速渲染 |
| libpromptbim | 透過 Swift C interop 呼叫 |

#### 4.3.2 Windows (Win11)

| 方案 | 優點 | 缺點 |
|------|------|------|
| **Qt 6 (C++)** | 跨平台、直接呼叫 libpromptbim、成熟 3D (Qt3D) | 授權費用（商用 GPL/Commercial）|
| **WinUI 3 (C#/C++)** | Windows 原生體驗最佳 | 僅 Windows |
| **.NET MAUI + C# binding** | 跨平台 | 3D 能力弱 |

**建議: Qt 6 (C++)**
- 與 libpromptbim 同為 C++，無 FFI overhead
- Qt3D 可取代 PyVista
- macOS 也可以用 Qt 統一（但犧牲 SwiftUI 原生體驗）
- CMake 整合良好

#### 4.3.3 Web Browser

| 技術 | 用途 |
|------|------|
| React / Vue 3 | UI 框架 |
| Three.js / Babylon.js | 3D BIM 預覽 |
| WASM (Emscripten) | libpromptbim 核心引擎在瀏覽器運行 |
| REST API | 連接後端 AI Service |

---

## 5. WASM 策略（Future Feature）

### 5.1 WASM 的定位

WASM 讓 libpromptbim 的核心引擎可以直接在瀏覽器中運行，實現：
- **離線 BIM 生成**（不需後端）
- **低延遲法規檢查**（本地計算）
- **降低伺服器成本**（計算下放到客戶端）

### 5.2 WASM Bundle 體積分析

| 模組 | 預估 WASM 體積 | 是否必要在客戶端 |
|------|:-------------:|:--------------:|
| Compliance Engine | ~2 MB | ✅ 即時檢查 |
| Cost Engine | ~1 MB | ✅ 即時估算 |
| MEP A* | ~3 MB | ⚠️ 可選 |
| Simulation | ~2 MB | ⚠️ 可選 |
| BIM IFC (IfcOpenShell) | ~15 MB | ❌ 太大，留後端 |
| BIM USD (Pixar) | ~20 MB | ❌ 太大，留後端 |
| GIS (GDAL) | ~25 MB | ❌ 太大，留後端 |
| **必要模組合計** | **~3 MB** | |
| **全量模組合計** | **~30-50 MB** | |

### 5.3 WASM 載入策略

**⚠️ 30-50MB 的 WASM bundle 體積在未來場景中不是問題**，原因：

1. **Progressive Loading** — 先載入必要模組（3MB），其餘按需載入
2. **Service Worker 快取** — 首次載入後快取在本地，後續秒開
3. **CDN 分發 + Brotli 壓縮** — 50MB 原始 → ~12MB 傳輸
4. **目標用戶是專業工程師** — 工作場景有穩定網路
5. **競品參考** — AutoCAD Web (~60MB WASM)、Figma (~15MB WASM) 已驗證可行

### 5.4 WASM 分層載入設計

```
初始載入 (< 500ms):
  → promptbim-core.wasm (~1MB) — 基礎型別 + JSON 序列化

互動時載入:
  → promptbim-compliance.wasm (~2MB) — 法規檢查
  → promptbim-cost.wasm (~1MB) — 成本估算

按需載入:
  → promptbim-mep.wasm (~3MB) — MEP 管線
  → promptbim-simulation.wasm (~2MB) — 施工模擬

永遠在後端:
  → IFC 生成 / USD 生成 / GIS 解析 / AI Agents
```

### 5.5 Emscripten Build 設定

```cmake
# CMakeLists.txt WASM target
if(EMSCRIPTEN)
    set(CMAKE_EXECUTABLE_SUFFIX ".js")
    target_link_options(promptbim-core PRIVATE
        "SHELL:-s MODULARIZE=1"
        "SHELL:-s EXPORT_NAME=PromptBIM"
        "SHELL:-s EXPORTED_FUNCTIONS=['_pb_version','_pb_check_compliance','_pb_estimate_cost','_pb_free_string']"
        "SHELL:-s EXPORTED_RUNTIME_METHODS=['ccall','cwrap','UTF8ToString']"
        "SHELL:-s ALLOW_MEMORY_GROWTH=1"
        "SHELL:-s TOTAL_MEMORY=67108864"  # 64MB initial
    )
endif()
```

---

## 6. 遷移路線圖

### Phase 0: 準備（與 V1 P13-P14 並行）

- 建立 `libpromptbim/` CMake 骨架 + vcpkg 設定
- 定義 C ABI header (`promptbim.h`)
- 建立 GoogleTest 框架
- **不重寫任何程式碼**，只建立骨架

### Phase 1: 純邏輯模組遷移

- Compliance Engine → C++ （純邏輯，最易轉）
- Cost Engine → C++
- pybind11 binding 讓 V1 Python 可呼叫 C++ 版本
- 驗證：C++ 版與 Python 版輸出一致

### Phase 2: 效能敏感模組

- MEP A* → C++（效能提升最明顯）
- Simulation Engine → C++
- 建立效能基準對照

### Phase 3: BIM 核心

- IFC Generator → 直接呼叫 IfcOpenShell C++ API
- USD Generator → 直接呼叫 pxr:: namespace
- USDZ Packer → C++ zip 封裝

### Phase 4: GIS + 平台 UI

- GIS → GDAL/OGR C API
- macOS: SwiftUI + SceneKit 3D
- Windows: Qt 6 C++ 移植

### Phase 5: Web + WASM

- Emscripten 編譯 libpromptbim
- React/Vue 前端 + Three.js 3D
- REST API 連接 AI Service

---

## 7. 向下相容策略

### 7.1 V1 Python 繼續運行

在整個遷移過程中，V1 的 Python 代碼繼續作為主要執行路徑。
每個 C++ 模組完成後，透過 pybind11 binding 讓 V1 可選擇性呼叫 C++ 版本：

```python
# V1 Python code — 自動選擇最佳引擎
try:
    from promptbim._native import check_compliance  # C++ 版本
    logger.info("Using native C++ compliance engine")
except ImportError:
    from promptbim.codes.registry import run_all_checks as check_compliance  # Python fallback
    logger.info("Using Python compliance engine")
```

### 7.2 測試一致性

每個 C++ 模組必須通過與 Python 版相同的測試案例：

```
tests/
├── fixtures/                    # 共用測試資料
│   ├── sample_plan.json
│   ├── sample_land.geojson
│   └── expected_results/
├── test_compliance_python.py    # Python 版測試
└── test_compliance_cpp.py       # C++ binding 測試（相同 fixtures）
```

---

## 8. Windows (Win11/VS) 相容性設計

### 8.1 編譯器要求

- **MSVC 2022** (v17+) — C++17 完整支援
- **CMake 3.24+** — 跨平台建構
- **vcpkg** — C++ 套件管理（微軟維護，與 VS 深度整合）

### 8.2 平台差異處理

| 差異 | macOS | Windows | 處理方式 |
|------|-------|---------|----------|
| 路徑分隔 | `/` | `\` | 使用 `std::filesystem::path` |
| 動態庫 | `.dylib` | `.dll` | CMake 自動處理 |
| 編碼 | UTF-8 | UTF-8 (Win11) | 統一 UTF-8，Win10 用 `SetConsoleOutputCP(65001)` |
| IPC | Unix socket | Named pipe | 抽象 IPC 層 |
| 安裝路徑 | `/usr/local` | `%PROGRAMFILES%` | CMake install prefix |

### 8.3 CI/CD 矩陣

```yaml
# .github/workflows/ci.yml
jobs:
  build:
    strategy:
      matrix:
        os: [macos-14, windows-2022, ubuntu-22.04]
        include:
          - os: macos-14
            cmake_args: "-DCMAKE_OSX_ARCHITECTURES=arm64"
          - os: windows-2022
            cmake_args: "-DCMAKE_TOOLCHAIN_FILE=vcpkg/scripts/buildsystems/vcpkg.cmake"
          - os: ubuntu-22.04
            cmake_args: ""  # for WASM build
```

---

## 9. 技術風險

| 風險 | 影響 | 緩解策略 |
|------|------|----------|
| IfcOpenShell C++ API 文件不足 | 延遲 Phase 3 | 先研究 API，準備 fallback 維持 Python binding |
| WASM 記憶體限制（4GB）| 大型建築 MEP 可能不足 | MEP/GIS 留在後端，WASM 只跑輕量模組 |
| Qt 授權成本 | 商用需 Commercial License | 評估 LGPL 合規或改用 Dear ImGui |
| AI Service 延遲 | 跨境 API 呼叫慢 | 台灣區域 proxy + 快取常見 prompt 結果 |
| 團隊 C++ 能力 | 開發速度 | Claude Code 輔助 C++ 開發 + 漸進遷移 |

---

## 10. 成本估算

| 階段 | 預估工時 | 輸出 |
|------|:--------:|------|
| Phase 0: 骨架 | 2-3 天 | CMake + C ABI header + GoogleTest |
| Phase 1: 純邏輯 | 5-7 天 | Compliance + Cost in C++ |
| Phase 2: 效能 | 5-7 天 | MEP + Simulation in C++ |
| Phase 3: BIM | 7-10 天 | IFC + USD in C++ |
| Phase 4: 平台 | 10-15 天 | Swift UI + Qt Windows |
| Phase 5: Web | 10-15 天 | WASM + React + REST API |
| **總計** | **~40-60 天** | 全面跨平台產品 |

---

## 11. 決策待定項

| 項目 | 選項 | 需要決策 |
|------|------|----------|
| Windows UI | Qt 6 vs WinUI 3 vs Dear ImGui | Qt 授權成本確認後 |
| AI Service 語言 | Python vs Node.js vs 兩者都支援 | 視團隊技能決定 |
| 3D Web 渲染 | Three.js vs Babylon.js | 評估 IFC/USD 載入能力 |
| WASM 時程 | Phase 5 同步或延後 | 視 Web 客戶需求決定 |
| V2 repo | 新 repo vs 同 repo 的 v2 branch | 視團隊偏好 |

---

## 12. 下一步

1. **審閱本文件** — 確認方向正確
2. **建立 Sprint Tasks** — 將 Phase 0-5 拆為可執行的 Sprint Prompt
3. **Phase 0 先行** — 在不影響 V1 P13/P14 進度的情況下建立 C++ 骨架
4. **Windows 環境準備** — 設定 Win11 開發機 + VS 2022 + vcpkg

---

*本文件由 Michael Lin 與 Claude Opus 4.6 協作產出。後續分析整理後將拆為具體 Sprint Tasks。*
