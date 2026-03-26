# PROMPT_P23.md — Future Features: GUI Polish + MCP Server + Voice Input

> **Sprint:** P23 | **目標版本:** v2.10.0 | **基於:** P22.1 (v2.9.1)
> **CLAUDE.md:** v1.16.2 | **SKILL.md:** v3.2（唯讀）
> **前置:** P22.1 完成（v2.9.1）
> **範圍:** 5 Parts / 25 Tasks — GUI 美化 + MCP Server + 語音輸入 + 效能優化 + 驗收

---

## ★★★ 絕對第一步：定義 notify 函數 + 發送啟動通知 ★★★

```bash
# ===== ★★★ Sprint 絕對第一步：定義 notify 函數 ★★★ =====
notify() {
    local msg="$1"
    osascript -e "
        tell application \"Messages\"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant \"chchlin1018@icloud.com\" of targetService
            send \"$msg\" to targetBuddy
        end tell
    " 2>/dev/null || \
    osascript -e "
        tell application \"Messages\"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant \"+886972535899\" of targetService
            send \"$msg\" to targetBuddy
        end tell
    " 2>/dev/null || \
    osascript -e "display notification \"$msg\" with title \"PromptBIM\"" 2>/dev/null || \
    echo "[NOTIFY FALLBACK] $msg"
}
echo "✅ notify 函數已定義"

TASK_TOTAL=25
PART_TOTAL=5
TASK_DONE=0
PART_DONE=0

MSG="🏗️ PromptBIM Sprint P23 啟動
📋 Future Features: GUI Polish + MCP + Voice
🎯 25 Tasks / 5 Parts → v2.10.0
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
echo "✅ 關鍵文件完整"
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
2. SKILL.md ← 唯讀，不得修改
3. CLAUDE.md ← v1.16.2，絕對不得修改
4. TODO.md
```

---

## Part A: GUI 美化 + UX 改善 (6 Tasks)

### Task 1: 主題色系統 (Dark/Light Mode)
支援 macOS 系統主題切換。定義 PromptBIM 品牌色。
> Task 1/25 | Part 0/5 | 4%

### Task 2: 左側面板改版 — 可折疊 + 圖標
專案樹加入圖標（📁土地、🏗️建築、📊報告）。支援展開/折疊。
> Task 2/25 | 8%

### Task 3: 2D 地籍視圖增強
標注面積數字、方位角、退縮距離。支援圖層切換（土地/建築/退縮/標注）。
> Task 3/25 | 12%

### Task 4: 3D 視圖增強
樓層剖面切換。半透明模式。材質顯示。
> Task 4/25 | 16%

### Task 5: 屬性面板增強
顯示成本明細（結構/裝修/MEP）。法規合規狀態（✅/⚠️/❌）。
> Task 5/25 | 20%

### Task 6: 進度指示器
生成過程中顯示每個 Agent 的進度條（Enhancer → Planner → Builder → Checker）。
> Task 6/25 | 24%

