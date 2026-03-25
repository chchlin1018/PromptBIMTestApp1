# PromptBIMTestApp1 — POC 擴充模組：施工模擬 + 成本估算 + MEP 管線

> SKILL.md v3.0 Addendum #2 — 三大 POC 模組
> 定位：概念驗證等級，展示完整 workflow，不追求生產級精度

---

## 模組 A：4D 施工模擬 (Construction Process Simulation)

### A.1 概念

把 3D 建築模型加上**時間軸**，模擬「從打地基到完工」的建設過程動畫。
每個構件（基礎→柱→梁→板→牆→門窗→MEP→裝修）依施工順序逐步顯現。

### A.2 POC 範圍

| 功能 | POC 做什麼 | 不做什麼 |
|------|-----------|---------|
| 施工排序 | AI 自動生成合理施工順序 | 不做 CPM/PERT 排程最佳化 |
| 時間軸 | 甘特圖 + 3D 動畫同步 | 不接 MS Project/P6 |
| 視覺化 | PyVista 逐步顯示構件 + 半透明/著色 | 不做工人/機具動畫 |
| 匯出 | GIF/MP4 動畫 + 甘特圖 SVG | 不輸出 NWD/Synchro 格式 |

### A.3 施工階段模板（AI 自動生成 → 可手動調整）

```python
# bim/simulation/construction_phases.py
STANDARD_PHASES = [
    # (phase_id, 名稱, IFC 構件類別, 預設工期比例)
    ("P01", "整地/開挖",      ["IfcSite"],                              0.05),
    ("P02", "基礎工程",       ["IfcFooting", "IfcPile"],                0.10),
    ("P03", "地下結構",       ["IfcWall:basement", "IfcSlab:basement"],  0.08),
    ("P04", "主體結構-柱",    ["IfcColumn"],                             0.10),
    ("P05", "主體結構-梁",    ["IfcBeam"],                               0.08),
    ("P06", "主體結構-板",    ["IfcSlab:floor"],                         0.08),
    ("P07", "剪力牆/核心筒",  ["IfcWall:shear"],                         0.05),
    ("P08", "屋頂",           ["IfcRoof"],                               0.04),
    ("P09", "外牆/帷幕牆",    ["IfcWall:exterior", "IfcCurtainWall"],    0.08),
    ("P10", "門窗安裝",       ["IfcDoor", "IfcWindow"],                  0.05),
    ("P11", "MEP 粗放",      ["IfcDuctSegment", "IfcPipeSegment"],      0.08),
    ("P12", "隔間牆",         ["IfcWall:partition"],                     0.05),
    ("P13", "電梯/電扶梯",   ["IfcTransportElement"],                   0.04),
    ("P14", "天花/地板裝修",  ["IfcCovering"],                           0.05),
    ("P15", "衛浴/設備安裝",  ["IfcSanitaryTerminal", "IfcFurniture"],   0.04),
    ("P16", "MEP 精裝",      ["IfcLightFixture", "IfcFireSuppression"],  0.03),
]
```

### A.4 PyVista 4D 動畫

```python
# viz/construction_anim.py
import pyvista as pv

class ConstructionAnimator:
    """4D 施工動畫生成器"""

    def __init__(self, building_meshes: dict[str, pv.PolyData], schedule: list):
        self.meshes = building_meshes   # component_id → mesh
        self.schedule = schedule         # [{phase, components, start_day, end_day}]

    def render_frame(self, day: int, plotter: pv.Plotter):
        """渲染某天的施工狀態"""
        for phase in self.schedule:
            for comp_id in phase["components"]:
                mesh = self.meshes.get(comp_id)
                if not mesh:
                    continue
                if day < phase["start_day"]:
                    pass  # 尚未開始 → 不顯示
                elif day < phase["end_day"]:
                    # 施工中 → 半透明 + 橘色
                    plotter.add_mesh(mesh, color="orange", opacity=0.5)
                else:
                    # 已完成 → 正常顯示
                    plotter.add_mesh(mesh, color="lightgray", opacity=1.0)

    def export_gif(self, output_path: str, total_days: int, fps: int = 10):
        """匯出施工動畫 GIF"""
        plotter = pv.Plotter(off_screen=True)
        plotter.open_gif(output_path)
        for day in range(0, total_days, max(1, total_days // (fps * 10))):
            plotter.clear()
            self.render_frame(day, plotter)
            plotter.write_frame()
        plotter.close()
```

