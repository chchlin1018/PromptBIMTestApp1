# Zigma PromptToBuild — SKILL.md v4.0

> Claude Code SSOT — 開發前必讀
> 最後更新: 2026-03-27 (v4.0 — Zigma 品牌 + 治理框架 + 命名規則)

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
PROJECT.md (作戰地圖 — 狀態追蹤) v1.0
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

### 0.3 命名規則（MANDATORY）

| 類型 | 格式 | 範例 |
|------|------|------|
| Phase | `PH{N}` | PH1 |
| Demo Task | `D{N}-S{X}-P{Y}-T{Z}` | D1-S1-PA-T4 |
| Sprint Task | `P{XX}-P{Y}-T{Z}` | P26-PA-T1 |
| Git Tag 正式 | `v{M}.{m}.{p}` | v3.0.0 |
| Git Tag Demo | `demo{N}-v{M}.{m}.{p}` | demo1-v0.1.0 |
| Git Branch Sprint | `sprint/{XX}` | sprint/26 |
| Git Branch Demo | `demo/{N}` | demo/1 |
| Git Branch Feature | `feature/{sprint}-{desc}` | feature/p26-plugin-bus |
| Git Commit | `[{scope}] {type}: {desc}` | [P26] feat: IPlugin base |
| AuditReport | `{Sprint/Demo}_AuditReport.md` | Sprint26_AuditReport.md |
| PROMPT | `PROMPT_{Sprint/Demo}.md` | PROMPT_P26.md |

scope: P26 / D1-S2 / docs / ci
type: feat / fix / refactor / test / docs / chore

### 0.4 狀態符號

| 符號 | 狀態 |
|:----:|------|
| ⬜ | Not Started |
| 🔵 | Active |
| ✅ | Done |
| ⚠️ | Blocked |
| ❌ | Failed |
| 🔄 | In Review |
| ⏭️ | Skipped |

### 0.5 同步規則

- Task 完成 → 更新 PROJECT.md
- Sprint 完成 → 更新 PROJECT.md + SKILL.md + AuditReport
- Demo 完成 → 更新 PROJECT.md + Demo_AuditReport + git tag
- Phase 完成 → SKILL.md 大更新 + PROJECT.md 里程碑
- 重大事故 → CLAUDE.md 新增規則 + SKILL.md 記錄教訓

詳細定義: docs/architecture/PromptToBuild_Governance_Framework_v1.0.md

---

## 0.6 [MANDATORY] Sprint 通知規則（v1.17.0 起生效）

> ⚠️ **此規則從 CLAUDE.md v1.23.0 同步，嚴格執行，不可跳過。**

### 通知收件人
- **★ 主要: `+886972535899`**（手機號碼，最優先）
- 備用: `chchlin1018@icloud.com`

### 雙向通知規則（MANDATORY）
- **★ 每個 Task 的「啟動 ▶️」和「結束 ✅」都必須發送 notify**
- **★ 每個 Part 的「啟動 ▶️」和「結束 ✅」都必須發送 notify**
- 每則 notify 必須含進度（Task N/Total | Part N/Total | %）
- Part 結束 notify 必須含 ⏭️ 下一步預告
- Sprint 啟動和最終完成各一則 notify
- 錯誤發生時立即 notify
- 缺少任何一則啟動或結束通知的 PROMPT 不合規

### notify 函數範本（必須複製到每個 PROMPT 最前面）
```bash
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
    osascript -e "display notification \"$msg\" with title \"Zigma\"" 2>/dev/null || \
    echo "[NOTIFY FALLBACK] $msg"
}
```

### PROMPT 創建 Checklist（MANDATORY — 每一條都必須滿足）
☐ notify() 主要收件人: +886972535899
☐ 每個 Task 有 ▶️ 啟動 notify + ✅ 結束 notify（共 2 則）
☐ 每個 Part 有 ▶️ 啟動 notify + ✅ 結束 notify（共 2 則）
☐ 每則 notify 含進度（Task N/Total | Part N/Total | %）
☐ Part 結束含 ⏭️ 下一步
☐ 包含失敗 + 中斷通知模板
☐ Sprint 結束必須產生下一個 PROMPT
☐ ★ 命名規則遵循 §0.3（v4.0 新增）
☐ ★ 每 Task 完成後更新 PROJECT.md（v4.0 新增）

