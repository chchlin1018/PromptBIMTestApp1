# USD → Revit Conversion Pipeline

## Overview

A validated pipeline for converting NVIDIA USD (.usd/.usdc/.usda) files into Autodesk Revit 2026, supporting two conversion layers:

- **Layer 1 (DirectShape)**: Equipment, structural elements — visual geometry, movable but not parametrically editable
- **Layer 2 (MEP Native)**: Piping systems — fully editable Revit MEP elements with flow analysis and construction drawing output

**No Blender required.** Pure Python (usd-core) + Revit MCP.

---

## Two-Layer Architecture

```
USD File (.usd/.usdc/.usda)
    ↓
    ├── Layer 1: Equipment & Structure (DirectShape)
    │     Step 1: Python (usd-core) — Resolve Instances, extract geometry
    │     Step 2: JSON — Batched vertex/triangle data (cm → ft)
    │     Step 3: Revit MCP — TessellatedShapeBuilder → DirectShape + Material
    │     Result: Visual geometry, movable, NOT parametrically editable
    │
    └── Layer 2: Piping Systems (MEP Native) ← NEW
          Step 1: Python (usd-core) — Read ilos: metadata (category, diameter, connections)
          Step 2: JSON — Element type + connection coordinates (cm → ft)
          Step 3: Revit MCP — Pipe.Create() + NewElbowFitting() + NewValveFitting()
          Result: Fully editable MEP pipes, elbows, valves — can produce construction drawings
```

### When to Use Which Layer

| USD Content | Layer | Revit Element | Editable | Can Produce Drawings |
|-------------|-------|---------------|----------|---------------------|
| Equipment (EUV, Pumps, VMB) | Layer 1 | DirectShape | Move/Rotate only | Basic outline |
| Piping (UPW, CDA, Exhaust) | **Layer 2** | **Pipe + Fitting** | **Full MEP editing** | **✅ ISO, Plan, Section** |
| Structure (Columns, Beams) | Layer 1 or Revit native | DirectShape or Column/Beam | Depends | Yes |
| Cable Trays | Layer 1 | DirectShape | Move/Rotate only | Basic |

---

## Prerequisites

### Software
| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | USD geometry extraction |
| usd-core | 24.x+ | `pip install usd-core` — USD file parsing |
| Revit | 2026 | Target BIM platform |
| Revit MCP Plugin | mcp-servers-for-revit | AI ↔ Revit communication |
| Node.js | 18+ | MCP server runtime |

