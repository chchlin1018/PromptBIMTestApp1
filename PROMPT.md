# PROMPT.md — Claude Code 執行指令

> **版本:** v1.1.0 | **更新:** 2026-03-25
> **版本控制:** 本文件任何修改必須更新版本號和日期，並同步更新 CLAUDE.md

---

## ① 專案概述

本專案是 **PromptBIMTestApp1**，一個 AI 驅動的 BIM 建築模型自動生成器 (POC)。
macOS 桌面應用，使用 **Xcode 專案 (SwiftUI)** 包裝 **Python 後端**。
用戶只需輸入土地資料 + 一句 Prompt，系統自動完成所有建築設計、BIM、MEP、法規、4D/5D、監控點。

---

## ② 執行前檢查清單

Claude Code 在開始任何開發任務前，**必須先執行以下檢查**：

### Step 1: 驗證核心文件存在

```bash
required_files=(
  "README.md"
  "SETUP.md"
  "SKILL.md"
  "TODO.md"
  "CHANGELOG.md"
  "CLAUDE.md"
  "PROMPT.md"
  "LICENSE"
  "pyproject.toml"
  ".env.example"
  ".gitignore"
  "PromptBIMTestApp1.xcodeproj/project.pbxproj"
  "docs/addendum/README.md"
  "docs/addendum/01_component_library.md"
  "docs/addendum/02_sim_cost_mep.md"
  "docs/addendum/03_tw_building_codes.md"
  "docs/addendum/04_interactive_modify_and_monitoring.md"
  "reference/sample_parcel.geojson"
  "reference/sample_parcel_irregular.geojson"
  "reference/ifc_usd_mapping.md"
  "reference/free_model_sources.md"
  "reference/tw_zoning_reference.md"
  "examples/test_prompts.txt"
  "examples/prompt_scenarios.md"
  "examples/prompt_modification_scenarios.md"
  "examples/README.md"
  "src/promptbim/__init__.py"
)

missing=0
for f in "${required_files[@]}"; do
  if [ ! -f "$f" ]; then
    echo "❌ MISSING: $f"
    missing=$((missing + 1))
  else
    echo "✅ OK: $f"
  fi
done

if [ $missing -gt 0 ]; then
  echo ""
  echo "⚠️ $missing 個文件缺失！"
  if [ ! -f "PromptBIMTestApp1.xcodeproj/project.pbxproj" ]; then
    echo "→ Xcode 專案尚未建立，Sprint P0 會自動建立。"
  fi
  echo "→ 其他缺失文件請參考 PROMPT.md ③ 上傳指引。"
fi
echo ""
echo "✅ 檢查完成。"
```

### Step 2: 讀取知識庫

```
必讀順序:
1. SKILL.md          ← 專案 SSOT
2. TODO.md           ← 確認當前 Sprint 狀態
3. CLAUDE.md         ← 開發行為規範 + [MANDATORY] 規則
4. 對應的 Addendum   ← 依當前 Sprint
```

| Sprint | 必讀 Addendum |
|--------|----------------|
| P0 | 無（只讀 SKILL.md）— **但必須建立 Xcode 專案** |
| P1 | 無 |
| P2 | 無 |
| P2.5 | `docs/addendum/01_component_library.md` |
| P3 | 無 |
| P4 | 無 |
| P4.5 | `docs/addendum/03_tw_building_codes.md` |
| P4.8 | `docs/addendum/04_interactive_modify_and_monitoring.md` |
| P5 | 無 |
| P6 | `docs/addendum/02_sim_cost_mep.md` (成本段) |
| P7 | `docs/addendum/02_sim_cost_mep.md` (MEP 段) |
| P8 | `docs/addendum/02_sim_cost_mep.md` (施工模擬段) |
| P8.5 | `docs/addendum/04_interactive_modify_and_monitoring.md` (監控段) |

---

## ③ 文件上傳指引（給 Michael 手動執行）

```bash
cd ~/Documents/MyProjects/PromptBIMTestApp1
git pull origin main
unzip -o ~/Downloads/PromptBIMTestApp1_pending_docs.zip -d .
git add -A
git commit -m "[P0] Add SKILL.md v3.0 + addendum specs"
git push origin main
```

---

## ④ Sprint P0 啟動指令（含 Xcode 專案建立）

### 完整 P0 指令（複製貼上即可）

