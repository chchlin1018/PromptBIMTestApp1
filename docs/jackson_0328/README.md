# Jackson 0328 — 外部夥伴技術文件

> **日期:** 2026-03-28
> **來源:** 外部夥伴 (Jackson)
> **用途:** ILOS + USD→Revit 整合參考

## 文件清單

| 文件 | 版本 | 說明 |
|------|------|------|
| ILOS_USD_Asset_Vendor_Spec.md | v2.1 | 廠商 USD 資產規格 — 所有廠商統一結構 |
| USD_Revit_Convert.md | v2.0 | USD→Revit 轉換 Pipeline — 兩層架構 (DirectShape + MEP Native) |
| USD_to_Revit_System_Architecture.md | v1.1 | 系統架構 — ILOS-FAB 到 Revit BIM 全流程 |

## 與 Zigma PromptToBuild 的關係

這三份文件定義了外部夥伴模組的技術規格，將來整合到 Zigma 平台中：

- **ILOS Vendor Spec** → Zigma 的 `io_usd` Plugin 需要能讀取 ilos: metadata
- **USD→Revit Converter** → 整合為 Zigma 的 `io_revit` Plugin (IIOPlugin)
- **System Architecture** → 定義了 W1 工作流 (ILOS USD → Zigma → Revit)

參見: `docs/architecture/Zigma_OCCT_QtQuick3D_Migration_Plan_v1.0.md`
