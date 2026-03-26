# PROMPT_P22.md — Senior Audit Full Remediation

> **Sprint:** P22 | **目標版本:** v2.9.0 | **基於:** AuditReport_03261630.md
> **CLAUDE.md:** v1.15.1 | **SKILL.md:** v3.2（唯讀）
> **前置:** P21 完成（v2.8.0, 957 tests, HEAD `fa5a64fc`）
> **範圍:** Part 0 清理 + 5 Critical + 8 High + 12 Medium + 5 Finalization = **36 Tasks / 6 Parts**

---

## 必讀文件

```
1. 本文件 sprints/PROMPT_P22.md ← 最重要
2. docs/audit-reports/AuditReport_Full_v2.8.0.md ← 審計報告（所有 issue ID 來源）
3. SKILL.md ← 專案 SSOT（唯讀，不得修改）
4. CLAUDE.md ← v1.15.1 行為規範（絕對不得修改）
5. TODO.md ← 確認當前狀態
```

---

## ★ 通知規則（本 Sprint 全程適用）★

> ⚠️ **依據 CLAUDE.md v1.15.1，每個 Task 和 Part 完成後都必須 echo + notify。**
> ⚠️ **錯誤發生時立即 echo + notify，不等 3 次失敗。**

### Task 完成通知（每個 Task 結束後必須執行）

```bash
MSG="🏗️ PromptBIM P22
✅ Task ${TASK_NUM}: ${TASK_DESCRIPTION}
📋 ${ISSUE_IDS_FIXED}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Part 完成通知（每個 Part 結束後必須執行）

```bash
MSG="🏗️ PromptBIM P22 Part ${PART} ✅
📋 ${PART_DESCRIPTION} (${TASK_COUNT} tasks)
✅ ${KEY_ACHIEVEMENTS}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### Task 失敗通知（錯誤發生時立即執行）

```bash
MSG="🏗️ PromptBIM P22
⚠️ Task ${TASK_NUM} 失敗: ${ERROR_DESCRIPTION}
🔄 嘗試修復 (${ATTEMPT}/3)...
🔧 修復方式: ${FIX_APPROACH}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

### 中斷通知（3 次修復失敗後執行）

```bash
MSG="🏗️ PromptBIM
❌ Sprint P22 執行中斷
📍 停在: Task ${TASK_NUM} (${TASK_DESCRIPTION})
❗ 原因: ${ERROR_DESCRIPTION}
🔄 已嘗試修復 3 次均失敗
💡 建議: ${SUGGESTED_ACTION}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
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

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "⛔ ANTHROPIC_API_KEY 已設定！"
    MSG="⛔ PromptBIM Sprint 中止 — 偵測到 ANTHROPIC_API_KEY
🔧 修復: unset ANTHROPIC_API_KEY
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
    echo "$MSG"
    notify "$MSG"
    exit 1
fi
echo "✅ 認證: Claude Max 訂閱"

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
🔔 通知: 每 Task + 每 Part + 錯誤即時
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part 0: 專案檔案重整（6 Tasks）

> 依據 CLAUDE.md v1.15.1 新規則，搬遷所有 Sprint Prompt 和 Audit Report。
> ⚠️ **每個 Task 完成後都必須 echo + notify。**

### Task 1: 搬遷所有 Sprint Prompt 到 sprints/
```bash
for f in PROMPT.md PROMPT_P*.md; do
    [ -f "$f" ] && git mv "$f" "sprints/$f" && echo "✅ Moved $f → sprints/$f"
done
```
> 完成後 notify: Task 1: 25 PROMPT files moved to sprints/

### Task 2: 搬遷所有 Audit Report 到 docs/audit-reports/
```bash
cd docs/reports
for f in *AuditReport*.md; do
    [ -f "$f" ] && git mv "$f" ../audit-reports/"$f"
done
cd ../..
[ -f "AuditReport.md" ] && git mv AuditReport.md docs/audit-reports/AuditReport_Legacy_P16.md
# 重命名: AuditReport_03261630.md → AuditReport_Full_v2.8.0.md
```
> 完成後 notify: Task 2: 8 AuditReport files moved to docs/audit-reports/

### Task 3: 清理 docs/reports/ 殘留
> 完成後 notify: Task 3: docs/reports/ cleaned, 6 non-audit files retained

### Task 4: 刪除 sprints/.gitkeep
```bash
git rm sprints/.gitkeep 2>/dev/null || true
```
> 完成後 notify: Task 4: sprints/.gitkeep removed

### Task 5: 驗證檔案結構
```bash
ls sprints/PROMPT_P*.md | wc -l   # 應 >= 25
ls docs/audit-reports/*.md | wc -l # 應 >= 7
ls PROMPT*.md 2>/dev/null && echo "❌ Root 仍有 PROMPT" || echo "✅ Root clean"
```
> 完成後 notify: Task 5: Structure verified — sprints/ N files, audit-reports/ N files

