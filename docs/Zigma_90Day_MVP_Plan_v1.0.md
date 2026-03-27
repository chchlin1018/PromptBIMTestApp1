# Zigma 90 天聚焦執行計畫

> **版本:** v1.0 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錜）× Claude（戰略評估 Session）
> **核心原則:** 先證明有人要，再建得完美
> **取代:** Dev Plan v1.1 中的 Phase 0 + Phase 0.5

---

## 執行哲學

這份計畫以「客戶驗證」而非「技術完整性」為優先。每個 MVP 的最後一個 Task 不是「推送 git tag」，而是「跟客戶坐下來談」。技術工作只做到能支撐客戶展示的程度，不多一行。

---

## 總覽

| | MVP-1 "Dirty Demo" | MVP-2 "Design Partner" |
|---|---|---|
| **週期** | Week 1-2 | Week 3-10 |
| **目標** | 產出 90秒展示影片 + pitch deck | 與夥伴手動操作，簽 LOI |
| **客戶驗證** | 1 場 Design Partner 會議 | 付費試用或 LOI |
| **技術範圍** | 現有 v2.12 + 簡化 layout | Win + Revit + 簡化 ILOS |
| **不做** | Plugin 重構、C++ 移植、Repo 重命名 | Multi-tenant、Web client、私有 LLM |
| **Task 數** | 15 | 40 |
| **關鍵產出** | 影片 + 簡報 + 1 場會議 | 可互動系統 + LOI |

---

# MVP-1: Dirty Demo

## 功能價值描述

### 一句話

> 「用一句中文告訴 AI 你要在這塊地上蓋什麼，60 秒後看到 3D 模型 + Revit 施工圖。」

### 展示情境（影片腳本）

```
0:00  「我要在這塊 2000㎡ 的地上蓋三層樓的半導體廠務辦公室。」
       → 在現有 GUI 中輸入

0:10  AI Enhancer 增強需求：自動加入台灣建築法規參數
       → 顯示增強後的規劃摘要

0:20  AI Planner 產生建築規劃 JSON
       → 顯示計算過程（容積率/建蔽率/退縮）

0:35  3D 模型即時生成
       → PyVista 3D 視圖旋轉展示

0:45  USD 檔案輸出
       → 顯示 .usda 檔案內容（含 ilos: metadata）

0:55  一鍵匯入 Revit
       → Revit DirectShape 顯示 3D 建築

1:10  「這就是 Zigma。從自然語言到 BIM，60 秒。」
```

### 要驗證的假設

1. **半導體廠務人員是否願意看這個 Demo？** → 如果連 30 分鐘都不願意花，說明問題不夠痛
2. **「自然語言 → BIM」這個價值主張是否成立？** → 如果他們說「我們已經有 Revit template」，我們需要轉向
3. **客戶最在乎的是 AI 規劃還是 Revit 輸出？** → 決定 MVP-2 的深入方向

---

## MVP-1 開發計畫（2 週，15 Tasks）

### Week 1: 技術組裝（7T）

| Task | 說明 | 平台 | 驗收標準 |
|------|------|------|--------|
| M1-T1 | 確認 v2.12 POC 可運行 + pytest pass | Mac | CLI generate 可執行 |
| M1-T2 | 建立簡化版 layout solver (Plan B) | Mac | 矩形地塀上放置建築+基本間距檢查 |
| M1-T3 | Planner prompt 針對半導體場景優化 | Mac | 輸入「三層樓廠務辦公室」產出合理 JSON |
| M1-T4 | USD 輸出加入 ilos: metadata 欄位 | Mac | .usda 含 ilos:category + ilos:part_number |
| M1-T5 | Win RTX 4090 環境建置 + Revit 2026 | Win | conda env + Revit MCP 可通訊 |
| M1-T6 | USD → Revit DirectShape 流程打通 | Win | ILOS 測試 USD 可轉 DirectShape |
| M1-T7 | 端到端流程: NL → AI → USD → Revit | Win+Mac | CLI 一鍵執行完整流程 |

### Week 2: 展示 + 外聯（8T）

| Task | 說明 | 平台 | 驗收標準 |
|------|------|------|--------|
| M1-T8 | 操作影片腳本敲定 + 排練 | Win | 90秒腳本完成 |
| M1-T9 | 螢幕錄影 + 剩輯（OBS 或 ScreenFlow） | Win+Mac | 可分享的 MP4 |
| M1-T10 | Pitch Deck 製作 (5-7 頁) | Mac | Keynote/PPTX 完成 |
| M1-T11 | 目標客戶清單（5-10 家）| — | HTFA/設備商/EPC 名單 |
| M1-T12 | 發送郁訊 + 預約第一場會議 | — | 至少 1 場會議確認 |
| M1-T13 | Design Partner 會議執行 | — | 30min demo + 反饋收集 |
| M1-T14 | 反饋整理 + MVP-2 範圍調整 | — | 文件化反饋 |
| M1-T15 | PROJECT.md 更新 + Gate 1 結果記錄 | GitHub | PROJECT.md 更新 |

