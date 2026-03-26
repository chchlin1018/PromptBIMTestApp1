# PROMPT_P22.md — Senior Audit Full Remediation

> **Sprint:** P22 | **目標版本:** v2.9.0 | **基於:** AuditReport_03261630.md
> **CLAUDE.md:** v1.15.0 | **SKILL.md:** v3.2（唯讀）
> **前置:** P21 完成（v2.8.0, 957 tests, HEAD `fa5a64fc`）
> **範圍:** Part 0 清理 + 5 Critical + 8 High + 12 Medium + 5 Finalization = **36 Tasks / 6 Parts**

---

## 必讀文件

```
1. 本文件 sprints/PROMPT_P22.md ← 最重要
2. docs/audit-reports/AuditReport_Full_v2.8.0.md ← 審計報告（所有 issue ID 來源）
3. SKILL.md ← 專案 SSOT（唯讀，不得修改）
4. CLAUDE.md ← v1.15.0 行為規範（絕對不得修改）
5. TODO.md ← 確認當前狀態
```

---

## 環境檢查（Sprint 開始前必須執行）

```bash
echo "========================================"
echo "🖥️  環境檢查 — $(hostname)"
echo "========================================"
echo "Hostname: $(hostname)"
echo "macOS: $(sw_vers -productVersion)"
echo "Git: $(git --version 2>/dev/null || echo '❌')"
echo "Xcode: $(xcodebuild -version 2>/dev/null | head -1 || echo '❌')"
echo "Python: $(python3 --version 2>/dev/null || echo '❌')"
echo "Conda: $(conda --version 2>/dev/null || echo '❌')"

# ★ API Key 衝突檢查 ★
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "⛔ ANTHROPIC_API_KEY 已設定！會走 API 計費而非 Max 訂閱"
    MSG="⛔ PromptBIM Sprint 中止 — 偵測到 ANTHROPIC_API_KEY
🔧 修復: unset ANTHROPIC_API_KEY
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
    echo "$MSG"
    notify "$MSG"
    exit 1
fi
echo "✅ 認證: Claude Max 訂閱（無 API Key 衝突）"

git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then echo "✅ 本地與遠端同步"
else echo "⚠️ 執行 git pull..."; git pull origin main; fi
```

---

## ★ 啟動通知（必須在 Part 0 之前執行）★

```bash
MSG="🏗️ PromptBIM Sprint P22 啟動
📋 Senior Audit Full Remediation
🎯 36 Tasks / 6 Parts → v2.9.0
📊 Part 0: 專案清理 + 5 Critical + 8 High + 12 Medium
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part 0: 專案檔案重整（6 Tasks）

> ⚠️ 依據 CLAUDE.md v1.15.0 新規則，將所有 Sprint Prompt 和 Audit Report 搬遷到正確位置。

### Task 1: 搬遷所有 Sprint Prompt 到 sprints/

將根目錄的所有 PROMPT 檔案移動到 `sprints/` 資料夾：

```bash
# 搬遷所有根目錄的 PROMPT 檔案
for f in PROMPT.md PROMPT_P*.md; do
    if [ -f "$f" ]; then
        git mv "$f" "sprints/$f"
        echo "✅ Moved $f → sprints/$f"
    fi
done
```

預期搬遷清單（25 檔）：
- `PROMPT.md` → `sprints/PROMPT.md`
- `PROMPT_P0.md` → `sprints/PROMPT_P0.md`
- `PROMPT_P2.md`, `PROMPT_P2.5.md` → `sprints/`
- `PROMPT_P3.md` ~ `PROMPT_P9.md` → `sprints/`
- `PROMPT_P10.md`, `PROMPT_P10.2.md`, `PROMPT_P10.3.md` → `sprints/`
- `PROMPT_P11.md` ~ `PROMPT_P22.md`（含 P17.1, P17.2）→ `sprints/`

> 注意: `sprints/PROMPT_P22.md` 已由本次 push 建立，root `PROMPT_P22.md` 是舊版，直接 `git rm` 即可。

### Task 2: 搬遷所有 Audit Report 到 docs/audit-reports/

```bash
# 從 docs/reports/ 搬遷所有 AuditReport
cd docs/reports
for f in *AuditReport*.md; do
    if [ -f "$f" ]; then
        git mv "$f" ../audit-reports/"$f"
        echo "✅ Moved docs/reports/$f → docs/audit-reports/$f"
    fi
done
cd ../..

