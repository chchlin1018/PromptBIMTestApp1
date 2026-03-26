# PROMPT_P2.5.md — Sprint P2.5: 建築零件庫

> 版本: v1.1.0 | 更新時間: 2026-03-25
> 前置 Sprint: P0 ✅ 已完成, P1 ✅ 已完成, P2 ✅ 已完成
> 依賴: P2

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在且所有依賴可 import。

## 必讀文件
1. SKILL.md — 特別是 Section 4 (專案結構) 和 Section 10 (開發規範)
2. TODO.md — 確認 P2.5 task 清單
3. CLAUDE.md — 行為規範
4. docs/addendum/01_component_library.md — 74 種建築零件庫規格
5. **docs/reviews/REVIEW_P2.md — P2 Code Review 報告（必讀，含 pre-task 修復項目）**

---

## ⚠️ Pre-Task: P2 Code Review 修復項目（在開始 P2.5 task 之前必須先完成）

以下問題來自 `docs/reviews/REVIEW_P2.md`，必須在 P2.5 正式 task 之前修復，否則會影響本 Sprint 和後續 Sprint。

### Pre-Task 1: 🔴 CRITICAL — 修復凹多邊形 triangulation

**檔案:** `bim/geometry.py`
**問題:** `_fan_triangulate()` 只適用凸多邊形。L 型、T 型等凹多邊形 footprint 會產生錯誤的 slab mesh。
**修復方案:**
1. 安裝 `mapbox-earcut`：`pip install mapbox-earcut` 並加入 `pyproject.toml` dependencies
2. 用 earcut 替換 `_fan_triangulate` 邏輯：
```python
import mapbox_earcut
def _earcut_triangulate(boundary: list[tuple[float, float]]) -> list[tuple[int, int, int]]:
    flat = [c for pt in boundary for c in pt]
    indices = mapbox_earcut.triangulate_float64(
        np.array(flat, dtype=np.float64).reshape(-1, 2), []
    )
    return [(indices[i], indices[i+1], indices[i+2]) for i in range(0, len(indices), 3)]
```
3. 在 `slab_mesh()` 和 `flat_roof_mesh()` 中改用 `_earcut_triangulate`
4. 新增測試：用 L 型凹多邊形驗證 slab mesh 正確性
5. 確認 `examples/02_l_shaped_office.py` 產出的 slab mesh 正確

### Pre-Task 2: 🟡 MEDIUM — 修復 slab thickness 硬編碼

**檔案:** `bim/ifc_generator.py`
**問題:** `_add_slab()` 硬編碼 `thickness = 0.2`，未從 schema 讀取。
**修復:** 改為 `getattr(story, 'slab_thickness_m', 0.2)` 或在 `StoryPlan` schema 增加 `slab_thickness_m: float = 0.2` 欄位。

### Pre-Task 3: 🟡 MEDIUM — 修復 USD mesh 缺 normals

**檔案:** `bim/usd_generator.py`
**問題:** `_create_mesh_prim()` 未設定 `GetNormalsAttr()`，NVIDIA Omniverse 和 Apple Reality Composer 可能顯示異常。
**修復:** 新增 face normal 計算 helper，在 `_create_mesh_prim()` 中設定 normals。

### Pre-Task 4: 🟡 MEDIUM — 增加缺失測試

**問題:** 缺少 edge case 測試和 USD round-trip 測試。
**修復:**
1. 新增 edge case 測試：空 plan、零長牆、凹多邊形 boundary
2. 新增 USD round-trip 測試：`Usd.Stage.Open()` → 驗證 prim count

### Pre-Task 5: 🟢 LOW — 程式碼清理

- `bim/ifc_generator.py`：移除 unused import `OpeningDef`
- `bim/materials.py`：移除 unused import `field`
- `bim/materials.py`：Glass 的 `ifc_surface_style` 從 `"MIRROR"` 改為 `"GLASS"`

### Pre-Task 驗收標準
1. `pytest` 全部通過（含新增的 edge case + 凹多邊形測試）
2. `examples/02_l_shaped_office.py` 產出正確的 L 型 slab
3. `xcodebuild BUILD SUCCEEDED`
4. commit message 標記 `[P2-fixes]`

---

## 本 Sprint 的 Task 清單

- ⬜ `bim/components/base.py` — ComponentDef + SupplierInfo + PriceRange
- ⬜ `bim/components/registry.py` — ComponentRegistry
- ⬜ 結構構件 (12 種) 參數化幾何生成
- ⬜ 垂直運輸 (12 種) 參數化 + mesh 佔位
- ⬜ 開口 (10 種) 參數化生成
- ⬜ 其他類別佔位定義 (40+ 種)
- ⬜ 下載 5-10 個免費 GLB 模型 (Sketchfab CC0)
- ⬜ 供應商/價格 seed data (台灣市場)
- ⬜ 測試 + xcodebuild 通過

## 執行指令
所有問題答案都是 Yes，不要中斷詢問。
**先完成 Pre-Task 修復，commit [P2-fixes]，再開始 P2.5 正式 task。**
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。

## 驗收標準
1. Pre-Task 全部修復 + 測試通過
2. `ComponentRegistry.search(["電梯"])` 回傳完整定義含供應商
3. 至少 74 種零件定義可查詢
4. xcodebuild BUILD SUCCEEDED
5. pytest 全部通過