```
請讀取 PROMPT.md，先執行 Step 1 檢查所有文件。

然後讀取 SKILL.md、TODO.md、CLAUDE.md。

執行 Sprint P0 的所有 task，特別注意：

1. 建立 Xcode 專案:
   - 建立 PromptBIMTestApp1.xcodeproj (macOS app target, SwiftUI)
   - 建立 PromptBIMTestApp1App.swift (App entry point)
   - 建立 ContentView.swift (主介面骨架)
   - 建立 PythonBridge.swift (用 Process() 呼叫 Python 後端)
   - 建立 Info.plist, Assets.xcassets, Entitlements
   - 加入 Build Phase Script: conda activate promptbim && python -m pytest tests/ -v
   - 加入 Build Phase Script: conda activate promptbim && ruff check src/

2. 建立 Python 專案骨架:
   - 所有 src/promptbim/ 目錄和 __init__.py
   - pyproject.toml 依賴驗證
   - src/promptbim/__main__.py (CLI: gui / --version)
   - src/promptbim/config.py (Pydantic BaseSettings)
   - 基本 PySide6 主視窗可啟動

3. 驗證:
   - xcodebuild -project PromptBIMTestApp1.xcodeproj -scheme PromptBIMTestApp1 build
   - python -m pytest tests/ -v
   - python -m promptbim --version

4. 工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟:
   - xcodebuild BUILD SUCCEEDED
   - pytest 全部通過
   - 更新 TODO.md, CHANGELOG.md, README.md
   - git commit + push
   - 輸出下次繼續的 prompt
```

---

## ⑤ 其他 Sprint 快速啟動指令

**通用模板:**
```
請讀取 PROMPT.md，先執行 Step 1 檢查。
然後讀取 SKILL.md、TODO.md、CLAUDE.md、{Addendum}，
執行 Sprint P{X} 的所有 task。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
```

**P2.5 零件庫:**
```
請讀取 PROMPT.md，先執行 Step 1 檢查。
然後讀取 SKILL.md、TODO.md、CLAUDE.md、docs/addendum/01_component_library.md，
執行 Sprint P2.5 的所有 task。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
```

**P4.5 法規引擎:**
```
請讀取 PROMPT.md，先執行 Step 1 檢查。
然後讀取 SKILL.md、TODO.md、CLAUDE.md、docs/addendum/03_tw_building_codes.md，
執行 Sprint P4.5 的所有 task。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
```

---

## ⑥ Sprint 總覽與依賴

```
P0  專案骨架 + Xcode + 環境         (1天)  ← 無依賴
P1  土地匯入 + 2D 視圖             (3天)  ← P0
P2  IFC + USD 生成核心            (3天)  ← P0
P2.5 建築零件庫                    (3天)  ← P2
P3  3D 互動預覽                    (2天)  ← P2
P4  AI Agent Pipeline              (3天)  ← P1, P2
P4.5 台灣法規引擎                  (3天)  ← P4
P4.8 互動式修改引擎                (2天)  ← P4
P5  語音 + 匯出                    (2天)  ← P4
P6  成本估算 (5D)                 (2天)  ← P2.5
P7  MEP 管線自動生成               (4天)  ← P4
P8  施工模擬 (4D)                 (3天)  ← P2
P8.5 智慧監控點自動配置             (3天)  ← P4, P7
```

---

## ⑦ [MANDATORY] 工作結束規則（摘自 CLAUDE.md）

每次 Claude Code 工作結束前，**必須完整執行**以下步驟：

```
□ xcodebuild BUILD SUCCEEDED
□ pytest 全部通過
□ TODO.md 已更新（完成的 task 標記 ✅）
□ CHANGELOG.md 已更新（如果完成 Sprint）
□ README.md 已更新（如果功能變更）
□ SETUP.md 已更新（如果安裝步驟變更）
□ git commit + push 完成
□ 下次繼續的 prompt 已輸出到 terminal
```

**如果任何一項未完成，不得結束工作。**

---

## ⑧ 文件版本控制規則

| 文件 | 誰負責更新 | Claude Code 可改？ |
|------|-----------|:-----------------:|
| `SKILL.md` | 人工 | ❌ 禁止 |
| `PROMPT.md` | 人工 | ❌ 禁止 |
| `CLAUDE.md` | 人工 | ❌ 禁止 |
| `docs/addendum/*.md` | 人工 | ❌ 禁止 |
| `README.md` | **Claude Code** | ✅ 必須更新 |
| `TODO.md` | **Claude Code** | ✅ 必須更新 |
| `CHANGELOG.md` | **Claude Code** | ✅ 必須更新 |
| `SETUP.md` | **Claude Code** | ✅ 可更新 |
| `src/**/*.py` | **Claude Code** | ✅ 核心工作 |
| `*.swift` | **Claude Code** | ✅ Xcode 整合 |
| `*.xcodeproj` | **Claude Code** | ✅ 專案結構 |

---

*PROMPT.md v1.1.0 | 2026-03-25 | 新增 Xcode 專案建立 + [MANDATORY] 工作結束規則引用*
