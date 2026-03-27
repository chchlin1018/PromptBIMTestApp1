# PromptToBuild 合作夥伴介面規格書

> **版本:** v1.0 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **性質:** 合作夥伴技術介面規格 — 外部 Python 模組如何整合進 Plugin 架構
> **機密等級:** 合作夥伴限閱

---

## 1. 文件目的

定義 PromptToBuild 平台與外部合作夥伴提供的 Python 模組之間的技術介面規格。

目標：
1. 明確「夥伴交付什麼」vs「平台消費什麼」的邊界
2. 定義 Plugin 介面合約，讓夥伴程式碼可插拔整合
3. 規劃 Python 原始碼保護策略（Cython → C++）
4. 建立溝通清單，確保雙方對介面理解一致

---

## 2. 合作夥伴模組總覽

| 模組 | 來源 | 語言 | 功能 | Plugin 介面 | 預計到位 |
|------|------|------|------|------------|---------|
| **ILOS Layout Engine** | 外部夥伴 | Python | 設備佈局優化 + 管路路由 | IEnginePlugin | Phase 3 (P34+) |
| **ILOS Piping Router** | 外部夥伴 | Python | 跨樓層管路 A* 路由 + 碰撞 | IEnginePlugin | Phase 3 (P34+) |
| **USD↔Revit Converter** | 外部夥伴 | Python | 雙向 USD ↔ Revit 轉換 | IIOPlugin | Phase 2 (P30+) |

---

## 3. 原始碼保護策略

### 3.1 問題

夥伴交付 Python 原始碼，但產品發布時不能暴露明文。
Python .py 可直接閱讀；.pyc 可被 uncompyle6 輕易反編譯。

### 3.2 三階段保護路徑

| 階段 | 方法 | 保護程度 | 效能 | 時機 |
|------|------|:-------:|------|------|
| **Stage 1** | Cython 編譯 → .so/.pyd | ★★★★ | 接近 C | 收到 Python 後立即 |
| **Stage 2** | Nuitka → 單一執行檔 | ★★★★★ | 原生速度 | 產品發布前 |
| **Stage 3** | 完全 C++ 改寫 | ★★★★★ | 最佳 | 長期（視需求） |

### 3.3 Cython 編譯流程（推薦首選）

```
夥伴交付: ilos_layout_engine.py
                ↓ Cython 編譯
            cythonize -i ilos_layout_engine.py
                ↓
產出: ilos_layout_engine.cpython-311-x86_64-linux-gnu.so
      (二進位，無法反編譯回可讀 Python)
                ↓
封裝為: engine_ilos_layout.so (IEnginePlugin)
                ↓
PromptToBuild Plugin Bus 動態載入
```

---

## 4. ILOS Layout Engine 介面規格

### 4.1 輸入（PromptToBuild → ILOS）

| 資料 | 格式 | 說明 |
|------|------|------|
| 建築平面 | USD Stage path | /World/Levels/ 含樓層定義 |
| 設備清單 | JSON array | IADL AssetType（含 ilos: metadata） |
| 約束條件 | JSON object | 間距/振動/潔淨度/樓層指派 |
| 廠商資產庫 | string path | 指向 Vendor USD 目錄 |

### 4.2 輸出（ILOS → PromptToBuild）

| 資料 | 格式 | 說明 |
|------|------|------|
| 優化後 USD Scene | .usd 檔案路徑 | 設備位置 + 管路路由 |
| 設備 Prim | USD + ilos: metadata | 必須有 category, part_number, level |
| 管路 Prim | USD + ilos: metadata | 必須有 connection_start/end, diameter, system |
| /Connections/ | USD Xform prims | 符合 ilos: spec v2.1 |
| 佈局報告 | JSON | 碰撞結果、約束違規、優化分數 |

### 4.3 Python 函式簽名（合約）

```python
class ILOSLayoutEngine:
    def optimize_layout(
        self,
        usd_stage_path: str,
        equipment_list: list[dict],
        constraints: dict,
        vendor_asset_dir: str,
    ) -> LayoutResult: ...

class ILOSPipingRouter:
    def route_piping(
        self,
        usd_stage_path: str,
        piping_systems: list[str],   # ["UPW", "CDA", "PCW"]
        constraints: dict,
    ) -> PipingResult: ...

@dataclass
class LayoutResult:
    output_usd_path: str
    equipment_count: int
    collision_count: int              # 應為 0
    constraint_violations: list[str]
    optimization_score: float         # 0.0 ~ 1.0
    report_json: dict

@dataclass
class PipingResult:
    output_usd_path: str
    pipe_segments: int
    fittings: int
    total_length_m: float
    report_json: dict
```

### 4.4 ilos: metadata 必要欄位

**設備 Prim:**
```
ilos:category = "Equipment"          # 必填
ilos:part_number = "ASML-NXE3400-C"  # 必填
ilos:manufacturer = "ASML"           # 必填
ilos:level = "FL3"                   # 必填 — ILOS 放置時指派
ilos:weight_kg = 17000.0             # 必填
```

