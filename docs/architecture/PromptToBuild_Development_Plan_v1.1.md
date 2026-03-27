# PromptToBuild 軟體開發計劃

> **版本:** v1.1 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **範圍:** P25 收尾 → P45+ 全 SaaS（七階段）
> **前置文件:** PromptToBuild Architecture v2.1 + Pre-P29 Validation Plan v1.0

---

## 開發階段總覽

| Phase | Sprint | 目標 | 版本 | 預估週數 |
|-------|--------|------|------|:--------:|
| **Phase 0** | P25收尾+P24 | 現有 POC 收尾 | v2.11-2.12 | 1 |
| **Phase 1** | P26-P29 | 介面設計 + Qt6 C++ + Plugin 架構 | **v3.0** | 8 |
| **Phase 2** | P30-P33 | Windows + 雙向 USD↔Revit + Hydra | **v3.x** | 8 |
| **Phase 3** | P34-P37 | ILOS Engine + Omniverse Streaming | **v4.0** | 8 |
| **Phase 4** | P38-P41 | Web Client + Session Manager + Mobile | **v4.x** | 8 |
| **Phase 5** | P42-P44 | 私有 LLM + 去除外部 AI | **v5.0** | 6 |
| **Phase 6** | P45-P50+ | Omniverse Extension + 多租戶 SaaS | **v5.x+** | 持續 |

---

## Phase 0: 現有 POC 收尾（1 週）

### P25 收尾 + P24 pytest 修復

#### Part A: P25 驗收（1 天）

| Task | 說明 | 驗收標準 |
|------|------|---------|
| T1 | 確認 P25 Part A/B/C commit 完整性 | 版本號一致 |
| T2 | Mac Mini pytest 安全模式 | offscreen + ignore e2e pass |
| T3 | Sprint25_AuditReport.md | 推送到 repo |
| T4 | git tag v2.12.0 | tag 存在 |
| T5 | PROJECT_STATUS.md 更新 | P25 ✅ |

#### Part B: P24 pytest OOM 修復（1 天）

| Task | 說明 | 驗收標準 |
|------|------|---------|
| T6 | conftest.py QT_QPA_PLATFORM=offscreen | 檔案已修改 |
| T7 | 逐目錄 pytest 找 OOM 元凶 | 安全目錄清單 |
| T8 | pytest 安全模式全通過 | pass |
| T9 | git tag v2.11.0 | tag 存在 |

#### Part C: Omniverse 前置驗證（2 天）

| Task | 說明 | 驗收標準 |
|------|------|---------|
| T10 | Win: Omniverse Nucleus 驗證 | localhost 可存取 |
| T11 | Win: ILOS 測試 USD 載入 | 場景正確顯示 |
| T12 | Win: USD→Revit DirectShape 測試 | 幾何正確 |
| T13 | Win: Pipe.Create + Elbow 測試 | 管路可編輯 |
| T14 | Win: Omniverse Streaming 測試 | MacBook 瀏覽器可接收 |
| T15 | .env API_TIMEOUT_SECONDS=120 | CLI 不逾時 |

---

## Phase 1: 介面設計 + Qt6 C++ + Plugin 架構（P26-P29, 8 週）

### P26: 抽象層介面設計 + 首批 Plugin 驗證（2 週, 30 Tasks）

> **P26 是整個平台最關鍵的 Sprint — 定義 6 大介面，用真實檔案驗證**

#### Part A: 六大介面定義 + Plugin Bus（3 天）

| Task | 說明 | 交付物 |
|------|------|-------|
| T1 | IPlugin base + PluginContext + PluginRegistry | iplugin.hpp |
| T2 | IIOPlugin + IOPluginManager | iio_plugin.hpp |
| T3 | IEnginePlugin + EnginePluginManager | iengine_plugin.hpp |
| T4 | IRenderBackend + RenderManager | irender_backend.hpp |
| T5 | IShellPlugin + PanelPlugin 子介面 | ishell_plugin.hpp |
| T6 | ITransport + InProcessTransport | itransport.hpp |
| T7 | Plugin 動態載入 (dlopen/LoadLibrary) | plugin_loader.cpp |
| T8 | Command/Response/Event protocol | protocol.hpp |

