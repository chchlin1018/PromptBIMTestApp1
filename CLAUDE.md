# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.1.0 | **更新:** 2026-03-25
> **版本控制:** 本文件由人工維護，Claude Code 不得直接修改

---

## 開發前必讀順序

```
1. PROMPT.md    ← 執行指令 + 文件檢查清單（最重要！）
2. SKILL.md     ← 專案 SSOT（架構、Schema、Agent Prompt、開發規範）
3. TODO.md      ← 確認當前 Sprint 狀態
4. 對應 Addendum ← 依當前 Sprint 讀取技術規格
5. CLAUDE.md    ← 本文件（行為規範）
```

---

## 專案本質

這是一個 **概念驗證 (POC)** 專案。目標是展示完整工作流，不追求生產級品質。

用戶只需要：
- 輸入土地資料（或隨意描述面積）
- 輸入 AI Prompt（如 "帶游泳池的3層別墅"）

系統自動完成：
- AI 搜尋建築規格和免費模型
- 自動設計建築平面和結構
- 生成 IFC + OpenUSD 雙格式
- 自動 MEP 管線路由
- 台灣法規合規檢查
- 施工模擬 (4D) + 成本估算 (5D)
- 智慧監控點自動配置
- 所有視覺化輸出
- **即時互動修改**（用戶說「改為9層」→ 所有關聯數據即時更新）

---

## 文件版本控制矩陣

| 文件 | 誰更新 | 何時更新 | Claude Code 可改？ |
|------|--------|----------|:-----------------:|
| `SKILL.md` | 人工 | 架構變更 | ❌ 禁止 |
| `PROMPT.md` | 人工 | 流程變更 | ❌ 禁止 |
| `CLAUDE.md` | 人工 | 規範變更 | ❌ 禁止 |
| `docs/addendum/*.md` | 人工 | 規格變更 | ❌ 禁止 |
| `README.md` | 人工 | 功能變更 | ❌ 禁止 |
| `TODO.md` | **Claude Code** | 每完成 1 個 task | ✅ 必須更新 |
| `CHANGELOG.md` | **Claude Code** | 每完成 1 個 Sprint | ✅ 必須更新 |
| `SETUP.md` | **Claude Code** | 安裝步驟變更 | ✅ 可更新 |
| `src/**/*.py` | **Claude Code** | 開發時 | ✅ 核心工作 |
| `tests/**/*.py` | **Claude Code** | 開發時 | ✅ 核心工作 |

### 版本號格式

- 人工文件: `vX.Y.Z`（Semver）
- TODO.md: 用 ✅/⬜/🔄 標記
- CHANGELOG.md: `[0.X.0] - YYYY-MM-DD`

---

## Git Commit 規範

```
[Sprint ID] 簡短描述

範例:
[P0] Init project scaffold
[P1] Add GeoJSON land parser
[P2] Implement IFC wall generation
[P2.5] Add elevator component definition
[P4] Integrate Planner agent with Claude API
[P4.5] Add BCR/FAR compliance rules
[P4.8] Implement modification engine with delta computation
[P7] Implement 3D A* MEP pathfinder
[P8.5] Add auto monitor placement for HVAC system
```

---

## 重要限制

- ⚠️ **不使用任何商業軟體或函式庫**
- ⚠️ Builder Agent **不使用 LLM**（純 Python 確定性程式碼）
- ⚠️ 所有座標使用**公尺制本地座標系**
- ⚠️ IFC 只用 `ifcopenshell.api.run()` 高階 API
- ⚠️ USD 只用 `pxr.Usd`, `pxr.UsdGeom`, `pxr.UsdShade`
- ⚠️ 修改指令用**增量更新**，不從頭重新生成
- ⚠️ 監控點輸出必須含 `monitor:` USD namespace（IDTF 對接）

---

## 測試要求

- 每個新 module 至少有 1 個 pytest 測試
- BIM 生成必須驗證 IFC 檔案可被 IfcOpenShell 重新讀取
- USD 生成必須驗證 stage 可被 pxr.Usd.Stage.Open() 開啟
- GUI 測試使用 pytest-qt
- 修改引擎需驗證版本歷史一致性

---

## 開發環境

- **平台:** macOS (Apple Silicon)
- **Python:** 3.11+
- **套件管理:** Conda (Miniforge) + pip
- **IDE:** Claude Code CLI
- **Git:** main branch, squash commits per Sprint

---

*CLAUDE.md v1.1.0 | 2026-03-25 | Claude Code 行為規範 + 版本控制矩陣*
