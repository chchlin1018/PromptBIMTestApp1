# ILOS USD Asset Vendor Specification

> Universal design guidelines for ANY vendor to create USD files compatible with the ILOS platform.
> The same specification applies whether you are ASML delivering an EUV scanner, Swagelok delivering a ball valve, or a casting foundry delivering a valve body.

**Version:** 2.0
**Date:** 2026-03-19
**Audience:** All product/component vendors
**Status:** Draft

---

## 1. Core Principle: Every Product is the Same

In the ILOS ecosystem, every product — regardless of complexity — is defined by exactly two things:

1. **What does it look like from the outside?** (Geometry)
2. **Where do things connect to it?** (Connection Points)

```
A semiconductor fab        = geometry + utility connections
An EUV scanner             = geometry + pipe/power/exhaust connections
A ball valve               = geometry + inlet/outlet connections
A valve body (casting)     = geometry + machining datum connections

Same USD structure. Same spec. Every level.
```

### The Recursive Nature

Your product is a "black box" to your customer, but an "assembly" to you:

```
Your Customer sees:    ┌─────────┐
                       │ ■■■■■■■ │ ← black box + connection points
                       └─────────┘

You see internally:    ┌─────────┐
                       │ ○─┤├─○  │ ← sub-components + internal routing
                       │ ○─██─○  │
                       └─────────┘

Your Supplier sees their part as:
                       ┌───┐
                       │ █ │ ← another black box to you
                       └───┘
```

This is handled by USD Variant Sets — one file, multiple levels of detail.

---

## 2. File Format

| Requirement | Specification |
|-------------|--------------|
| Format | OpenUSD (.usd, .usda, or .usdc) |
| Units | **Centimeters** — `metersPerUnit = 0.01` |
| Up axis | **Z** — `upAxis = "Z"` |
| Origin | Center of base/mounting surface |

```usda
#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 0.01
    upAxis = "Z"
)
```

---

## 3. USD Structure (Same for ALL Products)

```
/World
    /World/[ProductName]                        ← Root prim
    │
    ├── Metadata (ilos: attributes)             ← WHO and WHAT (Section 4)
    │
    ├── /Geometry                               ← WHAT IT LOOKS LIKE
    │   ├── /Body          (main mesh)
    │   ├── /SubPart_A     (optional)
    │   └── /SubPart_B     (optional)
    │
    ├── /Connections                             ← WHERE THINGS CONNECT (Section 5)
    │   ├── /Port_1        (position + direction + type)
    │   ├── /Port_2
    │   └── /Port_N
    │
    ├── /Looks                                  ← APPEARANCE (Section 7)
    │   └── /Material_1
    │
    └── variantSets = {                         ← LEVEL OF DETAIL (Section 6)
            string detail_level = "blackbox"     ← your customer uses this
                                   "assembly"    ← you use this (optional)
        }
```

---

## 4. Required Metadata

Attach these attributes to the root product prim. **All vendors provide the same set.**

### 4.1 Identity (Required — ALL vendors)

| Attribute | Type | Example (ASML) | Example (Swagelok) |
|-----------|------|-----------------|---------------------|
| `ilos:category` | string | `"Equipment"` | `"Valve"` |
| `ilos:part_number` | string | `"EQP_LITHO_EUV_NXE3400"` | `"VLV_ISOL_BALL_SS316L_2IN"` |
| `ilos:manufacturer` | string | `"ASML"` | `"Swagelok"` |
| `ilos:model` | string | `"NXE:3400C"` | `"SS-45S8-A"` |
| `ilos:description` | string | `"EUV Lithography System"` | `"2in SS316L Ball Valve"` |

### 4.2 Physical Properties (Required — ALL vendors)

| Attribute | Type | Example (ASML) | Example (Swagelok) |
|-----------|------|-----------------|---------------------|
| `ilos:material` | string | `"Mixed"` | `"SS316L"` |
| `ilos:weight_kg` | float | `17000.0` | `0.82` |
| `ilos:length_mm` | float | `3200.0` | `150.0` |
| `ilos:width_mm` | float | `2800.0` | `80.0` |
| `ilos:height_mm` | float | `3500.0` | `120.0` |