### Task 6: Commit 檔案重整
```bash
git add -A && git commit -m "refactor: project reorganization per CLAUDE.md v1.15.1"
```
> 完成後 notify: Task 6: Reorganization committed

### Part 0 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part 0 ✅
🗂️ 專案檔案重整 (6 tasks)
✅ 25 PROMPT files → sprints/
✅ 8 AuditReport files → docs/audit-reports/
✅ Root 已清理乾淨
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part A: C++ Critical + Robustness Fixes（7 Tasks）

> ⚠️ **每個 Task 完成後都必須 echo + notify。失敗時立即 notify。**

### Task 7: IFC Generator 線程安全 [CRITICAL: IFC-01 + IFC-02]
gmtime() → gmtime_r() + std::mutex 保護。
> 完成後 notify: Task 7: IFC thread safety fixed (IFC-01 + IFC-02) ✅
> 失敗時 notify: Task 7 ⚠️ IFC thread safety — {error} — 嘗試修復...

### Task 8: IFC 輸入驗證 + 溢位保護 [MEDIUM: IFC-03 + IFC-04]
> 完成後 notify: Task 8: IFC input validation (IFC-03 + IFC-04) ✅

### Task 9: CMake Build Hardening [MEDIUM: CMAKE-01~03]
> 完成後 notify: Task 9: CMake hardening (CMAKE-01~03) ✅

### Task 10: GIS Non-Convex Setback [MEDIUM: GIS-01]
> 完成後 notify: Task 10: GIS non-convex setback (GIS-01) ✅

### Task 11: GIS DXF + Shapefile Enhancement [MEDIUM: GIS-02 + GIS-03]
> 完成後 notify: Task 11: GIS DXF/SHP parser (GIS-02 + GIS-03) ✅

### Task 12: C++ GoogleTest [ALL C++ FIXES]
目標: ≥ 15 新增 GoogleTest cases（137 → ≥ 152）。
> 完成後 notify: Task 12: GoogleTest N/152+ passed ✅

### Task 13: NativeBIMBridge dlsym [CRITICAL: SW-05 + SW-06]
> 完成後 notify: Task 13: dlsym null check + pb_version (SW-05 + SW-06) ✅

### Part A 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part A ✅
🔧 C++ Critical + Robustness (7 tasks)
✅ IFC thread safety (mutex + gmtime_r)
✅ IFC input validation (NaN/overflow)
✅ CMake hardening + GIS fixes + dlsym
✅ GoogleTest ≥ 152
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part B: Python Critical + High Fixes（8 Tasks）

> ⚠️ **每個 Task 完成後都必須 echo + notify。**

### Task 14: Cache Store File Locking [CRITICAL: CACHE-01]
> 完成後 notify: Task 14: Cache file locking (CACHE-01) ✅

### Task 15: Orchestrator DI [HIGH: PY-01]
> 完成後 notify: Task 15: Orchestrator DI (PY-01) ✅

### Task 16: Async Builder Non-Blocking [HIGH: PY-02]
> 完成後 notify: Task 16: Async non-blocking (PY-02) ✅

### Task 17: Constraint Dedup + API Key [MEDIUM: PY-03 + PY-04]
> 完成後 notify: Task 17: Constraint dedup + API key (PY-03 + PY-04) ✅

### Task 18: Config validate_api_key [MEDIUM: CFG-01]
> 完成後 notify: Task 18: validate_api_key fix (CFG-01) ✅

### Task 19: Cost Missing Category [HIGH: COST-01]
> 完成後 notify: Task 19: Cost missing category (COST-01) ✅

### Task 20: MEP Grid + Registry [HIGH: MEP-01 + MEP-02]
> 完成後 notify: Task 20: MEP grid + registry (MEP-01 + MEP-02) ✅

### Task 21: Python Tests for Part B
目標: ≥ 20 新增 pytest cases（820 → ≥ 840）。
> 完成後 notify: Task 21: pytest N/840+ passed ✅

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

## Part C: Swift Fixes + XCTest（5 Tasks）

> ⚠️ **每個 Task 完成後都必須 echo + notify。**

### Task 22: PythonBridge Timeout + Termination [HIGH: SW-01 + SW-02]
> 完成後 notify: Task 22: PythonBridge timeout + termination (SW-01 + SW-02) ✅

### Task 23: PythonBridge Stderr + Path [MEDIUM: SW-03 + SW-04]
> 完成後 notify: Task 23: PythonBridge stderr + path (SW-03 + SW-04) ✅

### Task 24: BIMSceneBuilder.swift 獨立檔案
> ⚠️ **新增 Swift 檔案必須加入 pbxproj Compile Sources！**
> 完成後 notify: Task 24: BIMSceneBuilder.swift extracted + added to pbxproj ✅

### Task 25: Cross-Layer PBResult Error Propagation
> 完成後 notify: Task 25: PBResult struct implemented ✅

