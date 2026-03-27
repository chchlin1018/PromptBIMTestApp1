# PromptToBuild 合作夥伴介面規範 v1.0

> **版本:** v1.0 | **日期:** 2026-03-27
> **作者:** Michael Lin（林志錚）| Reality Matrix Inc.
> **性質:** 合作夥伴技術介面規範 — 定義外部模組整合的介面合約與程式碼保護策略
> **對象:** ILOS 佈局引擎團隊 · USD↔Revit 轉換器團隊

---

## 1. 文件目的

PromptToBuild 平台有兩個關鍵模組來自外部合作夥伴：

| 模組 | 來源 | 語言 | 狀態 | 整合介面 |
|------|------|------|------|---------|
| **ILOS 佈局引擎** | 外部合作夥伴 | Python | 開發中，數月後交付 | IEnginePlugin |
| **USD↔Revit Converter** | 外部合作夥伴 | Python | POC 已驗證 | IIOPlugin |

**兩個共同需求：**
1. Python 原始碼不能被最終用戶看到（IP 保護）
2. 必須透過 PromptToBuild 的 Plugin 介面整合

---

## 2. 程式碼保護策略

### 2.1 問題：Python 是明文語言

Python .py 和 .pyc 都可被輕易反編譯，無法保護商業 IP。

### 2.2 保護方案比較

| 方案 | 保護程度 | 難度 | 效能 | 推薦度 |
|------|:-------:|:---:|:---:|:------:|
| **Cython → .so/.pyd** | ★★★★ | 中 | 接近 C | ✅ 第一選擇 |
| **Nuitka → 單一執行檔** | ★★★★★ | 中 | 好 | ✅ 備選 |
| PyArmor 加密 | ★★★ | 低 | 原速 | ⚠️ 可被破解 |
| 完全改寫 C++ | ★★★★★ | 極高 | 最佳 | ⚠️ 長期目標 |

### 2.3 推薦路徑：三階段保護

**階段 1（立即）：Cython 編譯**
```
合作夥伴提供 Python → Cython 編譯為 .so/.pyd → 只發布二進位
```

**階段 2（中期）：Nuitka 打包**
```
進一步將整個模組編譯為單一 .so/.pyd → 更難反編譯
```

**階段 3（長期）：C++ 重寫核心**
```
效能關鍵路徑（A* 路由、幾何轉換）用 C++ 重寫
```

### 2.4 建置流程

```
合作夥伴提供:               我方建置:                  最終發布:
ilos_layout.py        →   Cython 編譯             →  engine_ilos_layout.so
ilos_piping.py        →   cythonize + gcc/msvc    →  engine_ilos_piping.so
usd_revit_convert.py  →   Cython 編譯             →  io_revit_converter.so
                           ↓
                      CMake 整合到 PromptToBuild
                      Plugin Bus 動態載入
```

---

## 3. ILOS 佈局引擎介面規範

### 3.1 介面合約：IEnginePlugin

ILOS 引擎必須實作 `IEnginePlugin` 介面。合作夥伴用 Python 實作，我方透過 libpython embedding 或 Cython 載入。

### 3.2 Python 介面定義（合作夥伴需實作）

```python
class ILOSLayoutEngine:
    """ILOS 佈局引擎 — 合作夥伴需實作此介面"""

    def initialize(self, config: dict) -> bool:
        """初始化引擎，載入資產庫"""
        pass

    def optimize_layout(
        self,
        equipment_list: list[dict],  # 設備清單 (IADL AssetType)
        floor_plan: dict,            # 樓層定義 (FDL)
        constraints: dict,           # 約束條件
    ) -> dict:
        """設備佈局優化

        Returns: {
            'placements': [
                {
                    'asset_type_id': 'ASML_NXE3400',
                    'position': [x, y, z],  # cm
                    'rotation': [rx, ry, rz],  # degrees
                    'level': 'FL3',
                    'ilos_metadata': {
                        'category': 'Equipment',
                        'part_number': 'EQP_LITHO_EUV_NXE3400',
                        'clearance_front_mm': 2000,
                        ...
                    }
                }
            ],
            'score': 0.87,
            'violations': []
        }
        """
        pass

    def shutdown(self) -> None:
        pass


class ILOSPipingEngine:
    """ILOS 管路路由引擎 — 合作夥伴需實作此介面"""

    def route_piping(
        self,
        connections: list[dict],  # 連接需求
        obstacles: list[dict],    # 障礙物
        floor_plan: dict,         # 樓層 + 穿越點
    ) -> dict:
        """管路自動路由

        Returns: {
            'pipes': [
                {
                    'pipe_id': 'UPW-3F-001-P01',
                    'connection_start': [x1, y1, z1],  # cm
                    'connection_end': [x2, y2, z2],     # cm
                    'nominal_diameter': 50.8,  # mm
                    'material': 'SS316L',
                    'piping_system': 'UPW',
                    'level': 'FL3',
                    'ilos_metadata': { ... }
                }
            ],
            'fittings': [
                {
                    'type': 'Elbow',
                    'position': [x, y, z],
                    'angle_deg': 90,
                    ...
                }
            ]
        }
        """
        pass
```

### 3.3 輸入/輸出資料格式

**輸入：JSON Schema**
- equipment_list: IADL AssetType 清單（ilos: spec v2.1）
- floor_plan: FDL 樓層定義（FL1/FL2/FL3 高程 + 邊界）
- constraints: 間距/振動/潔淨度/管路系統約束

**輸出：JSON → USD**
- placements → USD /World/Equipment/ 下的 Prim + ilos: metadata
- pipes → USD /World/Piping/ 下的 Prim + ilos: connection_start/end
- fittings → USD /World/Piping/ 下的 PipeFitting Prim

### 3.4 關鍵約束：NDH 可活化

