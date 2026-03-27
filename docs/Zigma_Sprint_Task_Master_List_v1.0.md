# Zigma PromptToBuild — Sprint / Task 總清單 v1.0

> **版本:** v1.0 | **日期:** 2026-03-28
> **來源:** Zigma_MVP_First_Plan_v1.0.md + Zigma_OCCT_QtQuick3D_Migration_Plan_v1.0.md
> **目的:** 完整列出所有 Sprint / Part / Task，標記 Demo 測試點與 Windows 驗證點

---

## ⚠️ Demo 測試點 & Windows 驗證點速查

### 🎯 Demo 測試點

| Tag | 可 Demo 什麼 | 給誰看 |
|-----|-------------|--------|
| **mvp-v0.1.0-alpha** (M1-S1) | 打字 prompt → AI 生成 3D → 旋轉/縮放/點擊屬性 | **內部驗證** — 確認 AgentBridge + 渲染管線通了 |
| **mvp-v0.1.0-beta** (M1-S2) | ★ **完整 TSMC Demo 7 分鐘**: 3 場景 + 成本 + 4D + 設計變更 Delta | **TSMC 預覽** — 核心價值全展現 |
| **mvp-v0.1.0** (M1-S3) | beta 全部 + USD import/export + Dark/Light + 品牌 + crash recovery | **★ TSMC 正式 Demo ★** |
| v2.13.0 (P30) | 上述全部 + **Revit .rvt 輸出** (DirectShape + MEP Pipe) | TSMC 追問 Revit 時展示 |
| v3.0.0 (P32) | 四個工作流全通 + OCCT B-Rep Boolean + 完整 Revit 輸出 | 正式產品 Demo |

### 🪟 Windows 驗證點

| Milestone | Windows 必做 | 環境需求 |
|-----------|-------------|---------|
| **M1-S1 T25** | Win build + run 驗證 | 見下方 §W |
| **M1-S2 T18** | S2 Fab 場景 GPU 渲染驗證 | RTX 4090 |
| **M1-S3 T11** | RTX 4090 GPU 渲染優化 | RTX 4090 + Vulkan/D3D12 |
| **P30** | Revit 2026 整合測試 | Revit 2026 + Python 3.11 |
| **P32** | v3.0.0 Release Win 全面驗證 | 全套環境 |

### §W — Windows 環境配置清單

```
硬體：
  GPU: NVIDIA RTX 4090 (已有)
  RAM: ≥32GB
  Storage: SSD

軟體：
  OS: Windows 11
  Visual Studio: 2022 (MSVC 17.x, C++17)
  CMake: ≥3.21
  Qt: 6.7+ (Quick + Quick3D + Core + ShaderTools)
       → Qt Online Installer → 選 MSVC 2022 64-bit
       → 勾選: Qt Quick 3D, Qt Shader Tools
  Python: 3.11 (miniconda/conda)
  NVIDIA Driver: ≥550.x (Vulkan 1.3 support)

Qt Quick 3D 渲染後端:
  - 預設: D3D12 (Windows)
  - 備選: Vulkan (需 Vulkan SDK 1.3+)
  - 環境變數: QSG_RHI_BACKEND=d3d12 或 vulkan

Phase 2 額外:
  OCCT: OpenCASCADE 7.8+ (vcpkg install opencascade)
  Revit: Autodesk Revit 2026 (P30 io_revit 測試)
  Python packages: usd-core, anthropic, pydantic

vcpkg 安裝:
  vcpkg install opencascade:x64-windows
  vcpkg install pybind11:x64-windows

CMake 配置:
  cmake -B build -G "Visual Studio 17 2022" \
    -DCMAKE_PREFIX_PATH="C:/Qt/6.7.x/msvc2022_64" \
    -DCMAKE_TOOLCHAIN_FILE="C:/vcpkg/scripts/buildsystems/vcpkg.cmake"
```

---

## 完整 Sprint / Part / Task 清單

---

## ✅ 已完成：Demo-1 (34/34 Tasks) — `demo1-v0.1.0`

略（詳見 PROJECT.md v1.5）

---

## 🔴 MVP Phase — 7 週 70 Tasks

### M1-S1: AgentBridge + Qt Quick 3D 骨架 (2.5 週, 25T) → `mvp-v0.1.0-alpha`