### A.5 GUI 整合

在主視窗加一個「施工模擬」Tab：
- 時間軸滑桿（拖動看任意時間點的 3D 狀態）
- 播放/暫停按鈕
- 甘特圖面板（matplotlib，與 3D 同步高亮）
- 匯出 GIF 按鈕

---

## 模組 B：建設成本估算 (Cost Estimation / 5D BIM)

### B.1 概念

從 BIM 模型自動萃取**工料數量 (QTO)**，乘以單價得出估算成本。
POC 等級：用 AI 生成的合理單價，不接造價資料庫。

### B.2 POC 範圍

| 功能 | POC 做什麼 | 不做什麼 |
|------|-----------|---------|
| 數量計算 | 自動從 IFC 萃取面積/體積/長度 | 不做精確放樣/損耗計算 |
| 單價 | AI 建議 + 內建台灣參考單價表 | 不接 PCCES/營造公會資料庫 |
| 分類 | 依施工階段/構件類型分項 | 不做細項編碼（MasterFormat） |
| 報表 | 表格 + 圓餅圖 + 匯出 CSV | 不做投標文件/量價表 |

### B.3 QTO (Quantity Take-Off) 自動萃取

```python
# bim/cost/qto.py
import ifcopenshell
import ifcopenshell.util.element as element_util

class QuantityTakeOff:
    """從 IFC 模型萃取工料數量"""

    def __init__(self, ifc_path: str):
        self.ifc = ifcopenshell.open(ifc_path)

    def extract(self) -> list[dict]:
        items = []
        for wall in self.ifc.by_type("IfcWall"):
            qty = self._get_quantities(wall)
            items.append({
                "id": wall.GlobalId,
                "type": "牆體",
                "ifc_class": "IfcWall",
                "name": wall.Name or "Wall",
                "length_m": qty.get("Length", 0),
                "height_m": qty.get("Height", 0),
                "area_sqm": qty.get("NetSideArea", 0),
                "volume_m3": qty.get("NetVolume", 0),
            })
        # IfcSlab, IfcColumn, IfcBeam, IfcDoor, IfcWindow, etc.
        return items
```

### B.4 台灣參考單價表（POC 等級）