### 4.3 Domain-Specific Properties (Required — per category)

**Only include the attributes relevant to your product category.**

**For piping components (Valve, PipeFitting, Filter, Regulator, Gauge):**

| Attribute | Type | Example |
|-----------|------|---------|
| `ilos:nominal_diameter` | float | `50.8` (mm) |
| `ilos:pressure_rating` | float | `68.9` (bar) |
| `ilos:temperature_rating_max` | float | `232.0` (°C) |
| `ilos:end_connection` | string | `"Swagelok Tube Fitting"` |
| `ilos:cv` | float | `13.7` |
| `ilos:insulation_thickness_mm` | float | `25.0` (affects clearance and cost) |
| `ilos:insulation_material` | string | `"Elastomeric Foam"` / `"Calcium Silicate"` / `"PVDF Jacket"` |

**For equipment (Equipment, Pump, Tank, HeatExchanger, AirHandler):**

| Attribute | Type | Example |
|-----------|------|---------|
| `ilos:power_kw` | float | `850.0` |
| `ilos:clearance_front_mm` | float | `2000.0` |
| `ilos:clearance_back_mm` | float | `1500.0` |
| `ilos:clearance_left_mm` | float | `1000.0` |
| `ilos:clearance_right_mm` | float | `1000.0` |
| `ilos:vibration_class` | string | `"VC-E"` |
| `ilos:cleanroom_class` | string | `"ISO 4"` |

### 4.4 Procurement Metadata (Recommended — ALL vendors)

| Attribute | Type | Example |
|-----------|------|---------|
| `ilos:vendor_url` | string | Product page URL |
| `ilos:datasheet_url` | string | Datasheet PDF URL |
| `ilos:lead_time_weeks` | float | `6.0` |
| `ilos:unit_price_usd` | float | `285.0` (optional) |

### 4.5 Downstream Mapping (Recommended — ALL vendors)

| Attribute | Type | Example |
|-----------|------|---------|
| `ilos:revit_category` | string | `"OST_PipeAccessory"` |
| `ilos:ifc_entity` | string | `"IfcValve"` |
| `ilos:ifc_predefined_type` | string | `"ISOLATING"` |

---

## 5. Connection Points (Critical)

**This is the most important part of the spec.** Connection points tell ILOS where pipes, cables, ducts, or mechanical interfaces attach to your product.

### 5.1 Structure

Each connection is an Xform prim under `/Connections/`:

```usda
def Xform "Connections"
{
    def Xform "UPW_Inlet"
    {
        double3 xformOp:translate = (-7.5, 0, 0)
        uniform token[] xformOpOrder = ["xformOp:translate"]

        custom string ilos:port_name = "UPW_Inlet"
        custom string ilos:port_type = "Pipe"
        custom string ilos:port_medium = "UPW"
        custom float ilos:port_size_mm = 50.8
        custom string ilos:port_standard = "Swagelok Tube Fitting"
        custom float3 ilos:port_direction = (-1, 0, 0)
    }
}
```

### 5.2 Required Attributes per Connection

| Attribute | Type | Description |
|-----------|------|-------------|
| `ilos:port_name` | string | Human-readable name (e.g., `"UPW_Inlet"`, `"Exhaust_Out"`) |
| `ilos:port_type` | string | `"Pipe"`, `"Electrical"`, `"Duct"`, `"Mechanical"` |
| `ilos:port_medium` | string | What flows through it (see Section 5.3) |
| `ilos:port_size_mm` | float | Connection size in mm |
| `ilos:port_direction` | float3 | Unit vector pointing **outward** from product |

### 5.3 Port Medium Values

| Medium | Description | Typical Vendor |
|--------|-------------|---------------|
| `UPW` | Ultra Pure Water | Swagelok, Entegris |
| `CDA` | Clean Dry Air | SMC, Parker |
| `N2` | Nitrogen | Swagelok, AP Tech |
| `Exhaust` | Process exhaust | Edwards |
| `PCW` | Process Cooling Water | Parker, Swagelok |
| `Chemical` | Acid/Solvent | Entegris, Saint-Gobain |
| `Vacuum` | Vacuum line | Edwards, Pfeiffer |
| `Power` | Electrical power | Electrical vendor |
| `Signal` | Control signal | — |
| `CW` | Chilled Water | — |
| `WW` | Waste Water | — |

