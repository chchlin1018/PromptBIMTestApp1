# Zigma PromptToBuild — SKILL.md v4.1

> Claude Code SSOT — 開發前必讀
> 最後更新: 2026-03-27 (v4.1 — ADR-001 Qt Quick 3D + notify v2 + xcodebuild mutex + safe_pytest_dir + OOM 診斷)

---

## 0. [MANDATORY] 專案治理框架 (v4.1)

### 0.1 Zigma 品牌架構

```
Zigma（整體解決方案品牌）— Reality Matrix Inc.
├── Zigma Core          — 共用底層框架（Plugin Bus + 6 介面 + USD Stage）
├── Zigma PromptToBuild — 設計→建造→交付（AI 建築/工廠規劃）
├── Zigma PromptToOperate — 交付→營運→維護→退役（即時監控/預測）
├── Zigma Cloud         — 雲端基礎設施（Session + Auth + Deploy）
└── Zigma NDH           — IDTF Neutral Data Hub（資料匯流排）
```

### 0.2 治理文件體系

```
CLAUDE.md (憲法 — 不可自動修改) v1.23.3
    │ 規範
    ▼
SKILL.md (百科 — 技術 SSOT) v4.1       ← 你在讀這份
    │ 參考
    ▼
PROJECT.md (作戰地圖 — 狀態追蹤) v1.4
    │ 紀錄
    ▼
audit-reports/ (歷史紀錄)
```

| 文件 | 角色 | 版本 | 維護者 | Claude Code 權限 |
|------|------|------|--------|------------------|
| CLAUDE.md | 最高治理規則 | v1.23.3 | 人工 | ❌ 禁止修改 |
| SKILL.md | 技術 SSOT | v4.1 | 人工 | ❌ 禁止修改 |
| PROJECT.md | 專案管理 | v1.4 | Claude Code + 人工 | ✅ 應主動更新 |
| audit-reports/ | Sprint 審計 | — | Claude Code | ✅ 每 Sprint 產出 |

### 0.3 [MANDATORY] Sprint PROMPT 三大鐵律

> ⚠️ **此規則從 CLAUDE.md v1.23.3 同步，最高優先級，違反者 PROMPT 禁止執行**

| # | 鐵律 | 說明 |
|---|------|------|
| **鐵律 1** | **嚴格遵守 CLAUDE.md** | 所有 Sprint PROMPT 必須 100% 符合 CLAUDE.md 所有 [MANDATORY] 規則 |
| **鐵律 2** | **遵循 PROJECT.md 管理** | Sprint 啟動讀取 PROJECT.md；狀態變更即時反映到 PROJECT.md |
| **鐵律 3** | **回報執行進度到 PROJECT.md** | task_done() 後更新狀態；sprint_finalize() 寫入最終結果 |

### 0.4 命名規則（MANDATORY）

| 類型 | 格式 | 範例 |
|------|------|------|
| Phase | `PH{N}` | PH1 |
| Demo Task | `D{N}-S{X}-P{Y}-T{Z}` | D1-S1-PA-T4 |
| Sprint Task | `P{XX}-P{Y}-T{Z}` | P26-PA-T1 |
| Git Tag 正式 | `v{M}.{m}.{p}` | v3.0.0 |
| Git Tag Demo | `demo{N}-v{M}.{m}.{p}` | demo1-v0.1.0 |
| Git Branch Sprint | `sprint/{XX}` | sprint/26 |
| Git Branch Demo | `demo/{N}` | demo/1 |
| Git Commit | `[{scope}] {type}: {desc}` | [P26] feat: IPlugin base |
| AuditReport | `{Sprint/Demo}_AuditReport.md` | Sprint26_AuditReport.md |
| PROMPT | `PROMPT_{Sprint/Demo}.md` | PROMPT_P26.md |

### 0.5 狀態符號

| 符號 | 狀態 |
|:----:|------|
| ⬜ | Not Started |
| 🔵 | Active |
| ✅ | Done |
| ⚠️ | Blocked |
| ❌ | Failed |
| 🔄 | In Review |
| ⏭️ | Skipped |

### 0.6 同步規則

