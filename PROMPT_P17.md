# PROMPT_P17.md — Sprint P17: V2 Architecture Migration (Phase 1)

> 版本: v1.0 | 建立時間: 2026-03-26
> 前置 Sprint: P16 ✅ 完成（全面品質修整, 725 tests, git tag v2.1.0）
> 前置 Sprint: P15 ⬜ 待執行（可獨立，不阻擋 P17）
> 依賴: docs/DesignDocForV2.md, SKILL.md v3.1, CLAUDE.md v1.8.0
> 目標版本: v2.2.0

---

## Sprint 目標

基於 `docs/DesignDocForV2.md` 設計文件，開始 V2 架構遷移的第一階段。
具體內容待審閱設計文件後決定。

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。
確認 `git pull origin main` 為最新。

## 必讀文件

1. **SKILL.md** — 專案 SSOT
2. **CLAUDE.md v1.8.0** — 行為規範
3. **docs/DesignDocForV2.md** — V2 架構設計文件
4. **TODO.md** — 確認當前 Sprint 狀態
5. **AuditReport.md** — 品質報告（確認未修復項目）

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保 Swift 檔案、Build Phase、Signing 設定正確。
⚠️ iMessage 通知必須發送（啟動 + 完成）。

---

*PROMPT_P17.md v1.0 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.8.0 ✅ | SKILL.md ✅*
