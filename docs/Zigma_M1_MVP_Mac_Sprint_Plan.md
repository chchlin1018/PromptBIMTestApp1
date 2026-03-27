# Zigma M1 MVP — Mac Mini 一次性 Sprint 計劃

> **版本:** v1.0 | **日期:** 2026-03-28
> **執行環境:** Mac Mini M4 (16GB) | macOS | Metal
> **總 Tasks:** 68/70 (排除 2 個 Windows-only)
> **預估時間:** 6-10 小時 Claude Code 連續執行

---

## 排除的 2 個 Windows-Only Tasks

| 原 # | ID | Task | 原因 | 何時手動做 |
|------|-----|------|------|----------|
| 25 | S1-C-T25 | Win build 驗證 (D3D12/Vulkan) | 需要 MSVC + RTX 4090 | alpha 後去 Windows |
| 61 | S3-B-T11 | RTX 4090 GPU 渲染優化 FPS≥30 | 需要 Vulkan/D3D12 tuning | release 前去 Windows |

---

## Sprint 結構: 9 Parts / 68 Tasks

### Part A: AgentBridge — Python↔C++ 通訊 (8T)

| # | Task | 驗收 |
|---|------|------|
| 1 | CMakeLists.txt: Qt6 Quick + Quick3D + Core + ShaderTools | cmake 成功 |
| 2 | AgentBridge C++: QProcess spawn, JSON stdio, heartbeat 120s | Python crash 不影響 GUI |
| 3 | agent_runner.py: asyncio → orchestrator, streaming | 能接收 generate/modify |
| 4 | JSON Protocol schema 定義 | 文件完成 |
| 5 | mesh 序列化: Python mesh → JSON vertex/index | 格式正確 |
| 6 | AgentBridge ctest ≥5 | ctest PASS |
| 7 | agent_runner pytest ≥5 | pytest PASS |
| 8 | E2E: prompt → Python → JSON → C++ | 端到端通過 |

→ `git commit -m "[M1] Part A: AgentBridge" && git push`

### Part B: Qt Quick 3D 渲染核心 (8T)

| # | Task | 驗收 |
|---|------|------|
| 9 | BIMGeometryProvider : QQuick3DGeometry, loadFromJSON | mesh 渲染 |
| 10 | BIMMaterialLibrary: concrete/glass/steel/wood → PBR | 4 種材質 |
| 11 | BIMSceneBuilder: JSON → Model QML nodes | 多元素場景 |
| 12 | BIMView3D.qml: View3D + Camera + OrbitController | 旋轉縮放 |
| 13 | Picking: View3D pick → element ID | 點擊選取 |
| 14 | 多視角: Perspective/Top/Front/Right | 4 視角 |
| 15 | benchmark: Fab 場景 < 300MB | 記憶體達標 |
| 16 | ctest ≥10 | ctest PASS |

→ `git commit -m "[M1] Part B: Qt Quick 3D renderer" && git push`

### Part C: QML GUI 骨架 (8T, 排除 T25 Win)

| # | Task | 驗收 |
|---|------|------|
| 17 | main.qml: SplitView (Chat/3D/Property) | 三欄佈局 |
| 18 | ChatPanel.qml: TextInput + streaming + 歷史 | 可對話 |
| 19 | PropertyPanel.qml: 點擊 → 屬性顯示 | 屬性正確 |
| 20 | StatusBar.qml: 記憶體/AI狀態/進度 | 狀態可見 |
| 21 | ChatPanel ↔ AgentBridge 連接 | prompt 可發送 |
| 22 | BIMView3D ↔ BIMSceneBuilder 連接 | AI 結果可渲染 |
| 23 | Picking → PropertyPanel 連接 | 點擊顯示屬性 |
| 24 | 🍎 Mac build 驗證 (Metal) | build + run |

→ `git commit -m "[M1] Part C: QML GUI skeleton" && git push`
→ 🏷️ `git tag mvp-v0.1.0-alpha`

---

### Part D: CostPanel + DeltaPanel (8T)

| # | Task | 驗收 |
|---|------|------|
| 25 | CostPanel.qml: NT$ + 圓餅圖 | 成本可見 |
| 26 | DeltaPanel.qml: Before/After + Undo | Delta 正確 |
| 27 | Modifier E2E: "變更游泳池" → delta → 3D | 端到端 |
| 28 | Cost 資料綁定: Python → JSON → QML | 即時更新 |
| 29 | Delta 動畫: 數字滾動 + 色彩 | 視覺回饋 |
| 30 | Undo/Redo stack: 10 次 | 可撤銷 |
| 31 | 多次修改累計 Delta 歷史 | 歷史可見 |
| 32 | ctest ≥5 | PASS |

→ `git commit -m "[M1] Part D: CostPanel + DeltaPanel" && git push`

### Part E: SchedulePanel + 4D (8T)

