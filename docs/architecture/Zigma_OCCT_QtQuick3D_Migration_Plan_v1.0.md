# Zigma OCCT + Qt Quick 3D 遷移計劃 v1.0

> **版本:** v1.0 | **日期:** 2026-03-28
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **性質:** 架構遷移計劃 — 從 PySide6+PyVista 遷移至 OCCT+Qt Quick 3D
> **前置文件:** ADR-001, Platform Architecture v2.1, Pre-P29 Validation Plan v1.0
> **外部夥伴文件:** ILOS_USD_Asset_Vendor_Spec v2.1, USD_Revit_Convert v2.0, USD_to_Revit_System_Architecture v1.1

---

## 1. 核心定位變更

### 1.1 之前的架構 (Platform Architecture v2.1)
- Omniverse 是核心渲染基礎設施
- 五六種渲染後端 (VTK/Hydra/Omniverse Stream/Three.js)
- Zigma 是 Omniverse 生態系前端

### 1.2 修正後的架構
- **Zigma 是獨立的 3D BIM 平台**
- OCCT (OpenCASCADE) 為幾何核心 — 真正的 CAD 引擎
- Qt Quick 3D 為唯一渲染後端 (RHI: Metal/Vulkan/D3D12)
- OpenUSD 只是 I/O 格式 — import from Omniverse, export to Omniverse
- **不直接整合 Omniverse**

### 1.3 Zigma 在生態系中的角色

```
Vendor USD (Component)
    ↓ ilos: metadata + /Connections/
ILOS + Omniverse (Scene Layout)
    ↓ scene-level: level, piping_system, line_number
    ↓ Output: Optimized USD Scene
    ↓
┌───────────────────────────────────────────┐
│  ★ Zigma PromptToBuild ★                 │
│                                           │
│  W1: ILOS USD → Zigma → Revit            │
│  W2: Prompt AI → OCCT BIM → Revit        │
│  W3: OCCT BIM → USD → Omniverse          │
│  W4: 業主設計變更 → delta → Revit         │
│                                           │
│  核心: OCCT + Qt Quick 3D + AI Agent      │
│  轉換器: USD→Revit (夥伴, 三層架構)       │
└────────────────────┬──────────────────────┘
                     ↓
              Revit BIM (.rvt)
              ├── 施工圖 (.dwg)
              ├── 送審 (.ifc)  ← IFC 只在這裡
              └── BOM/採購 (SAP)
```

---

## 2. 四個核心工作流

| # | 工作流 | 資料流向 | Zigma 角色 |
|---|--------|----------|-----------|
| W1 | ILOS 佈局 → 施工 | Omniverse USD → Zigma → Revit .rvt | USD→Revit 轉換器 |
| W2 | AI 建模 → 施工 | Prompt → OCCT BIM → Revit .rvt | AI 建模 + Revit 輸出 |
| W3 | 場景 → ILOS 處理 | OCCT BIM → USD → Omniverse | USD 匯出 |
| W4 | 業主設計變更 | 業主 on Zigma → cost/schedule delta → Revit | 變更管理平台 |

---

## 3. 技術選型

### 3.1 為什麼 OCCT + Qt Quick 3D

| 問題 | 現有 (Python) | 目標 (OCCT + Qt Quick 3D) |
|------|--------------|--------------------------|
| 記憶體 OOM | PySide6 26GB, test_agents 4GB | C++ 原生，QProcess 隔離 Python |
| 3D 效能 | PyVista→VTK Python GIL | Qt Quick 3D RHI (Metal/Vulkan/D3D12) |
| CAD 建模 | 手動算頂點 mesh | B-Rep (Boolean/掃掠/放樣) |
| Qt3D | deprecated Qt 6.8 | Qt Quick 3D 官方主推 |
| IFC 底層 | IfcOpenShell (底層也用 OCCT) | OCCT 天然相容 |

### 3.2 OCCT 在 BIM 中的能力

| 操作 | OCCT API |
|------|---------|
| 牆體 | BRepPrimAPI_MakeBox / BRepPrimAPI_MakePrism |
| 門窗開口 | BRepAlgoAPI_Cut (Boolean) |
| 柱 | BRepPrimAPI_MakeCylinder |
| 管路 | BRepOffsetAPI_MakePipe (掃掠) |
| 退縮偏移 | BRepOffsetAPI_MakeOffset |
| 面積體積 | GProp_GProps |
| STEP 匯入 | STEPControl_Reader |
| 組裝結構 | XDE (TDocStd_Document + XCAFDoc) |

