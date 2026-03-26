# PromptToBuild 統一平台架構設計 v2.1

> **版本:** v2.1 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **前身:** v2.0 (2026-03-27)
> **願景:** 從 PromptBIM POC 演進為 PromptToBuild 企業級統一平台
> **v2.1 重點:** 五大抽象層強制規範 — 高度插件化 + UI 可抽換 + 遠端渲染

---

## 1. 願景演進

```
PromptBIM (POC, v2.12.0)              PromptToBuild (Platform, v4.0+)
├─ 單一建築 BIM 生成                    ├─ 前端入口 + 後段整合平台
├─ 單機桌面 App                         ├─ 跨平台 (Win/Mac/Linux)
├─ Python + C++ 混合                    ├─ C++ Core + Plugin 架構
├─ 本地 PyVista 渲染                    ├─ Omniverse 遠端渲染 + Image Streaming
├─ IFC/USD 單向輸出                     ├─ 雙向 OpenUSD ↔ Revit (全插件化)
└─ 獨立運作                             ├─ ILOS AI 佈局引擎 (插件化)
                                        ├─ Omniverse Cluster 整合
                                        ├─ UI Shell 可抽換 (Qt6/Web/Headless)
                                        └─ Mobile/iPad 透過 Remote Streaming
```

---

## 2. 核心設計原則（8 項）

| # | 原則 | 說明 |
|---|------|------|
| 1 | **USD 為 SSOT** | OpenUSD Stage 是唯一資料真相來源 |
| 2 | **Everything is Plugin** | I/O、AI、渲染、法規、ERP — 全部插件化 |
| 3 | **渲染與邏輯完全分離** | 核心引擎零渲染依賴；渲染層可抽換或移除 |
| 4 | **UI Shell 可抽換** | Qt6 是預設，但可替換為 Web/Electron/Headless |
| 5 | **I/O 全插件化** | 每種檔案格式（USD/Revit/IFC/DWG）都是獨立 Plugin |
| 6 | **雙向互通** | USD ↔ Revit 持續同步，不是單向轉換 |
| 7 | **Scale-Out 渲染** | 小模型本地、大模型 Omniverse Streaming |
| 8 | **Desktop + Mobile 分離** | Desktop 原生 App；Mobile/iPad 僅 Remote Streaming |

---

## 3. ★ 五大抽象層強制規範（v2.1 核心）

### 規範 1: I/O 全插件化（ILOS / Revit / USD / IFC）

所有檔案進出口必須透過 `IIOPlugin` 介面，核心引擎不得直接依賴任何具體格式。

```cpp
class IIOPlugin : public IPlugin {
public:
    // 匯入
    virtual bool canImport(const std::string& format) const = 0;
    virtual UsdStagePtr import(const std::string& path, ImportOptions opts) = 0;

    // 匯出
    virtual bool canExport(const std::string& format) const = 0;
    virtual bool exportTo(const UsdStagePtr& stage, const std::string& path, ExportOptions opts) = 0;

    // 雙向同步（選用）
    virtual bool supportsBidirectional() const { return false; }
    virtual SyncSession* createSyncSession(const std::string& target) { return nullptr; }
};
```

**已知 I/O Plugins（均可獨立載入/卸載/替換）：**

| Plugin | 格式 | 方向 | 第三方 Library |
|--------|------|------|---------------|
| `io_usd` | .usd/.usda/.usdc | Import + Export | pxr (usd-core) |
| `io_revit` | .rvt (via MCP) | Bidirectional | Revit MCP + Revit API |
| `io_ifc` | .ifc (IFC2x3/4) | Export | ifcopenshell 或自研 |
| `io_dwg` | .dwg/.dxf | Export | Open Design Alliance |
| `io_geojson` | .geojson | Import | GDAL/OGR |
| `io_shapefile` | .shp | Import | GDAL/OGR |
| `io_kml` | .kml | Import | GDAL/OGR |
| `io_pdf_ocr` | .pdf | Import | PyMuPDF + Claude Vision |
| `io_step` | .step/.stp | Import | OpenCASCADE |
| `io_fbx` | .fbx | Import | FBX SDK (未來) |
| `io_gltf` | .gltf/.glb | Import + Export | tinygltf (未來) |

**擴充範例：** 客戶自訂 `io_custom_erp.so` → 直接從 SAP 讀取 BOM 並生成 USD。

### 規範 2: ILOS + AI 全插件化

ILOS 引擎和所有 AI Agent 都是 `IEnginePlugin`，核心平台不硬編碼任何 AI 邏輯。

```cpp
class IEnginePlugin : public IPlugin {
public:
    virtual bool canProcess(const EngineRequest& req) const = 0;
    virtual EngineResult process(const EngineRequest& req) = 0;
    virtual bool supportsAsync() const { return false; }
    virtual std::future<EngineResult> processAsync(const EngineRequest& req) { ... }
};
```