```python
# bim/cost/unit_prices_tw.py
"""台灣營建參考單價（2025-2026，概估用，非正式報價）"""

UNIT_PRICES_TWD = {
    # 結構
    "rc_concrete_m3":        {"price": 3200, "unit": "m³",  "desc": "RC混凝土 fc'280"},
    "rebar_ton":             {"price": 25000, "unit": "噸",  "desc": "SD420鋼筋"},
    "steel_structure_ton":   {"price": 45000, "unit": "噸",  "desc": "鋼構造（含加工安裝）"},
    "formwork_sqm":          {"price": 650,  "unit": "m²",  "desc": "模板工程"},
    # 外牆
    "brick_wall_sqm":        {"price": 1800, "unit": "m²",  "desc": "1B磚牆（含粉刷）"},
    "curtain_wall_sqm":      {"price": 12000,"unit": "m²",  "desc": "鋁帷幕牆"},
    "ext_paint_sqm":         {"price": 450,  "unit": "m²",  "desc": "外牆塗料"},
    # 內裝
    "partition_sqm":         {"price": 1200, "unit": "m²",  "desc": "輕隔間牆"},
    "ceiling_sqm":           {"price": 800,  "unit": "m²",  "desc": "輕鋼架天花板"},
    "raised_floor_sqm":      {"price": 2200, "unit": "m²",  "desc": "高架地板"},
    "floor_tile_sqm":        {"price": 1500, "unit": "m²",  "desc": "地磚鋪設（含材料）"},
    # 門窗
    "door_single":           {"price": 8000, "unit": "樘",  "desc": "鋁門 90x210cm"},
    "door_fire":             {"price": 18000,"unit": "樘",  "desc": "防火門 60min"},
    "window_sliding_sqm":    {"price": 6500, "unit": "m²",  "desc": "鋁推拉窗"},
    # MEP
    "hvac_sqm":              {"price": 3500, "unit": "m²",  "desc": "空調系統（含設備管路）"},
    "plumbing_sqm":          {"price": 1200, "unit": "m²",  "desc": "給排水"},
    "electrical_sqm":        {"price": 2000, "unit": "m²",  "desc": "電氣系統"},
    "fire_protection_sqm":   {"price": 800,  "unit": "m²",  "desc": "消防系統"},
    # 設備
    "elevator_unit":         {"price": 2500000,"unit":"台", "desc": "客用電梯（標準）"},
    "escalator_unit":        {"price": 4500000,"unit":"台", "desc": "電扶梯"},
    # 其他
    "site_work_sqm":         {"price": 1500, "unit": "m²",  "desc": "基地工程"},
    "landscaping_sqm":       {"price": 2500, "unit": "m²",  "desc": "景觀工程"},
}
```

### B.5 成本摘要輸出

```json
{
  "project": "L型辦公大樓",
  "total_cost_twd": 45680000,
  "cost_per_sqm_twd": 50755,
  "breakdown": [
    {"category": "結構工程", "cost": 15200000, "ratio": 0.333},
    {"category": "外殼工程", "cost": 8500000,  "ratio": 0.186},
    {"category": "室內裝修", "cost": 6800000,  "ratio": 0.149},
    {"category": "MEP 機電", "cost": 9500000,  "ratio": 0.208},
    {"category": "電梯設備", "cost": 2500000,  "ratio": 0.055},
    {"category": "門窗",     "cost": 1680000,  "ratio": 0.037},
    {"category": "基地景觀", "cost": 1500000,  "ratio": 0.033}
  ],
  "notes": "本估算為概估等級（±30%），僅供初期規劃參考"
}
```

---

## 模組 C：MEP 管線自動生成 (Auto MEP Routing)

### C.1 概念

根據建築平面，AI 自動規劃+生成四大管線系統：
- 🔵 **給排水 (Plumbing)** — 冷/熱水管、排水管、通氣管
- 🔴 **電力 (Electrical)** — 電纜管槽、配電路徑
- 🟢 **空調 (HVAC)** — 送風管、回風管、冷媒管
- 🟡 **消防 (Fire Protection)** — 灑水管、消防栓管

### C.2 POC 範圍

| 功能 | POC 做什麼 | 不做什麼 |
|------|-----------|---------|
| 管線路徑 | 3D orthogonal A* pathfinding | 不做壓損/風量計算 |
| 管徑 | AI 建議合理尺寸 | 不做工程計算 |
| 衝突 | 簡易碰撞偵測 (bounding box) | 不做細部 clash resolution |
| 設備定位 | 衛浴→水管 / 空調→風管 / 配電盤→電管 | 不做控制迴路 |
| IFC 輸出 | IfcDuctSegment / IfcPipeSegment / IfcCableCarrierSegment | 不做 fitting 細部 |
| 視覺化 | 顏色區分四大系統 + 透明建築疊合 | 不做 LOD400 |

### C.3 MEP 規劃邏輯

