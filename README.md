# PromptBIMTestApp1

## AI 驅動的 BIM 建築模型生成器

> **用自然語言，在真實土地上，自動生成帶 BIM 語義的 3D 建築模型**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-lightgrey.svg)]()

---

## 產品定位

PromptBIMTestApp1 是一個**概念驗證 (POC)** 專案，展示如何用 AI 從自然語言描述自動生成完整的 BIM 建築模型。靈感來自 [Text2BIM](https://github.com/dcy0577/Text2BIM) 學術專案，但**完全不依賴任何商業軟體**。

### 核心能力

1. **土地匯入** — 支援地籍圖 PDF、Shapefile、GeoJSON、KML、DXF、手動座標輸入
2. **AI 建築生成** — 用 Claude API Multi-Agent 架構，在真實土地上規劃合理的建築
3. **雙格式輸出** — IFC（BIM 語義完整）+ OpenUSD（Digital Twin / IDTF 接口）
4. **台灣法規合規** — 自動檢查建蔽率、容積率、耐震、防火、無障礙等法規
5. **MEP 管線自動生成** — 給排水、電力、空調、消防四大系統 3D 路由
6. **施工模擬 (4D)** — 時間軸動畫展示建設過程
7. **成本估算 (5D)** — 自動數量萃取 + 台灣市場單價估算
8. **桌面 3D 互動** — PySide6 + PyVista 桌面 App，即時旋轉/縮放/剖面
9. **語音輸入** — 支援語音描述建築需求
10. **74 種建築零件庫** — 含供應商資訊與參考價格

### 使用場景

```
用戶：「在這塊 300 坪的地上蓋一棟 5 層辦公大樓，一樓停車場」

→ AI 自動生成：
  ✅ 3D BIM 模型 (.ifc + .usda)
  ✅ 各層平面圖 (.svg)
  ✅ 配置圖（土地 + 建築 + 退縮線）
  ✅ MEP 管線（四色 3D）
  ✅ 法規合規報告
  ✅ 施工模擬動畫 (.gif)
  ✅ 成本估算 (¥45.7M ±30%)
```

---

## 技術棧（100% 開源）

| 層次 | 技術 | License |
|------|------|---------|
| Desktop GUI | PySide6 | LGPL-3.0 |
| 3D 視覺化 | PyVista + pyvistaqt | MIT |
| AI | Anthropic Claude API | MIT (SDK) |
| BIM Core | IfcOpenShell 0.8+ | LGPL-3.0 |
| OpenUSD | usd-core (pxr) | Apache-2.0 |
| GIS | geopandas + shapely + pyproj | BSD-3 |
| 幾何 | numpy + trimesh | MIT |
| 2D 繪圖 | matplotlib | BSD |
| 語音 | faster-whisper | MIT |
| MEP Routing | 自建 3D A* Pathfinder | MIT |
| 法規引擎 | 自建 Python Rule Engine | MIT |

**⚠️ 零商業軟體依賴。不需要 Vectorworks、Revit、Navisworks 或任何付費軟體。**

---

## 架構概覽

```
用戶語音/文字 → 匯入土地 GIS → Claude Multi-Agent Pipeline
                                       │
                    ┌──────────────────┤
                    ▼                  ▼
              IFC Generator      USD Generator
             (IfcOpenShell)      (pxr/usd-core)
                    │                  │
                    ├── MEP Auto-Route (A* Pathfinding)
                    ├── 台灣法規檢查 (Rule Engine)
                    ├── 成本估算 (QTO + 單價)
                    └── 施工模擬 (4D Animation)
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              PySide6 Desktop     F3D CLI Render
              (PyVista 3D)        (Offscreen PNG)
```

### Multi-Agent 架構

| Agent | 角色 | 使用 LLM？ |
|-------|------|:----------:|
| **Enhancer** | 理解使用者意圖，補充缺失細節 | ✅ Claude |
| **Planner** | 在土地上規劃建築（含法規約束） | ✅ Claude |
| **Builder** | 從 BuildingPlan JSON 生成 IFC + USD | ❌ 純 Python |
| **Checker** | 法規驗證 + 迭代修正 | ✅ + Rule Engine |
| **MEP Planner** | 決定設備位置，A* 管線路由 | ✅ + Algorithm |
| **Cost Advisor** | 估算成本，提出建議 | ✅ Claude |

---

## 快速開始

### 環境設定

```bash
git clone https://github.com/chchlin1018/PromptBIMTestApp1.git
cd PromptBIMTestApp1

# Python 環境
conda create -n promptbim python=3.11 -y
conda activate promptbim
conda install -c conda-forge ifcopenshell -y

# 安裝依賴
pip install -e ".[dev]"

# 設定 API Key
cp .env.example .env
# 編輯 .env 填入 ANTHROPIC_API_KEY

# 啟動 GUI
python -m promptbim gui
```

### CLI 使用

```bash
# 從文字生成建築
promptbim generate "在 100 坪的地上蓋 3 層住宅"

# 匯入土地 + 生成
promptbim generate --land sample_parcel.geojson "蓋一棟辦公大樓"
```

---

## 文件結構

| 文件 | 說明 |
|------|------|
| `SKILL.md` | Claude Code 知識庫（SSOT） |
| `TODO.md` | 開發計劃與 Sprint 追蹤 |
| `CHANGELOG.md` | 版本變更記錄 |
| `docs/` | 架構文件、法規規則、Agent Prompt 設計 |
| `docs/addendum/` | 零件庫、施工模擬、成本估算、MEP、法規引擎規格 |
| `examples/` | 範例程式碼與測試 prompt |
| `reference/` | 參考資料（GIS 範例、IFC 範例、法規摘錄） |

---

## 授權

MIT License — 詳見 [LICENSE](LICENSE)

---

## 致謝

- [Text2BIM](https://github.com/dcy0577/Text2BIM) — Multi-Agent BIM 生成架構靈感
- [IfcOpenShell](https://ifcopenshell.org/) — IFC 開源工具鏈
- [F3D](https://f3d.app/) — 3D 檢視器
- [OpenUSD](https://openusd.org/) — Pixar 通用場景描述
- [Anthropic Claude](https://anthropic.com/) — AI 引擎
- 內政部全國法規資料庫 — 台灣建築法規
- 國震中心 Sederes — 耐震設計參數

---

*Reality Matrix Inc. / Michael Lin (林志錚) — 2026*
