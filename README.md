# PromptBIMTestApp1

## AI 驅動的 BIM 建築模型自動生成器

> **用自然語言 + 土地資料，一鍵自動完成建築設計、BIM 模型、MEP 管線、法規檢查、施工模擬、成本估算、監控點配置**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)]()
[![Tests](https://img.shields.io/badge/Tests-675%20passed-green.svg)]()
[![POC](https://img.shields.io/badge/Stage-POC%20v1.4.0-orange.svg)]()

---

## 產品定位

PromptBIMTestApp1 是一個**概念驗證 (POC)** 專案。

**使用者只需要做兩件事：**
1. 輸入土地資料（面積/GeoJSON/或任意圖片）
2. 輸入一句 AI Prompt

**系統自動完成所有後續工作。**

---

## 快速開始

### 安裝

```bash
git clone https://github.com/chchlin1018/PromptBIMTestApp1.git
cd PromptBIMTestApp1
conda create -n promptbim python=3.11 -y
conda activate promptbim
conda install -c conda-forge ifcopenshell -y
pip install PySide6 pyvista pyvistaqt anthropic pydantic python-dotenv usd-core geopandas shapely fiona pyproj ezdxf numpy trimesh matplotlib Pillow
```

### 設定 Claude AI API Key

```bash
cp .env.example .env
nano .env
# 填入: ANTHROPIC_API_KEY=sk-ant-api03-你的Key
```

取得 Key → [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

### 啟動 App

```bash
conda activate promptbim
python -m promptbim gui              # GUI 模式
python -m promptbim gui --debug      # Debug 模式（詳細 log）
python -m promptbim check            # 環境健康檢查
python -m promptbim check --ai       # 只檢查 Claude AI 連線
```

### Xcode 開啟 (推薦)

```bash
open PromptBIMTestApp1.xcodeproj     # Scheme: PromptBIMTestApp1, Destination: My Mac
# Cmd+R → 自動啟動 PySide6 完整功能 GUI
# SwiftUI 窗口顯示啟動狀態 + Python 環境檢查
```

### 其他啟動方式

```bash
streamlit run src/promptbim/web/app.py    # Web UI
python -m promptbim.mcp.server            # MCP Server (Claude Desktop)
```

詳細安裝步驟見 **[SETUP.md](SETUP.md)**

---

## Prompt 範例

| Prompt | 系統自動處理 |
|--------|------------|
| `帶游泳池的3層別墅` | 含泳池的住宅平面、RC結構、泳池循環水系統 |
| `12層住宅大樓` | 每層4戶標準戶型、2部電梯+緊急梯、完整消防 |
| `100MW 數據中心` | 伺服器大廳冷熱通道、UPS+柴油發電機、氣體滅火 |
| `「請修改 12 樓層改為 9 個樓層」` | 面積-25%, 成本-25%, 工期-120天, 全部關聯數據即時更新 |

---

## 核心功能

| 功能 | 說明 |
|------|------|
| 🗺️ **土地匯入** | GeoJSON / Shapefile / DXF / KML / 手動 / **AI 圖像辨識** |
| 🧠 **AI 建築生成** | Claude Multi-Agent：Enhancer → Planner → Builder → Checker |
| 📐 **雙格式 BIM** | IFC（IfcOpenShell）+ OpenUSD（pxr）+ USDZ |
| 🔄 **即時互動修改** | 自然語言修改指令 → 增量更新所有關聯數據 |
| 📏 **台灣法規** | 建蔽率/容積率/高度/耐震/防火/無障礙 15+ 條 |
| 🔧 **MEP 自動路由** | 給排水🟦 / 電力🟥 / 空調🟢 / 消防🟡 3D A* |
| 🏗️ **施工模擬 (4D)** | 16 階段動畫 + 甘特圖 + GIF |
| 💰 **成本估算 (5D)** | 自動 QTO + 台灣市場單價 |
| 📡 **智慧監控點** | 48 種 M&C 點自動配置 + IDTF 對接 |
| 📦 **USDZ** | Apple Vision Pro / Quick Look |
| 🔌 **MCP Server** | Claude Desktop 整合 |
| 🌐 **Web UI** | Streamlit 瀏覽器介面 |

---

## 開發進度

| Sprint | 狀態 | 測試 | 說明 |
|--------|:----:|------:|------|
| P0 骨架 | ✅ | 29 | Xcode + Python skeleton |
| P1 土地匯入 | ✅ | 48 | GeoJSON/SHP/DXF parsers |
| P2 IFC+USD | ✅ | 82 | 雙格式 BIM 生成 |
| P2.5 零件庫 | ✅ | 108 | 76 種零件 + 供應商 |
| P3 3D 預覽 | ✅ | 127 | PyVista + 樓層切換 |
| P4 AI Agent | ✅ | 164 | 4 Agent Pipeline |
| P4.5 法規 | ✅ | 211 | 15+ 條台灣法規 |
| P4.8 修改 | ✅ | 235 | 即時修改引擎 |
| P5 語音+匯出 | ✅ | 265 | STT + 一鍵匯出 |
| P6 成本 5D | ✅ | 293 | QTO + 台灣單價 |
| P7 MEP | ✅ | 338 | A* 路由 + 碰撞偵測 |
| P8 施工 4D | ✅ | 388 | 16階段動畫 + GIF |
| P8.5 監控點 | ✅ | 440 | 48 種 + IDTF |
| P9 AI圖像+Backlog | ✅ | 516 | Vision + USDZ + MCP + Web |
| P10.2 Debug Log | 🔄 | — | 全模組 Debug Logging |
| P10.3 啟動檢查 | 🔄 | — | 環境 + Claude AI 驗證 |

---

## 技術栈（100% 開源）

| 層次 | 技術 |
|------|------|
| Desktop GUI | PySide6 |
| 3D | PyVista + pyvistaqt |
| AI | Anthropic Claude API |
| BIM | IfcOpenShell + usd-core (pxr) |
| GIS | geopandas + shapely + pyproj |
| MEP | 自建 3D A* Pathfinder |
| 法規 | 自建 Python Rule Engine |
| Web | Streamlit |
| MCP | FastMCP |

---

## 文件結構

| 文件 | 說明 |
|------|------|
| [SETUP.md](SETUP.md) | 安裝測試指南（含 API Key 設定、Xcode 開啟） |
| [SKILL.md](SKILL.md) | Claude Code 知識庫 (SSOT) |
| [TODO.md](TODO.md) | Sprint 進度追蹤 |
| [CHANGELOG.md](CHANGELOG.md) | 版本變更記錄 |
| [CLAUDE.md](CLAUDE.md) | Claude Code 行為規範 |
| [docs/reviews/](docs/reviews/) | Code Review 報告 |
| [docs/reports/](docs/reports/) | 完成報告 |

---

## 授權

MIT License — 詳見 [LICENSE](LICENSE)

---

*Reality Matrix Inc. / Michael Lin (林志鍾) — 2026*