### Gate 1 標準

| 指標 | 及格 | 優秀 |
|------|------|------|
| 影片完成 | ✅ 可分享 | ★ 可上 LinkedIn |
| Design Partner 會議 | 1 場 | 3+ 場 |
| 客戶反饋 | 「有趣」 | 「我們想試用」 |
| NL → Revit E2E | 可運行 | < 2 分鐘 |

---

# MVP-2: Design Partner Demo

## 功能價值描述

### 一句話

> 「打開 Zigma，輸入你的地址和需求，5 分鐘後在 Revit 裡面看到可以改的 BIM 模型。」

### 目標使用者

台灣半導體廠務工程師 / EPC 公司機電設計師 / 設備商專案經理

### 核心功能（MVP-2 範圍）

| # | 功能 | 價值主張 | 對客戶說 |
|---|------|----------|--------|
| F1 | **土地匯入**（GeoJSON/DXF/手動） | 用你真實的地 | 「把你廠區的 CAD 拖進來」 |
| F2 | **AI 互動規劃**（多輪對話） | 像跟建築師談話一樣 | 「加一個潔淨室在二樓」|
| F3 | **3D 即時預覽** + 樓層切換 | 看得懂才改得準 | 「旋轉看看三樓平面」 |
| F4 | **USD 輸出**（含 ilos: metadata） | Digital Twin Ready | 「這個檔案可以直接進 Omniverse」 |
| F5 | **Revit 匯入**（DirectShape + MEP） | 接入現有工作流 | 「在 Revit 裡繼續修改」 |
| F6 | **簡化配管**（直線 + L型） | 不只是殼子，有管路 | 「連 UPW 主管都畫好了」 |
| F7 | **台灣建築法規檢查** | 合規就不用重來 | 「容積率超標會自動警告」 |

### 不在 MVP-2 範圍內

- Plugin 架構重構（C++ / 6 大介面）→ Phase 1
- Omniverse Streaming → Phase 3
- Web / Mobile client → Phase 4
- 私有 LLM → Phase 5
- Repo 重命名 → v3.0 tag 時再做
- 多用戶 / 多穌戶 → Phase 6

### 要驗證的假設

1. **客戶是否願意用自己的地块資料試？** → 有 = 強烈興趣，沒有 = 價值主張不夠強
2. **「5 分鐘產出 BIM」相對於他們現在的 2 週，省多少？** → 量化 ROI
3. **USD + ilos: metadata 對客戶是否有意義？** → 決定 PromptToOperate 的緊迫性
4. **客戶願意為此付多少錢？** → 定價策略

---

## MVP-2 開發計畫（8 週，3 Sprint，40 Tasks）

### Sprint A: 核心流程強化（Week 3-4，14T）

> 目標：從「Demo 影片」升級到「可互動系統」

#### Part A: AI 規劃引擎強化（5T）

| Task | 說明 | 驗收 |
|------|------|------|
| M2-A-T1 | Planner 多輪對話: 修改指令可累加 | 「加一層」可正確處理 |
| M2-A-T2 | 簡化 layout solver: 矩形放置 + 間距 + 廠區分區 | 放 10+ 設備不重疊 |
| M2-A-T3 | 簡化配管: 直線 + L型 + 基本管徑計算 | 產出含 Pipe USD Prim |
| M2-A-T4 | Checker 加入台灣法規: 容積率/建蔽率/高度 | 超標自動警告 |
| M2-A-T5 | ilos: metadata 完善: category/connections/clearance | 每個 Prim 有完整 metadata |

#### Part B: 土地輸入擴充（4T）

| Task | 說明 | 驗收 |
|------|------|------|
| M2-A-T6 | GeoJSON 匯入 + 自動座標轉換 | 匯入台灣 GeoJSON 正確 |
| M2-A-T7 | DXF 匯入（廠區 CAD 常見格式） | 讀取廠區 boundary |
| M2-A-T8 | 手動座標輸入 + 地址查詢 | 輸入地址產生多邊形 |
| M2-A-T9 | 2D 地籍預覽（matplotlib）+ 面積/周長 | 顯示土地輪廓 + 數字 |

