# Zigma TSMC Demo-1 計畫 v1.1

> **版本:** v1.1 | **日期:** 2026-03-27
> **更新:** 根據 Michael 確認的 TSMC Demo-1 Mandatory/Nice-to-Have 重新設計
> **取代:** v1.0 的 Demo-1 部分（Demo-2 不變）

---

## TSMC Demo-1 需求確認

### Mandatory Features

| # | 需求 | 說明 | 技術對應 |
|---|------|------|--------|
| M1 | **文字 Prompt 描述** | Claude AI 處理語意分析 → BIM Engine | Claude Planner + Enhancer |
| M2 | **3D BIM 模型可視化** | Windows RTX 4090 / OpenGL/DirectX | VTK OpenGL / Hydra Storm |
| M3 | **成本 + 工期 + 4D + 變更再設計** | 產出 Cost, Schedule, 4D，變更後即時更新 | Cost Engine + Schedule Engine + 4D Player |
| M4 | **即時變更展示** | 「蓋別墅帶泳池」→「泳池移除改停車場」→ 立刻看到變更設計 + 成本 + Schedule | Modifier Agent + Delta Report |
| M5 | **4D 建造過程模擬** | 建造過程隨時間推進的動畫 | 4D Timeline Player |
| M6 | **供應商零件庫** | 設備/建材/配件 + 單價 + 規格 | Asset Library + Pricing DB |

### Nice to Have

| # | 需求 | 說明 | 技術對應 |
|---|------|------|--------|
| N1 | **語音輸入** | 語音轉文字 → Prompt | Whisper API / 系統 STT |

---

## 一句話價值描述

> **「幫我產出一個 3 層樓別墅帶泳池」 — 3 分鐘後看到 3D 模型、建造成本、建造週期、和一步一步蓋好的 4D 動畫。說一句「泳池移除改成停車場」，全部自動更新。」**

---

## 展示情境腳本ﾈ6 分鐘）

```
0:00  Michael: 「幫我產出一個 3 層樓別墅帶泳池」
       → Claude AI 分析語意...
       → 顯示規劃摘要: 3F / 建地 300㎡ / 泳池 15m×6m

0:40  ★ 3D BIM 模型生成 (RTX 4090 渲染)
       → 即時 3D 旋轉展示（OpenGL/DirectX）
       → 切換樓層：1F 客廳+泳池 / 2F 臥室 / 3F 書房
       → 點擊泳池: 顯示供應商零件——磁磚、循環系統、排水

1:20  ★ 成本報告
       → 總造價: NT$ 2,800萬
       → 結構: NT$ 1,200萬 | 完工: NT$ 800萬 | 泳池: NT$ 350萬 | MEP: NT$ 450萬
       → 供應商明細: 鐘山鐘磚 (磁磚) / 大金剛石 (結構) / ...

1:50  ★ 建造週期報告 + 甘特圖
       → 總工期: 32 週
       → 關鍵路徑: 基礎(6w) → 結構(10w) → MEP(8w) → 完工(8w)

2:20  ★★ 4D 建造模擬（精彩時刻）
       → Timeline 撥動梡:
         Week 0:  空地
         Week 6:  基礎完成（地基出現）
         Week 16: 結構完成（三層樓站起來）
         Week 20: 泳池完成（藍色水池出現）
         Week 24: MEP 完成（管路可見）
         Week 32: 全部完工（外觀+內裝）
       → 播放/暫停/拖動 Timeline

3:30  ★★ Prompt 變更: 「泳池移除，改成停車場」
       → AI 重新規劃...
       → 3D 模型即時更新（泳池消失，停車場出現）
       → 供應商零件更新（移除磁磚/循環，加入地坡/防滑地磚）

4:10  ★★ 變更對照報告
       → 成本差異: -NT$ 350萬 (泳池) + NT$ 180萬 (停車場) = 淨省 NT$ 170萬
       → 工期差異: -3 週 (泳池工程移除)
       → 4D 建造模擬自動更新（停車場階段替代泳池階段）

5:00  ★ 供應商零件庫展示
       → 瀏覽零件庫: 結構/MEP/完工/廠務
       → 點擊零件: 顯示規格 + 供應商 + 單價
       → 拖拉替換: 換一種磁磚 → 成本自動更新

5:30  Q&A + 「接下來看 Demo-2: 這個模型如何進入 Omniverse 再輸出建照」
```