#### Part A: AgentBridge — Python↔C++ 通訊 (8T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T1 | CMakeLists.txt | Qt6 Quick + Quick3D + Core + ShaderTools | `cmake --build` 成功 |
| T2 | AgentBridge C++ | QProcess spawn agent_runner.py, JSON stdio, heartbeat 120s, OOM 隔離 | Python crash 不影響 GUI |
| T3 | agent_runner.py | asyncio event loop, 接收 JSON → 呼叫既有 orchestrator, streaming response | 能接收 generate/modify |
| T4 | JSON Protocol | generate/modify/get_cost/get_schedule request/response schema 定義 | 文件 + schema 完成 |
| T5 | mesh 序列化 | Python Builder mesh → JSON vertex/index/element 格式 | 資料格式正確，可 round-trip |
| T6 | AgentBridge ctest | ≥5 個 C++ 單元測試 | ctest PASS |
| T7 | agent_runner pytest | ≥5 個 Python 單元測試 | pytest PASS |
| T8 | E2E 驗證 | prompt → Python → JSON → C++ 收到完整結果 | 端到端通過 |

#### Part B: Qt Quick 3D 渲染核心 (8T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T9 | BIMGeometryProvider | QQuick3DGeometry 子類, loadFromJSON(meshData) | mesh 渲染正確 |
| T10 | BIMMaterialLibrary | concrete/glass/steel/wood → PrincipledMaterial PBR | 4 種材質可見可區分 |
| T11 | BIMSceneBuilder | JSON model → 為每個 BIM element 建立 Model QML node | 多元素場景正確組裝 |
| T12 | BIMView3D.qml | View3D + PerspectiveCamera + OrbitCameraController | 可旋轉縮放平移 |
| T13 | Picking | View3D pick → element ID → signal 發出 | 點擊選取 highlight |
| T14 | 多視角 | Perspective / Top / Front / Right 切換 | 4 視角可切換 |
| T15 | benchmark | Demo-1 S2 Fab 場景渲染 < 300MB | 記憶體達標 |
| T16 | ctest | ≥10 個 Qt Quick 3D 相關測試 | ctest PASS |

#### Part C: 最小 QML GUI (9T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T17 | main.qml | ApplicationWindow + SplitView (左Chat/中3D/右Property) | 三欄佈局正確 |
| T18 | ChatPanel.qml | TextInput + Send + streaming AI 回覆顯示 + 歷史對話 | 可輸入、可看到 AI 回覆 |
| T19 | PropertyPanel.qml | 點擊 3D → 顯示 BIM type/dimensions/material/cost | 屬性顯示正確 |
| T20 | StatusBar.qml | 記憶體 / AI 狀態 / 生成進度 bar | 狀態可見 |
| T21 | ChatPanel↔AgentBridge | prompt 從 ChatPanel 發送到 AgentBridge | prompt 可發送 |
| T22 | BIMView3D↔BIMSceneBuilder | AgentBridge 結果 → BIMSceneBuilder → 3D 渲染 | AI 結果可渲染 |
| T23 | Picking→PropertyPanel | 點擊 3D element → PropertyPanel 更新 | 點擊顯示屬性 |
| T24 | 🍎 Mac build | macOS Metal 渲染驗證 | build + run 正常 |
| T25 | 🪟 **Win build** | **Windows D3D12/Vulkan 渲染驗證** | **build + run 正常** |

> 🎯 **alpha Demo 能力:** 打字 "建立一個標準工廠" → AI 生成 → 3D 渲染 → 旋轉/縮放 → 點擊看屬性
> 🏷️ Tag: `mvp-v0.1.0-alpha`

---

### M1-S2: Cost + Delta + 4D + TSMC 場景 (2.5 週, 25T) → `mvp-v0.1.0-beta`

#### Part A: CostPanel + DeltaPanel (8T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T1 | CostPanel.qml | 總成本 NT$ formatted + 分項圓餅圖 (Canvas/ChartView) | 成本可見 |
| T2 | DeltaPanel.qml | Before/After 對照 + 成本/GFA/工期增減 + Undo 按鈕 | Delta 正確顯示 |
| T3 | Modifier E2E | "變更游泳池成為停車場" → delta JSON → DeltaPanel + 3D 更新 | 全流程端到端 |
| T4 | Cost 資料綁定 | Python cost engine → JSON → QML property binding | 即時更新 |
| T5 | Delta 動畫 | 數字滾動 + 色彩回饋 (綠↓紅↑) | 視覺回饋明確 |
| T6 | Undo/Redo stack | 最近 10 次修改可撤銷 | 撤銷/重做正確 |
| T7 | 多次修改累計 | Delta 歷史列表 | 歷史可見可回顧 |
| T8 | ctest | ≥5 tests | ctest PASS |