- Task 完成 → 更新 PROJECT.md
- Sprint 完成 → 更新 PROJECT.md + SKILL.md + AuditReport
- Demo 完成 → 更新 PROJECT.md + Demo_AuditReport + git tag
- Phase 完成 → SKILL.md 大更新 + PROJECT.md 里程碑
- 重大事故 → CLAUDE.md 新增規則 + SKILL.md 記錄教訓

### 0.7 核心架構決策（已確立，不再討論）

| # | 決策 | 說明 |
|---|------|------|
| 1 | USD 為 SSOT | OpenUSD Stage 是唯一資料真相來源 |
| 2 | 6 大抽象介面 | IPlugin / IIOPlugin / IEnginePlugin / IRenderBackend / IShellPlugin / ITransport |
| 3 | 介面凍結時程 | P26 Draft → P27 RC → P28 Stable → P29 Frozen (v3.0 ABI) |
| 4 | ILOS 外部夥伴 | Python 代碼，保護: Cython→Nuitka→C++，到位 P34+ |
| 5 | USD↔Revit 外部夥伴 | Python 代碼，到位 P30+ |
| 6 | 最終部署 | 私有數據中心: Omniverse Server Farm + Core + 私有 LLM |
| 7 | Build→Operate 串接 | PromptToBuild 輸出 = PromptToOperate 輸入 |
| 8 | IDTF v3.5 底層 | 不是產品，是兩產品共用技術棧 |
| **9** | **ADR-001: Qt Quick 3D + QML** | **取代 PySide6 + PyVista（Qt3D deprecated Qt 6.8）。Demo 後 P26-P29 執行。AI Agent 保留 Python，QProcess + JSON stdio 通訊。** |

文件: docs/architecture/ADR-001_Qt_Quick_3D_Migration.md

### 0.8 ADR-001 架構變更摘要 (v4.1 新增)

```
現有 (Demo 期間保持)          目標 (P26-P29)
├─ PySide6 GUI (Python)      → Qt Quick (QML + C++)
├─ PyVista 3D (Python)       → Qt Quick 3D (QML, PBR, RHI)
├─ matplotlib charts         → QML Charts / Canvas
├─ pytest-qt                 → Qt Test + QML TestCase
├─ Python 直接嵌入 GUI        → QProcess + JSON stdio
└─ AI Agents (Python)        → AI Agents (Python, 不變)
```

P26-P29 拆分（風險遞增順序）:
| Sprint | 範圍 | 版本 |
|--------|------|------|
| P26 | AgentBridge (QProcess+JSON stdio) | v2.13.0 |
| P27 | QML GUI 骨架 (ApplicationWindow+ChatPanel) | v2.14.0 |
| P28 | Qt Quick 3D BIM 渲染 (View3D+PBR+Picking) | v2.15.0 |
| P29 | 清理: 移除 PySide6 + 測試遷移 | v3.0.0 🌟 |

---

## 0.9 [MANDATORY] Sprint 通知規則（v1.23.2 更新）

> ⚠️ **此規則從 CLAUDE.md v1.23.3 同步，嚴格執行，不可跳過。**

### 通知收件人
- **★ 主要: `+886972535899`**
- 備用: `chchlin1018@icloud.com`

### notify v2 函數（v1.23.2 — heredoc 版，Mac Mini 測試通過）

關鍵改進:
- heredoc `<<'EOF'` 取代巢狀轉義引號（解決 notify 引號爆炸問題）
- `service` + `buddy` API（非 `account` + `participant`）
- `/tmp/zigma-notify.log` 記錄所有通知
- 明確 return 0/1

### xcodebuild 互斥鎖 (v1.23.3 新增)

```
XCODE_LOCK="/tmp/zigma-xcodebuild.lock"
xcode_lock()   # mkdir atomic + 300s timeout + PID tracking
xcode_unlock()  # rm -rf
trap 'xcode_unlock' EXIT
```

Mac Mini 上可能同時有多個 Claude Code 實例。所有 xcodebuild 呼叫必須用 xcode_lock/xcode_unlock 包夾。

### PROMPT 創建 Checklist（MANDATORY — v4.1 更新）

