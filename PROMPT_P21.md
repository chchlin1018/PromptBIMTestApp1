# PROMPT_P21.md — Sprint P21: V2 Migration Phase 4 — GIS Engine C++ + macOS SwiftUI 3D

> 版本: v1.0 | 建立時間: 2026-03-26
> 前置 Sprint: P20 ✅ 完成（BIM Core IFC + USD C++, 930 tests, v2.7.0）
> 依賴: docs/DesignDocForV2.md, docs/V2_Migration_Tasks.md, CLAUDE.md v1.14.1, SKILL.md
> 來源: docs/V2_Migration_Tasks.md Phase 4 (V2-040~V2-051)
> 目標版本: v2.8.0

---

## Sprint 目標

**V2 Migration Phase 4 — GIS Engine C++ + macOS SwiftUI 3D**，共 **2 個 Part、8 個 Task**：

- Part A: GIS Engine C++ 遷移（4 Tasks）
- Part B: macOS SwiftUI 3D Preview + libpromptbim 直接呼叫（4 Tasks）

---

## ⚠️ 第一步：發送啟動通知（在任何 Task 之前必須執行）

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

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。
確認 `git pull origin main` 為最新。

## 必讀文件

1. **docs/DesignDocForV2.md** — V2 架構設計文件
2. **docs/V2_Migration_Tasks.md** — V2 遷移任務拆解（Phase 4）
3. **SKILL.md v3.2** — 專案 SSOT
4. **CLAUDE.md v1.14.1** — 行為規範

---

## Part A: GIS Engine C++ 遷移

> ⚠️ 完成後發送 iMessage：「Sprint P21 — Part A 完成：GIS Engine C++」

#### Task 1: GIS Engine C++ — GDAL/OGR 整合
- 評估 GDAL C++ API 可用性 (或直接解析 GeoJSON/Shapefile)
- 新建 `libpromptbim/src/gis/gis_engine.cpp` + `include/promptbim/gis_engine.hpp`

#### Task 2: GIS Engine — 幾何運算
- GEOS 或自行實作 setback/buffer
- 座標投影 (WGS84 → TWD97)

#### Task 3: GIS Engine GoogleTest
- 新建 `libpromptbim/tests/test_gis_engine.cpp`

#### Task 4: GIS Engine pybind11 + fallback
- 更新 `bindings.cpp` 和 `_native_bridge.py`

---

## Part B: macOS SwiftUI 3D Preview

> ⚠️ 完成後發送 iMessage：「Sprint P21 — Part B 完成：SwiftUI 3D Preview」

#### Task 5: SceneKit 3D Preview
- 新增 `SceneKitView.swift` — SceneKit 嵌入 SwiftUI

#### Task 6: libpromptbim Swift C interop
- Swift 直接呼叫 C ABI (`pb_generate_ifc`, `pb_generate_usd`)

#### Task 7: 3D Model Loading
- 從 .usda 載入 3D 模型到 SceneKit

#### Task 8: UI 整合
- ContentView 新增 3D tab + 生成按鈕

---

## 驗收標準

```
☐ GIS Engine C++ 通過 GoogleTest
☐ Swift 可直接呼叫 C ABI
☐ SceneKit 3D 預覽可用
☐ xcodebuild BUILD SUCCEEDED
☐ pytest >= 930 passed
☐ 全量文件同步完成
☐ Sprint 審計報告已產生 (docs/reports/Sprint21_AuditReport.md)
☐ git tag v2.8.0
☐ iMessage 已發送（啟動 + Part A + Part B + 審計 + 最終完成）
```

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。

---

*PROMPT_P21.md v1.0 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.14.1 ✅ | SKILL.md v3.2 ✅*
