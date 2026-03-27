# Zigma Agent Protocol — C++ ↔ Python JSON Stdio

> **Version:** 1.0 | **Transport:** stdin/stdout, one JSON per line (`\n` delimited)

---

## Request (C++ → Python)

### generate

```json
{"type":"generate","prompt":"建立一個標準工廠","land":{"width":100,"depth":80}}
```

### modify

```json
{"type":"modify","intent":"變更游泳池成為員工停車場","undo":false}
```

### get_cost

```json
{"type":"get_cost"}
```

### get_schedule

```json
{"type":"get_schedule"}
```

---

## Response (Python → C++)

### status (streaming progress)

```json
{
  "type": "status",
  "stage": "planner",
  "message": "Generating floor plan...",
  "progress": 0.3
}
```

### result (generation complete)

```json
{
  "type": "result",
  "model": {
    "elements": [
      {
        "id": "1F_wall_0",
        "type": "wall",
        "material": "concrete",
        "vertices": [[0,0,0],[10,0,0],[10,0,3],[0,0,3],...],
        "indices": [[0,1,2],[0,2,3],...],
        "color": [0.6, 0.6, 0.6, 1.0],
        "dimensions": {"width": 10.0, "height": 3.0, "depth": 0.2},
        "cost": 150000,
        "story": 0
      }
    ],
    "element_count": 42,
    "stories": 3
  },
  "cost": {
    "project_name": "...",
    "total_cost_twd": 45000000,
    "total_floor_area_sqm": 2400,
    "cost_per_sqm_twd": 18750,
    "line_items": [...],
    "breakdown": [...]
  },
  "schedule": {
    "total_days": 360,
    "phases": [
      {
        "phase": "foundation",
        "start_day": 0,
        "end_day": 45,
        "duration_days": 45,
        "components": ["1F_slab", "foundation_0"]
      }
    ]
  },
  "summary": {
    "stories": 3,
    "bcr": 0.45,
    "far": 1.35,
    "footprint_area": 800
  },
  "success": true
}
```

### delta (modification result)

```json
{
  "type": "delta",
  "model": { "elements": [...], "element_count": 40, "stories": 3 },
  "cost": { "total_cost_twd": 43000000, ... },
  "schedule": { "total_days": 350, "phases": [...] },
  "modification": { "description": "Replaced pool with parking" }
}
```

### error

```json
{
  "type": "error",
  "message": "Failed to generate plan: insufficient land area",
  "traceback": "..."
}
```

---

## Element Types

| Type | Material | Description |
|------|----------|-------------|
| wall | concrete | Wall segment |
| slab | concrete | Floor slab |
| column | steel | Structural column |
| window | glass | Window opening |
| door | wood | Door opening |
| roof | concrete | Roof element |
| pool | glass | Swimming pool |
| parking | concrete | Parking area |

---

## Material Properties (PBR)

| Material | baseColor | roughness | metalness | opacity |
|----------|-----------|-----------|-----------|---------|
| concrete | (0.6,0.6,0.6) | 0.85 | 0.0 | 1.0 |
| glass | (0.7,0.85,1.0) | 0.05 | 0.0 | 0.3 |
| steel | (0.8,0.8,0.82) | 0.35 | 0.9 | 1.0 |
| wood | (0.55,0.35,0.15) | 0.75 | 0.0 | 1.0 |
