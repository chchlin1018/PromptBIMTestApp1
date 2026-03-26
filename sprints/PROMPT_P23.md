# PROMPT_P23.md — Audit Fixes + GUI Polish + MCP Server + Voice Input

> **Sprint:** P23 | **目標版本:** v2.10.0 | **基於:** AuditReport_03261945 + P22.1 (v2.9.1)
> **CLAUDE.md:** v1.17.0 | **SKILL.md:** v3.3（唯讀）
> **前置:** P22.1 完成（v2.9.1, ~1012 tests）
> **範圍:** 7 Parts / 35 Tasks — Tier0 緊急修復 + Tier1 安全+品質 + GUI + MCP + Voice + 效能 + 驗收
> **審計來源:** AuditReport_03261945.md（32 issues: 3 Critical + 8 High + 12 Medium + 9 Low）

---

## ★★★ 絕對第一步：定義 notify 函數 + 發送啟動通知 ★★★

> ⚠️ Claude Code `-p` 模式不載入 `.zshrc`，notify 函數不存在，必須顯式定義。
> ⚠️ 主要收件人: `+886972535899`（手機號碼，最優先）

```bash
# ===== ★★★ Sprint 絕對第一步：定義 notify 函數 ★★★ =====
notify() {
    local msg="$1"
    osascript -e "
        tell application \"Messages\"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant \"+886972535899\" of targetService
            send \"$msg\" to targetBuddy
        end tell
    " 2>/dev/null || \
    osascript -e "
        tell application \"Messages\"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant \"chchlin1018@icloud.com\" of targetService
            send \"$msg\" to targetBuddy
        end tell
    " 2>/dev/null || \
    osascript -e "display notification \"$msg\" with title \"PromptBIM\"" 2>/dev/null || \
    echo "[NOTIFY FALLBACK] $msg"
}
echo "✅ notify 函數已定義"

TASK_TOTAL=35
PART_TOTAL=7
TASK_DONE=0
PART_DONE=0

MSG="🏗️ PromptBIM Sprint P23 啟動
📋 Audit Fixes + GUI + MCP + Voice
🎯 35 Tasks / 7 Parts → v2.10.0
📊 基於: AuditReport_03261945 (32 issues)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## 關鍵文件完整性檢查

```bash
CLAUDE_SIZE=$(wc -c < CLAUDE.md 2>/dev/null | tr -d ' ')
SKILL_SIZE=$(wc -c < SKILL.md 2>/dev/null | tr -d ' ')
if [ "$CLAUDE_SIZE" -lt 5000 ] 2>/dev/null || [ "$SKILL_SIZE" -lt 20000 ] 2>/dev/null; then
    MSG="⛔ 關鍵文件損壞！CLAUDE=${CLAUDE_SIZE}B SKILL=${SKILL_SIZE}B"
    echo "$MSG" && notify "$MSG" && exit 1
fi
echo "✅ 關鍵文件完整: CLAUDE=${CLAUDE_SIZE}B SKILL=${SKILL_SIZE}B"
```

---

## 環境檢查

```bash
if [ -n "$ANTHROPIC_API_KEY" ]; then
    MSG="⛔ PromptBIM Sprint 中止 — 偵測到 ANTHROPIC_API_KEY
🔧 修復: unset ANTHROPIC_API_KEY"
    echo "$MSG" && notify "$MSG" && exit 1
