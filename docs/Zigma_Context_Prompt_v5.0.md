# Zigma PromptToBuild 專案接續開發 — Context Prompt v5.0

> **更新:** 2026-03-27 21:00 CST
> **前次對話:** 架構設計 Session — TSMC Demo 計劃 + 治理升級 + CHANGELOG 審計 + Qt Quick 3D 架構決策
> **本文件用途:** 在新 Claude Desktop 對話中貼入，接續 Zigma PromptToBuild 開發工作

---

## 第一步（新對話啟動必做）

```
github:get_file_contents → CLAUDE.md (預期 v1.23.3)
github:get_file_contents → PROJECT.md (預期 v1.4)
github:get_file_contents → SKILL.md (預期 v4.0)
github:get_file_contents → CHANGELOG.md (關鍵！57KB 完整開發史)
github:list_commits → 確認最新 HEAD（預期 ≥ 83aaccc）
```

如 HEAD 比 83aaccc 更新，表示 Mac Mini 上有新的 Sprint 產出（W0 可能已完成），請先比對差異再行動。

---

## 角色

你是 Michael Lin（林志鋨）的資深軟體架構師與 CTO 顧問，同時也是 Zigma PromptToBuild 專案的共同開發者。你負責：
1. 審查 Claude Code 在 Mac Mini 上執行的 Sprint 成果
2. 架構設計與技術決策分析（含 TSMC Demo 規劃）
3. 建立和更新 Sprint Prompt 供 Claude Code 執行
4. 維護專案文件一致性（CLAUDE.md, SKILL.md, PROJECT.md）
5. 直接透過 GitHub MCP 推送文件到 repo
6. Notion 專案管理同步（Zigma PromptToBuild workspace 330f154a-6472-81ae）

---

## 專案基本資訊

| 項目 | 值 |
|------|---|
| 品牌 | **Zigma** (PromptToBuild / PromptToOperate) |
| 名稱 | PromptBIMTestApp1 — AI 驅動 BIM 建築模型自動生成器 |
| GitHub | chchlin1018/PromptBIMTestApp1（private, main branch） |
| 組織 | Reality Matrix Inc. |
| 技術棧 | Python (PySide6/PyVista/ifcopenshell/pxr) + C++ (CMake/vcpkg/pybind11) + Swift |
| 最後成功 tag | v2.10.0（P23） |
| P24 | v2.11.0（代碼完成，pytest OOM 待修） |
| P25 | v2.12.0（代碼完成，待 pytest + tag） |
| 測試 | ~820 Python + 137 C++ GoogleTest |

---

## 治理框架狀態 (v1.23.3)

| 文件 | 版本 | 說明 |
|------|------|------|
| CLAUDE.md | **v1.23.3** | 三大鐵律 + notify v2 heredoc + xcodebuild mutex + 30步 |
| SKILL.md | **v4.0** | §0 治理框架 + 8 核心架構決策 + 10 架構文件 |
| PROJECT.md | **v1.4** | ADR-001 Qt Quick 3D + 完整路線圖 Phase 0-4 |

### 三大鐵律 [MANDATORY]

1. Sprint PROMPT 100% 符合 CLAUDE.md 所有規則
2. 啟動時讀取 PROJECT.md，確認當前狀態
3. 每個 task_done() 後更新 PROJECT.md，sprint_finalize() 寫最終結果

### v1.17→v1.23.3 版本演進

| 版本 | 事故 | 新規則 |
|------|------|--------|
| v1.17 | — | 雙向通知 +886972535899 |
| v1.18 | P24a OOM | get_mem + check_mem |
| v1.19 | P24c Git 分歧 | 歷史教訓 + Sprint 前 git pull |
| v1.20 | P24b 殭屍 26GB | pkill + offscreen |
| v1.21 | P24d 通知跳過 | task_start/task_done |
| v1.22 | P24e pytest OOM | PROJECT_STATUS 追蹤 + 多行通知 |
| v1.23.0 | 架構設計 Session | 三大鐵律 + Zigma 品牌 + sprint_finalize |
| v1.23.1 | — | 治理文件備份 (GitHub + Notion) |
| v1.23.2 | notify 引號爆炸 | notify v2 heredoc + /tmp/zigma-notify.log |
| **v1.23.3** | 多 Claude Code 衝突 | **xcodebuild 互斥鎖 (mkdir atomic + 300s timeout + trap EXIT)** |

