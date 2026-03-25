# Code Review — Sprint P2: IFC + USD 生成核心

> **審查日期:** 2026-03-25
> **審查者:** Claude (Project Manager / Code Reviewer)
> **版本:** v0.2.0
> **測試結果:** 82 passed | xcodebuild BUILD SUCCEEDED
> **審查範圍:** `bim/geometry.py`, `bim/ifc_generator.py`, `bim/usd_generator.py`, `bim/materials.py`, `examples/`, `tests/test_bim/`

---

## 總評：⭐ 8.5 / 10 — 品質優良，POC 水準以上

P2 整體架構清晰，IFC 和 USD 各自封裝得當，完全符合 SKILL.md 的技術規範要求。測試覆蓋良好（34 個新測試），examples 可執行且包含 round-trip 驗證。以下逐檔分析。

---

## 1. `bim/geometry.py` — ✅ 優良

### 優點
- `Mesh` dataclass 乾淨，numpy array 帶完整 type hint (`np.ndarray` with shape comments)
- `wall_mesh` 零長牆防禦（`length < 1e-6` → 返回空 mesh），避免下游 division by zero
- `slab_mesh` fan triangulation 正確處理 winding order（底面反轉 normal 確保朝下）
- `gable_roof_mesh` 按 bounding box 最長軸自動選擇 ridge 方向，智能且合理
- 所有函式都有完整 docstring

### 問題

| 嚴重度 | 問題 | 說明 |
|:------:|------|------|
| 🔴 Critical | `_fan_triangulate` 只適用凸多邊形 | docstring 寫「works for convex and many concave polygons」，但 fan triangulation 對凹多邊形（如 L 型、T 型 footprint）會產生錯誤的三角形。`examples/02_l_shaped_office.py` 的 L 型 slab 可能已受影響。建議換成 `earcut` 或 `shapely.ops.triangulate`。 |
| 🟡 Medium | `gable_roof_mesh` 缺底面 | 兩個三角形面只蓋了斜面和山牆，從下方看是穿透的。對 3D 預覽影響不大，但 P6（5D 成本估算）體積計算會不準確。 |

### 建議修復
```python
# 替換 _fan_triangulate，使用 earcut 支援凹多邊形
# pip install mapbox-earcut
import mapbox_earcut
def _earcut_triangulate(boundary: list[tuple[float, float]]) -> list[tuple[int, int, int]]:
    flat = [c for pt in boundary for c in pt]
    indices = mapbox_earcut.triangulate_float64(
        np.array(flat, dtype=np.float64).reshape(-1, 2), []
    )
    return [(indices[i], indices[i+1], indices[i+2]) for i in range(0, len(indices), 3)]
```

---

## 2. `bim/ifc_generator.py` — ✅ 優良，完全符合規範

### 優點
- ✅ **100% 使用 `ifcopenshell.api.run()`** — 沒有任何低階 entity 操作，完全符合 SKILL.md [MANDATORY] 要求
- 正確的 IFC4 hierarchy：`IfcProject → IfcSite → IfcBuilding → IfcBuildingStorey → IfcWall/IfcSlab`
- 材質含 `IfcSurfaceStyleRendering` RGB colour
- `_placement_matrix` 4×4 矩陣正確處理 Z 軸旋轉 + XYZ 平移
- `_material_cache` dict 避免重複建立相同材質
- 牆的 representation 使用 `add_wall_representation`（長度+高度+厚度），符合 IFC best practice

### 問題

