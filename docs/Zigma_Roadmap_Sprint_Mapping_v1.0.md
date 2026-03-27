# Zigma 開發路線圖 — Sprint 對照與任務清單

> **版本:** v1.0 | **日期:** 2026-03-27
> **用途:** 現有 Sprint 歷史 ↔ TSMC Demo ↔ 未來 Roadmap 的完整對照
> **來源:** SKILL.md v4.0 + PROJECT_STATUS.md + Dev Plan v1.1 + TSMC Demo Plan v1.0

---

## 1. 已完成 Sprint 歷史 (P0–P25)

### 基礎建設期 (P0–P6)

| Sprint | 版本 | 主題 | 交付物 | TSMC Demo 複用 |
|--------|------|------|--------|:--------------:|
| P0 | v0.1 | 專案初始化 | repo + pyproject + 基本結構 | — |
| P1 | v0.2 | 土地匯入 | LandParcel + Shapefile/GeoJSON parser | ✅ D1 F1 |
| P2 | v0.3 | AI 建築規劃 | Agent 1 Enhancer + Agent 2 Planner | ✅ D1 核心 |
| P2.5 | v0.4 | 建築零件庫 | 74 種零件 + 供應商 + 價格 | ✅ D1 Cost |
| P3 | v0.5 | IFC 生成 | IfcOpenShell ifc_generator | ✅ D2 建照 |
| P4 | v0.6 | USD 生成 | pxr usd_generator | ✅ D1 + D2 核心 |
| P4.5 | v0.7 | 台灣建築法規 | 容積率/建蔽率/退縮/高度 | ✅ D1 F7 |
| P5 | v0.8 | 3D 視覺化 | PyVista + pyvistaqt 3D 視圖 | ✅ D1 F6 |
| P6 | v0.9 | GUI Desktop | PySide6 主視窗 + Chat 面板 | ✅ D1-S2 GUI |

### 整合期 (P11–P17)

| Sprint | 版本 | 主題 | 交付物 | TSMC Demo 複用 |
|--------|------|------|--------|:--------------:|
| P11 | v1.0 | Xcode 整合 | SwiftUI Wrapper + PythonBridge | — (Mac only) |
| P12 | v1.1 | 品質修復 | 單實例 + Process 管理 | — |
| P13 | v1.2 | CLI + PDF OCR | generate CLI + pdf_ocr.py | ✅ D1 CLI |
| P14 | v2.0 | CI/CD + 安全 | GitHub Actions + pip-audit | ✅ 基礎設施 |
| P16 | v2.1 | 品質修整 | constants.py + tenacity retry + timeout | ✅ 穩定性 |
| P17 | v2.4 | 架構強化 | Async + Cache + Plugin + Rate Limiter | ✅ D1 核心 |
| P17.1 | v2.4.1 | 審計修復 | 文檔一致性 patch | ✅ |

### 成熟期 (P18–P25)

| Sprint | 版本 | 主題 | 交付物 | TSMC Demo 複用 |
|--------|------|------|--------|:--------------:|
| P18 | v2.5 | 台灣法規強化 | Compliance Engine 擴充 | ✅ D1 F7 |
| P19 | v2.6 | 測試強化 | 測試覆蓋率提升 | ✅ 穩定性 |
| P20 | v2.7 | MCP Server | FastMCP + orchestrator | — |
| P21 | v2.8 | 文件整理 | SKILL 大更新 + 審計 | ✅ 治理 |
| P22 | v2.9 | 通知系統 | iMessage notify + 雙向通知 | ✅ 運維 |
| P23 | v2.10 | 審計修復 | 最後成功 tag | ✅ 基線 |
| **P24** | **v2.11** | **pytest 修復** | 代碼完成，**未打 tag** (OOM) | ⚠️ 待收尾 |
| **P25** | **v2.12** | **效能+Win+文件** | 代碼完成，**待 pytest+tag** | ⚠️ 待收尾 |

### 統計摘要

