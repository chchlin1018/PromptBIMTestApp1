# USD to Revit System Architecture

> ILOS-FAB Pipeline: From Omniverse Layout Optimization to Revit BIM Construction Documents

---

## 1. Document Purpose

This document defines the **system architecture** for converting USD scenes (produced by ILOS layout optimization in NVIDIA Omniverse) into editable Revit BIM models suitable for construction document output, regulatory submission, and contractor procurement.

---

## 2. End-to-End Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ILOS-FAB Platform                             │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────────────────┐ │
│  │  ILOS Asset   │    │  Omniverse   │    │   ILOS Optimization    │ │
│  │  Library      │───→│  USD Scene   │───→│   Engine               │ │
│  │              │    │              │    │   (Layout + Routing)   │ │
│  │  Vendor USD  │    │  Assembled   │    │                        │ │
│  │  + Metadata  │    │  Fab Layout  │    │  Output: Optimized USD │ │
│  └──────────────┘    └──────┬───────┘    └────────────────────────┘ │
│                             │                                        │
│                    ┌────────▼────────┐                               │
│                    │  USD-to-Revit   │                               │
│                    │  Converter      │  ← THIS DOCUMENT             │
│                    └────────┬────────┘                               │
│                             │                                        │
│              ┌──────────────┼──────────────┐                        │
│              ▼              ▼              ▼                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │
│  │ Revit BIM    │ │ BOM Cost     │ │ IFC Export   │               │
│  │ (Editable)   │ │ (SAP/ERP)   │ │ (Regulatory) │               │
│  │              │ │              │ │              │               │
│  │ → 施工圖     │ │ → 採購單     │ │ → 送審文件   │               │
│  │ → 發包       │ │ → 成本估算   │ │ → 法規合規   │               │
│  └──────────────┘ └──────────────┘ └──────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Conversion Path Decision History

### 3.1 Path A: USD → IFC → Revit (ABANDONED)

```
USD → Python (ifcopenshell) → IFC4 / IFC2x3 → Revit Open/Link IFC
```

**Status: ABANDONED after POC failure**

| Issue | Detail |
|-------|--------|
| IFC4 partial support | Revit 2026 warns "IFC 版本 4 只有部分受到支援" |
| Geometry not rendered | DirectShape elements exist in Revit but display as invisible |
| Brep geometry failure | IfcFacetedBrep geometry created by ifcopenshell not rendered by Revit |
| Unit mismatch | Blender meters stored as IFC millimeters → microscopic objects |
| IFC2x3 OwnerHistory | Schema differences require manual OwnerHistory creation |

**Conclusion:** IFC is suitable for regulatory submission (output), but NOT as a conversion intermediate format for geometry transfer.

### 3.2 Path B: USD → Revit API DirectShape (VALIDATED — Layer 1)

```
USD → Python (usd-core) → JSON (vertices + triangles) → Revit MCP → DirectShape
```

**Status: VALIDATED for equipment and complex geometry**

| Validation | Result |
|------------|--------|
| Factory Building (Revit → USD) | ✅ 92 meshes, complete building |
| KUKA Robot Arm (STEP → USD) | ✅ 114 meshes, 561K vertices, correct assembly |
| Car Lift (SolidWorks → USD) | ✅ 146 meshes, perfect match |
| City Demo (CityEngine → USD) | ✅ 913 buildings, large-scale scene |

**Limitation:** DirectShape is NOT editable — cannot modify dimensions, cannot produce parametric construction documents.

**Decision: DirectShape is NOT the target solution.** It was used to validate geometry transfer feasibility, but the project goal requires editable BIM elements. DirectShape is only acceptable as a **temporary fallback** for equipment that does not need parametric editing (move/rotate only). The long-term target for equipment is Adaptive Component or Equipment Family.

### 3.3 Path C: USD → Revit MEP Native Elements (VALIDATED — Layer 2)

```
USD (ilos: metadata) → Python → Revit MEP API → Pipe.Create() + NewElbowFitting()
```

**Status: VALIDATED for piping systems**

| Validation | Result |
|------------|--------|
| Single-floor pipeline (4 pipes + 2 elbows) | ✅ Fully editable, MEP properties populated |
| Cross-floor pipeline (3 floors, 6 pipes + 4 elbows) | ✅ Correct Z elevations, Level assignment |
| Elbow auto-insertion | ✅ Revit automatically creates correct fitting |
| Pipe properties | ✅ Diameter, length, system type, flow parameters all editable |

