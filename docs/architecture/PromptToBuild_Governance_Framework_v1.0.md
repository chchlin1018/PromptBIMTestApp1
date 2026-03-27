# PromptToBuild 專案治理架構

> **版本:** v1.0 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **性質:** 專案治理架構 — 管理文件體系、命名規則、同步機制

---

## 1. 治理文件體系（四層架構）

```
CLAUDE.md (憲法 — 不可自動修改)
    │ 規範
    ▼
SKILL.md (百科 — 技術 SSOT)
    │ 參考
    ▼
PROJECT.md (作戰地圖 — 狀態 + 版本 + 排程)
    │ 紀錄
    ▼
audit-reports/ (歷史紀錄)
```

| 文件 | 角色 | 維護者 | 修改頻率 |
|------|------|--------|--------|
| CLAUDE.md | 最高治理規則 | 人工 (Michael) | 極低（重大事故） |
| SKILL.md | 專案 SSOT | 人工 (Michael) | 每 Sprint |
| PROJECT.md | 專案管理中樞 | Claude Code + 人工 | 每 Task |
| audit-reports/ | Sprint 審計 | Claude Code | 每 Sprint |

---

## 2. 命名規則

### 2.1 階段 (Phase)

格式: `PH{N}` 或 `Phase-{N}`

| ID | 名稱 | Sprint |
|----|------|--------|
| PH0 | POC 收尾 | P25+P24 |
| PH0.5 | Demo | D1+D2 |
| PH1 | Plugin 架構 | P26-P29 |
| PH2 | Windows + USD↔Revit | P30-P33 |
| PH3 | ILOS + Omniverse | P34-P37 |
| PH4 | Web + Mobile | P38-P41 |
| PH5 | 私有 LLM | P42-P44 |
| PH6 | SaaS + Marketplace | P45-P50+ |

### 2.2 Demo Task

格式: `D{N}-S{X}-P{Y}-T{Z}`

- D = Demo 編號 (1, 2, 3...)
- S = Sprint 編號 (1, 2, 3...)
- P = Part (A, B, C, D)
- T = Task (1, 2, 3...)

範例: `D1-S1-PA-T4` = Demo 1, Sprint 1, Part A, Task 4

### 2.3 正式 Sprint Task

格式: `P{XX}-P{Y}-T{Z}`

- P{XX} = Sprint 編號 (25, 26... 50)
- P{Y} = Part (A, B, C, D)
- T{Z} = Task (1, 2, 3...)

範例: `P26-PA-T1` = Sprint 26, Part A, Task 1

### 2.4 Git Tag

| 類型 | 格式 | 範例 |
|------|------|------|
| 正式 | `v{MAJOR}.{MINOR}.{PATCH}` | v3.0.0 |
| Demo | `demo{N}-v{M}.{m}.{p}` | demo1-v0.1.0 |
| Sprint RC | `sprint-{XX}-rc` | sprint-26-rc |

### 2.5 Git Branch

| 類型 | 格式 | 範例 |
|------|------|------|
| 主幹 | `main` | — |
| Sprint | `sprint/{XX}` | sprint/26 |
| Demo | `demo/{N}` | demo/1 |
| Feature | `feature/{sprint}-{desc}` | feature/p26-plugin-bus |
| Fix | `fix/{sprint}-{desc}` | fix/p30-revit-timeout |

### 2.6 Commit Message

格式: `[{scope}] {type}: {description}`

- scope: P26 | D1-S2 | docs | ci
- type: feat | fix | refactor | test | docs | chore

範例:
- `[P26] feat: IPlugin base interface`
- `[D1-S2] feat: one-click USD to Revit`
- `[docs] update: Architecture v2.1`

### 2.7 AuditReport + PROMPT

- AuditReport: `{Sprint/Demo}_AuditReport.md` (e.g. Sprint26_AuditReport.md)
- PROMPT: `PROMPT_{Sprint/Demo}.md` (e.g. PROMPT_P26.md, PROMPT_D1.md)

