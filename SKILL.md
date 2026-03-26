# PromptBIMTestApp1 — SKILL.md v3.7

> Claude Code SSOT — 開發前必讀
> 最後更新: 2026-03-26 (v3.5 lessons learned + memory + git safety)

---

## 1. 專案核心定位

## 0. [MANDATORY] Sprint 通知規則（v1.17.0 起生效）

> ⚠️ **此規則從 CLAUDE.md v1.21.0 同步，嚴格執行，不可跳過。**

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
    osascript -e "display notification \"$msg\" with title \"PromptBIM\"" 2>/dev/null || \
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

> 完整範本見 CLAUDE.md v1.21.0

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

### 記憶體監控規則（v1.18.0 新增 — MANDATORY）
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

---

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
│                  PromptBIMTestApp1                        │
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
│  🔌 Plugin 架構（v2.4.0+）                               │
│  ├─ PluginRegistry + @register_plugin decorator          │
│  └─ 三種類型: agent / parser / code_rule                 │
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

```
PromptBIMTestApp1/
├── README.md
├── SKILL.md
├── CLAUDE.md                       # Claude Code 行為規範 (v1.13.0)
├── LICENSE                         # MIT
├── pyproject.toml
├── .env.example
├── .gitignore
├── .github/
│   ├── workflows/ci.yml            # GitHub Actions CI
│   └── dependabot.yml
│
├── src/
│   └── promptbim/
│       ├── __init__.py             # __version__, __all__, py.typed
│       ├── __main__.py             # CLI + GUI 啟動
│       ├── config.py               # Pydantic BaseSettings
│       ├── constants.py            # 具名常數 (P16+)
│       │
│       ├── gui/                    # === Desktop GUI (PySide6) ===
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   ├── land_panel.py
│       │   ├── property_panel.py
│       │   ├── map_view.py
│       │   ├── model_view.py
│       │   ├── chat_panel.py       # 含快取指示 (Cache hit/miss)
│       │   ├── project_tree.py
│       │   └── dialogs/
│       │
│       ├── land/                   # === 土地/GIS 處理 ===
│       │   ├── __init__.py
│       │   ├── parsers/            # Shapefile, GeoJSON, KML, DXF, PDF, Manual
│       │   ├── land_model.py
│       │   ├── setback.py          # uniform_setback() + per_side_setback() (P17)
│       │   ├── zoning.py
│       │   └── projection.py
│       │
│       ├── agents/                 # === AI Multi-Agent ===
│       │   ├── __init__.py
│       │   ├── base.py             # BaseAgent: run() + arun() (async, P17)
│       │   │                       #   tenacity retry (3x, exp backoff, 5xx)
│       │   │                       #   timeout=30s, AsyncAnthropic lazy init
│       │   ├── enhancer.py         # Agent 1: 需求增強 (sync + async)
│       │   ├── planner.py          # Agent 2: 建築規劃 (sync + async)
│       │   ├── builder.py          # Agent 3: IFC+USD 生成 (純 Python, 同步 only)
│       │   ├── checker.py          # Agent 4: 規則檢查 (sync + async)
│       │   ├── orchestrator.py     # generate() + agenerate() + 快取整合
│       │   └── rate_limiter.py     # Token bucket (50 RPM, P17)
│       │
│       ├── bim/                    # === BIM 生成 ===
│       │   ├── __init__.py
│       │   ├── ifc_generator.py
│       │   ├── usd_generator.py
│       │   ├── geometry.py
│       │   ├── materials.py
│       │   ├── rules.py            # 法規引擎 (plugin 化, P17)
│       │   └── templates/
│       │
│       ├── plugins/                # === Plugin 架構 (P17+) ===
│       │   ├── __init__.py
│       │   └── base.py             # PluginRegistry + @register_plugin
│       │                           # 三種類型: agent / parser / code_rule
│       │
│       ├── cache/                  # === Plan 快取 (P17+) ===
│       │   ├── __init__.py
│       │   ├── cache_key.py        # SHA-256(prompt + land + zoning)
│       │   └── store.py            # JSON store, LRU, TTL, ~/.promptbim/cache/
│       │
│       ├── viz/                    # === 視覺化 ===
│       │   ├── __init__.py
│       │   ├── site_plan.py
│       │   ├── floorplan.py
│       │   ├── model_3d.py
│       │   └── renderer.py
│       │
│       ├── voice/                  # === 語音 ===
│       │   ├── __init__.py
│       │   └── stt.py
│       │
│       ├── mcp/                    # === MCP Server ===
│       │   ├── __init__.py
│       │   └── server.py           # FastMCP + await orchestrator.agenerate()
│       │
│       └── schemas/                # === Pydantic Models ===
│           ├── __init__.py         # schema_version 檢查 (P17)
│           ├── land.py
│           ├── zoning.py
│           ├── requirement.py
│           ├── plan.py
│           └── result.py
│
├── tests/
│   ├── test_land/
│   │   └── test_fuzzing.py         # 惡意輸入測試 (P17)
│   ├── test_agents/
│   │   └── test_network_failure.py  # 網路故障模擬 (P17)
│   ├── test_bim/
│   ├── test_gui/
│   ├── test_integration/
│   │   └── test_permissions.py      # 檔案權限錯誤 (P17)
│   └── fixtures/
│
├── docs/
│   ├── API.md
│   ├── DesignDocForV2.md
│   ├── V2_Migration_Tasks.md        # V2 遷移任務拆解 (P17)
│   ├── PromptBIM_Context_Prompt.md
│   ├── reports/
│   │   ├── Sprint17_AuditReport.md
│   │   └── Sprint17.1_AuditReport.md
│   └── addendum/
│
├── PromptBIMTestApp1/               # === Xcode SwiftUI Wrapper ===
│   ├── PromptBIMTestApp1App.swift
│   ├── ContentView.swift            # 動態版本顯示: bridge.version (P17)
│   ├── PythonBridge.swift           # @Published version + conda 多路徑
│   └── Info.plist
│
├── PromptBIMTestApp1.xcodeproj/
│
├── examples/
│
├── resources/
│
└── output/                         # .gitignore
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
    # 幾何
    boundary: list[tuple[float, float]]  # 土地邊界座標 [(x,y), ...]
    area_sqm: float                      # 面積 (平方公尺)
    perimeter_m: float                   # 周長
    # 座標系
    crs: str = "EPSG:4326"              # 原始座標系
    local_origin: tuple[float, float] = (0, 0)  # 本地座標原點
    # 來源
    source_file: str | None = None       # 原始檔案路徑
    source_type: str = "manual"          # shapefile/geojson/kml/dxf/pdf/manual

    class Config:
        arbitrary_types_allowed = True
```