**已知 Engine Plugins：**

| Plugin | 功能 | 語言 | 可替換為 |
|--------|------|------|---------|
| `engine_promptbim_orchestrator` | AI Agent Pipeline | Python | 任何 LLM orchestrator |
| `engine_promptbim_enhancer` | 需求增強 | Python | GPT/Gemini Agent |
| `engine_promptbim_planner` | 建築規劃 | Python | 任何 planning engine |
| `engine_ilos_layout` | 設備佈局優化 | C++/Python | 第三方佈局引擎 |
| `engine_ilos_piping` | 管路自動路由 | C++/Python | 第三方路由引擎 |
| `engine_compliance_tw` | 台灣法規 | C++ | 日本/美國法規 Plugin |
| `engine_cost` | 成本估算 | C++ | SAP 成本引擎 |
| `engine_mep` | MEP A* 尋路 | C++ | 進階 MEP solver |
| `engine_simulation` | 4D 施工模擬 | C++ | Navisworks 連接器 |

**替換範例：** 把 `engine_promptbim_planner` 從 Claude 換成 GPT-5，只需替換一個 .so/.dll。

### 規範 3: 渲染層高度封裝（本地/遠端/Web 可抽換）

渲染層透過 `IRenderBackend` 介面完全隔離。核心引擎和 UI 只透過此介面操作，不直接呼叫任何渲染 API。

```cpp
class IRenderBackend : public IPlugin {
public:
    // 場景管理
    virtual void loadStage(const UsdStagePtr& stage) = 0;
    virtual void unloadStage() = 0;

    // 渲染控制
    virtual void render(const Camera& cam, FrameBuffer& fb) = 0;  // 本地渲染
    virtual void startStreaming(StreamConfig cfg) {}               // 遠端串流
    virtual void stopStreaming() {}

    // 互動
    virtual PickResult pick(int x, int y) = 0;
    virtual void setSelection(const std::vector<SdfPath>& paths) = 0;

    // 能力查詢
    virtual bool isLocal() const = 0;        // 本地 or 遠端
    virtual bool supportsStreaming() const { return false; }
    virtual int maxMeshCount() const = 0;    // 建議最大 mesh 數
};
```

**渲染後端矩陣：**

| Plugin | 類型 | 場景規模 | 輸出 |
|--------|------|---------|------|
| `render_vtk` | 本地 CPU/GPU | < 1,000 mesh | QWidget 直接繪製 |
| `render_hydra` | 本地 GPU | < 10,000 mesh | QOpenGLWidget |
| `render_omni_local` | 本地 Omniverse Kit | < 50,000 mesh | 視窗內嵌 |
| `render_omni_stream` | 遠端 Omniverse | 無上限 | **WebRTC image stream** |
| `render_omni_cluster` | 遠端叢集 | 超大場景 | **WebRTC image stream** |
| `render_web_threejs` | Web 瀏覽器 | < 5,000 mesh | Canvas/WebGL（未來）|

**整個渲染層可以移除：** Headless 模式下（CLI / 批次處理），不載入任何 render plugin。

### 規範 4: Qt Window 高度模組隔離（可抽換為 Web）

UI Shell 透過 `IShellPlugin` 介面隔離。Qt6 是預設實作，但未來可整體替換為 Web 或 Electron。

```cpp
class IShellPlugin : public IPlugin {
public:
    virtual void createMainWindow(AppContext& ctx) = 0;
    virtual void showPanel(const std::string& panel_id, PanelConfig cfg) = 0;
    virtual void hidePanel(const std::string& panel_id) = 0;
    virtual void setViewport(IRenderBackend* renderer) = 0;
    virtual void showDialog(const DialogSpec& spec) = 0;
    virtual void updateProperty(const PropertyUpdate& update) = 0;
};
```

**Qt6 內部也高度模組化：**

```
shell_qt6.so (IShellPlugin 實作)
├─ QMainWindow
├─ Panel Plugins (各面板獨立 .so)
│   ├─ panel_2d_map.so        — 2D 地籍視圖
│   ├─ panel_3d_viewport.so   — 3D 視埠（接收 IRenderBackend）
│   ├─ panel_chat.so          — AI 對話
│   ├─ panel_asset_browser.so — 廠商資產庫
│   ├─ panel_property.so      — 屬性編輯器
│   ├─ panel_cost.so          — 成本面板
│   ├─ panel_mep.so           — MEP 管路控制
│   └─ panel_simulation.so    — 4D 施工模擬
├─ Dialog Plugins
│   ├─ dialog_import.so
│   ├─ dialog_export.so
│   └─ dialog_settings.so
└─ Qt6 具體實作 (QWidget / QDockWidget)
```