> 完整範本見 CLAUDE.md v1.23.0

### 記憶體監控規則（v1.18.0+ MANDATORY）
- **★ 每個 PROMPT 最前面必須定義 get_mem + check_mem 函數**
- **★ Sprint 啟動時 check_mem — <1GB 中止**
- **★ 每個 Task ▶️ 啟動 notify 必須含 💾 get_mem 結果**
- **★ 每個 Part ▶️ 啟動前 check_mem — <1GB 暫停**
- P24 教訓: Mac Mini 16GB RAM 耗盡 → Claude Code 被暫停 → Sprint 靜默中斷

### pytest 安全規則（v1.20.0 新增 — MANDATORY）
- **★ Sprint 啟動時清理殭屍 Python: pkill -f "python.*pytest"**
- **★ export QT_QPA_PLATFORM=offscreen（禁止真正 GUI 視窗）**
- **★ pytest 必須加: --timeout=10 --ignore=tests/test_gui -x**
- P24b 教訓: pytest GUI 測試產生殭屍 Python 進程吃 26GB

### pytest OOM 根因（P24e — 4次事故總結）
- **★ conftest.py 最頂部必須設定 os.environ["QT_QPA_PLATFORM"] = "offscreen"**
- **★ 禁止同時跑多個 pytest 進程（Mac Mini 16GB 會 OOM）**
- **★ pytest 必須加 --ignore=tests/test_e2e_integration.py（20KB 觸發 PySide6）**
- **★ 每次 pytest 前後都 pkill -f "python.*pytest"**
- 根因: pytest 收集 test 檔案時 import PySide6 → 建立 QApplication → 每個進程吃數 GB
- Claude Code 同時啟動多個 pytest 進程 → 記憶體倍增 → swap 10.77GB → OOM

### Git 安全規則（v1.19.0 MANDATORY）
- **★ Sprint 啟動前 git pull origin main（防遠端分歧）**
- **★ 每個 Part 結束必須 git commit + push（增量保存）**
- **★ Push 失敗 → 自動 git pull --rebase + 重試**
- P22.1 教訓: Sprint 完成但沒 commit → 工作遺失
- P24 教訓: Claude.ai 推 commit 造成本地分歧 → push 失敗

### PROJECT.md 追蹤規則（v1.23.0 同步, v4.0 更新）
- **★ Sprint 啟動時必須先讀取 PROJECT.md（不再是 docs/PROJECT_STATUS.md）**
- **★ 每 Task 完成後更新 PROJECT.md 對應狀態 → ✅**
- **★ Sprint 結束時（成功/失敗/中斷）必須更新 PROJECT.md**
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

## 1.1 核心架構決策（v4.0 新增 — 來自上游架構設計 Session）

> 以下決策已確立，不再討論，Claude Code 執行時遵循。

