# Zigma PromptToBuild — MVP-First 開發計劃 v1.0

> **版本:** v1.0 | **日期:** 2026-03-28
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **目標:** 1st MVP / TSMC Demo — Prompt to Build on Qt Quick 3D
> **前置:** Demo-1 ✅ 34/34 Tasks (demo1-v0.1.0), OCCT Migration Plan v1.0

---

## 1. 核心策略：MVP-First, OCCT-Later

### 1.1 TSMC 要看什麼

TSMC 明確需求：
1. **Prompt → BIM 生成** — "建立一個標準工廠" → 3D + 成本 + 工期
2. **Prompt 設計變更** — "變更游泳池成為停車場" → cost/schedule delta
3. **USD → Revit 輸出** (Phase 2)

**TSMC 不在乎渲染引擎用什麼技術，他們要看 AI 智能。**

### 1.2 現有 AI 引擎已驗證

Demo-1 (34/34 Tasks) 已驗證：
- 6 場景 planner ✅
- Modifier (batch + delta) ✅
- Orchestrator (auto cost/schedule/4D) ✅
- Cost engine (22 單價 + estimator) ✅
- 4D simulation (16-phase + scheduler) ✅
- 台灣法規引擎 (含 TSMC 工業法規) ✅
- 零件庫 76→102 件 ✅

### 1.3 唯一要做的：換前端

```
  現有 (OOM 問題)              目標 (MVP)
  ┌──────────────┐            ┌──────────────┐
  │ PySide6 GUI  │            │ Qt Quick 3D  │
  │ PyVista 3D   │  ────→     │ QML GUI      │
  │ matplotlib   │            │ QProcess隔離  │
  └──────┬───────┘            └──────┬───────┘
         │                           │
  ┌──────┴───────┐            ┌──────┴───────┐
  │ Python AI    │            │ Python AI    │
  │ (同一進程    │            │ (獨立進程    │
  │  → OOM 互影響)│            │  → crash不影響GUI)│
  └──────────────┘            └──────────────┘
```

---

## 2. 架構

```
┌─────────────────────────────────┐
│  Qt Quick 3D GUI (QML + C++)   │
│  ChatPanel │ BIMView3D         │
│  CostPanel │ DeltaPanel        │
│  SchedulePanel │ AssetBrowser  │
│  PropertyPanel │ ScenePicker   │
└──────────────┬──────────────────┘
               │ AgentBridge
               │ QProcess + JSON stdio
               │ (OOM 隔離)
┌──────────────┴──────────────────┐
│  Python AI Backend (獨立進程)    │
│  Enhancer → Planner → Builder   │
│  → Checker → Modifier           │
│  Cost Engine │ Schedule Engine   │
│  法規引擎 │ 零件庫               │
│  Claude API                     │
│                                 │
│  ★ 完全不動 — Demo-1 已驗證 ★   │
└─────────────────────────────────┘
```

### AgentBridge Protocol

```json
// Request (C++ → Python)
{"type":"generate","prompt":"建立一個標準工廠","land":{"width":120,"depth":80}}

// Response (Python → C++)  — streaming
{"type":"status","message":"AI 分析需求中...","progress":0.1}
{"type":"status","message":"生成 3D 模型...","progress":0.5}
{"type":"result","model":{"elements":[...],"vertices":[...],"indices":[...]},"cost":{...},"schedule":{...}}

// Modify Request
{"type":"modify","intent":"變更游泳池成為員工停車場"}

// Modify Response
{"type":"delta","cost_delta":-2800000,"schedule_delta":-10,"gfa_delta":200,"model":{...}}
```

### Python mesh → Qt Quick 3D 渲染

```
Python Builder 產出:
  vertices: [[x,y,z], ...]     ← 現有 mesh 資料
  indices:  [[i0,i1,i2], ...]  ← 三角面索引
  elements: [{type:"wall", material:"concrete", ...}]

    ↓ JSON stdio

C++ BIMGeometryProvider : QQuick3DGeometry
  loadFromJSON(meshData)
  → setVertexData(QByteArray)
  → setIndexData(QByteArray)
  → setBounds(min, max)
  → PrincipledMaterial by element type
```

