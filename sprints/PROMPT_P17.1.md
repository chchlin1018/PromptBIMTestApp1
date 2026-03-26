# PROMPT_P17.1.md — Sprint P17.1: 審計修復 + 文檔一致性

> 版本: v1.0 | 建立時間: 2026-03-26
> 前置 Sprint: P17 ✅ 完成（Complete Hardening, 792 tests, v2.4.0）
> 來源: docs/reports/Sprint17_AuditReport.md（綜合評分 B，文檔 5/8）
> 依賴: CLAUDE.md v1.13.0
> 目標版本: v2.4.1（patch release — 僅文檔修復）

---

## Sprint 目標

**修復 Sprint 17 審計報告中發現的 3 個文檔一致性問題**，共 **1 個 Part、6 個 Task**。

---

## ⚠️ 第一步：發送啟動通知（在任何 Task 之前必須執行）

> 這是強制性的第一個動作。在讀完必讀文件、完成環境檢查後，必須立即發送以下 iMessage：

```bash
MSG="🏗️ PromptBIM
🚀 Sprint P17.1 開始執行
📋 Task: 6 項（1 Part）
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

**確認通知已發送後，才能繼續執行 Part A。**

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 `git pull origin main` 為最新。

## 必讀文件

1. **CLAUDE.md v1.13.0** — 行為規範（特別注意自我審計 3 領域規則）
2. **docs/reports/Sprint17_AuditReport.md** — 本 Sprint 的依據
3. **PROMPT_P18.md** — 需要修復的檔案

---

## Part A: 文檔一致性修復

> ⚠️ 完成後發送 iMessage：「Sprint P17.1 — Part A 完成：文檔修復」

#### Task 1: 修復 PROMPT_P18.md — 測試數
- 將 "776 tests" 改為 "792 tests"

#### Task 2: 修復 PROMPT_P18.md — CLAUDE.md 版本
- 將所有 "CLAUDE.md v1.9.0" 改為 "CLAUDE.md v1.13.0"
- 更新合規性檢查標記

#### Task 3: 修復 PROMPT_P18.md — 加入啟動通知步驟
- 在 Part 列表之前加入「⚠️ 第一步：發送啟動通知」段落
- 使用 CLAUDE.md v1.13.0 規定的模板
- 加入 Part 結構（如有多個 Part）或標明單 Part 完成通知

#### Task 4: 修復 PROMPT_P18.md — 加入 Part 完成通知
- 執行指令段落加入「每個 Part 完成 + 最終完成」通知提醒
- 確保符合 CLAUDE.md v1.13.0 所有合規性檢查項目

#### Task 5: 驗證 docs/PromptBIM_Context_Prompt.md
- 確認 Sprint 完成狀態寫的是 P17 ✅ 792 tests v2.4.0
- 如有不一致，修正為正確數據

#### Task 6: 檢查 SKILL.md 是否需更新
- P17 新增了 `plugins/`, `cache/`, async 架構
- 讀取 SKILL.md，評估是否需要加入這些架構變更
- 如需更新：加入新模組描述
- 如不需要：在 terminal echo 說明原因

---

## 驗收標準

```
☐ xcodebuild BUILD SUCCEEDED
☐ pytest >= 792 passed
☐ PROMPT_P18.md 測試數正確（792）
☐ PROMPT_P18.md 引用 CLAUDE.md v1.13.0
☐ PROMPT_P18.md 有啟動通知步驟
☐ PROMPT_P18.md 有 Part 完成通知
☐ docs/PromptBIM_Context_Prompt.md 數據一致
☐ SKILL.md 評估完成
☐ 全量文件同步完成
☐ Sprint 審計報告已產生（docs/reports/Sprint17.1_AuditReport.md）
☐ git tag v2.4.1
☐ iMessage 已發送（啟動 + Part 完成 + 審計 + 最終完成）
```

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保 Swift 檔案、Build Phase、Signing 設定正確。
⚠️ iMessage 通知必須發送（啟動 + 每個 Part 完成 + 最終完成）。
⚠️ Sprint 完成後必須產生自我審計報告（代碼 + 文檔 8/8 + Xcode 8/8）。
⚠️ 本 Sprint 是 patch release，僅修復文檔問題，不改動任何代碼邏輯。

---

*PROMPT_P17.1.md v1.0 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.13.0 ✅ | SKILL.md ✅ | 來源: Sprint17_AuditReport.md*
