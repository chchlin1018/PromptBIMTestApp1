# PromptBIMTestApp1 — 安裝與測試指南

> **版本:** v2.8.0 | **更新:** 2026-03-26 | **平台:** macOS (主力) | **Python:** 3.11+ | **C++:** 17
> **性質:** 概念驗證 (POC) — 展示 AI 驅動 BIM 自動生成的完整工作流

---

## 專案概念

PromptBIMTestApp1 是一個 **Prompt-to-Building** POC 系統。

使用者只需要做兩件事：
1. **輸入土地** — 土地大小/形狀（GeoJSON、座標、或隨意描述面積）
2. **輸入 Prompt** — 用自然語言描述想蓋的建築

系統會自動完成所有後續工作（BIM 生成、MEP、法規、4D/5D、監控點、即時修改）。

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
| **macOS** | 14.0 Sonoma 以上 | 建議 15.0+ |
| **Xcode** | 16.0+ | 含 SwiftUI, SceneKit, macOS target |
| **Python** | 3.11+ | 建議透過 Conda 安裝 |
| **Conda** | Miniconda 或 Miniforge | 推薦 Miniforge (ARM native) |
| **CMake** | 3.20+ | 編譯 C++ 核心需要 |
| **Git** | 2.30+ | Xcode Command Line Tools 含 |

### API Key

