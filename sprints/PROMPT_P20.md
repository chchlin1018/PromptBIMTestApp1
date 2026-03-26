# PROMPT_P20.md — Sprint P20: V2 Migration Phase 3 — BIM Core (IFC + USD C++)

> 版本: v1.0 | 建立時間: 2026-03-26
> 前置 Sprint: P19 ✅ 完成（MEP + Simulation C++ + P18 技術債修復, 883 tests, v2.6.0）
> 依賴: docs/DesignDocForV2.md, docs/V2_Migration_Tasks.md, CLAUDE.md v1.13.0, SKILL.md
> 來源: docs/V2_Migration_Tasks.md Phase 3 (V2-030~V2-035)
> 目標版本: v2.7.0

---

## Sprint 目標

**V2 Migration Phase 3 — BIM Core Engine C++ 遷移**，共 **2 個 Part、8 個 Task**：

- Part A: IFC Generator C++ 遷移（4 Tasks）
- Part B: USD Generator C++ + USDZ 打包 + pybind11（4 Tasks）

---

## ⚠️ 第一步：發送啟動通知（在任何 Task 之前必須執行）

```bash
MSG="🏗️ PromptBIM
🚀 Sprint P20 開始執行
📋 Task: 8 項（2 Parts）
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
2. **docs/V2_Migration_Tasks.md** — V2 遷移任務拆解（Phase 3）
3. **SKILL.md v3.2** — 專案 SSOT
4. **CLAUDE.md v1.13.0** — 行為規範

---

## Part A: IFC Generator C++ 遷移

> ⚠️ 完成後發送 iMessage：「Sprint P20 — Part A 完成：IFC Generator C++」

```bash
MSG="🏗️ PromptBIM
✅ Sprint P20 — Part A 完成
📋 IFC Generator C++ 遷移完成
🧪 pytest: ${TEST_COUNT}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

#### Task 1: 研究 IfcOpenShell C++ API
- 確認 IfcOpenShell C++ header 位置和 API 介面
- 評估是否可直接使用 C++ API 或需要通過 CMake 整合

#### Task 2: IFC Generator C++ 實作
- 新建 `libpromptbim/src/bim/ifc_generator.cpp` + `include/promptbim/ifc_generator.hpp`
- 使用 IfcOpenShell C++ API 直接生成 IFC 檔案
- C ABI: `pb_generate_ifc()` 替換 placeholder stub

#### Task 3: IFC Generator GoogleTest
- 新建 `libpromptbim/tests/test_ifc_generator.cpp`
- 驗證 IFC 輸出結構正確性

#### Task 4: IFC Generator pybind11 binding
- 加入 `bindings/python/bindings.cpp` 的 IFC 綁定
- `_native_bridge.py` 加入 IFC fallback 邏輯

---

## Part B: USD Generator C++ + USDZ + pybind11

> ⚠️ 完成後發送 iMessage：「Sprint P20 — Part B 完成：USD Generator C++」

```bash
MSG="🏗️ PromptBIM
✅ Sprint P20 — Part B 完成
📋 USD Generator C++ + USDZ 打包完成
🧪 pytest: ${TEST_COUNT}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

#### Task 5: USD Generator C++ 實作
- 新建 `libpromptbim/src/bim/usd_generator.cpp` + `include/promptbim/usd_generator.hpp`
- 使用 pxr:: namespace C++ API 生成 USD 檔案
- C ABI: `pb_generate_usd()` 替換 placeholder stub

#### Task 6: USDZ Packer C++ 實作
- C ABI: `pb_generate_usdz()` — zip 打包 USD + textures
- 替換 placeholder stub

#### Task 7: BIM Engine GoogleTest
- 新建 `libpromptbim/tests/test_bim_engine.cpp`
- 驗證 IFC + USD 輸出與 Python 版一致

#### Task 8: BIM Engine pybind11 binding
- 加入 `bindings/python/bindings.cpp` 的 BIM 綁定
- `_native_bridge.py` 加入 IFC/USD/USDZ fallback 邏輯

---

## 驗收標準

```
☐ IFC Generator C++ 通過 GoogleTest
☐ USD Generator C++ 通過 GoogleTest
☐ USDZ Packer 通過測試
☐ pybind11 binding 可正常呼叫
☐ xcodebuild BUILD SUCCEEDED
☐ pytest >= 883 passed
☐ 全量文件同步完成
☐ Sprint 審計報告已產生 (docs/reports/Sprint20_AuditReport.md)
☐ git tag v2.7.0
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

*PROMPT_P20.md v1.0 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.13.0 ✅ | SKILL.md v3.2 ✅*