| 指標 | 數值 |
|------|------|
| 已完成 Sprint | 25 個 (P0–P25) |
| 最後成功 Tag | v2.10.0 (P23) |
| 待收尾 | P24 (pytest OOM) + P25 (pytest+tag) |
| 總測試數 | ~799 tests |
| 審計報告 | 14 份 (P16–P25) |
| 治理文件 | CLAUDE v1.23.1 + SKILL v4.0 + PROJECT v1.2 |

---

## 2. 現有能力 vs TSMC Demo 需求對照

### ✅ 已具備（可直接複用）

| 能力 | 來源 Sprint | TSMC Demo 用途 |
|------|-----------|-------------|
| NL → AI 規劃 (Enhancer + Planner) | P2 + P17 | D1 核心流程 |
| USD 生成 (.usda + metadata) | P4 | D1 輸出 + D2 輸入 |
| IFC 生成 | P3 | D2 建照輔助 |
| PySide6 GUI (Chat + 3D + 2D) | P6 | D1-S2 展示界面 |
| PyVista 3D 視圖 | P5 | D1 3D 預覽 |
| 土地匯入 (GeoJSON/Shapefile) | P1 | D1 土地輸入 |
| 台灣建築法規檢查 | P4.5 + P18 | D1 合規檢查 |
| CLI generate 命令 | P13 | D1 E2E 流程 |
| Async Agent + Cache + Plugin | P17 | D1 效能 |
| Rate Limiter + Retry | P16 + P17 | D1 穩定性 |
| 建築零件庫 (74 種 + 價格) | P2.5 | D1 成本估算基礎 |

### 🟡 部分具備（需強化）

| 能力 | 現狀 | 需要做 | Demo |
|------|------|--------|:----:|
| Planner FAB 場景 | 通用建築 | 針對半導體廠務優化 prompt | D1 |
| ilos: metadata | 基本欄位 | 加 connections/clearance | D1+D2 |
| DirectShape → Revit | POC 已驗證 | 穩定化 + 批次處理 | D2 |
| Pipe.Create + Elbow | POC 已驗證 | 整合到流程 | D2 |
| Win 環境支援 | P25 基本支援 | Revit MCP 完整流程 | D1+D2 |

### 🔴 尚未具備（新開發）

| 能力 | TSMC 需求 | 對應 Demo |
|------|----------|--------|
| **Cost Engine** | Prompt 變更 → 即時成本 | D1 核心 |
| **Schedule Engine** | Prompt 變更 → 即時工期 | D1 核心 |
| **Modifier Agent** | 變更指令解析 + 重新規劃 | D1 核心 |
| **簡化 Layout Solver** | 區域分割 + 設備放置 + 間距 | D1 |
| **簡化配管** | 直線 + L型 + 管徑 | D1 |
| **成本/工期差異報告** | 變更前後對照 | D1 |
| **Omniverse Nucleus 整合** | USD publish + 載入 | D2 核心 |
| **Omniverse Streaming** | RTX 瀏覽器可視化 | D2 核心 |
| **Omniverse → Revit Connector** | 同步到 Revit 專案 | D2 核心 |
| **Revit 圖紙自動化** | 平面/立面/剖面/Schedule | D2 核心 |
| **PDF 建照圖說輸出** | 完整審核文件 | D2 |

---

## 3. TSMC Demo 開發路線圖

### 路線圖總覽

