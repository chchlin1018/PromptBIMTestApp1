# PROMPT_P21.md — Sprint P21: V2 Migration Phase 4 — GIS Engine C++ + macOS SwiftUI 3D

> 版本: v1.1 | 建立時間: 2026-03-26 | 修正: 合規性修復（執行指令 + pbxproj + Swift 檔案提醒）
> 前置 Sprint: P20 ✅ 完成（BIM Core IFC + USD C++, 930 tests, v2.7.0）
> 依賴: docs/DesignDocForV2.md, docs/V2_Migration_Tasks.md, CLAUDE.md v1.14.1, SKILL.md v3.2
> 來源: docs/V2_Migration_Tasks.md Phase 4 (V2-040~V2-051)
> 目標版本: v2.8.0

---

## Sprint 目標

**V2 Migration Phase 4 — GIS Engine C++ + macOS SwiftUI 3D**，共 **2 個 Part、8 個 Task**：

- Part A: GIS Engine C++ 遷移（4 Tasks）
- Part B: macOS SwiftUI 3D Preview + libpromptbim 直接呼叫（4 Tasks）

---

## ⚠️ 第一步：發送啟動通知（在任何 Task 之前必須執行）

> 這是強制性的第一個動作。在讀完必讀文件、完成環境檢查後，必須立即發送以下 iMessage：

```bash
MSG="🏗️ PromptBIM
🚀 Sprint P21 開始執行
📋 Task: 8 項（2 Parts）
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

**確認通知已發送後，才能繼續執行 Part A。**

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本（**含 API Key 衝突檢查**）。
確認 conda env `promptbim` 存在。
確認 `git pull origin main` 為最新。

## 必讀文件

1. **CLAUDE.md v1.14.1** — 行為規範（特別注意 20 步執行流程 + 三大領域審計）
2. **docs/DesignDocForV2.md** — V2 架構設計文件
3. **docs/V2_Migration_Tasks.md** — V2 遷移任務拆解（Phase 4）
4. **SKILL.md v3.2** — 專案 SSOT

---

## Part A: GIS Engine C++ 遷移

> ⚠️ 完成後發送 iMessage：

```bash
MSG="🏗️ PromptBIM
✅ Sprint P21 — Part A 完成
📋 GIS Engine C++ 遷移完成
🧪 pytest: ${TEST_COUNT}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

#### Task 1: GIS Engine C++ — GDAL/OGR 整合
- 評估 GDAL C++ API 可用性（或直接解析 GeoJSON/Shapefile）
- 新建 `libpromptbim/src/gis/gis_engine.cpp` + `include/promptbim/gis_engine.hpp`
- C ABI: `pb_parse_land()` + `pb_free_string()`

#### Task 2: GIS Engine — 幾何運算
- GEOS 或自行實作 setback/buffer
- 座標投影（WGS84 → TWD97）

#### Task 3: GIS Engine GoogleTest
- 新建 `libpromptbim/tests/test_gis_engine.cpp`
- 涵蓋：GeoJSON 解析、Shapefile 解析、setback 計算、座標投影

#### Task 4: GIS Engine pybind11 + fallback
- 更新 `bindings/python/bindings.cpp` 和 `_native_bridge.py`

---

## Part B: macOS SwiftUI 3D Preview

> ⚠️ 完成後發送 iMessage：

```bash
MSG="🏗️ PromptBIM
✅ Sprint P21 — Part B 完成
📋 SwiftUI 3D Preview + libpromptbim C interop
🧪 pytest: ${TEST_COUNT}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

> ⚠️ **本 Part 會新增 Swift 檔案（SceneKitView.swift 等），必須加入 pbxproj Compile Sources build phase。**

#### Task 5: SceneKit 3D Preview
- 新增 `PromptBIMTestApp1/SceneKitView.swift` — SceneKit 嵌入 SwiftUI
- **⚠️ 必須加入 pbxproj Compile Sources**

#### Task 6: libpromptbim Swift C interop
- Swift 直接呼叫 C ABI（`pb_generate_ifc`, `pb_generate_usd`）
- 可能需要新增 Bridging Header 或直接 import C module

#### Task 7: 3D Model Loading
- 從 .usda 載入 3D 模型到 SceneKit

#### Task 8: UI 整合
- ContentView 新增 3D tab + 生成按鈕
- **⚠️ 所有新增的 .swift 檔案都必須在 pbxproj 中正確引用**

---

## 驗收標準

```
☐ GIS Engine C++ 通過 GoogleTest
☐ Swift 可直接呼叫 C ABI
☐ SceneKit 3D 預覽可用
☐ xcodebuild BUILD SUCCEEDED
☐ Xcode pbxproj 完整性檢查通過（所有新增 Swift 檔案已加入 Compile Sources）
☐ Info.plist CFBundleShortVersionString = 2.8.0, CFBundleVersion = 21
☐ pytest >= 930 passed
☐ 全量文件同步完成
☐ Sprint 審計報告已產生 (docs/reports/Sprint21_AuditReport.md)
☐ 審計: 代碼 + 文檔 8/8 + Xcode 8/8
☐ git tag v2.8.0
☐ iMessage 已發送（啟動 + Part A + Part B + 審計 + Git 推送 + 最終完成）
```

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保所有新增 Swift 檔案（SceneKitView.swift 等）已加入 Compile Sources build phase。
⚠️ iMessage 通知必須發送（啟動 + 每個 Part 完成 + 審計 + Git 推送 + 最終完成）。
⚠️ Sprint 完成後必須產生自我審計報告（代碼 + 文檔 8/8 + Xcode 8/8）。
⚠️ 本 Sprint 會新增 Swift 檔案，pbxproj 完整性檢查特別重要。
⚠️ 不得修改 CLAUDE.md / SKILL.md（人工維護文件）。

---

*PROMPT_P21.md v1.1 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.14.1 ✅ | SKILL.md v3.2 ✅*