### 5.4 Examples by Product Type

**Ball Valve (2 connections):**
```
/Connections/
    Inlet   → pos:(-7.5, 0, 0)  dir:(-1, 0, 0)  type:Pipe  medium:UPW  size:50.8mm
    Outlet  → pos:(+7.5, 0, 0)  dir:(+1, 0, 0)  type:Pipe  medium:UPW  size:50.8mm
```

**Tee Fitting (3 connections):**
```
/Connections/
    Run_In  → pos:(-5.08, 0, 0) dir:(-1, 0, 0)  type:Pipe  size:50.8mm
    Run_Out → pos:(+5.08, 0, 0) dir:(+1, 0, 0)  type:Pipe  size:50.8mm
    Branch  → pos:(0, 0, +5.08) dir:(0, 0, +1)   type:Pipe  size:50.8mm
```

**EUV Scanner (8+ connections):**
```
/Connections/
    UPW_Supply    → pos:(-120, 50, 0)   dir:(-1, 0, 0)  type:Pipe  medium:UPW     size:25.4mm
    UPW_Return    → pos:(-120, -50, 0)  dir:(-1, 0, 0)  type:Pipe  medium:UPW     size:25.4mm
    CDA_Supply    → pos:(120, 50, 0)    dir:(+1, 0, 0)  type:Pipe  medium:CDA     size:12.7mm
    N2_Supply     → pos:(120, -50, 0)   dir:(+1, 0, 0)  type:Pipe  medium:N2      size:12.7mm
    Exhaust_Main  → pos:(0, -80, 300)   dir:(0, -1, 0)  type:Duct  medium:Exhaust size:200mm
    PCW_Supply    → pos:(-80, 0, 0)     dir:(-1, 0, 0)  type:Pipe  medium:PCW     size:50.8mm
    PCW_Return    → pos:(-80, -30, 0)   dir:(-1, 0, 0)  type:Pipe  medium:PCW     size:50.8mm
    Power_Main    → pos:(120, 0, -10)   dir:(+1, 0, 0)  type:Electrical medium:Power size:0
```

**Vacuum Pump (3 connections):**
```
/Connections/
    Inlet     → pos:(0, 0, 50)   dir:(0, 0, +1)   type:Pipe  medium:Vacuum  size:100mm
    Exhaust   → pos:(30, 0, 20)  dir:(+1, 0, 0)   type:Pipe  medium:Exhaust size:50mm
    N2_Purge  → pos:(-20, 0, 10) dir:(-1, 0, 0)   type:Pipe  medium:N2      size:6.35mm
```

---

## 6. Variant Sets: Black Box vs Assembly (Optional)

If your product has internal sub-components, you can provide two detail levels:

```usda
def Xform "SS_45S8_A" (
    variants = {
        string detail_level = "blackbox"
    }
    prepend variantSets = "detail_level"
)
{
    # Metadata and Connections are ALWAYS present (outside variant)
    custom string ilos:category = "Valve"
    custom string ilos:part_number = "VLV_ISOL_BALL_SS316L_2IN"
    # ...

    def Xform "Connections" { ... }  # Always available

    variantSet "detail_level" = {
        "blackbox" {
            # Simple external geometry only
            def Xform "Geometry" {
                def Mesh "Body" { ... }     # Solid exterior shape
                def Mesh "Handle" { ... }
            }
        }
        "assembly" {
            # Full internal breakdown
            def Xform "Geometry" {
                def Mesh "Valve_Body" { ... }
                def Mesh "Ball" { ... }
                def Mesh "Seat_1" { ... }
                def Mesh "Seat_2" { ... }
                def Mesh "Stem" { ... }
                def Mesh "Packing" { ... }
                def Mesh "Handle" { ... }
                def Mesh "Spring" { ... }
            }
        }
    }
}
```

**Rules:**
- `"blackbox"` variant is **required** — this is what your customer's ILOS loads
- `"assembly"` variant is **optional** — only if you use ILOS internally
- Metadata and Connections are **outside** the variant set — always accessible
- If you don't provide variants, your file is treated as blackbox by default

