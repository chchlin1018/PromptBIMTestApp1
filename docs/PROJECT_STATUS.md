# PromptBIM 專案狀態報告

> **更新:** 2026-03-28 23:00 CST | **報告人:** Claude Opus 4.6
> **Repo:** chchlin1018/PromptBIMTestApp1 (private, main branch)

---

## 1. 版本狀態

| 項目 | 狀態 |
|------|------|
| 當前版本 | **mvp-v0.2.1** (M2-ENV Sprint 完成) |
| 下一版本 | **mvp-v0.3.0** (M1-FIX Sprint) |
| POC 版本 | v2.12.0 ✅ **已 tag** |
| CLAUDE.md | **v1.23.3** |
| SKILL.md | **v4.2** |
| PROJECT.md | **v1.8** |
| Context Prompt | **v5.5** |

---

## 2. Sprint 進度

| Sprint | 版本 | 狀態 | 說明 |
|--------|------|------|------|
| P0~P25 | v0.1.0~v2.12.0 | ✅ 完成 | 全部已 tag |
| W0 | — | ✅ 完成 | POC 收尾 |
| D1-S1 | demo1-alpha | ✅ 完成 | AI場景+Cost+4D |
| D1-S2 | demo1-v0.1.0 | ✅ 完成 | GUI+TSMC展示 |
| **M1-MVP** | **mvp-v0.1.0** | **✅ 完成** | **68T/9Parts Qt Quick 3D** |
| **MEDIA-DL** | **media-v1.0** | **✅ 完成** | **37 files/81MB iCloud** |
| **M1-SCENE** | **mvp-v0.2.0** | **✅ 完成** | **22T: 3D Demo + Debug Logging** |
| **M2-ENV** | **mvp-v0.2.1** | **✅ 完成** | **8T: 環境驗證 + Agent Runner** |
| M1-FIX | — | ⬜ 待規劃 | Windows build + 整合 |
| M1-DEMO | — | ⬜ 待規劃 | TSMC Demo 排練 |

### M1-MVP Sprint — 2026-03-28 03:04

- **Tasks:** 68/68 ✅
- **時間:** ~40 分鐘 (Opus 4.6)
- **Tags:** mvp-v0.1.0-alpha, mvp-v0.1.0-beta, mvp-v0.1.0
- **Build:** CMake+Ninja OK, 2 ctests PASS
- **產出:** 5 C++ + 13 QML + 2 Python + io_usd module

### MEDIA-DL Sprint — 2026-03-28 10:46

- **Tasks:** 12/12 ✅
- **時間:** ~6 分鐘
- **產出:** 37 files (81MB) → ~/ZigmaMedia/ (iCloud)
- **manifest.json** SSOT 已同步

### MacBook Build 驗證 — 2026-03-28 12:00

- **cmake + ninja:** ✅ 62/62 build 成功
- **ctest:** ✅ 2/2 PASS
- **ZigmaApp:** ✅ GUI 三欄佈局 + Metal 渲染正常

### M1-SCENE Sprint — 2026-03-28 完成

- **Tasks:** 22/22 ✅
- **時間:** ~10 分鐘 (Opus 4.6)
- **Tags:** mvp-v0.2.0
- **Build:** CMake+Ninja OK, 2 ctests PASS
- **Part A (T1-9):** ZigmaLogger C++ singleton — Debug Log to File ✅
- **Part B (T10-16):** DemoScene.qml — TSMC fab 3D 場景 ✅
- **Part C (T17-22):** 收尾 + tag ✅
- **產出:** ZigmaLogger.h/.cpp + DemoScene.qml + BIMView3D rewrite + Python logging

### M2-ENV Sprint — 2026-03-28 完成

- **Tasks:** 8/8 ✅
- **版本:** mvp-v0.2.1
- **環境檢查結果:**
  - .env: ✅ API_TIMEOUT_SECONDS=120 + ANTHROPIC_API_KEY present
  - conda promptbim: ✅ Python 3.11.15 + anthropic 0.86 + PySide6 6.11 + usd-core 26.3
  - agent_runner.py: ✅ import OK (root-level)
  - CMake+Ninja: ✅ 6 targets built, 14/14 ctests PASS
  - ~/ZigmaMedia/: ✅ exists (10 subdirs from MEDIA-DL)