---

## vs v1.0 的關鍵變化

| 項目 | v1.0 | v1.1 | 原因 |
|------|------|------|------|
| **4D 建造模擬** | 無 | ★ Mandatory | TSMC 明確要求 |
| **3D 渲染** | PyVista | RTX OpenGL/DirectX | 展示品質需求 |
| **供應商零件庫** | 基本版 | ★ Mandatory 完整版 | TSMC 明確要求 |
| **展示場景** | 半導體廠房 | 別墅+泳池 (更直觀) | Demo 效果更好 |
| **語音輸入** | 無 | Nice-to-Have | 加分項 |
| **甘特圖** | 簡化版 | 包含在 4D 中 | 整合升級 |

---

## 技術架構

### 4D 建造模擬原理

```
Schedule Engine 產出工項清單:
  Phase 1: 基礎 (Week 0-6)   → USD Prim: /Foundation/*
  Phase 2: 結構 (Week 6-16)  → USD Prim: /Structure/*
  Phase 3: 泳池 (Week 10-20) → USD Prim: /Pool/*
  Phase 4: MEP  (Week 16-24) → USD Prim: /MEP/*
  Phase 5: 完工 (Week 24-32) → USD Prim: /Finish/*

4D Player:
  │ 讀取 ScheduleReport.phases[]
  │ 每個 phase 對應 USD Prim 路徑
  │ Timeline slider 控制 Prim visibility
  │ Week N → 顯示所有 end_week ≤ N 的 Prim
  ▼
  3D 視圖即時更新
```

### 3D 渲染升級路徑

```
現狀: PyVista (VTK OpenGL)
  │ 已經支援 OpenGL，在 RTX 4090 上效能足夠
  │ PyVista BackgroundPlotter + pyvistaqt 整合 PySide6
  │ 可以控制 mesh visibility (用於 4D)
  ▼
Demo-1 方案: PyVista + RTX 4090 OpenGL
  │ 不需要換 Hydra Storm
  │ VTK 在 RTX 4090 上已經可以渲染數千 mesh
  │ PyVista actor.SetVisibility() 用於 4D 控制
  ▼
未來 Phase 2+: Hydra Storm (真正 RTX ray-tracing)
```

### 供應商零件庫架構

```python
class AssetLibrary:
    """供應商零件庫系統"""
    
    categories = [
        "structure",    # 結構: 鋼筋/混凝土/鋼骨
        "mep",          # 機電: 管路/電線/空調
        "finish",       # 完工: 磁磚/油漆/地板
        "equipment",    # 設備: 幫浦/空壓機/冷卻塔
        "landscape",    # 景觀: 泳池/停車場/園藝
    ]
    
    class Part:
        name: str           # 「意大利白色拋光石英磚」
        supplier: str       # 「鐘山鐘磚」
        unit_price: float   # NT$ 1,200/㎡
        spec: dict          # {"size": "60x60cm", "material": "porcelain"}
        usd_prim_path: str  # 對應的 USD Prim
    
    def search(self, category, keyword) -> list[Part]: ...
    def get_alternatives(self, part) -> list[Part]: ...
    def swap(self, old_part, new_part) -> CostDelta: ...
```

---

## 更新後的 Demo-1 開發計畫ﾈ4 週，42 Tasks）

### Sprint D1-S1: AI + Cost + Schedule + 4D 核心 (Week 1-2, 20T)

#### Part A: AI 規劃強化 (6T)

