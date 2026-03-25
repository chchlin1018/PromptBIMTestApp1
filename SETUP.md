# PromptBIMTestApp1 — 安裝與測試指南

> **版本:** v1.0.0 | **平台:** macOS (主力) | **Python:** 3.11+
> **性質:** 概念驗證 (POC) — 展示 AI 驅動 BIM 自動生成的完整工作流

---

## 專案概念

PromptBIMTestApp1 是一個 **Prompt-to-Building** POC 系統。

使用者只需要做兩件事：
1. **輸入土地** — 土地大小/形狀（GeoJSON、座標、或隨意描述面積）
2. **輸入 Prompt** — 用自然語言描述想蓋的建築

系統會自動完成所有後續工作：

```
用戶輸入                        系統自動產生
─────────────                   ─────────────────────────────────
土地: 500坪商業用地               ✅ 建築設計 (平面/立面)
Prompt: "12層住宅大樓"           ✅ 3D BIM 模型 (IFC + OpenUSD)
                                 ✅ MEP 管線 (水/電/空調/消防)
                                 ✅ 台灣法規合規檢查
                                 ✅ 施工模擬動畫 (4D)
                                 ✅ 建設成本估算 (5D)
                                 ✅ 各層平面圖 + 配置圖
                                 ✅ 建築零件清單 + 供應商報價
```

### Prompt 範例

| Prompt | 系統自動處理 |
|--------|------------|
| `帶游泳池的3層別墅` | AI 設計含泳池的住宅平面、結構、MEP |
| `12層住宅大樓` | 自動規劃每層戶型、電梯配置、消防逃生 |
| `3層樓標準工廠廠房` | 工業用途大跨距結構、貨梯、通風系統 |
| `100MW 數據中心` | AI 搜尋數據中心規格、冷卻系統、UPS 配電 |
| `帶地下停車場的商辦大樓` | 地下室、車道、排煙、汙水處理 |
| `鄰近學校的社區活動中心` | 無障礙設施、多功能廳、消防避難 |

**AI 會自行搜尋資料、下載免費 3D 模型、套用建築規範、計算結構尺寸。**
使用者不需要懂建築——只需要說出想法。

---

## 系統需求

### 硬體

| 項目 | 最低需求 | 建議 |
|------|---------|------|
| CPU | Apple M1 | Apple M2 Pro 以上 |
| RAM | 8 GB | 16 GB 以上 |
| 儲存空間 | 5 GB | 10 GB（含模型快取）|
| 顯示器 | 1440×900 | 2560×1600 (Retina) |

### 軟體

| 項目 | 版本 | 備註 |
|------|------|------|
| **macOS** | 13.0 Ventura 以上 | 建議 15.0 Sequoia |
| **Python** | 3.11+ | 建議透過 Conda 安裝 |
| **Conda** | Miniconda 或 Miniforge | 推薦 Miniforge (ARM native) |
| **Git** | 2.30+ | Xcode Command Line Tools 含 |
| **F3D** | 3.3+ (選用) | `brew install f3d` |

### API Key