```
☐ notify(v2 heredoc) + get_mem + check_mem + xcode_lock/unlock
☐ task_start + task_done + part_start + part_done + sprint_finalize
☐ 殭屍清理 (pkill) + QT_QPA_PLATFORM=offscreen
☐ ★ 鐵律 2: 啟動讀 PROJECT.md
☐ ★ 鐵律 3: task_done→更新 PROJECT.md + sprint_finalize()
☐ 通知多行格式 + 每 Task/Part 前後 notify
☐ pytest: safe_pytest_dir 分目錄 或 安全模式
☐ xcodebuild: xcode_lock/xcode_unlock 包夾
☐ 命名: [{scope}] commit prefix
☐ Sprint 結束產生下一個 PROMPT
☐ 不修改 CLAUDE.md / SKILL.md
```

### pytest 安全規則（MANDATORY — v4.1 更新）

**標準模式:**
- conftest.py 最頂部: `os.environ["QT_QPA_PLATFORM"] = "offscreen"`
- 禁止同時跑多個 pytest 進程
- `--timeout=10 --ignore=tests/test_gui --ignore=tests/test_e2e_integration.py -x`
- 每次 pytest 前後 `pkill -f "python.*pytest"`

**safe_pytest_dir 模式（OOM 診斷用，v4.1 新增）:**
- 分 7 批獨立跑: test_land → test_agents → test_bim → test_codes → test_integration → test_cpp → root
- 每批之間: pkill + sleep 2s + check_mem
- 每批前後: notify 發送記憶體 before→after
- 用於找出哪個測試目錄造成 OOM

**已知 OOM 元凶 (v4.1 實測確認):**
- **test_agents** 目錄吃 ~4GB 記憶體（8.9GB→12.9GB）
- 根因: Agent 測試 import Claude API 相關模組 + PySide6 間接引用
- pkill 清理後可回收（12.9GB→4.0GB）

### 記憶體監控規則（MANDATORY）

- 每個 PROMPT 最前面定義 get_mem + check_mem 函數
- Sprint 啟動時 check_mem — <1GB 中止
- 每個 Task/Part 啟動 notify 含 💾 get_mem
- Mac Mini memory-watchdog.sh: swap>4GB + free<300MB → 3次命中 → 自動重啟 + iMessage 通知
- **Sprint 前必須 `pkill -9 -f python` 清除殘留進程（曾因 python3.11 佔 15GB 導致 OOM）**

### Git 安全規則（MANDATORY）

- Sprint 啟動前 git pull origin main
- 每個 Part 結束 git commit + push
- Push 失敗 → git pull --rebase + 重試
- **Sprint 進行中禁止從 Claude.ai 推 commit（P24c 教訓）**

### PROJECT.md 追蹤規則

- Sprint 啟動時讀取 PROJECT.md（鐵律 2）
- 每 Task 完成後更新 PROJECT.md 狀態 → ✅（鐵律 3）
- Sprint 結束呼叫 sprint_finalize()（鐵律 3）
- 錯誤/OOM 也必須記錄
- docs/PROJECT_STATUS.md 已 deprecated → 用 PROJECT.md

---

## 1. 專案核心定位

**用自然語言在一塊真實土地上蓋建築。**

使用者流程：
1. 匯入土地資料（地籍圖 PDF、Shapefile、GeoJSON、手動輸入座標）
2. 在 2D 地圖上看到土地輪廓、面積、形狀
3. 用文字或語音描述想蓋的建築
4. AI 自動在這塊地上生成 3D BIM 建築模型
5. 同時輸出 IFC（BIM 語義）+ OpenUSD（Digital Twin / IDTF）
6. 桌面 3D 互動預覽（旋轉/縮放/剖面）

**⚠️ 硬性規則：零商業軟體依賴。全部使用開源 GitHub / Library。**

---

## 2. 技術棧

