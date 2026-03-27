# Zigma TSMC Demo 計畫 v1.0

> **版本:** v1.0 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錜）× Claude
> **客戶:** TSMC （已明確表達希望看到）
> **環境:** Windows RTX 4090 + Revit 2026 + Omniverse

---

## TSMC 三大需求

| # | TSMC 要看到的 | Zigma 對應功能 | Demo |
|---|------------|------------|:----:|
| 1 | **Prompt 快速建立建築/廠房** | NL → AI 規劃 → 3D BIM 模型 | D1 |
| 2 | **Prompt 變更設計 → 成本 + 週期** | 變更指令 → 重新規劃 → 即時成本/工期更新 | D1 |
| 3 | **USD → Omniverse 可視化 → Revit 建照** | .usda → Nucleus → Streaming → Connector → Revit → 圖說 | D2 |

---

## Demo 分版策略

### 為什麼分兩版

Demo-1 專注「AI 規劃 + 成本」— 這是 TSMC 最可能當場價值感受最強的部分，且技術風險最可控。Demo-2 加入 Omniverse 全流程— 需要 Nucleus + Streaming + Connector 全部到位，技術複雜度高但解決了 TSMC 的完整工作流需求。

---

# Demo-1: Prompt → BIM → Cost/Schedule

## 一句話價值描述

> **「用一句中文描述廠房需求，3 分鐘後看到完整 BIM 模型 + 建造成本 + 建造週期。說一句『加一間 UPW 處理室』，成本和工期自動更新。」**

## 功能範圍

| # | 功能 | TSMC 看到的 | 技術實現 |
|---|------|------------|--------|
| F1 | **NL → BIM** | 「蓋一座 3F 潔淨室廠房」→ 3D 模型 | Claude Planner + Builder |
| F2 | **即時成本估算** | 總造價 NT$XXM，逐項明細 | Cost Engine (BOM × 單價) |
| F3 | **建造週期估算** | 總工期 XX 週，關鍵路徑 | Schedule Engine (工項依賴) |
| F4 | **Prompt 變更設計** | 「加 UPW 室」→ 模型更新 | Modifier Agent + Re-plan |
| F5 | **成本/工期差異比較** | 變更前後對照表 | Delta Cost/Schedule |
| F6 | **3D 預覽** | 旋轉/樓層切換 | PyVista + Qt |
| F7 | **USD 輸出** | .usda 檔案（含 ilos: metadata） | pxr USD export |

## 展示情境（Demo-1，5 分鐘）

```
0:00  Michael: 「我要在這塊 5000㎡ 的地上蓋一座三層樓的半導體廠務廠房。
        一樓是設備區和裝貨區，二樓是潔淨室，三樓是辦公區。」

0:30  Zigma AI 規劃中...
        → 顯示 AI 分析: 容積率 2.4 | 建蔽率 55% | 高度 14.4m
        → 顯示樓層規劃摘要

1:00  3D 模型生成完成
        → 旋轉展示三層樓結構
        → 切換到各樓層平面圖

1:30  建造成本報告
        → 總造價: NT$ 2.8 億
        → 結構: NT$ 1.2億 | MEP: NT$ 0.8億 | 完工: NT$ 0.8億
        → BOM 明細表

2:00  建造週期報告
        → 總工期: 38 週
        → 關鍵路徑: 基礎(8w) → 結構(12w) → MEP(10w) → 完工(8w)
        → 甘特圖簡化版

2:30  ★ Prompt 變更: 「在二樓加一間 UPW 處理室，含主要配管」
        → AI 重新規劃...
        → 3D 模型更新（UPW 室 + 管路）

3:30  ★ 成本/工期差異報告
        → 成本增加: +NT$ 3,200萬（UPW 設備 + 管路 + 安裝）
        → 工期延長: +3 週（MEP 階段）
        → 變更前/後對照表

4:00  匯出 USD 檔案
        → 顯示 .usda 內容（ilos: metadata）
        → 「這個檔案可以直接進 Omniverse，請看 Demo-2」

4:30  Q&A
```

## Demo-1 開發計畫（4 週，35 Tasks）

### Sprint D1-S1: 核心 AI + 建模（Week 1-2，15T）

#### Part A: 環境 + AI 規劃強化（6T）

