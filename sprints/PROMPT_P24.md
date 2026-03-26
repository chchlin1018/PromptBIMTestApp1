# PROMPT_P24.md — Demo 3D Auto-Gen + Free IFC Model + Advanced BIM

> **Sprint:** P24 | **目標版本:** v2.11.0 | **基於:** P23 (v2.10.0)
> **CLAUDE.md:** v1.17.0 | **SKILL.md:** v3.3（唯讀）
> **前置:** P23 完成（v2.10.0, ~1060+ tests）
> **範圍:** 5 Parts / 28 Tasks — Demo 3D 自動生成 + 免費 IFC 模型整合 + 進階 BIM + CI/CD + 測試
> **核心目標:** App 啟動即顯示 3D 建築模型（目前啟動是空白 3D 視窗）

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

TASK_TOTAL=28
PART_TOTAL=5
TASK_DONE=0
PART_DONE=0

MSG="🏗️ PromptBIM Sprint P24 啟動
📋 Demo 3D Auto-Gen + Free IFC Model + Advanced BIM
🎯 28 Tasks / 5 Parts → v2.11.0
📊 核心: App 啟動即顯示 3D 建築模型
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
1. 本文件 sprints/PROMPT_P24.md
2. docs/audit-reports/Sprint23_AuditReport.md ← P23 審計結果
3. src/promptbim/demo/demo_data.py ← 現有 Demo 資料（只有 Python 物件，沒有 3D 檔案）
4. SKILL.md ← v3.3 唯讀，不得修改
5. CLAUDE.md ← v1.17.0，絕對不得修改
```

---

## ★ 通知規則（本 Sprint 全程適用）★

> ⚠️ **遵守 CLAUDE.md v1.17.0：每個 Task/Part 啟動 ▶️ 和結束 ✅ 都必須 notify。**
> ⚠️ **主要收件人: +886972535899**

### Task 啟動通知 ▶️
```bash
MSG="🏗️ PromptBIM P24
▶️ Task ${TASK_NUM}/${TASK_TOTAL} 開始: ${TASK_DESCRIPTION}
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
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

