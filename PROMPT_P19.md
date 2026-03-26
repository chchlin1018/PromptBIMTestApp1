# PROMPT_P19.md — Sprint P19: V2 Migration Phase 2 — MEP + Simulation C++

> 版本: v1.0 | 建立時間: 2026-03-26
> 前置 Sprint: P18 ✅ 完成（C++ 骨架 + Compliance/Cost C++ + pybind11 + 24 GoogleTests, 820 tests, v2.5.0）
> 依賴: docs/DesignDocForV2.md, docs/V2_Migration_Tasks.md, CLAUDE.md v1.13.0, SKILL.md
> 目標版本: v2.6.0

---

## Sprint 目標

**V2 Migration Phase 2 — 效能敏感模組遷移**：

### Phase 2: 效能敏感模組（Part A + Part B）

1. MEP A* Pathfinding C++ 實作（src/promptbim/bim/mep/ 移植）
2. MEP Engine GoogleTest + 效能基準
3. MEP Engine pybind11 binding + Python fallback
4. Simulation Engine C++ — 4D scheduler 移植
5. Simulation Engine GoogleTest + pybind11
6. 效能對照報告（Python vs C++）
7. Fix pybind11 build dir 選擇問題（py3.11 vs py3.13 衝突）
8. `poly_area()` 抽取到共用 `geometry.cpp`（消除 DRY 問題）
9. C++ 中文訊息 UTF-8 CI locale 確認
10. Python pytest 820+ 通過

---

## ⚠️ 第一步：發送啟動通知（在任何 Task 之前必須執行）

```bash
MSG="🏗️ PromptBIM
🚀 Sprint P19 開始執行
📋 Task: 10 項（2 Parts）
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
2. **docs/V2_Migration_Tasks.md** — V2 遷移任務拆解
3. **SKILL.md** — 專案 SSOT
4. **CLAUDE.md v1.13.0** — 行為規範

---

## Part A: MEP A* C++

> ⚠️ 完成後發送 iMessage：「Sprint P19 — Part A 完成：MEP C++」

```bash
MSG="🏗️ PromptBIM
✅ Sprint P19 — Part A 完成
📋 MEP A* Pathfinding C++ 遷移完成
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Tasks 1–4: MEP Engine

參考 `src/promptbim/bim/mep/` 移植 A* 路徑尋找演算法到 C++。

---

## Part B: Simulation + 修復技術債

> ⚠️ 完成後發送 iMessage：「Sprint P19 — Part B 完成：Simulation C++ + 技術債修復」

```bash
MSG="🏗️ PromptBIM
✅ Sprint P19 — Part B 完成
📋 Simulation C++ 遷移 + poly_area 共用 + pybind11 修復
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Tasks 5–10: Simulation + 修復

---

## 驗收標準

```
☐ MEP A* C++ 通過 GoogleTest
☐ Simulation C++ 通過 GoogleTest
☐ pybind11 build dir 選擇問題修復（py3.11 優先）
☐ poly_area() 抽取到共用 geometry.cpp
☐ 效能對照報告產生
☐ xcodebuild BUILD SUCCEEDED
☐ pytest >= 820 passed
☐ 全量文件同步完成
☐ Sprint 審計報告已產生 (docs/reports/Sprint19_AuditReport.md)
☐ git tag v2.6.0
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

*PROMPT_P19.md v1.0 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.13.0 ✅ | SKILL.md ✅ | 基於 Sprint18 審計報告建議*
