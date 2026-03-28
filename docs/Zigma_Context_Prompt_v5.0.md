# Zigma PromptToBuild 專案接續開發 — Context Prompt v5.6

> **更新:** 2026-03-28 23:00 CST
> **前次對話:** Repo 遷移完成(兩台) + M1-SCENE Sprint 啟動
> **本文件用途:** 在新 Claude 對話中貼入，接續工作

---

## 第一步（新對話啟動必做）

```
github:get_file_contents → SKILL.md (預期 v4.2)
github:get_file_contents → PROJECT.md (預期 v1.8)
github:list_commits → HEAD ≥ 5d655da
```

---

## 角色

Michael Lin 的資深架構師與 CTO 顧問。負責 Sprint 審查、架構設計、PROMPT 建立、文件維護、GitHub MCP、Notion 同步。

## 專案資訊

| 項目 | 值 |
|------|---|
| 品牌 | **Zigma** (Reality Matrix Inc.) |
| GitHub | chchlin1018/PromptBIMTestApp1 (private) |
| HEAD | **5d655da** |
| Tags | **mvp-v0.1.0** + demo1-v0.1.0 + v2.12.0 |
| Notion | 330f154a-6472-81ae (workspace) / 320f154a-6472-804f (parent) |

## 治理文件

| 文件 | 版本 | 說明 |
|------|------|------|
| CLAUDE.md | **v1.23.3** | notify v2 heredoc + xcodebuild mutex + 三大鐵律 |
| SKILL.md | **v4.2** | M1-MVP Build 經驗 + iCloud Media + 4 Build Issues |
| PROJECT.md | **v1.8** | M1-SCENE 執行中 + MacBook 遷移完成 |

---

## 當前狀態

### ✅ 已完成

| Sprint | Tasks | 產出 | Tag |
|--------|:-----:|------|-----|
| M1-MVP | **68/68** ✅ | Qt Quick 3D + AgentBridge + 13 QML panels | **mvp-v0.1.0** |
| MEDIA-DL | **12/12** ✅ | 37 files (81MB) → iCloud ~/ZigmaMedia/ | media-v1.0 |
| D1-S2 | 14/14 ✅ | GUI + 3場景 + 60 tests | demo1-v0.1.0 |
| W0 | 5/5 ✅ | pytest + tag | v2.12.0 |

### 🔄 進行中

| Sprint | Tasks | 目標 | Tag |
|--------|:-----:|------|-----|
| **M1-SCENE** | **22T / 3 Parts** | 3D Demo Scene + Debug Logging | **mvp-v0.2.0** |

M1-SCENE 內容:
- **Part A:** ZigmaLogger C++ singleton → debuglog/zigma_*.log (C++/QML/Python AI)
- **Part B:** DemoScene.qml TSMC fab 場景 + BIMView3D Camera/Lights/Orbit
- **Part C:** 收尾 + tag

### 開發機路徑

| 機器 | Repo 路徑 | 狀態 |
|------|----------|:----:|
| **Mac Mini M4** | `~/Dev/PromptBIMTestApp1` | ✅ 已遷移 |
| **MacBook Air** | `~/Dev/PromptBIMTestApp1` | ✅ 已遷移 (fresh clone) |
| **Windows RTX4090** | `C:\Dev\PromptBIMTestApp1` | ⬜ 待設定 |

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

### .env
- 空的 ANTHROPIC_API_KEY 會讓 Claude Code 用它而非 Pro 訂閱 → .env 只放 `API_TIMEOUT_SECONDS=120`

### Git on Mac ✅ 已解決
- repo 已遷移到 `~/Dev/PromptBIMTestApp1`，git pull 秒完成

---

## 架構

```
zigma/ (Qt Quick 3D 前端, C++)
├── CMakeLists.txt
├── src/ (5+ headers + sources)
│   ├── main.cpp, AgentBridge, BIMSceneBuilder, BIMMaterialLibrary, BIMGeometryProvider
│   └── ZigmaLogger.h/.cpp (M1-SCENE 新增)
├── qml/ (14+ QML files)
│   ├── main.qml, BIMView3D, ChatPanel, PropertyPanel, CostPanel...
│   └── DemoScene.qml (M1-SCENE 新增)
└── tests/

agent_runner.py     ← Python↔C++ JSON stdio (含 debuglog logging)
src/promptbim/      ← Python AI engine
debuglog/           ← Runtime debug logs (M1-SCENE 新增)
~/ZigmaMedia/       ← iCloud 媒體資源
```

## MikeRunClaudeSafe

```bash
MikeRunClaudeSafe PromptBIMTestApp1 {Sprint} "指令" --conda promptbim --kill
# ANTHROPIC_MODEL=claude-opus-4-6 (in ~/.zshrc)
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

### 🔴 立即
1. M1-SCENE Sprint 完成 (執行中)
2. Sketchfab GLB 手動下載（8 個）
3. .env 補 ANTHROPIC_API_KEY

### 🟡 短期 Sprint
4. **M1-FIX (~15T):** Windows build + MediaManager C++
5. **M1-DEMO (~20T):** E2E Demo + TSMC 簡報 PPT

### 🔵 中期
6. **P30:** USD→Revit DirectShape + MEP
7. **P31:** OCCT Kernel B-Rep

### 🟢 長期
8. ILOS + Omniverse → Web → 私有 LLM

---

## Notion 同步

| 頁面 | ID |
|------|-----|
| M1-MVP 完成報告 | 331f154a-6472-81cc |
| 專案狀態總覽 | 331f154a-6472-81f5 |

---

*Context Prompt v5.6 | 2026-03-28*
*M1-MVP ✅ 68T | Repo ~/Dev/ ✅ | M1-SCENE 🔄 22T | SKILL v4.2*
