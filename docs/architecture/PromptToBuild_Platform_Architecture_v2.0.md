# PromptToBuild 統一平台架構設計 v2.0

> **版本:** v2.0 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **前身:** PromptBIM Architecture Design v1.0
> **願景:** 從 PromptBIM POC 演進為 PromptToBuild 企業級統一平台

---

## 1. 願景演進

```
PromptBIM (POC, v2.12.0)              PromptToBuild (Platform, v4.0+)
├─ 單一建築 BIM 生成                    ├─ 前端入口 + 後段整合平台
├─ 單機桌面 App                         ├─ 跨平台 (Win/Mac/Linux)
├─ Python + C++ 混合                    ├─ C++ Core + Plugin 架構
├─ 本地 PyVista 渲染                    ├─ Omniverse 遠端渲染 + Image Streaming
├─ IFC/USD 單向輸出                     ├─ 雙向 OpenUSD ↔ Revit
└─ 獨立運作                             ├─ ILOS AI 佈局引擎整合
                                        ├─ Omniverse Cluster 整合
                                        └─ 模組可插拔 / 多 Plugin 生態
```

### 六大整合需求

| # | 需求 | 說明 |
|---|------|------|
| 1 | 雙向 OpenUSD ↔ Revit | USD → Revit（已 POC 驗證）+ Revit → USD 回寫 |
| 2 | ILOS AI 佈局引擎 | 半導體晶圓廠設備佈局優化 + 管路自動路由 |
| 3 | Omniverse Cluster | 大型場景分散式渲染 + 協作 |
| 4 | PromptToBuild 前端 | 統一入口，整合後段所有服務 |
| 5 | 模組可插拔 | Plugin 架構支援第三方擴展 |
| 6 | 跨平台 + 遠端渲染 | Win/Mac/Linux + Omniverse Streaming |

---

## 2. 核心設計原則

| # | 原則 | 說明 |
|---|------|------|
| 1 | **USD 為 SSOT** | OpenUSD 場景是唯一的資料真相來源 |
| 2 | **Plugin-First** | 每個功能模組都是 Plugin，可獨立載入/卸載/替換 |
| 3 | **渲染與邏輯分離** | 核心服務不依賴渲染器；渲染器可抽換 |
| 4 | **跨平台原生** | C++ Core + Qt6 GUI，Win/Mac/Linux 統一程式碼 |
| 5 | **雙向互通** | USD ↔ Revit 是持續同步，不是單向轉換 |
| 6 | **Scale-Out 渲染** | 小模型本地渲染，大模型 Omniverse Streaming |

---

## 3. 六層架構

```
L6 前端層:     Qt6 C++ Desktop (Win/Mac/Linux) | Web | CLI | MCP
L5 渲染層:     VTK (本地) | Hydra Storm (GPU) | Omniverse Streaming (遠端)
L4 AI 服務:    PromptBIM Agents | ILOS Layout Optimizer (Python via libpython)
L3 核心引擎:   USD↔Revit | BIM | Compliance | Cost | MEP | Sim (全 C++)
L2 Plugin 匯流排: Parser|Agent|Code|Render|Export|Vendor|ERP|Custom
L1 資料層:     USD Stage (SSOT) | Omniverse Nucleus | Asset Library | CI/CD
```

---

## 4. 雙向 USD ↔ Revit

### 三層轉換策略（已 POC 驗證）

| Layer | USD Content | Revit Target | Status | Editable? |
|-------|------------|-------------|--------|----------|
| L1 | Equipment | DirectShape → Adaptive Comp. | v1 ✅ / v2 planned | v1: Move only |
| L2 | Piping | Pipe.Create + NewElbowFitting | ✅ Validated | Full MEP |
| L3 | Structure | Revit native structural | Future Phase 3 | Full |

### 關鍵技術: Instance 解析

```
final_transform = inst_xf × proto_inv × mesh_xf

stage.Traverse()       → ❌ 跳過 Instance 內部
stage.TraverseAll()    → ⚠️ 部分 USD 回傳 0 Instance Proxy
手動 inst×proto⁻¹×mesh → ✅ 始終正確
```

### 單位換算

| 來源 | 單位 | 轉換至 Revit (ft) |
|------|------|------------------|
| USD (NVIDIA) | cm | × 0.01 / 0.3048 |
| Blender | m | ÷ 0.3048 |
| IFC | mm | ÷ 304.8 |

### 路線決策歷程

- **路線 A (USD→IFC→Revit): 已放棄** — IfcFacetedBrep 幾何在 Revit 無法渲染
- **路線 B (DirectShape): 已驗證** — 10 個 POC 案例（913 建築 / 561K 頂點）
- **路線 C (MEP Native): 已驗證** — 跨樓層管路 + 自動彎頭完全可編輯

---

## 5. 渲染架構（Scale-Out）

### 渲染抽象層 (RAL) 自動選擇

| Backend | Scene Size | GPU | Use Case |
|---------|-----------|-----|----------|
| VTK (local) | < 1,000 mesh | CPU/iGPU | 建築設計、小型場景 |
| Hydra Storm | < 10,000 mesh | dGPU (RTX) | FAB 佈局、設備審查 |
| Omniverse Stream | > 10,000 mesh | Remote Farm | 整座晶圓廠、城市級 |
| Omniverse Cluster | Unlimited | GPU Cluster | 超大場景、多人協作 |