| Task | 說明 | 驗收 |
|------|------|------|
| D1-S1-PA-T1 | v2.12 POC 可運行 + pytest pass | Mac CLI 通過 |
| D1-S1-PA-T2 | Planner prompt 針對 FAB 場景優化 | 輸入「半導體廠務廠房」產出合理 JSON |
| D1-S1-PA-T3 | Modifier Agent: 變更指令解析 + 重新規劃 | 「加 UPW 室」可累加處理 |
| D1-S1-PA-T4 | 簡化 layout solver: 區域分割 + 設備放置 | 10+ 設備不重疊 |
| D1-S1-PA-T5 | 簡化配管: 直線 + L型 + 管徑 | 產出含 Pipe Prim |
| D1-S1-PA-T6 | USD 輸出強化: ilos: metadata 完整 | 每個 Prim 有 category/connections |

#### Part B: 成本引擎（4T）

| Task | 說明 | 驗收 |
|------|------|------|
| D1-S1-PB-T7 | 建立台灣營建單價資料庫 (JSON) | 結構/MEP/完工 單價表 |
| D1-S1-PB-T8 | Cost Engine: BOM × 單價 × 係數 | 輸入 BuildingPlan 輸出總價 |
| D1-S1-PB-T9 | 成本報告產生器: 逐項明細 + 總價 | 輸出 CSV + 預覽 |
| D1-S1-PB-T10 | 變更成本差異: 前後對照 | 顯示 +/- NT$ 金額 |

#### Part C: 工期引擎（5T）

| Task | 說明 | 驗收 |
|------|------|------|
| D1-S1-PC-T11 | 建立工項依賴模型 (JSON) | 基礎→結構→MEP→完工 依賴鏈 |
| D1-S1-PC-T12 | Schedule Engine: 工項工期 + 關鍵路徑 | 輸出總週數 + 關鍵路徑 |
| D1-S1-PC-T13 | 甘特圖簡化版產生器 | 輸出 SVG/HTML 甘特圖 |
| D1-S1-PC-T14 | 變更工期差異: 前後對照 | 顯示 +/- 週數 |
| D1-S1-PC-T15 | E2E: NL → BIM → Cost → Schedule 全流程 | CLI 一鍵執行 |

### Sprint D1-S2: GUI + 展示整合（Week 3-4，20T）

#### Part A: GUI 升級（7T）

| Task | 說明 | 驗收 |
|------|------|------|
| D1-S2-PA-T1 | GUI 整合: 土地 → AI Chat → 3D → 報告 一氣呱成 | 不需 CLI |
| D1-S2-PA-T2 | Chat 面板: 多輪對話 + 變更指令 | 「加 UPW 室」即時回應 |
| D1-S2-PA-T3 | 3D 視圖: 樓層切換 + 設備點擊屬性 | 點擊顯示名稱/成本 |
| D1-S2-PA-T4 | 成本面板: 逐項明細 + 圖表 | 圓餅圖/條形圖 |
| D1-S2-PA-T5 | 工期面板: 甘特圖 + 關鍵路徑標紅 | 可視化甘特圖 |
| D1-S2-PA-T6 | 變更對照面板: 前/後並排 | 成本+工期差異高亮 |
| D1-S2-PA-T7 | 匯出面板: USD + 成本報告 + 工期報告 | 單按鈕全部匯出 |

#### Part B: FAB 場景深化（6T）

| Task | 說明 | 驗收 |
|------|------|------|
| D1-S2-PB-T8 | 預設場景: 潔淨室廠房 (ISO Class 1-7) | 選擇後自動填參數 |
| D1-S2-PB-T9 | 預設場景: 廠務設施棟 (泵浦/電力/空調) | 同上 |
| D1-S2-PB-T10 | 預設場景: 辦公大樓 | 同上 |
| D1-S2-PB-T11 | 廠務設備庫: 幫浦/空壓機/冷卻水塔/UPW | 單價+規格 JSON |
| D1-S2-PB-T12 | 台灣建築法規檢查: 容積率/建蔽率/高度 | 超標自動警告 |
| D1-S2-PB-T13 | 消防法規基礎: 退縮/樓梯/防火區劃 | 基本檢查 |

#### Part C: 展示準備（7T）

| Task | 說明 | 驗收 |
|------|------|------|
| D1-S2-PC-T14 | Win RTX 4090 部署 + 測試 | GUI 可運行 |
| D1-S2-PC-T15 | 5 個不同場景 E2E 測試 | 5/5 pass |
| D1-S2-PC-T16 | 效能: NL → BIM+Cost+Schedule < 3 分鐘 | 計時通過 |
| D1-S2-PC-T17 | Demo 腳本撰寫 + 排練 | 5分鐘腳本完成 |
| D1-S2-PC-T18 | 螢幕錄影 (backup 用) | MP4 完成 |
| D1-S2-PC-T19 | TSMC 展示簡報 (8 頁) | Keynote/PPTX |
| D1-S2-PC-T20 | Demo-1 審計報告 + PROJECT.md 更新 | 推送 GitHub |

