# PromptBIM Windows 平台遷移計畫 v1.0

> **文件版本:** v1.0 | **建立日期:** 2026-03-26
> **決策者:** Michael Lin (林志錚) | **分析:** Claude (Senior Architect)
> **狀態:** ✅ 已批准 — 方案 C: Hydra Storm + PyVista 混合架構

---

## 1. 決策摘要

| 項目 | 決策 |
|------|------|
| **渲染方案** | 方案 C: Hydra Storm 嵌入 Qt + PyVista 輔助（混合） |
| **目標平台** | Windows (RTX 4090) + macOS（保持相容） |
| **GUI 框架** | PySide6（唯一跨平台 GUI） |
| **工程 3D 預覽** | PyVista + QVTKOpenGLNativeWidget |
| **品質 USD 渲染** | Hydra Storm (pxr.UsdImagingGL) + QOpenGLWidget |
| **OpenUSD 整合** | usd-core (pxr) 原生 API — Apache-2.0 |
| **放棄方案** | ❌ Unreal Engine / ❌ Omniverse / ❌ Qt3D |

---

## 2. 目標架構 (v3.0)

```
┌──────────────────────────────────────────────────────────────┐
│              PromptBIM v3.0 架構 (Windows + macOS)            │
│                                                                │
│  🖥️ GUI Layer — PySide6 (LGPL-3.0, 跨平台唯一 GUI)          │
│  ├─ MainWindow (QMainWindow)                                   │
│  │   ├─ MenuBar: File | Edit | View | Tools | Help            │
│  │   ├─ ToolBar: 常用操作按鈕                                  │
│  │   └─ StatusBar: 進度 + GPU 狀態                             │
│  ├─ 左側面板 (QDockWidget, 可折疊)                             │
│  │   ├─ ProjectTree (QTreeWidget)                              │
│  │   └─ PropertyPanel (QTreeWidget)                            │
│  ├─ 中央 Tab 視圖 (QTabWidget)                                │
│  │   ├─ Tab 1: 2D 地籍 → matplotlib FigureCanvas              │
│  │   ├─ Tab 2: 3D 工程 → QVTKOpenGLNativeWidget (PyVista)     │
│  │   └─ Tab 3: USD 渲染 → QOpenGLWidget (Hydra Storm) ★新增★  │
│  └─ 底部 Chat (QDockWidget)                                    │
│      ├─ QTextEdit (對話歷史)                                    │
│      ├─ QLineEdit + 🎤 (輸入 + 語音)                           │
│      └─ QProgressBar (AI 處理進度)                              │
│                                                                │
│  🔌 訊息通訊 (GUI ↔ Core)                                     │
│  ├─ Qt Signal/Slot — GUI 元件間事件                             │
│  ├─ QThread + Worker — AI Agent 非同步執行                     │
│  ├─ asyncio + qasync — async Agent 與 Qt event loop 橋接      │
│  └─ subprocess — 外部工具 (usdview, usdchecker)                │
│                                                                │
│  🧠 Core Layer — 純 Python (完全跨平台, 不動)                  │
│  ├─ agents/ (Claude API, sync + async)                         │
│  ├─ bim/                                                       │
│  │   ├─ ifc_generator.py → .ifc                               │
│  │   ├─ usd_generator.py → .usda (既有)                       │
│  │   └─ usd_scene.py ★新增★ — Hydra Storm 場景管理            │
│  ├─ land/ (GIS: geopandas, shapely, fiona)                    │
│  ├─ cache/, plugins/, schemas/, voice/                         │
│  └─ viz/ (matplotlib + PyVista + Hydra)                        │
│                                                                │
│  📦 OpenUSD 整合層 ★新增★                                      │
│  ├─ usd_scene.py — UsdSceneRenderer (Hydra Storm)             │
│  │   ├─ load_stage(path) → Usd.Stage                          │
│  │   ├─ setup_hydra(gl_widget) → UsdImagingGL.Engine          │
│  │   ├─ render_frame(camera, viewport)                         │
│  │   └─ pick_prim(x, y) → Usd.Prim path                      │
│  ├─ usd_materials.py — BIM 材質 → UsdShade PBR 對應           │
│  ├─ usd_camera.py — ArcballCamera (旋轉/縮放/平移)            │
│  └─ usd_export.py — 強化版 USD 匯出                           │
│      ├─ 完整 BIM 階層 (Site > Building > Story > Element)     │
│      ├─ PBR 材質綁定 (UsdShade + UsdPreviewSurface)           │
│      └─ Metadata (IFC GUID, 面積, 容積率)                      │
│                                                                │
│  ⚙️ C++ Core (P18+ 規劃, CMake + vcpkg)                       │
│  ├─ Windows: MSVC | macOS: Clang                               │
│  └─ pybind11 → Python 橋接                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. 技術棧變更對照

| 層 | v2.x (macOS) | v3.0 (Windows + macOS) | 變更 |
|----|-------------|----------------------|------|
| GUI | PySide6 + SwiftUI wrapper | PySide6 only | 移除 Swift |
| 2D | matplotlib | matplotlib | 不動 |
| 3D 工程 | PyVista + pyvistaqt | PyVista + QVTKOpenGLNativeWidget | 微調 |
| 3D USD | 無 | **Hydra Storm + QOpenGLWidget** | ★新增 |
| BIM | IfcOpenShell + usd-core | IfcOpenShell + usd-core | 不動 |
| AI | Claude API (anthropic SDK) | Claude API (anthropic SDK) | 不動 |
| GIS | geopandas, shapely | geopandas, shapely | 不動 |
| Build | Xcode + pytest | **pytest only** (移除 Xcode) | 簡化 |
| CI | GitHub Actions (macOS) | GitHub Actions (macOS + **Windows**) | 雙平台 |
| 語音 | NSSpeechRecognizer + whisper | **whisper only** (跨平台) | 統一 |
| 打包 | Xcode .app | **PyInstaller / cx_Freeze** | 新增 |

---

## 4. 訊息通訊架構

### 4.1 GUI 內部通訊 (Qt Signal/Slot)

```
ChatPanel.chat_submitted(str)
    → MainWindow._on_chat_submitted(text)
        → AgentWorker.start(text, land, zoning)