#### Part B: 首批 I/O Plugin + ILOS USD 測試（3 天）

| Task | 說明 | 交付物 |
|------|------|-------|
| T9 | io_usd Plugin — 讀寫 .usd/.usda/.usdc | plugins/io_usd/ |
| T10 | ★ ILOS USD 測試: ILOS_Test_Pipeline_v4.usda | ilos: metadata 完整 |
| T11 | ★ USD Instance 解析 (inst_xf × proto_inv × mesh_xf) | 座標正確 |
| T12 | io_geojson Plugin | plugins/io_geojson/ |
| T13 | io_ifc Plugin — 匯出 .ifc | plugins/io_ifc/ |
| T14 | io_revit Plugin 骨架 — MCP 封裝 | plugins/io_revit/ |
| T15 | ★ Revit DirectShape 匯入測試 | 幾何正確 |
| T16 | ★ Revit Pipe.Create+Elbow 測試 | 管路可編輯 |

#### Part C: 首批 Shell + Render Plugin（2 天）

| Task | 說明 |
|------|------|
| T17 | shell_qt6 Plugin (IShellPlugin) |
| T18 | panel_3d_viewport (IRenderBackend) |
| T19 | render_vtk Plugin |
| T20 | render_null Plugin (Headless) |
| T21 | engine_compliance_tw Plugin |

#### Part D: 介面驗證測試（2 天）

| Task | 說明 | 驗收標準 |
|------|------|---------|
| T22 | Plugin 載入/卸載/替換 | 3+ Plugin 不崩潰 |
| T23 | I/O 交叉: USD→Revit 全流程 | ILOS USD → Revit 正確 |
| T24 | I/O 交叉: USD→IFC | IFC schema 有效 |
| T25 | Render 替換: VTK→null | 不崩潰 |
| T26 | Shell Headless 測試 | 核心引擎可運作 |
| T27 | ITransport InProcess 測試 | Panel 透過 Transport 通訊 |
| T28 | 記憶體測試 | GUI < 200MB |
| T29 | 介面驗證測試套件 | ≥ 30 ctest |
| T30 | P26 審計報告 + PROMPT_P27 | 文件推送 |

---

### P27: Plugin 完整化 + 測試遷移（2 週, 26 Tasks）

> 介面狀態: **RC（候選發布）** — 可新增方法，不可刪除/重命名

#### Part A: I/O Plugin 擴充（7T）

| Task | 說明 |
|------|------|
| T1-T4 | io_shapefile / io_kml / io_dxf / io_pdf_ocr |
| T5 | io_revit 雙向 sync 骨架 (DocumentChanged event) |
| T6 | ★ ILOS 廠商 USD: Swagelok (/Connections/, Variant Set) |
| T7 | ★ ILOS E2E: USD → Plugin Bus → Revit MEP |

#### Part B: Qt6 Panel Plugin 完整化（8T）

| Task | 說明 |
|------|------|
| T8-T15 | panel_chat / property / cost / mep / sim / asset / 2d_map / dialog |

#### Part C: Engine Plugin 擴充（5T）

| Task | 說明 |
|------|------|
| T16-T19 | engine_orchestrator / enhancer / planner / checker (Python) |
| T20 | engine_cost + engine_mep (C++) |

#### Part D: 測試遷移（6T）

| Task | 說明 |
|------|------|
| T21-T24 | Qt Test + ctest, pytest-qt 遷移, ≥50 tests, CI 更新 |
| T25 | IFC 匯出 schema 驗證 |
| T26 | P27 審計 + PROMPT_P28 |

---

### P28: 效能優化 + 渲染擴充（2 週, 20 Tasks）

> 介面狀態: **Stable** — 只允許新增 optional 方法

#### Part A: 渲染 Plugin 擴充（4T）