### Demo-1 成功標準

| 指標 | 及格 | 優秀 |
|------|------|------|
| NL → 3D BIM | 3 分鐘內 | < 1 分鐘 |
| 成本報告 | 逐項明細 + 總價 | 與市場行情偏差 < 20% |
| 工期報告 | 總週數 + 關鍵路徑 | 甘特圖可視化 |
| Prompt 變更 | 可累加變更 | 即時成本/工期差異 |
| USD 輸出 | .usda 含 ilos: | Omniverse 可開啟 |
| TSMC 反應 | 「有趣」 | 「想看 Demo-2」 |

---

# Demo-2: USD → Omniverse → Revit → 建照

## 一句話價值描述

> **「Demo-1 產出的 USD 直接載入 Omniverse 進行 RTX 即時可視化審查，確認後透過 Omniverse Connector 同步到 Revit，一鍵產出建照審核圖說。」**

## 功能範圍

| # | 功能 | TSMC 看到的 | 技術實現 |
|---|------|------------|--------|
| F1 | **USD → Omniverse Nucleus** | 檔案發布到 Nucleus | omni:// publish |
| F2 | **Omniverse 3D 審查** | RTX 即時渲染，在瀏覽器中旋轉 | Kit + Streaming |
| F3 | **協作標註** | 在 3D 場景中加註解 | Omniverse 原生 |
| F4 | **Omniverse → Revit** | 透過 Connector 同步到 Revit | Omniverse Revit Connector |
| F5 | **Revit 建照文件** | 平面圖 + 立面圖 + 剖面圖 | Revit 圖紙產生 |
| F6 | **圖說輸出** | PDF 建照審核圖說 | Revit 列印/PDF |

## 展示情境（Demo-2，7 分鐘，接續 Demo-1）

```
0:00  「Demo-1 產出的 USD 檔案，現在載入 Omniverse。」
       → USD publish 到 Nucleus
       → 顯示 Nucleus 目錄結構

0:30  Omniverse RTX 即時渲染
       → MacBook 瀏覽器開啟 Streaming 網址
       → RTX 即時渲染的 3D 廠房模型
       → 旋轉/縮放/飛行瀏覽

1:30  ★ 在 Omniverse 中標註
       → 點擊 UPW 處理室: 「注意振動隔離」
       → 點擊樓板: 「載重確認 500kg/㎡」
       → 標註可見於所有協作者

2:30  Omniverse → Revit 同步
       → 開啟 Revit + Omniverse Connector
       → 點擊「Sync from Omniverse」
       → Revit 中出現完整 3D 模型
       → 顯示: Level 對應 / Material 正確 / 管路可編輯

4:00  ★ Revit 建照圖說產生
       → 建立圖紙: 各樓平面圖 + 立面圖 + 剖面圖
       → 加入標註: 尺寸 + 室名 + 樓高
       → 加入 Schedule: 門窗表 + 房間表
       → 匯出 PDF 建照審核圖說

5:30  完整流程回顧
       → 「從一句中文到建照圖說，全程 10 分鐘。
          傳統流程需要 2-3 個月。」

6:00  Q&A + 討論下一步
```

## Demo-2 開發計畫（6 週，35 Tasks）

### Sprint D2-S1: Omniverse 整合（Week 5-6，12T）

#### Part A: Omniverse 環境 + Nucleus（6T）

| Task | 說明 | 驗收 |
|------|------|------|
| D2-S1-PA-T1 | Win: Omniverse Nucleus 安裝 + 驗證 | localhost 可存取 |
| D2-S1-PA-T2 | USD publish 到 Nucleus 自動化 | CLI 一鍵 publish |
| D2-S1-PA-T3 | Nucleus 目錄結構規劃 | /Projects/TSMC_Demo/ |
| D2-S1-PA-T4 | Demo-1 USD 載入驗證 | Omniverse 可開啟 + 幾何正確 |
| D2-S1-PA-T5 | ilos: metadata 在 Omniverse 中可見 | Property panel 顯示 metadata |
| D2-S1-PA-T6 | Layer Stack 驗證: 多版本分層 | 變更前/後分層 |