# 搬遷根目錄的 AuditReport.md
if [ -f "AuditReport.md" ]; then
    git mv AuditReport.md docs/audit-reports/AuditReport_Legacy_P16.md
    echo "✅ Moved AuditReport.md → docs/audit-reports/AuditReport_Legacy_P16.md"
fi
```

搬遷清單：
- `docs/reports/Sprint17_AuditReport.md` → `docs/audit-reports/Sprint17_AuditReport.md`
- `docs/reports/Sprint17.1_AuditReport.md` → `docs/audit-reports/Sprint17.1_AuditReport.md`
- `docs/reports/Sprint18_AuditReport.md` → `docs/audit-reports/Sprint18_AuditReport.md`
- `docs/reports/Sprint19_AuditReport.md` → `docs/audit-reports/Sprint19_AuditReport.md`
- `docs/reports/Sprint20_AuditReport.md` → `docs/audit-reports/Sprint20_AuditReport.md`
- `docs/reports/Sprint21_AuditReport.md` → `docs/audit-reports/Sprint21_AuditReport.md`
- `docs/reports/AuditReport_03261630.md` → `docs/audit-reports/AuditReport_Full_v2.8.0.md`（重命名為有意義的名稱）
- `AuditReport.md`（根目錄）→ `docs/audit-reports/AuditReport_Legacy_P16.md`

### Task 3: 清理 docs/reports/ 殘留

確認 `docs/reports/` 只剩非審計文件：
- `Full_Codebase_Quality_Report.md` ← 保留
- `P11_Quality_Analysis_Report.md` ← 保留
- `P14_Quality_Analysis_Report.md` ← 保留
- `P16_Quality_Analysis_Report.md` ← 保留
- `REPORT_V1.0.0.md` ← 保留
- `V2_Performance_Comparison.md` ← 保留

### Task 4: 刪除 sprints/.gitkeep

`sprints/` 目錄現在有實際檔案了，刪除佔位用的 `.gitkeep`：
```bash
git rm sprints/.gitkeep 2>/dev/null || true
```

### Task 5: 驗證檔案結構

```bash
echo "=== sprints/ ==="
ls -la sprints/
echo "=== docs/audit-reports/ ==="
ls -la docs/audit-reports/
echo "=== Root PROMPT files (should be empty) ==="
ls PROMPT*.md 2>/dev/null || echo "✅ No PROMPT files in root"
echo "=== Root AuditReport (should be empty) ==="
ls AuditReport.md 2>/dev/null || echo "✅ No AuditReport in root"
```

### Task 6: Commit 檔案重整

```bash
git add -A
git commit -m "refactor: project reorganization — move PROMPTs to sprints/, AuditReports to docs/audit-reports/

Per CLAUDE.md v1.15.0:
- 25 PROMPT files moved from root to sprints/
- 7 AuditReport files moved to docs/audit-reports/
- AuditReport_03261630.md renamed to AuditReport_Full_v2.8.0.md
- Root AuditReport.md renamed to AuditReport_Legacy_P16.md
- sprints/.gitkeep removed (directory now has real files)"
```

### Part 0 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part 0 ✅
🗂️ 專案檔案重整 (6 tasks)
✅ 25 PROMPT files → sprints/
✅ 7 AuditReport files → docs/audit-reports/
✅ Root 已清理乾淨
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part A: C++ Critical + Robustness Fixes（7 Tasks）

> 修復 IFC 線程安全（IFC-01, IFC-02）、輸入驗證（IFC-03, IFC-04）、CMake 強化（CMAKE-01~03）、GIS 修復（GIS-01, GIS-02, GIS-03）

### Task 7: IFC Generator 線程安全 [CRITICAL: IFC-01 + IFC-02]

**IFC-01:** `ifc_generator.cpp` 中 `gmtime()` 回傳 static buffer，非 thread-safe。
- 替換為 `gmtime_r()`（POSIX）或 `gmtime_s()`（Windows），用 `#ifdef` 分平台

**IFC-02:** `IFCGenerator` 有 `next_id_` + `entities_` 成員狀態，並行呼叫會損壞。
- 方案 A（推薦）：加 `std::mutex` 保護 `generate_ifc_string()` 整體
- 方案 B：改為每次呼叫建立新實例（thread-local pattern）

**修改檔案:** `libpromptbim/src/bim/ifc_generator.cpp`, `libpromptbim/include/promptbim/ifc_generator.hpp`