#### Part B: SchedulePanel + 4D (8T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T9 | SchedulePanel.qml | 甘特圖 (Canvas 自繪) + 16-phase + 總天數 | 甘特圖正確 |
| T10 | 4D Timeline Slider | 拖動 → BIMView3D visibility/opacity 聯動 + Play/Pause + 速度 1x/2x/5x/10x | 動畫播放 |
| T11 | Gantt↔3D 雙向聯動 | 點擊甘特圖 → 3D 跳轉；點擊 3D → Gantt highlight | 雙向同步 |
| T12 | 施工機械 3D | 起重機/挖土機隨 timeline 移動 | 機械動畫正確 |
| T13 | Phase 顏色 | 已完工(實色)/施工中(半透明)/未開始(隱藏) | 視覺正確 |
| T14 | 截圖匯出 | 當前 3D 畫面 → PNG | 可匯出 |
| T15 | schedule 資料綁定 | Python schedule engine → JSON → QML | 即時更新 |
| T16 | ctest | ≥5 tests | ctest PASS |

#### Part C: TSMC Demo 場景 (9T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T17 | ScenePicker.qml | 選擇 S1 別墅 / S2 Fab / S3 DC | 可切換場景 |
| T18 | 🪟 S2 半導體廠房 | "建立TSMC風格半導體廠 120m×80m" → 全流程 | 3D+成本+4D 正確 |
| T19 | S3 數據中心 | 場景驗證 | 全流程正確 |
| T20 | S1 別墅 | 場景驗證 | 全流程正確 |
| T21 | 修改 E2E #1 | "請將 2F Data Hall 高度增加到 6m" → Delta | GFA+成本+工期 正確 |
| T22 | 修改 E2E #2 | "變更游泳池成為員工停車場" → Delta | 正確計算 |
| T23 | AssetBrowser.qml | 零件庫搜尋 + 點擊替換 + 成本更新 | 替換可用 |
| T24 | 法規面板 | TW-IND-001~004 合規 checklist | 法規顯示正確 |
| T25 | Demo 腳本 v1.0 | 完整 7 分鐘 walkthrough 無中斷 | 跑完不當 |

> 🎯 **beta Demo 能力 (★ 可給 TSMC 預覽):**
> - "建立一個標準工廠" → 3D + 成本 NT$ + 4D 甘特圖 + 施工動畫
> - "變更游泳池成為員工停車場" → cost/schedule/GFA delta 即時更新
> - 3 場景切換 (別墅/Fab/DC)
> - Gantt↔3D 雙向聯動
> - 法規核查
>
> 🏷️ Tag: `mvp-v0.1.0-beta`

---

### M1-S3: 打磨 + USD I/O + Release (2 週, 20T) → `mvp-v0.1.0` ★

#### Part A: io_usd — ILOS USD 支援 (6T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T1 | io_usd import metadata | 讀取 ILOS USD + ilos: attributes | metadata 正確解析 |
| T2 | io_usd import connections | /Connections/ 解析 port_type/medium/size/direction | 連接點正確 |
| T3 | io_usd import instances | Instance 解析: `inst_xf × proto_inv × mesh_xf` | 座標正確 |
| T4 | io_usd export | Python mesh → USD mesh + ilos: metadata | Omniverse 可開啟 |
| T5 | ILOS 測試場景 | ILOS_Test_Pipeline_v4.usda 載入 + 3D 顯示 | 完整渲染 |
| T6 | metadata 顯示 | ilos: category/part_number 在 PropertyPanel 顯示 | 可見 |