| 服務 | 用途 | 取得方式 |
|------|------|----------|
| **Anthropic Claude API** | AI 建築生成核心 | [console.anthropic.com](https://console.anthropic.com) |

> ⚠️ Claude API 是唯一的付費項目（按用量計費）。其餘全部開源免費。

---

## 安裝步驟

### Step 1: 安裝 Miniforge (如果尚未安裝)

```bash
# 下載 Miniforge (Apple Silicon native)
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh"
bash Miniforge3-MacOSX-arm64.sh -b
source ~/miniforge3/bin/activate
```

### Step 2: Clone 專案

```bash
cd ~/Documents/MyProjects  # 或你喜歡的位置
git clone https://github.com/chchlin1018/PromptBIMTestApp1.git
cd PromptBIMTestApp1
```

### Step 3: 建立 Conda 環境

```bash
# 建立獨立 Python 環境
conda create -n promptbim python=3.11 -y
conda activate promptbim

# 安裝 IfcOpenShell (必須透過 conda-forge)
conda install -c conda-forge ifcopenshell -y
```

### Step 4: 安裝 Python 依賴

```bash
# 核心依賴
pip install PySide6 pyvista pyvistaqt
pip install anthropic pydantic python-dotenv rich
pip install usd-core
pip install geopandas shapely fiona pyproj ezdxf fastkml
pip install numpy trimesh matplotlib Pillow
pip install pdfplumber  # PDF 地籍圖解析

# 開發依賴（選用）
pip install pytest ruff pytest-qt pytest-cov

# 語音輸入（選用）
pip install faster-whisper

# MCP Server — Claude Desktop 整合（選用）
pip install "mcp>=1.0"

# Web UI — Streamlit（選用）
pip install streamlit
```

### Step 5: 設定 API Key

```bash
cp .env.example .env
```

編輯 `.env` 檔案：
```env
ANTHROPIC_API_KEY=sk-ant-api03-你的KEY
DEFAULT_CITY=台北市
```

### Step 6: 安裝 F3D 3D 檢視器（選用但建議）

```bash
brew install f3d

# 驗證
f3d --version
```

### Step 7: 驗證安裝

```bash
# 執行驗證腳本
python -c "
import sys
print(f'Python: {sys.version}')

try:
    import ifcopenshell
    print(f'✅ IfcOpenShell: {ifcopenshell.version}')
except: print('❌ IfcOpenShell')

try:
    from pxr import Usd
    print(f'✅ OpenUSD: OK')
except: print('❌ OpenUSD (usd-core)')

try:
    from PySide6.QtWidgets import QApplication
    print(f'✅ PySide6: OK')
except: print('❌ PySide6')

try:
    import pyvista
    print(f'✅ PyVista: {pyvista.__version__}')
except: print('❌ PyVista')

try:
    import geopandas
    print(f'✅ GeoPandas: {geopandas.__version__}')
except: print('❌ GeoPandas')

try:
    import anthropic
    print(f'✅ Anthropic SDK: OK')
except: print('❌ Anthropic SDK')

try:
    import shapely
    print(f'✅ Shapely: {shapely.__version__}')
except: print('❌ Shapely')

try:
    import trimesh
    print(f'✅ Trimesh: {trimesh.__version__}')
except: print('❌ Trimesh')

print('\n--- 驗證完成 ---')
"
```

預期輸出：
```
Python: 3.11.x
✅ IfcOpenShell: 0.8.x
✅ OpenUSD: OK
✅ PySide6: OK
✅ PyVista: 0.4x.x
✅ GeoPandas: 0.1x.x
✅ Anthropic SDK: OK
✅ Shapely: 2.x.x
✅ Trimesh: 4.x.x

--- 驗證完成 ---
```

---

## 啟動 App

### GUI 模式（主要使用方式）

```bash
conda activate promptbim
python -m promptbim gui
```

### CLI 模式

```bash
# 查看版本
promptbim --version

# 直接從 prompt 生成
promptbim generate "在 300 坪地上蓋帶游泳池的3層別墅"

# 指定土地檔案
promptbim generate --land reference/sample_parcel.geojson "12層住宅大樓"

# 列出可用建築模板
promptbim templates

# 執行法規檢查
promptbim check output/model.ifc --city 台北市 --zone 住三
```

---

## 使用流程

### 流程 A：快速生成（只需 Prompt）

```
1. 啟動 App
2. 在底部 Chat 面板輸入:
   "在 200 坪的地上蓋一棟帶游泳池的3層別墅"
3. 等待 30-60 秒
4. 2D Tab: 查看平面配置
5. 3D Tab: 旋轉查看建築模型
6. 點擊「匯出」→ 一鍵下載所有檔案
```

### 流程 B：帶土地資料生成

```
1. 啟動 App
2. File > Import Land → 選擇 .geojson / .shp / .dxf
   (或拖放檔案到視窗)
3. 左側面板顯示土地資訊（面積、退縮線）
4. 設定分區（住宅/商業/工業）和法規參數
5. 在 Chat 輸入: "12層住宅大樓，每層4戶"
6. AI 自動在土地上生成合規的建築
7. 查看 → 調整 → 匯出
```

### 流程 C：語音輸入

```
1. 啟動 App + 匯入土地
2. 按住 🎤 按鈕
3. 說: "幫我在這塊地上蓋一個三層樓的標準工廠"
4. 放開按鈕 → AI 處理 → 生成建築
```

---

## 輸出檔案

每次生成後，系統自動產生以下檔案：

```
output/
├── project_name.ifc          # BIM 模型（完整語義）
├── project_name.usda         # OpenUSD 場景（Digital Twin）
├── floorplan_1F.svg          # 一樓平面圖
├── floorplan_2F.svg          # 二樓平面圖
├── floorplan_3F.svg          # ...
├── site_plan.svg             # 配置圖（土地+建築+退縮線）
├── preview_front.png         # 3D 正面預覽
├── preview_aerial.png        # 3D 鳥瞰預覽
├── mep_plumbing.ifc          # 給排水管線（藍色）
├── mep_electrical.ifc        # 電力管線（紅色）
├── mep_hvac.ifc              # 空調管線（綠色）
├── mep_fire.ifc              # 消防管線（黃色）
├── construction_anim.gif     # 施工模擬動畫
├── gantt_chart.svg           # 施工甘特圖
├── cost_estimate.csv         # 成本估算明細
├── cost_summary.json         # 成本摘要
├── compliance_report.json    # 法規合規報告
└── summary.json              # 建築參數總表
```

### 檢視輸出

```bash
# 用 F3D 查看 IFC
f3d output/project_name.ifc

# 用 F3D 查看 USD
f3d output/project_name.usda

# 用瀏覽器查看 SVG
open output/site_plan.svg

# 用 Preview 查看 GIF
open output/construction_anim.gif
```

---

## 測試

### 單元測試

```bash
conda activate promptbim
python -m pytest tests/ -v
```

### 整合測試（需要 API Key）

```bash
python -m pytest tests/ -v -m integration
```

### 手動測試 Prompt

使用 `examples/test_prompts.txt` 中的 12 個測試案例：

```bash
# 依序測試
promptbim generate "Build a simple 2-story rectangular house"
promptbim generate "建一棟3層樓的方形辦公大樓"
promptbim generate --land reference/sample_parcel.geojson "在台北信義區蓋10層辦公大樓"
```

### 快速冒煙測試（不需 API Key）

```bash
# 測試 IFC 生成（硬編碼，不用 Claude）
python examples/01_simple_box.py

# 驗證輸出
ls -la output/simple_box.ifc output/simple_box.usda
f3d output/simple_box.ifc  # 如果有安裝 F3D
```

---

## 常見問題

### Q: IfcOpenShell 安裝失敗？

```bash
# 必須用 conda-forge，pip 安裝可能缺少二進制
conda install -c conda-forge ifcopenshell -y

# 如果還是失敗，嘗試指定版本
conda install -c conda-forge ifcopenshell=0.8.1 -y
```

### Q: PySide6 在 macOS 上閃退？

```bash
# 確保沒有同時安裝 PyQt5
pip uninstall PyQt5 PyQt5-sip -y

# 重新安裝
pip install --force-reinstall PySide6
```

### Q: usd-core 匯入失敗？

```bash
# usd-core 需要特定 Python 版本
pip install usd-core==24.11  # 指定版本

# 如果衝突，在獨立 venv 中測試
python -c "from pxr import Usd; print('OK')"
```

### Q: PyVista 3D 視窗沒有出現？

```bash
# macOS 需要允許 VTK 使用 GPU
export DISPLAY=:0  # 有時需要

# 或使用軟體渲染
export PYVISTA_OFF_SCREEN=true
```

### Q: Claude API 費用大概多少？

每次建築生成約消耗 2000-5000 tokens（Enhancer + Planner + Checker），以 Claude Sonnet 計算約 USD $0.01-0.03 / 次。一天測試 100 次約 USD $1-3。

### Q: 沒有土地資料怎麼辦？

系統支援三種方式：
1. **隨意描述面積** — "在 200 坪的地上" → AI 自動假設矩形
2. **手動繪製** — 在 2D 視圖中用滑鼠畫多邊形
3. **使用範例** — `reference/sample_parcel.geojson` 台北信義區 300 坪

### Q: 可以在 Windows 上跑嗎？

技術上所有依賴都支援 Windows，但 POC 階段主要在 macOS 上開發和測試。Windows 支援列在未來 Backlog 中。

---

## 開發者指南

### 程式碼風格

```bash
# Lint
ruff check src/

# Format
ruff format src/
```

### 新增功能

1. 讀取 `SKILL.md` 了解架構
2. 讀取 `docs/addendum/` 對應的附錄
3. 按 TODO.md 的 Sprint 順序開發
4. 每完成一個 Sprint 更新 TODO.md 和 CHANGELOG.md
5. Commit 格式: `[P2] Add IFC wall generation`

### Claude Code 使用

```bash
# 進入專案目錄
cd ~/Documents/MyProjects/PromptBIMTestApp1
conda activate promptbim

# 告訴 Claude Code 開始某個 Sprint
claude "讀取 SKILL.md 和 docs/addendum/01_component_library.md，
        然後執行 Sprint P2.5: 建立建築零件庫"
```

---

## 專案架構速覽

```
PromptBIMTestApp1/
├── 📋 文件控制
│   ├── README.md         # 專案介紹（中文）
│   ├── SETUP.md          # 安裝測試指南（本文件）
│   ├── SKILL.md          # Claude Code 知識庫 (SSOT)
│   ├── TODO.md           # Sprint 追蹤
│   ├── CHANGELOG.md      # 版本記錄
│   └── LICENSE           # MIT
│
├── 📖 技術規格
│   └── docs/addendum/
│       ├── 01_component_library.md   # 零件庫
│       ├── 02_sim_cost_mep.md        # 4D/5D/MEP
│       └── 03_tw_building_codes.md   # 法規引擎
│
├── 🏗️ 原始碼
│   └── src/promptbim/
│       ├── gui/          # PySide6 桌面 App
│       ├── agents/       # Claude AI Multi-Agent
│       ├── bim/          # IFC + USD 生成
│       ├── land/         # GIS 土地處理
│       ├── viz/          # 視覺化
│       ├── codes/        # 台灣法規引擎
│       ├── voice/        # 語音輸入
│       └── schemas/      # Pydantic 資料模型
│
├── 🧪 測試 & 範例
│   ├── tests/
│   ├── examples/
│   └── reference/        # GeoJSON 土地範例
│
└── 📦 輸出 (gitignore)
    └── output/           # .ifc .usda .svg .gif .csv .json
```

---

*SETUP.md v1.0.0 | 2026-03-25 | macOS POC 安裝指南*