**替換整個 UI：** 把 `shell_qt6.so` 換成 `shell_web.so`（基於 Electron 或純 Web），所有面板透過 WebSocket 與核心通訊。

```
未來 Web 架構:
┌──────────────────────────────────┐
│  Web Browser (React/Vue)         │
│  ├─ WebSocket ↔ Core Server     │
│  └─ WebRTC ← Omniverse Stream   │
└──────────────────────────────────┘
         │ WebSocket (JSON-RPC)
         ▼
┌──────────────────────────────────┐
│  PromptToBuild Core (Headless)   │
│  ├─ Plugin Bus                   │
│  ├─ Engine Plugins               │
│  └─ I/O Plugins                  │
└──────────────────────────────────┘
```

### 規範 5: 多平台策略（Desktop 原生 / Mobile 遠端串流）

| 平台 | 實作方式 | 渲染 | UI Shell |
|------|---------|------|----------|
| **Windows** | 原生 C++ + Qt6 | 本地/Streaming | shell_qt6 |
| **macOS** | 原生 C++ + Qt6 | 本地/Streaming | shell_qt6 |
| **Linux** | 原生 C++ + Qt6 | 本地/Streaming | shell_qt6 |
| **Web Browser** | 未來 | Streaming only | shell_web |
| **iPad** | **獨立 App** | **Remote Streaming** | SwiftUI thin client |
| **iPhone** | **獨立 App** | **Remote Streaming** | SwiftUI thin client |
| **Android** | **獨立 App** | **Remote Streaming** | Compose thin client |

**Mobile/Tablet 架構（遠端串流）：**

```
┌─────────────────────────────┐
│  iPad/iPhone App (SwiftUI)  │
│  ├─ WebRTC Video Player     │  ← 接收渲染畫面
│  ├─ Touch Input → JSON      │  ← 發送觸控事件
│  ├─ Property Inspector      │  ← 輕量本地 UI
│  └─ Offline Cache (USD)     │  ← 離線預覽
└──────────────┬──────────────┘
               │ WebRTC + WebSocket
               ▼
┌─────────────────────────────┐
│  PromptToBuild Cloud Server │
│  ├─ Core Engine (Headless)  │
│  ├─ Omniverse Streaming     │
│  └─ Session Manager         │
└─────────────────────────────┘
```

**Mobile 不執行核心引擎。** 所有計算和渲染在伺服器端完成，只回傳 image stream。

---

## 4. 七層架構圖（v2.1 更新）

```
L7 Client 層:
┌────────────────────────────────────────────────────────────┐
│  Desktop: shell_qt6 (Win/Mac/Linux)                        │
│  Web:     shell_web (Electron / 純 Web) — 未來             │
│  Mobile:  Thin Client (SwiftUI/Compose) — Remote Streaming │
│  CLI:     shell_headless (無 UI，批次處理)                  │
│  MCP:     Claude Desktop 整合                              │
└────────────────────────────────────────────────────────────┘
         │  IShellPlugin interface
L6 UI Panel 層:
┌────────────────────────────────────────────────────────────┐
│  panel_3d_viewport │ panel_chat │ panel_property           │
│  panel_2d_map │ panel_cost │ panel_mep │ panel_sim         │
│  panel_asset_browser │ dialog_import │ dialog_export       │
│  (每個面板獨立 Plugin，可獨立載入/卸載)                     │
└────────────────────────────────────────────────────────────┘
         │  IRenderBackend interface
L5 渲染層:
┌────────────────────────────────────────────────────────────┐
│  render_vtk │ render_hydra │ render_omni_stream            │
│  render_omni_cluster │ render_web_threejs                  │
│  (可完全移除 — Headless 模式)                               │
└────────────────────────────────────────────────────────────┘
         │  IEnginePlugin interface
L4 AI / Engine 層:
┌────────────────────────────────────────────────────────────┐
│  engine_promptbim_* (AI Agent Pipeline)                    │
│  engine_ilos_layout │ engine_ilos_piping                   │
│  engine_compliance_* │ engine_cost │ engine_mep            │
│  (每個引擎獨立 Plugin，AI 部分 Python via libpython)       │
└────────────────────────────────────────────────────────────┘
         │  Core C++ API
L3 核心引擎層:
┌────────────────────────────────────────────────────────────┐
│  USD ↔ Revit Bidirectional Converter (3-Layer)            │
│  BIM Engine (IFC-SPF + USD + USDZ)                        │
│  Unit Conversion │ Instance Resolution │ Geometry Kernel  │
│  (唯一不可插件化的層 — 平台核心)                            │
└────────────────────────────────────────────────────────────┘
         │  IIOPlugin interface
L2 I/O Plugin 層:
┌────────────────────────────────────────────────────────────┐
│  io_usd │ io_revit │ io_ifc │ io_dwg │ io_step           │
│  io_geojson │ io_shapefile │ io_kml │ io_pdf_ocr          │
│  io_fbx │ io_gltf │ io_custom_erp                         │
│  (所有格式進出口都是獨立 Plugin)                            │
└────────────────────────────────────────────────────────────┘
         │
L1 資料層:
┌────────────────────────────────────────────────────────────┐
│  USD Stage Manager (SSOT)                                  │
│  Omniverse Nucleus (omni:// 雲端同步)                     │
│  Asset Library (ilos: spec v2.1 + Vendor USD)             │
│  Configuration (TOML/YAML) │ CI/CD (GitHub Actions)       │
└────────────────────────────────────────────────────────────┘
```