### 5.2 ZoningRules（分區規則）

```python
# schemas/zoning.py
class ZoningRules(BaseModel):
    """使用分區規則"""
    zone_type: str = "residential"       # residential/commercial/industrial
    far_limit: float = 2.0              # 容積率上限 (Floor Area Ratio)
    bcr_limit: float = 0.6             # 建蔽率上限 (Building Coverage Ratio)
    height_limit_m: float = 15.0        # 高度限制 (公尺)
    setback_front_m: float = 5.0        # 前方退縮
    setback_back_m: float = 3.0         # 後方退縮
    setback_left_m: float = 2.0         # 左側退縮
    setback_right_m: float = 2.0        # 右側退縮
    min_parking_per_unit: float = 1.0   # 每戶停車位
```

### 5.3 BuildingPlan（Agent 2 輸出）

```python
# schemas/plan.py — Agent 2 (Planner) 的輸出
class BuildingPlan(BaseModel):
    """建築規劃（在土地上的配置）"""
    name: str
    schema_version: str = "2.4.0"       # Schema 版本 (P17+)
    # 土地資訊（從 LandParcel 帶入）
    land_boundary: list[tuple[float, float]]
    buildable_area: list[tuple[float, float]]  # 退縮後可建範圍

    # 建築配置
    building_footprint: list[tuple[float, float]]  # 建築 footprint
    building_bcr: float                            # 實際建蔽率
    building_far: float                            # 實際容積率

    # 樓層
    stories: list[StoryPlan]

    # 屋頂
    roof: RoofPlan
```

---

## 6. Agent 2 (Planner) — 關鍵 Prompt 設計

Planner 是最關鍵的 Agent：它必須**在真實土地形狀上**規劃合理的建築。

```python
PLANNER_SYSTEM_PROMPT = """
You are an expert architect and urban planner. Your task is to generate a
BuildingPlan JSON that places a building on a real land parcel.

## INPUT
You will receive:
1. LandParcel: boundary coordinates, area, shape
2. ZoningRules: FAR limit, BCR limit, height limit, setbacks
3. BuildingRequirement: user's building description (enhanced by Agent 1)

## CONSTRAINTS (MUST follow)
- Building footprint MUST fit inside the buildable area (land minus setbacks)
- BCR (building footprint area / land area) MUST NOT exceed bcr_limit
- FAR (total floor area / land area) MUST NOT exceed far_limit
- Building height MUST NOT exceed height_limit_m
- All coordinates are in METERS, relative to land's local origin
- Walls must form closed polygons per floor
- Every space must be bounded by walls
- Corridors minimum 1.2m width
- Doors minimum 0.9m width, 2.1m height
- Windows minimum 0.6m width, sill height 0.9m for non-ground floors

## OUTPUT
Return a valid BuildingPlan JSON matching the schema exactly.
All coordinates must be precise to 0.01m.
"""
```