> **每個輸出的 ilos: metadata 都必須包含 NDH 綁定所需欄位，確保 PromptToOperate 可以直接活化為 Asset Servant。**

必須欄位：
- `ilos:category` — 設備類別
- `ilos:part_number` — 料號
- `ilos:manufacturer` — 廠商
- `/Connections/` — 連接點（含 port_type, port_medium, port_size_mm）
- `ilos:level` — 樓層
- `ilos:piping_system` — 管路系統

---

## 4. USD↔Revit Converter 介面規範

### 4.1 介面合約：IIOPlugin

轉換器必須實作 `IIOPlugin` 介面，支援雙向轉換。

### 4.2 Python 介面定義（合作夥伴需實作）

```python
class USDRevitConverter:
    """USD↔Revit 轉換器 — 合作夥伴需實作此介面"""

    def initialize(self, config: dict) -> bool:
        """初始化轉換器，連接 Revit MCP"""
        pass

    # === USD → Revit ===

    def usd_to_revit_equipment(
        self, usd_prims: list[dict]
    ) -> dict:
        """Layer 1: 設備 → DirectShape / Adaptive Component"""
        pass

    def usd_to_revit_piping(
        self, usd_prims: list[dict]
    ) -> dict:
        """Layer 2: 管路 → Pipe.Create + NewElbowFitting"""
        pass

    def usd_to_revit_structure(
        self, usd_prims: list[dict]
    ) -> dict:
        """Layer 3: 結構 → Revit Column/Beam/Floor"""
        pass

    # === Revit → USD ===

    def revit_to_usd_sync(
        self, changed_elements: list[dict]
    ) -> dict:
        """增量回寫：Revit 變更 → USD Prim 更新"""
        pass

    def shutdown(self) -> None:
        pass
```

### 4.3 已驗證的技術要點（合作夥伴必須遵循）

**Instance 解析：** `final_xf = inst_xf × proto_inv × mesh_xf`（手動計算，不依賴 XformCache）

**單位換算：** USD(cm) × 0.01 / 0.3048 = Revit(ft)

**Revit MCP 規則：**
- 不可建立 Transaction（MCP 自動包裝）
- 必須建立 Material（否則全黑）
- DisplayStyle.Realistic 須在獨立 MCP 呼叫中設定
- 批次大小 ≤ 30 meshes

**三層轉換（已 POC 驗證）：**

| Layer | USD 內容 | Revit 目標 | 狀態 |
|-------|---------|-----------|------|
| L1 | Equipment | DirectShape → Adaptive Comp. | v1 ✅ |
| L2 | Piping | Pipe.Create + Elbow | ✅ 驗證 |
| L3 | Structure | Column/Beam/Floor | 待開發 |

---

## 5. 整合時程

| 階段 | 時間 | ILOS 引擎 | USD↔Revit Converter |
|------|------|----------|---------------------|
| P26-P29 | 現在~+2月 | **Mock Stub**（模擬資料） | **Mock Stub** |
| P30-P33 | +2~4月 | Mock + 介面驗證 | POC Python 整合 |
| **P34** | **+4月** | **★ 收到 Python → Cython → Plugin** | **Cython → Plugin** |
| P35-P37 | +6月 | 廠商資產 + Omniverse | 雙向 Sync 完整化 |
| P42-P44 | +10月 | 評估 C++ 重寫核心 | 評估 C++ 重寫核心 |

### Mock Stub 策略（P26-P29）

ILOS 尚未到貨前，我方用 Mock Plugin 驗證介面：

```python
class MockILOSLayout(ILOSLayoutEngine):
    """模擬 ILOS 佈局引擎，用於介面驗證"""
    def optimize_layout(self, equipment_list, floor_plan, constraints):
        return load_mock_placements('test_fixtures/mock_layout.json')
```

確保 P26 的介面設計基於真實資料結構，不是空想。

---

## 6. 合作夥伴溝通清單

### 6.1 需與 ILOS 團隊確認

- [ ] ILOS Python 預計交付時間？
- [ ] ILOS 依賴哪些 Python 套件？（numpy/scipy/其他？）
- [ ] ILOS 是否有自己的 USD 讀寫邏輯？還是只輸出 JSON？
- [ ] ILOS 輸出的 ilos: metadata 格式是否與 spec v2.1 一致？
- [ ] ILOS 是否支援非同步處理？（大型場景可能需幾分鐘）
- [ ] ILOS 的授權模式？（Runtime license? Per-seat? Per-project?）
- [ ] 我方可否對原始碼做 Cython 編譯？
- [ ] ILOS 團隊是否有計劃遷移到 C++？

### 6.2 需與 USD↔Revit Converter 團隊確認

- [ ] Converter 目前的 Python 版本和依賴？
- [ ] Converter 是否直接操作 Revit MCP？還是輸出 JSON 由我方操作？
- [ ] 回寫（Revit→USD）的範圍？只有管路？還是包含設備和結構？
- [ ] Converter 對 USD Instance 的處理方式？是否用 inst_xf×proto_inv×mesh_xf？
- [ ] 我方可否對原始碼做 Cython 編譯？
- [ ] 是否有計劃遷移到 C++？

### 6.3 合作夥伴需在 P34 前提供

| 交付物 | 說明 | 格式 |
|--------|------|------|
| Python 原始碼 | 佈局優化 + 管路路由 / 轉換器 | .py |
| 依賴清單 | pip requirements.txt | .txt |
| 單元測試 | pytest 測試案例 | .py |
| 範例輸入/輸出 | JSON 測試資料 | .json |
| API 文件 | 函數簽名 + 參數說明 | .md |

---

*PromptToBuild 合作夥伴介面規範 v1.0*
*Reality Matrix Inc. | 2026-03-27*