---

## 7. Geometry Requirements

| Requirement | Specification |
|-------------|--------------|
| Format | UsdGeom.Mesh |
| Max polygon count | ≤50,000 faces (blackbox) |
| Normals | Outward-facing |
| Origin | Center of base/mounting surface |
| Flow direction | Along X axis (for piping components) |

### Recommended Materials

```usda
def Material "Metal_SS316L"
{
    token outputs:surface.connect = </...Shader.outputs:surface>
    def Shader "Shader"
    {
        uniform token info:id = "UsdPreviewSurface"
        color3f inputs:diffuseColor = (0.75, 0.75, 0.78)
        float inputs:metallic = 0.9
        float inputs:roughness = 0.3
        token outputs:surface
    }
}
```

---

## 8. Validation Checklist

### Required (ALL vendors, ALL products)

- [ ] File opens in usdview or Omniverse without errors
- [ ] `metersPerUnit = 0.01` and `upAxis = "Z"`
- [ ] `ilos:category` present on root prim
- [ ] `ilos:part_number` present
- [ ] `ilos:manufacturer` and `ilos:model` present
- [ ] `ilos:material` present
- [ ] `ilos:weight_kg` present
- [ ] `ilos:length_mm`, `ilos:width_mm`, `ilos:height_mm` present
- [ ] At least one Connection point under `/Connections/`
- [ ] Each Connection has `ilos:port_type`, `ilos:port_size_mm`, `ilos:port_direction`
- [ ] Geometry renders correctly

### Piping Components (additional)

- [ ] `ilos:nominal_diameter` present
- [ ] `ilos:pressure_rating` present
- [ ] Connection positions match actual port locations on geometry

### Equipment (additional)

- [ ] Clearance values present
- [ ] All utility connections defined (UPW, CDA, Exhaust, PCW, Power, etc.)

---

## 9. Category Reference

| `ilos:category` | Products | Typical Vendors |
|------------------|----------|-----------------|
| `Valve` | Ball, gate, diaphragm, check, butterfly, needle | Swagelok, Entegris, SMC, Parker |
| `PipeFitting` | Elbow, tee, reducer, cap, union, cross | Swagelok, Parker, Valex |
| `Pipe` | Straight tubing, pipe spool | Valex, Dockweiler |
| `Filter` | Gas filter, liquid filter, strainer | Entegris, Pall |
| `Regulator` | Pressure regulator, back pressure | AP Tech, Swagelok |
| `Gauge` | Pressure gauge, flow meter | Brooks, Horiba |
| `FlexHose` | Flex hose, bellows | Swagelok, Parker |
| `Equipment` | Process tool, scanner, etcher | ASML, AMAT, TEL, LAM |
| `Pump` | Vacuum pump, chemical pump | Edwards, Ebara |
| `Tank` | Chemical tank, gas cabinet, VMB/VMP | Kinetics, Air Liquide |
| `HeatExchanger` | Chiller, heat exchanger | SMC, Parker |
| `AirHandler` | FFU, MAU, scrubber | Camfil, AAF |
| `Support` | Pipe hanger, equipment stand | Unistrut, Hilti |
| `CableTray` | Cable tray, conduit | Legrand, Cooper |
| `ElectricalPanel` | Panel board, MCC, transformer | Schneider, ABB |

---

## 10. Scene-Level vs Component-Level Attributes

**Important distinction:** The Vendor Spec defines **component-level** attributes (what the product IS). When ILOS places a component into a scene, **scene-level** attributes are added by the ILOS system, not by the vendor.

| Attribute | Defined By | Level | Purpose |
|-----------|-----------|-------|---------|
| `ilos:category` | **Vendor** | Component | What is this product |
| `ilos:part_number` | **Vendor** | Component | Product identity |
| `ilos:nominal_diameter` | **Vendor** | Component | Product specification |
| `/Connections/` | **Vendor** | Component | Where things connect |
| `ilos:level` | **ILOS** | Scene | Which floor (→ Revit Level) |
| `ilos:piping_system` | **ILOS** | Scene | Which system: UPW/CDA/PCW (→ Revit PipingSystemType) |
| `ilos:line_number` | **ILOS** | Scene | Pipe line ID: UPW-3F-001 (→ Revit System Name) |
| `ilos:connection_start` | **ILOS** | Scene | World coordinate of pipe start (→ Revit Pipe.Create) |
| `ilos:connection_end` | **ILOS** | Scene | World coordinate of pipe end (→ Revit Pipe.Create) |

