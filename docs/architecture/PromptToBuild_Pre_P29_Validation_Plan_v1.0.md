# PromptToBuild 抽象層前置驗證計劃

> **版本:** v1.0 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **性質:** 架構決策文件 — P29 前必須完成的抽象層設計與測試
> **前置文件:** PromptToBuild Platform Architecture v2.1

---

## 1. 核心問題：為什麼不能等到 P29 後才設計抽象層？

### 1.1 如果不前置設計會怎樣

```
❌ 錯誤路徑（先實作再抽象）:

P26: 寫死 Qt6 GUI         → P30: 發現無法抽換成 Web → 重寫
P27: 寫死 VTK 渲染        → P33: 接 Omniverse Streaming → 重構渲染層
P28: 寫死 GIS parser       → P34: 接 ILOS USD 輸入 → 重構 I/O 層
P29: 移除 PySide6 → v3.0  → v3.0 架構已經是 tightly coupled → 技術債爆炸

結果: P30+ 每個 Sprint 都在重構，而不是做新功能
```

### 1.2 正確路徑（Interface-First）

```
✅ 正確路徑:

P26: 定義 5 大介面 + 第一個實作驗證
     ├─ IShellPlugin → shell_qt6
     ├─ IRenderBackend → render_vtk
     ├─ IIOPlugin → io_usd + io_geojson
     ├─ IEnginePlugin → engine_compliance_tw
     └─ 用真實 ILOS USD + Revit MCP 測試 I/O 介面

P27-P29: 在已驗證的介面上填充更多實作
     → v3.0 出來時架構已經是 pluggable 的
     → P30+ 只是新增 Plugin，不需要重構
```

### 1.3 結論

**抽象層介面必須在 P26 設計、P27 驗證、P28 穩定、P29 凍結。**

**P26 不是「開始寫 Qt6 GUI」，而是「設計並驗證平台插件化骨架」。**

**前置設計投資回報: 1 Sprint 額外設計 = 省下 4 Sprint 重構。**

---

## 2. 修訂版 P26-P29 路線圖

| Sprint | 原始計劃 | 修訂計劃 |
|--------|---------|---------|
| **P26** | Qt6 C++ GUI 骨架 | **★ 抽象層介面設計 + 首批 Plugin 驗證** |
| **P27** | Qt6 GUI 完整 + 測試 | Qt6 Panel Plugin 完整 + I/O Plugin 完整 |
| **P28** | Python 最小化 + 效能 | Engine Plugin + 渲染 Plugin + 整合測試 |
| **P29** | 清理 + v3.0 | 介面凍結 + 移除舊依賴 + Release v3.0 |

### P26 詳細分解（最關鍵的 Sprint）

```
Part A: 五大介面定義 + Plugin Bus 核心
  T1-T6: IPlugin, IIOPlugin, IEnginePlugin, IRenderBackend, IShellPlugin, 動態載入

Part B: 首批 I/O Plugin + ILOS USD 測試
  T7:  io_usd — 讀寫 .usd（★ 用真實 ILOS 測試 USD）
  T8:  io_geojson — 讀取 .geojson
  T9:  io_ifc — 匯出 .ifc
  T10: io_revit — DirectShape + Pipe.Create（★ 用真實 Revit MCP）

Part C: 首批 Shell + Render Plugin
  T11-T14: shell_qt6, panel_3d_viewport, render_vtk, engine_compliance_tw

Part D: 介面驗證測試
  T15-T18: Plugin 載入/卸載、I/O 交叉測試、渲染切換、Headless 模式
  交付: ≥ 30 介面驗證測試
```

---

## 3. ILOS / USD / Revit 測試計劃

### 3.1 測試檔案

