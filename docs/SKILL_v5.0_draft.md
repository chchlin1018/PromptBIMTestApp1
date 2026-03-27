# SKILL.md v5.0 Draft — For Michael's Review

> **Note:** This is a DRAFT. Claude Code does NOT directly modify SKILL.md.
> Michael should review and manually merge desired changes into SKILL.md.

---

## Proposed Additions for v5.0

### New Skills: Qt Quick 3D + C++

```yaml
- name: Qt Quick 3D BIM Rendering
  level: intermediate
  details:
    - QQuick3DGeometry for custom mesh (stride 24, pos+normal)
    - PBR materials: PrincipledMaterial (baseColor, roughness, metalness, opacity)
    - SceneEnvironment: MSAA High, Metal backend
    - OrbitCameraController + PerspectiveCamera presets
    - View3D.pick() for element selection
    - DirectionalLight (3-point lighting setup)

- name: Qt QML Architecture
  level: intermediate
  details:
    - QML_ELEMENT + Q_PROPERTY for C++/QML integration
    - Singleton pattern (pragma Singleton + set_source_files_properties)
    - SplitView + TabBar + StackLayout for panel layout
    - Shortcut {} for keyboard bindings
    - Canvas {} for custom drawing (pie charts, Gantt charts)
    - SequentialAnimation for splash/loading effects

- name: C++ QProcess Bridge
  level: intermediate
  details:
    - JSON stdio protocol (newline-delimited, QJsonDocument)
    - QProcess + readyReadStandardOutput for async communication
    - QTimer heartbeat with auto-restart on timeout
    - Crash recovery with reconnection and retry count
    - conda run integration for Python environment management
```

### New Skills: CMake + Build System

```yaml
- name: CMake Qt6 Build
  level: intermediate
  details:
    - qt_add_executable + qt_add_qml_module
    - target_include_directories for MOC header discovery
    - OUTPUT_NAME to avoid directory/executable collision
    - qt_standard_project_setup() for modern Qt6
    - enable_testing() + add_test() for ctest integration
```

### Updated Skills: USD I/O

```yaml
- name: USD ILOS Import/Export
  level: intermediate
  details:
    - pxr (OpenUSD): Usd.Stage, UsdGeom.Mesh, Sdf.ValueTypeNames
    - ILOS custom attributes (ilos:category, ilos:part_number, etc.)
    - Instance transform: final_xf = inst_xf × proto_inv × mesh_xf
    - Quad triangulation in importer
    - ConnectionPort extraction from child prims
    - to_json() serialization for C++ bridge
```

### Updated Skills: Mesh Generation

```yaml
- name: NumPy Mesh Generation
  level: intermediate
  details:
    - Box mesh: 8 vertices, 12 triangle faces
    - Normal computation: face normals accumulated per vertex
    - Stride 24 bytes: 3 pos + 3 normal × float32
    - Material mapping: element_type → material → PBR params
    - Color mapping: element_type → RGBA tuple
```

---

## Proposed Changes Summary

| Section | Change |
|---------|--------|
| C++ | Add Qt Quick 3D, QML Architecture, QProcess Bridge |
| Build | Add CMake Qt6 Build |
| USD | Update with ILOS import/export details |
| Mesh | Update with NumPy mesh generation |
| Testing | Add ctest + Qt Test patterns |

---

*SKILL.md v5.0 Draft — Generated 2026-03-28*
*For Michael's review and manual merge*