---

## 3. 狀態符號

| 符號 | 狀態 | 說明 |
|:----:|------|------|
| ⬜ | Not Started | 尚未開始 |
| 🔵 | Active | 進行中 |
| ✅ | Done | 完成 |
| ⚠️ | Blocked | 被阻塞 |
| ❌ | Failed | 失敗 |
| 🔄 | In Review | 審查中 |
| ⏭️ | Skipped | 跳過 |

---

## 4. 同步規則

| 事件 | CLAUDE.md | SKILL.md | PROJECT.md | audit-reports/ |
|------|:---------:|:--------:|:----------:|:--------------:|
| Task 開始 | — | — | 🔵 | — |
| Task 完成 | — | — | ✅ | — |
| Sprint 完成 | — | 更新 | ✅+版本 | ✅ 產生 |
| Demo 完成 | — | — | ✅+tag | ✅ Demo 報告 |
| Phase 完成 | 可能 | 大更新 | 里程碑 | 階段總結 |
| 重大事故 | 新增規則 | 記錄教訓 | 問題追蹤 | 詳細報告 |

---

## 5. CLAUDE.md v1.23.0 建議新增規則

```
== PROJECT.md 同步規則 (v1.23.0) ==

1. PROJECT.md 是專案狀態的唯一真相來源
2. 每 Task 開始前: PROJECT.md 狀態 → 🔵
3. 每 Task 完成後: PROJECT.md 狀態 → ✅
4. Sprint 完成: PROJECT.md + SKILL.md + AuditReport
5. Demo 完成: PROJECT.md + Demo_AuditReport + git tag
6. 命名規則: 全部遵循 PROJECT.md §7
7. Claude Code 禁止修改 CLAUDE.md / SKILL.md
8. Claude Code 可以且應該更新 PROJECT.md
```

---

## 6. SKILL.md v4.0 建議新增內容

```
== 專案治理 ==

治理文件:
- CLAUDE.md v1.23.0: 最高規則（人工）
- SKILL.md v4.0: 技術 SSOT（人工）
- PROJECT.md v1.0: 專案狀態（Claude Code 可更新）

命名規則:
- Demo: D{N}-S{X}-P{Y}-T{Z}
- Sprint: P{XX}-P{Y}-T{Z}
- Tag: v{M}.{m}.{p} / demo{N}-v{M}.{m}.{p}
- Branch: sprint/{XX} / demo/{N}
- Commit: [{scope}] {type}: {desc}
```

---

## 7. AuditReport 標準格式

```markdown
# {Sprint/Demo} 審計報告

## 摘要
- Sprint/Demo: {ID}
- 日期: {start} → {end}
- 狀態: ✅ / ❌
- 版本: {version}

## Task 完成狀態
| Task ID | 說明 | 狀態 | 備註 |

## 技術決策紀錄
## 事故紀錄
## 指標 (Task 完成率 / 測試通過率 / 記憶體)
## 下一步
```

---

## 8. Repo 目錄結構

```
PromptBIMTestApp1/
├── CLAUDE.md              ← 憲法 (v1.22.0 → v1.23.0)
├── SKILL.md               ← 百科 (v3.8 → v4.0)
├── PROJECT.md             ← 作戰地圖 (v1.0) ★ NEW
├── PROJECT_STATUS.md      ← deprecated
├── docs/architecture/     ← 架構文件 (9 份)
├── audit-reports/         ← Sprint 審計
├── prompts/               ← Sprint/Demo 執行指令
├── src/                   ← 原始碼
├── tests/                 ← 測試
├── plugins/               ← Plugin (P26+)
├── demo/                  ← Demo 腳本 (D1+)
└── examples/
```

---

*PromptToBuild 專案治理架構 v1.0*
*Reality Matrix Inc. | 2026-03-27*
