# PROMPT_P24.md — Demo 3D Auto-Gen + Free IFC Model + Advanced BIM

> **Sprint:** P24 | **版本:** v3.0 | **目標版本:** v2.11.0 | **基於:** P23 (v2.10.0)
> **CLAUDE.md:** v1.18.0 | **SKILL.md:** v3.4（唯讀）
> **前置:** P23 完成 + P24 Part A-D 部分恢復（OOM 中斷）
> **範圍:** 5 Parts / 28 Tasks
> **核心目標:** App 啟動即顯示 3D 建築模型
> **v3.0 變更:** ★ 全面記憶體監控（CLAUDE.md v1.18.0 合規）★

---

## ★★★ 絕對第一步：定義 notify + get_mem + check_mem 函數 ★★★

> ⚠️ Claude Code `-p` 模式不載入 `.zshrc`，函數不存在，必須顯式定義。
> ⚠️ P24 OOM 教訓: Mac Mini 16GB RAM 耗盡 → Claude Code 被暫停 → Sprint 靜默中斷。
> ⚠️ 主要收件人: `+886972535899`（手機號碼，最優先）

```bash
# ===== ★★★ Sprint 絕對第一步：定義 notify + get_mem + check_mem 函數 ★★★ =====
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

# ===== ★★★ 記憶體監控函數 (CLAUDE.md v1.18.0 MANDATORY) ★★★ =====
get_mem() {
    local page_size=$(sysctl -n hw.pagesize 2>/dev/null || echo 4096)
    local total_bytes=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
    local total_gb=$(echo "scale=1; $total_bytes / 1073741824" | bc 2>/dev/null || echo "?")
    local free_pages=$(vm_stat 2>/dev/null | awk '/Pages free/ {gsub(/\./,"",$3); print $3}')
    local inactive_pages=$(vm_stat 2>/dev/null | awk '/Pages inactive/ {gsub(/\./,"",$3); print $3}')
    local free_bytes=$(( (${free_pages:-0} + ${inactive_pages:-0}) * page_size ))
    local free_gb=$(echo "scale=1; $free_bytes / 1073741824" | bc 2>/dev/null || echo "?")
    local used_gb=$(echo "scale=1; ($total_bytes - $free_bytes) / 1073741824" | bc 2>/dev/null || echo "?")
    local pressure=$(memory_pressure 2>/dev/null | grep "System-wide" | awk '{print $NF}' || echo "unknown")
    echo "${used_gb}/${total_gb}GB (free:${free_gb}GB) pressure:${pressure}"
}

check_mem() {
    local MEM_INFO=$(get_mem)
    local free_gb=$(echo "$MEM_INFO" | grep -oE 'free:[0-9.]+' | grep -oE '[0-9.]+')
    if [ "$(echo "${free_gb:-0} < 1.0" | bc 2>/dev/null)" = "1" ]; then
        MSG="⛔ PromptBIM 記憶體嚴重不足！
💾 ${MEM_INFO}
❗ Free < 1GB — Sprint 可能被系統終止
🔧 請關閉 Chrome/Notion/AnyDesk 後重試
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
        echo "$MSG" && notify "$MSG"
        return 1
    elif [ "$(echo "${free_gb:-0} < 2.0" | bc 2>/dev/null)" = "1" ]; then
        MSG="⚠️ PromptBIM 記憶體偏低
💾 ${MEM_INFO}
⚠️ Free < 2GB — 建議關閉非必要 App
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
        echo "$MSG" && notify "$MSG"
    fi
    return 0
}

echo "✅ notify + get_mem + check_mem 函數已定義"
```

---

## ★★★ 第二步：記憶體檢查（<1GB 中止 Sprint）★★★

```bash
check_mem || { echo "⛔ 記憶體不足，Sprint 中止"; exit 1; }
echo "✅ 記憶體檢查通過"
```

---

## 第三步：Sprint 啟動通知（含 💾 記憶體）

```bash
SPRINT=24
TASK_TOTAL=28
PART_TOTAL=5
TASK_DONE=0
PART_DONE=0
PCT=0

MEM_INFO=$(get_mem)
MSG="🏗️ PromptBIM Sprint P24 啟動
📋 Demo 3D Auto-Gen + Free IFC Model + Advanced BIM
🎯 28 Tasks / 5 Parts → v2.11.0
📊 核心: App 啟動即顯示 3D 建築模型
💾 ${MEM_INFO}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG"
notify "$MSG"
```

---

## 第四步：關鍵文件完整性檢查