| # | 決策 | 說明 |
|---|------|------|
| 1 | USD 為 SSOT | OpenUSD Stage 是唯一資料真相來源，貫穿設計→營運 |
| 2 | 6 大抽象介面 | IPlugin / IIOPlugin / IEnginePlugin / IRenderBackend / IShellPlugin / ITransport |
| 3 | 介面凍結時程 | P26 Draft → P27 RC → P28 Stable → P29 Frozen (v3.0 ABI) |
| 4 | ILOS 外部夥伴 | Python 代碼，保護: Cython→Nuitka→C++，到位 P34+ |
| 5 | USD↔Revit 外部夥伴 | Python 代碼，到位 P30+ |
| 6 | 最終部署 | 私有數據中心: Omniverse Server Farm + Core + 私有 LLM |
| 7 | Build→Operate 串接 | PromptToBuild 輸出 = PromptToOperate 輸入，Prim+ilos:metadata |
| 8 | IDTF v3.5 底層 | 不是產品，是兩產品共用技術棧 (IADL/FDL/NDH/MCP/Asset Servants) |

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
│  ├─ Shapefile (.shp): geopandas + fiona (BSD)            │
│  ├─ GeoJSON (.geojson): geopandas (BSD)                  │
│  ├─ KML (.kml): fastkml (LGPL) + lxml (BSD)              │
│  ├─ PDF 地籍圖: PyMuPDF/fitz (AGPL) → 圖片 + OCR        │
│  ├─ DXF (.dxf): ezdxf (MIT)                              │
│  ├─ 手動繪製: matplotlib interactive polygon              │
│  └─ 座標系轉換: pyproj (MIT)                             │
│                                                          │
│  🧠 AI — Claude API (Anthropic SDK, MIT)                 │
│  ├─ Agent 1: Enhancer（需求增強）                         │
│  ├─ Agent 2: Planner（建築規劃 + 退縮/容積計算）          │
│  ├─ Agent 4: Checker（規則檢查 + 修正建議）              │
│  ├─ async/await: BaseAgent.arun() + AsyncAnthropic       │
│  ├─ Rate Limiter: token bucket (50 RPM)                  │
│  └─ Retry: tenacity (3x exponential backoff, 5xx only)   │
│                                                          │
│  🏗️ BIM 生成（純 Python，不用 LLM）                      │
│  ├─ IFC: IfcOpenShell 0.8+ (LGPL)                       │
│  ├─ USD: usd-core / pxr (Apache-2.0)                    │
│  ├─ 幾何: shapely (BSD) + numpy + trimesh (MIT)          │
│  └─ 材質: 內建 PBR 預設                                  │
│                                                          │
│  🔌 Plugin 架構（v2.4.0+ / v3.0 重構）                   │
│  ├─ PluginRegistry + @register_plugin decorator          │
│  ├─ 三種類型: agent / parser / code_rule                 │
│  └─ v3.0: 6 大抽象介面 (IPlugin/IIOPlugin/IEngine/...)   │
│                                                          │
│  ⚡ Plan 快取（v2.4.0+）                                 │
│  ├─ SHA-256 cache key (prompt + land + zoning)           │
│  ├─ 本地 JSON store (~/.promptbim/cache/)                │
│  ├─ LRU 淘汰 (max 100 entries) + TTL 7 天               │
│  └─ CLI: cache list / clear / stats                      │
│                                                          │
│  👁️ 3D 渲染（嵌入桌面 App）                              │
│  ├─ PyVista (MIT) — VTK Python 高階封裝                  │
│  ├─ pyvistaqt (MIT) — Qt 嵌入元件                        │
│  └─ F3D CLI (BSD) — 離線批次渲染 PNG（選用）             │
│                                                          │
│  🗣️ 語音                                                 │
│  ├─ whisper.cpp / faster-whisper (MIT) — 本地 STT        │
│  └─ 或 macOS NSSSpeechRecognizer (系統 API)              │
│                                                          │
│  💾 Storage: 本地檔案 + SQLite                           │
└──────────────────────────────────────────────────────────┘
```

### 2.1 依賴 License 審計（全部開源）

| 依賴 | License | 用途 |
|------|---------|------|
| PySide6 | LGPL-3.0 | Desktop GUI |
| PyVista | MIT | 3D 視覺化 |
| pyvistaqt | MIT | PyVista ↔ Qt 橋接 |
| IfcOpenShell | LGPL-3.0 | IFC BIM 生成 |
| usd-core (pxr) | Apache-2.0 | OpenUSD 生成 |
| anthropic SDK | MIT | Claude API |
| geopandas | BSD-3 | GIS 資料讀取 |
| shapely | BSD-3 | 2D 幾何運算 |
| fiona | BSD-3 | Shapefile/GeoJSON I/O |
| pyproj | MIT | 座標系轉換 |
| ezdxf | MIT | DXF 讀取 |
| PyMuPDF (fitz) | AGPL-3.0 | PDF 地籍圖解析 |
| fastkml | LGPL-3.0 | KML 讀取 |
| lxml | BSD-3 | XML 解析 (fastkml) |
| numpy | BSD-3 | 數值運算 |
| trimesh | MIT | Mesh 操作 |
| matplotlib | PSF/BSD | 2D 繪圖 (地籍+平面圖) |
| Pillow | HPND | 圖片處理 |
| faster-whisper | MIT | 本地語音辨識 |
| pydantic | MIT | 資料驗證 |
| tenacity | Apache-2.0 | API retry with backoff |
| rich | MIT | Terminal UI |

> **PyMuPDF 注意:** AGPL-3.0 要求開源分發。如需避免 AGPL，可改用 `pdfplumber`（MIT）作為 PDF 解析替代方案。

---

## 3. 桌面 App 架構

### 3.1 主視窗佈局

```
┌──────────────────────────────────────────────────────┐
│  Menu Bar: File | Edit | View | Tools | Help         │
├────────────────────┬─────────────────────────────────┤
│                    │                                 │
│   左側面板         │         中央視圖區               │
│   (350px)          │                                 │
│                    │   ┌─ Tab: 2D 地籍 ──────────┐  │
│  ┌──────────────┐  │   │                         │  │
│  │ 📁 專案樹    │  │   │  [matplotlib canvas]    │  │
│  │  └ 土地       │  │   │   土地輪廓              │  │
│  │  └ 建築      │  │   │   建築 footprint        │  │
│  │    └ 1F      │  │   │   退縮線                 │  │
│  │    └ 2F      │  │   │   面積標注               │  │
│  │    └ 3F      │  │   │                         │  │
│  └──────────────┘  │   └─────────────────────────┘  │
│                    │                                 │
│  ┌──────────────┐  │   ┌─ Tab: 3D 建築 ──────────┐  │
│  │ 📋 屬性面板  │  │   │                         │  │
│  │  面積: 450㎡  │  │   │  [PyVista QtInteractor] │  │
│  │  樓層: 3     │  │   │   3D 建築模型            │  │
│  │  容積率: 2.1 │  │   │   互動旋轉/縮放         │  │
│  │  建蔽率: 58% │  │   │   樓層剖面              │  │
│  └──────────────┘  │   │                         │  │
│                    │   └─────────────────────────┘  │
├────────────────────┴─────────────────────────────────┤
│  底部: AI Chat 面板                                   │
│  ┌───────────────────────────────────────────┬─────┐ │
│  │ 💬 在這塊地上蓋3層辦公樓，一樓停車場...    │ 🎤  │ │
│  └───────────────────────────────────────────┴─────┘ │
│  Claude: 正在分析土地形狀... 規劃建築配置中...        │
│  ✅ 已生成 3 層辦公大樓 (建蔽率 55%, 容積率 165%)     │
└──────────────────────────────────────────────────────┘
```

### 3.2 使用者流程

```
Step 1: 匯入土地
  ├─ 拖放 .shp / .geojson / .kml / .dxf / .pdf
  ├─ 或手動輸入座標 / 繪製多邊形
  └─ 自動計算: 面積、周長、形狀、方位

