# PROMPT_P19.md — Sprint P19: V2 Migration Phase 2 — MEP + Simulation C++ + P18 技術債

> 版本: v1.1 | 建立時間: 2026-03-26 | 修正: 補入 P18 技術債第 4 項
> 前置 Sprint: P18 ✅ 完成（C++ 骨架 + Compliance/Cost C++ + pybind11 + 24 GoogleTests, 820 tests, v2.5.0）
> 依賴: docs/DesignDocForV2.md, docs/V2_Migration_Tasks.md, CLAUDE.md v1.13.0, SKILL.md
> 來源: docs/reports/Sprint18_AuditReport.md（綜合 A，4 項技術債）
> 目標版本: v2.6.0

---

## Sprint 目標

**V2 Migration Phase 2 — 效能敏感模組遷移 + P18 技術債清理**，共 **2 個 Part、11 個 Task**：

- Part A: MEP A* Pathfinding C++ 遷移（4 Tasks）
- Part B: Simulation C++ 遷移 + P18 技術債修復（7 Tasks）

---

## ⚠️ 第一步：發送啟動通知（在任何 Task 之前必須執行）

```bash
MSG="🏗️ PromptBIM
🚀 Sprint P19 開始執行
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
2. **docs/V2_Migration_Tasks.md** — V2 遷移任務拆解
3. **docs/reports/Sprint18_AuditReport.md** — P18 審計報告（技術債來源）
4. **SKILL.md v3.2** — 專案 SSOT
5. **CLAUDE.md v1.13.0** — 行為規範

---

## Part A: MEP A* C++ 遷移

> ⚠️ 完成後發送 iMessage：「Sprint P19 — Part A 完成：MEP C++」

```bash
MSG="🏗️ PromptBIM
✅ Sprint P19 — Part A 完成
📋 MEP A* Pathfinding C++ 遷移完成
🧪 pytest: ${TEST_COUNT}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

#### Task 1: MEP A* Pathfinding C++ 實作
- 參考 `src/promptbim/bim/mep/` 移植 A* 路徑尋找演算法
- 新建 `libpromptbim/src/mep/mep_engine.cpp` + `include/promptbim/mep_engine.hpp`
- C ABI: `pb_plan_mep()` + `pb_free_string()`

#### Task 2: MEP Engine GoogleTest
- 新建 `libpromptbim/tests/test_mep_engine.cpp`
- 涵蓋：基本路徑、障礙物繞行、無路徑情況、效能基準

#### Task 3: MEP Engine pybind11 binding
- 加入 `bindings/python/bindings.cpp` 的 MEP 綁定
- `_native_bridge.py` 加入 MEP fallback 邏輯

#### Task 4: MEP C++ vs Python 效能對照
- 測試相同輸入下 C++ vs Python 的效能差異
- 產出效能對照數據（列入審計報告）

---

## Part B: Simulation C++ 遷移 + P18 技術債修復

> ⚠️ 完成後發送 iMessage：「Sprint P19 — Part B 完成：Simulation C++ + 技術債修復」

```bash
MSG="🏗️ PromptBIM
✅ Sprint P19 — Part B 完成
📋 Simulation C++ + poly_area 共用 + pybind11 修復 + stubs 分離
🧪 pytest: ${TEST_COUNT}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

#### Task 5: Simulation Engine C++ 實作
- 4D scheduler 移植到 `libpromptbim/src/simulation/simulation_engine.cpp`
- C ABI: `pb_simulate_construction()` + `pb_free_string()`

#### Task 6: Simulation Engine GoogleTest + pybind11
- GoogleTest 覆蓋基本排程、依賴關係、並行任務
- pybind11 binding + Python fallback

#### Task 7: 修復 pybind11 build dir 選擇問題 [P18 技術債 Medium]
- py3.11 vs py3.13 衝突：CMakeLists.txt 加入明確的 `Python3_EXECUTABLE` 指定
- 優先使用 conda env 中的 python3.11
- CI 矩陣中驗證 build dir 正確

#### Task 8: `poly_area()` 抽取到共用 `geometry.cpp` [P18 技術債 Low]
- 新建 `libpromptbim/src/geometry/geometry.cpp` + `include/promptbim/geometry.hpp`
- compliance_engine.cpp 和 cost_engine.cpp 改為 `#include` 共用版本
- 確保現有 GoogleTest 全部通過

#### Task 9: C++ 中文訊息 UTF-8 CI locale 確認 [P18 技術債 Medium]
- CI 矩陣加入 `LC_ALL=en_US.UTF-8` 環境變數
- 加入含中文訊息的 GoogleTest 確認 UTF-8 正確解析
- macOS + Ubuntu 雙平台驗證

#### Task 10: Placeholder stubs 分離 [P18 技術債 Low]
- compliance_engine.cpp 中的 Phase 3/4 placeholder stubs 移至獨立檔案
- 新建 `libpromptbim/src/stubs/future_stubs.cpp`
- 確保現有 GoogleTest 不受影響

#### Task 11: 效能對照報告
- 產出 `docs/reports/V2_Performance_Comparison.md`
- 涵蓋 Compliance / Cost / MEP / Simulation 四個引擎的 C++ vs Python 效能差異

---

## 驗收標準

```
☐ MEP A* C++ 通過 GoogleTest
☐ Simulation C++ 通過 GoogleTest
☐ pybind11 build dir 選擇問題修復（py3.11 優先）
☐ poly_area() 抽取到共用 geometry.cpp
☐ C++ UTF-8 中文訊息 CI 驗證通過
☐ Placeholder stubs 已分離到獨立檔案
☐ 效能對照報告已產生
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
⚠️ P18 技術債 4 項必須全部處理（Task 7-10）。

---

*PROMPT_P19.md v1.1 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.13.0 ✅ | SKILL.md v3.2 ✅ | 基於 Sprint18_AuditReport.md 技術債*