---

## 4. Three-Layer Conversion Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                  USD-to-Revit Converter                          │
│                                                                  │
│  Input: Optimized USD Scene + ILOS Asset Library Metadata        │
│                                                                  │
│  ┌─ Layer 1: Equipment (放置型) ─────────────────────────────┐  │
│  │                                                            │  │
│  │  USD Category: Equipment                                   │  │
│  │  Examples: ASML EUV, AMAT Endura, Edwards Pump, VMB/VMP   │  │
│  │                                                            │  │
│  │  Target (v2):  Adaptive Component / Equipment Family       │  │
│  │  Fallback (v1): DirectShape + SharedParameter              │  │
│  │                                                            │  │
│  │  ┌─ v1 (Current — Temporary) ──────────────────────────┐  │  │
│  │  │ DirectShape: geometry transfer only                  │  │  │
│  │  │ Move/Rotate: ✅  Parametric edit: ❌  Drawing: ⚠️   │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                            │  │
│  │  ┌─ v2 (Target — Editable BIM) ────────────────────────┐  │  │
│  │  │ Adaptive Component: vendor geometry wrapped in       │  │  │
│  │  │ Revit Family → movable, taggable, schedulable       │  │  │
│  │  │ Move/Rotate: ✅  Tag/Schedule: ✅  Drawing: ✅      │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                            │  │
│  │  Decision: DirectShape is NOT the end goal.                │  │
│  │  The project requires editable BIM for construction docs.  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ Layer 2: Piping System (重複型 + 參數型) ────────────────┐  │
│  │                                                            │  │
│  │  USD Category: Pipe (LinearComponent)                      │  │
│  │       → Revit: Pipe.Create(start, end, diameter)           │  │
│  │                                                            │  │
│  │  USD Category: PipeFitting (Elbow, Tee, Reducer)           │  │
│  │       → Revit: NewElbowFitting() / NewTeeFitting()         │  │
│  │       → Revit auto-selects correct Family                  │  │
│  │                                                            │  │
│  │  USD Category: Valve                                       │  │
│  │       → Revit: FamilyInstance (vendor .rfa or generic)     │  │
│  │       → Three-tier: vendor .rfa > generic Family > DS      │  │
│  │                                                            │  │
│  │  Editability: FULL — drag endpoints, change diameter,      │  │
│  │               reroute, replace fittings                    │  │
│  │  Drawing: Plan view, section, ISO, P&ID                    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─ Layer 3: Structure (結構型) ─────────────────────────────┐  │
│  │                                                            │  │
│  │  USD Category: Structural (Column, Beam, Slab)             │  │
│  │  Conversion: Revit native structural elements              │  │
│  │  Editability: FULL — Revit native parametric               │  │
│  │  Drawing: Structural plans, sections, details              │  │
│  │                                                            │  │
│  │  Status: NOT YET VALIDATED (future Phase 3)                │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Output: Revit BIM Model (.rvt)                                  │
│          → Editable piping + positioned equipment + structure     │
│          → Construction drawings                                 │
│          → BOM/Schedule extraction                               │
│          → IFC export for regulatory submission                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Data Flow Detail

### 5.1 USD Scene Structure (ILOS Output)

```
Optimized_Fab.usd
│
├── /World/Levels/
│   ├── FL1  (elevation: 0mm)      ← Sub-Fab
│   ├── FL2  (elevation: 4500mm)   ← Interstitial
│   └── FL3  (elevation: 9000mm)   ← Cleanroom
│
├── /World/Equipment/
│   ├── ASML_NXE3400_001           ← Reference to vendor USD
│   │   ilos:category = "Equipment"
│   │   ilos:part_number = "ASML-NXE3400-C"
│   │   ilos:utility_connections = [{type:"UPW", pos:(5100,3050,9000)}]
│   │
│   └── Edwards_iXH4545_001
│       ilos:category = "Equipment"
│       位置: (8000, 3000, 0)  ← 1F Sub-Fab
│
├── /World/Piping/
│   ├── UPW_System/
│   │   ├── Line_UPW_3F_001/
│   │   │   ├── PF_PIPE_001  (ilos:category = "Pipe")
│   │   │   │   ilos:connection_start = (5100, 3050, 9000)
│   │   │   │   ilos:connection_end = (5100, 3050, 4500)
│   │   │   │   ilos:nominal_diameter = 50.8
│   │   │   │   ilos:piping_system = "UPW"
│   │   │   │   ilos:level = "FL3"
│   │   │   │
│   │   │   ├── PF_ELBOW_001  (ilos:category = "PipeFitting")
│   │   │   ├── VLV_001  (ilos:category = "Valve")
│   │   │   └── ...
│   │   └── Line_UPW_3F_002/
│   │
│   ├── CDA_System/
│   ├── PCW_System/
│   └── Exhaust_System/
│
└── /World/Structure/
    ├── Columns/
    ├── Beams/
    └── Slabs/
```

