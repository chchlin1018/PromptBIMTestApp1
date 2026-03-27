# Zigma PromptToBuild 專案管理

> **版本:** v1.3 | **最後更新:** 2026-03-27
> **專案:** Zigma PromptToBuild (PromptBIMTestApp1)
> **組織:** Reality Matrix Inc.
> **倉庫:** github.com/chchlin1018/PromptBIMTestApp1

---

## 1. 版本控制

| 標籤 | 版本 | Sprint/Demo | 日期 | 說明 |
|------|------|------------|------|------|
| v2.10.0 | 2.10.0 | P23 | 2026-03 | 審計修復（最後成功 tag） |
| v2.11.0 | 2.11.0 | P24 | 2026-03 | 代碼完成，**待 tag**（pytest OOM） |
| v2.12.0 | 2.12.0 | P25 | 2026-03 | 代碼完成，**待 pytest + tag** |
| demo1-v0.1.0 | 0.1.0 | D1 | — | TSMC Demo-1（NL→BIM→Cost→4D） |
| demo2-v0.2.0 | 0.2.0 | D2 | — | TSMC Demo-2（USD→Omniverse→Revit→建照） |

---

## 2. 治理文件同步狀態

| 文件 | 版本 | 維護者 |
|------|------|--------|
| CLAUDE.md | **v1.23.1** | 人工 |
| SKILL.md | **v4.0** | 人工 |
| PROJECT.md | **v1.3** | Claude Code + 人工 |

---

## 3. TSMC Demo-1 需求（v1.2 確認版）

### Mandatory

| # | 需求 | 現有模組 | 狀態 |
|---|------|--------|:----:|
| M1 | Prompt → AI 語意 → BIM | agents/planner.py (14KB) + enhancer.py | ✅ 強化 |
| M2 | 3D BIM (RTX 4090 OpenGL) | viz/model_3d.py + gui/model_view.py | ✅ 強化 |
| M3 | Cost + Schedule + 變更 | bim/cost/ (P6) + bim/simulation/ (P8) | ✅ 強化 |
| M4 | 即時變更（泳池→停車場） | agents/modifier.py (17KB, P4.8) | ✅ 強化 |
| M5 | 4D 建造模擬 + 施工機械 | bim/simulation/ + gui/simulation_tab.py (P8) | 🟡 擴充 |
| M6 | 供應商零件庫 3 分類 | bim/components/ (76件, P2.5) | 🟡 擴充 |
| M7 | MEP 管路+衝突+穿孔 | bim/mep/ (A*, 4系統, P7) | 🟡 擴充 |

### Nice to Have

| N1 | 語音輸入 | voice/stt.py (Whisper, P5) | ✅ 已有 |

---

## 4. Sprint 計劃（Demo-1，34 Tasks，4.5 週）

### 工時與 Token 估算

| Sprint | 週數 | Tasks | 新建 | 強化 | 預估 Tokens |
|--------|:----:|:-----:|:----:|:----:|:-----------:|
| W0 收尾 | 0.5 | 5 | 0 | 5 | ~30K |
| D1-S1 引擎強化 | 2 | 15 | 4 | 11 | ~150K |
| D1-S2 GUI+展示 | 2 | 14 | 3 | 11 | ~120K |
| **合計** | **4.5** | **34** | **7** | **27** | **~300K** |

---

### W0: POC 收尾（2-3 天，5T，~30K tokens）

| ID | 說明 | 檔案 | 狀態 |
|----|------|------|:----:|
| W0-T1 | P24 conftest.py offscreen 修復 | tests/conftest.py | ⬜ |
| W0-T2 | P24 pytest pass + tag v2.11.0 | git tag | ⬜ |
| W0-T3 | P25 pytest 驗證 | tests/ | ⬜ |
| W0-T4 | P25 tag v2.12.0 | git tag | ⬜ |
| W0-T5 | Win RTX 4090 conda + PyVista OpenGL 確認 | 新環境 | ⬜ |

---

### D1-S1: 引擎強化（Week 1-2，15T，~150K tokens）

#### Part A: AI + 場景 + 變更（5T，~50K）

| ID | 說明 | 現有檔案 | 操作 | 狀態 |
|----|------|---------|------|:----:|
| D1-S1-PA-T1 | Planner 6 場景 prompt template | agents/planner.py | 加 6 template | ⬜ |
| D1-S1-PA-T2 | Modifier 累加變更邏輯強化 | agents/modifier.py | 強化多輪 | ⬜ |
| D1-S1-PA-T3 | Orchestrator 串接 Cost+Schedule+4D | agents/orchestrator.py | 擴充流程 | ⬜ |
| D1-S1-PA-T4 | USD phase tag + MEP layer 加入 | bim/usd_generator.py | 加欄位 | ⬜ |
| D1-S1-PA-T5 | 現成 BIM 轉換: IFC/FBX→USD 管線 | bim/ 新增 converter.py | **新建** | ⬜ |

#### Part B: 成本 + 零件庫擴充（5T，~50K）