```
═══ 收尾期 (Week 0) ═════════════════════════════════

P24 pytest OOM 修復 + P25 tag v2.12.0
  │ 收尾現有 POC，確保基線穩定
  ▼
═══ Demo-1 (Week 1-4) ══════════════════════════════

D1-S1: AI + Cost Engine + Schedule Engine (Week 1-2)
D1-S2: GUI + FAB 場景 + TSMC 展示 (Week 3-4)
  │ ★ TSMC Demo-1 展示
  │ Gate: TSMC 想看 Demo-2?
  ▼
═══ Demo-2 (Week 5-10) ═════════════════════════════

D2-S1: Omniverse Nucleus + Streaming (Week 5-6)
D2-S2: Omniverse → Revit + 建照圖說 (Week 7-8)
D2-S3: 整合測試 + TSMC 展示 (Week 9-10)
  │ ★ TSMC Demo-2 展示
  │ Gate: LOI / Pilot?
  ▼
═══ Phase 1 (Week 11-18) ═══════════════════════════

P26-P29: Plugin 架構 + Qt6 C++ + ABI 凍結 → v3.0
  ▼
═══ Phase 2+ (Week 19+) ══════════════════════════

P30-P33 Windows + USD↔Revit → P34-P37 ILOS+Omniverse
→ P38-P41 Web+Mobile → P42-P44 私有LLM → P45+ SaaS
```

---

## 4. Sprint 對照表：舊版 Dev Plan v1.1 vs TSMC Demo Plan

| 舊版 Sprint | 舊版內容 | 新版對應 | 變化說明 |
|-----------|--------|--------|--------|
| PH0 P25收尾 | POC pytest+tag | **Week 0 收尾** | 不變，但縮短到 2-3 天 |
| PH0 P24修復 | conftest OOM | **Week 0 收尾** | 合併到收尾期 |
| PH0 Win驗證 | Omniverse/Revit 前置 | **D1-S1-PA-T5~T6** | 提前到 Demo-1 |
| PH0.5 D1-S1 | 環境+POC驗證 (12T) | **D1-S1 (15T)** | 加入 Cost+Schedule Engine |
| PH0.5 D1-S2 | USD→Revit轉換 (12T) | **D2-S2 (12T)** | 移到 Demo-2（透過 Omniverse） |
| PH0.5 D1-S3 | AI規劃+Demo整合 (11T) | **D1-S2 (20T)** | 擴充 GUI + FAB 場景 + 成本報告 |
| PH0.5 D2-S1 | ILOS整合+Cython (11T) | **延後到 Phase 3** | ILOS 夥伴未到位，用簡化版替代 |
| PH0.5 D2-S2 | Omniverse視覺化+Streaming (11T) | **D2-S1 (12T)** | 縮範圍但加深 |
| PH0.5 D2-S3 | Demo-2整合+交付 (10T) | **D2-S3 (11T)** | 加入建照圖說+PDF |
| RS-S1 | Repo重構 (30T) | **延後到 v3.0** | 不在 TSMC Demo 範圍內 |
| PH1 P26-P29 | Plugin架構+Qt6 (96T) | **Phase 1 (Week 11-18)** | Demo 後執行，不變 |

### 關鍵變化摘要

1. **新增模組:** Cost Engine、Schedule Engine、Modifier Agent、簡化 Layout Solver、簡化配管 — 這些在舊版是 Phase 2+ 的工作，因為 TSMC 需求提前
2. **提前模組:** Omniverse 整合從 Phase 3 提前到 Demo-2
3. **延後模組:** RS-S1 Repo 重構、ILOS 夥伴整合、C++ 移植
4. **路徑變更:** USD → Revit 從「DirectShape 直接」變成「USD → Omniverse → Connector → Revit」

---

## 5. 完整任務清單

### Week 0: 收尾期 (5 Tasks)

| ID | 說明 | 來源 | 平台 | 狀態 |
|----|------|------|------|:----:|
| W0-T1 | P24 conftest.py offscreen 修復 | P24 | Mac | ⬜ |
| W0-T2 | P24 pytest pass + git tag v2.11.0 | P24 | Mac | ⬜ |
| W0-T3 | P25 pytest 驗證 | P25 | Mac | ⬜ |
| W0-T4 | P25 git tag v2.12.0 | P25 | Mac | ⬜ |
| W0-T5 | Win RTX 4090 基本環境確認 | PH0 | Win | ⬜ |

### Demo-1 Sprint D1-S1: AI + Cost + Schedule (Week 1-2, 15T)