| 類別 | 測試檔案 | 驗證重點 | Sprint |
|------|---------|---------|--------|
| ILOS USD | ILOS_Test_Pipeline_v4.usda | ilos: metadata、Instance 解析、跨樓層管路 | P26 |
| ILOS USD | 廠商 USD (ASML/Swagelok) | /Connections/、Variant Set | P27 |
| ILOS USD | 大型場景 (>1000 mesh) | 效能、記憶體 | P28 |
| Revit | DirectShape 匯入 | io_revit → Revit MCP → 幾何正確 | P26 |
| Revit | MEP Pipe.Create | io_revit → 管路 → 彎頭 → 可編輯 | P26 |
| Revit | 回寫 USD | Revit → io_revit → USD Stage | P28 |
| IFC | 法規送審匯出 | io_ifc → IFC 2x3/4 | P27 |

### 3.2 端對端測試場景（P29 必須全部通過）

```
E2E Test 1: ILOS USD → PromptToBuild → Revit
  輸入: ILOS_Test_Pipeline_v4.usda (3 樓層, 設備, 管路)
  流程: io_usd.import → engine_compliance → io_revit.export → io_ifc.export
  驗證: USD Stage 正確、metadata 保留、Revit 可編輯、IFC 有效

E2E Test 2: Revit → USD 回寫
  輸入: Revit 中修改管路
  流程: Revit event → io_revit.sync → USD Stage update (增量)
  驗證: USD 反映變更、只更新變更的 Prim

E2E Test 3: 渲染 Plugin 熱切換
  流程: render_vtk → 截圖 → 卸載 → render_hydra → 截圖 → render_null
  驗證: 幾何一致、App 不崩潰、Headless 可運作

E2E Test 4: Shell Plugin 切換
  流程 A: shell_qt6 + render_vtk (Desktop)
  流程 B: shell_headless + render_null (CLI)
  驗證: 相同 USD/IFC 輸出、核心引擎行為一致
```

---

## 4. 介面成熟度模型

| 階段 | Sprint | 介面狀態 | 允許的變更 |
|------|--------|---------|----------|
| **Draft** | P26 | 初稿，可能大改 | 任何變更（包括破壞性） |
| **RC** | P27 | 候選發布 | 新增方法可以，刪除/重命名不行 |
| **Stable** | P28 | 穩定 | 只允許新增 optional 方法 |
| **Frozen** | P29 | v3.0 ABI 凍結 | 不允許任何 ABI 變更 |

---

## 5. 風險分析

| 風險（不前置驗證） | 影響 | 嚴重度 |
|------------------|------|:------:|
| 介面不符實際需求 | P30+ 全面重構 | 🔴 Critical |
| ILOS USD 格式變更 | io_usd 重寫 | 🔴 Critical |
| Revit MCP 限制未發現 | io_revit 架構錯誤 | 🟡 High |
| Plugin 載入效能問題 | 啟動 > 10 秒 | 🟡 High |
| Qt6 Panel 隔離不夠 | 無法抽換成 Web | 🟡 High |

---

## 6. P26 驗收標準

```
P26 必須通過（P27 的 Gate）:

☐ Plugin Bus 可載入/卸載至少 3 個 .so Plugin
☐ io_usd 可讀取 ILOS_Test_Pipeline_v4.usda（含 ilos: metadata）
☐ io_usd 可正確解析 USD Instance (inst_xf × proto_inv × mesh_xf)
☐ io_revit 可透過 Revit MCP 建立 DirectShape
☐ io_revit 可透過 Revit MCP 建立 Pipe + Elbow
☐ shell_qt6 透過 IShellPlugin 載入（不是硬編碼）
☐ render_vtk 透過 IRenderBackend 載入（不是硬編碼）
☐ Headless 模式可執行核心引擎
☐ 介面驗證測試 ≥ 30 tests
☐ GUI Plugin 記憶體 < 200MB
```

---

## 7. 結論

**P26 不是「開始寫 Qt6 GUI」，而是「設計並驗證整個平台的插件化骨架」。**

Qt6 只是第一個 IShellPlugin。VTK 只是第一個 IRenderBackend。
**介面才是產品；實作是可替換的。**

---

*PromptToBuild 抽象層前置驗證計劃 v1.0*
*Reality Matrix Inc. | 2026-03-27*