### 3.3 OCCT → Qt Quick 3D 橋樑

```cpp
class BIMGeometryProvider : public QQuick3DGeometry {
    Q_OBJECT
    QML_NAMED_ELEMENT(BIMGeometry)
public:
    void loadFromShape(const TopoDS_Shape& shape) {
        BRepMesh_IncrementalMesh mesher(shape, 0.1);
        // 提取三角面 → setVertexData / setIndexData
    }
};
```

### 3.4 雙 SSOT 策略

| 場景 | 內部 SSOT | 原因 |
|------|----------|------|
| W2: AI 建模 | OCCT XDE | B-Rep 精確建模，Boolean |
| W1: ILOS USD 匯入 | USD Stage | 保留 ilos: metadata |
| W3: 匯出 | OCCT → USD | tessellation 轉換 |
| W4: 設計變更 | OCCT XDE | 變更需要 Boolean/重建 |

---

## 4. 系統架構圖

```
┌─────────────────────────────────────────────────┐
│  L5: Qt Quick 3D GUI (QML + C++)                │
│  ┌────────────┬────────────┬──────────────────┐  │
│  │ ChatPanel  │ BIMView3D  │ PropertyPanel    │  │
│  │ CostPanel  │ AssetBrowse│ SchedulePanel    │  │
│  └────────────┴────────────┴──────────────────┘  │
│  IShellPlugin → shell_qt6                        │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────┐
│  L4: BIMGeometryProvider (OCCT → Qt Quick 3D)   │
│  OCCT TopoDS_Shape                               │
│    → BRepMesh_IncrementalMesh (tessellation)     │
│    → QQuick3DGeometry (vertex/index buffers)     │
│    → PrincipledMaterial (PBR from BIM data)      │
│  IRenderBackend → render_qt3d + render_null      │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────┐
│  L3: OCCT Geometry Kernel (C++ Core)             │
│  BRepBuilderAPI — Wall/Slab/Column/Beam B-Rep   │
│  BRepAlgoAPI    — Boolean (Door/Window Opening)  │
│  BRepOffsetAPI  — Pipe Sweep / Loft              │
│  STEPControl    — STEP import/export             │
│  XDE (XCAF)     — Assembly + Properties + Color  │
│  Engine: compliance_tw + cost + mep + simulation │
└──────────────────┬──────────────────────────────┘
                   │ QProcess + JSON stdio
┌──────────────────┴──────────────────────────────┐
│  L2: Python AI Backend (Isolated Process)        │
│  agent_runner.py (asyncio)                       │
│  Enhancer → Planner → Builder → Checker → Modif  │
│  Claude API (now) → Private LLM (future)         │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────┐
│  L1: I/O Plugin Layer                            │
│  io_usd   — import/export .usd/.usda (ILOS)     │
│  io_ifc   — export IFC2x3/4 (IfcOpenShell)      │
│  io_revit — 3-Layer Converter (Partner Module)   │
│  io_step  — import .step (OCCT STEPControl)      │
│  io_geojson / io_shapefile / io_kml (GIS)        │
└──────────────────────────────────────────────────┘
```

---

## 5. 外部夥伴模組整合

### 5.1 USD→Revit Converter (io_revit)

已 POC 驗證的三層轉換架構：

| Layer | USD Content | Revit Target | Status |
|-------|-----------|-------------|--------|
| L1 | Equipment | DirectShape → Adaptive Comp. (v2) | v1 ✅ |
| L2 | Piping | Pipe.Create + NewElbowFitting | ✅ Validated |
| L3 | Structure | Column/Beam/Floor | Future |

關鍵技術：
- Instance 解析: `final_xf = inst_xf × proto_inv × mesh_xf`
- 單位: USD(cm) × 0.01 / 0.3048 = Revit(ft)
- IFC 不作為中間格式（已驗證失敗），只作為 output

### 5.2 ILOS Vendor Spec v2.1