| ID | 說明 | 對應需求 | 驗收 |
|----|------|--------|------|
| D1-S1-PA-T1 | v2.12 POC 可運行 + pytest pass | 基線 | CLI 通過 |
| D1-S1-PA-T2 | Planner prompt 別墅/FAB 場景優化 | M1 | 「3層別墅帶泳池」產出合理 JSON |
| D1-S1-PA-T3 | Modifier Agent: 變更指令 + 重新規劃 | M4 | 「泳池移除改停車場」可累加 |
| D1-S1-PA-T4 | 簡化 layout solver: 區域 + 設備 + 間距 | M1 | 10+ 區域不重疊 |
| D1-S1-PA-T5 | 簡化配管: 直線 + L型 + 管徑 | M1 | Pipe Prim |
| D1-S1-PA-T6 | USD 輸出: ilos: metadata + phase tag | M5 | Prim 包含 phase 標註 |

#### Part B: 成本引擎 + 供應商零件庫 (6T)

| ID | 說明 | 對應需求 | 驗收 |
|----|------|--------|------|
| D1-S1-PB-T7 | 供應商零件庫: 5 大類×20+ 零件 | M6 | JSON + 單價 + 規格 |
| D1-S1-PB-T8 | 零件庫搜尋 + 替代品推薦 | M6 | 搜「磁磚」回傳替代品+價差 |
| D1-S1-PB-T9 | Cost Engine: BOM × 零件庫單價 × 係數 | M3 | 輸出總價+明細 |
| D1-S1-PB-T10 | 成本報告: 逐項 + 供應商明細 + 圖表 | M3 | CSV + 預覽 |
| D1-S1-PB-T11 | 零件替換 → 成本即時更新 | M6+M3 | 換磁磚→價格變 |
| D1-S1-PB-T12 | 變更成本差異: 前後對照 | M4 | +/- NT$ |

#### Part C: 工期引擎 + 4D 核心 (8T)

| ID | 說明 | 對應需求 | 驗收 |
|----|------|--------|------|
| D1-S1-PC-T13 | 工項依賴模型: 基礎→結構→MEP→完工 | M3 | JSON 依賴鏈 |
| D1-S1-PC-T14 | Schedule Engine: 工期 + 關鍵路徑 | M3 | 總週+關鍵路徑 |
| D1-S1-PC-T15 | 甘特圖產生器 (HTML/SVG) | M3 | 可視化 |
| D1-S1-PC-T16 | 變更工期差異: 前後對照 | M4 | +/- 週數 |
| D1-S1-PC-T17 | **4D Phase Mapper: Schedule 工項 → USD Prim 對應** | M5 | 每個 phase 對應 Prim 路徑 |
| D1-S1-PC-T18 | **4D Visibility Engine: Week N → 顯示對應 Prim** | M5 | 設定 week=16 顯示基礎+結構 |
| D1-S1-PC-T19 | **4D 變更連動: 設計變更後 4D 自動更新** | M5+M4 | 移除泳池␂4D無泳池階段 |
| D1-S1-PC-T20 | E2E: NL → BIM → Cost → Schedule → 4D | M1-M5 | CLI 全流程 |

### Sprint D1-S2: GUI + 4D Player + 展示 (Week 3-4, 22T)

#### Part A: GUI + 3D + 4D Player (9T)

| ID | 說明 | 對應需求 | 驗收 |
|----|------|--------|------|
| D1-S2-PA-T1 | Win RTX 4090 部署 + PyVista OpenGL | M2 | GPU 加速確認 |
| D1-S2-PA-T2 | GUI 整合: Prompt→AI→3D→報告 一氣呱成 | M1 | 不需 CLI |
| D1-S2-PA-T3 | Chat 面板: 多輪對話 + 變更指令 | M4 | 即時回應 |
| D1-S2-PA-T4 | 3D 視圖: 樓層切換 + 點擊顯示零件資訊 | M2+M6 | 點擊顯示供應商+單價 |
| D1-S2-PA-T5 | **4D Timeline Player: 播放/暫停/Slider** | M5 | 拖動 slider 看建造過程 |
| D1-S2-PA-T6 | **4D 動畫: mesh 淨現/淨出過渡** | M5 | 平滑過渡不是突然出現 |
| D1-S2-PA-T7 | 成本面板: 明細 + 圖表 + 供應商 | M3+M6 | 圓餅/條形圖 |
| D1-S2-PA-T8 | 工期面板: 甘特圖 + 關鍵路徑 + 4D 聯動 | M3+M5 | 點擊甘特圖→跳到 4D 對應週 |
| D1-S2-PA-T9 | 變更對照面板: 前/後 + 成本 + 工期 + 4D | M4 | 一頁看完所有差異 |