---

## 7. pyproject.toml

```toml
[project]
name = "promptbim"
version = "2.4.1"
description = "Prompt to BIM — AI-powered building generation on real land parcels with IFC + OpenUSD dual output"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "Michael Lin", email = "michael@realitymatrix.com"}]

dependencies = [
    # GUI
    "PySide6>=6.6",
    "pyvista>=0.43",
    "pyvistaqt>=0.11",
    # AI
    "anthropic>=0.40.0",
    # BIM
    "ifcopenshell>=0.8.0",
    "usd-core>=24.0",
    # GIS / Land
    "geopandas>=0.14",
    "shapely>=2.0",
    "fiona>=1.9",
    "pyproj>=3.6",
    "ezdxf>=1.1",
    "fastkml>=1.0",
    "lxml>=5.0",
    # Geometry & Viz
    "mapbox-earcut>=2.0",
    "numpy>=1.26",
    "trimesh>=4.0",
    "matplotlib>=3.8",
    "Pillow>=10.0",
    # Infra
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

### P0-P6: 基礎功能（已完成，見歷史）

### P11-P14: Xcode 整合 + CLI + CI/CD（已完成）

### P16: 品質修整（已完成）
- 具名常數提取到 `constants.py`
- tenacity retry (3x exponential backoff, 5xx only)
- Agent timeout 30s
- pip-audit 修正（移除假 CVE）
- 版本同步機制建立

### P17: 全面修整 + 架構強化（已完成，v2.4.0 → v2.4.1）
- **Part A:** CI/CD 修復（requirements-frozen.txt 清理）
- **Part B:** AuditReport 修復（per_side_setback, rate limiter, schema version, file size limits, registry index, conda paths）
- **Part C:** V2 架構（lazy import, plugin 架構, V2 migration tasks 文件）
- **Part D:** 測試缺口（network failure, fuzzing, permissions — +26 tests）
- **Part E:** Swift 修復（ContentView 動態版本顯示, 報告歸檔）
- **Part F:** Async/Await（BaseAgent.arun, Orchestrator.agenerate, 並行 Agent）
- **Part G:** Plan 快取（SHA-256 key, JSON store, LRU, TTL, CLI commands）
- **Part H:** 全量文件同步 + 驗收
- **P17.1:** 審計修復 + 文檔一致性 patch（v2.4.1）

### P18: V2 Migration Phase 0-1（下一個）
- C++ 核心骨架 + CMake + vcpkg
- Compliance Engine + Cost Engine C++ 移植
- pybind11 binding + Python fallback

---

## 9. 環境設定 (Claude Code 直接執行)

```bash
cd ~/Documents/MyProjects
cd PromptBIMTestApp1

# Python 環境 (conda 推薦，因 ifcopenshell)
conda create -n promptbim python=3.11 -y
conda activate promptbim

# 核心依賴
conda install -c conda-forge ifcopenshell -y
pip install -e ".[dev]"

