# BuildSetupAndDemo_0326.md — 本機建構與 Demo 使用指南

> **版本:** v2.9.0 (P22) → v2.9.1 (P22.1 規劃中)
> **日期:** 2026-03-26
> **平台:** macOS 14.0+ (Apple Silicon / Intel)
> **IDE:** Xcode 16.0+
> **作者:** Michael Lin / Reality Matrix Inc.

---

## 一、前置環境準備

### 1.1 系統需求

| 項目 | 最低要求 |
|------|---------|
| macOS | 14.0 Sonoma+ |
| Xcode | 16.0+ |
| Python | 3.11+ (via Conda) |
| Git | 2.39+ |
| 硬碟空間 | ~5GB (含 conda 環境) |

### 1.2 Clone 專案

```bash
git clone git@github.com:chchlin1018/PromptBIMTestApp1.git
cd PromptBIMTestApp1
```

### 1.3 Python 環境安裝 (Conda)

```bash
# 安裝 Miniforge (如未安裝)
brew install miniforge

# 建立 promptbim 環境
conda create -n promptbim python=3.11 -y
conda activate promptbim

# 安裝 IfcOpenShell (必須用 conda)
conda install -c conda-forge ifcopenshell -y

# 安裝其他依賴
pip install -e ".[dev]"
```

### 1.4 驗證 Python 環境

```bash
python -c "import ifcopenshell; print(f'IfcOpenShell {ifcopenshell.version}')"
python -c "from pxr import Usd; print('OpenUSD OK')"
python -c "from PySide6.QtWidgets import QApplication; print('PySide6 OK')"
python -c "import pyvista; print(f'PyVista {pyvista.__version__}')"
python -c "import anthropic; print('Anthropic SDK OK')"
python -m promptbim --version
```

應該看到: `promptbim 2.9.0`

### 1.5 設定 API Key

```bash
cp .env.example .env
chmod 600 .env

# 編輯 .env，填入你的 Anthropic API Key
# ANTHROPIC_API_KEY=sk-ant-api03-...
```

### 1.6 C++ Core 建構 (選用)

```bash
cd libpromptbim
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(sysctl -n hw.ncpu)
cd ../..

# 驗證
cd libpromptbim/build && ctest --output-on-failure && cd ../..
```

---

## 二、Xcode 建構步驟

### 2.1 開啟專案

```bash
open PromptBIMTestApp1.xcodeproj
```

### 2.2 Xcode 設定檢查

| 設定項 | 期望值 |
|--------|--------|
| Scheme | `PromptBIMTestApp1` |
| Build Configuration | `Debug` |
| Destination | `My Mac` |
| Signing | `Sign to Run Locally` (ad-hoc) |
| Bundle ID | `com.realitymatrix.PromptBIMTestApp1` |
| Deployment Target | `macOS 14.0` |
| Swift Language Version | `6.0` |

### 2.3 Signing 設定 (重要)

因為是開發階段，不需要 Apple Developer Certificate：

1. 選擇 Target `PromptBIMTestApp1`
2. 進入 `Signing & Capabilities` tab
3. 取消勾選 `Automatically manage signing`
4. Signing Certificate 選 `Sign to Run Locally`
5. 或者保持 ad-hoc：`ENABLE_USER_SCRIPT_SANDBOXING = NO`

### 2.4 Build (Command + B)

```
快捷鍵: ⌘B
```

或用命令列：

```bash
xcodebuild -project PromptBIMTestApp1.xcodeproj \
  -scheme PromptBIMTestApp1 \
  -configuration Debug \
  build 2>&1 | tail -20
```

期望結果: `** BUILD SUCCEEDED **`

### 2.5 Run (Command + R)

```
快捷鍵: ⌘R
```

App 啟動後會自動：
1. 檢查 Python 環境
2. 顯示版本號 (右下角)
3. 載入 Demo Data (v2.9.1 後)

### 2.6 常見建構問題排除