#### Part B: Streaming + 協作（6T）

| Task | 說明 | 驗收 |
|------|------|------|
| D2-S1-PB-T7 | Kit App 啟動 + Pixel Streaming | MacBook 瀏覽器可接收 |
| D2-S1-PB-T8 | Streaming 互動: 旋轉/縮放/平移 | 延遲 < 200ms |
| D2-S1-PB-T9 | 自適應品質設定 | 依頻寬自動調整 |
| D2-S1-PB-T10 | 標註功能: 3D 場景中加註解 | 標註可見於所有協作者 |
| D2-S1-PB-T11 | 截圖/錄影功能 | 即時截圖分享 |
| D2-S1-PB-T12 | Sprint D2-S1 審計 | 推送 GitHub |

### Sprint D2-S2: Revit 同步 + 建照（Week 7-8，12T）

#### Part A: Omniverse → Revit（6T）

| Task | 說明 | 驗收 |
|------|------|------|
| D2-S2-PA-T1 | Revit 2026 + Omniverse Connector 安裝 | Connector 可連線 Nucleus |
| D2-S2-PA-T2 | USD → Revit: 結構體 (DirectShape) | 幾何正確 + Level 對應 |
| D2-S2-PA-T3 | USD → Revit: MEP 管路 (Pipe + Elbow) | 可編輯的 Revit 管路 |
| D2-S2-PA-T4 | Material 對應: OmniPBR → Revit Material | 不再全黑 |
| D2-S2-PA-T5 | SharedParameter 對應: ilos: → Revit | Revit 可查詢 metadata |
| D2-S2-PA-T6 | 同步流程穩定性: 100+ mesh 不崩 | 批次 30 mesh 穩定 |

#### Part B: 建照圖說產生（6T）

| Task | 說明 | 驗收 |
|------|------|------|
| D2-S2-PB-T7 | Revit 圖紙樣板: 各樓平面圖 | 自動建立 |
| D2-S2-PB-T8 | Revit 圖紙樣板: 立面圖 + 剖面圖 | 自動建立 |
| D2-S2-PB-T9 | 標註自動化: 尺寸/室名/樓高 | 主要標註完成 |
| D2-S2-PB-T10 | Schedule 表: 門窗表 + 房間表 | Revit Schedule 可用 |
| D2-S2-PB-T11 | PDF 匯出: 完整建照圖說 | PDF 可列印 |
| D2-S2-PB-T12 | Sprint D2-S2 審計 | 推送 GitHub |

### Sprint D2-S3: 整合測試 + TSMC 展示（Week 9-10，11T）

#### Part A: E2E 整合（5T）

| Task | 說明 | 驗收 |
|------|------|------|
| D2-S3-PA-T1 | 全流程 E2E: NL → BIM → Cost → USD → Omniverse → Revit → PDF | 一氣呱成 |
| D2-S3-PA-T2 | 3 個 FAB 場景 E2E 測試 | 3/3 pass |
| D2-S3-PA-T3 | 效能: 全流程 < 10 分鐘 | 計時通過 |
| D2-S3-PA-T4 | 斷點復原: 任一步驟失敗可重試 | 各步驟獨立 |
| D2-S3-PA-T5 | Streaming 穩定性: 30分鐘不斷線 | 通過 |

#### Part B: TSMC 展示準備（6T）

| Task | 說明 | 驗收 |
|------|------|------|
| D2-S3-PB-T6 | Demo 腳本撰寫: D1+D2 連貫 12 分鐘 | 腳本完成 |
| D2-S3-PB-T7 | 排練 3 次 + 應變準備 | 各種故障場景有 backup |
| D2-S3-PB-T8 | TSMC 專屬簡報: ROI 分析 | 「2週 → 10分鐘」量化 |
| D2-S3-PB-T9 | 螢幕錄影 (backup) | MP4 完成 |
| D2-S3-PB-T10 | TSMC 展示執行 | 完成 |
| D2-S3-PB-T11 | Demo-2 審計 + PROJECT.md + 下一步 | 推送 GitHub |

### Demo-2 成功標準

| 指標 | 及格 | 優秀 |
|------|------|------|
| USD → Omniverse | 可載入 + 旋轉 | RTX Streaming 流暢 |
| Omniverse → Revit | 幾何+管路正確 | Material + Level 正確 |
| 建照圖說 | PDF 可列印 | 平面+立面+剖面+Schedule |
| 全流程時間 | < 15 分鐘 | < 10 分鐘 |
| TSMC 反應 | 「想深入討論」 | 「LOI / Pilot」 |

