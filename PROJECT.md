# Zigma PromptToBuild 專案管理

> **版本:** v1.4 | **最後更新:** 2026-03-27
> **專案:** Zigma PromptToBuild (PromptBIMTestApp1)
> **組織:** Reality Matrix Inc.
> **倉庫:** github.com/chchlin1018/PromptBIMTestApp1

---

## 1. 版本控制

| 標籤 | 版本 | Sprint/Demo | 日期 | 說明 |
|------|------|------------|------|------|
| v2.10.0 | 2.10.0 | P23 | 2026-03 | 審計修復（最後成功 tag） |
| v2.11.0 | 2.11.0 | P24 | 2026-03 | 代碼完成，**待 tag** |
| v2.12.0 | 2.12.0 | P25 | 2026-03 | 代碼完成，**待 pytest + tag** |
| demo1-v0.1.0 | 0.1.0 | D1 | — | TSMC Demo-1（NL→BIM→Cost→4D） |
| demo2-v0.2.0 | 0.2.0 | D2 | — | TSMC Demo-2（USD→Omniverse→Revit→建照） |
| v3.0.0 | 3.0.0 | P29 | — | Qt Quick 3D + QML 原生 GUI |

---

## 2. 治理文件

| 文件 | 版本 | 維護者 |
|------|------|--------|
| CLAUDE.md | **v1.23.3** | 人工 |
| SKILL.md | **v4.0** | 人工 |
| PROJECT.md | **v1.4** | Claude Code + 人工 |

---

## 3. 架構決策記錄 (ADR)

### ADR-001: GUI 遷移至 Qt Quick 3D + QML (2026-03-27)

| 項目 | 決策 |
|------|------|
| **狀態** | ✅ 已確認 |
| **背景** | PySide6 記憶體問題 (ISSUE-004, 16GB OOM)；Qt3D 已在 Qt 6.8 deprecated |
| **決策** | 採用 Qt Quick 3D + QML 取代 PySide6 + PyVista |
| **理由** | Qt 官方主推、內建 RHI (Vulkan/Metal/D3D12)、PBR 材質、代碼量減 50%、動畫系統整合 |
| **風險** | 需學 QML；大量 BIM 元素效能未驗證 |
| **替代方案** | Qt3D (✘ deprecated)、QRhi 自建 (✘ 工程量太大)、保持 PyVista (✘ 記憶體) |
| **執行時機** | Demo-1 + Demo-2 完成後 (Phase 1, P26-P29) |

### 技術架構變更

```
現有 (Demo 期間保持)          目標 (P26-P29)
────────────────────          ───────────────
├─ PySide6 GUI (Python)      → Qt Quick (QML + C++)
├─ PyVista 3D (Python)       → Qt Quick 3D (QML)
├─ matplotlib charts         → QML Charts / Canvas
├─ pytest-qt                 → Qt Test + QML TestCase
├─ Python 直接嵌入 GUI        → QProcess + JSON stdio
└─ AI Agents (Python)        → AI Agents (Python, 不變)
```

### QProcess + JSON stdio 架構

```
Qt Quick 3D GUI (主進程, C++/QML)
    │  QProcess::start("python3 agents/agent_runner.py")
    │  stdin  ← JSON {"action":"enhance","prompt":"..."}
    │  stdout → JSON {"type":"delta","text":"..."}
    │  stderr → 錯誤日誌
    ▼
Python AI Agent Runner (子進程)
    │  asyncio.StreamReader 讀 stdin
    │  Claude API (AsyncAnthropic)
    │  JSON streaming 輸出
    └─ heartbeat 每 10s
```

---

## 4. 開發路線圖

### Phase 0: Demo 展示 (Week 0-10)

| Sprint | 週數 | Tasks | 目標 | 版本 | 狀態 |
|--------|:----:|:-----:|------|------|:----:|
| **W0 收尾** | 0.5 | 5 | P24/P25 pytest + tag | v2.11+v2.12 | ✅ |
| **D1-S1 引擎** | 2 | 15 | AI場景+Cost+4D+MEP | demo1-alpha | ✅ |
| **D1-S2 GUI+展示** | 2 | 14 | GUI整合+場景+TSMC展示 | demo1-v0.1.0 | ✅ |
| **D2 Omniverse** | 5 | 35 | USD→Omni→Revit→建照 | demo2-v0.2.0 | ⬜ |

### Phase 1: Qt Quick 3D 遷移 (Week 11-18, P26-P29)