| 問題 | 解法 |
|------|------|
| `No signing certificate` | 選 `Sign to Run Locally` |
| `Module not found` | 確認 Conda 環境已啟動 |
| `.swift 檔案 not in target` | 手動拖入 Xcode → Build Phases → Compile Sources |
| `Python not found` | 設定環境變數 `PROMPTBIM_PYTHON=/path/to/python` |
| `libpromptbim.dylib not found` | 正常，C++ 層是選用的，App 會 fallback 到 Python |

---

## 三、Swift 檔案結構

```
PromptBIMTestApp1/
├── PromptBIMTestApp1App.swift    ← App 入口 + AppDelegate
├── ContentView.swift              ← 主視圖 (Splash + Python 檢查)
├── PythonBridge.swift             ← Python 子程序管理
├── SceneKitView.swift             ← 3D 視圖 (SceneKit)
├── NativeBIMBridge.swift          ← C++ 動態庫橋接
├── BIMSceneBuilder.swift          ← 3D 場景建構器
├── PBResult.swift                 ← 跨層錯誤傳遞型別
└── Info.plist                     ← App 設定 (v2.9.0 / build 22)
```

---

## 四、測試執行

### 4.1 Python Tests (pytest)

```bash
conda activate promptbim
python -m pytest tests/ -x --tb=short -q
```

期望: `820 passed`

### 4.2 C++ Tests (GoogleTest)

```bash
cd libpromptbim/build
ctest --output-on-failure
cd ../..
```

期望: `139 tests passed`

### 4.3 Swift Tests (XCTest)

在 Xcode 中: `⌘U` 或 `Product > Test`

期望: `15+ tests passed`

### 4.4 全部一次跑

```bash
# Python
python -m pytest tests/ -x --tb=short -q

# C++
cd libpromptbim/build && ctest --output-on-failure && cd ../..

# Xcode Build
xcodebuild -project PromptBIMTestApp1.xcodeproj \
  -scheme PromptBIMTestApp1 \
  -configuration Debug \
  build 2>&1 | tail -5
```

---

## 五、Demo Data 使用指南 (v2.9.1+)

> ⚠️ Demo Data 功能在 Sprint P22.1 (v2.9.1) 中開發，以下為規劃的使用流程。

### 5.1 啟動 App 即有展示

App 啟動後自動載入內建範例專案：

| 區域 | 展示內容 |
|------|---------|
| **左側專案樹** | Demo Project (台北信義區 3F 住宅) |
| **2D 地籍 Tab** | 600㎡ L型土地輪廓 + 建築 footprint + 退縮線 |
| **3D 建築 Tab** | 3層住宅 3D 模型 (可旋轉/縮放) |
| **屬性面板** | 面積 330㎡、樓層 3、容積率 1.65、建蔽率 55% |
| **Chat 面板** | 歡迎訊息 + 專案摘要 |

### 5.2 Demo 專案詳情

```
📍 土地: 台北市信義區，600㎡ L型地塊
🏠 建築: 3層住宅
   - 1F: 客廳、廚房、玄關、儲藏室
   - 2F: 主臥、次臥、書房、衛浴
   - 3F: 家庭室、臥室、露台
📐 法規: 住宅區 / 容積率 2.0 / 建蔽率 0.6 / 高度 15m
💰 預算: NT$ 18,500,000
   - 結構: NT$ 11,100,000
   - 裝修: NT$ 4,625,000
   - MEP:  NT$ 2,775,000
✅ 法規檢查: 全通過 (BCR 55% < 60%, FAR 1.65 < 2.0, H 10.5m < 15m)
```

### 5.3 互動操作

**3D 視圖操作：**

| 操作 | 動作 |
|------|------|
| 旋轉 | 左鍵拖曳 |
| 縮放 | 滾輪 / 兩指捏合 |
| 平移 | 右鍵拖曳 / 兩指拖曳 |
| 重置視角 | 雙擊 |

**2D 視圖操作：**

| 操作 | 動作 |
|------|------|
| 縮放 | 滾輪 |
| 平移 | 拖曳 |
| 查看面積 | 滑鼠懸停 |

### 5.4 清除展示 → 開始新專案