| ID | 說明 | 現有檔案 | 操作 | 狀態 |
|----|------|---------|------|:----:|
| D1-S1-PB-T6 | 零件庫擴充: 家用+建築+工廠 100+ | bim/components/ (76件) | 擴充 JSON | ⬜ |
| D1-S1-PB-T7 | 零件庫搜尋+替代+競合 API | bim/components/registry.py | 加方法 | ⬜ |
| D1-S1-PB-T8 | Cost Engine: 供應商明細+圖表升級 | bim/cost/estimator.py + cost_charts.py | 強化 | ⬜ |
| D1-S1-PB-T9 | 零件替換→成本即時重算 | bim/cost/ + bim/components/ | 加 swap | ⬜ |
| D1-S1-PB-T10 | 變更成本差異報告（前後對照） | bim/cost/ 新增 cost_delta.py | **新建** | ⬜ |

#### Part C: 4D + MEP 擴充（5T，~50K）

| ID | 說明 | 現有檔案 | 操作 | 狀態 |
|----|------|---------|------|:----:|
| D1-S1-PC-T11 | 4D 擴充: 地下開挖+鋼梁架設動畫 | bim/simulation/animator.py | 加動畫類型 | ⬜ |
| D1-S1-PC-T12 | 4D 施工機械 3D 資產+進場邏輯 | assets/ 新增 + simulation/ | **新建** | ⬜ |
| D1-S1-PC-T13 | 4D 變更連動: 設計變更→4D 自動更新 | bim/simulation/scheduler.py | 加 rebuild | ⬜ |
| D1-S1-PC-T14 | MEP 擴充: 電力+HVAC 路由+穿孔 | bim/mep/planner.py + systems.py | 強化 | ⬜ |
| D1-S1-PC-T15 | 變更工期差異+甘特圖對照 | bim/simulation/ 新增 schedule_delta.py | **新建** | ⬜ |

---

### D1-S2: GUI + 多場景 + 展示（Week 3-4，14T，~120K tokens）

#### Part A: GUI 面板升級（5T，~50K）

| ID | 說明 | 現有檔案 | 操作 | 狀態 |
|----|------|---------|------|:----:|
| D1-S2-PA-T1 | Win RTX 4090 部署 + GPU 渲染確認 | viz/ | 環境 | ⬜ |
| D1-S2-PA-T2 | GUI 一氣呵成: Prompt→3D→Cost→4D | gui/main_window.py | 串接 | ⬜ |
| D1-S2-PA-T3 | 3D: 樓層切換+點擊零件+MEP分層 | gui/model_view.py + mep_toggle.py | 強化 | ⬜ |
| D1-S2-PA-T4 | 4D Player: 甘特圖↔4D 聯動 | gui/simulation_tab.py | 強化 | ⬜ |
| D1-S2-PA-T5 | 變更對照面板: 3D+Cost+Schedule+4D | gui/ 新增 delta_panel.py | **新建** | ⬜ |

#### Part B: 場景 + 零件庫 GUI（4T，~35K）

| ID | 說明 | 現有檔案 | 操作 | 狀態 |
|----|------|---------|------|:----:|
| D1-S2-PB-T6 | 場景 S1: 3層別墅+泳池 | bim/templates/ | 新 template | ⬜ |
| D1-S2-PB-T7 | 場景 S2: 半導體廠房 | bim/templates/ | 新 template | ⬜ |
| D1-S2-PB-T8 | 場景 S3: 數據中心 | bim/templates/ | 新 template | ⬜ |
| D1-S2-PB-T9 | 零件庫 GUI: 3 分類瀏覽+替換 | gui/ 新增 asset_browser.py | **新建** | ⬜ |

#### Part C: 展示準備（5T，~35K）

| ID | 說明 | 檔案 | 狀態 |
|----|------|------|:----:|
| D1-S2-PC-T10 | 3 場景 E2E 測試（S1-S3 必過） | tests/ 新增 | ⬜ |
| D1-S2-PC-T11 | 效能: 全流程 < 3 分鐘 | 全系統 | ⬜ |
| D1-S2-PC-T12 | Demo 腳本 7min + 排練 | docs/DEMO_SCRIPT.md | ⬜ |
| D1-S2-PC-T13 | TSMC 簡報 10 頁 + 螢幕錄影 | — | ⬜ |
| D1-S2-PC-T14 | Demo-1 審計 + PROJECT.md + tag | docs/ + git | ⬜ |

---

## 5. 現有模組 vs Demo-1 對照（基於 CHANGELOG 審計）

### 完整存在（直接複用，不改或微調）

