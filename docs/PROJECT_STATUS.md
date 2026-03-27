# PromptBIM 專案狀態報告

> **更新:** 2026-03-27 21:45 CST | **報告人:** Claude (claude-sonnet-4-6)
> **Repo:** chchlin1018/PromptBIMTestApp1 (private, main branch)

---

## 1. 版本狀態

| 項目 | 狀態 |
|------|------|
| 當前版本 | **v2.12.0** (W0 Sprint 完成) |
| P24 版本 | v2.11.0 ✅ **已 tag** (2026-03-27 W0 Sprint) |
| P25 版本 | v2.12.0 ✅ **已 tag** (2026-03-27 W0 Sprint，tag 已存在) |
| CLAUDE.md | **v1.23.3** |
| SKILL.md | **v3.8** (13071B — 低於 20000B 閾值，需調查) |
| PROMPT_W0.md | **v2 — ✅ 已完成執行** |
| PROMPT_P26.md | **⬜ 待建立** |

---

## 2. Sprint 進度

| Sprint | 版本 | 狀態 | 說明 |
|--------|------|------|------|
| P0~P23 | v0.1.0~v2.10.0 | ✅ 完成 | 全部已 tag |
| **P24** | v2.11.0 | **✅ 完成** | pytest 驗證 ✅ + tag v2.11.0 ✅ (W0 Sprint 2026-03-27) |
| **P25** | v2.12.0 | **✅ 完成** | pytest 驗證 ✅ + tag v2.12.0 ✅ (W0 Sprint 2026-03-27) |
| **W0** | — | **✅ 完成** | POC 收尾：pytest OOM 診斷 + P24/P25 tag |
| **P26** | — | **🔜 待規劃** | W0 完成後建立 |

### P25 執行結果 — 2026-03-27

| Part | Commit | Tasks | 說明 | 狀態 |
|------|--------|-------|------|------|
| A | `acda37c` | 1-6 | Performance + Benchmarks | ✅ |
| B | `4b0f924` | 7-12 | Windows Platform Support | ✅ |
| C | `c1ce70f` | 13-18 | Documentation + API | ✅ |

**P25 完成摘要 (W0 Sprint 2026-03-27)：**
- ✅ pytest 驗證（核心目錄全 PASS）
- ✅ git tag v2.12.0 pushed
- ⬜ Sprint25_AuditReport.md (待後續)
- ⬜ PROMPT_P26.md (待後續)
- ⬜ 版本一致性確認（pyproject.toml / __init__.py / CHANGELOG）

### Sprint W0 執行結果 — 2026-03-27 21:45

- **狀態:** ✅ 完成
- **版本:** v2.12.0
- **Tasks:** 5/5
- **記憶體:** 6.7/16.0GB(free:9.2GB)
- **pytest 結果:**
  - ✅ test_land (103), test_bim (279), test_codes (44), test_integration (58)
  - ✅ test_agents (100, 2 deselect), test_cache/demo/plugins/schemas/startup/viz/voice/web (154)
  - ❌ test_cli (6 timeout >10s — subprocess issue, 非 OOM)
  - ❌ test_p0_skeleton (2 stale version: 2.6.0 vs 2.10.0)
  - ⚠️ test_orchestrator::TestOrchestratorConstraintDedup (2 skip — missing builder mock)
- **OOM 根因:** conftest.py offscreen 已在位，前次 OOM 根因已解決
- **已知問題:** test_cli subprocess timeout、test_p0 stale version 需後續 sprint 修復

---

## 3. 治理框架

| 文件 | 版本 | 核心規則 |
|------|------|----------|
| CLAUDE.md | **v1.22.0** | 28 步流程 + PROJECT_STATUS 追蹤 + 通知多行格式 |
| SKILL.md | **v3.8** | 同步 v1.22.0 + P24e pytest 根因 |

### 歷史教訓

