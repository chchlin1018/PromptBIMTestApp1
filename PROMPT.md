# PROMPT.md — Claude Code 執行指令

> **版本:** v1.0.0 | **更新:** 2026-03-25
> **版本控制:** 本文件任何修改必須更新版本號和日期，並同步更新 CLAUDE.md

---

## ① 專案概述

本專案是 **PromptBIMTestApp1**，一個 AI 驅動的 BIM 建築模型自動生成器 (POC)。
用戶只需輸入土地資料 + 一句 Prompt，系統自動完成所有建築設計、BIM 模型、MEP 管線、法規檢查、施工模擬 (4D)、成本估算 (5D)、監控點配置。

---

## ② 執行前檢查清單

Claude Code 在開始任何開發任務前，**必須先執行以下檢查**：

### Step 1: 驗證核心文件存在

```bash
# 檢查所有必要文件是否存在
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
  echo "⚠️ $missing 個文件缺失！請先解壓縮並提交待推送文件。"
  echo "參考 PROMPT.md ③ 的上傳指引。"
  exit 1
fi
echo ""
echo "✅ 所有 ${#required_files[@]} 個必要文件都存在，可以開始開發！"
```

### Step 2: 讀取知識庫

```
必讀順序:
1. SKILL.md          ← 專案 SSOT (架構、Schema、Agent Prompt、開發規範)
2. TODO.md           ← 確認當前 Sprint 狀態
3. CLAUDE.md         ← 開發行為規範
4. 對應的 Addendum   ← 依當前 Sprint 決定讀哪一份
```

| Sprint | 必讀 Addendum |
|--------|----------------|
| P0 | 無（只讀 SKILL.md） |
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

以下文件已打包為 `PromptBIMTestApp1_pending_docs.zip`，需要手動解壓縮並推送到 GitHub：

```bash
# 1. 進入專案目錄
cd ~/Documents/MyProjects/PromptBIMTestApp1
git pull origin main

# 2. 解壓縮 ZIP（覆蓋到專案根目錄）
unzip -o ~/Downloads/PromptBIMTestApp1_pending_docs.zip -d .

# 3. 驗證文件
 ls -la SKILL.md
 ls -la docs/addendum/01_component_library.md
 ls -la docs/addendum/02_sim_cost_mep.md
 ls -la docs/addendum/03_tw_building_codes.md

# 4. 提交並推送
git add -A
git commit -m "[P0] Add SKILL.md v3.0 + addendum specs (component library, sim/cost/MEP, TW building codes)"
git push origin main

# 5. 驗證 GitHub 上的文件
open https://github.com/chchlin1018/PromptBIMTestApp1
```

---

## ④ 開發執行指令（給 Claude Code）

### 啟動某個 Sprint 的標準指令

```
請讀取以下文件，然後執行 Sprint [P編號]:

1. cat SKILL.md
2. cat TODO.md
3. cat docs/addendum/[XX_對應附錄].md  (如果該 Sprint 有對應附錄)
4. cat CLAUDE.md

然後開始執行 TODO.md 中該 Sprint 的所有 task。
每完成一個 task 就 commit 並更新 TODO.md 狀態。
Sprint 全部完成後更新 CHANGELOG.md。
```

### 快速開始指令（複製貼上即可）

**P0 開始:**
```
請讀取 PROMPT.md，先執行 Step 1 檢查所有文件是否存在。
如果全部通過，讀取 SKILL.md 和 TODO.md，然後執行 Sprint P0 的所有 task。
```

**P2.5 開始:**
```
請讀取 PROMPT.md，先執行 Step 1 檢查。
然後讀取 SKILL.md、TODO.md、docs/addendum/01_component_library.md，
執行 Sprint P2.5 的所有 task。
```

**P4.5 開始:**
```
請讀取 PROMPT.md，先執行 Step 1 檢查。
然後讀取 SKILL.md、TODO.md、docs/addendum/03_tw_building_codes.md，
執行 Sprint P4.5 的所有 task。
```

---

## ⑤ Sprint 總覽與依賴

```
P0  專案骨架 + 環境               (1天)  ← 無依賴
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

## ⑥ 文件版本控制規則

| 文件 | 誰負責更新 | 何時更新 | 版本格式 |
|------|-----------|----------|----------|
| `SKILL.md` | 人工 | 架構變更 | vX.Y.Z |
| `PROMPT.md` | 人工 | Sprint 流程變更 | vX.Y.Z |
| `CLAUDE.md` | 人工 | 開發規範變更 | vX.Y.Z |
| `TODO.md` | Claude Code | 每完成 1 個 task | 自動 |
| `CHANGELOG.md` | Claude Code | 每完成 1 個 Sprint | Semver |
| `SETUP.md` | Claude Code | 安裝步驟變更 | vX.Y.Z |
| `docs/addendum/*.md` | 人工 | 規格變更 | vX.Y |

**Claude Code 不得修改**: SKILL.md, PROMPT.md, CLAUDE.md, docs/addendum/*.md
**Claude Code 必須更新**: TODO.md (每個 task), CHANGELOG.md (每個 Sprint)

---

*PROMPT.md v1.0.0 | 2026-03-25 | Claude Code 執行指令檔*