| ID | 說明 | 新/複用 | 平台 |
|----|------|--------|------|
| D1-S1-PA-T1 | v2.12 POC 可運行 + pytest pass | 複用 | Mac |
| D1-S1-PA-T2 | Planner prompt FAB 場景優化 | 強化 | Mac |
| D1-S1-PA-T3 | Modifier Agent: 變更指令 + 重新規劃 | **新** | Mac |
| D1-S1-PA-T4 | 簡化 layout solver: 區域 + 設備 + 間距 | **新** | Mac |
| D1-S1-PA-T5 | 簡化配管: 直線 + L型 + 管徑 | **新** | Mac |
| D1-S1-PA-T6 | USD 輸出: ilos: metadata 完整 | 強化 | Mac |
| D1-S1-PB-T7 | 台灣營建單價資料庫 (JSON) | **新** | Mac |
| D1-S1-PB-T8 | Cost Engine: BOM × 單價 × 係數 | **新** | Mac |
| D1-S1-PB-T9 | 成本報告產生器: 逐項明細 + 總價 | **新** | Mac |
| D1-S1-PB-T10 | 變更成本差異: 前後對照 | **新** | Mac |
| D1-S1-PC-T11 | 工項依賴模型 (JSON) | **新** | Mac |
| D1-S1-PC-T12 | Schedule Engine: 工期 + 關鍵路徑 | **新** | Mac |
| D1-S1-PC-T13 | 甘特圖產生器 (SVG/HTML) | **新** | Mac |
| D1-S1-PC-T14 | 變更工期差異: 前後對照 | **新** | Mac |
| D1-S1-PC-T15 | E2E: NL → BIM → Cost → Schedule | 整合 | Mac |

### Demo-1 Sprint D1-S2: GUI + 展示 (Week 3-4, 20T)

| ID | 說明 | 新/複用 | 平台 |
|----|------|--------|------|
| D1-S2-PA-T1 | GUI 整合: 土地→AI→報告 一氣呱成 | 強化 | Mac |
| D1-S2-PA-T2 | Chat 面板: 多輪對話 + 變更指令 | 強化 | Mac |
| D1-S2-PA-T3 | 3D 視圖: 樓層切換 + 點擊屬性 | 強化 | Mac |
| D1-S2-PA-T4 | 成本面板: 明細 + 圖表 | **新** | Mac |
| D1-S2-PA-T5 | 工期面板: 甘特圖 + 關鍵路徑 | **新** | Mac |
| D1-S2-PA-T6 | 變更對照面板: 前/後並排 | **新** | Mac |
| D1-S2-PA-T7 | 匯出面板: USD + 成本 + 工期 | 強化 | Mac |
| D1-S2-PB-T8 | 預設場景: 潔淨室廠房 | **新** | Mac |
| D1-S2-PB-T9 | 預設場景: 廠務設施棟 | **新** | Mac |
| D1-S2-PB-T10 | 預設場景: 辦公大樓 | **新** | Mac |
| D1-S2-PB-T11 | 廠務設備庫: 幫浦/空壓機/UPW | **新** | Mac |
| D1-S2-PB-T12 | 台灣法規檢查: 容積/建蔽/高度 | 強化 | Mac |
| D1-S2-PB-T13 | 消防法規基礎: 退縮/樓梯/防火 | **新** | Mac |
| D1-S2-PC-T14 | Win RTX 4090 部署 + 測試 | 複用 | Win |
| D1-S2-PC-T15 | 5 場景 E2E 測試 | 整合 | Win |
| D1-S2-PC-T16 | 效能: < 3 分鐘 | 整合 | Win |
| D1-S2-PC-T17 | Demo 腳本 + 排練 | **新** | Win |
| D1-S2-PC-T18 | 螢幕錄影 (backup) | **新** | Win |
| D1-S2-PC-T19 | TSMC 展示簡報 (8頁) | **新** | Mac |
| D1-S2-PC-T20 | Demo-1 審計 + PROJECT.md | 治理 | — |