#### Part C: Revit 輸出強化（5T）

| Task | 說明 | 驗收 |
|------|------|------|
| M2-A-T10 | Revit DirectShape 穩定化: 批次 30 mesh | 100+ mesh 不崩潰 |
| M2-A-T11 | Revit Pipe.Create + Elbow: UPW 主管 | 可編輯的 Revit 管路 |
| M2-A-T12 | Revit Material 指派: 不再全黑 | 管路/結構不同色 |
| M2-A-T13 | Revit Level 對應: 樓層正確 | 3F 對應 3 個 Level |
| M2-A-T14 | Sprint A 審計 + 客戶 check-in | 向夥伴展示進度 |

### Sprint B: 使用體驗升級（Week 5-7，14T）

> 目標：從「CLI 工具」升級到「客戶可自己操作的應用」

#### Part A: GUI 升級（6T）

| Task | 說明 | 驗收 |
|------|------|------|
| M2-B-T1 | GUI 整合: 土地匯入 → AI 對話 → 3D 預覽 一氣呱成 | 不需要 CLI |
| M2-B-T2 | Chat 面板升級: 顯示規劃過程 + 容積率即時計算 | 過程可見 |
| M2-B-T3 | 3D 視圖升級: 樓層切換 + 點擊顯示屬性 | 點擊樓板顯示面積 |
| M2-B-T4 | 導覽列: 匯入 → 規劃 → 預覽 → 匯出 步驟指引 | 客戶知道下一步 |
| M2-B-T5 | 匯出面板: 一鍵匯出 USD + IFC + Revit | 單按鈕完成 |
| M2-B-T6 | 錯誤處理 + Loading 狀態 | 不會白屏 |

#### Part B: 場景深化（4T）

| Task | 說明 | 驗收 |
|------|------|------|
| M2-B-T7 | 預設場景範本: 半導體潔淨室 | 選擇後自動填入參數 |
| M2-B-T8 | 預設場景範本: 辦公大樓 | 同上 |
| M2-B-T9 | 預設場景範本: 廠務設施 (泵浦/電力) | 同上 |
| M2-B-T10 | BOM 基礎版: 從 USD 提取設備清單 + 數量 | 輸出 CSV |

#### Part C: 穩定性（4T）

| Task | 說明 | 驗收 |
|------|------|------|
| M2-B-T11 | E2E 測試: 5 個不同場景全流程 | 5/5 pass |
| M2-B-T12 | 效能: NL → Revit < 3 分鐘 | 計時通過 |
| M2-B-T13 | Win 部署: 一鍵安裝腳本 | 客戶機器可裝 |
| M2-B-T14 | Sprint B 審計 + 客戶 check-in #2 | 客戶試用自己的地 |

### Sprint C: 客戶交付 + 簽約（Week 8-10，12T）

> 目標：Design Partner 簽 LOI 或啟動付費 Pilot

#### Part A: 客戶專屬場景（5T）

| Task | 說明 | 驗收 |
|------|------|------|
| M2-C-T1 | 客戶實際地塊資料匯入測試 | 客戶 CAD 讀入正確 |
| M2-C-T2 | 客戶實際需求場景調整 Planner | 客戶說「這像我們要的」 |
| M2-C-T3 | 客戶 Revit 版本相容性 | 客戶 Revit 可開啟 |
| M2-C-T4 | 客戶專屬法規參數調整 | 合規檢查正確 |
| M2-C-T5 | 客戶 on-site demo 準備 | 簡報 + 即時 demo 腳本 |

#### Part B: 商業交付（4T）

| Task | 說明 | 驗收 |
|------|------|------|
| M2-C-T6 | ROI 計算: 客戶現行流程 vs Zigma | 數字化比較 |
| M2-C-T7 | 定價方案 + Pilot 條款草擬 | 文件完成 |
| M2-C-T8 | LOI / Pilot 合約草擬 | 可簽署的文件 |
| M2-C-T9 | On-site demo + 商務談判 | 會議完成 |

#### Part C: 收尾（3T）

| Task | 說明 | 驗收 |
|------|------|------|
| M2-C-T10 | Gate 2 結果評估 + 教訓整理 | 文件化 |
| M2-C-T11 | Phase 1 範圍根據客戶反饋調整 | 更新後的 Dev Plan |
| M2-C-T12 | PROJECT.md 更新 + Gate 2 結果 | PROJECT.md 更新 |

### Gate 2 標準