#### Part B: 展示打磨 (8T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T7 | Dark/Light theme | 主題切換 | 兩主題可用 |
| T8 | Loading animation | AI 生成時進度指示器 | 進度可見 |
| T9 | 歡迎畫面 | Zigma PromptToBuild 品牌 Splash | 品牌顯示 |
| T10 | 鍵盤快捷鍵 | Space(旋轉), F(fit), 1-4(視角) | 操作順暢 |
| T11 | 🪟 **RTX 4090 GPU 優化** | **Windows Vulkan/D3D12 渲染效能** | **FPS ≥ 30** |
| T12 | 🍎 Mac Metal 驗證 | macOS Metal 最終渲染驗證 | Mac 可用 |
| T13 | 記憶體 profiling | 全場景 < 500MB | 不 OOM |
| T14 | crash recovery | Python crash → GUI 不掛 → 自動重啟 Python process | 穩定 |

#### Part C: Release (6T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T15 | E2E 完整測試 | 3 場景 × 2 修改 = 6 scenarios 全部通過 | 全 PASS |
| T16 | Demo 腳本 v2.0 | 更新為 Qt Quick 3D 版 7 分鐘腳本 | 無中斷跑完 |
| T17 | TSMC 簡報 v2.0 | 10 頁簡報更新 | 可交付 |
| T18 | SKILL.md v5.0 | 更新技術文件 | 推送 |
| T19 | PROJECT.md 更新 | 狀態更新 | 推送 |
| T20 | git tag | `mvp-v0.1.0` | tag 存在 |

> 🎯 **★ 正式 TSMC Demo (mvp-v0.1.0):**
> - beta 全部功能
> - **+ ILOS USD import/export** (W1/W3 工作流)
> - + Dark/Light theme 專業外觀
> - + 品牌歡迎畫面
> - + crash recovery (穩定)
> - + Mac + Windows 雙平台
> - + 完整 7 分鐘 Demo 腳本 v2.0
>
> 🏷️ Tag: **`mvp-v0.1.0`** ★ TSMC Demo Ready

---

## 🟡 Phase 2 — Revit 輸出 + OCCT 引入 (~6 週, ~75T) → `v3.0.0`

### P30: io_revit 夥伴 Converter 整合 (2 週, ~25T) → `v2.13.0`

#### Part A: L1 DirectShape (8T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T1 | Converter Plugin 包裝 | 夥伴 Python 代碼 → io_revit Plugin | import 成功 |
| T2 | USD mesh 萃取 | usd-core 讀取 + vertex/face 萃取 | 資料正確 |
| T3 | Instance 解析整合 | `inst_xf × proto_inv × mesh_xf` 公式 | 座標正確 |
| T4 | 單位轉換 | USD(cm) × 0.01 / 0.3048 = Revit(ft) | 尺寸正確 |
| T5 | DirectShape 建立 | → Revit MCP API → DirectShape elements | Revit 可見 |
| T6 | 材質對應 | BIM type → Revit Material | 顏色正確 |
| T7 | Category 對應 | ilos:revit_category → OST 分類 | 分類正確 |
| T8 | 🪟 **L1 E2E** | **Zigma → USD → Revit DirectShape** | **Revit 2026 開啟正確** |

#### Part B: L2 MEP Native (8T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T9 | Pipe.Create 整合 | ilos: metadata → Revit Pipe.Create(start, end, dia) | 管路可編輯 |
| T10 | NewElbowFitting | 轉角自動建立 elbow fitting | 接頭正確 |
| T11 | 跨樓層配管 | Sub-Fab / Interstitial / Cleanroom 三層 | Z elevation 正確 |
| T12 | PipingSystemType | ilos:piping_system → Revit System (UPW/CDA/PCW) | 系統正確 |
| T13 | Level 對應 | ilos:level → Revit Level | 樓層正確 |
| T14 | MEP 屬性 | diameter/length/flow → SharedParameters | 屬性可編輯 |
| T15 | 🪟 **L2 E2E** | **ILOS piping USD → Revit MEP Native** | **完全可編輯** |
| T16 | ctest + pytest | ≥10 tests | PASS |