### 5.2 Conversion Logic

```python
def convert_usd_to_revit(usd_path: str, revit_doc):
    stage = Usd.Stage.Open(usd_path)

    # Phase 1: Create Levels
    for level_prim in find_prims(stage, '/World/Levels/'):
        elevation = level_prim.get('ilos:elevation_mm')
        Level.Create(revit_doc, mm_to_ft(elevation))

    # Phase 2: Equipment → DirectShape
    for equip in find_prims(stage, category='Equipment'):
        geometry = extract_mesh_with_instance_resolution(equip)
        ds = create_directshape(revit_doc, geometry)
        inject_shared_parameters(ds, equip.ilos_metadata)

    # Phase 3: Piping → Revit MEP Native
    for pipe in find_prims(stage, category='Pipe'):
        start = pipe.get('ilos:connection_start')
        end = pipe.get('ilos:connection_end')
        dia = pipe.get('ilos:nominal_diameter')
        system = pipe.get('ilos:piping_system')
        level = find_nearest_level(revit_doc, start.z)

        revit_pipe = Pipe.Create(revit_doc,
            get_system_type(system),
            get_pipe_type(),
            level, mm_to_ft(start), mm_to_ft(end))
        set_diameter(revit_pipe, dia)

    # Phase 4: Connect pipes at junctions → Auto elbow
    for junction in find_pipe_junctions():
        connector1 = get_nearest_connector(pipe1, junction)
        connector2 = get_nearest_connector(pipe2, junction)
        revit_doc.Create.NewElbowFitting(connector1, connector2)

    # Phase 5: Valves → Family Instance or DirectShape
    for valve in find_prims(stage, category='Valve'):
        mapping = asset_library.get_revit_mapping(valve.part_number)
        if mapping.has_rfa():
            place_family_instance(revit_doc, mapping.rfa, valve.position)
        else:
            create_directshape_with_metadata(revit_doc, valve)

    # Phase 6: Set display
    set_realistic_display(revit_doc)
```

---

## 6. USD Instance Resolution

### 6.1 The Problem

USD files use Instance/Prototype for geometry reuse. Direct traversal gives wrong world coordinates for instanced meshes.

### 6.2 Solution: inst_xf × proto_inv × mesh_xf

```python
for prim in stage.TraverseAll():
    if not prim.IsInstance():
        continue

    # Instance's world transform
    inst_xf = UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(time)

    # Prototype's root transform (to cancel out)
    proto = prim.GetPrototype()
    proto_xf = UsdGeom.Xformable(proto).ComputeLocalToWorldTransform(time)
    proto_inv = proto_xf.GetInverse()

    # For each mesh in prototype
    for child in Usd.PrimRange(proto):
        if child.GetTypeName() != 'Mesh':
            continue
        mesh_xf = UsdGeom.Xformable(child).ComputeLocalToWorldTransform(time)

        # Correct world transform
        final_xf = inst_xf * proto_inv * mesh_xf
```

### 6.3 Known Limitations

| API | Works? | Note |
|-----|--------|------|
| `stage.Traverse()` | ❌ | Skips instance internals |
| `stage.TraverseAll()` | ⚠️ | Returns 0 Instance Proxies for some USD files |
| `UsdGeom.XformCache` | ⚠️ | Incorrect transforms when Instance Proxy count = 0 |
| `inst_xf * proto_inv * mesh_xf` | ✅ | Manual calculation — always correct |

---

## 7. Unit Conversion Chain

```
USD (cm) → Revit Internal (ft)

Conversion factor: 0.01 / 0.3048 = 0.032808399

Example:
  USD coordinate: (5000, 3000, 9000) cm
  = (50, 30, 90) m
  = (164.04, 98.43, 295.28) ft  ← Revit internal unit
```