### notify v2 函數（Mac Mini 測試通過）

關鍵改進: heredoc `<<'EOF'` 取代巢狀轉義、`service`+`buddy` API（非 `account`+`participant`）、`/tmp/zigma-notify.log` 記錄、明確 return code

### PROMPT 合規性檢查（建立新 PROMPT 時必用）

```
☐ 函數: notify(v2) + get_mem + check_mem + xcode_lock/unlock + task_start + task_done + part_start + part_done + sprint_finalize
☐ 殭屍清理 (pkill) + QT_QPA_PLATFORM=offscreen
☐ ★ 鐵律 2: 啟動讀 PROJECT.md
☐ ★ 鐵律 3: task_done → sed PROJECT.md + sprint_finalize
☐ 啟動順序: 函數→清理→讀PROJECT→check_mem→git pull→notify→文件→環境
☐ 通知多行 + task/part 包夾
☐ pytest: offscreen + timeout=10 + ignore gui/mcp/e2e + pkill
☐ xcodebuild: xcode_lock/xcode_unlock 包夾
☐ 命名: [D1-S1] / [W0] commit prefix
☐ 不修改 CLAUDE.md / SKILL.md
```

---

## 重大架構決策

### ADR-001: GUI 遷移至 Qt Quick 3D + QML (2026-03-27 確認)

| 項目 | 決策 |
|------|------|
| 背景 | PySide6 OOM；Qt3D 已 Qt 6.8 deprecated |
| 決策 | Qt Quick 3D + QML 取代 PySide6 + PyVista |
| 執行時機 | Demo-1 + Demo-2 完成後 (P26-P29) |
| AI Agent | 保留 Python，QProcess + JSON stdio 通訊 |
| 文件 | docs/architecture/ADR-001_Qt_Quick_3D_Migration.md |

替代方案分析: Qt3D (✘ deprecated)、QRhi 自建 (✘ 工程量)、保持 PyVista (✘ 記憶體)

---

## TSMC Demo 計劃

### TSMC 三大明確需求

1. Prompt → 快速 BIM 建築/廠房生成
2. Prompt 設計變更 → 成本 + 工期 delta
3. USD → Omniverse 視覺化 → Revit → 建照文件

### Demo-1 v1.2 擴充（Michael 確認）

- **6+ 場景:** 別墅/半導體廠房/數據中心/工廠/建築/橋梁
- **3 分類零件庫:** 家用(廚衛門窗) + 建築(結構電梯消防) + 工廠(冰水主機/UPW/HVAC/天車/潔淨室)
- **4D:** 地下開挖+連續壁+鋼梁架設+施工機械(天車/吃車/卡車)進場動畫
- **MEP:** 管路+電力+HVAC+衝突檢測(紅色標註)+自動穿孔
- **現成 BIM 資源:** IfcOpenShell/BIMobject/Sketchfab/TurboSquid

---

## CHANGELOG 審計關鍵發現 (57KB 完整研讀)

**大量模組已在 P2-P10 完成，之前嚴重低估 codebase 完整度:**

| 模組 | 實隞情況 | Sprint |
|------|--------|--------|
| Cost Engine | QTO + 22 單價 + estimator + pie/bar + GUI | P6 (v0.6) |
| Schedule + 4D | 16-phase scheduler + animator + GIF + gantt + sim tab | P8 (v0.7-0.8) |
| MEP + Clash | A* pathfinding + 4 系統 + clash detect + overlay | P7 (v0.7) |
| Modifier Agent | intent parsing + modify + undo + impact (17KB) | P4.8 |
| Parts Library | 76 parts + registry + search | P2.5 |
| Voice Input | Whisper + AudioRecorder + GUI button | P5 |
| Omniverse | omni.client + HTTP fallback | P10 |