Step 2: 設定土地參數（可選）
  ├─ 使用分區: 住宅/商業/工業
  ├─ 容積率上限 / 建蔽率上限
  ├─ 退縮距離（前/後/左/右）
  └─ 高度限制

Step 3: AI 對話生成建築
  ├─ 文字: "在這塊地上蓋一棟3層樓住宅..."
  ├─ 語音: 按住 🎤 說話
  └─ AI 自動考慮土地形狀 + 退縮 + 容積率

Step 4: 預覽與調整
  ├─ 2D Tab: 看 footprint 是否合理
  ├─ 3D Tab: 互動瀏覽建築模型
  └─ 文字微調: "把入口移到南面" / "加一間會議室"

Step 5: 匯出
  ├─ model.ifc (BIM 完整語義)
  ├─ model.usda (OpenUSD, IDTF 接口)
  ├─ floorplan.svg (各層平面圖)
  ├─ site_plan.svg (配置圖含土地+建築)
  └─ summary.json (面積/容積率/建蔽率 等)
```

---

## 4. 專案結構

### 4.1 現行結構 (v2.12, RS-S1 前)

```
PromptBIMTestApp1/
├── README.md
├── SKILL.md               # v4.0 (本文件)
├── CLAUDE.md              # v1.23.0
├── PROJECT.md             # v1.0 ★ NEW
├── LICENSE                # MIT
├── pyproject.toml
├── .env.example
├── .gitignore
├── .github/
│   ├── workflows/ci.yml
│   └── dependabot.yml
│
├── src/promptbim/         # 源碼 (RS-S1 後 → zigma_build/)
├── tests/
├── docs/
│   ├── architecture/      # 10 份架構文件
│   ├── drafts/            # 治理文件草稿 (審閱用)
│   ├── reports/
│   └── addendum/
│
├── PromptBIMTestApp1/     # Xcode SwiftUI Wrapper
├── PromptBIMTestApp1.xcodeproj/
├── examples/
├── resources/
└── output/                # .gitignore
```

### 4.2 目標結構 (RS-S1 後, zigma mono-repo)

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
├── legacy/        ← 舊版（SwiftUI/xcodeproj/libpromptbim）
└── cpp/           ← C++ 原生引擎
```