fi
echo "✅ 認證: Claude Max 訂閱"
```

---

## 必讀文件

```
1. 本文件 sprints/PROMPT_P23.md
2. docs/audit-reports/AuditReport_03261945.md ← 32 issues 來源
3. SKILL.md ← v3.3 唯讀，不得修改
4. CLAUDE.md ← v1.17.0，絕對不得修改
5. TODO.md
```

---

## ★ 通知規則（本 Sprint 全程適用）★

> ⚠️ **遵守 CLAUDE.md v1.17.0：每個 Task/Part 啟動 ▶️ 和結束 ✅ 都必須 notify。**
> ⚠️ **主要收件人: +886972535899**

### Task 啟動通知 ▶️
```bash
MSG="🏗️ PromptBIM P23
▶️ Task ${TASK_NUM}/${TASK_TOTAL} 開始: ${TASK_DESCRIPTION}
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Task 結束通知 ✅
```bash
TASK_DONE=$((TASK_DONE + 1))
PCT=$((TASK_DONE * 100 / TASK_TOTAL))
MSG="🏗️ PromptBIM P23
✅ Task ${TASK_NUM}/${TASK_TOTAL} 完成: ${TASK_DESCRIPTION}
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Part 啟動通知 ▶️
```bash
MSG="🏗️ PromptBIM P23
▶️ Part ${PART} 開始: ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Part 結束通知 ✅
```bash
PART_DONE=$((PART_DONE + 1))
MSG="🏗️ PromptBIM P23 Part ${PART} ✅
📋 ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
⏭️ 下一步: Part ${NEXT_PART} (${NEXT_PART_TASKS} tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Task 失敗通知 ⚠️
```bash
MSG="🏗️ PromptBIM P23
⚠️ Task ${TASK_NUM} 失敗: ${ERROR_DESCRIPTION}
🔄 嘗試修復 (${ATTEMPT}/3)...
📊 進度: ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part A: Tier 0 — 緊急修復 (3 Tasks)

> ▶️ Part A 啟動 notify | ✅ Part A 結束 notify

### Task 1: BIMSceneBuilder 重複代碼清除 [CRITICAL]
**問題:** `SceneKitView.swift:57-187` 完整複製 `BIMSceneBuilder` 類別。
**修復:** 刪除 `SceneKitView.swift` 中的重複類別，改為 `import` 引用 `BIMSceneBuilder`。
> ▶️ Task 1 開始 | ✅ Task 1 完成 | 3%

### Task 2: BIMSceneBuilder 加入 Compile Sources [CRITICAL]
**問題:** `BIMSceneBuilder.swift` 在 pbxproj 中未加入 Sources build phase。
**修復:** 確保在 `project.pbxproj` 的 Compile Sources 中。
> ▶️ Task 2 開始 | ✅ Task 2 完成 | 6%

### Task 3: pbxproj 版本同步 [HIGH]
**問題:** pbxproj MARKETING_VERSION=2.9.0, build=22（應 2.10.0 / 24）。
**修復:** 更新 pbxproj + Info.plist 為 2.10.0 / build 24。
> ▶️ Task 3 開始 | ✅ Task 3 完成 | 9%

