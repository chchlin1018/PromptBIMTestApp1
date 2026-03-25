# PromptBIMTestApp1

## AI 驅動的 BIM 建築模型自動生成器

> **用自然語言 + 土地資料，一鍵自動完成建築設計、BIM 模型、MEP 管線、法規檢查、施工模擬、成本估算、監控點配置**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)]()
[![POC](https://img.shields.io/badge/Stage-POC-orange.svg)]()

---

## 產品定位

PromptBIMTestApp1 是一個**概念驗證 (POC)** 專案。

**使用者只需要做兩件事：**
1. 輸入土地資料（面積/GeoJSON/或隨意描述）
2. 輸入一句 AI Prompt

**系統自動完成所有後續工作** — AI 搜尋資料、下載免費模型、設計建築、生成 BIM、配置管線、檢查法規、模擬施工、估算成本。

---

## 使用場景與 Prompt 範例

### 🏠 住宅類

| Prompt | 系統自動產生 |
|--------|------------|
| `帶游泳池的3層別墅` | 含泳池的住宅平面、RC結構、泳池循環水系統、庭院景觀 |
| `12層住宅大樓` | 每層4戶標準戶型、2部電梯+緊急梯、地下停車場、完整消防系統 |
| `4層透天厝，一樓車庫` | 車庫+客廳→主臥+次臥→書房+陽台、鋼筋混凝土結構 |
| `雙拼別墅，每戶3房` | 對稱配置、各戶獨立入口、共用車道 |

### 🏢 商業/辦公類

| Prompt | 系統自動產生 |
|--------|------------|
| `帶地下停車場的商辦大樓` | 地上8層+地下3層、帷幕牆、中央空調、獨立配電、消防排煙 |
| `5層辦公樓，頂樓員工餐廳` | 開放辦公區+會議室、頂樓廚房MEP、員工休憩露台 |
| `共享辦公空間` | 彈性隔間、大量插座、會議艙、咖啡吧檯區 |

### 🏭 工業類

| Prompt | 系統自動產生 |
|--------|------------|
| `3層樓標準工廠廠房` | 大跨距鋼構(15m+)、貨梯2部、工業通風、三相電力配置 |
| `100MW 數據中心` | 伺服器大廳冷熱通道、冷水機組+冷卻塔、UPS+柴油發電機、氣體滅火、門禁系統 |
| `冷凍倉儲物流中心` | 低溫區劃、月台+卸貨區、冷鏈溫控系統 |

### 🏥 公共建築類

| Prompt | 系統自動產生 |
|--------|------------|
| `200床地區醫院` | 急診/門診/手術/病房分層、醫療氣體管路、特殊排水、直升機停機坪 |
| `鄰近學校的社區活動中心` | 多功能廳(200人)、教室、圖書室、完整無障礙設施、太陽能板 |
| `消防局` | 車庫(消防車)、值班室、訓練塔、緊急出動動線 |

### 🔄 互動修改場景

| 初始生成後的修改指令 | 系統即時反應 |
|---------------------|------------|
| `「請修改 12 樓層改為 9 個樓層」` | 面積-25%, 成本-25%, 工期-120天, 高度從超限變合規, 監控點156→117個 |
| `「一樓改為商場, 加設電扶梯」` | 1F平面重配、電扶梯×2加入、消防升級（商場標準）、成本+¥12M |
| `「改用鋼構」` | 結構全部重算、成本變化、工期可能縮短、柱斷面改變 |
| `「加一層地下停車場」` | 基礎加深、車道坡道、排煙系統、汙水處理、成本+15% |
| `「頂樓改為露台」` | 屋頂結構調整、容積率重算、防水處理 |
| `「撤銷上一步」` | 恢復到前一版本，所有數據回復 |

### 📊 自動產生的完整輸出

每次生成（含修改後），系統自動產生：

```
output/
├── model.ifc              ← BIM 模型（含 MEP + 監控點 IfcSensor）
├── model.usda             ← OpenUSD（含 monitor: namespace → IDTF 對接）
├── floorplan_*.svg        ← 各層平面圖
├── site_plan.svg          ← 配置圖（土地+建築+退縮線）
├── mep_overlay.png        ← MEP 四色管線 3D 視圖
├── construction_anim.gif  ← 施工模擬動畫 (4D)
├── gantt_chart.svg        ← 施工甘特圖
├── cost_estimate.csv      ← 成本估算明細 (5D)
├── cost_summary.json      ← 成本摘要（總價 + 分項比例）
├── compliance_report.json ← 台灣法規合規報告（15+ 條）
├── monitor_dashboard.json ← 智慧監控點清單（48種 M&C 點）
├── modification_history.json ← 版本修改歷史 + 差異比較
└── summary.json           ← 建築參數總表
```

---

## 核心功能

| 功能 | 說明 |
|------|------|
| 🗺️ **土地匯入** | GeoJSON / Shapefile / DXF / KML / 手動座標 / 隨意描述面積 |
| 🧠 **AI 建築生成** | Claude Multi-Agent：Enhancer → Planner → Builder → Checker |
| 📐 **雙格式 BIM** | IFC（IfcOpenShell）+ OpenUSD（pxr）同步輸出 |
| 🔄 **即時互動修改** | 自然語言修改指令 → 增量更新所有關聯數據 |
| 📏 **台灣法規** | 建蔽率/容積率/高度/耐震/防火/無障礙 15+ 條自動檢查 |
| 🔧 **MEP 自動路由** | 給排水🔵 / 電力🔴 / 空調🟢 / 消防🟡 3D A* Pathfinding |
| 🏗️ **施工模擬 (4D)** | 16 階段施工順序動畫 + 甘特圖 |
| 💰 **成本估算 (5D)** | 自動 QTO + 台灣市場單價 → 分項報表 |
| 📡 **智慧監控點** | 48 種 M&C 點自動配置（HVAC/電力/消防/結構/安全） |
| 🗣️ **語音輸入** | 按住說話 → faster-whisper 本地辨識 |
| 🧩 **零件庫** | 74 種建築零件 + IFC 映射 + 供應商 + 台灣市場價格 |

---

## 技術棧（100% 開源，零商業軟體依賴）

| 層次 | 技術 | License |
|------|------|---------|
| Desktop GUI | PySide6 | LGPL-3.0 |
| 3D 視覺化 | PyVista + pyvistaqt | MIT |
| AI | Anthropic Claude API | MIT (SDK) |
| BIM Core | IfcOpenShell 0.8+ | LGPL-3.0 |
| OpenUSD | usd-core (pxr) | Apache-2.0 |
| GIS | geopandas + shapely + pyproj | BSD-3 |
| MEP Routing | 自建 3D A* Pathfinder | MIT |
| 法規引擎 | 自建 Python Rule Engine | MIT |
| 監控點 | 自建 Auto-Placement Engine | MIT |

---

## 快速開始

詳見 **[SETUP.md](SETUP.md)** — macOS 完整安裝測試指南。

```bash
git clone https://github.com/chchlin1018/PromptBIMTestApp1.git
cd PromptBIMTestApp1
# 詳細步驟見 SETUP.md
```

---

## 文件結構

| 文件 | 說明 | 誰維護 |
|------|------|--------|
| `README.md` | 專案介紹（本文件） | 人工 |
| `SETUP.md` | 安裝測試指南 | Claude Code |
| `SKILL.md` | Claude Code 知識庫（SSOT） | 人工 |
| `TODO.md` | Sprint 追蹤 | Claude Code |
| `CHANGELOG.md` | 版本變更記錄 | Claude Code |
| `CLAUDE.md` | Claude Code 行為規範 | 人工 |
| `PROMPT.md` | Claude Code 執行指令檔 | 人工 |
| `docs/addendum/01` | 零件庫規格 | 人工 |
| `docs/addendum/02` | 施工/成本/MEP 規格 | 人工 |
| `docs/addendum/03` | 台灣法規引擎規格 | 人工 |
| `docs/addendum/04` | 互動修改 + 監控點規格 | 人工 |

---

## 授權

MIT License — 詳見 [LICENSE](LICENSE)

---

*Reality Matrix Inc. / Michael Lin (林志錚) — 2026*