### Task 26: Swift XCTest Suite [CRITICAL: SW-07]
目標: ≥ 15 XCTest cases。
> ⚠️ **XCTest target + 檔案都必須加入 xcodeproj。**
> 完成後 notify: Task 26: XCTest N/15+ cases created (SW-07) ✅

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

> ⚠️ **每個 Task 完成後都必須 echo + notify。**

### Task 27: Monitoring Sensor-Space Validation [MEDIUM: MON-01]
> 完成後 notify: Task 27: Sensor-space validation (MON-01) ✅

### Task 28: Simulation Enum Classification [MEDIUM: SIM-01]
> 完成後 notify: Task 28: Enum classification (SIM-01) ✅

### Task 29: Orchestrator Encapsulation [LOW: PY-05 + PY-06]
> 完成後 notify: Task 29: Orchestrator encapsulation (PY-05 + PY-06) ✅

### Task 30: pybind11 .pyi Type Stubs
> 完成後 notify: Task 30: .pyi type stubs created ✅

### Task 31: Plugin System Activation [HIGH: PLG-01]
> 完成後 notify: Task 31: Plugin system activated (PLG-01) ✅

### Part D 完成通知

```bash
MSG="🏗️ PromptBIM P22 Part D ✅
🔌 Subsystem Fixes (5 tasks)
✅ Sensor validation + Enum + Plugin activation + .pyi stubs
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## Part E: Build Verification + Documentation + Finalization（5 Tasks）

> ⚠️ **每個 Task 完成後都必須 echo + notify。**

### Task 32: Context Prompt Update
> 完成後 notify: Task 32: Context Prompt updated to v2.9.0 ✅

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
> 完成後 notify: Task 33: Doc sync 8/8 — all version = 2.9.0 ✅

### Task 34: Build + Test Verification
> 完成後 notify: Task 34: Build OK — GoogleTest N + pytest N + XCTest N ✅
> 失敗時 notify: Task 34 ⚠️ Build failed — {error} — 嘗試修復...

### Task 35: Self-Audit Report
產生 `docs/audit-reports/Sprint22_AuditReport.md`。
> 完成後 notify: Task 35: Audit report — Code {grade} / Docs {N}/8 / Xcode {N}/8 ✅

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
> 完成後 notify: Task 36: Git pushed + tagged v2.9.0 ✅

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

## ★ Sprint 最終完成通知 ★

```bash
MSG="🏗️ PromptBIM Sprint P22 完成 🎉
📋 Senior Audit Full Remediation
🏷️ v2.9.0 | 36 Tasks / 6 Parts
🧪 GoogleTest ≥152 + pytest ≥840 + XCTest ≥15
🔧 Fixed: 5 Critical + 8 High + 12 Medium
📊 Audit: Code {grade} / Docs {N}/8 / Xcode {N}/8
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## 執行指令

1. **全量文件同步：** 8 項逐一驗證
2. **pbxproj 完整性：** 6 Swift 檔案（含 BIMSceneBuilder.swift）都在 Compile Sources
3. **每個 Task 完成 → echo + notify**（36 次 Task 通知）
4. **每個 Part 完成 → echo + notify**（6 次 Part 通知）
5. **錯誤發生 → 立即 echo + notify**（含錯誤描述 + 嘗試修復方式）
6. **修復嘗試 → 每次 echo + notify**（含嘗試次數）
7. **3 次修復失敗 → echo + notify 中斷通知**（含建議）
8. **審計報告存放:** `docs/audit-reports/Sprint22_AuditReport.md`
9. **不得修改 CLAUDE.md** — 絕對禁止
10. **不得修改 SKILL.md** — 唯讀
11. **不得中途詢問用戶**
12. **Part 0 的 git mv 必須先執行**，後續 Part 才開始修改代碼

---

## 通知覆蓋率總計

| 類型 | 次數 | 說明 |
|------|------|------|
| 啟動通知 | 1 | Sprint 開始 |
| Task 完成 | 36 | 每個 Task 結束 |
| Part 完成 | 6 | 每個 Part 結束 |
| Git 推送 | 1 | 含 commit hash |
| 最終完成 | 1 | Sprint 結束 |
| 錯誤 (按需) | N | 每次失敗立即 |
| 修復嘗試 (按需) | N | 每次嘗試 |
| **最低通知數** | **45** | 不含錯誤/修復 |

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
☐ 每個 Task 都有 echo + notify（36 次）
☐ 每個 Part 都有 echo + notify（6 次）
☐ 錯誤和修復都有 echo + notify
☐ 最終完成通知已發送
```

---

*sprints/PROMPT_P22.md v2.1 | 2026-03-26 | CLAUDE.md v1.15.1 合規 ✅*
*通知覆蓋率: 45+ 次（36 Tasks + 6 Parts + 啟動 + Git + 最終 + 錯誤即時）*
