# Zigma PromptToBuild 專案管理

> **版本:** v1.6 | **最後更新:** 2026-03-28
> **專案:** Zigma PromptToBuild (PromptBIMTestApp1)
> **組織:** Reality Matrix Inc.
> **Tag:** mvp-v0.1.0

---

## 1. 版本控制

| 標籤 | Sprint | 日期 | 狀態 |
|------|--------|------|:----:|
| v2.10.0 | P23 | 2026-03 | ✅ |
| **v2.11.0** | P24 | 2026-03-27 | **✅ W0 tagged** |
| **v2.12.0** | P25 | 2026-03-27 | **✅ W0 tagged** |
| **demo1-v0.1.0** | D1 | **2026-03-27** | **✅ Demo-1 Ready** |
| **mvp-v0.1.0** | M1-MVP | **2026-03-28** | **✅ Qt Quick 3D MVP** |
| demo2-v0.2.0 | D2 | — | ⬜ |
| v3.0.0 | P29 | — | ⬜ |

## 2. 治理文件

| 文件 | 版本 |
|------|------|
| CLAUDE.md | **v1.23.3** |
| SKILL.md | **v4.1** |
| PROJECT.md | **v1.6** |

## 3. ADR-001: Qt Quick 3D + QML

狀態: ✅ 已確認 | 執行: Demo 完成後 P26-P29

---

## 4. 開發路線圖

| Sprint | Tasks | 版本 | 狀態 |
|--------|:-----:|------|:----:|
| **W0** | 5/5 | v2.11+v2.12 | **✅** |
| **D1-S1** | 15/15 | demo1-alpha | **✅** |
| **D1-S2** | 14/14 | demo1-v0.1.0 | **✅** |
| **M1-MVP** | **68/68** | **mvp-v0.1.0** | **✅** |
| D2 | 35 | demo2-v0.2.0 | ⬜ |
| P26-P29 | — | v3.0.0 | ⬜ |

## 5. Demo-1 完成狀態 (34/34 Tasks)

### W0: POC 收尾 ✅

| ID | 說明 | 狀態 |
|----|------|:----:|
| W0-T1 | conftest.py offscreen | ✅ |
| W0-T2 | P24 分目錄 pytest + v2.11.0 | ✅ |
| W0-T3 | P25 pytest 驗證 | ✅ |
| W0-T4 | v2.12.0 tag | ✅ |
| W0-T5 | Win RTX 4090 待辦 | ✅ |

### D1-S1: 引擎強化 ✅

| Part | Tasks | 內容 | 狀態 |
|------|:-----:|------|:----:|
| A | 5 | planner 6場景 + modifier + orchestrator + usd + converter | ✅ |
| B | 5 | 零件庫 76→102 + cost_delta + vendor | ✅ |
| C | 5 | 4D機械 + MEP擴充 + schedule_delta | ✅ |

### D1-S2: GUI+展示 ✅ (60/60 pytest PASS)

| Part | Tasks | 內容 | 狀態 |
|------|:-----:|------|:----:|
| A | 5 | gpu_render + workflow + delta_panel + 4D Player | ✅ |
| B | 4 | 3場景 + asset_browser + tw_industrial_code + export | ✅ |
| C | 5 | E2E(28+19) + Demo腳本 + TSMC簡報 + 審計 | ✅ |

### W0 OOM 診斷結果

| 批次 | 記憶體變化 | 結論 |
|------|------------|------|
| test_land | 8.7→8.7GB | ✅ 穩定 |
| **test_agents** | 8.9→12.9GB | **⚠️ OOM +4GB** |
| test_bim | 12.9→4.0GB | ✅ pkill回收 |

## 6. 已知問題

| ID | 問題 | 狀態 |
|----|------|:----:|
| ~~ISSUE-001~~ | pytest OOM | **✅ 已解決** |
| ISSUE-002 | API Timeout | 🟡 .env 120s |
| ISSUE-004 | PySide6 記憶體 | 🔴 P29 |
| OOM-001 | test_agents +4GB | 🟡 safe_pytest_dir |
| OOM-002 | python3.11 殘留 | 🟡 Sprint前 pkill |

## 7. Mac Mini

```bash
# MikeRunClaudeSafe v2.0
MikeRunClaudeSafe PromptBIMTestApp1 {Sprint} "..." --conda promptbim --kill
```

## 8. 里程碑

```
2026 Q2: W0✅ → D1-S1✅ → D1-S2✅ → Demo-1★✅ → M1-MVP★✅ → D2 → Demo-2★
2026 Q3: P26-P29 → v3.0.0
2026 Q4: P30-P33 Windows+ILOS
2027 Q1: P34-P41 Web+Mobile
2027 Q2: P42-P44 私有 LLM
```

## 9. 變更日誌

| 版本 | 變更 |
|------|------|
| v1.0-v1.4 | 初始 → ADR-001 + 路線圖 |
| **v1.5** | **Demo-1 完成! 34/34 Tasks✅。W0+D1-S1+D1-S2 全部完成。demo1-v0.1.0 tagged。pytest 60/60 PASS。OOM診斷完成。MikeRunClaudeSafe v2.0。SKILL.md v4.1。** |
| **v1.6** | **M1-MVP 完成! 68/68 Tasks✅。Qt Quick 3D + AgentBridge + PBR + Cost/Schedule/Delta/4D。ThemeManager + Splash + Crash Recovery。io_usd ILOS。6 E2E scenarios PASS。mvp-v0.1.0 tagged。** |

---

*PROJECT.md v1.6 | Zigma PromptToBuild | 2026-03-28*