**管路 Prim:**
```
ilos:category = "Pipe"               # 必填
ilos:connection_start = [x, y, z]    # 必填 — cm
ilos:connection_end = [x, y, z]      # 必填 — cm
ilos:nominal_diameter = 50.8         # 必填 — mm
ilos:piping_system = "UPW"           # 必填
ilos:material = "SS316L"             # 必填
ilos:level = "FL3"                   # 必填
```

---

## 5. USD↔Revit Converter 介面規格

### 5.1 Python 函式簽名（合約）

```python
class USDRevitConverter:
    def usd_to_revit(
        self,
        usd_path: str,
        mcp_endpoint: str,
        config: dict,
    ) -> ConversionResult: ...

    def revit_to_usd(
        self,
        mcp_endpoint: str,
        output_usd_path: str,
        mode: str,  # "full_export" | "incremental_sync"
    ) -> SyncResult: ...

    def start_live_sync(
        self,
        mcp_endpoint: str,
        usd_stage_path: str,
        on_change_callback: Callable,
    ) -> SyncSession: ...
```

### 5.2 已驗證的 POC 技術約束（Converter 必須遵守）

| 約束 | 說明 |
|------|------|
| Instance 解析 | 必須使用 inst_xf × proto_inv × mesh_xf |
| 單位換算 | USD(cm) × 0.01 / 0.3048 = Revit(ft) |
| Transaction | 不可建立明確 Transaction（MCP 自動包裝） |
| 材質 | 必須建立 Material 並指派（否則全黑） |
| DisplayStyle | 必須在獨立 MCP 呼叫中設定 Realistic |
| 退化三角形 | 跳過距離 < 0.0001 ft 的三角形 |
| 批次大小 | 30 mesh/batch for MCP 穩定性 |

---

## 6. Plugin 封裝規格

```
夥伴交付:                     平台封裝:

ilos_layout_engine.py    →    engine_ilos_layout.so (IEnginePlugin)
ilos_piping_router.py    →    engine_ilos_piping.so (IEnginePlugin)
usd_revit_converter.py   →    io_revit.so (IIOPlugin)
```

平台負責在夥伴 Python 外面包 C++ Plugin wrapper（libpython embedding + Cython .so）。

---

## 7. 與合作夥伴溝通清單

### 7.1 需要夥伴確認的事項

| # | 問題 | 影響 | 優先度 |
|---|------|------|:------:|
| 1 | Python 最低版本？ | Cython 相容性 | 🔴 高 |
| 2 | 第三方 pip 套件清單？ | 封裝打包 | 🔴 高 |
| 3 | 是否使用 NumPy/SciPy/PyTorch？ | Cython 策略 | 🔴 高 |
| 4 | 同意 §4.3 ILOS 函式簽名？ | 介面合約 | 🔴 高 |
| 5 | 同意 §4.4 ilos: metadata 必要欄位？ | 資料合約 | 🔴 高 |
| 6 | 同意 §5.1 Converter 函式簽名？ | 介面合約 | 🔴 高 |
| 7 | 同意 §5.2 POC 技術約束？ | 避免重蹈覆轍 | 🔴 高 |
| 8 | 預計交付時間表？ | Phase 2/3 排程 | 🟡 中 |
| 9 | 接受 Cython 編譯保護？ | 保護策略 | 🟡 中 |
| 10 | 願意後續逐步改寫 C++？ | 長期路線 | 🟢 低 |

### 7.2 需要平台提供給夥伴的資料

| # | 資料 | 說明 |
|---|------|------|
| 1 | ILOS_Test_Pipeline_v4.usda | 測試 USD（含 ilos: metadata） |
| 2 | ILOS_USD_Asset_Vendor_Spec.md v2.1 | 廠商 USD 規格書 |
| 3 | USD_to_Revit_System_Architecture.md | 系統架構（含 POC 驗證結果） |
| 4 | USD_Revit_Convert.md | SOP + 可重複執行 Checklist |
| 5 | IEnginePlugin / IIOPlugin C++ header | Plugin 介面定義 |
| 6 | 範例 Plugin 原始碼 | engine_compliance_tw 作為參考 |
| 7 | Revit MCP 測試環境存取 | Windows RTX 4090 |

---

## 8. 時程與里程碑

| 里程碑 | Sprint | 前提 | 交付物 |
|--------|--------|------|--------|
| 介面合約簽定 | P26 前 | 雙方同意 §4/§5 | 簽名確認文件 |
| Mock Plugin 驗證 | P26-P29 | 平台用 stub 驗證介面 | engine_ilos_mock.so 通過 E2E |
| Converter Python 到位 | P30 | 夥伴交付 | 整合測試通過 |
| ILOS Python 到位 | P34 | 夥伴交付 | 整合測試通過 |
| Cython 編譯驗證 | P34+1 | 確認 .so 功能一致 | 二進位 Plugin 通過全部測試 |
| C++ 改寫評估 | P42+ | 效能數據 + 業務需求 | 決策文件 |

---

*PromptToBuild 合作夥伴介面規格書 v1.0*
*Reality Matrix Inc. | 2026-03-27*