AgentWorker.generation_complete(PBResult)
    → MainWindow._on_generation_complete(result)
        → MapView.update_footprint(result.plan)
        → VTKView.load_mesh(result.mesh)
        → UsdView.load_stage(result.usda_path)   ★新增
        → PropertyPanel.update(result.plan)

UsdView.prim_selected(str)
    → PropertyPanel.show_prim_properties(prim_path)
    → ProjectTree.highlight_prim(prim_path)
```

### 4.2 非同步 AI 執行 (QThread)

```python
class AgentWorker(QThread):
    started = Signal(str)           # "正在分析土地..."
    progress = Signal(str, int)     # ("Agent 2 規劃中", 50)
    generation_complete = Signal(object)  # PBResult
    error = Signal(str)

    def run(self):
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(
            self.orchestrator.agenerate(self.text, self.land, self.zoning)
        )
        self.generation_complete.emit(result)
```

### 4.3 外部工具呼叫 (subprocess)

```python
# usdview 獨立視窗預覽
subprocess.Popen(["usdview", str(usda_path)])

# usdchecker 驗證
result = subprocess.run(
    ["usdchecker", str(usda_path)],
    capture_output=True, text=True
)
```

---

## 5. Sprint 路線圖 (P24 → P33)

### 總覽

```
Phase 1: macOS 功能完善 (P24~P29)     → v2.10~v2.15
Phase 2: Windows 遷移 (P30~P31)       → v3.0-alpha ~ v3.0-beta
Phase 3: Hydra Storm 整合 (P32~P33)   → v3.0-rc ~ v3.0
```

### Phase 1: macOS 功能完善 (繼續既有計畫)

#### P24 — Demo 3D Auto-Gen + Free IFC + Advanced BIM (v2.11.0)
> 已有 PROMPT_P24.md v2.0

- Part A: Demo 3D 修復 — 實際 IFC/USDA 3D 檔案（修復 demo_data.py 空白問題）
- Part B: Free IFC 模型整合 — 從開源 repo 下載範例 IFC
- Part C: Advanced BIM — Agent 2 Planner 品質強化
- Part D: 驗收

#### P25 — USD 匯出品質強化 (v2.12.0)
> ★ 為 Windows Hydra Storm 做準備 ★

| Part | Tasks | 重點 |
|------|-------|------|
| A | 5 | **USD 場景階層** — Site > Building > Story > Element 完整 Prim 結構 |
| B | 5 | **UsdShade PBR 材質** — UsdPreviewSurface: 混凝土/玻璃/鋼/木/磁磚 |
| C | 4 | **USD Metadata** — customData: IFC GUID, 面積, 用途, 法規符合度 |
| D | 3 | **usdchecker 驗證** — 自動跑 usdchecker, 修復所有 warnings |
| E | 3 | 驗收 + 測試 |

#### P26 — 完整端到端 Pipeline (v2.13.0)

| Part | Tasks | 重點 |
|------|-------|------|
| A | 5 | **土地 → 建築** 完整流程（輸入 GeoJSON → 輸出 IFC + USD + SVG） |
| B | 5 | **多建築類型** — 住宅/辦公/廠房 各一個完整 Demo |
| C | 4 | **2D/3D 聯動** — 點選 2D footprint ↔ highlight 3D 構件 |
| D | 3 | 效能優化 + 測試 |

#### P27 — GUI 品質提升 (v2.14.0)

| Part | Tasks | 重點 |
|------|-------|------|
| A | 4 | **Project 管理** — 新建/開啟/儲存專案 (.pbim 自定義格式) |
| B | 4 | **Undo/Redo** — QUndoStack 整合 AI 操作歷史 |
| C | 4 | **Settings Dialog** — API Key, 快取, 渲染設定 |
| D | 3 | **國際化** — 中文/英文 UI (Qt i18n) |
| E | 3 | 測試 + 驗收 |

#### P28 — C++ Core Phase 0 (v2.15.0)

| Part | Tasks | 重點 |
|------|-------|------|
| A | 5 | **CMake + vcpkg** — 跨平台 C++ build 骨架 |
| B | 5 | **Compliance Engine C++** — 法規引擎移植 |
| C | 4 | **pybind11 binding** — Python fallback 機制 |
| D | 3 | 測試 + benchmark |

#### P29 — 穩定化 + 跨平台準備 (v2.16.0)

| Part | Tasks | 重點 |
|------|-------|------|
| A | 5 | **移除 Swift 依賴** — 刪除 Xcode project, SwiftUI wrapper |
| B | 4 | **PySide6 standalone** — 不依賴 Xcode 的完整 GUI 啟動 |
| C | 4 | **抽象化平台差異** — 路徑/字體/語音 的 platform adapter |
| D | 3 | **CI 準備** — pytest + ruff 在 macOS + Windows 都能跑 |
| E | 3 | 全面回歸測試 |

---

### Phase 2: Windows 遷移 (核心里程碑)

#### P30 — Windows 環境建立 + 核心驗證 (v3.0-alpha)
> ★ 第一次在 Windows RTX 4090 上跑 PromptBIM ★

| Part | Tasks | 重點 | 驗收標準 |
|------|-------|------|---------|
| A | 5 | **Windows 環境** | |
| | | ① conda create -n promptbim python=3.11 (Windows) | conda activate OK |
| | | ② pip install PySide6 pyvista pyvistaqt | import 全部成功 |
| | | ③ conda install -c conda-forge ifcopenshell | ifcopenshell.version OK |
| | | ④ pip install usd-core | `from pxr import Usd` OK |
| | | ⑤ 驗證 GPU: `pyvista.GPUInfo()` 顯示 RTX 4090 | GPU 被偵測到 |
| B | 5 | **Python 核心跑通** | |
| | | ① pytest tests/ 全部通過 (排除 macOS-specific) | 1000+ tests PASS |
| | | ② promptbim generate "3-story villa" 成功 | 生成 .ifc + .usda |
| | | ③ promptbim gui 啟動 PySide6 視窗 | GUI 顯示 |
| | | ④ PyVista 3D 預覽正常 | 可旋轉/縮放 |
| | | ⑤ usdview 開啟 .usda 正常 | Hydra Storm 渲染 |
| C | 3 | **跨平台 CI** | |
| | | ① GitHub Actions 新增 windows-latest job | CI 綠燈 |
| | | ② pytest 在 Windows runner 通過 | Tests PASS |
| | | ③ 修復所有 Windows path 問題 (\\\\→/) | 無 path 錯誤 |
| D | 3 | **Claude Code Windows** | |
| | | ① WSL2 or native Windows Claude Code 測試 | 可執行 Sprint |
| | | ② Windows notify 替代方案 (PowerShell Toast) | 收到通知 |
| | | ③ SSH 從 Mac Mini 到 Windows 測試 | SSH OK |
| E | 3 | 驗收 | Audit Report |

**P30 版本交付物:**
- `v3.0-alpha` tag
- Windows 環境 setup script: `scripts/setup_windows.ps1`
- CI: `.github/workflows/ci.yml` 新增 Windows matrix
- 文件: `docs/WINDOWS_SETUP.md`

---

#### P31 — QVTKWidget + 跨平台 GUI 完善 (v3.0-beta)
> ★ PySide6 成為唯一 GUI，雙平台穩定 ★

| Part | Tasks | 重點 | 驗收標準 |
|------|-------|------|---------|
| A | 5 | **QVTKOpenGLNativeWidget 整合** | |
| | | ① 替換 pyvistaqt.QtInteractor → QVTKWidget | VTK 渲染正常 |
| | | ② 3D 互動: 旋轉/縮放/平移/剖面 | 操作流暢 |
| | | ③ GPU 加速驗證: RTX 4090 vs M4 效能對比 | >5x 提升 |
| | | ④ 大模型測試: 10K+ mesh elements | >30 FPS |
| | | ⑤ 相機預設: Top/Front/Right/Perspective | 一鍵切換 |
| B | 4 | **GUI 雙平台統一** | |
| | | ① Dark/Light mode (QPalette) | 雙平台一致 |
| | | ② DPI scaling (High-DPI aware) | 4K 顯示正常 |
| | | ③ 字體: 中文顯示 (CJK font fallback) | 無方框 |
| | | ④ 鍵盤快捷鍵: Ctrl vs Cmd 適配 | 平台正確 |
| C | 4 | **語音跨平台** | |
| | | ① whisper.cpp / faster-whisper Windows 測試 | STT OK |
| | | ② 移除 NSSpeechRecognizer 依賴 | macOS 也用 whisper |
| | | ③ 麥克風權限處理 (Windows/macOS) | 錄音正常 |
| | | ④ GPU 加速 whisper (CUDA on RTX 4090) | 即時辨識 |
| D | 3 | 測試 + 驗收 | Audit Report |

---

### Phase 3: Hydra Storm 整合 (核心創新)

#### P32 — Hydra Storm 嵌入 PySide6 (v3.0-rc)
> ★ 核心創新 — OpenUSD 原生渲染嵌入桌面 App ★

| Part | Tasks | 重點 | 驗收標準 |
|------|-------|------|---------|
| A | 5 | **UsdSceneRenderer 核心** | |
| | | ① `bim/usd_scene.py` — load_stage(), Hydra Engine init | Stage 載入 |
| | | ② `UsdImagingGL.Engine` 初始化 + RenderParams | 引擎啟動 |
| | | ③ render_frame() — Hydra Storm 繪製一幀 | 畫面出現 |
| | | ④ 相機矩陣計算 (Gf.Matrix4d) | 可旋轉 |
| | | ⑤ Viewport resize 處理 | 視窗縮放正常 |
| B | 5 | **UsdViewWidget (QOpenGLWidget)** | |
| | | ① 繼承 QOpenGLWidget, initializeGL/paintGL/resizeGL | Widget 渲染 |
| | | ② ArcballCamera — 滑鼠旋轉/滾輪縮放/中鍵平移 | 操作順暢 |
| | | ③ Selection — pick_prim(x, y) 點選查詢 | 點選 highlight |
| | | ④ 嵌入 MainWindow Tab 3 | 切換正常 |
| | | ⑤ RTX 4090 GPU 驗證 + FPS 顯示 | >30 FPS |
| C | 5 | **PBR 材質渲染** | |
| | | ① UsdPreviewSurface 材質載入 | 材質顯示 |
| | | ② BIM 材質庫: 混凝土/玻璃/鋼/木/磁磚 | 5 種材質 |
| | | ③ 環境光 (Dome Light + HDRI) | 光影正確 |
| | | ④ 陰影 (Shadow) | 陰影顯示 |
| | | ⑤ 透明材質 (玻璃 opacity) | 透明正確 |
| D | 4 | **GUI 聯動** | |
| | | ① UsdView.prim_selected → PropertyPanel | 屬性顯示 |
| | | ② UsdView.prim_selected → ProjectTree.highlight | 樹狀高亮 |
| | | ③ ProjectTree.item_clicked → UsdView.focus_prim | 相機飛到構件 |
| | | ④ VTKView ↔ UsdView 同步相機 (選用) | 雙視圖連動 |
| E | 4 | **測試 + 效能** | |
| | | ① pytest: UsdSceneRenderer 單元測試 | Tests PASS |
| | | ② pytest: UsdViewWidget 整合測試 (pytest-qt) | Tests PASS |
| | | ③ 效能 benchmark: 1K/5K/10K prims | 記錄 FPS |
| | | ④ 記憶體 leak 測試 (GL context 清理) | 無 leak |
| F | 2 | 驗收 | Audit Report |

**P32 新增檔案:**
```
src/promptbim/
├── bim/
│   ├── usd_scene.py        ★ UsdSceneRenderer (Hydra Storm 核心)
│   ├── usd_materials.py     ★ BIM PBR 材質庫
│   └── usd_camera.py        ★ ArcballCamera
├── gui/
│   └── usd_view.py          ★ UsdViewWidget (QOpenGLWidget)
└── viz/
    └── usd_renderer.py      ★ Hydra 渲染輔助函數