```bash
CLAUDE_SIZE=$(wc -c < CLAUDE.md 2>/dev/null | tr -d ' ')
SKILL_SIZE=$(wc -c < SKILL.md 2>/dev/null | tr -d ' ')
if [ "$CLAUDE_SIZE" -lt 5000 ] 2>/dev/null || [ "$SKILL_SIZE" -lt 20000 ] 2>/dev/null; then
    MEM_INFO=$(get_mem)
    MSG="⛔ 關鍵文件損壞！CLAUDE=${CLAUDE_SIZE}B SKILL=${SKILL_SIZE}B 💾 ${MEM_INFO}"
    echo "$MSG" && notify "$MSG" && exit 1
fi
echo "✅ 關鍵文件完整: CLAUDE=${CLAUDE_SIZE}B SKILL=${SKILL_SIZE}B"
```

---

## 第五步：環境檢查

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
1. 本文件 sprints/PROMPT_P24.md (v3.0)
2. docs/audit-reports/Sprint23_AuditReport.md ← P23 審計結果
3. src/promptbim/demo/demo_data.py ← 現有 Demo 資料
4. SKILL.md ← v3.4 唯讀，不得修改
5. CLAUDE.md ← v1.18.0，絕對不得修改
```

---

## ★ 通知規則（CLAUDE.md v1.18.0 全程適用）★

> ⚠️ **每個 Task/Part 啟動 ▶️ 和結束 ✅ 都必須 notify**
> ⚠️ **★ Task 啟動 ▶️ 必須含 💾 get_mem 記憶體狀態 ★**
> ⚠️ **★ Part 啟動前必須 check_mem — <1GB 暫停 Sprint ★**
> ⚠️ **主要收件人: +886972535899**

### Task 啟動通知 ▶️（含 💾 記憶體）
```bash
PCT=$((TASK_DONE * 100 / TASK_TOTAL))
MEM_INFO=$(get_mem)
MSG="🏗️ PromptBIM P24
▶️ Task ${TASK_NUM}/${TASK_TOTAL} 開始: ${TASK_DESCRIPTION}
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
💾 ${MEM_INFO}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Task 結束通知 ✅
```bash
TASK_DONE=$((TASK_DONE + 1))
PCT=$((TASK_DONE * 100 / TASK_TOTAL))
MSG="🏗️ PromptBIM P24
✅ Task ${TASK_NUM}/${TASK_TOTAL} 完成: ${TASK_DESCRIPTION}
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Part 啟動通知 ▶️（含 check_mem + 💾 記憶體）
```bash
check_mem || { echo "⛔ 記憶體不足，Sprint 暫停"; MSG="⛔ PromptBIM P24 記憶體不足暫停 at Part ${PART} 💾 $(get_mem)"; notify "$MSG"; exit 1; }
MEM_INFO=$(get_mem)
MSG="🏗️ PromptBIM P24
▶️ Part ${PART} 開始: ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
💾 ${MEM_INFO}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Part 結束通知 ✅
```bash
PART_DONE=$((PART_DONE + 1))
PCT=$((TASK_DONE * 100 / TASK_TOTAL))
MSG="🏗️ PromptBIM P24 Part ${PART} ✅
📋 ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
⏭️ 下一步: Part ${NEXT_PART} (${NEXT_PART_TASKS} tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Task 失敗通知 ⚠️（含 💾 記憶體）
```bash
MEM_INFO=$(get_mem)
MSG="🏗️ PromptBIM P24
⚠️ Task ${TASK_NUM} 失敗: ${ERROR_DESCRIPTION}
🔄 嘗試修復 (${ATTEMPT}/3)...
📊 進度: ${PCT}%
💾 ${MEM_INFO}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### 中斷通知 ❌（含 💾 記憶體）
```bash
MEM_INFO=$(get_mem)
MSG="🏗️ PromptBIM
❌ Sprint P24 中斷
📍 停在: Task ${TASK_NUM}/${TASK_TOTAL} (${TASK_DESCRIPTION})
❗ 原因: ${ERROR_DESCRIPTION}
📊 完成度: ${PCT}% (${TASK_DONE}/${TASK_TOTAL} tasks)
💾 ${MEM_INFO}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part A: Demo 3D 自動生成 — App 啟動即顯示模型 (8 Tasks)

> ⚠️ **Part 啟動前: check_mem**
> ⚠️ **P24 前次已完成 Part A 部分工作（commit 18623db），檢查已有檔案避免重複。**

### Task 1: 從 demo_data.py 自動生成 Demo IFC 檔案
新增 `generate_demo_ifc()` — 用 BuilderAgent 從 demo BuildingPlan 生成 IFC。
> ▶️ notify（含💾） → 執行 → ✅ notify | 4%

### Task 2: 從 demo_data.py 自動生成 Demo USDA 檔案
新增 `generate_demo_usda()` — USDGenerator 生成 .usda。
> ▶️💾 → ✅ | 7%

### Task 3: 生成 Demo 2D 平面圖 SVG
`demo_floorplan_1f.svg` / `2f.svg` / `3f.svg` + `demo_site_plan.svg`。
> ▶️💾 → ✅ | 11%

### Task 4: 下載免費 IFC 範例模型 (Fallback)
來源: `github.com/youshengCode/IfcSampleFiles` (MIT) → `resources/demo/sample_house.ifc`。
> ▶️💾 → ✅ | 14%

### Task 5: `generate_all_demo_resources()` 整合函數
整合 Task 1-3 + save_demo_resources() 到統一入口。
> ▶️💾 → ✅ | 18%

### Task 6: GUI 啟動時載入 Demo 3D 模型
修改 `main_window.py` — 啟動時自動載入 IFC/USDA 到 3D 視窗 + 2D 載入 SVG。
> ▶️💾 → ✅ | 21%

### Task 7: Swift 3D 視圖載入 Demo USDA
`ContentView.swift` + `BIMSceneBuilder.swift` — SceneKit 渲染 USDA。
> ▶️💾 → ✅ | 25%

### Task 8: Demo 3D 測試 (+5 tests)
生成 IFC/USDA 有效性 + GUI 非空 + 清除後重生成。
> ▶️💾 → ✅ | 29%

---

## Part B: 進階 BIM 功能 (6 Tasks)

> ⚠️ **Part 啟動前: check_mem（<1GB 暫停）**

### Task 9: Multi-story 自動停車場生成
1F 自動停車場配置（車位/車道/斜坡）。
> ▶️💾 → ✅ | 32%

### Task 10: 建築材質系統
牆壁/地板/天花板材質定義 + PBR 渲染。
> ▶️💾 → ✅ | 36%

### Task 11: 結構系統自動生成
柱/梁/基礎 根據 BuildingPlan 自動配置。
> ▶️💾 → ✅ | 39%

### Task 12: MEP 管線自動路由
簡易水電管線路由（垂直管道 + 水平分支）。
> ▶️💾 → ✅ | 43%

### Task 13: 樓梯/電梯自動生成
根據樓層數自動加入樓梯間和電梯井。
> ▶️💾 → ✅ | 46%

### Task 14: 進階 BIM Tests (+6 tests)
> ▶️💾 → ✅ | 50%

---

## Part C: CI/CD + 啟動優化 (6 Tasks)

> ⚠️ **Part 啟動前: check_mem（<1GB 暫停）**

### Task 15: GitHub Actions 修復 + 優化
分鐘用完 → 只跑 Linux pytest + lint，跳過 macOS runner。
> ▶️💾 → ✅ | 54%

### Task 16: App 啟動時間優化 (目標 < 3s)
Profiling + lazy import + 延遲 3D 渲染。
> ▶️💾 → ✅ | 57%

### Task 17: 自動版本同步腳本
`scripts/sync_version.sh` — 一次更新所有版本檔案。
> ▶️💾 → ✅ | 61%

### Task 18: 開發者快速啟動腳本
`scripts/dev_setup.sh` — conda + pip + C++ build + 驗證。
> ▶️💾 → ✅ | 64%

### Task 19: Pre-commit hooks
ruff lint + version sync check。
> ▶️💾 → ✅ | 68%

### Task 20: CI/CD Tests (+4 tests)
> ▶️💾 → ✅ | 71%

---

## Part D: 測試補齊 + 整合測試 (4 Tasks)

> ⚠️ **Part 啟動前: check_mem（<1GB 暫停）**

### Task 21: E2E Pipeline 整合測試 (+5 tests)
prompt → IFC + USDA 完整 pipeline（mock LLM）。
> ▶️💾 → ✅ | 75%

### Task 22: MCP Server 整合測試 (+3 tests)
Claude Desktop → MCP → generate → IFC。
> ▶️💾 → ✅ | 79%

### Task 23: Swift ↔ Python 整合測試 (+4 tests)
PythonBridge → GUI → 3D render → cleanup。
> ▶️💾 → ✅ | 82%

### Task 24: 覆蓋率門檻提升
pyproject.toml `fail_under` 70 → 75。
> ▶️💾 → ✅ | 86%

---

## Part E: 驗收 + 推送 (4 Tasks)

> ⚠️ **Part 啟動前: check_mem（<1GB 暫停）**

### Task 25: xcodebuild + pytest + GoogleTest + XCTest 全通過
BUILD SUCCEEDED + pytest ≥880 + GoogleTest ≥170 + XCTest ≥40。
> ▶️💾 → ✅ | 89%

### Task 26: 全量文件同步 (8項)
TODO / CHANGELOG / README / pyproject / __init__ / Info.plist / CMakeLists / Context Prompt → v2.11.0。
> ▶️💾 → ✅ | 93%

### Task 27: 自我審計報告 + Git push + Tag v2.11.0
`docs/audit-reports/Sprint24_AuditReport.md`
> ▶️💾 → ✅ | 96%

### Task 28: 產生 PROMPT_P25.md
依 CLAUDE.md v1.18.0 合規性檢查（含 get_mem + check_mem 函數）。
> ▶️💾 → ✅ | 100%

### Sprint 最終通知（含 💾 記憶體）
```bash
MEM_INFO=$(get_mem)
MSG="🏗️ PromptBIM Sprint P24 完成 🎉
📋 Demo 3D Auto-Gen + Free IFC + Advanced BIM
🏷️ v2.11.0 | 28 Tasks / 5 Parts
🏠 App 啟動即顯示 3D 建築模型
🧪 Tests: pytest ≥880 + GoogleTest ≥170 + XCTest ≥40
📊 完成度: 100% ✅
💾 ${MEM_INFO}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## 執行規則（CLAUDE.md v1.18.0 嚴格合規）