| 服務 | 用途 | 取得方式 |
|------|------|----------|
| **Anthropic Claude API** | AI 建築生成核心 | [console.anthropic.com](https://console.anthropic.com) |

> ⚠️ Claude API 是唯一的付費項目（按用量計費）。其餘全部開源免費。

---

## 安裝步驟

### Step 1: 安裝 Miniforge (如果尚未安裝)

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh"
bash Miniforge3-MacOSX-arm64.sh -b
source ~/miniforge3/bin/activate
```

### Step 2: Clone 專案

```bash
cd ~/Documents/MyProjects
git clone https://github.com/chchlin1018/PromptBIMTestApp1.git
cd PromptBIMTestApp1
```

### Step 3: 建立 Conda 環境 + 安裝依賴

```bash
conda create -n promptbim python=3.11 -y
conda activate promptbim
conda install -c conda-forge ifcopenshell -y
pip install -e ".[dev]"
```

> `pip install -e ".[dev]"` 會一次安裝所有核心依賴 + 開發工具（pytest, ruff, pytest-cov 等）。
> 如果只需要基本功能，可以用 `pip install -e "."` 代替。

### Step 4: 設定 Claude AI API Key

```bash
cp .env.example .env
chmod 600 .env
nano .env
# 填入: ANTHROPIC_API_KEY=sk-ant-api03-你的Key
```

> ⚠️ `.env` 已在 `.gitignore` 中，不會被推到 GitHub。

### Step 5: 驗證安裝

```bash
conda activate promptbim
python -m promptbim --version   # 應顯示 v2.8.0
python -m promptbim check       # 12 項環境檢查
```

### Step 6: 編譯 C++ 核心（選用，建議）

```bash
cd libpromptbim
mkdir -p build && cd build
cmake ..
make -j$(sysctl -n hw.ncpu)
ctest --output-on-failure   # 應顯示 137 tests passed
cd ../..
```

> C++ 核心提供高效能的 Compliance/Cost/MEP/Simulation/IFC/USD/GIS 引擎。
> 如果不編譯 C++，Python 會自動 fallback 到純 Python 實作。

### Step 7: 用 Xcode 開啟專案

```bash
cd ~/Documents/MyProjects/PromptBIMTestApp1
open PromptBIMTestApp1.xcodeproj
# Cmd+B Build → 應顯示 BUILD SUCCEEDED
# Cmd+R Run → SwiftUI Splash Screen + PySide6 GUI 啟動
```

---

## 啟動 App

### 方式 1：PySide6 GUI（主要使用方式）

```bash
conda activate promptbim
python -m promptbim gui          # 完整 GUI
python -m promptbim gui --debug  # Debug 模式
```

### 方式 2：Xcode SwiftUI（含 3D 預覽）

```bash
open PromptBIMTestApp1.xcodeproj
# Cmd+R 啟動
# SwiftUI App 含 Dashboard + 3D Preview (SceneKit) Tab
# PySide6 GUI 會在另一個視窗開啟
```

### 方式 3：CLI 直接生成

```bash
# 查看版本
python -m promptbim --version

# 直接從 prompt 生成
python -m promptbim generate "在 300 坪地上蓋帶游泳池的3層別墅" -o ./output
python -m promptbim generate --land site.geojson "12層住宅大樓"
python -m promptbim generate --no-cache "工廠" -o ./output  # 跳過快取

# 快取管理
python -m promptbim cache list    # 列出快取
python -m promptbim cache stats   # 命中率
python -m promptbim cache clear   # 清除快取

# 環境健康檢查
python -m promptbim check         # 全部 12 項
python -m promptbim check --ai    # 只檢查 AI
python -m promptbim check --fix   # 自動修復
```

### 方式 4：Web UI + MCP Server（選用）

```bash
# Streamlit Web UI
pip install -e ".[web]"
streamlit run src/promptbim/web/app.py

# MCP Server (Claude Desktop 整合)
pip install -e ".[mcp]"
python -m promptbim.mcp.server
```

---

## 使用流程

### 流程 A：快速生成（只需 Prompt）

```
1. conda activate promptbim && python -m promptbim gui
2. 在底部 Chat 面板輸入:
   "在 200 坪的地上蓋一棟帶游泳池的3層別墅"
3. 等待 30-60 秒（AI 7-Agent Pipeline）
4. 2D Tab: 查看平面配置 + 退縮線
5. 3D Tab: 旋轉查看建築模型
6. 點擊「匯出」→ 一鍵下載所有檔案
```

### 流程 B：圖片匯入（AI 圖像辨識）

```
1. 啟動 App
2. File > Import Land > Image (AI) Tab
3. 拖放任意圖片（照片/截圖/掌描/手繪）
4. Claude Vision 自動辨識土地邊界
5. 預覽確認（可微調頂點）→ 確認
6. 在 Chat 輸入 Prompt → 生成
```

### 流程 C：Xcode SwiftUI 3D 預覽（v2.8.0 新增）

```
1. open PromptBIMTestApp1.xcodeproj && Cmd+R
2. Dashboard Tab: 查看專案狀態
3. 3D Preview Tab: SceneKit 即時預覽
4. Generate 按鈕: 透過 NativeBIMBridge 呼叫 C++ 核心
5. 生成結果自動載入 SceneKit 場景
```

---

## 輸出檔案

```
output/
├── model.ifc              ← BIM 模型（含 MEP + 監控點）
├── model.usda             ← OpenUSD（含 monitor: namespace）
├── model.usdz             ← Apple Vision Pro / Quick Look
├── floorplan_*.svg        ← 各層平面圖
├── site_plan.svg          ← 配置圖
├── construction_anim.gif  ← 施工模擬動畫 (4D)
├── gantt_chart.svg        ← 施工甘特圖
├── cost_estimate.csv      ← 成本估算明細 (5D)
├── compliance_report.json ← 法規合規報告
└── monitor_dashboard.json ← 監控點清單
```

---

## 測試

```bash
conda activate promptbim

# Python 測試 (820 tests)
python -m pytest tests/ -v
python -m pytest tests/ -m "not api and not slow" -q   # 快速測試
python -m pytest --cov=src/promptbim --cov-report=term-missing

# C++ GoogleTest (137 tests)
cd libpromptbim/build
ctest --output-on-failure

# Xcode Build
xcodebuild -project PromptBIMTestApp1.xcodeproj \
  -scheme PromptBIMTestApp1 -destination 'platform=macOS' build

# Lint + Security
ruff check src/ tests/
pip-audit -r requirements-frozen.txt
```

---

## 多台機器開發

### Mac Mini M4（Claude Code 執行）

```bash
ssh michaellin@michaelmac-mini
tmux new -s dev || tmux attach -t dev
cd ~/Documents/MyProjects/PromptBIMTestApp1
git pull origin main && conda activate promptbim
unset ANTHROPIC_API_KEY  # 確保走 Max 訂閱而非 API 計費
claude --dangerously-skip-permissions -p "請讀取 PROMPT_P{X}.md 並執行所有 task。不要問任何問題。"
```

> ⚠️ **重要：** 每次執行 Claude Code 前必須 `unset ANTHROPIC_API_KEY`，否則會走 API 計費而非 Claude Max 訂閱。
> `.env` 中的 API Key 是給 Python App 的 AI Agent 使用，不能刪除。

### MacBook（Xcode + 測試）

```bash
cd ~/documents/myprojects/PromptBIMTestApp1
git pull origin main
conda activate promptbim
pip install -e ".[dev]"  # 首次或有新依賴時執行
open PromptBIMTestApp1.xcodeproj
```

---

## 常見問題

### Q: GUI 啟動失敗，顯示 "No module named 'tenacity'"?

```bash
conda activate promptbim
pip install -e ".[dev]"  # 重新安裝所有依賴
```

### Q: Claude API Key 無效？

```bash
grep ANTHROPIC_API_KEY .env
# 應顯示: ANTHROPIC_API_KEY=sk-ant-api03-...
python -m promptbim check --ai
```

### Q: Claude Code 顯示 "credit balance too low"?

```bash
unset ANTHROPIC_API_KEY
echo $ANTHROPIC_API_KEY  # 確認空白
# 重新執行 claude 指令
```

### Q: Xcode Build 失敗？

```bash
git pull origin main   # 確保最新代碼
xcodebuild -project PromptBIMTestApp1.xcodeproj \
  -scheme PromptBIMTestApp1 -destination 'platform=macOS' build 2>&1 | tail -20
```

### Q: PySide6 GUI 看不到？

從 Xcode 啟動時，PySide6 GUI 是另一個獨立視窗。用 `Cmd+Tab` 切換到 Python 圖示的視窗。
或者直接從 Terminal 啟動：`python -m promptbim gui`

### Q: CJK 字型警告（DejaVu Sans）?

這是 matplotlib 的字型警告，不影響功能。中文標註可能顯示為方塊，但建築生成本身完全正常。

---

*SETUP.md v2.8.0 | 2026-03-26 | 更新: V2 C++ 核心 + SwiftUI 3D + 快取管理 + 多台機器開發 + API Key 計費問題修復*
