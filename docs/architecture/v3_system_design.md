# PromptBIM v3.0 — 系統設計文件

> **版本:** v1.0 | **日期:** 2026-03-26
> **架構決策:** 方案 C — Hydra Storm + PyVista 混合渲染
> **目標平台:** Windows (RTX 4090) + macOS

---

## 1. 設計原則

- **100% 開源** — 零商業軟體依賴
- **Python 核心不動** — 既有 agents/bim/land/cache 完全保留
- **可插拔渲染** — VTK (工程) + Hydra Storm (品質) 雙後端
- **跨平台 GUI** — PySide6 為唯一 GUI 框架
- **OpenUSD 原生** — 直接用 pxr API，不經過中間格式轉換

---

## 2. 三層渲染架構

### Tab 1: 2D 地籍 (matplotlib)
- FigureCanvas 嵌入 QWidget
- 土地輪廓 + 建築 footprint + 退縮線 + 面積標注
- 不變，跨平台完全相容

### Tab 2: 3D 工程預覽 (PyVista + QVTKOpenGLNativeWidget)
- VTK 9.x 底層，PyVista 高階封裝
- QVTKOpenGLNativeWidget 嵌入 PySide6
- 用途：快速預覽、剖面分析、量測、wireframe
- RTX 4090 自動 GPU 加速（VTK OpenGL backend）

### Tab 3: USD 品質渲染 (Hydra Storm + QOpenGLWidget) ★新增★
- Pixar Hydra Storm 渲染器（OpenUSD 內建）
- UsdImagingGL.Engine 直接渲染 .usda 場景
- PBR 材質 (UsdPreviewSurface)
- 環境光 (Dome Light + HDRI)
- 原生理解 USD Prim 階層 → 點選即可查詢屬性

---

## 3. 訊息通訊架構

```
ChatPanel.chat_submitted(str)
  → MainWindow._on_chat_submitted(text)
    → AgentWorker(QThread).start(text, land, zoning)
      → orchestrator.agenerate()  [asyncio in QThread]
        ├─ Agent 1 Enhancer (async)
        ├─ Agent 2 Planner  (async)
        ├─ Agent 3 Builder  (sync)
        └─ Agent 4 Checker  (async)
      → emit generation_complete(PBResult)
    → MapView.update_footprint()        [2D]
    → VTKView.load_mesh()               [3D VTK]
    → UsdView.load_stage(usda_path)     [3D Hydra] ★
    → PropertyPanel.update()

UsdView.prim_selected(str)
  → PropertyPanel.show_prim_properties()
  → ProjectTree.highlight_prim()
```

---

## 4. OpenUSD 整合層 (新增模組)

### 4.1 UsdSceneRenderer (bim/usd_scene.py)
```python
class UsdSceneRenderer:
    def load_stage(self, usda_path: str) -> Usd.Stage
    def setup_hydra(self, gl_widget: QOpenGLWidget) -> UsdImagingGL.Engine
    def render_frame(self, camera: Gf.Matrix4d, viewport: Gf.Vec4d)
    def pick_prim(self, x: int, y: int) -> str | None
    def set_render_params(self, lighting=True, materials=True)
```

### 4.2 UsdViewWidget (gui/usd_view.py)
```python
class UsdViewWidget(QOpenGLWidget):
    prim_selected = Signal(str)
    def initializeGL(self)    # Hydra Engine init
    def paintGL(self)         # render_frame() 每幀
    def resizeGL(self, w, h)  # viewport 更新
    def mousePressEvent(self) # 點選 → pick_prim
    def mouseMoveEvent(self)  # ArcballCamera 旋轉
    def wheelEvent(self)      # 縮放
```

### 4.3 ArcballCamera (bim/usd_camera.py)
```python
class ArcballCamera:
    def rotate(self, dx, dy)      # 軌道旋轉
    def zoom(self, delta)          # 滾輪縮放
    def pan(self, dx, dy)          # 中鍵平移
    def focus_on(self, bbox)       # 飛到指定 Prim
    def get_view_matrix(self) -> Gf.Matrix4d
    def get_projection_matrix(self, aspect) -> Gf.Matrix4d
    def set_preset(self, name: str)  # top/front/right/perspective
```

### 4.4 BIM PBR 材質庫 (bim/usd_materials.py)
```python
MATERIAL_LIBRARY = {
    "concrete":  {"diffuseColor": (0.65, 0.65, 0.62), "roughness": 0.85},
    "glass":     {"diffuseColor": (0.85, 0.92, 0.95), "roughness": 0.05, "opacity": 0.3},
    "steel":     {"diffuseColor": (0.75, 0.75, 0.78), "roughness": 0.35, "metallic": 0.9},
    "wood":      {"diffuseColor": (0.55, 0.35, 0.18), "roughness": 0.75},
    "tile":      {"diffuseColor": (0.90, 0.88, 0.82), "roughness": 0.40},
}

def create_pbr_material(stage, name, params) -> UsdShade.Material
def bind_material(prim, material) -> None
```

---

## 5. C++ Core 架構 (P28+)

### 5.1 目錄結構
```
cpp/
├── CMakeLists.txt              # C++ 核心 library
├── src/
│   ├── compliance_engine.h     # 法規引擎介面
│   ├── compliance_engine.cpp
│   ├── cost_engine.h           # 成本估算介面
│   └── cost_engine.cpp
├── bindings/
│   └── pybind_module.cpp       # pybind11 → Python
└── tests/
    ├── test_compliance.cpp     # GoogleTest
    └── test_cost.cpp
```

### 5.2 Build System
- **Windows:** Visual Studio 2025 + CMake + vcpkg
- **macOS:** Clang + CMake + vcpkg
- **CMakePresets.json** 提供 VS2025 一鍵開啟

---

## 6. 依賴矩陣

| 依賴 | License | 用途 | Win | Mac |
|------|---------|------|:---:|:---:|
| PySide6 ≥6.6 | LGPL-3.0 | GUI | ✅ | ✅ |
| PyVista ≥0.43 | MIT | 3D VTK | ✅ | ✅ |
| vtk ≥9.3 | BSD | QVTKWidget | ✅ | ✅ |
| usd-core ≥24.0 | Apache-2.0 | OpenUSD + Hydra | ✅ | ✅ |
| IfcOpenShell ≥0.8 | LGPL-3.0 | IFC 生成 | ✅ | ✅ |
| anthropic ≥0.40 | MIT | Claude API | ✅ | ✅ |
| geopandas ≥0.14 | BSD-3 | GIS | ✅ | ✅ |
| shapely ≥2.0 | BSD-3 | 幾何 | ✅ | ✅ |
| qasync ≥0.27 | BSD | asyncio↔Qt | ✅ | ✅ |
| pybind11 ≥2.12 | BSD | C++↔Python | ✅ | ✅ |

---

*v3 System Design v1.0 | 2026-03-26 | Reality Matrix Inc.*