| 模組 | Sprint | 檔案 | 大小 |
|------|--------|------|------|
| Enhancer Agent | P2 | agents/enhancer.py | 5KB |
| Builder Agent | P2 | agents/builder.py | 4KB |
| Checker Agent | P4.5 | agents/checker.py | 9KB |
| Land Reader Agent | P9 | agents/land_reader.py | 8KB |
| Rate Limiter | P17 | agents/rate_limiter.py | 2KB |
| IFC Generator | P2+P20 | bim/ifc_generator.py + C++ | 11KB+C++ |
| USD Generator | P4+P20 | bim/usd_generator.py + C++ | 9KB+C++ |
| Geometry | P2 | bim/geometry.py | 8KB |
| Structural | P24 | bim/structural.py | 4KB |
| Materials | P24 | bim/materials.py | 3KB |
| Parking | P24 | bim/parking.py | 4KB |
| Vertical | P24 | bim/vertical.py | 5KB |
| Land Parsers | P1+P9+P13 | land/parsers/ (5 parsers) | 全 |
| Taiwan Code Engine | P4.5+P18 | codes/ (15 rules) + C++ | 全+C++ |
| Voice STT | P5 | voice/stt.py | Whisper |
| GUI MainWindow | P6 | gui/main_window.py | PySide6 |
| GUI ChatPanel | P4 | gui/chat_panel.py | 有 |
| GUI ModelView | P3 | gui/model_view.py | PyVista |
| Omniverse | P10 | bim/omniverse.py | 8KB |
| Debug | P10.2 | debug.py | 全 |
| Health Check | P10.3 | startup/ | 全 |
| Cache | P17 | cache/ | 全 |
| Schemas | P0+ | schemas/ | 全 |

### 需要強化（已有基礎，加功能）

| 模組 | Sprint | 現有 | Demo-1 要加什麼 |
|------|--------|------|----------------|
| Planner | P2 | 通用建築 prompt | +6 場景 template |
| Modifier | P4.8 | 單次修改+undo | +多輪累加+差異報告 |
| Orchestrator | P4 | Enhance→Plan→Build→Check | +Cost→Schedule→4D 串接 |
| Cost Engine | P6 | QTO+22 單價+estimator | +供應商明細+替換+差異 |
| 4D Simulation | P8 | 16-phase+scheduler+GIF | +開挖/架設動畫+機械 |
| MEP | P7 | A*+4系統+clash | +電力路由+穿孔 |
| Components | P2.5 | 76 件+registry | +100 件+3 分類+替換 |
| Simulation Tab | P8 | timeline+play+gantt | +甘特↔4D 聯動 |
| Cost Panel | P6 | pie/bar+detail | +供應商+替換 |
| Model View | P3 | floor切換+section | +點擊零件+MEP 分層 |

### 真正新建（7 個檔案）

| 新檔案 | 用途 |
|--------|------|
| bim/converter.py | IFC/FBX/glTF → USD 轉換 |
| bim/cost/cost_delta.py | 變更成本差異報告 |
| bim/simulation/schedule_delta.py | 變更工期差異 |
| gui/delta_panel.py | 變更對照面板 |
| gui/asset_browser.py | 零件庫 GUI 瀏覽器 |
| assets/equipment/ | 施工機械 3D 資產 |
| bim/templates/villa.py + fab.py + datacenter.py | 場景模板 |

---

## 6. Demo-2 計劃（不變）

Demo-2（USD→Omniverse→Revit→建照）維持 v1.0 計劃，35T，Week 5-10。
注意: bim/omniverse.py (P10) 已有 Nucleus connector 骨架。

---

## 7. 合作夥伴狀態

| 模組 | 狀態 | Plan B |
|------|:----:|--------|
| ILOS Layout Engine | ⬜ 未到（P34+） | 現有 simulation/ 簡化版 |
| ILOS Piping Router | ⬜ 未到（P34+） | 現有 mep/pathfinder.py (A*) |

---

## 8. 已知問題

| ID | 問題 | 嚴重度 | 計劃 |
|----|------|:------:|------|
| ISSUE-001 | P24 pytest OOM | 🔴 | W0-T1/T2 |
| ISSUE-002 | API Timeout 30s | 🟡 | .env 120s |
| ISSUE-004 | PySide6 記憶體 | 🔴 | P29 移除 |

---

## 9. 里程碑

```
Week 0:    W0 收尾 → v2.11.0 + v2.12.0 tags
Week 1-2:  D1-S1 引擎強化 (15T)
Week 3-4:  D1-S2 GUI+展示 (14T) → demo1-v0.1.0
           ★ TSMC Demo-1 展示
Week 5-10: D2 Omniverse→Revit→建照 (35T)
           ★ TSMC Demo-2 展示 → LOI?
Week 11+:  Phase 1 (P26-P29) Plugin 架構
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
| v1.1 | 2026-03-27 | +治理草稿追蹤 |
| v1.2 | 2026-03-27 | GOV-T7/T8 完成, 三大鐵律 |
| **v1.3** | **2026-03-27** | **TSMC Demo-1 Sprint 計劃（基於 CHANGELOG 完整審計）。50T→34T 大幅精簡（Cost/4D/MEP/Modifier 已存在）。新建僅 7 檔案，其餘為強化。Token 估算 ~300K。** |

---

*PROJECT.md v1.3 | Zigma PromptToBuild | 2026-03-27*
