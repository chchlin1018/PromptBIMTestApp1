# PROMPT_P15.md — Sprint P15: V2 Architecture Migration

> 版本: v2.1.0 | 建立時間: 2026-03-26
> 前置 Sprint: P14 ✅ 完成（CI/CD + Security + Docs v2.0, 705 tests）
> 依賴: P0~P14, docs/DesignDocForV2.md
> 品質分析: docs/reports/Full_Codebase_Quality_Report.md

## Sprint 目標

1. **V2 Architecture Review** — 審閱 DesignDocForV2.md，拆解為可執行 tasks
2. **Lazy Import Optimization** — Orchestrator + module-level imports 改為 lazy
3. **Plugin System** — Agent / Parser / Code Rule 可擴充架構
4. **Test Refactor** — Mock isolation improvement, fixture consolidation

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。

## 必讀文件
1. SKILL.md
2. CLAUDE.md
3. TODO.md
4. docs/DesignDocForV2.md
5. pyproject.toml

---

## 執行指令
所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保 Swift 檔案、Build Phase、Signing 設定正確。
⚠️ iMessage 通知必須發送（啟動 + 完成）。