### Task 8: IFC 輸入驗證 + 溢位保護 [MEDIUM: IFC-03 + IFC-04]

**IFC-03:** `next_id_` 無整數溢位保護。加 `if (next_id_ >= INT32_MAX) throw`。
**IFC-04:** 座標無 NaN/infinity 驗證。在 `add_wall()`, `add_slab()` 入口加 `std::isfinite()` 檢查。

### Task 9: CMake Build Hardening [MEDIUM: CMAKE-01 + CMAKE-02 + CMAKE-03]

加編譯器安全旗標 (`-fstack-protector-strong`, `-D_FORTIFY_SOURCE=2`)、symbol visibility 控制、sanitizer 開發模式。

**修改檔案:** `libpromptbim/CMakeLists.txt`

### Task 10: GIS Non-Convex Setback Fix [MEDIUM: GIS-01]

以重心收縮計算 setback 遇非凸多邊形會自交。實作邊法線平移近似或凸性檢測 + fallback。

### Task 11: GIS DXF + Shapefile Parser 增強 [MEDIUM: GIS-02 + GIS-03 + P21 技術債]

DXF 增加 POLYLINE + ARC + CIRCLE + Z 座標。Shapefile 改為讀取所有 polygon。

### Task 12: C++ 新增 GoogleTest [ALL C++ FIXES]

為 Task 7-11 新增 ≥ 15 GoogleTest cases（137 → ≥ 152）。

### Task 13: NativeBIMBridge dlsym Null Check [CRITICAL: SW-05 + SW-06]

`dlsym()` 回傳值做 null check + 加 `pb_version()` 版本比對。

**修改檔案:** `PromptBIMTestApp1/NativeBIMBridge.swift`, `libpromptbim/include/promptbim/promptbim.h`

### Part A 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part A ✅
🔧 C++ Critical + Robustness (7 tasks)
✅ IFC thread safety + input validation
✅ CMake hardening + GIS fixes
✅ NativeBIMBridge dlsym + version check
✅ GoogleTest ≥ 152
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part B: Python Critical + High Fixes（8 Tasks）

### Task 14: Cache Store File Locking [CRITICAL: CACHE-01]
使用 `fcntl.flock()` 加排他鎖。

### Task 15: Orchestrator Dependency Injection [HIGH: PY-01]
Constructor 接受 optional agent 參數。

### Task 16: Async Builder Non-Blocking [HIGH: PY-02]
`await asyncio.to_thread(self._builder.build, self.plan)`

### Task 17: Constraint Dedup + API Key Early Validation [MEDIUM: PY-03 + PY-04]

### Task 18: Config validate_api_key Fix [MEDIUM: CFG-01]
空字串 → False。

### Task 19: Cost Estimator Missing Category Error [HIGH: COST-01]
log warning + `unpriced_categories` 清單。

### Task 20: MEP Configurable Grid + System Registry [HIGH: MEP-01 + MEP-02]
grid_size 參數化 + MEPSystemRegistry class。

### Task 21: Python Tests for Part B
新增 ≥ 20 pytest cases（820 → ≥ 840）。

### Part B 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part B ✅
🐍 Python Critical + High (8 tasks)
✅ Cache locking + Orchestrator DI + async
✅ Cost + MEP + Config fixes
✅ pytest ≥ 840
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part C: Swift Fixes + XCTest [CRITICAL: SW-07]（5 Tasks）

### Task 22: PythonBridge Timeout + Termination [HIGH: SW-01 + SW-02]
30s timeout + defer pattern for termination pairing。

### Task 23: PythonBridge Stderr + Path [MEDIUM: SW-03 + SW-04]
stdout/stderr 分 Pipe + 簡化路徑偵測。

### Task 24: BIMSceneBuilder.swift 獨立檔案 [Context Prompt 不一致]
從 SceneKitView.swift 提取為獨立檔案。
> ⚠️ **新增 Swift 檔案必須加入 pbxproj Compile Sources build phase！**

### Task 25: Cross-Layer PBResult Error Propagation [MEDIUM]
定義 `PBResult` struct（code + data），更新 C++ + Swift 端。

### Task 26: Swift XCTest Suite [CRITICAL: SW-07]
建立 XCTest target + ≥ 15 test cases。
> ⚠️ **XCTest target + 檔案都必須加入 xcodeproj。**