---

## 5. 核心 Schema（Pydantic）

### 5.1 LandParcel（土地）

```python
# schemas/land.py
from pydantic import BaseModel
from shapely.geometry import Polygon

class LandParcel(BaseModel):
    """一筆土地的完整資訊"""
    name: str = "Untitled Parcel"
    boundary: list[tuple[float, float]]
    area_sqm: float
    perimeter_m: float
    crs: str = "EPSG:4326"
    local_origin: tuple[float, float] = (0, 0)
    source_file: str | None = None
    source_type: str = "manual"

    class Config:
        arbitrary_types_allowed = True
```

### 5.2 ZoningRules（分區規則）

```python
# schemas/zoning.py
class ZoningRules(BaseModel):
    zone_type: str = "residential"
    far_limit: float = 2.0
    bcr_limit: float = 0.6
    height_limit_m: float = 15.0
    setback_front_m: float = 5.0
    setback_back_m: float = 3.0
    setback_left_m: float = 2.0
    setback_right_m: float = 2.0
    min_parking_per_unit: float = 1.0
```

### 5.3 BuildingPlan（Agent 2 輸出）

```python
# schemas/plan.py
class BuildingPlan(BaseModel):
    name: str
    schema_version: str = "2.4.0"
    land_boundary: list[tuple[float, float]]
    buildable_area: list[tuple[float, float]]
    building_footprint: list[tuple[float, float]]
    building_bcr: float
    building_far: float
    stories: list[StoryPlan]
    roof: RoofPlan
```

---

## 6. Agent 2 (Planner) — 關鍵 Prompt 設計

```python
PLANNER_SYSTEM_PROMPT = """
You are an expert architect and urban planner. Your task is to generate a
BuildingPlan JSON that places a building on a real land parcel.

## INPUT
1. LandParcel: boundary coordinates, area, shape
2. ZoningRules: FAR limit, BCR limit, height limit, setbacks
3. BuildingRequirement: user's building description

## CONSTRAINTS (MUST follow)
- Building footprint MUST fit inside the buildable area
- BCR MUST NOT exceed bcr_limit
- FAR MUST NOT exceed far_limit
- Building height MUST NOT exceed height_limit_m
- All coordinates in METERS, relative to land's local origin
- Walls must form closed polygons per floor
- Corridors minimum 1.2m width
- Doors minimum 0.9m width, 2.1m height
- Windows minimum 0.6m width, sill height 0.9m

## OUTPUT
Return a valid BuildingPlan JSON matching the schema exactly.
All coordinates precise to 0.01m.
"""
```

---

## 7. pyproject.toml

```toml
[project]
name = "promptbim"
version = "2.12.0"
description = "Zigma PromptToBuild — AI-powered building generation on real land parcels"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "Michael Lin", email = "michael@realitymatrix.com"}]

dependencies = [
    "PySide6>=6.6",
    "pyvista>=0.43",
    "pyvistaqt>=0.11",
    "anthropic>=0.40.0",
    "ifcopenshell>=0.8.0",
    "usd-core>=24.0",
    "geopandas>=0.14",
    "shapely>=2.0",
    "fiona>=1.9",
    "pyproj>=3.6",
    "ezdxf>=1.1",
    "fastkml>=1.0",
    "lxml>=5.0",
    "mapbox-earcut>=2.0",
    "numpy>=1.26",
    "trimesh>=4.0",
    "matplotlib>=3.8",
    "Pillow>=10.0",
    "tenacity>=8.0",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "python-dotenv>=1.0",
    "imageio>=2.30",
]

[project.optional-dependencies]
pdf = ["pdfplumber>=0.10", "PyMuPDF>=1.23"]
voice = ["faster-whisper>=1.0", "sounddevice>=0.4"]
mcp = ["mcp>=1.0"]
web = ["streamlit>=1.30"]
dev = ["pytest>=8.0", "ruff>=0.4", "pytest-qt>=4.3", "pytest-cov>=5.0", "pip-audit>=2.7", "pip-tools>=7.0"]
```