**Vendors do NOT need to provide scene-level attributes.** These are generated automatically when ILOS places the component during layout optimization.

```
Vendor provides:                    ILOS adds at placement:
┌──────────────────────┐           ┌──────────────────────────┐
│ ss-45s8-a.usd        │           │ Scene USD                │
│                      │           │                          │
│ category: Valve      │     →     │ Reference → ss-45s8-a.usd│
│ diameter: 50.8mm     │  placed   │ position: (6000, 3050, 4500) │
│ manufacturer: Swagelok│  in scene │ level: FL2               │
│ connections: [in/out]│           │ piping_system: UPW       │
│                      │           │ line_number: UPW-3F-001  │
└──────────────────────┘           └──────────────────────────┘
```

---

## 11. End-to-End Traceability

Every vendor-provided attribute has a clear consumer at each stage:

```
Vendor USD           Omniverse              Revit                 Drawing Output
─────────────────────────────────────────────────────────────────────────────────
ilos:category    →   Placement rules    →   API selection     →   Correct sheet
ilos:part_number →   BOM counting       →   SharedParameter   →   Schedule/Tag
ilos:manufacturer→   BOM cost (SAP)     →   SharedParameter   →   Schedule
ilos:nominal_dia →   Pipe size match    →   Pipe.Create(dia)  →   Plan annotation
ilos:material    →   Compatibility chk  →   SharedParameter   →   Pipe schedule
ilos:weight_kg   →   Load calculation   →   SharedParameter   →   Structural calc
ilos:pressure_r  →   System validation  →   SharedParameter   →   P&ID annotation
ilos:cv          →   Flow calculation   →   SharedParameter   →   Flow calc sheet
ilos:insulation  →   Clearance calc     →   Pipe insulation   →   Insulation spec
port_direction   →   Auto pipe routing  →   Pipe endpoints    →   Correct routing
port_size_mm     →   Auto size match    →   Pipe diameter     →   Size annotation
port_medium      →   System assignment  →   PipingSystemType  →   Color/layer
```

---

## 12. FAQ

**Q: I make ball valves. Do I need to know about ASML or semiconductor fabs?**
A: No. Just follow this spec. Your valve will work in any ILOS system — fab, data center, or another vendor's assembly line.

**Q: Do I need to provide the "assembly" variant showing internal parts?**
A: No. Only the "blackbox" variant is required. Provide "assembly" only if you want to use ILOS for your own manufacturing.

**Q: What if my product has a proprietary connection?**
A: Define it with `ilos:port_standard = "Proprietary"` and provide the physical dimensions. ILOS will handle the adapter logic.

**Q: I already have STEP files. Can I just convert those?**
A: STEP provides geometry but not metadata or connection points. You can convert geometry, but you must add the `ilos:` attributes and `/Connections/` manually (or use ILOS-provided tooling).

**Q: What if I don't know the Revit or IFC mapping?**
A: Leave those fields empty. ILOS team will assign them.

**Q: Does the same file work in NVIDIA Omniverse and Autodesk Revit?**
A: Yes. ILOS reads the metadata and connection points to create native Revit elements. Your geometry is used for Omniverse visualization.

**Q: My product has 200,000 polygons. Is that OK?**
A: For the blackbox variant, simplify to ≤50,000. You can keep full detail in the assembly variant.

---

## 13. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-19 | Initial spec (split by equipment vs piping) |
| 2.0 | 2026-03-19 | Unified spec — same structure for ALL vendors based on recursive ILOS-[Domain] architecture; added Variant Set support, port_medium, port_type |
| 2.1 | 2026-03-19 | Added insulation attributes, Scene-Level vs Component-Level distinction, End-to-End Traceability matrix |