#### Part C: Workflow E2E (9T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T17 | W1 E2E | ILOS USD → Zigma → Revit (DirectShape + MEP) | 全流程通 |
| T18 | W2 E2E | Prompt → Zigma BIM → Revit 輸出 | 全流程通 |
| T19 | IFC export | Revit → IFC (原生 Revit exporter) | 法規送審用 |
| T20 | BOM export | ilos: metadata → BOM CSV/Excel | 可供採購 |
| T21 | 3 場景 × Revit | S1/S2/S3 場景各自 Revit 輸出 | 3 場景通 |
| T22 | Demo 腳本 v3.0 | 含 Revit 輸出段落 | 跑完 |
| T23 | TSMC 簡報 v3.0 | Revit 截圖加入 | 可交付 |
| T24 | PROJECT.md 更新 | 狀態 | 推送 |
| T25 | git tag v2.13.0 | | tag 存在 |

> 🎯 **P30 Demo 新增能力:** 以上全部 + **Revit .rvt 輸出** (L1 DirectShape + L2 MEP Pipe)
> 🪟 **Windows 必測:** Revit 2026 + Python 3.11 + usd-core
> 🏷️ Tag: `v2.13.0`

---

### P31: OCCT Kernel 引入 (2 週, ~25T) → `v2.14.0`

#### Part A: OCCT 基礎 (8T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T1 | vcpkg + CMake | opencascade:x64-windows/arm64-osx | build 成功 |
| T2 | BIMKernel class | Wall/Slab/Column/Beam B-Rep primitives | 基本幾何正確 |
| T3 | Wall B-Rep | BRepPrimAPI_MakeBox / MakePrism | 牆體正確 |
| T4 | Boolean 門窗 | BRepAlgoAPI_Cut → 開口 | Boolean 正確 |
| T5 | Column B-Rep | BRepPrimAPI_MakeCylinder | 柱正確 |
| T6 | Pipe Sweep | BRepOffsetAPI_MakePipe | 管路正確 |
| T7 | XDE Assembly | TDocStd_Document + XCAFDoc properties/colors | 組裝正確 |
| T8 | ctest ≥10 | | PASS |

#### Part B: OCCT → Qt Quick 3D (8T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T9 | tessellation | BRepMesh_IncrementalMesh → vertex/index | mesh 正確 |
| T10 | BIMGeometryProvider v2 | loadFromShape(TopoDS_Shape) 替代 loadFromJSON | 渲染正確 |
| T11 | Normal 計算 | OCCT face normal → QQuick3DGeometry | 光影正確 |
| T12 | 材質對應 | XDE color → PrincipledMaterial | 材質正確 |
| T13 | AI Builder v2 | Python AI → OCCT BIMKernel (替代 Python mesh) | AI 建模走 OCCT |
| T14 | Boolean E2E | "加一扇窗" → OCCT Boolean Cut → 3D 更新 | 開口正確 |
| T15 | GProp | 面積/體積計算 → CostPanel 更新 | 數值正確 |
| T16 | benchmark | OCCT 場景 < 400MB | 記憶體達標 |

#### Part C: 整合 + 驗證 (9T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T17 | Dual SSOT | AI 建模用 OCCT XDE, ILOS 匯入用 USD Stage | 雙 SSOT 正確 |
| T18 | io_step import | STEPControl_Reader → OCCT → 3D | STEP 可載入 |
| T19 | OCCT → USD export | tessellation → USD mesh | Omniverse 可開啟 |
| T20 | W2 OCCT E2E | Prompt → OCCT BIM → Qt Quick 3D | 全流程通 |
| T21 | W4 OCCT E2E | 設計變更 → OCCT Boolean → delta | 全流程通 |
| T22 | 🪟 **Win OCCT build** | **vcpkg OCCT + Qt Quick 3D 在 Windows** | **build + run** |
| T23 | 🍎 Mac OCCT build | homebrew OCCT + Qt Quick 3D 在 macOS | build + run |
| T24 | PROJECT.md 更新 | | 推送 |
| T25 | git tag v2.14.0 | | tag 存在 |

> 🏷️ Tag: `v2.14.0`

---

### P32: 清理 + v3.0.0 Release (2 週, ~25T) → `v3.0.0` ★

#### Part A: 清理 (8T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T1 | 移除 PySide6 | 全部 GUI code → QML 替代 | 無 PySide6 import |
| T2 | 移除 PyVista | 全部 3D code → Qt Quick 3D 替代 | 無 PyVista import |
| T3 | 移除 matplotlib | 全部 chart → QML Canvas 替代 | 無 matplotlib import |
| T4 | Plugin Bus 正式化 | IPlugin 6 大介面凍結 | 介面文件定義 |
| T5 | ABI 版本 | v3.0.0 ABI stamp | 版本標記 |
| T6 | Python deps 瘦身 | requirements.txt 清理 | 最小依賴 |
| T7 | CMake 清理 | 移除舊 target | build 乾淨 |
| T8 | ctest + pytest 全跑 | 所有測試 PASS | 全綠 |