| 指標 | 及格 | 優秀 |
|------|------|------|
| Design Partner 試用 | 用自己的地 | 用自己的地+需求 |
| 商業驗證 | LOI 簽署 | 付費 Pilot 啟動 |
| NL → Revit E2E | 5 場景通過 | < 3 分鐘 |
| BOM 輸出 | CSV 可用 | 客戶說「可以用」 |
| 客戶反饋 | 正面 | 「什麼時候可以買」 |

---

## Pitch Deck 大綱（MVP-1 用）

| 頁 | 內容 |
|---|------|
| 1 | **Zigma** — AI-Powered BIM for Semiconductor Fabs |
| 2 | **問題:** 一座新廠的規劃設計要 6-12 個月，80% 是重複工作 |
| 3 | **解決:** 用自然語言描述需求，5 分鐘產出 BIM 模型 |
| 4 | **Demo:** 90秒影片 |
| 5 | **技術:** USD SSOT + AI Agent + 零商業依賴 |
| 6 | **市場:** 台灣半導體 FAB 建設市場 $XX B |
| 7 | **團隊:** 20+ 年 AVEVA/半導體生態經驗 |

---

## 技術架構注意事項

### ILOS Plan B（簡化版 Layout Solver）

MVP-1/2 不等 ILOS 夥伴交付，自建極簡版：

```python
class SimpleLayoutSolver:
    """簡化版佈局引擎 - ILOS Plan B
    只做:
    - 矩形區域分割
    - 設備放置 + 間距檢查
    - 直線 + L型管路
    不做:
    - 振動最佳化 (VC)
    - 3D A* 路由
    - 碰撞迴避最佳化
    """
    def place_equipment(self, land, equipment_list, constraints):
        """..."""
    def route_pipe_simple(self, start, end, pipe_spec):
        """..."""
```

ILOS 到位後作為 `IEnginePlugin` 替換即可。

### 不做 Repo 重構

繼續用 `PromptBIMTestApp1` 和 `promptbim` package。品牌重命名等 v3.0。

### 治理精簡

MVP 階段只遵守 5 條核心規則：
1. 不改 CLAUDE.md / SKILL.md
2. check_mem （<1GB 暫停）
3. 每個 Part 結束 git commit+push
4. 錯誤立即 notify
5. Sprint 結束更新 PROJECT.md

---

## 風險與應對

| 風險 | 機率 | 應對 |
|------|------|------|
| 找不到 Design Partner | 中 | 擴大到 EPC/設備商，不只找廠務 |
| Revit MCP 不穩定 | 高 | M1-T6 早期驗證，不穩定則 fallback 到 IFC |
| AI 規劃品質不夠 | 中 | 縮小場景（單層樓），加預設範本 |
| Win 環境建置卡住 | 低 | M1-T5 Week 1 就做，卡住則全在 Mac |
| 客戶說「不需要」 | 低中 | pivot 到不同價值主張（成本估算 > 規劃） |

---

## 時程總覽

```
Week 1-2:  MVP-1 — Dirty Demo
           → 影片 + Pitch Deck + 1 場會議
           → Gate 1: Partner found?

Week 3-4:  MVP-2 Sprint A — 核心流程強化
           → AI + Layout + Revit 可靠運行
           → 客戶 check-in #1

Week 5-7:  MVP-2 Sprint B — 使用體驗升級
           → GUI 可操作 + 5 場景測試
           → 客戶 check-in #2: 用自己的地

Week 8-10: MVP-2 Sprint C — 客戶交付 + 簽約
           → 客戶專屬 demo + ROI + LOI
           → Gate 2: LOI signed?

Week 11-12: 緩衝 + Phase 1 規劃
           → 根據客戶反饋重新規劃 Phase 1
```

---

## Gate 失敗的回應方案

### Gate 1 失敗（找不到 Partner）

- 原因分析: 價值主張不對？目標客戶不對？展示不夠好？
- 行動: 擴大目標客戶群（EPC、設備商、建築師事務所）
- Pivot: 從「AI 規劃」轉向「USD Digital Twin 建模」價值主張
- 時限: 再花 2 週嘗試，失敗則重新評估整體方向

### Gate 2 失敗（沒簽 LOI）

- 原因分析: 功能不夠？價格不對？決策鏈太長？
- 行動: 進入「免費 Pilot」模式，用使用數據證明價值
- Pivot: 從 SaaS 轉向「專案制服務 + 軟體」模式
- 時限: Pilot 4 週，失敗則重新評估產品方向

---

*Zigma 90 天聚焦執行計畫 v1.0*
*Reality Matrix Inc. | 2026-03-27*
*核心原則: 先活下來，再優雅*