| # | Task | 驗收 |
|---|------|------|
| 33 | SchedulePanel.qml: 甘特圖 + 16-phase | 甘特圖正確 |
| 34 | 4D Timeline Slider + Play/Pause + 速度 | 動畫播放 |
| 35 | Gantt ↔ 3D 雙向聯動 | 點擊同步 |
| 36 | 施工機械 3D 隨 timeline | 機械動畫 |
| 37 | Phase 顏色: 實色/半透明/隱藏 | 視覺正確 |
| 38 | 截圖匯出 → PNG | 可匯出 |
| 39 | schedule 資料綁定 | 即時更新 |
| 40 | ctest ≥5 | PASS |

→ `git commit -m "[M1] Part E: SchedulePanel + 4D" && git push`

### Part F: TSMC Demo 場景 (9T)

| # | Task | 驗收 |
|---|------|------|
| 41 | ScenePicker.qml: S1/S2/S3 | 可切換 |
| 42 | S2 半導體廠房全流程 | 3D+成本+4D |
| 43 | S3 數據中心驗證 | 全流程 |
| 44 | S1 別墅驗證 | 全流程 |
| 45 | 修改 E2E: "2F 高度→6m" | Delta 正確 |
| 46 | 修改 E2E: "游泳池→停車場" | Delta 正確 |
| 47 | AssetBrowser.qml: 搜尋+替換 | 替換可用 |
| 48 | 法規面板: TW-IND-001~004 | 法規顯示 |
| 49 | 7 分鐘 Demo 腳本 v1 walkthrough | 無中斷 |

→ `git commit -m "[M1] Part F: TSMC Demo scenes" && git push`
→ 🏷️ `git tag mvp-v0.1.0-beta`

---

### Part G: io_usd — ILOS USD I/O (6T)

| # | Task | 驗收 |
|---|------|------|
| 50 | io_usd import: ILOS USD + ilos: metadata | metadata 正確 |
| 51 | io_usd import: /Connections/ 解析 | 連接點正確 |
| 52 | io_usd import: Instance 解析 | 座標正確 |
| 53 | io_usd export: mesh → USD | Omniverse 可開 |
| 54 | ILOS_Test_Pipeline_v4.usda 載入 | 完整渲染 |
| 55 | ilos: metadata → PropertyPanel | 可見 |

→ `git commit -m "[M1] Part G: io_usd ILOS support" && git push`

### Part H: 展示打磨 (7T, 排除 T11 Win GPU)

| # | Task | 驗收 |
|---|------|------|
| 56 | Dark/Light theme | 兩主題 |
| 57 | Loading animation | 進度可見 |
| 58 | 歡迎畫面: Zigma 品牌 | 品牌顯示 |
| 59 | 鍵盤快捷鍵 Space/F/1-4 | 操作順暢 |
| 60 | 🍎 Mac Metal 渲染驗證 | Mac 可用 |
| 61 | 記憶體 profiling < 500MB | 不 OOM |
| 62 | crash recovery: Python crash → 自動重啟 | 穩定 |

→ `git commit -m "[M1] Part H: Polish + crash recovery" && git push`

### Part I: Release (6T)

| # | Task | 驗收 |
|---|------|------|
| 63 | E2E: 3場景 × 2修改 = 6 scenarios | 全部通過 |
| 64 | Demo 腳本 v2.0 | 7 分鐘無中斷 |
| 65 | TSMC 簡報 v2.0 | 10 頁更新 |
| 66 | SKILL.md v5.0 | 推送 |
| 67 | PROJECT.md 更新 | 推送 |
| 68 | git tag mvp-v0.1.0 | ★ tag 存在 |

→ `git commit -m "[M1] Part I: Release mvp-v0.1.0" && git push`
→ 🏷️ `git tag mvp-v0.1.0` ★

---

## 通知密度

每個 Task: `task_start()` + `task_done()` = **136 條 iMessage**
每個 Part: `part_start()` + `part_done()` = **18 條 iMessage**
Sprint 啟動/完成: **2 條**

**合計: ~156 條 iMessage 通知**

## Tags 產出 (3 個)

| Tag | 產出時間 | Demo 能力 |
|-----|---------|----------|
| `mvp-v0.1.0-alpha` | Part C 後 | prompt → 3D → 旋轉/點擊 |
| `mvp-v0.1.0-beta` | Part F 後 | ★ TSMC 7 分鐘完整 Demo |
| `mvp-v0.1.0` ★ | Part I 後 | 正式 TSMC Demo + USD |

## 執行前必做

```bash
# 1. 安裝環境
brew install cmake ninja
# + Qt 6.7 Online Installer (含 Quick3D + ShaderTools)

# 2. 驗證環境
chmod +x scripts/m1_preflight_check.sh
./scripts/m1_preflight_check.sh

# 3. 全部 ✅ 後啟動
MikeRunClaudeSafe PromptBIMTestApp1 M1-MVP "..." --conda promptbim --kill
```

## Sprint 完成後手動做

1. 🪟 Windows RTX 4090: build + run 驗證 (alpha 的 T25)
2. 🪟 Windows RTX 4090: GPU 優化 FPS≥30 (release 的 T11)
3. 確認 3 個 git tags 存在

---

*Zigma M1 MVP Mac Sprint Plan v1.0 | 2026-03-28*
*68 Tasks / 9 Parts / 3 Tags / ~156 iMessage notifications*
