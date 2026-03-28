# Zigma PromptToBuild 專案接續開發 — Context Prompt v5.5

> **更新:** 2026-03-28 22:00 CST
> **前次對話:** Repo 遷移 ~/Dev/ + git pull 速度修復
> **本文件用途:** 在新 Claude 對話中貼入，接續工作

---

## 第一步（新對話啟動必做）

```
github:get_file_contents → SKILL.md (預期 v4.2)
github:get_file_contents → PROJECT.md (預期 v1.7)
github:list_commits → HEAD ≥ (本次 commit)
```

---

## 角色

Michael Lin 的資深架構師與 CTO 顧問。負責 Sprint 審查、架構設計、PROMPT 建立、文件維護、GitHub MCP、Notion 同步。

## 專案資訊

| 項目 | 值 |
|------|---|
| 品牌 | **Zigma** (Reality Matrix Inc.) |
| GitHub | chchlin1018/PromptBIMTestApp1 (private) |
| Tags | **mvp-v0.1.0** + mvp-v0.1.0-alpha + mvp-v0.1.0-beta + demo1-v0.1.0 + v2.12.0 |
| Notion | 330f154a-6472-81ae (workspace root) / 320f154a-6472-804f (parent page) |

## 治理文件

| 文件 | 版本 | 說明 |
|------|------|------|
| CLAUDE.md | **v1.23.3** | notify v2 heredoc + xcodebuild mutex + 三大鐵律 |
| SKILL.md | **v4.2** | M1-MVP Build 經驗 + iCloud Media + 4 Build Issues |
| PROJECT.md | **v1.7** | repo 遷移 ~/Dev/ 完成 |

---

## 當前狀態

### ✅ 已完成

| Sprint | Tasks | 產出 | Tag |
|--------|:-----:|------|-----|
| M1-MVP | **68/68** ✅ | Qt Quick 3D + AgentBridge + 13 QML panels | **mvp-v0.1.0** |
| MEDIA-DL | **12/12** ✅ | 37 files (81MB) → iCloud ~/ZigmaMedia/ | media-v1.0 |
| D1-S2 | 14/14 ✅ | GUI + 3場景 + 60 tests | demo1-v0.1.0 |
| W0 | 5/5 ✅ | pytest + tag | v2.12.0 |

### M1-MVP 產出

**C++ (zigma/src/):** main.cpp, AgentBridge.h/.cpp (QProcess+JSON+120s heartbeat+3x crash recovery), BIMGeometryProvider.h/.cpp (QQuick3DGeometry), BIMMaterialLibrary.h/.cpp, BIMSceneBuilder.h/.cpp

**QML (zigma/qml/, 13 files):** main.qml, BIMView3D, ChatPanel, PropertyPanel, CostPanel, DeltaPanel, SchedulePanel, StatusBar, ScenePicker, AssetBrowser, ThemeManager, LoadingOverlay, SplashScreen

**Python:** agent_runner.py (JSON stdio bridge), mesh_serializer.py (Plan→mesh)

**io_usd:** src/promptbim/bim/io_usd/ (ILOS USD import/export)

### 媒體資源

- iCloud Drive ~/ZigmaMedia/ — 三平台同步 (Mac Mini/MacBook/Windows)
- media/manifest.json (GitHub SSOT) — 37 files, 81MB
- textures 10套 PBR + hdri 3個 + branding 4個
- Sketchfab GLB 8個 🔴 必備 — **尚未手動下載**

### Build 驗證

| 機器 | Build | Test | Run | 狀態 |
|------|:-----:|:----:|:---:|:----:|
| Mac Mini M4 | ✅ Ninja+Metal | ✅ 2 ctest + 18 pytest | ✅ | 主開發機 |
| MacBook Air | ✅ Ninja+Metal | ✅ 2 ctest | ✅ ZigmaApp GUI 正常 | 驗證通過 |
| Windows RTX4090 | ⬜ | ⬜ | ⬜ | 待驗證 |

---

## ★★★ 關鍵 Build 經驗（必讀）★★★

### CMakeLists.txt
- C++ source 用 `${CMAKE_CURRENT_SOURCE_DIR}/` 絕對路徑
- QML files 用相對路徑 `qml/main.qml`
- find_package 必須含 `ShaderTools`

### QML
- Canvas 裡不能放 root property 的 `onXxxChanged` handler → 移到 root Rectangle

### main.cpp
- 正確 QRC 路徑: `qrc:/Zigma/qml/main.qml`
- `loadFromModule("Zigma", "main")` 不行（小寫 main）

### .env
- 空的 ANTHROPIC_API_KEY 會讓 Claude Code 用它而非 Pro 訂閱 → `Invalid API key`
- .env 只放 `API_TIMEOUT_SECONDS=120`