### Part 啟動通知 ▶️
```bash
MSG="🏗️ PromptBIM P24
▶️ Part ${PART} 開始: ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Part 結束通知 ✅
```bash
PART_DONE=$((PART_DONE + 1))
MSG="🏗️ PromptBIM P24 Part ${PART} ✅
📋 ${PART_DESCRIPTION} (${PART_TASK_COUNT} tasks)
📊 進度: Task ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
⏭️ 下一步: Part ${NEXT_PART} (${NEXT_PART_TASKS} tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

### Task 失敗通知 ⚠️
```bash
MSG="🏗️ PromptBIM P24
⚠️ Task ${TASK_NUM} 失敗: ${ERROR_DESCRIPTION}
🔄 嘗試修復 (${ATTEMPT}/3)...
📊 進度: ${PCT}%
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part A: Demo 3D 自動生成 — App 啟動即顯示模型 (8 Tasks)

> ⚠️ **這是本 Sprint 最重要的 Part。**
> ⚠️ **目前問題:** `demo_data.py` 只有 Python 資料物件（BuildingPlan, LandParcel 等），
>    但沒有實際的 IFC/USDA 3D 檔案。App 啟動後 3D 視窗是空白的。
> ⚠️ **目標:** App 啟動時自動生成或載入 3D 模型，使用者立即看到建築。

### Task 1: 從 demo_data.py 自動生成 Demo IFC 檔案

**問題:** `demo_data.py` 有完整的 `BuildingPlan`，但從未呼叫 `BuilderAgent.build()` 來生成 IFC。
**修復:** 新增 `generate_demo_ifc()` 函數：
```python
def generate_demo_ifc(output_dir: Path = DEMO_RESOURCES_DIR) -> Path:
    """用 BuilderAgent 從 demo BuildingPlan 生成 IFC 檔案。"""
    from promptbim.bim.ifc_generator import IFCGenerator
    plan = get_demo_plan()
    gen = IFCGenerator()
    ifc_path = output_dir / "demo_building.ifc"
    gen.generate(plan, str(ifc_path))
    return ifc_path
```
> ▶️/✅ | 4%

### Task 2: 從 demo_data.py 自動生成 Demo USDA 檔案

同上，新增 `generate_demo_usda()`：
```python
def generate_demo_usda(output_dir: Path = DEMO_RESOURCES_DIR) -> Path:
    from promptbim.bim.usd_generator import USDGenerator
    plan = get_demo_plan()
    gen = USDGenerator()
    usda_path = output_dir / "demo_building.usda"
    gen.generate(plan, str(usda_path))
    return usda_path
```
> ▶️/✅ | 7%

### Task 3: 生成 Demo 2D 平面圖 SVG

新增 `generate_demo_svg()`：
- `demo_floorplan_1f.svg` / `2f.svg` / `3f.svg`
- `demo_site_plan.svg`（土地 + 建築 footprint + 退縮線）
> ▶️/✅ | 11%

### Task 4: 下載免費 IFC 範例模型 (Fallback)

從 GitHub 開源 IFC 集合下載一個小型住宅模型作為 fallback：
- **來源:** `https://github.com/youshengCode/IfcSampleFiles` (MIT License)
- **或:** `https://github.com/bimdata/BIMData-Research-and-Development` 的 LTU_AHouse_ARC.ifc
- 下載到 `resources/demo/sample_house.ifc`（< 5MB）
- 如果本地生成失敗，fallback 到此預下載檔案

> ▶️/✅ | 14%

### Task 5: `generate_all_demo_resources()` 整合函數

整合 Task 1-3 到一個函數：
```python
def generate_all_demo_resources() -> dict[str, Path]:
    """生成所有 Demo 資源（IFC + USDA + SVG + JSON）。"""
    paths = save_demo_resources()  # 現有的 JSON
    paths["ifc"] = generate_demo_ifc()
    paths["usda"] = generate_demo_usda()
    paths["svg"] = generate_demo_svg()
    return paths
```
> ▶️/✅ | 18%

### Task 6: GUI 啟動時載入 Demo 3D 模型

**修改:** `src/promptbim/gui/main_window.py`
- App 啟動時呼叫 `generate_all_demo_resources()`
- 自動載入 `demo_building.ifc` 或 `demo_building.usda` 到 3D 視窗
- 2D Tab 載入 `demo_site_plan.svg`
- 屬性面板載入 Demo 資料
- Chat 面板顯示歡迎訊息

> ▶️/✅ | 21%

### Task 7: Swift 3D 視圖載入 Demo USDA

**修改:** `PromptBIMTestApp1/ContentView.swift` + `BIMSceneBuilder.swift`
- 如果 Xcode App 啟動，自動從 `resources/demo/demo_building.usda` 載入 3D 場景
- SceneKit 渲染 3D 建築（旋轉/縮放/平移）
- Fallback: 如果找不到 USDA，從 `sample_house.ifc` 轉換

> ▶️/✅ | 25%

### Task 8: Demo 3D 測試 (+5 tests)

- 測試 `generate_demo_ifc()` 產生有效 IFC
- 測試 `generate_demo_usda()` 產生有效 USDA
- 測試 `generate_all_demo_resources()` 產生所有檔案
- 測試 GUI 啟動後 3D 視圖非空
- 測試清除 Demo 後重新生成

> ▶️/✅ | 29%

### Part A 結束通知
```bash
PART_DONE=1
MSG="🏗️ PromptBIM P24 Part A ✅
🏠 Demo 3D 自動生成 (8 tasks)
✅ IFC + USDA + SVG + Fallback + GUI 載入 + Swift 3D
📊 進度: Task 8/28 | Part 1/5 | 29%
⏭️ 下一步: Part B — 進階 BIM 功能 (6 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part B: 進階 BIM 功能 (6 Tasks)

### Task 9: Multi-story 自動停車場生成
1F 自動停車場配置（車位/車道/斜坡）。
> ▶️/✅ | 32%

### Task 10: 建築材質系統
牆壁/地板/天花板材質定義 + 渲染（PBR）。
> ▶️/✅ | 36%

### Task 11: 結構系統自動生成
柱/梁/基礎 根據 BuildingPlan 自動配置。
> ▶️/✅ | 39%

### Task 12: MEP 管線自動路由
簡易水電管線路由（垂直管道 + 水平分支）。
> ▶️/✅ | 43%

### Task 13: 樓梯/電梯自動生成
根據樓層數自動加入樓梯間和電梯井。
> ▶️/✅ | 46%

### Task 14: 進階 BIM Tests (+6 tests)
> ▶️/✅ | 50%

### Part B 結束通知
```bash
PART_DONE=2
MSG="🏗️ PromptBIM P24 Part B ✅
🏗️ 進階 BIM (6 tasks)
📊 進度: Task 14/28 | Part 2/5 | 50%
⏭️ 下一步: Part C — CI/CD + 啟動優化 (6 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part C: CI/CD + 啟動優化 (6 Tasks)

### Task 15: GitHub Actions 修復 + 優化
修復 CI workflow（分鐘用完問題 → 只跑 Linux pytest + lint，跳過 macOS runner）。
> ▶️/✅ | 54%

### Task 16: App 啟動時間優化 (目標 < 3s)
Profiling + lazy import + 延遲 3D 渲染。
> ▶️/✅ | 57%

### Task 17: 自動版本同步腳本
`scripts/sync_version.sh` — 一次更新 pyproject + __init__ + Info.plist + CMake + pbxproj。
> ▶️/✅ | 61%

### Task 18: 開發者快速啟動腳本
`scripts/dev_setup.sh` — conda 環境 + pip install + C++ build + 驗證。
> ▶️/✅ | 64%

### Task 19: Pre-commit hooks
ruff lint + version sync check。
> ▶️/✅ | 68%

### Task 20: CI/CD Tests (+4 tests)
> ▶️/✅ | 71%

### Part C 結束通知
```bash
PART_DONE=3
MSG="🏗️ PromptBIM P24 Part C ✅
⚙️ CI/CD + 啟動優化 (6 tasks)
📊 進度: Task 20/28 | Part 3/5 | 71%
⏭️ 下一步: Part D — 測試補齊 + 整合測試 (4 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part D: 測試補齊 + 整合測試 (4 Tasks)

### Task 21: E2E Pipeline 整合測試 (+5 tests)
從 prompt 到 IFC + USDA 完整 pipeline（mock LLM）。
> ▶️/✅ | 75%

### Task 22: MCP Server 整合測試 (+3 tests)
Claude Desktop → MCP → generate → IFC。
> ▶️/✅ | 79%

### Task 23: Swift ↔ Python 整合測試 (+4 tests)
PythonBridge → GUI → 3D render → cleanup。
> ▶️/✅ | 82%

### Task 24: 覆蓋率門檻提升
pyproject.toml `fail_under` 70 → 75。
> ▶️/✅ | 86%

### Part D 結束通知
```bash
PART_DONE=4
MSG="🏗️ PromptBIM P24 Part D ✅
🧪 測試 + 整合 (4 tasks)
📊 進度: Task 24/28 | Part 4/5 | 86%
⏭️ 下一步: Part E — 驗收推送 (4 tasks)
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
echo "$MSG" && notify "$MSG"
```

---

## Part E: 驗收 + 推送 (4 Tasks)

### Task 25: xcodebuild + pytest + GoogleTest + XCTest 全通過
驗收: BUILD SUCCEEDED + pytest ≥880 + GoogleTest ≥170 + XCTest ≥40
> ▶️/✅ | 89%

### Task 26: 全量文件同步 (8項)
TODO / CHANGELOG / README / pyproject.toml / __init__.py / Info.plist / CMakeLists.txt / Context Prompt → v2.11.0
> ▶️/✅ | 93%

### Task 27: 自我審計報告 + Git push + Tag v2.11.0
`docs/audit-reports/Sprint24_AuditReport.md`
> ▶️/✅ | 96%

### Task 28: 產生 PROMPT_P25.md
依 CLAUDE.md v1.17.0 合規性檢查。
> ▶️/✅ | 100%

### Sprint 最終通知
```bash
MSG="🏗️ PromptBIM Sprint P24 完成 🎉
📋 Demo 3D Auto-Gen + Free IFC + Advanced BIM
🏷️ v2.11.0 | 28 Tasks / 5 Parts
🏠 App 啟動即顯示 3D 建築模型
🧪 Tests: pytest ≥880 + GoogleTest ≥170 + XCTest ≥40
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
6. **每則 notify 含進度** (Task N/28 | Part N/5 | %)
7. **Part 結束含 ⏭️ 下一步預告**
8. **不得修改 CLAUDE.md / SKILL.md / docs/backups/**
9. **不得中途詢問用戶**
10. **審計報告: docs/audit-reports/Sprint24_AuditReport.md**

---

## 驗收標準

```
☐ 啟動通知已收到（+886972535899）
☐ ★ App 啟動即顯示 3D 建築模型（不再空白）
☐ ★ Demo IFC + USDA + SVG 自動生成
☐ ★ 免費 IFC 模型下載作為 Fallback
☐ 進階 BIM: 停車場 + 材質 + 結構 + MEP + 樓梯
☐ CI/CD: Actions 修復 + 啟動優化 + 版本同步腳本
☐ E2E 整合測試通過
☐ xcodebuild BUILD SUCCEEDED
☐ pytest ≥880 + GoogleTest ≥170 + XCTest ≥40
☐ git tag v2.11.0
☐ docs/audit-reports/Sprint24_AuditReport.md
☐ sprints/PROMPT_P25.md 已建立
☐ ★ 每 Task 有 ▶️ 啟動 + ✅ 結束 notify
☐ ★ 每 Part 有 ▶️ 啟動 + ✅ 結束 notify
☐ 最終完成 notify (100%)
```

---

## 免費 IFC 模型來源參考

| 來源 | URL | License | 推薦模型 |
|------|-----|---------|---------|
| IfcSampleFiles | github.com/youshengCode/IfcSampleFiles | MIT | 小型住宅範例 |
| BIMData Research | github.com/bimdata/BIMData-Research-and-Development | Open | LTU_AHouse_ARC.ifc |
| OpenIFC Repository | openifcmodel.cs.auckland.ac.nz | Academic | 多種建築類型 |
| IfcOpenShell Examples | ifcopenshell.org | LGPL | 官方測試檔案 |

**選擇標準:** < 5MB、住宅類型、IFC2X3 或 IFC4、有牆壁+樓板+屋頂。

---

*sprints/PROMPT_P24.md v2.0 | 2026-03-26*
*★ 核心目標: App 啟動即顯示 3D 建築模型（Demo IFC + USDA 自動生成）*
*★ 主要收件人: +886972535899 | 備用: chchlin1018@icloud.com*
*★ 雙向通知: 每 Task/Part 啟動 ▶️ + 結束 ✅*
*CLAUDE.md: v1.17.0 | SKILL.md: v3.3*