| 嚴重度 | 問題 | 說明 |
|:------:|------|------|
| 🟡 Medium | `_add_slab` 硬編碼 `thickness = 0.2` | 沒有從 `StoryPlan` 讀取。未來 schema 若加 `slab_thickness_m` 欄位，此處會被遺忘。建議改為 `story.slab_thickness_m if hasattr(story, 'slab_thickness_m') else 0.2`。 |
| 🟡 Medium | Roof assign 到 `self._building` | IFC 規範允許，但不常見。部分 IFC viewer（如 BIMcollab ZOOM）可能不顯示未 assign 到 storey 的構件。建議改為 assign 到最後一個 storey。 |
| 🟢 Low | `OpeningDef` import 未使用 | P2 scope 不含 openings，但 unused import 不乾淨。建議移除或加 `# noqa: F401` 註解。 |
| 🟢 Low | `self._file` 缺 None guard | type hint `ifcopenshell.file | None` 但沒有 `assert self._file is not None` 或 `if not self._file: raise`。目前靠呼叫順序保證（`_init_file` → `_create_project` → `_add_story`），但 fragile。 |

---

## 3. `bim/usd_generator.py` — ✅ 優良，完全符合規範

### 優點
- ✅ **只用 `pxr.Usd`, `UsdGeom`, `UsdShade`** — 符合 SKILL.md
- `UsdGeom.SetStageUpAxis(stage, Tokens.z)` + `SetStageMetersPerUnit(1.0)` — 正確的 Z-up + 公尺設定
- `UsdPreviewSurface` PBR shader 完整：diffuseColor / roughness / metallic / opacity
- `_safe_name` 處理 digit-prefix（`"1F"` → `"F1F"`）和特殊字元替換
- `MaterialBindingAPI` 正確 bind material 到 mesh prim
- Root prim `/Building` 設定 `kind = "assembly"` — 好的 USD 慣例

### 問題

| 嚴重度 | 問題 | 說明 |
|:------:|------|------|
| 🟡 Medium | Mesh 缺 normals | `UsdGeom.Mesh` 的 `GetNormalsAttr()` 未設定，靠 viewer 自動計算 face normals。大部分 DCC 工具能處理，但 **NVIDIA Omniverse** 和 **Apple Reality Composer** 可能顯示異常（全黑面或光照錯誤）。建議加 `_compute_face_normals()` helper。 |
| 🟢 Low | float64 → float32 精度降轉 | `geometry.py` 用 `np.float64`，`_create_mesh_prim` 轉成 `Gf.Vec3f`（float32）。建築尺度下精度損失可忽略，但不一致。 |
| 🟢 Low | 子層級 Xform 未設 `kind` | Root 設了 `"assembly"` 但 storey Xform 沒有設 `"group"`。Omniverse hierarchy 顯示可能不完整。 |

### 建議修復 — Normals
```python
def _compute_face_normals(mesh_data: Mesh) -> list[Gf.Vec3f]:
    """Compute per-face normals for a triangle mesh."""
    normals = []
    for tri in mesh_data.faces:
        v0, v1, v2 = mesh_data.vertices[tri]
        e1 = v1 - v0
        e2 = v2 - v0
        n = np.cross(e1, e2)
        length = np.linalg.norm(n)
        if length > 1e-10:
            n = n / length
        normals.extend([Gf.Vec3f(*n)] * 3)  # per-vertex (flat shading)
    return normals
```

---

## 4. `bim/materials.py` — ✅ 乾淨

### 優點
- 9 種材質定義完整，dual mapping（IFC surface style + USD PBR 參數）
- `wall_material` / `slab_material` / `roof_material` 工廠函式語意清楚
- Fallback to `"concrete"` 合理安全
- `MaterialDef` dataclass 整潔，欄位帶預設值

### 問題

| 嚴重度 | 問題 | 說明 |
|:------:|------|------|
| 🟢 Low | `field` import 未使用 | `from dataclasses import dataclass, field` — `field` 從未使用，建議移除。 |
| 🟢 Low | Glass 的 IFC surface style | `"MIRROR"` 不太合適。`IfcSurfaceStyleRendering.ReflectanceMethod` 應為 `"GLASS"` 或 `"TRANSPARENT"`，而非 `"MIRROR"`。不影響功能但語意不精確。 |

---

## 5. 測試品質 — ✅ 覆蓋良好

