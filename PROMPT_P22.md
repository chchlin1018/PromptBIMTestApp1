# PROMPT_P22.md — Sprint P22: V2 Migration Phase 5 — Web WASM + REST API

> 版本: v1.0 | 建立時間: 2026-03-26
> 前置 Sprint: P21 ✅ 完成（GIS C++ + SwiftUI 3D, 957 tests, v2.8.0）
> 依賴: docs/DesignDocForV2.md, docs/V2_Migration_Tasks.md, CLAUDE.md v1.14.1, SKILL.md v3.2
> 來源: docs/V2_Migration_Tasks.md Phase 5 (V2-070~V2-076)
> 目標版本: v2.9.0
> ℹ️ Windows Qt 6 (V2-060~V2-062) 已移至 Future Features，需要 Windows 環境才能實際 build/test

---

## Sprint 目標

**V2 Migration Phase 5 — Web WASM + REST API + Frontend**，共 **3 個 Part、10 個 Task**：

- Part A: WASM Core — Emscripten build + 引擎編譯（4 Tasks）
- Part B: REST API Backend — FastAPI + AI Service（3 Tasks）
- Part C: Web Frontend — React + Three.js 3D + E2E（3 Tasks）

---

## ⚠️ 第一步：發送啟動通知（在任何 Task 之前必須執行）

> 這是強制性的第一個動作。在讀完必讀文件、完成環境檢查後，必須立即發送以下 iMessage：

```bash
MSG="🏗️ PromptBIM
🚀 Sprint P22 開始執行
📋 Task: 10 項（3 Parts）
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
安裝 Emscripten (emsdk)：如未安裝，執行 `brew install emscripten` 或從 emsdk 官網安裝。

## 必讀文件

1. **CLAUDE.md v1.14.1** — 行為規範（特別注意 20 步執行流程 + 三大領域審計）
2. **docs/DesignDocForV2.md** — V2 架構設計文件
3. **docs/V2_Migration_Tasks.md** — V2 遷移任務拆解（Phase 5）
4. **SKILL.md v3.2** — 專案 SSOT
5. **libpromptbim/** — 現有 C++ 核心（P18-P21 建立）

---

## Part A: WASM Core — Emscripten Build

> ⚠️ 完成後發送 iMessage：

```bash
MSG="🏗️ PromptBIM
✅ Sprint P22 — Part A 完成
📋 WASM Core: Emscripten build + Compliance/Cost/GIS 編譯
🧪 pytest: ${TEST_COUNT}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

#### Task 1: Emscripten Build Setup
- 新建 `libpromptbim/CMakeLists.wasm.txt` 或在現有 CMakeLists.txt 加入 WASM target
- 設定 emscripten toolchain file
- 目標：`emcmake cmake .. && emmake make` 可編譯
- 產出 `promptbim.js` + `promptbim.wasm`

#### Task 2: WASM Compliance + Cost Engine
- Compliance Engine + Cost Engine 編譯為 WASM
- JavaScript binding (Embind 或 cwrap)
- 簡單 HTML 測試頁驗證 WASM 可呼叫

#### Task 3: WASM GIS Engine
- GIS Engine 編譯為 WASM
- GeoJSON 解析在瀏覽器中可運作

#### Task 4: WASM Progressive Loading + Service Worker
- WASM 模組分割（core + gis + bim 懶加載）
- Service Worker 快取 WASM 檔案
- 目標：首次載入 < 5MB，後續快取

---

## Part B: REST API Backend

> ⚠️ 完成後發送 iMessage：

```bash
MSG="🏗️ PromptBIM
✅ Sprint P22 — Part B 完成
📋 REST API: FastAPI + AI Service endpoint
🧪 pytest: ${TEST_COUNT}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

#### Task 5: FastAPI Backend Skeleton
- 新建 `web/api/` 目錄
- FastAPI app + CORS + health endpoint
- Docker compose 設定（選用）

#### Task 6: AI Service Endpoint
- `/api/generate` — 接收 prompt + land GeoJSON，回傳 BuildingPlan JSON
- 內部呼叫 Orchestrator.agenerate()
- SSE streaming 回傳進度（Enhancing... Planning... Building... Done）

#### Task 7: API Tests
- pytest + httpx AsyncClient 測試
- Mock Claude API，驗證完整 pipeline

---

## Part C: Web Frontend

> ⚠️ 完成後發送 iMessage：

```bash
MSG="🏗️ PromptBIM
✅ Sprint P22 — Part C 完成
📋 Web Frontend: React + Three.js 3D + E2E
🧪 pytest: ${TEST_COUNT}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

#### Task 8: React Frontend Skeleton
- 新建 `web/frontend/` — Vite + React + TypeScript
- 主頁面佈局：左側土地資訊 + 中央 3D 視圖 + 底部 Chat
- 接入 WASM 模組（Compliance check 在瀏覽器端執行）

#### Task 9: Three.js 3D Viewer
- Three.js 場景：載入 .usda/.gltf 模型
- 軌道控制器（旋轉/縮放/平移）
- 地板 + 光源 + 樓層切換

#### Task 10: Web E2E 測試
- Playwright 或 Cypress E2E
- 測試流程：開啟頁面 → 輸入 prompt → API 呼叫 → 3D 模型顯示

---

## Future Features（未納入本 Sprint）

| 功能 | 原始任務 | 原因 | 建議 Sprint |
|------|----------|------|:-----------:|
| Windows Qt 6 骨架 | V2-060 | 需要 Windows 環境 build/test | P23+ |
| Windows Qt 6 主視窗 + 3D | V2-061 | 需要 Windows 環境 | P23+ |
| Windows Qt 6 AI 整合 | V2-062 | 需要 Windows 環境 | P23+ |

---

## 驗收標準

```
☐ WASM 編譯成功（promptbim.js + promptbim.wasm）
☐ WASM Compliance/Cost/GIS 在瀏覽器中可呼叫
☐ Service Worker 快取 WASM
☐ FastAPI /api/generate endpoint 可運作
☐ SSE streaming 進度回傳
☐ React + Three.js 3D viewer 可顯示模型
☐ Web E2E 測試通過
☐ xcodebuild BUILD SUCCEEDED
☐ Xcode pbxproj 完整性檢查通過
☐ pytest >= 957 passed
☐ 全量文件同步完成
☐ Sprint 審計報告已產生 (docs/reports/Sprint22_AuditReport.md)
☐ 審計: 代碼 + 文檔 8/8 + Xcode 8/8
☐ git tag v2.9.0
☐ iMessage 已發送（啟動 + Part A + Part B + Part C + 審計 + Git 推送 + 最終完成）
```

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保 Swift 檔案、Build Phase、Signing 設定正確。
⚠️ iMessage 通知必須發送（啟動 + 每個 Part 完成 + 審計 + Git 推送 + 最終完成）。
⚠️ Sprint 完成後必須產生自我審計報告（代碼 + 文檔 8/8 + Xcode 8/8）。
⚠️ 不得修改 CLAUDE.md / SKILL.md（人工維護文件）。
⚠️ 如果 Emscripten 未安裝，自行安裝（`brew install emscripten` 或 emsdk）。
⚠️ Web frontend 使用 Vite + React + TypeScript，不使用 Next.js。

---

*PROMPT_P22.md v1.0 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.14.1 ✅ | SKILL.md v3.2 ✅ | Windows Qt 6 移至 Future Features*