```
1. ★ 定義 notify + get_mem + check_mem（絕對第一步）
2. ★ check_mem — <1GB 中止 Sprint
3. ★ 啟動通知（含 💾 記憶體）
4. 關鍵文件完整性檢查
5. 環境檢查（ANTHROPIC_API_KEY 衝突）
6. ★ 每 Task 啟動 ▶️ notify（含 💾 get_mem）
7. ★ 每 Task 結束 ✅ notify
8. ★ 每 Part 啟動前 check_mem（<1GB 暫停）
9. ★ 每 Part 啟動 ▶️ notify（含 💾 記憶體）
10. ★ 每 Part 結束 ✅ notify（含 ⏭️ 下一步）
11. ★ 失敗/中斷 notify（含 💾 記憶體）
12. 不得修改 CLAUDE.md / SKILL.md / docs/backups/
13. 不得中途詢問用戶
14. 審計報告: docs/audit-reports/Sprint24_AuditReport.md
15. Sprint 結束產生 PROMPT_P25.md（合規 v1.18.0）
```

---

## 驗收標準

```
☐ ★ notify + get_mem + check_mem 函數已定義
☐ ★ Sprint 啟動 check_mem 通過
☐ ★ 啟動通知含 💾 記憶體（已收到 +886972535899）
☐ ★ 每 Task ▶️ notify 含 💾 get_mem
☐ ★ 每 Part ▶️ 啟動前 check_mem 通過
☐ App 啟動即顯示 3D 建築模型（不再空白）
☐ Demo IFC + USDA + SVG 自動生成
☐ 免費 IFC 模型下載作為 Fallback
☐ 進階 BIM: 停車場 + 材質 + 結構 + MEP + 樓梯
☐ CI/CD: Actions 修復 + 啟動優化 + 版本同步腳本
☐ E2E 整合測試通過
☐ xcodebuild BUILD SUCCEEDED
☐ pytest ≥880 + GoogleTest ≥170 + XCTest ≥40
☐ git tag v2.11.0
☐ docs/audit-reports/Sprint24_AuditReport.md
☐ sprints/PROMPT_P25.md（合規 CLAUDE.md v1.18.0 含記憶體監控）
☐ 最終 notify (100% + 💾 記憶體)
```

---

## 免費 IFC 模型來源參考

| 來源 | URL | License | 推薦模型 |
|------|-----|---------|---------|
| IfcSampleFiles | github.com/youshengCode/IfcSampleFiles | MIT | 小型住宅範例 |
| BIMData Research | github.com/bimdata/BIMData-Research-and-Development | Open | LTU_AHouse_ARC.ifc |
| OpenIFC Repository | openifcmodel.cs.auckland.ac.nz | Academic | 多種建築類型 |
| IfcOpenShell Examples | ifcopenshell.org | LGPL | 官方測試檔案 |

---

*sprints/PROMPT_P24.md v3.0 | 2026-03-26*
*★ v3.0 核心變更: 全面記憶體監控（CLAUDE.md v1.18.0 合規）*
*★ 每 Task ▶️ 含 💾 get_mem | 每 Part 啟動前 check_mem (<1GB 暫停)*
*★ P24 OOM 教訓: Mac Mini 16GB 耗盡 → Sprint 靜默中斷*
*★ 主要收件人: +886972535899 | 備用: chchlin1018@icloud.com*
*CLAUDE.md: v1.18.0 | SKILL.md: v3.4*
