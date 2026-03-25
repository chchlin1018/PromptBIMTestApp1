# PromptBIMTestApp1 — 安裝與測試指南

> **版本:** v1.1.0 | **更新:** 2026-03-25 | **平台:** macOS (主力) | **Python:** 3.11+
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
| **macOS** | 13.0 Ventura 以上 | 建議 15.0 Sequoia |
| **Xcode** | 16.0+ | 含 SwiftUI, macOS target |
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

### Step 3: 建立 Conda 環境

```bash
conda create -n promptbim python=3.11 -y
conda activate promptbim
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
pip install pdfplumber mapbox-earcut

# 開發依賴（選用）
pip install pytest ruff pytest-qt pytest-cov

# 語音輸入（選用）
pip install faster-whisper sounddevice

# MCP Server（選用）
pip install "mcp>=1.0"

# Web UI（選用）
pip install streamlit
```

### Step 5: 設定 Claude AI API Key

#### 5a. 取得 API Key

1. 前往 [Anthropic Console](https://console.anthropic.com/settings/keys)
2. 登入帳號（或註冊新帳號）
3. 點擊 **Create Key**
4. 複製產生的 Key（格式：`sk-ant-api03-...`）

> ⚠️ Key 只會顯示一次，請立即複製保存。

#### 5b. 建立 .env 檔案

```bash
cd ~/Documents/MyProjects/PromptBIMTestApp1
cp .env.example .env
```

#### 5c. 編輯 .env 填入 API Key

```bash
nano .env
```

找到這行並填入你的 Key：
```env
ANTHROPIC_API_KEY=sk-ant-api03-你的完整Key貼在這裡
DEFAULT_CITY=台北市
```

存檔：`Ctrl + O` → `Enter` → `Ctrl + X`

#### 5d. 驗證 API Key

```bash
# 確認格式正確
grep ANTHROPIC_API_KEY .env
# 應顯示：ANTHROPIC_API_KEY=sk-ant-api03-...

# 驗證 API 連線（P10.3 完成後可用）
python -m promptbim check --ai
```

#### 5e. 安全提醒

- `.env` 已在 `.gitignore` 中，**不會被推到 GitHub**
- 不要把 API Key 寫在程式碼裡
- 如果 Key 不小心被 commit，立刻到 Anthropic Console 撤銷並建立新的
- 多台機器開發時，每台機器都需要各自設定 `.env`

### Step 6: 用 Xcode 開啟專案

#### 6a. 在 Terminal 開啟

```bash
cd ~/Documents/MyProjects/PromptBIMTestApp1
open PromptBIMTestApp1.xcodeproj
```

或在 Finder 雙擊 `PromptBIMTestApp1.xcodeproj`。

#### 6b. 確認 Xcode 設定

1. 上方工具列 Scheme 選擇：**PromptBIMTestApp1**
2. Destination 選擇：**My Mac**（Apple Silicon）
3. 按 `Cmd + B` Build → 應顯示 **BUILD SUCCEEDED**

#### 6c. 同步 GitHub

```bash
# 每次開發前先拉最新
git pull origin main

# 你修改後推回 GitHub
git add -A
git commit -m "描述你的修改"
git push origin main
```

Xcode 會自動偵測檔案變更，`git pull` 後不需重開專案。

### Step 7: 安裝 F3D 3D 檢視器（選用但建議）

```bash
brew install f3d
```

### Step 8: 驗證安裝

```bash
conda activate promptbim
python -c "
import sys; print(f'Python: {sys.version}')
try:
    import ifcopenshell; print(f'✅ IfcOpenShell: {ifcopenshell.version}')
except: print('❌ IfcOpenShell')
try:
    from pxr import Usd; print('✅ OpenUSD: OK')
except: print('❌ OpenUSD (usd-core)')
try:
    from PySide6.QtWidgets import QApplication; print('✅ PySide6: OK')
except: print('❌ PySide6')
try:
    import pyvista; print(f'✅ PyVista: {pyvista.__version__}')
except: print('❌ PyVista')
try:
    import anthropic; print('✅ Anthropic SDK: OK')
except: print('❌ Anthropic SDK')
try:
    import shapely; print(f'✅ Shapely: {shapely.__version__}')
except: print('❌ Shapely')
print('\n--- 驗證完成 ---')
"
```

---

## 啟動 App

### GUI 模式（主要使用方式）

```bash
conda activate promptbim
python -m promptbim gui
```

App 啟動時會自動執行環境檢查（P10.3 功能），確認 Python 依賴、Claude API 連線、檔案系統都正常。

### Debug 模式（顯示詳細 log）

```bash
# 方法 1: CLI 參數
python -m promptbim gui --debug

# 方法 2: 環境變數
export PROMPTBIM_DEBUG=1
python -m promptbim gui

# 方法 3: .env 中設定
# PROMPTBIM_DEBUG=1
```

Production 模式（預設）只顯示 WARNING 和 ERROR，無效能影響。

### CLI 模式

```bash
# 查看版本
python -m promptbim --version

# 環境健康檢查
python -m promptbim check           # 全部 12 項檢查
python -m promptbim check --ai      # 只檢查 AI 相關
python -m promptbim check --json    # JSON 格式輸出

# 直接從 prompt 生成
python -m promptbim generate "在 300 坪地上蓋帶游泳池的3層別墅"

# 指定土地檔案
python -m promptbim generate --land reference/sample_parcel.geojson "12層住宅大樓"
```

### MCP Server（Claude Desktop 整合）

```bash
# 啟動 MCP Server
python -m promptbim.mcp.server

# Claude Desktop 設定檔在 mcp/config.json
```

### Web UI（Streamlit）

```bash
streamlit run src/promptbim/web/app.py
```

---

## 使用流程

### 流程 A：快速生成（只需 Prompt）

```
1. conda activate promptbim && python -m promptbim gui
2. 在底部 Chat 面板輸入:
   "在 200 坪的地上蓋一棟帶游泳池的3層別墅"
3. 等待 30-60 秒
4. 2D Tab: 查看平面配置
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

### 流程 C：語音輸入

```
1. 啟動 App + 匯入土地
2. 按住 🎤 按鈕
3. 說: "幫我在這塊地上蓋一個三層樓的標準工廠"
4. 放開按鈕 → AI 處理 → 生成建築
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

# 全部測試
python -m pytest tests/ -v

# 快速冒煙測試（不需 API Key）
python examples/01_simple_box.py
ls -la output/simple_box.ifc output/simple_box.usda
```

---

## 常見問題

### Q: Claude API Key 無效？

```bash
# 確認 .env 格式
cat .env | grep ANTHROPIC
# 應顯示: ANTHROPIC_API_KEY=sk-ant-api03-...

# Key 必須以 sk-ant- 開頭
# 如果無效，到 console.anthropic.com 重新產生
```

### Q: Claude API 費用？

每次建築生成約消耗 2000-5000 tokens，以 Claude Sonnet 計算約 USD $0.01-0.03 / 次。

### Q: IfcOpenShell 安裝失敗？

```bash
conda install -c conda-forge ifcopenshell=0.8.1 -y
```

### Q: 多台機器開發？

每台機器都需要：
1. `git clone` 或 `git pull` 同步程式碼
2. `conda create -n promptbim` 建立環境
3. `cp .env.example .env` 並填入 API Key
4. `.env` 不會被同步，每台機器各自設定

---

## 開發者指南

### Claude Code CLI 自動開發

```bash
cd ~/Documents/MyProjects/PromptBIMTestApp1
conda activate promptbim
claude --dangerously-skip-permissions -p "請讀取 PROMPT_P{X}.md 並執行所有 task。不要問任何問題。"
```

### 在 Mac Mini 上用 tmux 執行（推薦）

```bash
ssh michaellin@MichaeldeMac-mini.local
tmux new -s dev   # 或 tmux attach -t dev
cd ~/Documents/MyProjects/PromptBIMTestApp1
git pull origin main && conda activate promptbim
claude --dangerously-skip-permissions -p "請讀取 PROMPT_P{X}.md 並執行所有 task。不要問任何問題。"
# Ctrl+B 再按 D 脱離 tmux，SSH 斷線也不影響
```

Sprint 完成時會自動透過 iMessage 通知你的 iPhone。

---

*SETUP.md v1.1.0 | 2026-03-25 | 新增: API Key 詳細設定步驟 + Xcode 開啟方式 + Debug 模式 + 環境檢查 + MCP/Web UI 啟動*