```
Step 1: 設備定位 (由 AI Planner 決定)
  ├─ 每層衛浴位置 → 給排水起點
  ├─ 每層空調出風口位置 → HVAC 起點
  ├─ 配電盤位置 → 電力起點
  └─ 灑水頭位置 → 消防起點

Step 2: 幹管路徑 (A* Pathfinding)
  ├─ 機房/管道間 → 各層垂直管井 (riser)
  ├─ 管井 → 走廊天花板空間 (水平主幹管)
  └─ 主幹管 → 各端點 (分支管)

Step 3: 管徑/尺寸 (規則表)
  ├─ HVAC: 主風管 600x400mm → 分支 300x200mm
  ├─ 給水: 主管 65mm → 分支 25mm
  ├─ 排水: 主管 100mm → 分支 50mm
  └─ 電力: 主槽 200x100mm → 分支 100x50mm

Step 4: 避障 + 層高分配
  天花板空間 (約 600mm) 分層:
  ├─ 頂層: HVAC 風管 (最大, 最優先)
  ├─ 中層: 消防灑水管 + 電力管槽
  └─ 底層: 給排水管
```

### C.4 3D Orthogonal A* Pathfinder

```python
# bim/mep/pathfinder.py
import heapq
import numpy as np

class MEPPathfinder:
    """3D 正交 A* 尋路（限制 90° 轉彎）"""

    DIRECTIONS = [
        (1,0,0), (-1,0,0),  # X±
        (0,1,0), (0,-1,0),  # Y±
        (0,0,1), (0,0,-1),  # Z±
    ]

    def __init__(self, grid_size: float = 0.3):
        self.grid = grid_size  # 格點大小(公尺)
        self.obstacles = set()  # 障礙格點

    def add_obstacles_from_building(self, walls, slabs, beams):
        """從建築構件生成障礙網格"""
        for element in walls + slabs + beams:
            for voxel in self._voxelize(element):
                self.obstacles.add(voxel)

    def find_path(self, start: tuple, end: tuple,
                  turn_penalty: float = 2.0) -> list[tuple]:
        """A* 尋路，含轉彎懲罰"""
        start_g = self._to_grid(start)
        end_g = self._to_grid(end)
        open_set = [(0, start_g, None)]  # (f_cost, pos, prev_dir)
        came_from = {}
        g_score = {start_g: 0}

        while open_set:
            f, current, prev_dir = heapq.heappop(open_set)
            if current == end_g:
                return self._reconstruct(came_from, current)

            for dx, dy, dz in self.DIRECTIONS:
                neighbor = (current[0]+dx, current[1]+dy, current[2]+dz)
                if neighbor in self.obstacles:
                    continue
                move_cost = self.grid
                # 轉彎懲罰
                curr_dir = (dx, dy, dz)
                if prev_dir and curr_dir != prev_dir:
                    move_cost += turn_penalty
                new_g = g_score[current] + move_cost
                if new_g < g_score.get(neighbor, float('inf')):
                    g_score[neighbor] = new_g
                    h = self._manhattan(neighbor, end_g)
                    heapq.heappush(open_set, (new_g + h, neighbor, curr_dir))
                    came_from[neighbor] = current
        return []  # 無路徑
```

### C.5 IFC MEP 輸出

```python
# bim/mep/ifc_mep.py
import ifcopenshell.api as api

class MEPGenerator:
    """MEP 管線 IFC 生成"""

    SYSTEM_COLORS = {
        "plumbing":  (0.2, 0.4, 0.8),   # 藍色
        "electrical": (0.8, 0.2, 0.2),   # 紅色
        "hvac":      (0.2, 0.8, 0.2),    # 綠色
        "fire":      (0.8, 0.8, 0.0),    # 黃色
    }

    def add_pipe_run(self, path: list, system: str, diameter_mm: float):
        """沿路徑生成管段"""
        for i in range(len(path) - 1):
            segment = api.run("root.create_entity", self.ifc,
                ifc_class="IfcPipeSegment" if system != "hvac" else "IfcDuctSegment",
                name=f"{system}_{i:03d}")
            # 設定幾何 (圓管或矩形管)
            # 設定 IfcSystem 歸屬
            # 設定材質顏色

    def add_elbow(self, position, direction_in, direction_out, system):
        """轉彎處加彎頭"""
        fitting = api.run("root.create_entity", self.ifc,
            ifc_class="IfcPipeFitting",
            predefined_type="BEND")
```

