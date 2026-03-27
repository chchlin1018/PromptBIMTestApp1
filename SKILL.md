# Zigma PromptToBuild — SKILL.md v4.0

> Claude Code SSOT — 開發前必讀
> 最後更新: 2026-03-27 (v4.0 — Zigma 品牌 + 治理框架 + 命名規則 + Sprint PROMPT 三大鐵律)

---

## 0. [MANDATORY] 專案治理框架 (v4.0 新增)

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
CLAUDE.md (憲法 — 不可自動修改) v1.23.0
    │ 規範
    ▼
SKILL.md (百科 — 技術 SSOT) v4.0       ← 你在讀這份
    │ 參考
    ▼
PROJECT.md (作戰地圖 — 狀態追蹤) v1.1
    │ 紀錄
    ▼
audit-reports/ (歷史紀錄)
```

| 文件 | 角色 | 維護者 | Claude Code 權限 |
|------|------|--------|------------------|
| CLAUDE.md | 最高治理規則 | 人工 | ❌ 禁止修改 |
| SKILL.md | 技術 SSOT | 人工 | ❌ 禁止修改 |
| PROJECT.md | 專案管理 | Claude Code + 人工 | ✅ 應主動更新 |
| audit-reports/ | Sprint 審計 | Claude Code | ✅ 每 Sprint 產出 |

### 0.3 [MANDATORY] Sprint PROMPT 三大鐵律

> ⚠️ **此規則從 CLAUDE.md v1.23.0 同步，最高優先級，違反者 PROMPT 禁止執行**

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

詳細定義: docs/architecture/PromptToBuild_Governance_Framework_v1.0.md

---

## 0.8 [MANDATORY] Sprint 通知規則（v1.17.0 起生效）

> ⚠️ **此規則從 CLAUDE.md v1.23.0 同步，嚴格執行，不可跳過。**

### 通知收件人
- **★ 主要: `+886972535899`**（手機號碼，最優先）
- 備用: `chchlin1018@icloud.com`

### 雙向通知規則（MANDATORY）
- **★ 每個 Task 的「啟動 ▶️」和「結束 ✅」都必須發送 notify**
- **★ 每個 Part 的「啟動 ▶️」和「結束 ✅」都必須發送 notify**
- 每則 notify 必須含進度（Task N/Total | Part N/Total | %）
- Part 結束 notify 必須含 ⏭️ 下一步預告

### PROMPT 創建 Checklist（MANDATORY）
☐ notify() 主要收件人: +886972535899
☐ 每個 Task 有 ▶️ 啟動 notify + ✅ 結束 notify
☐ 每個 Part 有 ▶️ 啟動 notify + ✅ 結束 notify
☐ 每則 notify 含進度
☐ Part 結束含 ⏭️ 下一步
☐ 包含失敗 + 中斷通知模板
☐ Sprint 結束必須產生下一個 PROMPT
☐ ★ 鐵律 1: 100% 符合 CLAUDE.md MANDATORY（v4.0 新增）
☐ ★ 鐵律 2: 啟動讀 PROJECT.md（v4.0 新增）
☐ ★ 鐵律 3: task_done→更新 PROJECT.md + sprint_finalize()（v4.0 新增）

### 記憶體監控規則（MANDATORY）
- **★ 每個 PROMPT 最前面必須定義 get_mem + check_mem 函數**
- **★ Sprint 啟動時 check_mem — <1GB 中止**
- **★ 每個 Task ▶️ 啟動 notify 必須含 💾 get_mem 結果**
- **★ 每個 Part ▶️ 啟動前 check_mem — <1GB 暫停**

### pytest 安全規則（MANDATORY）
- **★ conftest.py 最頂部: os.environ["QT_QPA_PLATFORM"] = "offscreen"**
- **★ 禁止同時跑多個 pytest 進程**
- **★ pytest 必須加 --timeout=10 --ignore=tests/test_gui --ignore=tests/test_e2e_integration.py -x**
- **★ 每次 pytest 前後都 pkill -f "python.*pytest"**

### Git 安全規則（MANDATORY）
- **★ Sprint 啟動前 git pull origin main**
- **★ 每個 Part 結束必須 git commit + push**
- **★ Push 失敗 → git pull --rebase + 重試**

### PROJECT.md 追蹤規則（v1.23.0 同步, v4.0 更新）
- **★ Sprint 啟動時必須先讀取 PROJECT.md（不再是 docs/PROJECT_STATUS.md）**
- **★ 每 Task 完成後更新 PROJECT.md 對應狀態 → ✅（鐵律 3）**
- **★ Sprint 結束時呼叫 sprint_finalize() 更新最終結果（鐵律 3）**
- **★ 錯誤、OOM 等異常也必須記錄到 PROJECT.md**
- **★ docs/PROJECT_STATUS.md 已 deprecated**

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

## 2. 100% 開源技術棧

```
┌──────────────────────────────────────────────────────────┐
│                  Zigma PromptToBuild                      │
│                  (promptbim → zigma_build)                │
│                                                          │
│  🖥️ Desktop GUI — PySide6 (LGPL-3.0)                    │
│  ├─ 2D 地籍視圖: matplotlib + shapely (嵌入 Qt)          │
│  ├─ 3D 建築視圖: PyVista + pyvistaqt (MIT)               │
│  └─ Chat 面板: QTextEdit + 語音按鈕                      │
│                                                          │
│  🗺️ GIS / 土地輸入                                       │
│  🧠 AI — Claude API (Anthropic SDK, MIT)                 │
│  🏗️ BIM 生成（純 Python，不用 LLM）                      │
│  🔌 Plugin 架構（v2.4.0+ / v3.0 重構）                   │
│  ⚡ Plan 快取（SHA-256, LRU, TTL）                       │
│  👁️ 3D 渲染（PyVista + pyvistaqt）                       │
│  🗣️ 語音（faster-whisper / macOS API）                   │
│  💾 Storage: 本地檔案 + SQLite                           │
└──────────────────────────────────────────────────────────┘
```

完整依賴清單與 License 審計見 SKILL.md v3.8 §2.1（全部開源）。

---

## 3. 專案結構

### 3.1 現行結構 (v2.12, RS-S1 前)

```
PromptBIMTestApp1/
├── CLAUDE.md              ← 憲法 (v1.23.0)
├── SKILL.md               ← 百科 (v4.0, 本文件)
├── PROJECT.md             ← 作戰地圖 (v1.1) ★
├── src/promptbim/         ← 源碼 (RS-S1 後 → zigma_build/)
├── tests/
├── docs/
│   ├── architecture/      ← 10 份架構文件
│   ├── drafts/            ← 治理文件草稿 (審閱完畢可清除)
│   ├── reports/
│   └── addendum/
├── PromptBIMTestApp1/     ← Xcode SwiftUI Wrapper
└── PromptBIMTestApp1.xcodeproj/
```

### 3.2 目標結構 (RS-S1 後, zigma mono-repo)

```
zigma/
├── core/          ← Zigma Core（C++ Plugin 介面）
├── build/         ← Zigma PromptToBuild（Python + Plugins）
├── operate/       ← Zigma PromptToOperate（未來）
├── cloud/         ← Zigma Cloud（未來）
├── shell/         ← UI Shell（qt6/web/headless）
├── render/        ← Render Backend（vtk/hydra/omni）
├── demo/          ← Demo 腳本
├── docs/architecture/
├── governance/    ← audit-reports + prompts + sprints
├── legacy/        ← 舊版
└── cpp/           ← C++ 原生引擎
```

---

## 4. 開發路線圖

| Phase | Sprint | 目標 | 版本 | 週數 |
|-------|--------|------|------|:----:|
| PH0 | P25收尾 | POC 收尾 | v2.12 | 1 |
| PH0.5 | D1+D2 | Demo 展示 | demo1/2 | 6 |
| PH1 | P26-P29 | Plugin 架構 + Qt6 | v3.0 | 8 |
| PH2 | P30-P33 | Windows + USD↔Revit | v3.x | 8 |
| PH3 | P34-P37 | ILOS + Omniverse | v4.0 | 8 |
| PH4 | P38-P41 | Web + Mobile | v4.x | 8 |
| PH5 | P42-P44 | 私有 LLM | v5.0 | 6 |
| PH6 | P45-P50+ | SaaS + Marketplace | v5.x | 持續 |

### 合作夥伴外部模組

| 模組 | Plugin 介面 | 保護方案 | 預計到位 |
|------|------------|---------|--------|
| ILOS Layout Engine | IEnginePlugin | Cython→C++ | P34+ |
| ILOS Piping Router | IEnginePlugin | Cython→C++ | P34+ |
| USD↔Revit Converter | IIOPlugin | Cython→C++ | P30+ |

P26-P29 用 mock stub 驗證介面，不阻塞 Phase 1。

### ILOS-FAB 技術約束（POC 已驗證）

- Instance 解析: final_xf = inst_xf × proto_inv × mesh_xf
- 單位: USD(cm) × 0.01 / 0.3048 = Revit(ft)
- 批次大小: 30 mesh/batch
- Path B (DirectShape) + Path C (MEP Native) 已驗證

---

## 5. 開發規範

1. **GUI:** PySide6 + Qt Designer 風格
2. **3D:** PyVista mesh 作為中間格式
3. **Agent:** sync `run()` + async `arun()`，BuilderAgent 僅 sync
4. **Builder:** 純 Python，不用 LLM，確定性輸出
5. **座標:** 內部統一公尺制本地座標系
6. **IFC:** 只用 `ifcopenshell.api.run()` 高階 API
7. **USD:** 只用 `pxr.Usd`, `pxr.UsdGeom`, `pxr.UsdShade`
8. **Git:** 遵循 §0.4 命名規則
9. **測試:** pytest + pytest-qt，coverage >= 70%
10. **快取:** generate/agenerate 預設走快取
11. **Plugin:** 新增 parser/rule 用 @register_plugin
12. **常數:** 魔術數字放 `constants.py`
13. **PROJECT.md:** 每 Task 完成後更新（鐵律 3）

---

## 6. 環境設定

```bash
cd ~/Documents/MyProjects/PromptBIMTestApp1
conda activate promptbim
pip install -e ".[dev]"
python -m promptbim --version
```

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

---

## 附錄文件 (Addendum)

| 文件 | 內容 | 對應 Sprint |
|------|------|------------|
| `docs/addendum/01_component_library.md` | 74 種建築零件庫 | P2.5 |
| `docs/addendum/02_sim_cost_mep.md` | 4D/5D + MEP | P6-P8 |
| `docs/addendum/03_tw_building_codes.md` | 台灣建築法規引擎 | P4.5 |

Claude Code 開發各 Sprint 前，**必須先讀取 SKILL.md + 對應的附錄/架構文件**。

---

*SKILL.md v4.0 | Zigma PromptToBuild | 2026-03-27*
*★ Sprint PROMPT 三大鐵律: 遵守 CLAUDE.md + 遵循 PROJECT.md + 回報進度到 PROJECT.md*