### Part A ▶️ 啟動 + ✅ 結束通知
```bash
# Part A 結束
PART_DONE=1
MSG="🏗️ PromptBIM P23 Part A ✅
🚨 Tier 0 緊急修復 (3 tasks)
✅ 重複代碼清除 + Compile Sources + 版本同步
📊 進度: Task 3/35 | Part 1/7 | 9%
⏭️ 下一步: Part B — Tier 1 安全+品質 (7 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part B: Tier 1 — 安全 + 品質修復 (7 Tasks)

### Task 4: PythonBridge 線程安全 [HIGH]
加 `DispatchQueue` serial 保護 `guiProcess` 存取。
> ▶️/✅ | 11%

### Task 5: NativeBIMBridge 安全 C 字串轉換 [HIGH]
`String(cString:)` → `String(validatingCString:)` + fallback。
> ▶️/✅ | 14%

### Task 6: ContentView force unwrap 修復 [MEDIUM]
`UTType(filenameExtension:)!` → optional chaining。
> ▶️/✅ | 17%

### Task 7: BIMSceneBuilder 路徑注入防護 [HIGH]
`loadUSDA(at:)` 加入路徑正規化 + symlink 檢查。
> ▶️/✅ | 20%

### Task 8: C++ 版本號統一 [MEDIUM]
`vcpkg.json` + `promptbim.h` + `test_version.cpp` 更新為 2.10.0。
> ▶️/✅ | 23%

### Task 9: Web app 輸入驗證 [MEDIUM]
`web/app.py:60-63` float 轉換加 try/catch。圖片大小驗證。
> ▶️/✅ | 26%

### Task 10: 根目錄清理 [MEDIUM]
移動 `BuildSetupAndDemo_0326.md` → `docs/`。
移除 `Miniforge3-MacOSX-arm64.sh`（65MB）。
清除根目錄殘留 PROMPT 副本。
> ▶️/✅ | 29%

### Part B 結束通知
```bash
PART_DONE=2
MSG="🏗️ PromptBIM P23 Part B ✅
🔒 Tier 1 安全+品質 (7 tasks)
📊 進度: Task 10/35 | Part 2/7 | 29%
⏭️ 下一步: Part C — GUI 美化 (6 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part C: GUI 美化 + UX 改善 (6 Tasks)

### Task 11: 主題色系統 (Dark/Light Mode)
> ▶️/✅ | 31%

### Task 12: 左側面板改版 — 可折疊 + 圖標
> ▶️/✅ | 34%

### Task 13: 2D 地籍視圖增強（圖層切換、面積標注）
> ▶️/✅ | 37%

### Task 14: 3D 視圖增強（樓層剖面、半透明、材質）
> ▶️/✅ | 40%

### Task 15: 屬性面板增強（成本明細、法規合規狀態）
> ▶️/✅ | 43%

### Task 16: 進度指示器（Agent Pipeline 進度條）
> ▶️/✅ | 46%

### Part C 結束通知
```bash
PART_DONE=3
MSG="🏗️ PromptBIM P23 Part C ✅
🎨 GUI 美化 (6 tasks)
📊 進度: Task 16/35 | Part 3/7 | 46%
⏭️ 下一步: Part D — MCP Server (5 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part D: MCP Server 完善 (5 Tasks)

### Task 17: MCP Server 完整實作 (FastMCP + agenerate)
> ▶️/✅ | 49%

### Task 18: MCP Tools 定義 (generate/check/cost/cache)
> ▶️/✅ | 51%

### Task 19: Claude Desktop 整合 (config.json 範例)
> ▶️/✅ | 54%

### Task 20: MCP Error Handling + Timeout
> ▶️/✅ | 57%

### Task 21: MCP Tests (+5 tests)
> ▶️/✅ | 60%

### Part D 結束通知
```bash
PART_DONE=4
MSG="🏗️ PromptBIM P23 Part D ✅
🔌 MCP Server (5 tasks)
📊 進度: Task 21/35 | Part 4/7 | 60%
⏭️ 下一步: Part E — 語音輸入 (5 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part E: 語音輸入 (5 Tasks)

### Task 22: macOS NSSpeechRecognizer 整合
> ▶️/✅ | 63%

### Task 23: faster-whisper 本地 STT (選用)
> ▶️/✅ | 66%

### Task 24: 語音按鈕 UI (🎤 按住說話)
> ▶️/✅ | 69%

### Task 25: 語音 → AI 生成 Pipeline
> ▶️/✅ | 71%

### Task 26: 語音 Tests (+4 tests)
> ▶️/✅ | 74%

### Part E 結束通知
```bash
PART_DONE=5
MSG="🏗️ PromptBIM P23 Part E ✅
🗣️ 語音輸入 (5 tasks)
📊 進度: Task 26/35 | Part 5/7 | 74%
⏭️ 下一步: Part F — 效能+測試 (5 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part F: 效能優化 + 測試補齊 (5 Tasks)

### Task 27: Pipeline Benchmark 腳本
> ▶️/✅ | 77%

### Task 28: Lazy Import + 記憶體優化
> ▶️/✅ | 80%

### Task 29: Swift 測試補齊 (+15 XCTest) 目標覆蓋 60%+
覆蓋: PythonBridge、ContentView、SceneKitView。
> ▶️/✅ | 83%

### Task 30: Python/C++ 測試補齊 (pytest +20, GoogleTest +13)
Rate limiter 測試、Cache 併發、C++ 並發。
> ▶️/✅ | 86%

### Task 31: API.md 重寫 [CRITICAL] + Context Prompt 更新 [HIGH]
從 v2.0.0 更新至 v2.10.0。
> ▶️/✅ | 89%

### Part F 結束通知
```bash
PART_DONE=6
MSG="🏗️ PromptBIM P23 Part F ✅
⚡ 效能+測試 (5 tasks)
📊 進度: Task 31/35 | Part 6/7 | 89%
⏭️ 下一步: Part G — 驗收推送 (4 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part G: 驗收 + 推送 (4 Tasks)

### Task 32: xcodebuild + pytest + GoogleTest + XCTest 全通過
驗收: BUILD SUCCEEDED + pytest ≥860 + GoogleTest ≥165 + XCTest ≥35
> ▶️/✅ | 91%

### Task 33: 全量文件同步 (8項)
TODO.md / CHANGELOG.md / README.md / pyproject.toml / __init__.py / Info.plist / CMakeLists.txt / Context Prompt → v2.10.0
> ▶️/✅ | 94%

### Task 34: 自我審計報告 + Git push + Tag v2.10.0
`docs/audit-reports/Sprint23_AuditReport.md`
> ▶️/✅ | 97%

### Task 35: 產生 PROMPT_P24.md
依 CLAUDE.md v1.17.0 合規性檢查。
> ▶️/✅ | 100%

### Sprint 最終通知
```bash
MSG="🏗️ PromptBIM Sprint P23 完成 🎉
📋 Audit Fixes + GUI + MCP + Voice
🏷️ v2.10.0 | 35 Tasks / 7 Parts
🔧 Fixed: 3 Critical + 8 High + 12 Medium
🧪 Tests: pytest ≥860 + GoogleTest ≥165 + XCTest ≥35
📊 完成度: 100% ✅
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## 執行指令

1. **第一步: 定義 notify + 啟動通知**（主要收件人 +886972535899）
2. **關鍵文件完整性檢查**（CLAUDE ≥5000B, SKILL ≥20000B）
3. **環境檢查**（ANTHROPIC_API_KEY 衝突）
4. **★ 每 Task 啟動 ▶️ notify + 結束 ✅ notify ★**
5. **★ 每 Part 啟動 ▶️ notify + 結束 ✅ notify ★**
6. **每則 notify 含進度** (Task N/35 | Part N/7 | %)
7. **Part 結束含 ⏭️ 下一步預告**
8. **不得修改 CLAUDE.md / SKILL.md / docs/backups/**
9. **不得中途詢問用戶**
10. **審計報告: docs/audit-reports/Sprint23_AuditReport.md**

---

## 驗收標準

```
☐ 啟動通知已收到（+886972535899）
☐ Tier 0: BIMSceneBuilder 重複清除 + Compile Sources + 版本同步
☐ Tier 1: 線程安全 + C 字串安全 + 路徑注入 + 版本統一
☐ GUI: Dark/Light + 折疊面板 + 增強視圖 + 進度指示器
☐ MCP: Server + Claude Desktop 整合
☐ Voice: 🎤 按鈕 + STT → AI pipeline
☐ Tests: pytest ≥860 + GoogleTest ≥165 + XCTest ≥35
☐ API.md 重寫 (v2.0.0 → v2.10.0)
☐ xcodebuild BUILD SUCCEEDED
☐ git tag v2.10.0
☐ docs/audit-reports/Sprint23_AuditReport.md
☐ sprints/PROMPT_P24.md 已建立
☐ ★ 每 Task 有 ▶️ 啟動 + ✅ 結束 notify
☐ ★ 每 Part 有 ▶️ 啟動 + ✅ 結束 notify
☐ 最終完成 notify (100%)
```

---

*sprints/PROMPT_P23.md v2.0 | 2026-03-26*
*審計來源: AuditReport_03261945.md (32 issues)*
*★ 主要收件人: +886972535899 | 備用: chchlin1018@icloud.com*
*★ 雙向通知: 每 Task/Part 啟動 ▶️ + 結束 ✅*
*CLAUDE.md: v1.17.0 | SKILL.md: v3.3*