---

## 3. Sprint 計劃

### 總覽

| Sprint | 內容 | 週數 | Tasks | Tag |
|--------|------|:----:|:-----:|-----|
| M1-S1 | AgentBridge + Qt Quick 3D 骨架 | 2.5 | 25 | mvp-v0.1.0-alpha |
| M1-S2 | Cost + Delta + 4D + TSMC 場景 | 2.5 | 25 | mvp-v0.1.0-beta |
| M1-S3 | 打磨 + USD I/O + Release | 2 | 20 | **mvp-v0.1.0** ★ |
| **總計** | | **~7 週** | **70** | |

---

### M1-S1: AgentBridge + Qt Quick 3D 骨架 (~2.5 週, 25T)

#### Part A: AgentBridge — Python↔C++ 通訊 (8T)

| Task | 說明 | 驗收 |
|------|------|------|
| T1 | CMakeLists.txt: Qt6 Quick + Quick3D + Core | cmake 成功 |
| T2 | AgentBridge (C++): QProcess spawn agent_runner.py, JSON stdio, heartbeat 120s, OOM 隔離 | Python crash 不影響 GUI |
| T3 | agent_runner.py: asyncio event loop, 接收 JSON → 呼叫既有 orchestrator, streaming response | 能接收 generate/modify |
| T4 | JSON Protocol: generate/modify/get_cost/get_schedule request/response schema | 文件定義完成 |
| T5 | mesh 序列化: Python Builder mesh → JSON vertex/index/element | 資料格式正確 |
| T6 | AgentBridge 單元測試 ≥ 5 ctest | pass |
| T7 | agent_runner 單元測試 ≥ 5 pytest | pass |
| T8 | E2E: prompt → Python → JSON → C++ 收到結果 | 端到端通過 |

#### Part B: Qt Quick 3D 渲染核心 (8T)

| Task | 說明 | 驗收 |
|------|------|------|
| T9 | BIMGeometryProvider : QQuick3DGeometry, loadFromJSON | mesh 渲染正確 |
| T10 | BIMMaterialLibrary: concrete/glass/steel/wood → PrincipledMaterial PBR | 材質可見 |
| T11 | BIMSceneBuilder: JSON model → 為每個 BIM element 建立 Model QML node | 多元素場景 |
| T12 | BIMView3D.qml: View3D + PerspectiveCamera + OrbitCameraController | 可旋轉縮放 |
| T13 | Picking: View3D pick → element ID → signal | 點擊選取 |
| T14 | 多視角: Perspective / Top / Front / Right 切換 | 4 視角 |
| T15 | benchmark: Demo-1 S2 Fab 場景渲染 < 300MB | 記憶體達標 |
| T16 | ctest ≥ 10 tests | pass |

#### Part C: 最小 QML GUI (9T)

| Task | 說明 | 驗收 |
|------|------|------|
| T17 | main.qml: ApplicationWindow + SplitView (左Chat/中3D/右Property) | 佈局正確 |
| T18 | ChatPanel.qml: TextInput + Send + streaming AI 回覆 + 歷史 | 可對話 |
| T19 | PropertyPanel.qml: 點擊 3D → 顯示 BIM type/dimensions/material/cost | 屬性顯示 |
| T20 | StatusBar.qml: 記憶體 / AI 狀態 / 生成進度 | 狀態可見 |
| T21 | ChatPanel ↔ AgentBridge 連接 | prompt 可發送 |
| T22 | BIMView3D ↔ BIMSceneBuilder 連接 | AI 結果可渲染 |
| T23 | Picking → PropertyPanel 連接 | 點擊顯示屬性 |
| T24 | Mac build 驗證 (Metal) | build + run |
| T25 | Win build 驗證 (D3D12/Vulkan) | build + run |