```
┌──────────────────────────────────────────────────────────┐
│                  Zigma PromptToBuild                      │
│                                                          │
│  🖥️ Desktop GUI — PySide6 (現有) → Qt Quick 3D (P26-P29) │
│  🗺️ GIS / 土地輸入                                       │
│  🧠 AI — Claude API (Anthropic SDK)                      │
│  🏗️ BIM 生成（純 Python，確定性輸出）                      │
│  🔌 Plugin 架構（v2.4.0+）                               │
│  ⚡ Plan 快取（SHA-256, LRU, TTL）                       │
│  👁️ 3D 渲染 — PyVista (現有) → Qt Quick 3D (P28)         │
│  🗣️ 語音（faster-whisper / macOS API）                   │
│  💰 Cost Engine（QTO + 22 單價 + estimator, P6）          │
│  📅 4D Simulation（16-phase + scheduler + GIF, P8）       │
│  🔧 MEP（A* pathfinding + 4 系統 + clash, P7）           │
│  🔄 Modifier Agent（intent + modify + undo, P4.8, 17KB） │
│  📦 Parts Library（76+ parts + registry, P2.5）           │
│  💾 Storage: 本地檔案 + SQLite                           │
│  🧪 Tests: ~820 Python + 137 C++ GoogleTest              │
└──────────────────────────────────────────────────────────┘
```

---

## 3. 專案結構

```
PromptBIMTestApp1/
├── CLAUDE.md              ← 憲法 (v1.23.3)
├── SKILL.md               ← 百科 (v4.1, 本文件)
├── PROJECT.md             ← 作戰地圖 (v1.4, ADR-001 + 路線圖)
├── src/promptbim/
│   ├── agents/            ← 7 agents (enhancer/planner/builder/checker/modifier/orchestrator/land_reader)
│   ├── bim/
│   │   ├── cost/          ← QTO + estimator + unit_prices + charts (P6)
│   │   ├── mep/           ← A* pathfinder + 4 systems + clash (P7)
│   │   ├── simulation/    ← 16-phase + scheduler + animator + GIF (P8)
│   │   ├── components/    ← 76 parts + registry + search (P2.5)
│   │   ├── templates/     ← school/hospital/factory (P10)
│   │   └── monitoring/    ← 48 sensor types (P8.5)
│   ├── gui/               ← PySide6 (main_window/chat/model_view/cost/sim/mep)
│   ├── viz/               ← PyVista (model_3d/cost_charts/gantt/mep_overlay)
│   ├── land/              ← 7 parsers (geojson/shp/dxf/kml/manual/pdf/image)
│   ├── codes/             ← 台灣法規 15 rules + C++ engine
│   ├── voice/             ← Whisper STT (P5)
│   └── libpromptbim/      ← C++ core (pybind11)
├── sprints/               ← Sprint PROMPTs (W0/D1-S1/D1-S2)
├── docs/
│   ├── architecture/      ← ADR-001 + 10 架構文件
│   └── Zigma_Context_Prompt_v5.0.md
├── tests/
├── PromptBIMTestApp1/     ← Xcode SwiftUI Wrapper
└── PromptBIMTestApp1.xcodeproj/
```

---

## 4. 開發路線圖 (v1.4)

### Phase 0: Demo 展示 (Week 0-10, 54T)

| Sprint | 週 | Tasks | 目標 | 版本 |
|--------|:--:|:-----:|------|------|
| W0 收尾 | 0.5 | 5 | pytest + tag | v2.11+v2.12 |
| D1-S1 引擎 | 2 | 15 | AI場景+Cost+4D+MEP | demo1-alpha |
| D1-S2 GUI | 2 | 14 | GUI+場景+TSMC展示 | demo1-v0.1.0 |
| D2 Omniverse | 5 | 35 | USD→Omni→Revit→建照 | demo2-v0.2.0 |

### Phase 1: Qt Quick 3D 遷移 (Week 11-18)

| Sprint | 週 | 目標 | 版本 |
|--------|:--:|------|------|
| P26 | 1 | AgentBridge QProcess+JSON | v2.13.0 |
| P27 | 2 | QML GUI 骨架 | v2.14.0 |
| P28 | 2 | Qt Quick 3D BIM | v2.15.0 |
| P29 | 1 | 清理 + PySide6 移除 | v3.0.0 🌟 |

### Phase 2-6: 未來

| Phase | Sprint | 目標 |
|-------|--------|------|
| PH2 | P30-P33 | Windows + USD↔Revit |
| PH3 | P34-P37 | ILOS + Omniverse |
| PH4 | P38-P41 | Web + Mobile |
| PH5 | P42-P44 | 私有 LLM |
| PH6 | P45-P50+ | SaaS + Marketplace |