| Task | 說明 |
|------|------|
| T1 | render_hydra (Hydra Storm) |
| T2 | RAL 自動選擇策略 |
| T3 | ★ render_omni_stream 骨架 |
| T4 | RTX 4090 Hydra 測試 |

#### Part B: 效能驗證（6T）

| Task | 說明 | 目標 |
|------|------|------|
| T5-T10 | GUI<200MB, Core<100MB, test<500MB, Plugin<2s, ★ 1000+mesh, Benchmark |

#### Part C: Python 最小化（4T）

| Task | 說明 |
|------|------|
| T11-T14 | AI only Python, libpython 穩定, GIL, 確認 C++ 原生 |

#### Part D: 穩定性 + 回寫原型（6T）

| Task | 說明 |
|------|------|
| T15-T16 | ABI 版本測試, 熱載入 |
| T17 | ★ Revit→USD 回寫原型 |
| T18 | ★ 回寫驗證: Revit→USD→Omniverse |
| T19 | ITransport 壓力測試 |
| T20 | P28 審計 + PROMPT_P29 |

---

### P29: 介面凍結 + Release v3.0.0（2 週, 20 Tasks）

> 介面狀態: **Frozen** — v3.0 ABI 凍結

#### Part A: 介面凍結 + SDK（4T）

| Task | 說明 |
|------|------|
| T1-T4 | 6 大介面 v3.0 ABI, Plugin SDK 文件, Template, 版本檢查 |

#### Part B: 舊依賴移除（4T）

| Task | 說明 |
|------|------|
| T5-T8 | 移除 PySide6, SwiftUI Wrapper, pytest-qt, 清理 CMake |

#### Part C: E2E 驗證（6T）

| Task | 說明 |
|------|------|
| T9 | ★ E2E 1: ILOS USD → Revit |
| T10 | ★ E2E 2: Revit → USD 回寫 |
| T11 | ★ E2E 3: 渲染切換 VTK→Hydra→Null |
| T12 | ★ E2E 4: Shell 切換 Qt6→Headless |
| T13 | ★ E2E 5: ITransport 可替換性 |
| T14 | 跨平台: Win+Mac 同 Plugin 集 |

#### Part D: Release（6T）

| Task | 說明 |
|------|------|
| T15-T20 | v3.0.0 tag, SKILL v4.0, CLAUDE v1.23.0, SDK v1.0, P29 審計, PROMPT_P30 |

---

## Phase 2: Windows + 雙向 USD↔Revit + Hydra Storm（P30-P33, 8 週）

### P30: Windows 全功能（2 週, 14T）

- **Part A (4T):** CMake/vcpkg Win 全依賴, ci-windows.yml, NSIS installer, Plugin 路徑
- **Part B (6T):** Revit MCP 穩定化, L1 Equipment→DirectShape, L2 Pipe+Elbow+Valve, 跨樓層, SharedParameter, 圖面輸出
- **Part C (4T):** Win 全 Plugin 測試, Revit E2E, RTX benchmark, P30 審計

### P31: USD→Revit Layer 2/3 完整（2 週, 13T）

- **Part A (5T):** Valve→FamilyInstance, Valve 三層 fallback, Tee, Reducer, 系統對應
- **Part B (4T):** Column→Revit, Beam→Revit, Slab→Floor, 結構 Level
- **Part C (4T):** Adaptive Component 原型, OmniPBR→Material, Mesh 合併, P31 審計

### P32: Revit→USD 回寫（2 週, 12T）

- **Part A (5T):** DocumentChanged, 變更偵測, Element→Prim 映射, 增量 Sync, TfNotice
- **Part B (4T):** 測試: 改管徑/拖端點/新增管路/循環驗證
- **Part C (3T):** Nucleus 同步, Omniverse 即時顯示, P32 審計

### P33: Hydra Storm 本地 GPU（2 週, 11T）