---

## 總時程

```
Week 1-2:  D1-S1 — AI + 成本引擎 + 工期引擎
           → NL → BIM → Cost → Schedule E2E 打通

Week 3-4:  D1-S2 — GUI + FAB 場景 + 展示
           → Demo-1 展示給 TSMC
           → Gate: TSMC 想看 Demo-2?

Week 5-6:  D2-S1 — Omniverse Nucleus + Streaming
           → USD 在 Omniverse 中可視化

Week 7-8:  D2-S2 — Omniverse → Revit + 建照圖說
           → 全流程打通

Week 9-10: D2-S3 — 整合測試 + TSMC 展示
           → Demo-2 展示給 TSMC
           → Gate: LOI / Pilot?
```

---

## 技術架構注意事項

### 全流程數據流

```
NL Prompt
  │ Claude Planner
  ▼
BuildingPlan (JSON)
  │ Builder + Cost Engine + Schedule Engine
  ▼
USD (.usda) + CostReport + ScheduleReport
  │ ilos: metadata embedded
  ▼
Omniverse Nucleus (omni://)
  │ Kit + Pixel Streaming
  ▼
Omniverse Revit Connector
  │ Sync to Revit
  ▼
Revit Project (.rvt)
  │ 圖紙 + 標註 + Schedule
  ▼
PDF 建照圖說
```

### 關鍵技術風險

| 風險 | 影響 | 機率 | 緩解 |
|------|------|------|------|
| Omniverse Connector → Revit 不穩定 | D2 全部 | 中 | Week 5 早期驗證，fallback 為手動 import |
| Streaming 延遲高 | D2 體驗差 | 低 | 內網環境，RTX 4090 強制力夠 |
| 成本估算偏差太大 | D1 可信度 | 中 | 用台灣營建實際行情校準，標註「估算值」 |
| Revit 圖紙自動化不夠完整 | D2 過程繁瑣 | 中 | 樣板預建 + 手動補完 |
| AI 規劃品質不夠 | D1 核心 | 低中 | 預設場景範本 + 提示引導 |

### Omniverse Revit Connector 依賴

Demo-2 依賴 NVIDIA Omniverse Connector for Revit。如果版本不相容：
- **Plan A:** Omniverse Connector (NVIDIA 官方) — 優先
- **Plan B:** 直接 USD → Revit MCP (POC 已驗證的 DirectShape 路徑) — 跳過 Omniverse
- **Plan C:** Omniverse 可視化 + 手動 Revit import — 最保守

### 成本引擎設計

```python
class CostEngine:
    """基於 BOM 的建造成本估算"""
    
    def estimate(self, plan: BuildingPlan) -> CostReport:
        """
        1. 從 BuildingPlan 提取 BOM (結構/MEP/完工)
        2. BOM × 台灣單價資料庫
        3. × 區域係數 × 廠房結構係數
        4. 輸出: 總價 + 逐項明細 + 圖表
        """
    
    def compare(self, before: CostReport, after: CostReport) -> CostDelta:
        """變更前後成本差異報告"""
```

### 工期引擎設計

```python
class ScheduleEngine:
    """基於工項依賴的建造週期估算"""
    
    def estimate(self, plan: BuildingPlan, cost: CostReport) -> ScheduleReport:
        """
        1. 從 BuildingPlan 提取工項清單
        2. 建立依賴關係 (基礎→結構→MEP→完工)
        3. 計算關鍵路徑
        4. 輸出: 總週數 + 甘特圖 + 關鍵路徑
        """
    
    def compare(self, before: ScheduleReport, after: ScheduleReport) -> ScheduleDelta:
        """變更前後工期差異報告"""
```

---

## 參考文件

- Architecture: `docs/architecture/PromptToBuild_Platform_Architecture_v2.1.md`
- Partner Spec: `docs/architecture/PromptToBuild_Partner_Interface_Spec_v1.0.md`
- ILOS Constraints: SKILL.md §ILOS-FAB 技術約束
- 台灣建築法規: `docs/addendum/03_tw_building_codes.md`
- 成本估算: `docs/addendum/02_sim_cost_mep.md`

---

*Zigma TSMC Demo 計畫 v1.0*
*Reality Matrix Inc. | 2026-03-27*
*核心原則: TSMC 已明確表達需求 — 每一行代碼都爲了這場 Demo*