### 測試結構
```
tests/test_bim/
├── test_geometry.py      — wall/slab/roof mesh 生成
├── test_ifc_generator.py — IFC round-trip 驗證（8 test cases）
├── test_materials.py     — 材質查詢 + fallback
└── test_usd_generator.py — USD 生成驗證
```

### 優點
- IFC 測試做了完整 **round-trip 驗證**（generate → `ifcopenshell.open` → 查 entity type + count）
- Multi-storey case 有專門測試（2 storeys, 8 walls）
- 使用 pytest `tmp_path` fixture，不汙染 filesystem
- `simple_plan` fixture 可複用

### 問題

| 嚴重度 | 問題 | 說明 |
|:------:|------|------|
| 🟡 Medium | 缺 edge case 測試 | 無測試：空 plan（0 walls, 0 stories）、零長牆（length=0）、重複頂點 boundary、凹多邊形 boundary |
| 🟡 Medium | USD 缺 round-trip 測試 | IFC 有 `ifcopenshell.open` 驗證，但 USD 測試沒有 `Usd.Stage.Open` + prim count 驗證（只在 example 裡做了） |
| 🟢 Low | 每個 IFC test 重新 generate | 可改用 `@pytest.fixture(scope="module")` 共享生成結果，提升測試效率 |

---

## 6. Examples — ✅ 優良

### `01_simple_box.py`
- 乾淨的 end-to-end demo：10×8m 單層方盒
- IFC + USD 雙生成 + 雙 round-trip 驗證
- 良好的 docstring 和輸出訊息

### `02_l_shaped_office.py`
- 2 層 L 型辦公樓，展示多樓層能力
- ⚠️ 注意：如果 L 型 footprint 是凹多邊形，slab mesh 可能有 triangulation 錯誤（見 geometry.py 問題）

---

## 📋 修復優先級總表

| 優先 | 檔案 | 問題 | 影響 | 建議修復時機 |
|:----:|------|------|------|:-----------:|
| 🔴 | `geometry.py` | fan triangulation 不支援凹多邊形 | L/T 型建築 slab mesh 錯誤 | **P2.5 或 P3 之前** |
| 🟡 | `ifc_generator.py` | slab thickness 硬編碼 0.2 | schema 擴充時遺漏 | P2.5 |
| 🟡 | `usd_generator.py` | mesh 缺 normals | Omniverse/Reality Composer 顯示異常 | P3 |
| 🟡 | `ifc_generator.py` | Roof assign 到 building 而非 storey | 部分 IFC viewer 不顯示 | P3 |
| 🟡 | `tests/` | 缺 edge case + USD round-trip 測試 | 測試覆蓋不完整 | P2.5 |
| 🟢 | `ifc_generator.py` | unused import `OpeningDef` | 程式碼衛生 | 隨時 |
| 🟢 | `materials.py` | unused import `field` | 程式碼衛生 | 隨時 |
| 🟢 | `materials.py` | Glass IFC style 應為 GLASS 非 MIRROR | 語意不精確 | 隨時 |
| 🟢 | `usd_generator.py` | float64→float32 精度降轉 | 理論問題，實務無害 | Low priority |
| 🟢 | `usd_generator.py` | 子層級 Xform 未設 kind | Omniverse hierarchy 不完整 | P3 |

---

## 結論

Sprint P2 的程式碼品質紮實，架構設計對後續 Sprint 擴展友好。**最需要優先處理的是凹多邊形 triangulation 問題**，因為 P2.5（建築零件庫）和 P3（3D 預覽）都會遇到非矩形的 footprint。其餘為中低優先級的改善項目。

### CLAUDE.md 合規性：✅ 全部通過
- [x] xcodebuild BUILD SUCCEEDED
- [x] pytest 82 passed
- [x] TODO.md 已更新
- [x] CHANGELOG.md v0.2.0 已記錄
- [x] PROMPT_P2.5.md 已建立
- [x] git commit + push 完成