---

## 5. TSMC Demo 需求 (v4.1 新增)

TSMC 明確需求:
1. Prompt → 快速 BIM 建築/廠房生成
2. Prompt 設計變更 → 成本 + 工期 delta
3. USD → Omniverse → Revit → 建照

Demo-1 v1.2: 6場景 + 3分類零件庫 + 4D施工機械 + MEP衝突穿孔
文件: docs/Zigma_TSMC_Demo_Plan_v1.2.md

---

## 6. 開發規範

1. **GUI:** PySide6 (Demo期間) → Qt Quick 3D (P26-P29)
2. **3D:** PyVista (Demo期間) → Qt Quick 3D View3D (P28)
3. **Agent:** sync `run()` + async `arun()`，BuilderAgent 僅 sync
4. **Builder:** 純 Python，不用 LLM，確定性輸出
5. **座標:** 內部統一公尺制本地座標系
6. **IFC:** 只用 `ifcopenshell.api.run()` 高階 API
7. **USD:** 只用 `pxr.Usd`, `pxr.UsdGeom`, `pxr.UsdShade`
8. **Git:** 遵循 §0.4 命名規則
9. **測試:** pytest (safe_pytest_dir 或標準模式)，coverage >= 70%
10. **快取:** generate/agenerate 預設走快取
11. **Plugin:** 新增 parser/rule 用 @register_plugin
12. **PROJECT.md:** 每 Task 完成後更新（鐵律 3）
13. **Sprint 前:** pkill -9 -f python + sudo purge（清殭屍）

---

## 7. 架構文件索引

| # | 文件 | 版本 |
|---|------|------|
| 1 | PromptBIM_Architecture_Design_v1.0 | v1.0 |
| 2 | PromptToBuild_Platform_Architecture_v2.0 | v2.0 |
| 3 | PromptToBuild_Platform_Architecture_v2.1 | v2.1 |
| 4 | PromptToBuild_Pre_P29_Validation_Plan_v1.0 | v1.0 |
| 5 | Reality_Matrix_Unified_Product_Architecture_v1.0 | v1.0 |
| 6 | PromptToBuild_Development_Plan_v1.1 | v1.1 |
| 7 | PromptToBuild_Partner_Interface_Spec_v1.0 | v1.0 |
| 8 | PromptToBuild_Governance_Framework_v1.0 | v1.0 |
| 9 | PromptToBuild_Repo_Restructuring_Plan_v1.0 | v1.0 |
| 10 | PromptToBuild_Repo_Restructure_Plan_v1.0 | v1.0 |
| **11** | **ADR-001_Qt_Quick_3D_Migration** | **v1.0** |
| **12** | **Zigma_TSMC_Demo_Plan_v1.2** | **v1.2** |
| **13** | **Zigma_Context_Prompt_v5.0** | **v5.0** |

---

## 附錄: 已知問題與 OOM 經驗 (v4.1 新增)

| ID | 問題 | 根因 | 解法 |
|----|------|------|------|
| ISSUE-001 | P24 pytest OOM | conftest import PySide6 → QApplication 佔數GB | conftest offscreen + safe_pytest_dir |
| ISSUE-002 | API Timeout | 預設 30s | .env API_TIMEOUT_SECONDS=120 |
| ISSUE-004 | PySide6 記憶體 | Python GUI 框架固有 | P29 Qt Quick 3D 取代 |
| **OOM-001** | **test_agents 吃 4GB** | **Agent 測試 import 重量級模組** | **safe_pytest_dir pkill 每批清理** |
| **OOM-002** | **python3.11 殘留 15GB** | **Sprint 前未清理舊進程** | **Sprint 前 pkill -9 -f python** |

Memory Watchdog (Mac Mini launchd):
- swap>4GB + free<300MB → 連續 3 次 → 自動重啟 + iMessage
- 與 Sprint check_mem() 互補

---

*SKILL.md v4.1 | Zigma PromptToBuild | 2026-03-27*
*★ v4.1 新增: ADR-001 Qt Quick 3D + notify v2 + xcodebuild mutex + safe_pytest_dir + OOM 診斷經驗*