| Source | Unit | To Revit (ft) |
|--------|------|---------------|
| USD (NVIDIA standard) | cm | × 0.01 / 0.3048 |
| Blender | m | ÷ 0.3048 |
| IFC | mm | ÷ 304.8 |
| Revit internal | ft | — |

---

## 8. Revit Element Types and API

### 8.1 Layer 1: Equipment → DirectShape (v1 Fallback) / Adaptive Component (v2 Target)

**v1 (Current — DirectShape fallback):**

```csharp
// Create material for realistic display
var matId = Material.Create(document, "USD_Equipment_Gray");
var mat = document.GetElement(matId) as Material;
mat.Color = new Color(160, 160, 160);

// Build tessellated geometry
var builder = new TessellatedShapeBuilder();
builder.Target = TessellatedShapeBuilderTarget.AnyGeometry;
builder.Fallback = TessellatedShapeBuilderFallback.Mesh;
builder.OpenConnectedFaceSet(false);
foreach (var tri in triangles)
    builder.AddFace(new TessellatedFace(tri_points, matId));
builder.CloseConnectedFaceSet();
builder.Build();

// Create DirectShape
var ds = DirectShape.CreateElement(document,
    new ElementId(BuiltInCategory.OST_GenericModel));
ds.SetShape(builder.GetBuildResult().GetGeometricalObjects());

// CRITICAL: Set DisplayStyle.Realistic in separate MCP call
```

### 8.2 Layer 2: Piping → Revit MEP Native

```csharp
// Find system and pipe types
var systemType = new FilteredElementCollector(document)
    .OfClass(typeof(PipingSystemType)).Cast<PipingSystemType>()
    .First(s => s.SystemClassification == MEPSystemClassification.SupplyHydronic);

var pipeType = new FilteredElementCollector(document)
    .OfClass(typeof(PipeType)).Cast<PipeType>().First();

var level = new FilteredElementCollector(document)
    .OfClass(typeof(Level)).Cast<Level>().First();

// Create pipe
var pipe = Pipe.Create(document, systemType.Id, pipeType.Id, level.Id,
    new XYZ(startX, startY, startZ),
    new XYZ(endX, endY, endZ));

// Set diameter
pipe.get_Parameter(BuiltInParameter.RBS_PIPE_DIAMETER_PARAM)
    .Set(diameterInFeet);

// Connect two pipes with elbow (Revit auto-selects fitting)
var conn1 = GetNearestConnector(pipe1, junctionPoint);
var conn2 = GetNearestConnector(pipe2, junctionPoint);
document.Create.NewElbowFitting(conn1, conn2);
```

---

## 9. Cross-Floor Piping

### 9.1 Architecture

```
FL3 (9000mm) ─── Cleanroom Tool UPW Port
    │               connection: (5100, 3050, 9000)
    │
    │  Pipe.Create(FL3, (5100,3050,9000), (5100,3050,4750))
    │  ← Vertical drop, reference level = FL3
    │
    ▼ Elbow (auto)

FL2 (4500mm) ─── Interstitial Valve Station
    │               Horizontal run + valve
    │
    │  Pipe.Create(FL2, ...)
    │  ← Reference level = FL2
    │
    ▼ Elbow (auto)

FL1 (0mm) ──── Sub-Fab VMB/VMP Supply
                Horizontal run to supply main
```

### 9.2 Level Assignment Logic

```python
def find_reference_level(revit_doc, start_z_ft, end_z_ft):
    """Assign pipe to nearest level at its midpoint elevation"""
    mid_z = (start_z_ft + end_z_ft) / 2
    levels = get_all_levels(revit_doc)  # sorted by elevation
    return min(levels, key=lambda lv: abs(lv.elevation - mid_z))
```

### 9.3 Drawing Output per Level

| View | Shows |
|------|-------|
| FL3 Plan | Cleanroom tools + horizontal pipes at 3F |
| FL2 Plan | Valve stations + horizontal pipes at 2F + penetration symbols |
| FL1 Plan | Sub-fab equipment + horizontal pipes at 1F |
| Section | Full vertical routing across all floors |

---

## 10. IFC Role in the Pipeline

**IFC is NOT used as a conversion intermediate.** It serves as an **output format** for regulatory compliance:

```
                    ┌─────────────────────┐
                    │ Revit BIM Model     │
                    │ (editable .rvt)     │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ .dwg     │   │ .ifc     │   │ .pdf     │
        │ 施工圖   │   │ 送審用   │   │ 圖面輸出 │
        └──────────┘   └──────────┘   └──────────┘
```

### Why IFC failed as conversion intermediate:

1. Revit's IFC import engine cannot render IfcFacetedBrep geometry from ifcopenshell
2. IFC4 is only partially supported by Revit 2026
3. IFC2x3 requires complex OwnerHistory setup
4. Unit conversion issues (mm vs m) cause invisible geometry
5. DirectShape via Revit API is faster, more reliable, and produces identical results

### When IFC IS used:

- Revit → IFC export for regulatory submission (Revit handles this natively)
- Each element has `ilos:ifc_entity` attribute for correct IFC class mapping
- IfcGUID is auto-generated by Revit during export

---

## 11. Relationship to Other Documents

```
┌──────────────────────────────────────────────────────────┐
│                    Document Map                           │
│                                                          │
│  THIS DOCUMENT (Architecture)                            │
│  USD_to_Revit_System_Architecture.md                     │
│      │                                                   │
│      ├──→ USD_Revit_Convert.md (SOP / Checklist)         │
│      │    How to execute the conversion step-by-step     │
│      │                                                   │
│      ├──→ ILOS_USD_Asset_Vendor_Spec.md (Interface Spec) │
│      │    What vendors must provide in their USD files    │
│      │                                                   │
│      ├──→ ILOS_BOM_Cost_Engine.md (Module Spec)          │
│      │    How BOM extraction and SAP costing works        │
│      │                                                   │
│      ├──→ piping_connection.md (Technical Reference)     │
│      │    Elbow geometry math and connection alignment    │
│      │                                                   │
│      ├──→ RGRL_Whitepaper_EN/ZH.md (Business Context)   │
│      │    Why this system exists, market positioning      │
│      │                                                   │
│      └──→ RGRL_PRD_EN/ZH.md (Product Requirements)      │
│           Feature requirements and roadmap               │
└──────────────────────────────────────────────────────────┘
```

---

## 12. Validated POC Results Summary

| # | Test Case | Source | Method | Elements | Result |
|---|-----------|--------|--------|----------|--------|
| 1 | Factory Building | Revit→USD | DirectShape | 92 mesh | ✅ |
| 2 | KUKA Robot Arm | STEP→USD | DirectShape | 114 mesh (561K verts) | ✅ |
| 3 | Car Lift | SolidWorks→USD | DirectShape | 146 mesh | ✅ |
| 4 | Vehicle Hanger | SolidWorks→USD | DirectShape | 90 mesh | ✅ |
| 5 | Electrical Box | SubUSD | DirectShape | 8 mesh | ✅ |
| 6 | Pipes | SubUSD | DirectShape | 4 mesh | ✅ |
| 7 | City Demo | CityEngine→USD | DirectShape (merged) | 913 buildings | ✅ |
| 8 | KUKA × 6 copies | STEP→USD | DirectShape (batch) | 666 parts | ✅ |
| 9 | Single-floor pipe | ILOS test USD | MEP Native Pipe | 4 pipes + 2 elbows | ✅ |
| 10 | Cross-floor pipe | ILOS test USD | MEP Native Pipe | 6 pipes + 4 elbows | ✅ |

---

## 13. Known Limitations and Future Work

| Limitation | Impact | Planned Resolution |
|------------|--------|-------------------|
| DirectShape not editable | Equipment cannot be parametrically modified, cannot produce proper construction documents | **Must migrate to Adaptive Component / Equipment Family (v2 target)** — DirectShape is temporary fallback only |
| Valve Family not auto-created | Valves show as gaps in piping | Phase 2: Load vendor .rfa or use generic valve Family |
| No structural element conversion | Columns/beams not as native Revit elements | Phase 3: Map to Revit structural families |
| Color/material not transferred | All DirectShapes are uniform gray | Future: Read USD OmniPBR → create Revit materials |
| Large scene performance | >1000 DirectShapes can slow Revit | Mesh merging by category/region |

---

## 14. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-24 | Initial architecture document consolidating all POC findings, decision history, and validated conversion paths |
| 1.1 | 2026-03-24 | Corrected Layer 1 strategy — DirectShape is temporary fallback, NOT target solution. Target is Adaptive Component / Equipment Family for editable BIM. Updated decision rationale throughout. |