| Sprint | 週數 | 目標 | 版本 |
|--------|:----:|------|------|
| **P26 AgentBridge** | 1 | QProcess+JSON stdio + agent_runner.py | v2.13.0 |
| **P27 QML GUI** | 2 | ApplicationWindow + ChatPanel + QML 基礎 | v2.14.0 |
| **P28 Quick 3D** | 2 | Qt Quick 3D 取代 PyVista + BIM 渲染 | v2.15.0 |
| **P29 清理** | 1 | 移除 PySide6/PyVista + 測試遷移 | v3.0.0 |

#### P26: AgentBridge (風險最低，價值最高)
- AgentBridge.h/cpp: QProcess + JSON stdio
- agents/agent_runner.py: asyncio stdin reader + Claude streaming
- heartbeat + timeout 機制
- Qt Test: ping/pong < 5s

#### P27: QML GUI 骨架
- main.qml: ApplicationWindow + SplitView
- ChatPanel.qml: 輸入 + streaming 顯示
- LandView2D.qml: Canvas 地籍圖
- AgentBridge 透過 Q_PROPERTY/Q_INVOKABLE 暴露給 QML

#### P28: Qt Quick 3D
- View3D + PerspectiveCamera + OrbitCameraController
- BIM 幾何體: Model + PrincipledMaterial (PBR)
- USD → Qt Quick 3D 橋接 (QQuick3DGeometry C++)
- 實體選取 + 高亮 (PickHandler)
- 4D 動畫: NumberAnimation on visible/opacity/position

#### P29: 清理 + 測試遷移
- 移除 PySide6/PyVista/pyvistaqt/pytest-qt
- 820 個 pytest → ~150 個 AI Agent 測試 (tests/python_ai/)
- Qt Test + QML TestCase (tests/cpp/)
- 記憶體基線: 啟動 < 500MB

### Phase 2: 平台擴展 (Week 19-26, P30-P33)

| Sprint | 目標 |
|--------|------|
| P30 | Windows 平台 + USD↔Revit |
| P31 | ILOS Plugin 整合 |
| P32 | Omniverse 深化 |
| P33 | 認證 + 安全 |

### Phase 3: 雲端 + 行動 (Week 27-34, P34-P41)

| Sprint | 目標 |
|--------|------|
| P34-P37 | Web 版 (React/WebGPU) |
| P38-P41 | Mobile (iPad/Vision Pro) |

### Phase 4: 私有 LLM (Week 35+, P42-P44)

| Sprint | 目標 |
|--------|------|
| P42-P44 | 零外部 AI API，完全 on-premise |

---

## 5. TSMC Demo-1 Sprint 計劃 (34T, 4.5 週)

### 工時與 Token 估算

| Sprint | 週數 | Tasks | 新建 | 強化 | Tokens |
|--------|:----:|:-----:|:----:|:----:|:------:|
| W0 收尾 | 0.5 | 5 | 0 | 5 | ~30K |
| D1-S1 引擎 | 2 | 15 | 4 | 11 | ~150K |
| D1-S2 GUI | 2 | 14 | 3 | 11 | ~120K |
| **合計** | **4.5** | **34** | **7** | **27** | **~300K** |

(詳細 Task 清單見下方 Sprint 進度區段)

---

## 6. 當前 Sprint 進度

### W0: POC 收尾

| ID | 說明 | 狀態 |
|----|------|:----:|
| W0-T1 | P24 conftest.py offscreen | ⬜ |
| W0-T2 | P24 pytest + tag v2.11.0 | ⬜ |
| W0-T3 | P25 pytest 驗證 | ⬜ |
| W0-T4 | P25 tag v2.12.0 | ⬜ |
| W0-T5 | Win RTX 4090 環境 | ⬜ |

### D1-S1: 引擎強化

| ID | 說明 | 狀態 |
|----|------|:----:|
| D1-S1-PA-T1 | Planner 6 場景 | ⬜ |
| D1-S1-PA-T2 | Modifier 累加變更 | ⬜ |
| D1-S1-PA-T3 | Orchestrator Cost+Schedule+4D | ⬜ |
| D1-S1-PA-T4 | USD phase+MEP tag | ⬜ |
| D1-S1-PA-T5 | BIM 轉換 converter.py | ⬜ |
| D1-S1-PB-T6 | 零件庫 3分類 100+ | ⬜ |
| D1-S1-PB-T7 | 零件搜尋+替代 | ⬜ |
| D1-S1-PB-T8 | Cost 供應商+圖表 | ⬜ |
| D1-S1-PB-T9 | 零件替換→成本 | ⬜ |
| D1-S1-PB-T10 | 成本差異報告 | ⬜ |
| D1-S1-PC-T11 | 4D 開挖+架設 | ⬜ |
| D1-S1-PC-T12 | 4D 施工機械 | ⬜ |
| D1-S1-PC-T13 | 4D 變更連動 | ⬜ |
| D1-S1-PC-T14 | MEP 電力+HVAC+穿孔 | ⬜ |
| D1-S1-PC-T15 | 工期差異+甘特圖 | ⬜ |

