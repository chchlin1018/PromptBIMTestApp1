# PromptBIM 專案狀態報告

> **更新:** 2026-03-28 22:00 CST | **報告人:** Claude Opus 4.6
> **Repo:** chchlin1018/PromptBIMTestApp1 (private, main branch)

---

## 1. 版本狀態

| 項目 | 狀態 |
|------|------|
| 當前版本 | **mvp-v0.1.0** (M1-MVP Sprint 完成) |
| POC 版本 | v2.12.0 ✅ **已 tag** |
| CLAUDE.md | **v1.23.3** |
| SKILL.md | **v4.2** |
| PROJECT.md | **v1.7** |

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

---

## 3. Build 經驗教訓

| ID | 問題 | 解法 | 狀態 |
|----|------|------|:----:|
| BUILD-001 | CMake Ninja regeneration 路徑 | C++ 絕對路徑 + QML 相對路徑 | ✅ |
| BUILD-002 | QML onPropertyChanged 位置 | handler 放 property 所有者(root) | ✅ |
| BUILD-003 | loadFromModule 找不到 "main" | 改用 QUrl qrc:/Zigma/qml/main.qml | ✅ |
| BUILD-004 | .env 空 API key | 移除空 key，只留 TIMEOUT | ✅ |
| **BUILD-005** | **git pull iCloud 卡住** | **repo 遷移到 ~/Dev/（不被 iCloud 同步）** | **✅ 已解決** |
| BUILD-006 | git index.lock 殘留 | rm .git/index.lock + checkout -- . | ✅ |

---

## 4. 開發機路徑與 Build 環境

| 機器 | Repo 路徑 | Build | Test | Run | 狀態 |
|------|----------|:-----:|:----:|:---:|:----:|
| **Mac Mini M4** | **~/Dev/PromptBIMTestApp1** | ✅ Ninja+Metal | ✅ 2 ctest + 18 pytest | ✅ ZigmaApp | ✅ 已遷移 |
| **MacBook Air** | ~/Documents/MyProjects/... | ✅ Ninja+Metal | ✅ 2 ctest | ✅ ZigmaApp | ⬜ 待遷移 ~/Dev/ |
| Windows RTX4090 | — | ⬜ | ⬜ | ⬜ | alpha 後 |

### Repo 遷移記錄 — 2026-03-28 22:00

- **原因:** `~/Documents/` 被 iCloud Drive 同步，git checkout 觸發 iCloud 上傳 → I/O 阻塞 → git pull 卡死
- **解法:** `mv ~/Documents/MyProjects/PromptBIMTestApp1 ~/Dev/PromptBIMTestApp1`
- **結果:** git pull 從 3+ 分鐘卡死 → 秒完成 ✅
- **symlink:** `~/Documents/MyProjects/PromptBIMTestApp1` → `~/Dev/PromptBIMTestApp1` (向後相容，待補建)

---

## 5. 治理框架

| 文件 | 版本 | 核心規則 |
|------|------|----------|
| CLAUDE.md | v1.23.3 | 28 步流程 + notify + 鐵律 |
| SKILL.md | **v4.2** | v4.1 + M1-MVP Build 經驗 + iCloud Media |

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
| 🔴 | Sketchfab 8 GLB 手動下載 | 30 min |
| 🔴 | .env 補 ANTHROPIC_API_KEY | 2 min |
| 🔴 | MacBook repo 遷移到 ~/Dev/ | 5 min |
| 🔴 | MikeRunClaudeSafe 路徑確認/更新 | 5 min |
| 🟡 | Sprint M1-FIX (15T): Windows build + MediaManager | 本週 |
| 🟡 | Sprint M1-DEMO (20T): E2E Demo + TSMC 簡報 | 下週 |
| 🔵 | Sprint P30 (25T): USD→Revit | Week 3-4 |

---

*docs/PROJECT_STATUS.md | 2026-03-28 22:00 CST*