- **Part A (4T):** Hydra+QOpenGLWidget, Stage 載入, 相機控制, Pick+Highlight
- **Part B (3T):** RAL 自動選擇, 熱切換, 品質設定
- **Part C (4T):** RTX benchmark(10K), Mac Metal, VTK vs Hydra 報告, P33 審計

---

## Phase 3: ILOS Engine + Omniverse Streaming（P34-P37, 8 週）

### P34: ILOS 佈局引擎核心（2 週, 11T）

- **Part A (5T):** engine_ilos_layout 骨架, 設備放置(間距), 振動(VC), 潔淨度(ISO), 多樓層
- **Part B (6T):** engine_ilos_piping, 3D A*路由, 跨樓層垂直管, 碰撞迴避, metadata注入, P34審計

### P35: 廠商資產庫（2 週, 12T）

- **Part A (4T):** ilos: v2.1 驗證, /Connections/ 檢查, Variant Set, 自動修復
- **Part B (4T):** Asset Library DB, panel_asset_browser, 匯入工作流, STEP→USD
- **Part C (4T):** ASML/Swagelok/Edwards 測試, P35 審計

### P36: Omniverse Nucleus 整合（2 週, 10T）

- **Part A (4T):** omni:// 連線, Stage 發布/讀取, Layer Stack, Checkpoint
- **Part B (3T):** Live Sync 雙向, 變更通知, 衝突解決
- **Part C (3T):** USD↔Core↔Revit 三向同步, 延遲<5s, P36 審計

### P37: Omniverse Streaming（2 週, 11T）

- **Part A (5T):** Kit 啟動, Pixel Streaming, WebRTC Widget, 事件轉發, 自適應品質
- **Part B (3T):** RAL 自動切換, 無感切換, 延遲監控
- **Part C (3T):** 1000+mesh 測試, MacBook→Win 測試, P37 審計

---

## Phase 4: Web Client + Session Manager + Mobile（P38-P41, 8 週）

### P38: ITransport 網路化 + Session Manager（2 週, 11T）

- **Part A (4T):** WebSocketTransport (JSON-RPC), 序列化, Event 推送, 斷線重連
- **Part B (3T):** Session Manager, JWT 認證, 每 Session 獨立 Stage
- **Part C (4T):** Server 部署(Docker), Headless 啟動, API Gateway, P38 審計

### P39: shell_web 實作（2 週, 11T）

- **Part A (5T):** shell_web (React), WebSocket→ITransport, WebRTC Player, 面板框架, 觸控
- **Part B (6T):** panel_chat/property/asset Web版, dialog, 響應式佈局, P39 審計

### P40: Mobile Thin Client（2 週, 10T）

- **Part A (5T):** SwiftUI iPad 骨架, WebRTC Player, Touch→Command, Property Inspector, 離線預覽
- **Part B (5T):** iPad↔Server E2E, 延遲<100ms, 頻寬測試, Android 骨架(選), P40 審計

### P41: 三端整合 + Release v4.0（2 週, 18T）

#### Part A: 三端整合測試（5T）

| Task | 說明 |
|------|------|
| T1 | Desktop (Qt6) + Server E2E |
| T2 | Web Client (React) + Server E2E |
| T3 | iPad App + Server E2E |
| T4 | 三端同時連同一 Session |
| T5 | 三端不同 Session 隔離 |

#### Part B: 壓力測試（4T）

| Task | 說明 |
|------|------|
| T6 | 10 用戶同時連線 |
| T7 | Session 超時回收 |
| T8 | 斷線重連 |
| T9 | Streaming 多 Session 分配 |

#### Part C: 安全審計（4T）

