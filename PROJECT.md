# PromptToBuild 專案管理

> **版本:** v1.0 | **最後更新:** 2026-03-27
> **專案:** PromptToBuild (PromptBIMTestApp1)
> **組織:** Reality Matrix Inc.
> **倉庫:** github.com/chchlin1018/PromptBIMTestApp1

---

## 1. 版本控制

| 標籤 | 版本 | Sprint/Demo | 日期 | 說明 |
|------|------|------------|------|------|
| v2.10.0 | 2.10.0 | P23 | 2026-03 | 審計修復（最後成功 tag） |
| v2.12.0 | 2.12.0 | P25 | 2026-03 | 效能 + Windows + 文件 |
| demo1-v0.1.0 | 0.1.0 | D1 | — | Demo-1（Win+Revit，無 ILOS/Omni） |
| demo2-v0.2.0 | 0.2.0 | D2 | — | Demo-2（+ILOS+Omniverse） |
| v3.0.0 | 3.0.0 | P29 | — | Plugin 架構 + Qt6 |
| v4.0.0 | 4.0.0 | P41 | — | Web + Mobile |
| v5.0.0 | 5.0.0 | P44 | — | 私有 LLM（零外部 AI） |

---

## 2. 治理文件同步狀態

| 文件 | 版本 | 角色 | 維護者 |
|------|------|------|--------|
| CLAUDE.md | v1.22.0 | 最高治理規則 | 人工 |
| SKILL.md | v3.8 | 技術 SSOT | 人工 |
| **PROJECT.md** | **v1.0** | **專案管理** | **Claude Code + 人工** |
| PROJECT_STATUS.md | ⚠️ deprecated | 舊版狀態追蹤 | 已遷移至 PROJECT.md |

---

## 3. 開發狀態總覽

### Phase 狀態

| Phase | Sprint | 目標 | 版本 | 狀態 |
|-------|--------|------|------|:----:|
| PH0 | P25收尾+P24 | POC 收尾 | v2.12 | 🔵 |
| PH0.5 | D1+D2 | Demo 展示 | demo1/2 | ⬜ |
| PH1 | P26-P29 | Plugin + Qt6 | v3.0 | ⬜ |
| PH2 | P30-P33 | Windows + USD↔Revit | v3.x | ⬜ |
| PH3 | P34-P37 | ILOS + Omniverse | v4.0 | ⬜ |
| PH4 | P38-P41 | Web + Mobile | v4.x | ⬜ |
| PH5 | P42-P44 | 私有 LLM | v5.0 | ⬜ |
| PH6 | P45-P50+ | SaaS + Marketplace | v5.x | ⬜ |

### Demo 狀態

| Demo | Sprint | 重點 | 需要 ILOS | 需要 Omni | 狀態 |
|------|--------|------|:---------:|:---------:|:----:|
| D1 | D1-S1~S3 | Win + Revit + AI 規劃 | ❌ | ❌ | ⬜ |
| D2 | D2-S1~S3 | +ILOS + Omniverse | ✅ | ✅ | ⬜ |

---

## 4. 當前 Sprint 進度

### PH0: P25 收尾 + P24 修復

| Task ID | 說明 | 狀態 |
|---------|------|:----:|
| P25-PA-T1 | 確認 P25 commit 完整性 | ⬜ |
| P25-PA-T2 | Mac Mini pytest pass | ⬜ |
| P25-PA-T3 | Sprint25_AuditReport | ⬜ |
| P25-PA-T4 | git tag v2.12.0 | ⬜ |
| P25-PA-T5 | PROJECT.md 更新 | ⬜ |
| P24-PB-T6 | conftest.py offscreen | ⬜ |
| P24-PB-T7 | 逐目錄 pytest | ⬜ |
| P24-PB-T8 | pytest pass | ⬜ |
| P24-PB-T9 | git tag v2.11.0 | ⬜ |
| PH0-PC-T10 | Win: Omniverse Nucleus 驗證 | ⬜ |
| PH0-PC-T11 | Win: ILOS USD 載入 | ⬜ |
| PH0-PC-T12 | Win: DirectShape 測試 | ⬜ |
| PH0-PC-T13 | Win: Pipe.Create 測試 | ⬜ |
| PH0-PC-T14 | Win: Omniverse Streaming | ⬜ |
| PH0-PC-T15 | .env API_TIMEOUT=120 | ⬜ |

---

## 5. 合作夥伴狀態

| 模組 | 來源 | Plugin 介面 | 狀態 | 預計到位 |
|------|------|------------|:----:|--------|
| ILOS Layout Engine | 外部夥伴 | IEnginePlugin | ⬜ 未到 | P34+ |
| ILOS Piping Router | 外部夥伴 | IEnginePlugin | ⬜ 未到 | P34+ |
| USD↔Revit Converter | 外部夥伴 | IIOPlugin | ⬜ 未到 | P30+ |
| 介面合約簽定 | 雙方 | — | ⬜ | P26 前 |

---

## 6. 已知問題與技術債

| ID | 問題 | 嚴重度 | 狀態 | 計劃解決 |
|----|------|:------:|:----:|--------|
| ISSUE-001 | pytest OOM 26GB | 🔴 | ⚠️ | P25 conftest.py |
| ISSUE-002 | API Timeout 30s | 🟡 | ⬜ | .env 120s |
| ISSUE-003 | ci-windows.yml 缺依賴 | 🟡 | ⬜ | 改 workflow_dispatch |
| ISSUE-004 | PySide6 記憶體開銷 | 🔴 | ⬜ | P29 移除 |

---

## 7. 命名規則速查

| 類型 | 格式 | 範例 |
|------|------|------|
| Demo Task | `D{N}-S{X}-P{Y}-T{Z}` | D1-S1-PA-T4 |
| Sprint Task | `P{XX}-P{Y}-T{Z}` | P26-PA-T1 |
| Git Tag | `v{M}.{m}.{p}` / `demo{N}-v{M}.{m}.{p}` | v3.0.0 / demo1-v0.1.0 |
| Git Branch | `sprint/{XX}` / `demo/{N}` | sprint/26 / demo/1 |
| Commit | `[{scope}] {type}: {desc}` | [P26] feat: IPlugin base |
| AuditReport | `{Sprint/Demo}_AuditReport.md` | Sprint26_AuditReport.md |
| PROMPT | `PROMPT_{Sprint/Demo}.md` | PROMPT_P26.md |

詳細規則見: docs/architecture/PromptToBuild_Governance_Framework_v1.0.md

---

## 8. 里程碑時間線

```
2026 Q2:     PH0 (P25收尾)       → v2.12.0
2026 Q2:     PH0.5 Demo-1 (3週)   → demo1-v0.1.0
2026 Q2-Q3:  PH0.5 Demo-2 (3週)   → demo2-v0.2.0
2026 Q3:     PH1 (P26-P29, 8週)   → v3.0.0
2026 Q3-Q4:  PH2 (P30-P33, 8週)   → v3.x
2026 Q4-27Q1: PH3 (P34-P37, 8週)  → v4.0
2027 Q1-Q2:  PH4 (P38-P41, 8週)   → v4.x
2027 Q2-Q3:  PH5 (P42-P44, 6週)   → v5.0
2027 Q3+:    PH6 (P45-P50+)       → v5.x+
```

---

*PROJECT.md v1.0 | PromptToBuild | Reality Matrix Inc. | 2026-03-27*