```
Menu: File > Clear Demo & Start Fresh
```

或點擊 Toolbar 上的「清除展示」按鈕。

清除後：
1. 所有視圖清空
2. 專案樹重置
3. Chat 顯示: "已清除展示。請匯入土地或輸入描述開始新專案。"
4. 準備好接受你自己的土地資料和建築需求

### 5.5 用 AI 生成新建築

清除展示後，你可以：

**方式 1: 匯入土地 + AI 描述**
1. 拖放 `.geojson` / `.shp` / `.dxf` / `.kml` 到 App
2. 在 Chat 輸入: "在這塊地上蓋一棟 5 層辦公大樓，一樓停車場"
3. AI 自動規劃 + 生成 IFC + USD

**方式 2: 純文字描述**
1. 在 Chat 輸入: "在台北市大安區 500 平方公尺的地上蓋 3 層住宅"
2. AI 自動建立土地 + 規劃建築 + 生成模型

**方式 3: CLI**
```bash
conda activate promptbim
python -m promptbim generate "3-story residential building" \
  --land examples/sample_land.geojson \
  -o ./output
```

### 5.6 匯出檔案

生成完成後，檔案在 `output/` 目錄：

| 檔案 | 說明 |
|------|------|
| `model.ifc` | BIM 完整語義模型 (可用 BIM Viewer 開啟) |
| `model.usda` | OpenUSD 模型 (Digital Twin / AR Preview) |
| `floorplan.svg` | 各層平面圖 |
| `site_plan.svg` | 配置圖 (土地 + 建築) |
| `summary.json` | 數據摘要 (面積/容積率/建蔽率/成本) |

---

## 六、CLI 快速參考

```bash
conda activate promptbim

# 查看版本
python -m promptbim --version

# 啟動 GUI
python -m promptbim gui [--debug]

# AI 生成建築
python -m promptbim generate "描述" -o ./output [--land file.geojson]

# 不用快取重新生成
python -m promptbim generate --no-cache "描述" -o ./output

# 快取管理
python -m promptbim cache list
python -m promptbim cache clear
python -m promptbim cache stats

# 法規檢查
python -m promptbim check [--ai] [--fix] [--json]
```

---

## 七、開發者快速指引

### 7.1 關鍵文件（不可修改）

| 文件 | 說明 |
|------|------|
| `SKILL.md` | 專案 SSOT (27KB, v3.2) |
| `CLAUDE.md` | Claude Code 治理規範 (v1.16.2) |
| `docs/addendum/*.md` | 技術規格附錄 |

### 7.2 Sprint 執行 (Mac Mini)

```bash
ssh michaellin@michaelmac-mini
cd ~/Documents/MyProjects/PromptBIMTestApp1
conda activate promptbim
unset ANTHROPIC_API_KEY
claude --dangerously-skip-permissions -p "請讀取 sprints/PROMPT_P{X}.md 並執行所有 task。不要問任何問題。"
```

### 7.3 備份驗證

```bash
bash scripts/backup_verify.sh
# ✅ CLAUDE.md: ~10KB
# ✅ SKILL.md: 27027 bytes
```

### 7.4 iMessage 通知測試

```bash
osascript -e 'tell application "Messages" to send "🏗️ test" to participant "chchlin1018@icloud.com" of (1st account whose service type = iMessage)'
```

---

## 八、專案當前狀態

```
版本:      v2.9.0 (P22 完成)
測試:      GoogleTest 139 + pytest 820 + XCTest 15+ = 974+
評分:      A- (Senior Audit)
Swift:    7 個檔案
C++:      libpromptbim (IFC + USD + GIS + Compliance + Cost + MEP)
Python:   完整 4-Agent Pipeline (Enhancer → Planner → Builder → Checker)
下一步:    P22.1 (v2.9.1) — 代碼品質 + 測試補齊 + Demo Data
```

---

*BuildSetupAndDemo_0326.md | 2026-03-26 | Reality Matrix Inc.*
*PromptBIM — 用自然語言在真實土地上蓋建築*