### Part A 完成通知
```bash
PART_DONE=1
MSG="🏗️ PromptBIM P23 Part A ✅
🎨 GUI 美化 + UX 改善 (6 tasks)
📊 進度: Task 6/25 | Part 1/5 | 24%
⏭️ 下一步: Part B — MCP Server (5 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part B: MCP Server 完善 (5 Tasks)

### Task 7: MCP Server 完整實作
`src/promptbim/mcp/server.py` — FastMCP + await orchestrator.agenerate()。
> Task 7/25 | 28%

### Task 8: MCP Tools 定義
`generate_building`、`check_compliance`、`estimate_cost`、`list_cache`。
> Task 8/25 | 32%

### Task 9: MCP 與 Claude Desktop 整合測試
寫 claude_desktop_config.json 範例。
> Task 9/25 | 36%

### Task 10: MCP Error Handling + Timeout
30s timeout + 重試 + 錯誤回傳。
> Task 10/25 | 40%

### Task 11: MCP Tests (+5 tests)
> Task 11/25 | 44%

### Part B 完成通知
```bash
PART_DONE=2
MSG="🏗️ PromptBIM P23 Part B ✅
🔌 MCP Server (5 tasks)
📊 進度: Task 11/25 | Part 2/5 | 44%
⏭️ 下一步: Part C — 語音輸入 (5 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part C: 語音輸入 (5 Tasks)

### Task 12: macOS NSSpeechRecognizer 整合
Swift 端接入系統語音辨識。
> Task 12/25 | 48%

### Task 13: faster-whisper 本地 STT (選用)
Python 端離線語音辨識。
> Task 13/25 | 52%

### Task 14: 語音按鈕 UI
Chat 面板加入 🎤 按鈕，按住說話，放開送出文字。
> Task 14/25 | 56%

### Task 15: 語音 → AI 生成 Pipeline
語音辨識文字 → Orchestrator.generate()。
> Task 15/25 | 60%

### Task 16: 語音 Tests (+4 tests)
> Task 16/25 | 64%

### Part C 完成通知
```bash
PART_DONE=3
MSG="🏗️ PromptBIM P23 Part C ✅
🗣️ 語音輸入 (5 tasks)
📊 進度: Task 16/25 | Part 3/5 | 64%
⏭️ 下一步: Part D — 效能優化 (5 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part D: 效能優化 + 穩定性 (5 Tasks)

### Task 17: Pipeline Benchmark 腳本
`scripts/benchmark.py` — 測量每個 Agent 階段耗時。
> Task 17/25 | 68%

### Task 18: Lazy Import 優化
確保 `--version` 和 `cache` 命令不觸發重依賴 import。
> Task 18/25 | 72%

### Task 19: 記憶體 Profiling
大型建築（10F+）的記憶體使用分析。
> Task 19/25 | 76%

### Task 20: Error Recovery 強化
每個 Agent 失敗後的 graceful degradation。
> Task 20/25 | 80%

### Task 21: 效能 Tests (+4 tests)
> Task 21/25 | 84%

### Part D 完成通知
```bash
PART_DONE=4
MSG="🏗️ PromptBIM P23 Part D ✅
⚡ 效能優化 (5 tasks)
📊 進度: Task 21/25 | Part 4/5 | 84%
⏭️ 下一步: Part E — 驗收推送 (4 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part E: 驗收 + 推送 (4 Tasks)

### Task 22: xcodebuild + pytest + GoogleTest + XCTest 全通過
> Task 22/25 | 88%

### Task 23: 全量文件同步 (8項)
> Task 23/25 | 92%

### Task 24: 自我審計報告 + Git push + Tag v2.10.0
> Task 24/25 | 96%

### Task 25: 產生 PROMPT_P24.md
> Task 25/25 | 100%

### Sprint 最終通知
```bash
MSG="🏗️ PromptBIM Sprint P23 完成 🎉
📋 GUI Polish + MCP Server + Voice Input
🏷️ v2.10.0 | 25 Tasks / 5 Parts
📊 完成度: 100% ✅
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## 執行指令

1. **第一步: 定義 notify + 啟動通知**
2. **關鍵文件完整性檢查**
3. **環境檢查（含 API Key 衝突）**
4. **每 Task notify 含進度** (Task N/25 | Part N/5 | %)
5. **每 Part notify 含下一步預告**
6. **不得修改 CLAUDE.md / SKILL.md / docs/backups/**
7. **不得中途詢問用戶**

---

## 驗收標準

```
☐ 啟動通知已收到
☐ GUI: Dark/Light mode + 折疊面板 + 增強視圖
☐ MCP: Server 可用 + Claude Desktop 整合
☐ Voice: 語音按鈕 + STT → AI pipeline
☐ Performance: Benchmark 腳本 + lazy import
☐ xcodebuild BUILD SUCCEEDED
☐ 所有測試通過
☐ git tag v2.10.0
☐ docs/audit-reports/Sprint23_AuditReport.md
☐ sprints/PROMPT_P24.md 已建立
☐ 每個 Task/Part notify 含進度 %
☐ 最終完成 notify (100%)
```

---

*sprints/PROMPT_P23.md v1.0 | 2026-03-26*
*notify: chchlin1018@icloud.com / +886972535899*
*通知: Task N/25 | Part N/5 | N%*