### Demo-2 Sprint D2-S1: Omniverse (Week 5-6, 12T)

| ID | 說明 | 新/複用 | 平台 |
|----|------|--------|------|
| D2-S1-PA-T1 | Omniverse Nucleus 安裝 + 驗證 | **新** | Win |
| D2-S1-PA-T2 | USD publish 到 Nucleus 自動化 | **新** | Win |
| D2-S1-PA-T3 | Nucleus 目錄結構規劃 | **新** | Win |
| D2-S1-PA-T4 | Demo-1 USD 載入驗證 | 整合 | Win |
| D2-S1-PA-T5 | ilos: metadata 在 Omniverse 可見 | 強化 | Win |
| D2-S1-PA-T6 | Layer Stack: 多版本分層 | **新** | Win |
| D2-S1-PB-T7 | Kit App + Pixel Streaming | **新** | Win |
| D2-S1-PB-T8 | Streaming 互動: 旋轉/縮放 | **新** | Win+Mac |
| D2-S1-PB-T9 | 自適應品質 | **新** | Win |
| D2-S1-PB-T10 | 3D 場景標註功能 | **新** | Win |
| D2-S1-PB-T11 | 截圖/錄影功能 | **新** | Win |
| D2-S1-PB-T12 | Sprint D2-S1 審計 | 治理 | — |

### Demo-2 Sprint D2-S2: Revit + 建照 (Week 7-8, 12T)

| ID | 說明 | 新/複用 | 平台 |
|----|------|--------|------|
| D2-S2-PA-T1 | Revit 2026 + Omniverse Connector | **新** | Win |
| D2-S2-PA-T2 | USD → Revit: 結構體 DirectShape | 強化 | Win |
| D2-S2-PA-T3 | USD → Revit: MEP 管路 | 強化 | Win |
| D2-S2-PA-T4 | Material 對應: OmniPBR → Revit | **新** | Win |
| D2-S2-PA-T5 | SharedParameter: ilos: → Revit | **新** | Win |
| D2-S2-PA-T6 | 同步穩定性: 100+ mesh | 強化 | Win |
| D2-S2-PB-T7 | Revit 圖紙: 各樓平面圖 | **新** | Win |
| D2-S2-PB-T8 | Revit 圖紙: 立面 + 剖面 | **新** | Win |
| D2-S2-PB-T9 | 標註自動化: 尺寸/室名/樓高 | **新** | Win |
| D2-S2-PB-T10 | Schedule 表: 門窗/房間 | **新** | Win |
| D2-S2-PB-T11 | PDF 建照圖說輸出 | **新** | Win |
| D2-S2-PB-T12 | Sprint D2-S2 審計 | 治理 | — |

### Demo-2 Sprint D2-S3: 整合 + 展示 (Week 9-10, 11T)

| ID | 說明 | 新/複用 | 平台 |
|----|------|--------|------|
| D2-S3-PA-T1 | 全流程 E2E: NL→BIM→Cost→USD→Omni→Revit→PDF | 整合 | Win |
| D2-S3-PA-T2 | 3 個 FAB 場景 E2E | 整合 | Win |
| D2-S3-PA-T3 | 效能: 全流程 < 10 分鐘 | 整合 | Win |
| D2-S3-PA-T4 | 斷點復原: 各步驟可重試 | **新** | Win |
| D2-S3-PA-T5 | Streaming 30分鐘穩定性 | 整合 | Win |
| D2-S3-PB-T6 | Demo 腳本: D1+D2 連貫 12分鐘 | **新** | Win |
| D2-S3-PB-T7 | 排練 3次 + 應變 | **新** | Win |
| D2-S3-PB-T8 | TSMC ROI 簡報 | **新** | Mac |
| D2-S3-PB-T9 | 螢幕錄影 (backup) | **新** | Win |
| D2-S3-PB-T10 | TSMC 展示執行 | **新** | Win |
| D2-S3-PB-T11 | Demo-2 審計 + PROJECT.md + 下一步 | 治理 | — |

