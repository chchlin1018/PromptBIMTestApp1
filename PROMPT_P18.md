# PROMPT_P18.md — Sprint P18: V2 Migration Phase 0-1

> 版本: v1.1 | 建立時間: 2026-03-26 | 修訂: 2026-03-26 (P17.1 修復)
> 前置 Sprint: P17 ✅ 完成（全面修整 + Async + 快取, 792 tests, v2.4.0）
> 依賴: docs/DesignDocForV2.md, docs/V2_Migration_Tasks.md, CLAUDE.md v1.13.0, SKILL.md
> 目標版本: v2.5.0

---

## Sprint 目標

**V2 Migration Phase 0-1 — 建立 C++ 核心骨架 + 純邏輯模組遷移**：

### Phase 0: 準備（Part A）
1. 建立 `libpromptbim/` CMake 骨架
2. 設定 vcpkg.json (nlohmann-json, gtest)
3. 定義 C ABI header (promptbim.h)
4. 建立 GoogleTest 框架
5. 配置 GitHub Actions CI 矩陣 (macOS, Windows, Ubuntu)

### Phase 1: 純邏輯模組遷移（Part B）
6. Compliance Engine C++ 實作
7. Compliance Engine GoogleTest
8. pybind11 binding + Python fallback
9. Cost Engine C++ 實作
10. Cost Engine GoogleTest + pybind11
11. C++ vs Python 輸出一致性驗證

---

## ⚠️ 第一步：發送啟動通知（在任何 Task 之前必須執行）

> 這是強制性的第一個動作。在讀完必讀文件、完成環境檢查後，必須立即發送以下 iMessage：

```bash
MSG="🏗️ PromptBIM
🚀 Sprint P18 開始執行
📋 Task: 11 項（2 Parts）
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

**確認通知已發送後，才能繼續執行 Part A。**

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。
確認 `git pull origin main` 為最新。

## 必讀文件

1. **docs/DesignDocForV2.md** — V2 架構設計文件
2. **docs/V2_Migration_Tasks.md** — V2 遷移任務拆解（P17 Task 13 產出）
3. **SKILL.md** — 專案 SSOT
4. **CLAUDE.md v1.13.0** — 行為規範

---

## Part A: Phase 0 準備

> ⚠️ 完成後發送 iMessage：「Sprint P18 — Part A 完成：C++ 骨架建立」

```bash
MSG="🏗️ PromptBIM
✅ Sprint P18 — Part A 完成
📋 C++ CMake 骨架 + vcpkg + GoogleTest 建立完成
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Tasks 1–5: CMake / CI 骨架
（詳見 Sprint 目標 Phase 0 第 1-5 項）

---

## Part B: Phase 1 純邏輯遷移

> ⚠️ 完成後發送 iMessage：「Sprint P18 — Part B 完成：Engine 遷移」

```bash
MSG="🏗️ PromptBIM
✅ Sprint P18 — Part B 完成
📋 Compliance + Cost Engine C++ 遷移完成
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Tasks 6–11: Engine 遷移
（詳見 Sprint 目標 Phase 1 第 6-11 項）

---

## 驗收標準

```
☐ libpromptbim/ CMake 骨架建立
☐ vcpkg.json 可正確拉取依賴
☐ C ABI header 定義完成
☐ GoogleTest 框架可運行
☐ Compliance Engine C++ 通過 GoogleTest
☐ pybind11 binding 可被 Python 呼叫
☐ Python V1 自動選擇 native vs Python compliance engine
☐ CI 矩陣在 macOS + ubuntu 通過
☐ xcodebuild BUILD SUCCEEDED
☐ pytest >= 792 passed
☐ 全量文件同步完成
☐ Sprint 審計報告已產生 (docs/reports/Sprint18_AuditReport.md)
☐ git tag v2.5.0
☐ iMessage 已發送（啟動 + Part A + Part B + 審計 + 最終完成）
```

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保 Swift 檔案、Build Phase、Signing 設定正確。
⚠️ iMessage 通知必須發送（啟動 + 每個 Part 完成 + 審計 + 最終完成）。
⚠️ Sprint 完成後必須產生自我審計報告（代碼 + 文檔 8/8 + Xcode 8/8）。

---

*PROMPT_P18.md v1.1 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.13.0 ✅ | SKILL.md ✅ | 修訂: P17.1 修復測試數+版本+啟動通知+Part通知*