### Omniverse 整合

```
Client → omni:// → Omniverse Nucleus (USD 儲存)
Client → Kit API → Omniverse Kit (場景編輯)
Client → Farm API → Omniverse Farm (批次渲染)
Client → Streaming → WebRTC/Pixel Streaming → 3D Viewport Widget
```

---

## 6. ILOS 佈局引擎整合

```
使用者描述 → PromptBIM AI Agent (需求增強+規劃)
  → BuildingPlan + Equipment List
  → ILOS Layout Optimizer (設備放置+管路路由+碰撞檢測)
  → Optimized USD Scene (ilos: metadata)
  → USD↔Revit Converter
  → Revit .rvt (施工圖) / BOM (SAP/ERP) / IFC (送審)
```

### 廠商資產規格 (ilos: spec v2.1)

```
元件層級 (廠商提供)        場景層級 (ILOS 自動注入)
├─ ilos:category            ├─ ilos:level (FL1/FL2/FL3)
├─ ilos:part_number         ├─ ilos:piping_system (UPW/CDA)
├─ ilos:nominal_diameter    ├─ ilos:connection_start [x,y,z]
├─ /Connections/            ├─ ilos:connection_end [x,y,z]
└─ /Geometry/               └─ ilos:line_number
```

---

## 7. Plugin 架構

| Category | Examples | Language | Hot Reload? |
|----------|---------|----------|:-----------:|
| Parser | GeoJSON, SHP, DXF, KML | C++ | Yes |
| Agent | Enhancer, Planner, ILOS | Python | Yes |
| CodeRule | Taiwan, Japan, US codes | C++ | Yes |
| Renderer | VTK, Hydra Storm, Omniverse | C++ | No |
| Exporter | IFC, USD, DWG, PDF | C++ | Yes |
| VendorAsset | ASML, Swagelok, Edwards | C++/Data | Yes |
| ERPConnector | SAP, Oracle | C++ | Yes |
| Custom | Client-specific | C++/Python | Yes |

### Plugin 介面

```cpp
class IPlugin {
public:
    virtual void initialize(PluginContext& ctx) = 0;
    virtual void shutdown() = 0;
    virtual std::string name() const = 0;
    virtual PluginCategory category() const = 0;
    virtual PluginCapabilities capabilities() const = 0;
};
```

Plugin Discovery: 掃描 plugins/ 目錄 → dlopen() / LoadLibrary() → 動態載入

---

## 8. 跨平台策略

| 元件 | Windows | macOS | Linux |
|------|---------|-------|-------|
| Qt6 GUI | MSVC + vcpkg | Clang + brew | GCC + apt |
| C++ Core | ✅ | ✅ | ✅ |
| Python AI | ✅ | ✅ | ✅ |
| Omniverse | ✅ (主要) | ⚠️ | ✅ |
| Revit MCP | ✅ (唯一) | ❌ (遠端) | ❌ (遠端) |

---

## 9. 開發路線圖

| Phase | Sprints | Focus | Version |
|-------|---------|-------|--------|
| Phase 1 | P26-P29 | Qt6 C++ GUI + Plugin + RAL | v3.0.0 |
| Phase 2 | P30-P33 | Windows + 雙向 USD↔Revit + Hydra Storm | v3.x |
| Phase 3 | P34-P37 | ILOS Engine + Vendor Assets + Omniverse | v4.0 |
| Phase 4 | P38+ | Enterprise: BOM/SAP + Collaboration + Cluster | v4.x+ |

---

## 10. 文件對應關係

| 平台文件 | ILOS-FAB 文件 |
|---------|---------------|
| 本文件 (v2.0) | USD_to_Revit_System_Architecture.md |
| 本文件 (v2.0) | USD_Revit_Convert.md (SOP) |
| 本文件 (v2.0) | ILOS_USD_Asset_Vendor_Spec.md (v2.1) |
| PromptBIM Arch v1.0 | — (原始 POC 架構) |

---

## 11. 技術風險

| 風險 | 影響 | 緩解策略 |
|------|------|--------|
| Omniverse Linux SDK | Linux client 受限 | VTK fallback + Streaming |
| Revit 僅限 Windows | Mac/Linux 無法直接 Revit | Revit MCP 作為遠端服務 |
| 超大 USD 場景 | 單機無法載入 | Omniverse Nucleus + 分頁載入 |
| Plugin ABI 穩定性 | 跨版本相容 | 穩定 C ABI + 版本化介面 |
| AI Agent 延遲 | Planner 60-90s | 非同步 + 快取 |
| 廠商 USD 品質 | metadata 不合規 | 驗證引擎 + 自動修復 |

---

*PromptToBuild 統一平台架構設計 v2.0*
*Reality Matrix Inc. | 2026-03-27*
*整合: ILOS-FAB + Omniverse + 雙向 USD↔Revit + Plugin 架構 + 遠端渲染*
*完整 PDF 版含詳細系統上下文圖、渲染架構圖、Plugin 載入流程圖*