### Revit MCP Setup
1. Download from [mcp-servers-for-revit Releases](https://github.com/mcp-servers-for-revit/mcp-servers-for-revit/releases) (Revit2026 version)
2. Extract to `%AppData%\Autodesk\Revit\Addins\2026\`
3. Launch Revit → Add-ins → Revit MCP Plugin → MCP Switch (Open Server)

---

## Step 1: Extract USD Geometry (Python)

### Key Concept: USD Instance Resolution

USD files use **Instancing** — shared geometry (Prototype) placed multiple times with different transforms (Instance). The critical formula:

```
final_transform = instance_world_xf × inverse(prototype_root_xf) × mesh_local_xf
```

This maps each mesh from prototype-local space to its correct world position.

### Important Findings
- `stage.TraverseAll()` may return **0 Instance Proxies** for some USD files
- `UsdGeom.XformCache.GetLocalToWorldTransform()` does NOT correctly resolve Instance transforms in this case
- Must manually iterate Instances → Prototypes → Meshes with the formula above

### Complete Extraction Script

```python
"""
USD → JSON Geometry Extractor
Reads USD file, resolves Instance transforms, outputs batched JSON for Revit import.
"""
from pxr import Usd, UsdGeom
import json, os, math, time


def extract_usd_to_json(usd_path: str, output_dir: str, batch_size: int = 30) -> dict:
    """
    Extract all mesh geometry from a USD file with correct Instance resolution.

    Args:
        usd_path: Path to .usd/.usdc/.usda file
        output_dir: Directory to write batch JSON files
        batch_size: Number of meshes per batch (30 recommended for Revit MCP)

    Returns:
        dict with extraction statistics
    """
    t0 = time.time()
    stage = Usd.Stage.Open(usd_path)

    # USD uses centimeters, Revit internal unit is feet
    CM_TO_FT = 0.01 / 0.3048  # cm → m → ft

    meshes = []

    # ── Phase 1: Collect Instanced Meshes ──
    # For each Instance, apply its world transform to prototype meshes
    for prim in stage.TraverseAll():
        if not prim.IsInstance():
            continue

        inst_xf = UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(
            Usd.TimeCode.Default()
        )
        proto = prim.GetPrototype()
        proto_root_xf = UsdGeom.Xformable(proto).ComputeLocalToWorldTransform(
            Usd.TimeCode.Default()
        )
        proto_inv = proto_root_xf.GetInverse()

        for child in Usd.PrimRange(proto):
            if child.GetTypeName() != 'Mesh':
                continue

            mesh_data = _extract_mesh(child, inst_xf, proto_inv, CM_TO_FT)
            if mesh_data:
                meshes.append(mesh_data)

    # ── Phase 2: Collect Non-Instanced Meshes ──
    # Some USD files have meshes outside of any Instance
    for prim in stage.TraverseAll():
        if prim.GetTypeName() != 'Mesh':
            continue
        if prim.IsInstanceProxy() or prim.IsInPrototype():
            continue

        xf = UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(
            Usd.TimeCode.Default()
        )
        # For non-instanced meshes: identity prototype transform
        from pxr import Gf
        identity = Gf.Matrix4d(1)
        mesh_data = _extract_mesh(prim, xf, identity.GetInverse(), CM_TO_FT)
        if mesh_data:
            meshes.append(mesh_data)

    # ── Phase 3: Write Batched JSON ──
    num_batches = math.ceil(len(meshes) / batch_size)
    batch_prefix = os.path.splitext(os.path.basename(usd_path))[0]

    for bi in range(num_batches):
        batch = meshes[bi * batch_size : (bi + 1) * batch_size]
        out_path = os.path.join(output_dir, f"{batch_prefix}_batch_{bi}.json")
        with open(out_path, "w") as f:
            json.dump(batch, f)

    # ── Statistics ──
    total_verts = sum(len(m["verts"]) for m in meshes)
    total_tris = sum(len(m["tris"]) for m in meshes)

    # Bounding box check (sanity)
    if meshes:
        all_x = [v[0] for m in meshes for v in m["verts"]]
        all_y = [v[1] for m in meshes for v in m["verts"]]
        all_z = [v[2] for m in meshes for v in m["verts"]]
        span = {
            "x_ft": round(max(all_x) - min(all_x), 2),
            "y_ft": round(max(all_y) - min(all_y), 2),
            "z_ft": round(max(all_z) - min(all_z), 2),
        }
        span["x_m"] = round(span["x_ft"] * 0.3048, 2)
        span["y_m"] = round(span["y_ft"] * 0.3048, 2)
        span["z_m"] = round(span["z_ft"] * 0.3048, 2)
    else:
        span = {}

    return {
        "meshes": len(meshes),
        "vertices": total_verts,
        "triangles": total_tris,
        "batches": num_batches,
        "batch_prefix": batch_prefix,
        "span": span,
        "time_sec": round(time.time() - t0, 1),
    }


def _extract_mesh(
    prim, inst_xf, proto_inv, cm_to_ft: float
) -> dict | None:
    """
    Extract a single mesh prim's geometry in world space.

    Args:
        prim: USD Mesh prim
        inst_xf: Instance world transform (Gf.Matrix4d)
        proto_inv: Inverse of prototype root transform (Gf.Matrix4d)
        cm_to_ft: Unit conversion factor

    Returns:
        dict with name, verts, tris — or None if invalid
    """
    mesh = UsdGeom.Mesh(prim)
    pts = mesh.GetPointsAttr().Get()
    fca = mesh.GetFaceVertexCountsAttr().Get()
    fi = mesh.GetFaceVertexIndicesAttr().Get()

    if not pts or not fca or not fi:
        return None

    # Compute final world transform
    mesh_local_xf = UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(
        Usd.TimeCode.Default()
    )
    final_xf = inst_xf * proto_inv * mesh_local_xf

    # Transform vertices to world space (ft)
    verts = []
    for pt in pts:
        w = final_xf.Transform(
            (float(pt[0]), float(pt[1]), float(pt[2]))
        )
        verts.append([
            round(float(w[0]) * cm_to_ft, 6),
            round(float(w[1]) * cm_to_ft, 6),
            round(float(w[2]) * cm_to_ft, 6),
        ])

    # Triangulate faces (USD may have quads or n-gons)
    tris = []
    idx = 0
    for fc in fca:
        n = int(fc)
        if n == 3:
            tris.append([int(fi[idx]), int(fi[idx + 1]), int(fi[idx + 2])])
        elif n == 4:
            tris.append([int(fi[idx]), int(fi[idx + 1]), int(fi[idx + 2])])
            tris.append([int(fi[idx]), int(fi[idx + 2]), int(fi[idx + 3])])
        elif n > 4:
            # Fan triangulation for n-gons
            for i in range(1, n - 1):
                tris.append([int(fi[idx]), int(fi[idx + i]), int(fi[idx + i + 1])])
        idx += n

    if not tris:
        return None

    return {"name": prim.GetName(), "verts": verts, "tris": tris}


# ── Usage Example ──
if __name__ == "__main__":
    result = extract_usd_to_json(
        usd_path=r"C:\path\to\KukaArm1.usd",
        output_dir=r"C:\path\to\output",
        batch_size=30,
    )
    print(f"Extracted: {result['meshes']} meshes, "
          f"{result['vertices']} verts, {result['triangles']} tris, "
          f"{result['batches']} batches in {result['time_sec']}s")
    print(f"Span: {result['span']}")
```

---

## Step 2: Unit Conversion

| Source | Unit | Conversion |
|--------|------|------------|
| USD (NVIDIA) | centimeters (cm) | × 0.01 → meters |
| Blender import | meters (m) | ÷ 0.3048 → feet |
| Revit internal | feet (ft) | — |

Combined: `cm_to_ft = 0.01 / 0.3048 = 0.032808`

---

## Step 3: Import to Revit via MCP (C#)

### Key Requirements
1. **Do NOT create explicit `Transaction`** — Revit MCP wraps its own transaction automatically
2. **Must create and assign a `Material`** — Without material, Mesh-type DirectShapes render as **solid black** in Realistic mode
3. **Use `TessellatedShapeBuilderFallback.Mesh`** — Required for complex geometry that can't form a Solid
4. **Filter degenerate triangles** — Skip triangles where any two vertices are closer than 0.0001 ft

### Complete Revit Import Script (C#, via send_code_to_revit)

```csharp
// ── Phase 1: Create Material ──
// This MUST be done before importing geometry.
// Without material, all faces render black in Realistic mode.

var matId = ElementId.InvalidElementId;
var mats = new FilteredElementCollector(document)
    .OfClass(typeof(Material))
    .Cast<Material>()
    .ToList();

Material kubaMat = mats.FirstOrDefault(m => m.Name == "USD_Gray");
if (kubaMat == null) {
    matId = Material.Create(document, "USD_Gray");
    kubaMat = document.GetElement(matId) as Material;
    kubaMat.Color = new Color(160, 160, 160);  // Light gray
} else {
    matId = kubaMat.Id;
}
```

```csharp
// ── Phase 2: Import Batched JSON → DirectShape ──

string basePath = @"C:\path\to\output\";
string prefix = "KukaArm1";  // Must match batch_prefix from Python
int numBatches = 4;           // From Python extraction result
int total = 0;

for (int bi = 0; bi < numBatches; bi++) {
    string raw = System.IO.File.ReadAllText(
        basePath + prefix + "_batch_" + bi + ".json"
    );
    var jarr = Newtonsoft.Json.Linq.JArray.Parse(raw);

    foreach (Newtonsoft.Json.Linq.JObject m in jarr) {
        try {
            var vArr = m["verts"] as Newtonsoft.Json.Linq.JArray;
            var tArr = m["tris"] as Newtonsoft.Json.Linq.JArray;

            // Parse vertices
            var verts = new List<XYZ>();
            foreach (Newtonsoft.Json.Linq.JArray v in vArr)
                verts.Add(new XYZ((double)v[0], (double)v[1], (double)v[2]));

            // Build tessellated shape
            var builder = new TessellatedShapeBuilder();
            builder.Target = TessellatedShapeBuilderTarget.AnyGeometry;
            builder.Fallback = TessellatedShapeBuilderFallback.Mesh;
            builder.OpenConnectedFaceSet(false);

            foreach (Newtonsoft.Json.Linq.JArray tri in tArr) {
                int i0 = (int)tri[0], i1 = (int)tri[1], i2 = (int)tri[2];

                // Bounds check
                if (i0 >= 0 && i0 < verts.Count &&
                    i1 >= 0 && i1 < verts.Count &&
                    i2 >= 0 && i2 < verts.Count) {

                    var p0 = verts[i0];
                    var p1 = verts[i1];
                    var p2 = verts[i2];

                    // Skip degenerate triangles
                    if (p0.DistanceTo(p1) > 0.0001 &&
                        p1.DistanceTo(p2) > 0.0001 &&
                        p0.DistanceTo(p2) > 0.0001) {

                        // Pass matId (NOT ElementId.InvalidElementId)
                        builder.AddFace(new TessellatedFace(
                            new List<XYZ>{p0, p1, p2}, matId));
                    }
                }
            }

            builder.CloseConnectedFaceSet();
            builder.Build();
            var result = builder.GetBuildResult();

            if (result.Outcome == TessellatedShapeBuilderOutcome.Nothing)
                continue;

            // Create DirectShape
            var ds = DirectShape.CreateElement(
                document,
                new ElementId(BuiltInCategory.OST_GenericModel)
            );
            ds.SetShape(result.GetGeometricalObjects());
            ds.Name = m["name"].ToString();
            total++;

        } catch { }
    }
}
```

```csharp
// ── Phase 3: Set Display Style ──
// MUST be Realistic mode for material colors to show

var view = document.ActiveView as View3D;
if (view != null) {
    view.DisplayStyle = DisplayStyle.Realistic;
}
```

---

## Layer 2: MEP Piping Conversion (NEW — v2.0)

### Concept

Unlike Layer 1 (visual geometry only), Layer 2 reads **ILOS metadata** from USD prims and creates **Revit native MEP elements** that are fully editable, connected, and can produce construction drawings.

### USD Metadata Requirements (ILOS Convention)

Each pipe component in the USD scene must have `ilos:` prefixed attributes:

```
ilos:category           → "Pipe" | "PipeFitting" | "Valve"
ilos:part_number        → "PF_PIPE_SS316L_2IN" | "PF_ELBOW_90_SS316L_2IN" | "VLV_ISOL_BALL_SS316L_2IN"
ilos:nominal_diameter   → 50.8 (mm)
ilos:material           → "SS316L"
ilos:connection_start   → [x, y, z] in cm
ilos:connection_end     → [x, y, z] in cm
ilos:revit_family       → "Pipe" | "M_Elbow - Generic" | "M_Valve - Ball"
ilos:revit_type         → "Standard" | "50mm"
```

Optional attributes:
```
ilos:length_mm          → 2000.0
ilos:angle_deg          → 90.0 (for elbows)
ilos:valve_type         → "Ball" | "Gate" | "Check"
ilos:manufacturer       → "Swagelok"
ilos:model              → "SS-45S8-A"
```

### Step 1: Extract MEP Metadata (Python)

```python
"""
Read ILOS pipe metadata from USD, output JSON for Revit MEP import.
"""
from pxr import Usd, Sdf
import json

def extract_mep_metadata(usd_path: str, output_path: str) -> list:
    stage = Usd.Stage.Open(usd_path)
    CM_TO_FT = 0.01 / 0.3048

    elements = []
    for prim in stage.Traverse():
        if not prim.HasAttribute('ilos:category'):
            continue

        elem = {'prim_name': prim.GetName()}
        for attr in prim.GetAttributes():
            name = attr.GetName()
            if not name.startswith('ilos:'):
                continue
            key = name.replace('ilos:', '')
            val = attr.Get()
            if isinstance(val, (int, float, str)):
                elem[key] = val
            elif hasattr(val, '__len__') and len(val) == 3:
                elem[key] = [float(val[0]), float(val[1]), float(val[2])]

        # Convert cm → ft
        for k in ['connection_start', 'connection_end']:
            if k in elem:
                elem[k] = [round(v * CM_TO_FT, 6) for v in elem[k]]

        elements.append(elem)

    with open(output_path, 'w') as f:
        json.dump(elements, f, indent=2)

    return elements
```

### Step 2: Create Revit MEP Pipes (C# via MCP)

**Strategy**: Create only `Pipe` elements from connection coordinates. Revit automatically inserts elbow fittings when pipes are connected at angles via `NewElbowFitting()`.

```csharp
// ── Read JSON metadata ──
string jsonPath = @"C:\path\to\ilos_pipeline_mep.json";
string raw = System.IO.File.ReadAllText(jsonPath);
var elements = Newtonsoft.Json.Linq.JArray.Parse(raw);

// ── Get Revit MEP types ──
var pipeType = new FilteredElementCollector(document)
    .OfClass(typeof(Autodesk.Revit.DB.Plumbing.PipeType))
    .FirstElement();
var systemType = new FilteredElementCollector(document)
    .OfClass(typeof(Autodesk.Revit.DB.Plumbing.PipingSystemType))
    .FirstElement();
var level = new FilteredElementCollector(document)
    .OfClass(typeof(Level))
    .FirstElement() as Level;

// ── Create Pipe elements ──
double diameter = 50.8 / 304.8;  // 50.8mm → feet
var createdPipes = new List<Autodesk.Revit.DB.Plumbing.Pipe>();

foreach (Newtonsoft.Json.Linq.JObject elem in elements)
{
    string cat = elem["category"]?.ToString() ?? "";
    if (cat != "Pipe") continue;

    var cs = elem["connection_start"] as Newtonsoft.Json.Linq.JArray;
    var ce = elem["connection_end"] as Newtonsoft.Json.Linq.JArray;
    var startPt = new XYZ((double)cs[0], (double)cs[1], (double)cs[2]);
    var endPt = new XYZ((double)ce[0], (double)ce[1], (double)ce[2]);

    var pipe = Autodesk.Revit.DB.Plumbing.Pipe.Create(
        document, systemType.Id, pipeType.Id, level.Id, startPt, endPt);

    var diamParam = pipe.get_Parameter(BuiltInParameter.RBS_PIPE_DIAMETER_PARAM);
    if (diamParam != null) diamParam.Set(diameter);

    createdPipes.Add(pipe);
}
```

### Step 3: Connect Pipes with Elbow Fittings (C# via MCP)

```csharp
// ── Find adjacent pipe connectors and insert elbows ──
// For each pair of consecutive pipes, find the closest unconnected connectors
// and use NewElbowFitting to join them.

for (int i = 0; i < createdPipes.Count - 1; i++)
{
    var pipe_a = createdPipes[i];
    var pipe_b = createdPipes[i + 1];

    // Find the end connector of pipe_a closest to start of pipe_b
    Connector connA = null, connB = null;
    double minDist = double.MaxValue;

    foreach (Connector ca in pipe_a.ConnectorManager.Connectors)
    {
        foreach (Connector cb in pipe_b.ConnectorManager.Connectors)
        {
            double d = ca.Origin.DistanceTo(cb.Origin);
            if (d < minDist)
            {
                minDist = d;
                connA = ca;
                connB = cb;
            }
        }
    }

    if (connA != null && connB != null && minDist < 2.0)  // within 2 feet
    {
        try
        {
            document.Create.NewElbowFitting(connA, connB);
        }
        catch { /* Skip if elbow can't be inserted (e.g., valve position) */ }
    }
}
```

### Step 4: Set Display Mode (Separate MCP Call)

```csharp
var view = document.ActiveView as View3D;
if (view != null) view.DisplayStyle = DisplayStyle.Realistic;
```

### Cross-Floor Piping Support

ILOS-FAB scenarios typically involve piping across multiple floors (e.g., fab cleanroom on 3F → sub-fab on 1F). Revit fully supports this:

```
3F (FL3, 9000mm) ─── Cleanroom equipment (EUV, Endura)
    │                  UPW/CDA/Exhaust ports
    │  ← Vertical pipe (crosses floors)
2F (FL2, 4500mm) ─── Interstitial / pipe gallery
    │                  Valves, branch connections
    │  ← Vertical pipe
1F (FL1, 0mm)    ─── Sub-fab (Pumps, Scrubbers, VMB/VMP)
                      Supply main connections
```

**Implementation:**

```python
# USD provides: level definitions + pipe coordinates with Z elevations

# Step 1: Create Revit Levels from USD metadata
levels = [
    {"name": "FL1", "elevation_mm": 0},
    {"name": "FL2", "elevation_mm": 4500},
    {"name": "FL3", "elevation_mm": 9000},
]

# Step 2: Each pipe is assigned to the nearest Level
# But pipe endpoints can be at ANY Z elevation — Revit handles cross-floor automatically
```

```csharp
// Create levels
Level.Create(document, 0);           // FL1
Level.Create(document, 14.7637795);  // FL2 (4500mm in feet)
Level.Create(document, 29.5275591);  // FL3 (9000mm in feet)

// Pipes reference nearest level, but endpoints can be anywhere
Pipe.Create(doc, sysId, typeId, FL3_Id,
    new XYZ(x, y, 29.53),   // 3F equipment port
    new XYZ(x, y, 14.76));  // drops to 2F
Pipe.Create(doc, sysId, typeId, FL2_Id,
    new XYZ(x, y, 14.76),   // 2F horizontal
    new XYZ(x2, y, 14.76));
```

**Result in Revit:**
- FL3 Plan View → Shows equipment + pipe penetration symbol
- FL2 Plan View → Shows horizontal pipe + valve + up/down penetration symbols
- FL1 Plan View → Shows horizontal pipe + VMB connection
- Section View → Shows complete cross-floor routing

### Layer 2 Validation Results

| Test | Elements | Result |
|------|----------|--------|
| Pipe.Create() × 4 segments | 2" SS316L, 0.5m~2m lengths | ✅ Created with correct diameter |
| NewElbowFitting() × 2 | 90° elbows at pipe junctions | ✅ Auto-inserted by Revit |
| Select pipe → Properties | All MEP parameters visible | ✅ Diameter, length, system type, flow |
| Drag pipe endpoint | Pipe resizes, elbow follows | ✅ Fully editable |
| FL1 Plan View | Pipe line + elbow symbol + connector | ✅ Construction drawing ready |
| IFC Export parameters | IfcGUID assigned to elbows | ✅ IFC-ready |

---

## Validated Test Cases

### Layer 1 (DirectShape — Equipment & Structure)

| # | USD Asset | Source Format | Meshes | Vertices | Result |
|---|-----------|-------------|--------|----------|--------|
| 1 | Factory Building | Revit → USD | 92 | 138K | ✅ Complete building |
| 2 | KUKA Robot Arm (KR 10 R1440) | STEP → USD | 114 | 561K | ✅ All 6 joints correct |
| 3 | Car Lift | SolidWorks → USD | 146 | 30K | ✅ Perfect match |
| 4 | Vehicle Hanger | SolidWorks → USD | 90 | — | ✅ Truss + hooks |
| 5 | Electrical Box | SubUSD | 8 | — | ✅ Box + breaker |
| 6 | Pipes (visual) | SubUSD | 4 | — | ✅ Elbows + risers |
| 7 | City Demo (full city) | CityEngine → USD | 913 | 1.2M | ✅ Entire cityscape |

### Layer 2 (MEP Native — Piping)

| # | Test | Pipe Segments | Fittings | Result |
|---|------|--------------|----------|--------|
| 8 | ILOS Test Pipeline (UPW 2" SS316L) | 4 pipes | 2 elbows | ✅ Fully editable MEP |

---

## Troubleshooting

### Problem: Parts not assembled correctly
**Cause:** Instance transforms not resolved properly.
**Solution:** Use `inst_xf * proto_inv * mesh_local_xf` formula. Do NOT rely on `UsdGeom.XformCache.GetLocalToWorldTransform()` — it returns 0 Instance Proxies for some USD files.

### Problem: All geometry renders as solid black
**Cause:** No material assigned to TessellatedFace.
**Solution:** Create a Revit Material and pass its `ElementId` to `builder.AddFace(new TessellatedFace(vertices, matId))` instead of `ElementId.InvalidElementId`.

### Problem: "Exception has been thrown by the target of an invocation"
**Cause:** Revit MCP Plugin already wraps code in a Transaction.
**Solution:** Do NOT create `new Transaction(document, ...)`. Remove all explicit `tx.Start()` / `tx.Commit()` calls.

### Problem: Revit crashes on large scenes
**Cause:** Too many vertices/faces in a single MCP call.
**Solution:** Split meshes into batches of 30. For very large scenes (>1000 meshes), merge multiple small meshes into fewer DirectShapes.

### Problem: Model too large or too small
**Cause:** Unit conversion error.
**Solution:** Verify USD unit (usually cm for NVIDIA assets). Apply `cm × 0.01 / 0.3048 = ft`.

### Problem: Bounding box sanity check
**Expected sizes (approximate):**
- KUKA KR 10 R1440: ~1.3 × 0.6 × 1.3 m (4.3 × 2.0 × 4.1 ft)
- Factory Building: ~60 × 30 × 12 m
- City scene: varies

---

## Large Scene Optimization

For scenes with >1000 meshes:

1. **Mesh Merging** — Combine nearby small meshes into single DirectShapes
2. **LOD Decimation** — Reduce polygon count based on object size
3. **Spatial Partitioning** — Only import the area of interest
4. **Batch Size Tuning** — 30 meshes/batch for MCP stability

---

## File Locations

| File | Path |
|------|------|
| USD Explorer Sample | `C:\Users\kaiji\MCPProject\OPENUSD-Study\Data\USD_Explorer_Sample_NVD@10011\` |
| Factory Building USD | `..\Factory\Source_Files\Revit\USD\Factory_Building.usd` |
| KUKA Arm USD | `..\Factory\Source_Files\STEP\USD\KukaArm1.usd` |
| Car Lift USD | `..\Factory\Source_Files\SolidWorks\USD\car_lift.usd` |
| Output JSON/IFC | `C:\Users\kaiji\MCPProject\OPENUSD-Study\Omniverse Project\docs\` |

---

## Repeatable Execution Checklist

Every time you run this pipeline, follow this exact order to avoid unexpected results:

### Pre-flight
- [ ] Revit: Open a **new blank project** (not reuse existing)
- [ ] Revit: Switch to **3D View** BEFORE importing
- [ ] Revit: **Add-ins → Revit MCP Plugin → MCP Switch** (Open Server)
- [ ] Verify MCP: `return document.Title;` should return project name

### Import — MANDATORY 2-Step Execution

**⚠️ MUST be two separate MCP calls. Do NOT combine into one.**

**MCP Call 1: Import geometry**
```
Phase 1: Delete old DirectShapes (clean slate)
Phase 2: Create/find Material (KUKA_Gray, Color 160,160,160)
Phase 3: Import all JSON batches with matId
```

**MCP Call 2: Set display (ALWAYS run separately after Call 1)**
```csharp
var v = document.ActiveView as View3D;
v.DisplayStyle = DisplayStyle.Realistic;
return "Display: " + v.DisplayStyle;
```

**Why 2 steps?** Setting DisplayStyle in the same MCP call as geometry import does not reliably persist. The display reverts to ShadingWithEdges, causing all-black rendering.

### Post-import Verification
- [ ] Confirm return value of Call 2 shows `Realistic`
- [ ] If still `ShadingWithEdges` → user must be in 3D view first, then re-run Call 2

### Known Gotchas

| Issue | Root Cause | Prevention |
|-------|-----------|------------|
| All black | Material not assigned OR display not Realistic | Always pass `matId` to AddFace, always set Realistic |
| Parts scattered | Instance transforms wrong | Use `inst_xf * proto_inv * mesh_xf` formula |
| Transaction error | MCP already wraps transaction | NEVER create `new Transaction()` |
| Display not changing | ActiveView is floor plan, not 3D | Switch to 3D view BEFORE running code |
| Duplicate geometry | Old DirectShapes not deleted | Always delete old ones first |

---

## Automation Script

A single Python script that handles Step 1 (extraction) and generates the complete C# code for Step 3 (Revit import):

```
python usd_to_revit.py <usd_file_path> [batch_size]
```

Located at: `OPENUSD-Revit-connector/usd_to_revit.py`

This script:
1. Reads USD file with correct Instance resolution
2. Writes batched JSON files
3. Generates a `.cs` file with the complete Revit MCP import code
4. Prints the code for direct copy-paste into `send_code_to_revit`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-18 | Initial validated pipeline (Layer 1: DirectShape) |
| 1.1 | 2026-03-18 | Added repeatable checklist, automation script, known gotchas |
| 2.0 | 2026-03-19 | **Major update**: Added Layer 2 (MEP Native Piping) — Pipe.Create + NewElbowFitting, ILOS metadata convention, cross-floor support, construction drawing validation |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [piping_connection.md](docs/piping_connection.md) | Elbow-to-pipe geometry guide (correct bend center calculation) |
| [ILOS_Test_Pipeline_v4.usda](../Omniverse%20Project/docs/ILOS_Test_Pipeline_v4.usda) | Test USD with ILOS metadata |
| [create_ilos_pipeline_v4.py](../Omniverse%20Project/docs/create_ilos_pipeline_v4.py) | Script to generate test USD |

---

*Generated from POC validation session — Claude Code + Revit MCP + usd-core*