#### Part B: 場景 + 零件庫 GUI (6T)

| ID | 說明 | 對應需求 | 驗收 |
|----|------|--------|------|
| D1-S2-PB-T10 | 預設場景: 3層別墅+泳池 | M4 | 選擇後自動填 |
| D1-S2-PB-T11 | 預設場景: 半導體廠務廠房 | — | 同上 |
| D1-S2-PB-T12 | 預設場景: 辦公大樓 | — | 同上 |
| D1-S2-PB-T13 | 零件庫瀏覽器: 分類 + 搜尋 + 競合 | M6 | GUI 可用 |
| D1-S2-PB-T14 | 台灣法規檢查: 容積/建蔽/高度 | M1 | 超標警告 |
| D1-S2-PB-T15 | 匯出面板: USD + 成本 + 工期 + BOM | M3 | 單按鈕 |

#### Part C: 展示準備 + Nice-to-Have (7T)

| ID | 說明 | 對應需求 | 驗收 |
|----|------|--------|------|
| D1-S2-PC-T16 | 5 場景 E2E 測試 (別墅/廠房/辦公) | M1-M6 | 5/5 pass |
| D1-S2-PC-T17 | 效能: NL → 3D+Cost+Schedule+4D < 3min | M1-M5 | 計時通過 |
| D1-S2-PC-T18 | Demo 腳本 (6分鐘) + 排練 | 展示 | 腳本完成 |
| D1-S2-PC-T19 | 螢幕錄影 (backup) | 展示 | MP4 |
| D1-S2-PC-T20 | TSMC 展示簡報 (8頁) | 展示 | PPTX |
| D1-S2-PC-T21 | *Nice-to-Have: 語音輸入 (Whisper/系統STT)* | N1 | 語音→文字→Prompt |
| D1-S2-PC-T22 | Demo-1 審計 + PROJECT.md | 治理 | GitHub |

---

## Demo-1 成功標準 (v1.1)

| 指標 | 及格 | 優秀 |
|------|------|------|
| NL → 3D BIM | 3 分鐘 | < 1 分鐘 |
| 3D 渲染 | RTX OpenGL 流暢 | 60fps |
| 成本報告 | 逐項+總價+供應商 | 偏差 < 20% |
| 工期報告 | 總週+關鍵路徑+甘特圖 | 可互動 |
| **4D 建造模擬** | **Timeline 可播放** | **平滑動畫+拖動** |
| **供應商零件庫** | **可瀏覽+搜尋** | **替換→成本即時更新** |
| Prompt 變更 | 可累加 | 即時 3D+Cost+Schedule+4D 全部更新 |
| 語音輸入 | — | 可用 (Nice-to-Have) |
| TSMC 反應 | 「有趣」 | 「想看 Demo-2」 |

---

## 任務統計 (v1.1 vs v1.0)

| | v1.0 Demo-1 | v1.1 Demo-1 | 差異 |
|---|---|---|---|
| 總 Tasks | 35 | 42 | +7 |
| 新增模組 | Cost+Schedule | +4D Player +零件庫完整版 +語音 | 3 個模組 |
| 週數 | 4 | 4 | 不變 |
| Demo 時長 | 5 min | 6 min | +1 min (4D 展示) |

---

## Demo-2 不變

Demo-2 (USD → Omniverse → Revit → 建照) 維持 v1.0 計畫不變，35 Tasks，Week 5-10。

---

*Zigma TSMC Demo Plan v1.1 | 2026-03-27*
*更新: +4D 建造模擬 + 供應商零件庫完整版 + 語音 Nice-to-Have*