- **GTest:** installed via brew (was missing)

---

## 3. Build 經驗教訓

| ID | 問題 | 解法 | 狀態 |
|----|------|------|:----:|
| BUILD-001 | CMake Ninja regeneration 路徑 | C++ 絕對路徑 + QML 相對路徑 | ✅ |
| BUILD-002 | QML onPropertyChanged 位置 | handler 放 property 所有者(root) | ✅ |
| BUILD-003 | loadFromModule 找不到 "main" | 改用 QUrl qrc:/Zigma/qml/main.qml | ✅ |
| BUILD-004 | .env 空 API key | 移除空 key，只留 TIMEOUT | ✅ |
| **BUILD-005** | **git pull iCloud 卡住** | **repo 遷移到 ~/Dev/** | **✅ 已解決** |
| BUILD-006 | git index.lock 殘留 | rm .git/index.lock + checkout -- . | ✅ |

---

## 4. 開發機路徑與 Build 環境

| 機器 | Repo 路徑 | Build | Test | Run | 狀態 |
|------|----------|:-----:|:----:|:---:|:----:|
| **Mac Mini M4** | **~/Dev/PromptBIMTestApp1** | ✅ Ninja+Metal | ✅ 2 ctest + 18 pytest | ✅ ZigmaApp | ✅ 已遷移 |
| **MacBook Air** | **~/Dev/PromptBIMTestApp1** | ✅ Ninja+Metal | ✅ 2 ctest | ✅ ZigmaApp | ✅ 已遷移 (fresh clone) |
| Windows RTX4090 | — | ⬜ | ⬜ | ⬜ | alpha 後 |

### Repo 遷移記錄 — 2026-03-28

- **原因:** `~/Documents/` 被 iCloud Drive 同步 → git pull 卡死
- **解法:** mv 到 `~/Dev/PromptBIMTestApp1`
- **Mac Mini:** ✅ mv 遷移，git pull 秒完成
- **MacBook:** ✅ fresh clone（原目錄是 iCloud 同步殘片，無 .git）

---

## 5. 治理框架

| 文件 | 版本 | 核心規則 |
|------|------|----------|
| CLAUDE.md | v1.23.3 | 28 步流程 + notify + 鐵律 |
| SKILL.md | **v4.2** | M1-MVP Build 經驗 + iCloud Media |

---

## 6. 媒體資源

| 項目 | 狀態 |
|------|------|
| iCloud ~/ZigmaMedia/ | ✅ 37 files (81MB) |
| media/manifest.json | ✅ SSOT 同步 |
| Poly Haven PBR (10) | ✅ 自動下載 |
| Poly Haven HDRI (3) | ✅ 自動下載 |
| Branding (4) | ✅ 自動建立 |
| Sketchfab GLB (8 🔴) | ⬜ 需手動下載 |

---

## 7. 下一步

| 優先級 | 項目 | 時間 |
|--------|------|------|
| ✅ | M1-SCENE Sprint 完成 | 2026-03-28 |
| 🔴 | Sketchfab 8 GLB 手動下載 | 30 min |
| 🔴 | .env 補 ANTHROPIC_API_KEY | 2 min |
| 🟡 | Sprint M1-FIX (15T): Windows build + MediaManager | 本週 |
| 🟡 | Sprint M1-DEMO (20T): E2E Demo + TSMC 簡報 | 下週 |
| 🔵 | Sprint P30 (25T): USD→Revit | Week 3-4 |

---

## 8. Notion 同步

| Notion 頁面 | ID | 內容 |
|-------------|-----|------|
| Workspace Root | 330f154a-6472-81ae | — |
| Zigma Parent | 320f154a-6472-804f | MeetingCopilot + Zigma 報告 |
| M1-MVP 完成報告 | 331f154a-6472-81cc | Sprint 68T 完成 |
| 專案狀態總覽 | 331f154a-6472-81f5 | 今日全面更新 (本次) |

---

*docs/PROJECT_STATUS.md v1.10 | 2026-03-28 CST*
*M1-MVP ✅ | MEDIA-DL ✅ | M1-SCENE ✅ | M2-ENV ✅ | Repo ~/Dev/ ✅*