### Part C 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part C ✅
🍎 Swift Fixes + XCTest (5 tasks)
✅ PythonBridge + BIMSceneBuilder + PBResult
✅ XCTest ≥ 15 cases
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part D: Subsystem Fixes（5 Tasks）

### Task 27: Monitoring Sensor-Space Validation [MEDIUM: MON-01]
### Task 28: Simulation Enum Classification [MEDIUM: SIM-01]
### Task 29: Orchestrator Encapsulation + Callback Typing [LOW: PY-05 + PY-06]
### Task 30: pybind11 .pyi Type Stubs [MEDIUM]
### Task 31: Plugin System Activation [HIGH: PLG-01]

### Part D 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part D ✅
🔌 Subsystem Fixes (5 tasks)
✅ Sensor validation + Enum + Plugin activation
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part E: Build Verification + Documentation + Finalization（5 Tasks）

### Task 32: Context Prompt Update
Swift 源碼表 6 檔案 + P22 + v2.9.0 + 測試數。

### Task 33: Full Document Sync（8 項逐一驗證）

```
☐ TODO.md — P22 ✅ + v2.9.0
☐ CHANGELOG.md — v2.9.0 條目
☐ README.md — 測試數 + v2.9.0
☐ docs/PromptBIM_Context_Prompt.md — Sprint P22 + v2.9.0
☐ pyproject.toml — version = "2.9.0"
☐ src/promptbim/__init__.py — __version__ = "2.9.0"
☐ Info.plist — 2.9.0 / 22
☐ SKILL.md — 唯讀，不修改
```

### Task 34: Build + Test Verification
GoogleTest ≥ 152 + pytest ≥ 840 + XCTest ≥ 15 + xcodebuild BUILD SUCCEEDED

### Task 35: Self-Audit Report
產生 `docs/audit-reports/Sprint22_AuditReport.md`。

### Task 36: Git Commit + Push + Tag

```bash
git add -A
git commit -m "[P22] Senior Audit Full Remediation — 36 tasks, v2.9.0

Part 0: Project reorganization (sprints/ + docs/audit-reports/)
Part A: C++ Critical (IFC thread safety, CMake, GIS, dlsym)
Part B: Python Critical+High (Cache, DI, async, MEP registry)
Part C: Swift (timeout, BIMSceneBuilder, PBResult, XCTest)
Part D: Subsystem (sensor, enum, plugin)
Part E: Documentation + verification

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"

git push origin main
git tag -a v2.9.0 -m "v2.9.0 — Senior Audit Full Remediation (P22)"
git push origin v2.9.0
```

### Part E 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part E ✅
📦 Finalization (5 tasks)
✅ Docs 8/8 + Build verified + Tagged v2.9.0
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## 執行指令

1. **全量文件同步：** 8 項逐一驗證
2. **pbxproj 完整性：** 6 Swift 檔案（含 BIMSceneBuilder.swift）都在 Compile Sources
3. **iMessage 通知：** 啟動 + 6 Parts + Git + 最終 = 至少 9 次 notify
4. **所有 notify 必須搭配 echo**
5. **審計報告存放:** `docs/audit-reports/Sprint22_AuditReport.md`
6. **不得修改 CLAUDE.md** — 絕對禁止
7. **不得修改 SKILL.md** — 唯讀
8. **不得中途詢問用戶**
9. **遇到錯誤自行修復** — 3 次仍失敗才發送中斷通知
10. **Part 0 的 git mv 必須先執行**，後續 Part 才開始修改代碼

---

## 驗收標準

```
☐ Part 0: 根目錄無 PROMPT*.md / AuditReport.md 殘留
☐ Part 0: sprints/ 有 25+ 個 PROMPT 檔案
☐ Part 0: docs/audit-reports/ 有 7+ 個 AuditReport 檔案
☐ xcodebuild BUILD SUCCEEDED
☐ pbxproj 8/8（含 BIMSceneBuilder.swift）
☐ GoogleTest ≥ 152
☐ pytest ≥ 840
☐ XCTest ≥ 15
☐ 5 Critical issues 全修
☐ 8 High issues 全修
☐ Info.plist: 2.9.0 / 22
☐ 6 處版本一致
☐ docs/audit-reports/Sprint22_AuditReport.md 產生
☐ git tag v2.9.0
☐ iMessage（啟動 + 6 Parts + Git + 最終）
```

---

*sprints/PROMPT_P22.md v2.0 | 2026-03-26 | CLAUDE.md v1.15.0 合規 ✅*