#### Part B: 四個工作流 E2E (10T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T9 | W1 E2E | ILOS USD → Zigma → Revit .rvt | ✅ |
| T10 | W2 E2E | Prompt → OCCT BIM → Revit .rvt | ✅ |
| T11 | W3 E2E | OCCT BIM → USD → Omniverse | ✅ |
| T12 | W4 E2E | 設計變更 → OCCT Boolean → delta → Revit | ✅ |
| T13 | 3 場景 × 4 workflow | 12 scenario 全部通過 | 全 PASS |
| T14 | 🪟 **Win 全面驗證** | **Windows 所有 workflow** | **全部正確** |
| T15 | 🍎 Mac 全面驗證 | macOS 所有 workflow | 全部正確 |
| T16 | 效能 benchmark | 全場景 < 500MB, FPS ≥ 30 | 達標 |
| T17 | crash test | 連續 2 小時操作無 crash | 穩定 |
| T18 | Demo 腳本 v4.0 | v3.0.0 版本 4 workflow 完整演示 | 跑完 |

#### Part C: Release (7T)

| # | Task | 說明 | 驗收標準 |
|---|------|------|---------|
| T19 | TSMC 簡報 v4.0 | 四個工作流 + OCCT + Revit | 可交付 |
| T20 | SKILL.md v6.0 | 完整更新 | 推送 |
| T21 | PROJECT.md 更新 | v3.0.0 里程碑 | 推送 |
| T22 | CLAUDE.md 檢視 | 確認規則仍適用 | 確認 |
| T23 | README.md 公開版 | 專案說明 | 推送 |
| T24 | Audit Report | v3.0.0 完整審計 | 推送 |
| T25 | git tag v3.0.0 | | **★ tag 存在** |

> 🎯 **★ v3.0.0 Demo 能力:** 四個工作流全通，OCCT B-Rep Boolean，Revit .rvt 輸出，穩定可交付
> 🪟 **Windows 全面驗證必做**
> 🏷️ Tag: **`v3.0.0`** ★

---

## 📊 數字摘要

| 階段 | Sprint | 週數 | Tasks | Tag |
|------|--------|:----:|:-----:|-----|
| MVP S1 | M1-S1 | 2.5 | 25 | mvp-v0.1.0-alpha |
| MVP S2 | M1-S2 | 2.5 | 25 | mvp-v0.1.0-beta |
| MVP S3 | M1-S3 | 2 | 20 | **mvp-v0.1.0 ★** |
| **MVP 小計** | | **7** | **70** | |
| Ph2 P30 | io_revit | 2 | ~25 | v2.13.0 |
| Ph2 P31 | OCCT | 2 | ~25 | v2.14.0 |
| Ph2 P32 | cleanup | 2 | ~25 | **v3.0.0 ★** |
| **Ph2 小計** | | **6** | **~75** | |
| **合計到 v3.0.0** | | **~13** | **~145** | |

---

## 🪟 Windows 驗證完整清單

| 時間點 | 測試項目 | 環境 |
|--------|---------|------|
| M1-S1 T25 | Qt Quick 3D GUI build + run | Qt 6.7 MSVC + CMake |
| M1-S2 T18 | S2 Fab GPU 渲染 | RTX 4090 + D3D12 |
| M1-S3 T11 | GPU 渲染優化 FPS≥30 | RTX 4090 + Vulkan/D3D12 |
| P30 T8 | DirectShape → Revit | Revit 2026 |
| P30 T15 | MEP Native → Revit | Revit 2026 |
| P31 T22 | OCCT build + Qt Quick 3D | vcpkg OCCT + Qt 6.7 MSVC |
| P32 T14 | **v3.0.0 全面驗證** | **全套環境** |

---

*Sprint/Task Master List v1.0 | Zigma PromptToBuild | 2026-03-28*
*MVP: 7w/70T → mvp-v0.1.0 | Phase 2: 6w/~75T → v3.0.0*