---

## 6. 任務統計

| 階段 | Sprint | Tasks | 新開發 | 複用/強化 | 週數 |
|------|--------|:-----:|:------:|:---------:|:----:|
| 收尾 | W0 | 5 | 0 | 5 | 0.5 |
| Demo-1 | D1-S1 | 15 | 10 | 5 | 2 |
| Demo-1 | D1-S2 | 20 | 12 | 8 | 2 |
| Demo-2 | D2-S1 | 12 | 10 | 2 | 2 |
| Demo-2 | D2-S2 | 12 | 8 | 4 | 2 |
| Demo-2 | D2-S3 | 11 | 6 | 5 | 2 |
| **合計** | **6 Sprint** | **75** | **46** | **29** | **10.5** |

**全新模組占比:** 46/75 = 61% — 大部分是新工作（Cost/Schedule/Omniverse/建照）
**複用占比:** 29/75 = 39% — P0-P25 的積累提供了近 4 成的基礎

---

## 7. 未來路線圖（Demo 後）

Demo 完成後回到 Dev Plan v1.1 的主線，但根據 TSMC 反饋調整優先級：

| Phase | Sprint | 目標 | 版本 | 與 Demo 的關係 |
|-------|--------|------|------|------------|
| **PH1** | P26-P29 | Plugin 架構 + Qt6 C++ | v3.0 | Demo 結果決定優先級 |
| **PH2** | P30-P33 | Windows + USD↔Revit L2/3 | v3.x | 深化 Demo-2 的 Revit |
| **PH3** | P34-P37 | ILOS Engine + Omniverse | v4.0 | 深化 Demo-1 的 Layout |
| PH4 | P38-P41 | Web + Mobile | v4.x | TSMC thin client 需求 |
| PH5 | P42-P44 | 私有 LLM | v5.0 | TSMC 零外部 AI 需求 |
| PH6 | P45-P50+ | SaaS + Marketplace | v5.x+ | 規模化 |

### 依賴關係

```
Demo-1 結果
  ├─ TSMC 要求「更精確的成本」→ 優先 PH2 (ERP 整合)
  ├─ TSMC 要求「更複雜的佈局」→ 優先 PH3 (ILOS)
  └─ TSMC 要求「零外部 AI」→ 優先 PH5 (私有 LLM)

Demo-2 結果
  ├─ TSMC 要求「更好的 Revit 輸出」→ 優先 PH2 (USD↔Revit L2/3)
  ├─ TSMC 要求「網頁存取」→ 優先 PH4 (Web Client)
  └─ TSMC 要求「多人協作」→ P48 (Collaboration)
```

---

## 8. 技術債追蹤

| ID | 債務 | 來源 | 計畫解決 | 影響 |
|----|------|------|--------|------|
| TD-001 | P24 pytest OOM 未 tag | P24 | W0-T1/T2 | ⬜ 基線不穩 |
| TD-002 | PySide6 記憶體開銷 | P24b | P29 移除 | 🟡 可容忍 |
| TD-003 | Repo 未重命名 (zigma) | RS-S1 | v3.0 時 | 🟢 不影響 Demo |
| TD-004 | Package 未重命名 (zigma_build) | RS-S1 | v3.0 時 | 🟢 不影響 Demo |
| TD-005 | ILOS 夥伴未到位 | PH3 | 簡化版替代 | 🟡 Demo 用 Plan B |
| TD-006 | C++ 移植未開始 | PH1 | P26-P29 | 🟢 Demo 不需要 |
| TD-007 | 成本估算精確度 | Demo-1 | 客戶反饋調整 | 🟡 標註「估算值」 |

---

*Zigma 開發路線圖 v1.0 | 2026-03-27*
*P0-P25 歷史 + TSMC Demo + Phase 1-6 完整對照*