```

---

#### P33 — 品質強化 + 打包 + v3.0 Release (v3.0)
> ★ 第一個 Windows 正式發佈版 ★

| Part | Tasks | 重點 | 驗收標準 |
|------|-------|------|---------|
| A | 5 | **USD 場景品質** | |
| | | ① Hydra 剖面功能 (clipping plane) | 可剖切 |
| | | ② 樓層隱藏/顯示 (visibility toggle) | 可切換 |
| | | ③ 爆炸圖 (exploded view per story) | 展開動畫 |
| | | ④ 標註 (面積, 尺寸 overlay) | 文字顯示 |
| | | ⑤ 截圖匯出 (Hydra → PNG) | 高品質截圖 |
| B | 4 | **匯出強化** | |
| | | ① .usdz 匯出 (AR Preview 用) | usdz 可開啟 |
| | | ② .glb 匯出 (Web viewer 用) | glTF 正確 |
| | | ③ usdchecker 自動驗證 pipeline | 零 warnings |
| | | ④ IFC ↔ USD 雙向 metadata 對照表 | 文件完整 |
| C | 4 | **Windows 打包** | |
| | | ① PyInstaller spec 檔案 | .exe 可執行 |
| | | ② NSIS / Inno Setup installer | 安裝包 |
| | | ③ 桌面捷徑 + 檔案關聯 (.ifc, .usda) | 雙擊開啟 |
| | | ④ 自動更新機制 (選用) | 版本檢查 |
| D | 4 | **文件 + 驗收** | |
| | | ① README.md 更新 (Windows 安裝說明) | 文件完整 |
| | | ② SKILL.md v4.0 (加入 USD 渲染架構) | SSOT 更新 |
| | | ③ 全面審計 (三大領域) | A 評分 |
| | | ④ v3.0 tag + GitHub Release | Release 發佈 |

---

## 6. Sprint 總覽甘特圖

```
Sprint    版本         平台        重點
───────────────────────────────────────────────────────────────
P24       v2.11.0      macOS       Demo 3D + Free IFC
P25       v2.12.0      macOS       ★ USD 匯出品質 (為 Hydra 準備)
P26       v2.13.0      macOS       端到端 Pipeline
P27       v2.14.0      macOS       GUI 品質提升
P28       v2.15.0      macOS       C++ Core Phase 0
P29       v2.16.0      macOS       ★ 移除 Swift + 跨平台準備
──────────────────── Phase 1 完成 ─────────────────────────────
P30       v3.0-alpha   ★Windows★   環境建立 + 核心驗證
P31       v3.0-beta    Win+Mac     QVTKWidget + 跨平台 GUI
──────────────────── Phase 2 完成 ─────────────────────────────
P32       v3.0-rc      Win+Mac     ★ Hydra Storm 嵌入 PySide6 ★
P33       v3.0         Win+Mac     品質強化 + 打包 + Release
──────────────────── Phase 3 完成 / v3.0 發佈 ─────────────────
```

---

## 7. 依賴與風險

### 7.1 新增 Python 依賴

| 依賴 | 版本 | 用途 | License | Windows |
|------|------|------|---------|---------|
| usd-core (pxr) | ≥24.0 | OpenUSD + Hydra Storm | Apache-2.0 | ✅ pip wheel |
| PySide6 | ≥6.6 | GUI (既有) | LGPL-3.0 | ✅ pip wheel |
| pyvista | ≥0.43 | 3D 工程預覽 (既有) | MIT | ✅ pip wheel |
| vtk | ≥9.3 | QVTKWidget | BSD | ✅ pip wheel |
| qasync | ≥0.27 | asyncio ↔ Qt 橋接 | BSD | ✅ pip wheel |

### 7.2 風險矩陣

| 風險 | 影響 | 機率 | 緩解 |
|------|------|------|------|
| Hydra Storm GL context 與 QOpenGLWidget 衝突 | 🔴 高 | 中 | P32 Part A 先做 POC spike |
| usd-core Windows wheel 缺 UsdImagingGL | 🔴 高 | 低 | pip wheel 包含; 備案: conda-forge |
| IfcOpenShell Windows conda 安裝問題 | 🟧 中 | 中 | conda-forge 有 Windows build |
| PyVista GPU 不自動用 RTX 4090 | 🟨 低 | 低 | 環境變數強制指定 GPU |
| CJK 字體在 Windows matplotlib 缺失 | 🟢 低 | 高 | 打包時 bundle 字體 |

### 7.3 Gate Review (關鍵決策點)

| 節點 | 條件 | 不通過的後備方案 |
|------|------|-----------------|
| P30 Part B 結束 | pytest 90%+ PASS on Windows | 修復 platform-specific 問題再繼續 |
| P32 Part A Task 3 | Hydra Storm render_frame() 成功出圖 | 退回 PyVista only (放棄 Hydra Tab) |
| P32 Part B Task 5 | >30 FPS on RTX 4090 | 降低渲染品質 / 用 LOD |

---

## 8. 開發環境

### Windows (新增)

```
硬體: RTX 4090 (24GB VRAM)
OS: Windows 11
Python: conda (miniconda), Python 3.11
IDE: VSCode / PyCharm
Claude Code: WSL2 或 native Windows
Git: Git for Windows
SSH: OpenSSH (內建)
```

### macOS (維持)

```
Mac Mini M4: Claude Code Sprint 執行
MacBook: Xcode (P29 前) → VSCode (P29 後)
Python: conda, Python 3.11
```

### Setup Script (P30 交付)

```powershell
# scripts/setup_windows.ps1
conda create -n promptbim python=3.11 -y
conda activate promptbim
conda install -c conda-forge ifcopenshell -y
pip install -e ".[dev]"
pip install usd-core qasync
python -c "from pxr import Usd, UsdImagingGL; print('OpenUSD + Hydra OK')"
python -c "import pyvista; print(f'PyVista {pyvista.__version__}'); print(pyvista.GPUInfo())"
python -c "from PySide6.QtWidgets import QApplication; print('PySide6 OK')"
python -m promptbim --version
```

---

## 9. 成功指標

| 指標 | P24 (現在) | P30 (alpha) | P33 (v3.0) |
|------|-----------|-------------|------------|
| Tests | ~1,060 | 1,100+ (Win) | 1,300+ |
| 平台 | macOS only | macOS + Windows | 雙平台穩定 |
| 3D 渲染 | PyVista only | PyVista (Win) | PyVista + Hydra Storm |
| USD 品質 | 基本 .usda | PBR 材質 | 完整 BIM 場景 |
| GUI | PySide6 + Swift | PySide6 only | PySide6 + UsdView |
| FPS (3D) | ~30 (M4) | ~60 (RTX 4090) | >60 (Hydra + RTX) |
| 版本 | v2.10.0 | v3.0-alpha | v3.0 |
| 評分 | A (9.0) | B+ (target) | A (target) |

---

*Windows_Migration_Plan v1.0 | 2026-03-26*
*方案 C: Hydra Storm + PyVista 混合架構*
*零商業依賴 — 100% 開源技術棧*