---

## 5. 雙向 USD ↔ Revit（同 v2.0）

| Layer | USD Content | Revit Target | Status | Editable? |
|-------|------------|-------------|--------|----------|
| L1 | Equipment | DirectShape → Adaptive Comp. | v1 ✅ / v2 planned | v1: Move only |
| L2 | Piping | Pipe.Create + NewElbowFitting | ✅ Validated | Full MEP |
| L3 | Structure | Revit native structural | Future Phase 3 | Full |

Instance 解析: `final_xf = inst_xf × proto_inv × mesh_xf`（始終正確）

單位: USD(cm) × 0.01 / 0.3048 = Revit(ft)

---

## 6. ILOS 佈局引擎（同 v2.0，但作為 Plugin 載入）

```
使用者 → engine_promptbim_orchestrator (AI)
  → engine_ilos_layout (設備佈局)
  → engine_ilos_piping (管路路由)
  → io_revit (雙向同步)
  → 輸出: Revit .rvt / BOM / IFC
```

廠商資產: 元件層級（廠商）vs 場景層級（ILOS 自動注入）— spec v2.1

---

## 7. 開發路線圖（v2.1 修訂）

| Phase | Sprints | Focus | Version |
|-------|---------|-------|--------|
| Phase 1 | P26-P29 | Qt6 C++ GUI + IPlugin 基礎 + RAL + Panel Plugin | v3.0.0 |
| Phase 2 | P30-P33 | Windows + io_revit 雙向 + render_hydra | v3.x |
| Phase 3 | P34-P37 | engine_ilos + io_vendor + render_omni_stream | v4.0 |
| Phase 4 | P38-P41 | shell_web + Mobile thin client + Omniverse Cluster | v4.x |
| Phase 5 | P42+ | Enterprise: ERP Plugin + Marketplace + 多人協作 | v5.0+ |

---

## 8. 抽象層對照總表

| 抽象介面 | 隔離什麼 | 預設實作 | 可替換為 |
|---------|---------|---------|---------|
| `IShellPlugin` | UI 框架 | Qt6 | Web / Electron / Headless |
| `IRenderBackend` | 渲染引擎 | VTK | Hydra / Omniverse / Three.js |
| `IIOPlugin` | 檔案格式 | USD+IFC | Revit / DWG / STEP / FBX / 自訂 |
| `IEnginePlugin` | 計算引擎 | PromptBIM AI | ILOS / GPT / Gemini / 自訂 |
| `IPlugin` (base) | 所有擴展 | — | 任何第三方 |

---

## 9. 技術風險（v2.1 更新）

| 風險 | 影響 | 緩解策略 |
|------|------|--------|
| Plugin ABI 穩定性 | 跨版本相容 | 穩定 C ABI + 版本化介面 + 語義版本號 |
| Qt → Web 遷移成本 | IShellPlugin 介面不夠抽象 | 從 P26 開始就用 Panel Plugin 隔離 |
| Remote Streaming 延遲 | Mobile 互動體驗差 | WebRTC + 觸控預測 + 離線 USD 預覽 |
| Plugin 數量爆炸 | 依賴管理複雜 | Plugin Manifest + 依賴圖 + 沙盒載入 |
| AI Plugin 換 LLM | prompt 格式不相容 | 統一 EngineRequest/EngineResult schema |
| Revit 僅限 Windows | Mac/Linux 無法直接操作 | io_revit 作為 Windows 遠端 Plugin |

---

## 10. 版本歷程

| 版本 | 日期 | 變更 |
|------|------|------|
| v2.0 | 2026-03-27 | 初始統一平台架構（ILOS + Omniverse + USD↔Revit） |
| **v2.1** | **2026-03-27** | **五大抽象層規範 + I/O 全插件化 + UI Shell 可抽換 + Mobile 遠端串流** |

---

*PromptToBuild 統一平台架構設計 v2.1*
*Reality Matrix Inc. | 2026-03-27*
*整合: ILOS-FAB + Omniverse + 雙向 USD↔Revit + Plugin 架構 + 遠端渲染*
*v2.1: 五大抽象層強制規範 — IIOPlugin + IEnginePlugin + IRenderBackend + IShellPlugin + Mobile Strategy*