🏷️ **mvp-v0.1.0-alpha**

---

### M1-S2: Cost + Delta + 4D + TSMC 場景 (~2.5 週, 25T)

#### Part A: CostPanel + DeltaPanel (8T)

| Task | 說明 | 驗收 |
|------|------|------|
| T1 | CostPanel.qml: 總成本 NT$ + 分項圓餅圖 (Canvas/ChartView) | 成本可見 |
| T2 | DeltaPanel.qml: Before/After 對照 + 成本/GFA/工期增減 + Undo | Delta 正確 |
| T3 | Modifier E2E: "變更游泳池成為停車場" → delta JSON → DeltaPanel + 3D 更新 | 端到端 |
| T4 | Cost 資料綁定: Python cost engine → JSON → QML property binding | 即時更新 |
| T5 | Delta 動畫: 數字滾動 + 色彩 (綠↓紅↑) | 視覺回饋 |
| T6 | Undo/Redo stack: 最近 10 次修改 | 可撤銷 |
| T7 | 多次修改累計: Delta 歷史列表 | 歷史可見 |
| T8 | ctest ≥ 5 | pass |

#### Part B: SchedulePanel + 4D (8T)

| Task | 說明 | 驗收 |
|------|------|------|
| T9 | SchedulePanel.qml: 甘特圖 (Canvas) + 16-phase + 總天數 | 甘特圖正確 |
| T10 | 4D Timeline Slider: 拖動 → BIMView3D visibility/opacity 聯動 + Play/Pause + 速度 | 動畫播放 |
| T11 | Gantt ↔ 3D 雙向聯動 | 點擊同步 |
| T12 | 施工機械 3D: 起重機/挖土機隨 timeline 移動 | 機械動畫 |
| T13 | Phase 顏色: 已完工(實色)/施工中(半透明)/未開始(隱藏) | 視覺正確 |
| T14 | 截圖匯出: 當前 3D → PNG | 可匯出 |
| T15 | schedule 資料綁定: Python → JSON → QML | 即時更新 |
| T16 | ctest ≥ 5 | pass |

#### Part C: TSMC Demo 場景 (9T)

| Task | 說明 | 驗收 |
|------|------|------|
| T17 | ScenePicker.qml: S1 別墅 / S2 Fab / S3 DC | 可切換 |
| T18 | S2 半導體廠房: "建立TSMC風格半導體廠 120m×80m" → 全流程 | 3D+成本+4D |
| T19 | S3 數據中心 場景驗證 | 全流程 |
| T20 | S1 別墅 場景驗證 | 全流程 |
| T21 | 修改 E2E: "請將 2F Data Hall 高度增加到 6m" → Delta 正確 | GFA+成本+工期 |
| T22 | 修改 E2E: "變更游泳池成為員工停車場" → Delta 正確 | 正確計算 |
| T23 | AssetBrowser.qml: 零件搜尋 + 點擊替換 + 成本更新 | 替換可用 |
| T24 | 法規面板: TW-IND-001~004 合規 checklist | 法規顯示 |
| T25 | 完整 7 分鐘 Demo 腳本 walkthrough | 無中斷跑完 |

🏷️ **mvp-v0.1.0-beta**

---

### M1-S3: 打磨 + USD I/O + Release (~2 週, 20T)

#### Part A: io_usd — ILOS USD 支援 (6T)

| Task | 說明 | 驗收 |
|------|------|------|
| T1 | io_usd import: 讀取 ILOS USD + ilos: metadata | metadata 正確 |
| T2 | io_usd import: /Connections/ 解析 | 連接點正確 |
| T3 | io_usd import: Instance 解析 (inst_xf × proto_inv × mesh_xf) | 座標正確 |
| T4 | io_usd export: mesh → USD + ilos: metadata | 可被 Omniverse 開啟 |
| T5 | ILOS_Test_Pipeline_v4.usda 載入 + 3D 顯示 | 完整渲染 |
| T6 | ilos: metadata 在 PropertyPanel 顯示 | category/part_number 可見 |