---

## 8. 開發路線圖

### P0-P17: 已完成（見歷史）

### P18-P24: POC 階段（大部分完成）

### 未來路線圖（Zigma 架構）

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

| 模組 | 語言 | Plugin 介面 | 保護方案 | 預計到位 |
|------|------|------------|---------|---------|
| ILOS Layout Engine | Python | IEnginePlugin | Cython→C++ | P34+ |
| ILOS Piping Router | Python | IEnginePlugin | Cython→C++ | P34+ |
| USD↔Revit Converter | Python | IIOPlugin | Cython→C++ | P30+ |

P26-P29 用 mock stub 驗證介面，不阻塞 Phase 1。

### ILOS-FAB 技術約束（POC 已驗證）

- Instance 解析: final_xf = inst_xf × proto_inv × mesh_xf
- 單位: USD(cm) × 0.01 / 0.3048 = Revit(ft)
- Transaction: 不可建立明確 Transaction（Revit MCP 自動包裝）
- 材質: 必須建立 Material 並指派（否則全黑）
- 退化三角形: 跳過距離 < 0.0001 ft
- 批次大小: 30 mesh/batch
- Path B (DirectShape) 已驗證, Path C (MEP Native) 已驗證

---

## 9. 環境設定

```bash
cd ~/Documents/MyProjects/PromptBIMTestApp1
conda activate promptbim
pip install -e ".[dev]"

# 驗證
python -c "import ifcopenshell; print(f'IfcOpenShell {ifcopenshell.version}')"
python -c "from pxr import Usd; print('OpenUSD OK')"
python -c "from PySide6.QtWidgets import QApplication; print('PySide6 OK')"
python -m promptbim --version
```

---

## 10. 開發規範

1. **GUI:** PySide6 + Qt Designer 風格
2. **3D:** PyVista mesh 作為中間格式
3. **Agent:** System prompt 作為常數，sync `run()` + async `arun()`
4. **Builder:** 純 Python，不用 LLM，確定性輸出
5. **座標:** 內部統一使用公尺制本地座標系
6. **IFC:** 只用 `ifcopenshell.api.run()` 高階 API
7. **USD:** 只用 `pxr.Usd`, `pxr.UsdGeom`, `pxr.UsdShade`
8. **Git:** 遵循 §0.3 命名規則（v4.0 更新）
9. **測試:** pytest + pytest-qt，coverage >= 70%
10. **快取:** generate/agenerate 預設走快取
11. **Plugin:** 新增 parser/rule 用 @register_plugin
12. **常數:** 魔術數字放 `constants.py`
13. **PROJECT.md:** 每 Task 完成後更新（v4.0 新增）

---

## 11. CLI 使用範例

```bash
python -m promptbim --version
python -m promptbim gui [--debug]
python -m promptbim generate "3-story villa" -o ./output [--land site.geojson]
python -m promptbim generate --no-cache "villa" -o ./output
python -m promptbim cache list | clear | stats
python -m promptbim check [--ai] [--fix] [--json]
```

---

## 附錄文件 (Addendum)

| 文件 | 內容 | 對應 Sprint |
|------|------|------------|
| `docs/addendum/01_component_library.md` | 74 種建築零件庫 | P2.5 |
| `docs/addendum/02_sim_cost_mep.md` | 4D/5D + MEP | P6-P8 |
| `docs/addendum/03_tw_building_codes.md` | 台灣建築法規引擎 | P4.5 |

## 架構文件索引 (v4.0 新增)

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

Claude Code 開發各 Sprint 前，**必須先讀取 SKILL.md + 對應附錄/架構文件**。

---

*SKILL.md v4.0 DRAFT | Zigma PromptToBuild | 2026-03-27*
*⚠️ 本文件為草稿，待 Michael 審閱後替換根目錄 SKILL.md*