### D1-S2: GUI + 展示

| ID | 說明 | 狀態 |
|----|------|:----:|
| D1-S2-PA-T1 | Win RTX 4090 GPU | ⬜ |
| D1-S2-PA-T2 | GUI 一氣呵成 | ⬜ |
| D1-S2-PA-T3 | 3D 樓層+零件+MEP | ⬜ |
| D1-S2-PA-T4 | 4D 甘特↔4D | ⬜ |
| D1-S2-PA-T5 | 變更對照面板 | ⬜ |
| D1-S2-PB-T6 | 場景 S1 別墅 | ⬜ |
| D1-S2-PB-T7 | 場景 S2 廠房 | ⬜ |
| D1-S2-PB-T8 | 場景 S3 數據中心 | ⬜ |
| D1-S2-PB-T9 | 零件庫 GUI | ⬜ |
| D1-S2-PC-T10 | 3場景 E2E | ⬜ |
| D1-S2-PC-T11 | 效能 <3min | ⬜ |
| D1-S2-PC-T12 | Demo 腳本 | ⬜ |
| D1-S2-PC-T13 | TSMC 簡報 | ⬜ |
| D1-S2-PC-T14 | 審計+tag | ⬜ |

---

## 7. 合作夥伴

| 模組 | 狀態 | Plan B |
|------|:----:|--------|
| ILOS Layout Engine | ⬜ P34+ | simulation/ 簡化版 |
| ILOS Piping Router | ⬜ P34+ | mep/pathfinder.py (A*) |

---

## 8. 已知問題

| ID | 問題 | 嚴重度 | 計劃 |
|----|------|:------:|------|
| ISSUE-001 | P24 pytest OOM | 🔴 | W0 分目錄 pytest |
| ISSUE-002 | API Timeout 30s | 🟡 | .env 120s |
| ISSUE-004 | PySide6 記憶體 | 🔴 | P29 Qt Quick 3D 取代 |

---

## 9. 里程碑時間線

```
2026 Q2:
  Week 0     W0 收尾              → v2.11+v2.12
  Week 1-2   D1-S1 引擎強化       → demo1-alpha
  Week 3-4   D1-S2 GUI+展示       → demo1-v0.1.0
             ★ TSMC Demo-1
  Week 5-10  D2 Omniverse+Revit    → demo2-v0.2.0
             ★ TSMC Demo-2 → LOI?

2026 Q3:
  Week 11    P26 AgentBridge       → v2.13.0
  Week 12-13 P27 QML GUI           → v2.14.0
  Week 14-15 P28 Qt Quick 3D       → v2.15.0
  Week 16    P29 清理+測試遷移    → v3.0.0 🌟

2026 Q4:
  Week 19-26 P30-P33 Windows+ILOS  → v3.x

2027 Q1:
  P34-P41 Web + Mobile             → v4.x

2027 Q2:
  P42-P44 私有 LLM                 → v5.0
```

---

## 10. 命名規則

| 類型 | 格式 | 範例 |
|------|------|------|
| Demo Task | `D{N}-S{X}-P{Y}-T{Z}` | D1-S1-PA-T4 |
| Sprint Task | `P{XX}-P{Y}-T{Z}` | P26-PA-T1 |
| Git Tag | `demo{N}-v{M}.{m}.{p}` | demo1-v0.1.0 |
| Commit | `[D1-S1] feat: ...` | [D1-S1] feat: 6-scene planner |
| PROMPT | `PROMPT_D1-S{X}.md` | PROMPT_D1-S1.md |

---

## 11. 變更日誌

| 版本 | 日期 | 變更 |
|------|------|------|
| v1.0 | 2026-03-27 | 初始建立 |
| v1.1 | 2026-03-27 | +治理草稿 |
| v1.2 | 2026-03-27 | 三大鐵律 |
| v1.3 | 2026-03-27 | Demo-1 Sprint 計劃 (CHANGELOG 審計) |
| **v1.4** | **2026-03-27** | **ADR-001: Qt Quick 3D + QML 架構決策。完整開發路線圖 Phase 0-4。P26-P29 拆分為 4 個獨立 Sprint (AgentBridge → QML GUI → Quick 3D → 清理)。Qt3D deprecated → Qt Quick 3D。** |

---

*PROJECT.md v1.4 | Zigma PromptToBuild | 2026-03-27*