所有廠商 USD 遵循統一結構：
- `/Geometry/` — 外觀幾何
- `/Connections/` — 連接點 (port_type, port_medium, port_size_mm)
- `ilos:` metadata — 身分+物理屬性+採購資訊
- Variant Set: blackbox (必要) / assembly (選用)

Component-level (Vendor) vs Scene-level (ILOS) 分離：
- Vendor: category, part_number, manufacturer, connections
- ILOS at placement: level, piping_system, line_number, position

---

## 6. 開發路線圖

### 6.1 Sprint 概覽

| Phase | Sprint | 內容 | 週數 | Tasks | 版本 |
|-------|--------|------|:----:|:-----:|------|
| PH0 | RS-S1 | Repo 重構 + OCCT/Qt6 環境 | 1.5 | 25 | restructure-v1.0 |
| PH1 | P26 | OCCT BIM Kernel + Plugin Bus + io_usd | 3 | 30 | v2.13.0 |
| PH2 | P27 | Qt Quick 3D GUI + BIMGeometryProvider | 2 | 26 | v2.14.0 |
| PH2 | P28 | 3D 完整化 + 4D + ILOS 場景 | 2 | 20 | v2.15.0 |
| PH3 | P29 | io_revit 整合 + 清理 + v3.0.0 | 3 | 25 | **v3.0.0** |
| | | **總計** | **~13** | **126** | |

### 6.2 里程碑驗收

| 里程碑 | Sprint | 工作流驗收 |
|--------|--------|-----------|
| OCCT 能建模 | P26 | — |
| 能看到 3D + 載入 ILOS USD | P27 | W1 部分 |
| 能 Prompt→3D + 4D 動畫 | P28 | W2 部分 |
| 四個工作流全通 | P29 | **W1+W2+W3+W4** |
| **v3.0.0 Release** | P29 | **Demo-2 ready** |

### 6.3 後續路線

```
2026 Q3-Q4:
  P30-P33: Windows + io_revit 完整化 (L1 v2 + L2 + L3)
  
2027 Q1:
  P34-P35: io_usd 完整 + ILOS 真實整合 (Cython)
  P36-P39: Web + Mobile

2027 Q2:
  P40-P42: 私有 LLM + 去除外部 AI
```

---

## 7. 從 Platform Architecture v2.1 移除的項目

| 移除項目 | 原因 |
|----------|------|
| render_omni_local / stream / cluster | 不直接整合 Omniverse |
| Omniverse Nucleus 同步 | 不需要 |
| WebRTC image streaming | 不需要 |
| Hydra Storm 渲染器 | Qt Quick 3D 取代 |
| render_web_threejs | 未來再議 |
| v3_system_design.md 方案 C | 完全過時 |

## 8. 從 Platform Architecture v2.1 保留的項目

| 保留項目 | 調整 |
|----------|------|
| Plugin 架構 (6 大介面) | 簡化，render 只需 qt3d + null |
| AgentBridge (QProcess+JSON) | 不變 |
| io_usd | 純 import/export |
| io_ifc | export only (法規送審) |
| io_revit | 三層轉換器 (夥伴模組) |
| AI Agent Pipeline | 保留 Python，QProcess 隔離 |

---

## 9. 風險分析

| 風險 | 影響 | 緩解 |
|------|------|------|
| OCCT + Qt Quick 3D 整合複雜度 | QQuick3DGeometry 需自訂 | OCCT 官方有 QML 範例；Mayo 參考架構 |
| Qt Quick 3D 大場景效能 | >10K mesh | progressive loading + LOD |
| OCCT 學習曲線 | Sole developer | FreeCAD/Mayo 大量參考代碼 |
| 夥伴 Converter 整合時程 | P29 需要 io_revit | P26-P28 用 Mock；Cython 編譯 |
| Dual SSOT 同步 | OCCT↔USD 可能不一致 | 明確分場景：AI 建模用 OCCT，ILOS 用 USD |

---

## 10. 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| v1.0 | 2026-03-28 | 初始版本：OCCT + Qt Quick 3D 獨立 3D BIM 平台架構 |

---

*Zigma OCCT + Qt Quick 3D Migration Plan v1.0*
*Reality Matrix Inc. | 2026-03-28*
*OCCT Geometry Kernel + Qt Quick 3D Renderer + Plugin Architecture + USD I/O + Revit Output*