### Git on Mac ✅ 已解決
- ~~`~/Documents/` 被 iCloud 同步會導致 git pull 卡住~~
- **已解決 (2026-03-28):** repo 已遷移到 `~/Dev/PromptBIMTestApp1`
- `~/Dev/` 不被 iCloud 同步，git pull 秒完成
- symlink: `~/Documents/MyProjects/PromptBIMTestApp1` → `~/Dev/PromptBIMTestApp1` (向後相容)
- git pull 卡住後 `Ctrl+C` 會中斷 checkout → 需要 `rm .git/index.lock` + `git checkout -- .`

---

## 架構

```
zigma/ (Qt Quick 3D 前端, C++)
├── CMakeLists.txt
├── src/ (5 headers + 5 sources)
├── qml/ (13 QML files)
└── tests/ (2 test executables)

agent_runner.py     ← Python↔C++ JSON stdio
mesh_serializer.py  ← BuildingPlan→vertex/index
src/promptbim/      ← Python AI engine (不變)
  ├── agents/       ← 7 agents
  ├── bim/io_usd/   ← ILOS USD import/export
  └── ...

~/ZigmaMedia/ (iCloud) ← 媒體資源
media/manifest.json    ← SSOT (GitHub)
```

## 開發機路徑

| 機器 | Repo 路徑 | 狀態 |
|------|----------|:----:|
| **Mac Mini M4** | `~/Dev/PromptBIMTestApp1` | ✅ 已遷移 |
| **MacBook Air** | `~/Dev/PromptBIMTestApp1` | ⬜ 待遷移 |
| **Windows RTX4090** | `C:\Dev\PromptBIMTestApp1` | ⬜ 待設定 |

## MikeRunClaudeSafe

```bash
MikeRunClaudeSafe PromptBIMTestApp1 {Sprint} "指令" --conda promptbim --kill
# conda activate + source .env + claude --dangerously-skip-permissions -p "..."
# ANTHROPIC_MODEL=claude-opus-4-6 (in ~/.zshrc)
# ⚠️ 腳本 base path 可能需要從 ~/Documents/MyProjects → ~/Dev 更新
```

## Mac Mini Build

```bash
cd ~/Dev/PromptBIMTestApp1/zigma
rm -rf build && mkdir build && cd build
cmake .. -G Ninja -DCMAKE_PREFIX_PATH=/opt/homebrew/opt/qt
ninja && ctest --output-on-failure && ./ZigmaApp
```

---

## 待辦

### 🔴 立即（手動）
1. Sketchfab GLB 手動下載（8 個 🔴 必備模型）
2. Mac Mini .env 補 ANTHROPIC_API_KEY
3. ~~Mac Mini git 穩定性（搬 repo 到 ~/Dev/）~~ ✅ 已完成
4. MacBook 也搬 repo 到 ~/Dev/
5. 確認 MikeRunClaudeSafe 路徑

### 🟡 短期 Sprint
6. **M1-FIX (~15T):** Windows build + MediaManager C++ + ctest 增加
7. **M1-DEMO (~20T):** E2E Demo + TSMC 簡報 PPT + 7min Demo 排練

### 🔵 中期 Phase 2
8. **P30 (~25T):** io_revit: USD→Revit DirectShape + MEP
9. **P31 (~25T):** OCCT Kernel: B-Rep + vcpkg
10. **P32-P33:** 清理 + Windows installer

### 🟢 長期
11. PH3: ILOS + Omniverse
12. PH4: Web + Mobile
13. PH5: 私有 LLM

---

## GitHub 文件索引

| 文件 | 版本/狀態 |
|------|----------|
| CLAUDE.md | v1.23.3 |
| SKILL.md | **v4.2** |
| PROJECT.md | **v1.7** |
| Context Prompt | **v5.5** (本文件) |
| zigma/CMakeLists.txt | 修正版 (絕對C++ + 相對QML + ShaderTools) |
| zigma/src/main.cpp | 修正版 (qrc:/Zigma/qml/main.qml) |
| zigma/qml/CostPanel.qml | 修正版 (onBreakdownChanged→root) |
| zigma/qml/SchedulePanel.qml | 修正版 (onPhasesChanged→root) |
| media/manifest.json | 37 files / 81MB |
| docs/Zigma_Windows_Checklist.md | v1.0 |
| docs/Zigma_Media_Asset_Workflow.md | v1.0 |
| sprints/PROMPT_M1-MVP.md | 68T 完成 |
| sprints/PROMPT_MEDIA-DL.md | 12T 完成 |

---

*Context Prompt v5.5 | 2026-03-28*
*M1-MVP ✅ 68T | MEDIA-DL ✅ 37files | MacBook Build ✅ | Repo ~/Dev/ ✅ | SKILL v4.2*