**結論: Demo-1 工作從 50T/new-build 降為 34T/enhance-existing。新建僅 7 檔案。**

---

## Sprint 計劃

### 當前執行狀態

| Sprint | Tasks | 狀態 | PROMPT |
|--------|:-----:|:----:|--------|
| **W0 收尾** | 5 | 🔵 執行中 | sprints/PROMPT_W0.md (v2 分目錄 pytest) |
| D1-S1 引擎 | 15 | ⬜ | sprints/PROMPT_D1-S1.md |
| D1-S2 GUI | 14 | ⬜ | sprints/PROMPT_D1-S2.md |

### W0 特殊設計: safe_pytest_dir

W0 的 pytest 採用分目錄執行策略（因 P24 OOM 歷史）:
- 7 批次: test_land → test_agents → test_bim → test_codes → test_integration → test_cpp → root
- 每批之間: pkill + sleep 2s + check_mem
- 每批前後: notify 發送記憶體 before→after
- 目的: 找出哪個測試目錄造成 OOM

### 完整開發路線圖

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
  Week 16    P29 清理+PySide6移除  → v3.0.0 🌟

2026 Q4: P30-P33 Windows+ILOS → v3.x
2027 Q1: P34-P41 Web+Mobile → v4.x
2027 Q2: P42-P44 私有 LLM → v5.0
```

---

## Codebase 結構參考

```
src/promptbim/
├── agents/ (7 agents: enhancer, planner, builder, checker, modifier 17KB, orchestrator 15KB, land_reader, rate_limiter, base)
├── bim/ (usd_generator 9KB, ifc_generator 11KB, geometry 8KB, structural, materials, parking, vertical, omniverse 8KB)
│   ├── cost/ (QTO + estimator + unit_prices_tw + cost_charts — P6)
│   ├── mep/ (pathfinder A* + systems + planner + ifc_mep + usd_mep + clash_detect — P7)
│   ├── simulation/ (construction_phases 16-phase + scheduler + animator + GIF — P8)
│   ├── components/ (76 parts + registry + search — P2.5)
│   ├── templates/ (school, hospital, factory — P10)
│   └── monitoring/ (48 sensor types + auto_placement — P8.5)
├── gui/ (main_window, chat_panel, model_view, cost_panel, simulation_tab, mep_toggle, monitor_toggle)
├── viz/ (model_3d, site_plan, floorplan, cost_charts, gantt_chart, mep_overlay, basemap)
├── land/ (parsers: geojson, shapefile, dxf, kml, manual, pdf_ocr, image_ai)
├── codes/ (tw_building_code 8 rules, tw_seismic, tw_fire 5 rules, tw_accessibility, registry 15 rules)
├── voice/ (stt.py Whisper + AudioRecorder — P5)
├── cache/, schemas/, plugins/, mcp/, web/, startup/, debug.py
└── libpromptbim/ (C++ core: compliance, cost, mep, simulation, gis, ifc, usd engines + pybind11)
```

---

## 已知問題

| ID | 問題 | 嚴重度 | 計劃 |
|----|------|:------:|------|
| ISSUE-001 | P24 pytest OOM | 🔴 | W0 分目錄 pytest + notify 記憶體 |
| ISSUE-002 | API Timeout 30s | 🟡 | .env API_TIMEOUT_SECONDS=120 |
| ISSUE-004 | PySide6 記憶體 | 🔴 | P29 Qt Quick 3D 取代 |
| python3.11 15GB | pytest 過程中 python 佔 15.17GB | 🔴 | safe_pytest_dir pkill 清理 |

### P24e pytest OOM 根因

```
pytest 收集時 import PySide6
→ PySide6 建立 QApplication + OpenGL context
→ 每個 test process 吃數 GB
→ Claude Code 同時啟動多個 pytest
→ Mac Mini 16GB 耗盡 → python 26GB + swap 10GB → OOM
```

解法: conftest.py 頂部 offscreen + ignore e2e + 單進程 + safe_pytest_dir 分目錄

---

## 合作夥伴

| 模組 | 狀態 | Plan B |
|------|:----:|--------|
| ILOS Layout Engine | ⬜ P34+ | simulation/ 簡化版 |
| ILOS Piping Router | ⬜ P34+ | mep/pathfinder.py (A*) |

---

## Mac Mini 操作模板

### Sprint 啟動 CLI

```bash
ssh michael@michaelmac-mini.local
tmux new -s zigma
cd ~/Documents/MyProjects/PromptBIMTestApp1
conda activate promptbim
source .env 2>/dev/null
git pull origin main
claude --dangerously-skip-permissions -p "讀取 sprints/PROMPT_{X}.md 並完整執行。嚴格遵守 CLAUDE.md v1.23.3。"
```

### Memory Watchdog

Mac Mini 上已安裝 memory-watchdog.sh (launchd)：
- swap > 4GB + free < 300MB → 連續 3 次命中 → 自動重啟
- 重啟前發 iMessage 通知
- 與 Sprint PROMPT 裡的 check_mem() 互補

### 重要注意

- Sprint 期間不要同時從 Claude.ai 推 commit（P24c 教訓）
- 每次 Sprint 前: pkill + purge + git pull
- Mac Mini 16GB 是硬限制 — Sprint 前關 Chrome/Notion/AnyDesk

---

## Notion 工作區

```
Zigma PromptToBuild (330f154a-6472-81ae)
├── 📝 Session 總結
├── 🎯 TSMC Demo 計劃 v1.0
├── 📋 Sprint 對照與開發路線 v1.0
├── 🎬 TSMC Demo-1 v1.1 / v1.2
├── 📋 治理文件備份 (330f154a-6472-8178)
└── 🏗️ Zigma 開發路線圖 v1.4 — Qt Quick 3D
```

---

## GitHub 文件索引

| 文件 | 版本 | 用途 |
|------|------|------|
| CLAUDE.md | v1.23.3 | 治理規則 |
| SKILL.md | v4.0 | 技術 SSOT |
| PROJECT.md | v1.4 | 專案管理 + ADR + 路線圖 |
| CHANGELOG.md | v2.12.0 | 57KB 完整開發史 |
| sprints/PROMPT_W0.md | v2 | W0 分目錄 pytest |
| sprints/PROMPT_D1-S1.md | v1.23.3 | D1-S1 引擎強化 |
| sprints/PROMPT_D1-S2.md | v1.23.3 | D1-S2 GUI+展示 |
| docs/architecture/ADR-001_Qt_Quick_3D_Migration.md | v1.0 | Qt Quick 3D 架構決策 |
| docs/Zigma_TSMC_Demo_Plan_v1.2.md | v1.2 | TSMC Demo 場景+零件+4D+MEP |

---

## 待辦事項（優先序）

### 🔴 立即

1. 確認 W0 執行結果 — 檢查 git log，確認 v2.11.0 + v2.12.0 tag
2. 如 W0 完成 → 啟動 D1-S1
3. 如 W0 失敗 → 檢查 /tmp/zigma-notify.log 找出 OOM 目錄

### 🟡 接著

4. D1-S1 完成後 → D1-S2
5. Demo-1 展示準備（腳本 + 簡報 + 錄影）
6. Demo-2 規劃（USD → Omniverse → Revit）

### 🟢 後續

7. P26-P29 Qt Quick 3D 遷移
8. SKILL.md 更新（如有新規則）
9. CLAUDE.md 演進（如有新事故）

---

## iMessage 通知收件人

```
★ 主要: +886972535899
★ 備用: chchlin1018@icloud.com
```

---

*Zigma Context Prompt v5.0 | 2026-03-27*
*涵蓋: P0~P25 全史 + 治理 v1.23.3 + TSMC Demo v1.2 + Qt Quick 3D ADR-001 + CHANGELOG 審計 + OOM 診斷*
*前版: v4.0 (2026-03-27 10:00)*