| # | 事故 | 規則 |
|---|------|------|
| 🔴 P18 | 文件截斷 | 禁止修改治理文件 |
| 🔴 P22 | notify 遺失 | PROMPT 顯式定義函數 |
| 🔴 P22.1 | 未 commit | Part 結束 commit+push |
| 🔴 P24a | OOM | check_mem + <1GB 暫停 |
| 🔴 P24b | 殭屍 Python | pkill + offscreen |
| 🔴 P24d | Task 通知跳過 | task_start/task_done |
| 🔴 P24e | pytest 反覆 OOM | conftest.py + 禁止多 pytest + ignore e2e |
| 🟧 P24c | Git 遠端分歧 | Sprint 前 git pull |

---

## 4. Windows 遷移架構

| 項目 | 決策 |
|------|------|
| 方案 | Hydra Storm + PyVista hybrid |
| 路線圖 | P24-P29 (macOS) → P30-P31 (Windows) → P32-P33 (Hydra Storm v3.0) |

---

*docs/PROJECT_STATUS.md | 2026-03-27*

---

## D1-S2 Sprint 執行結果 — 2026-03-27

### Sprint D1-S2 執行結果 — 2026-03-27 23:15

- **狀態:** ✅ 完成
- **版本:** demo1-v0.1.0
- **Tasks:** 14/14
- **Parts:** 3/3
- **記憶體:** ~8GB used / 16GB(free:~8GB)
- **pytest:** 60/60 PASS (test_demo/ all green)
- **錯誤:** 無

### 新增檔案 (D1-S2)

| 檔案 | 說明 |
|------|------|
| `src/promptbim/gpu_render.py` | GPU 能力偵測 + RTX4090 preset |
| `src/promptbim/gui/workflow_controller.py` | Prompt→3D→Cost→4D 自動流程控制 |
| `src/promptbim/gui/delta_panel.py` | 變更對照面板 (3D+Cost+Schedule) |
| `src/promptbim/gui/asset_browser.py` | 零件庫 GUI (24 assets, 3 categories) |
| `src/promptbim/demo/scene_templates.py` | S1 Villa+Pool / S2 Fab / S3 DC 場景模板 |
| `src/promptbim/codes/tw_industrial_code.py` | 台灣工業廠房法規檢核 (TW-IND-001~004) |
| `src/promptbim/bim/export.py` | Demo-1 匯出 (JSON/CSV) |
| `tests/test_demo/test_d1_s2_scenes.py` | 28 E2E 測試 (3 scenes + GPU + assets) |
| `tests/test_demo/test_d1_performance.py` | 19 效能測試 (pipeline < 60s) |
| `docs/DEMO_SCRIPT_D1.md` | 7分鐘 Demo 腳本 (TSMC版) |
| `docs/TSMC_Presentation_D1.md` | 10頁 TSMC 簡報 |

### 修改檔案 (D1-S2)

| 檔案 | 變更 |
|------|------|
| `gui/main_window.py` | WorkflowController + DeltaPanel + ProgressBar 整合 |
| `gui/model_view.py` | Component pick + MEP layer filter + sidebar |
| `gui/simulation_tab.py` | Speed control + Gantt→4D click link |
| `viz/gantt_chart.py` | day_clicked Signal + mpl click handler |

### D1-S2 成果摘要

- ✅ GUI: Prompt→3D→Cost→4D 一氣呵成 (WorkflowController + ProgressBar)
- ✅ 3D: 樓層切換 + 零件點選 + MEP 8層分層顯示
- ✅ 4D: Gantt 點擊跳轉 + 1×/2×/5×/10× 播放速度
- ✅ Delta: 3D+Cost+Schedule 變更對照面板
- ✅ S1 Villa+Pool: 1200m² | 4 stories | BCR=45%
- ✅ S2 TSMC Fab: 9600m² | 4 stories | 無塵室 54.5% PASS
- ✅ S3 Data Center: 4800m² | 5 stories | TIA-942 PASS
- ✅ 零件庫 GUI: 24 assets / 3 categories / keyword search
- ✅ 台灣工業法規: TW-IND-001~004 全 PASS
- ✅ 60 tests PASS | 0.89s | 全流程 < 60s headless