| Task | 說明 |
|------|------|
| T10 | WebSocket TLS (wss://) |
| T11 | JWT Token + 過期 |
| T12 | CORS 白名單 |
| T13 | Stage 存取隔離 |

#### Part D: Release v4.0.0（5T）

| Task | 說明 |
|------|------|
| T14-T18 | v4.0.0 tag, SKILL v5.0, DEPLOY.md, P41 審計 |

---

## Phase 5: 私有 LLM + 去除外部 AI（P42-P44, 6 週）

### P42: 私有 LLM 伺服器部署（2 週, 15T）

#### Part A: LLM 伺服器建置（5T）

| Task | 說明 |
|------|------|
| T1 | LLM 框架選型: vLLM vs NeMo vs TGI |
| T2 | 模型選型: Llama 3.x / Qwen 2.x / Mistral |
| T3 | GPU VRAM 評估 (RTX 4090 24GB) |
| T4 | LLM Server Docker 部署 |
| T5 | OpenAI 相容 API (/v1/chat/completions) |

#### Part B: engine_planner_local（5T）

| Task | 說明 |
|------|------|
| T6 | engine_planner_local Plugin 骨架 |
| T7 | Planner prompt 適配本地模型 |
| T8 | JSON 格式驗證 + 自動修復 |
| T9 | 多輪迭代策略 |
| T10 | Chain-of-Thought 分步引導 |

#### Part C: 品質對比（5T）

| Task | 說明 |
|------|------|
| T11 | 10 案例測試集 |
| T12 | Claude vs 本地品質對比 |
| T13 | 回應時間 benchmark |
| T14 | VRAM 監控 |
| T15 | P42 審計 + PROMPT_P43 |

### P43: AI Agent 全本地化（2 週, 16T）

#### Part A: Enhancer + Checker（4T）

| Task | 說明 |
|------|------|
| T1 | engine_enhancer_local (≥80% of Claude) |
| T2 | engine_checker_local (≥90% 準確) |
| T3-T4 | 兩者 prompt 最佳化 |

#### Part B: Modifier + LandReader（4T）

| Task | 說明 |
|------|------|
| T5 | engine_modifier_local |
| T6 | engine_land_reader_local (Vision) |
| T7 | Vision 模型部署 (LLaVA/InternVL) |
| T8 | Vision 品質對比 |

#### Part C: 移除外部依賴（4T）

| Task | 說明 |
|------|------|
| T9 | 移除 Anthropic SDK |
| T10 | 移除 .env ANTHROPIC_API_KEY |
| T11 | 防火牆零外部連線 (tcpdump) |
| T12 | BUILD_WITHOUT_EXTERNAL_AI=ON |

#### Part D: 全本地 E2E（4T）

| Task | 說明 |
|------|------|
| T13 | E2E: 全流程零外部 API |
| T14 | 品質回歸 ≥75% |
| T15 | 性能 <5min/案例 |
| T16 | P43 審計 + PROMPT_P44 |

### P44: Release v5.0 — 完全私有化（2 週, 17T）

#### Part A: 零外部連線審計（4T）

| Task | 說明 |
|------|------|
| T1 | 72h 零外部連線監控 |
| T2 | 離線依賴快取 |
| T3 | USD 資產本地儲存 |
| T4 | LLM 權重本地儲存 |

#### Part B: 部署指南（5T）

| Task | 說明 |
|------|------|
| T5 | 硬體需求規格書 |
| T6 | Omniverse Server SOP |
| T7 | Core Server SOP |
| T8 | LLM Server SOP |
| T9 | Docker Compose 一鍵部署 |

#### Part C: 合併部署（3T）

| Task | 說明 |
|------|------|
| T10 | docker compose up 全部 |
| T11 | Health check /api/health |
| T12 | 自動重啟策略 |

#### Part D: Release v5.0.0（5T）

| Task | 說明 |
|------|------|
| T13 | v5.0.0 tag |
| T14 | DEPLOY_ON_PREMISE.md |
| T15 | 安全白皮書 |
| T16 | git tag |
| T17 | P44 審計 + PROMPT_P45 |

---

## Phase 6: Omniverse Extension + 多租戶 SaaS（P45-P50+）

### P45: Kit Extension（2 週, 11T）

| Part | Tasks | 說明 |
|------|-------|------|
| A: 骨架 | T1-T4 | Extension 初始化, Core 封裝, Plugin Bus, Stage 共享(零複製) |
| B: UI | T5-T8 | Kit UI Panel(omni.ui), Chat, Property, 共用 Viewport |
| C: 驗證 | T9-T11 | Launcher 安裝, Kit 內 E2E, P45 審計 |

### P46: 多租戶架構（2 週, 11T）

| Part | Tasks | 說明 |
|------|-------|------|
| A: 隔離 | T1-T5 | Tenant UUID, Stage 隔離, LLM 隔離, Session 多租戶, SSO |
| B: 配額 | T6-T8 | GPU 時間, 儲存, 並行 Session |
| C: 管理 | T9-T11 | Admin Dashboard, 計費 API, P46 審計 |

### P47: BOM→SAP/ERP（2 週, 11T）

| Part | Tasks | 說明 |
|------|-------|------|
| A: BOM | T1-T4 | ilos: metadata→BOM, 數量統計, 成本, PDF 報表 |
| B: ERP | T5-T8 | io_erp_sap (RFC/BAPI), 物料對應, 採購單, Oracle(選) |
| C: 驗證 | T9-T11 | 100+設備 BOM, SAP Mock, P47 審計 |

### P48: 多人協作（2 週, 10T）

| Part | Tasks | 說明 |
|------|-------|------|
| A: Nucleus | T1-T5 | Live Session, 游標可見, 衝突視覺化, Audio, 權限 |
| B: 功能 | T6-T8 | AI 對話共享, Audit log, 回滾 |
| C: 驗證 | T9-T10 | 3 用戶同時編輯, P48 審計 |

### P49: Omniverse Cluster（2 週, 10T）

| Part | Tasks | 說明 |
|------|-------|------|
| A: 設定 | T1-T5 | Farm Cluster, Spatial partition, Tile composition, 負載平衡, GPU 監控 |
| B: 測試 | T6-T8 | 100K+mesh FPS≥30, 1M+mesh, 故障轉移 |
| C: 驗證 | T9-T10 | 10 用戶+Cluster 穩定 1h, P49 審計 |

### P50: Plugin Marketplace（2 週, 10T）

| Part | Tasks | 說明 |
|------|-------|------|
| A: 基礎 | T1-T5 | 打包格式, 代碼簽署, Registry, CLI install, Web 前端 |
| B: DX | T6-T8 | SDK v2.0, Template Generator, 沙盒 |
| C: 驗證 | T9-T10 | 模擬第三方全流程, P50 審計 |

---

## 附錄 A: Sprint 依賴關係圖

```
P25 → P26 (Interface) → P27 (Plugin) → P28 (Perf) → P29 (v3.0)
                                                         │
  P30 (Windows) → P31 (USD→Revit L2/3) → P32 (Revit→USD) → P33 (Hydra)
                                                                │
  P34 (ILOS) → P35 (Assets) → P36 (Nucleus) → P37 (Streaming)
                                                    │
  P38 (Transport) → P39 (Web) → P40 (Mobile) → P41 (v4.0)
                                                    │
  P42 (LLM) → P43 (AI Local) → P44 (v5.0)
                                    │
  P45 (Extension) → P46 (Multi-tenant) → P47 (ERP)
  P48 (Collab) → P49 (Cluster) → P50 (Marketplace)
```

## 附錄 B: 數據彙整

| 指標 | 數值 |
|------|------|
| 開發階段 | 7 個 Phase (Phase 0-6) |
| Sprint 數 | 26 個具名 Sprint (P25-P50) |
| Part 數 | ~100 Parts |
| Task 數 | 350+ Tasks |
| 預估時程 | 15+ 個月 (2026 Q2 → 2027 Q3+) |
| 最關鍵 Sprint | **P26**（介面設計 — 決定架構成敗） |
| 最終形態 | 私有數據中心 + Omniverse Server + 純 Web/Mobile 介面 |

---

*PromptToBuild 軟體開發計劃 v1.1*
*Reality Matrix Inc. | 2026-03-27*
*七階段 · 50+ Sprints · 350+ Tasks*