#### Part B: 展示打磨 (8T)

| Task | 說明 | 驗收 |
|------|------|------|
| T7 | Dark/Light theme 切換 | 兩主題可用 |
| T8 | Loading animation: AI 生成進度指示器 | 進度可見 |
| T9 | 歡迎畫面: Zigma PromptToBuild 品牌 | 品牌顯示 |
| T10 | 鍵盤快捷鍵: Space/F/1-4 | 操作順暢 |
| T11 | RTX 4090 GPU 渲染優化 | FPS ≥ 30 |
| T12 | Mac Metal 渲染驗證 | Mac 可用 |
| T13 | 記憶體 profiling: 全場景 < 500MB | 不 OOM |
| T14 | crash recovery: Python crash → GUI 不掛 → 自動重啟 Python | 穩定 |

#### Part C: Release (6T)

| Task | 說明 | 驗收 |
|------|------|------|
| T15 | E2E: 3 場景 × 2 修改 = 6 scenarios | 全部通過 |
| T16 | Demo 腳本 v2.0 (Qt Quick 3D 版) | 7 分鐘無中斷 |
| T17 | TSMC 簡報 v2.0 | 10 頁更新 |
| T18 | SKILL.md v5.0 更新 | 推送 |
| T19 | PROJECT.md 更新 | 推送 |
| T20 | git tag mvp-v0.1.0 | tag 存在 |

🏷️ **mvp-v0.1.0 — 1st MVP / TSMC Demo Ready** ★

---

## 4. Phase 2: Revit 輸出 + OCCT 引入 (MVP 之後, ~6 週)

| Sprint | 內容 | 週數 | Tag |
|--------|------|:----:|-----|
| P30 | io_revit: 夥伴 Converter 整合 (L1+L2) | 2 | v2.13.0 |
| P31 | OCCT Kernel: Wall/Slab/Column/Pipe B-Rep + Boolean | 2 | v2.14.0 |
| P32 | 清理 PySide6 + Plugin Bus + ABI 凍結 | 2 | **v3.0.0** |

### Phase 2 完成後的四個工作流

| 工作流 | MVP | Phase 2 |
|--------|:---:|:-------:|
| W1: ILOS USD → Revit | ⚠️ 可顯示 | ✅ 可輸出 Revit |
| W2: Prompt → Revit | ⚠️ 可建模 | ✅ 可輸出 Revit |
| W3: Zigma → USD | ✅ | ✅ |
| W4: 設計變更 → Delta | ✅ | ✅ + OCCT Boolean |

---

## 5. TSMC Demo 驗收矩陣

| TSMC 需求 | Demo-1 (已完成) | MVP (目標) |
|-----------|:-:|:-:|
| "建立一個標準工廠" → 3D | ✅ PySide6 | ✅ **Qt Quick 3D** |
| 成本估算 (NT$) | ✅ | ✅ CostPanel |
| 4D 施工模擬 + Gantt | ✅ | ✅ 雙向聯動 |
| "變更游泳池成為停車場" → Delta | ✅ | ✅ DeltaPanel |
| 法規核查 (TW-IND) | ✅ | ✅ |
| USD import (ILOS) | ❌ | ✅ **新增** |
| USD export | ❌ | ✅ **新增** |
| GPU 渲染 (Metal/Vulkan) | ❌ PyVista | ✅ **Qt Quick 3D RHI** |
| 記憶體穩定 | ⚠️ OOM | ✅ **QProcess 隔離** |
| Revit 輸出 | ❌ | ❌ → Phase 2 (P30) |

---

## 6. 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| v1.0 | 2026-03-28 | MVP-First 計劃：7 週 70T 到 TSMC Demo |

---

*Zigma PromptToBuild MVP-First Plan v1.0*
*Reality Matrix Inc. | 2026-03-28*
*7 週 · 70 Tasks · Prompt to Build on Qt Quick 3D*