### C.6 MEP 系統定義（每棟建築的 MEP 清單）

```python
# bim/mep/systems.py
MEP_SYSTEM_TEMPLATES = {
    "office": {
        "hvac": {
            "type": "central_air",
            "equipment": ["rooftop_ahu"],
            "main_duct_mm": (600, 400),     # 寬x高
            "branch_duct_mm": (300, 200),
            "terminals_per_100sqm": 4,       # 出風口密度
        },
        "plumbing": {
            "cold_water_main_mm": 65,
            "cold_water_branch_mm": 25,
            "drain_main_mm": 100,
            "drain_branch_mm": 50,
            "fixtures": ["toilet", "sink", "urinal"],
        },
        "electrical": {
            "main_tray_mm": (200, 100),
            "branch_tray_mm": (100, 50),
            "panel_per_floor": 1,
            "outlets_per_100sqm": 20,
        },
        "fire_protection": {
            "sprinkler_main_mm": 65,
            "sprinkler_branch_mm": 25,
            "heads_per_sqm": 0.08,           # 每㎡灑水頭數
            "extinguisher_per_floor": 2,
        },
    }
}
```

---

## 新增專案結構

```
src/promptbim/
├── bim/
│   ├── simulation/              # 模組 A: 施工模擬
│   │   ├── __init__.py
│   │   ├── construction_phases.py   # 施工階段模板
│   │   ├── scheduler.py            # AI 排程生成
│   │   └── animator.py             # PyVista 4D 動畫
│   │
│   ├── cost/                    # 模組 B: 成本估算
│   │   ├── __init__.py
│   │   ├── qto.py                  # 數量萃取 (QTO)
│   │   ├── unit_prices_tw.py       # 台灣單價表
│   │   ├── estimator.py            # 成本計算引擎
│   │   └── report.py               # 報表生成 (CSV + 圖表)
│   │
│   └── mep/                     # 模組 C: MEP 管線
│       ├── __init__.py
│       ├── pathfinder.py           # 3D A* 正交尋路
│       ├── systems.py              # MEP 系統定義模板
│       ├── planner.py              # AI MEP 規劃 (設備定位+管徑)
│       ├── ifc_mep.py              # MEP IFC 生成
│       ├── usd_mep.py              # MEP USD 生成
│       └── clash_detect.py         # 簡易碰撞偵測
│
├── viz/
│   ├── construction_anim.py     # 施工動畫 (PyVista GIF)
│   ├── gantt_chart.py           # 甘特圖 (matplotlib)
│   ├── cost_charts.py           # 成本圓餅圖/長條圖
│   └── mep_overlay.py           # MEP 疊合顯示 (顏色區分)
│
└── gui/
    ├── simulation_tab.py        # 施工模擬 Tab (時間軸+3D)
    ├── cost_panel.py            # 成本估算面板
    └── mep_toggle.py            # MEP 系統顯示開關
```

---

## 新增開發路線圖

在原 P5 之後加入：

### P6: 成本估算 (~2 天)
- [ ] `bim/cost/qto.py` — IFC 數量萃取
- [ ] `bim/cost/unit_prices_tw.py` — 單價表
- [ ] `bim/cost/estimator.py` — 自動計算
- [ ] `viz/cost_charts.py` — 圓餅圖 + 長條圖
- [ ] `gui/cost_panel.py` — GUI 整合
- **驗收:** 生成建築後自動顯示估算總價 + 分項比例

