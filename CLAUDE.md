# CLAUDE.md — Claude Code 自動開發指引

> 本文件供 Claude Code 讀取，定義自動開發的行為規範

## 開發前必讀

1. **先讀 SKILL.md** — 專案的 Single Source of Truth
2. **再讀對應的 Addendum** — `docs/addendum/` 下的技術規格
3. **檢查 TODO.md** — 確認當前 Sprint 狀態
4. **遵守 CHANGELOG.md** — 每完成 Sprint 要更新

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
- 所有視覺化輸出

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
[P7] Implement 3D A* MEP pathfinder
```

## 文件版本控制

| 文件 | 誰更新 | 何時更新 |
|------|--------|----------|
| SKILL.md | 人工 | 架構變更時 |
| TODO.md | Claude Code | 每完成一個 task |
| CHANGELOG.md | Claude Code | 每完成一個 Sprint |
| SETUP.md | Claude Code | 安裝步驟變更時 |
| docs/addendum/*.md | 人工 | 規格變更時 |

## 測試要求

- 每個新 module 至少有 1 個 pytest 測試
- BIM 生成必須驗證 IFC 檔案可被 IfcOpenShell 重新讀取
- USD 生成必須驗證 stage 可被 pxr.Usd.Stage.Open() 開啟
- GUI 測試使用 pytest-qt

## 重要限制

- ⚠️ **不使用任何商業軟體或函式庫**
- ⚠️ Builder Agent **不使用 LLM**（純 Python 確定性程式碼）
- ⚠️ 所有座標使用**公尺制本地座標系**
- ⚠️ IFC 只用 `ifcopenshell.api.run()` 高階 API
- ⚠️ USD 只用 `pxr.Usd`, `pxr.UsdGeom`, `pxr.UsdShade`
