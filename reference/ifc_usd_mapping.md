# IFC ↔ OpenUSD 語義映射表

> 本表定義 IFC 構件到 USD Prim 的對應關係
> Builder Agent 生成 IFC 和 USD 時必須遵循本表

| IFC Class | USD Prim Path Pattern | USD Type | USD Custom Properties |
|-----------|----------------------|----------|----------------------|
| IfcProject | /Project | Xform | bim:ifc_class |
| IfcSite | /Project/Site | Xform | bim:latitude, bim:longitude |
| IfcBuilding | /Project/Site/Building | Xform | bim:name |
| IfcBuildingStorey | .../Building/Storey_N | Xform | bim:elevation, bim:height |
| IfcWall | .../Storey_N/Wall_001 | Mesh | bim:thickness, bim:wall_type |
| IfcSlab | .../Storey_N/Slab | Mesh | bim:thickness, bim:slab_type |
| IfcColumn | .../Storey_N/Column_001 | Mesh | bim:width, bim:depth |
| IfcBeam | .../Storey_N/Beam_001 | Mesh | bim:width, bim:depth, bim:span |
| IfcDoor | .../Storey_N/Door_001 | Mesh | bim:width, bim:height, bim:door_type |
| IfcWindow | .../Storey_N/Window_001 | Mesh | bim:width, bim:height, bim:sill_height |
| IfcRoof | .../Building/Roof | Mesh | bim:roof_type |
| IfcSpace | .../Storey_N/Space_Name | Scope | bim:area, bim:space_type (invisible) |
| IfcStair | .../Storey_N/Stair_001 | Mesh | bim:stair_type, bim:riser_count |
| IfcRailing | .../Storey_N/Railing_001 | Mesh | bim:height |
| IfcCurtainWall | .../Storey_N/CurtainWall_001 | Mesh | bim:panel_width |
| IfcTransportElement (ELEVATOR) | .../Building/Elevator_001 | Xform | bim:capacity_kg, bim:speed_mps |
| IfcTransportElement (ESCALATOR) | .../Building/Escalator_001 | Mesh | bim:angle_deg, bim:width |
| IfcPipeSegment | .../MEP/Plumbing/Pipe_001 | Mesh | bim:diameter_mm, bim:system |
| IfcDuctSegment | .../MEP/HVAC/Duct_001 | Mesh | bim:width_mm, bim:height_mm |
| IfcCableCarrierSegment | .../MEP/Electrical/Tray_001 | Mesh | bim:width_mm |
| IfcFireSuppressionTerminal | .../MEP/Fire/Sprinkler_001 | Mesh | bim:coverage_sqm |
| IfcSanitaryTerminal | .../Storey_N/Toilet_001 | Mesh | bim:fixture_type |
| IfcLightFixture | .../Storey_N/Light_001 | Mesh | bim:wattage, bim:lumen |
| IfcMaterial | USD Material (UsdShade) | Material | bim:material_name |

## USD 場景設定

- Up Axis: Z (建築慣例)
- Meters Per Unit: 1.0
- BIM 語義: 透過 `bim:` namespace custom properties 保留