### P7: MEP 管線自動生成 (~4 天)
- [ ] `bim/mep/pathfinder.py` — 3D A* 尋路
- [ ] `bim/mep/systems.py` — 系統模板
- [ ] `bim/mep/planner.py` — AI 決定設備位置+管徑
- [ ] `bim/mep/ifc_mep.py` + `usd_mep.py` — 雙輸出
- [ ] `bim/mep/clash_detect.py` — 基本碰撞偵測
- [ ] `viz/mep_overlay.py` — 四色管線疊合 3D
- [ ] `gui/mep_toggle.py` — 勾選顯示/隱藏各系統
- **驗收:** 生成建築後一鍵「Auto MEP」→ 四大系統管線出現 + IFC/USD 含 MEP

### P8: 施工模擬 (~3 天)
- [ ] `bim/simulation/construction_phases.py` — 階段模板
- [ ] `bim/simulation/scheduler.py` — AI 排程
- [ ] `bim/simulation/animator.py` — PyVista 動畫引擎
- [ ] `viz/construction_anim.py` + `viz/gantt_chart.py`
- [ ] `gui/simulation_tab.py` — 時間軸滑桿 + 播放
- [ ] 匯出 GIF/MP4
- **驗收:** 拖動滑桿看施工進度 + 匯出動畫 + 甘特圖

---

## Agent 擴充

### Agent 5: MEP Planner（新增）

```python
MEP_PLANNER_PROMPT = """
You are an MEP (Mechanical, Electrical, Plumbing) engineer.
Given a building plan with spaces and their functions, determine:

1. Equipment locations:
   - AHU/FCU positions for HVAC
   - Electrical panel positions
   - Plumbing riser positions
   - Fire sprinkler main positions

2. Terminal positions per room:
   - Supply/return air grilles (HVAC)
   - Power outlets and light fixtures (Electrical)
   - Sprinkler heads (Fire protection)
   - Plumbing fixtures based on room type (bathroom→toilet+sink, kitchen→sink)

3. Main riser/shaft positions (vertical distribution)

Output JSON with coordinates for all equipment and terminals.
Routing between them will be computed algorithmically.
"""
```

### Agent 6: Cost Advisor（新增，可選）

```python
COST_ADVISOR_PROMPT = """
You are a construction cost estimator for the Taiwan market.
Given a QTO (Quantity Take-Off) and unit price table,
review the estimate and provide:
1. Total cost validation (is it reasonable for this building type?)
2. Cost optimization suggestions (where can costs be reduced?)
3. Risk items (which costs might significantly exceed estimates?)
Output a structured review JSON.
"""
```

---

## 完整 POC Demo 流程

```
用戶: "在這塊300坪的地上蓋一棟5層辦公大樓"

→ AI 生成建築（P4 完成的功能）
  ├─ model.ifc + model.usda
  ├─ 2D 平面圖 + 3D 預覽
  └─ 建蔽率/容積率合規

→ 一鍵「Auto MEP」(P7)
  ├─ 🔵 給排水管線出現（藍色）
  ├─ 🔴 電力管槽出現（紅色）
  ├─ 🟢 空調風管出現（綠色）
  └─ 🟡 消防管線出現（黃色）

→ 「估算成本」(P6)
  ├─ 結構 ¥15.2M (33%)
  ├─ MEP  ¥9.5M (21%)
  ├─ 外殼 ¥8.5M (19%)
  ├─ ...
  └─ 總計 ¥45.7M (±30%)

→ 「模擬施工」(P8)
  ├─ 甘特圖顯示 16 個階段
  ├─ 拖動滑桿：Day 0→60→120→180→...
  ├─ 3D 建築逐步成形
  └─ 匯出動畫 GIF

→ 匯出完整套件
  ├─ model.ifc (建築+MEP)
  ├─ model.usda (建築+MEP)
  ├─ cost_estimate.csv
  ├─ construction_schedule.svg (甘特圖)
  ├─ construction_anim.gif
  ├─ floorplans/*.svg
  └─ summary.json
```

---

*POC Addendum v1.0 | 2026-03-25 | 施工模擬 + 成本估算 + MEP 自動管線*
