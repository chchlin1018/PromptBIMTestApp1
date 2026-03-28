# Sprint P30: USD to Revit Pipeline

> **目標:** 完整的 OpenUSD -> Revit API -> IFC 輸出管線
> **Tasks:** 25 / **Parts:** 4 / **Tag:** v3.0.0
> **前提:** M2-MEP-DEMO 已完成 (BIMEntity + Scene Graph + 管線系統)

## Pipeline 架構

```
Zigma Scene (BIMEntity)
    |
    v
io_usd Exporter -> OpenUSD Stage (.usda/.usdc)
    |
    v
io_revit -> Revit API (DirectShape Layer 1 + MEP Native Layer 2)
    |
    v
IFC Generator -> IFC 2x3/4 (法規合規輸出)
```

## Part A (T1-7): USD Export 升級

升級 `bim/io_usd/exporter.py`:
- 從 BIMEntity Scene Graph 直接匯出 USD Stage
- 每個 BIMEntity 對應一個 USD Prim
- 保留所有 properties (cost, connections, type) 作為 USD Custom Attributes
- 材質對應: BIMMaterialLibrary -> USD Preview Surface
- 幾何: Primitives -> USD Cube/Cylinder/Mesh
- MEP 管線: PipeSegment -> USD Cylinder with connections metadata
- 輸出格式: .usda (文字, 開發用) + .usdc (二進制, 生產用)

升級 `bim/usd_generator.py`:
- 參數化 USD 生成 (根據 equipment_catalog.json)
- 建築模板: Fab, CUB, Office, CoolingTower
- MEP 模板: Chiller, Compressor, UPW, Pipe
- LOD 支援: LOD0 (box) / LOD1 (basic shape) / LOD2 (detailed)

建立 `bim/io_usd/stage_manager.py`:
- USD Stage CRUD 操作
- Layer 管理 (base layer + override layers)
- Reference/Payload 支援 (大場景分層載入)
- 版本追蹤 (每次操作產生新 layer)

## Part B (T8-14): Revit API 連接 (Windows)

建立 `bim/io_revit/` 模組:
- `exporter.py` — USD Stage -> Revit API
- `directshape.py` — Layer 1: DirectShape (快速匯入, 任意幾何)
- `native_mep.py` — Layer 2: Revit Native MEP 元件
- `family_mapper.py` — BIMEntity type -> Revit Family 對應表
- `parameter_writer.py` — BIMEntity properties -> Revit Shared Parameters

Layer 1 — DirectShape (快速, 視覺化用):
- 所有 BIMEntity 幾何體轉換為 Revit DirectShape
- 保留位置/尺寸/材質
- 適用: 快速預覽, 客戶審查

Layer 2 — Native MEP (精確, 工程用):
- Chiller -> Revit Mechanical Equipment Family
- CoolingTower -> Revit Mechanical Equipment Family
- Pipe -> Revit Pipe + Pipe Fitting
- Duct -> Revit Duct
- 適用: 工程出圖, 施工文件

★ Revit API 只能在 Windows 上執行 (需要 Revit 安裝)
★ 開發: Python + pyRevit 或 Revit.NET API via IronPython
★ 測試: Windows RTX4090 (VS2022 + Revit 2024)

## Part C (T15-20): IFC 輸出

升級 `bim/ifc_generator.py`:
- 從 BIMEntity Scene Graph 生成 IFC 2x3
- IfcBuilding / IfcBuildingStorey / IfcSpace 層級結構
- MEP 元件: IfcFlowTerminal, IfcFlowSegment, IfcDistributionPort
- 屬性集: Pset_MechanicalEquipment, Pset_ElectricalEquipment
- 數量集: Qto_PipeBaseQuantities (管線長度/直徑/面積)

升級 `bim/mep/ifc_mep.py`:
- MEP 系統關聯: IfcSystem (冷卻水/冰水/壓縮空氣)
- 連接關係: IfcRelConnectsPortToElement
- 流向標註: IfcDistributionPort (SOURCE/SINK)

IFC 驗證:
- ifcopenshell 驗證語法正確性
- 台灣建築法規欄位檢查 (建蔽率/容積率)

## Part D (T21-25): Omniverse 連接 + 測試

升級 `bim/omniverse.py`:
- USD Stage 上傳到 Omniverse Nucleus Server
- Live sync: Zigma 操作 -> Omniverse 即時更新
- 多用戶: 不同用戶同時操作同一場景
- ★ 需要 Windows RTX4090 + Omniverse Nucleus

端到端測試:
- Zigma NL -> BIMEntity -> USD -> Omniverse (視覺化)
- Zigma NL -> BIMEntity -> USD -> Revit (工程用)
- Zigma NL -> BIMEntity -> IFC (法規用)
- 三條管線獨立運作，共享同一個 Scene Graph

Build + ctest + pytest
更新 PROJECT_STATUS.md
git tag v3.0.0

## 依賴

| 項目 | 平台 | 說明 |
|------|------|------|
| pxr (OpenUSD) | macOS/Windows | pip install usd-core |
| ifcopenshell | macOS/Windows | pip install ifcopenshell |
| pyRevit / Revit API | Windows only | 需要 Revit 2024+ |
| Omniverse Kit | Windows only | NVIDIA Omniverse Launcher |
| Qt Quick 3D | macOS/Windows | 已有 (M1-MVP) |

## BUILD 鐵律

- CMake: C++ 絕對路徑 / QML 相對路徑
- USD: 用 pxr Python binding (不用 C++ USD SDK)
- Revit: 只在 Windows 上開發和測試
- IFC: 用 ifcopenshell Python library
- Omniverse: 用 omni.client Python API