# 驗證
python -c "import ifcopenshell; print(f'IfcOpenShell {ifcopenshell.version}')"
python -c "from pxr import Usd; print('OpenUSD OK')"
python -c "from PySide6.QtWidgets import QApplication; print('PySide6 OK')"
python -c "import pyvista; print(f'PyVista {pyvista.__version__}')"
python -c "import geopandas; print(f'GeoPandas {geopandas.__version__}')"
python -c "import anthropic; print('Anthropic SDK OK')"
python -m promptbim --version
```

---

## 10. 開發規範

1. **GUI:** PySide6 + Qt Designer 風格，所有 widget 繼承 QWidget
2. **3D:** PyVista mesh (pv.PolyData) 作為中間格式，同時餵給 Qt 視圖和匯出
3. **Agent:** System prompt 作為 `SYSTEM_PROMPT` 常數存在各 agent .py
4. **Agent async:** 所有 AI Agent 支援 sync `run()` + async `arun()`，BuilderAgent 僅 sync
5. **Builder:** 純 Python，不用 LLM，確定性輸出
6. **土地座標:** 內部統一使用公尺制本地座標系，匯入時用 pyproj 轉換
7. **IFC:** 只用 `ifcopenshell.api.run()` 高階 API
8. **USD:** 只用 `pxr.Usd`, `pxr.UsdGeom`, `pxr.UsdShade`
9. **Git:** `[P0] Init`, `[P1] Land import`, `[P17] Hardening`, etc.
10. **測試:** pytest + pytest-qt，coverage >= 70%
11. **快取:** generate/agenerate 預設走快取，`use_cache=False` 強制重新生成
12. **Plugin:** 新增 parser/rule 優先用 @register_plugin 註冊
13. **常數:** 魔術數字必須放 `constants.py`，命名大寫

---

## 11. P11-P17 新增功能

### P11: Xcode <-> PySide6 GUI 整合
- `PythonBridge.swift` — findCondaPython(), loadDotEnv(), launchPySide6GUI(), terminateGUI()
- `ContentView.swift` — Splash screen + Python 環境檢查
- `AppDelegate` — applicationWillTerminate 確保 Python process 清理
- 23 個 E2E 整合測試

### P12: 品質修復
- PythonBridge 單實例注入（@EnvironmentObject）
- App 關閉終止 Python Process
- NSSupportsSuddenTermination 正確管理
- Pipeline 效能基準 < 5s

### P13: CLI + PDF OCR
- `generate` CLI 命令 — 完整 pipeline 從命令列執行
- `pdf_ocr.py` — PDFLandParser (pdfplumber text + PyMuPDF images + Claude Vision)
- 共用測試 fixtures (conftest.py)
- `poly_area()` 統一實作在 geometry.py

### P14: CI/CD + 安全 + 文件
- GitHub Actions CI: lint (ruff) + test (pytest) + build (xcodebuild) + security (pip-audit)
- Dependabot 自動依賴更新
- API Key 格式驗證 + .env 權限檢查
- `py.typed` marker + `__all__` exports
- `docs/API.md` API 文件
- Coverage > 70% 目標

### P16: 品質修整 (v2.1.0)
- `constants.py` — 6 個具名常數（story height, wall thickness, slab, tokens, GUI delay）
- `agents/base.py` — tenacity retry (3x, exponential backoff, 5xx only) + timeout=30s
- pip-audit 修正（移除 `|| true`，改用正確 CVE ignore）
- 版本同步機制（pyproject.toml = __init__.py = Info.plist = CHANGELOG）
- 725 tests

### P17: 全面修整 + 架構強化 (v2.4.0)
- **Async/Await:** BaseAgent.arun() + Orchestrator.agenerate() + asyncio.gather 並行
- **Plan 快取:** SHA-256 key + JSON store + LRU (max 100) + TTL 7天 + CLI commands
- **Plugin 架構:** PluginRegistry + @register_plugin + 三種類型 (agent/parser/code_rule)
- **Rate Limiter:** token bucket (50 RPM, config.py 可調)
- **Schema Versioning:** schema_version 欄位 + 載入相容性檢查
- **Lazy Import:** `--version` 路徑不觸發 agent/bim import
- **Per-Side Setback:** 逐邊退縮支援（矩形+L形）
- **Input Size Limits:** MAX_LAND_FILE_SIZE_MB = 50
- **ComponentRegistry Index:** `_by_category` 倒排索引
- **PythonBridge 多路徑:** Intel Mac + `which python3` fallback + PROMPTBIM_PYTHON env
- **ContentView 動態版本:** `bridge.version` 替代硬編碼
- **V2 Migration Tasks:** docs/V2_Migration_Tasks.md
- 792→799 tests

### CLI 使用範例

```bash
python -m promptbim --version
python -m promptbim gui [--debug]
python -m promptbim generate "3-story villa" -o ./output [--land site.geojson] [--city Taipei]
python -m promptbim generate --no-cache "villa" -o ./output
python -m promptbim cache list
python -m promptbim cache clear
python -m promptbim cache stats
python -m promptbim check [--ai] [--fix] [--json]
```

### CI/CD 流程

```
git push → GitHub Actions:
  1. Setup conda + Python 3.11
  2. pip install -e ".[dev]"
  3. ruff check src/ tests/
  4. pytest -m "not api and not slow" --cov --cov-fail-under=70
  5. xcodebuild build (macOS runner)
  6. pip-audit security scan
```

---

*SKILL.md v3.7 | 2026-03-26 | 100% 開源 + 桌面 App + GIS + IFC/USD + Async + Cache + Plugins + CI/CD*

---

## 附錄文件 (Addendum)

完整技術規格分為三份附錄文件，位於 `docs/addendum/`：

| 文件 | 內容 | 對應 Sprint |
|------|------|------------|
| `01_component_library.md` | 74 種建築零件庫 + 供應商 + 價格 | P2.5 |
| `02_sim_cost_mep.md` | 施工模擬 (4D) + 成本估算 (5D) + MEP 管線 | P6, P7, P8 |
| `03_tw_building_codes.md` | 台灣建築法規引擎 | P4.5 |

Claude Code 開發各 Sprint 前，**必須先讀取 SKILL.md + 對應的附錄文件**。
