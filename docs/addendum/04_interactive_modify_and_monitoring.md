# PromptBIMTestApp1 — 互動式修改 + 智慧監控點自動配置

> SKILL.md v3.0 Addendum #4
> 版本: v1.0.0 | 2026-03-25

---

## 模組 D：互動式即時修改 (Interactive Real-time Modification)

### D.1 概念

使用者在建築生成後，可以用**自然語言下達修改指令**，
系統即時重新計算並更新所有關聯資料：

```
用戶: "請修改 12 樓層改為 9 個樓層"

→ 系統即時更新:
  ✅ 3D 模型重新生成 (IFC + USD)
  ✅ 建蔽率/容積率重新計算
  ✅ 法規合規重新檢查 (高度限制可能從 FAIL → PASS)
  ✅ 施工時程重新排程 (4D 甘特圖縮短)
  ✅ 建設成本重新估算 (5D 減少 ~25%)
  ✅ MEP 管線重新路由 (少了 3 層的管路)
  ✅ 電梯/樓梯配置重新評估
  ✅ 結構尺寸重新建議 (柱可能從 60cm 降到 50cm)
  ✅ 監控點數量重新計算
```

### D.2 支援的修改類型

| 類別 | Prompt 範例 | 影響範圍 |
|------|-----------|----------|
| **樓層變更** | "改為 9 個樓層" | 全面重算 |
| | "加一層地下室" | 結構+MEP+成本 |
| | "頂樓改為露台" | 屋頂+容積率 |
| **空間調整** | "一樓加一間會議室" | 平面+隔間+MEP |
| | "把廚房移到北側" | 平面+管路 |
| | "每戶加一間衛浴" | 平面+管路+成本 |
| **結構變更** | "改用鋼構" | 結構+成本+工期 |
| | "柱距改為 8 米" | 結構+平面 |
| **設備變更** | "加一部電梯" | MEP+平面+成本 |
| | "改用 VRF 空調" | MEP+成本 |
| | "加設太陽能板" | 屋頂+電力+成本 |
| **外觀變更** | "外牆改帷幕牆" | 外殼+成本+能耗 |
| | "加雨遮" | 外殼+成本 |
| **用途變更** | "3 樓改為商場" | 平面+MEP+法規+成本 |
| | "地下改為停車場" | 全面重算 |
| **數值調整** | "層高改為 3.2 米" | 高度+結構+MEP |
| | "退縮增加到 6 米" | 平面+容積率 |

### D.3 修改引擎架構

```python
# agents/modifier.py

class ModifierAgent:
    """Agent 5: 互動式修改處理器"""

    SYSTEM_PROMPT = """
    You are a building modification analyst.
    Given the CURRENT BuildingPlan and a user's modification request,
    determine:

    1. modification_type: what category of change
    2. affected_components: which parts of the plan need updating
    3. delta_plan: the specific changes as a JSON patch
    4. impact_analysis: what downstream effects this has

    Rules:
    - NEVER regenerate from scratch — only modify the delta
    - Preserve all unchanged components exactly
    - Flag if the modification would violate building codes
    - Estimate the cost impact (increase/decrease percentage)
    - Estimate the schedule impact (days added/removed)
    """

    def process_modification(self, current_plan, user_request):
        """處理用戶修改指令"""
        # 1. Claude 分析修改意圖
        analysis = self.analyze(current_plan, user_request)

        # 2. 套用 delta 到 BuildingPlan
        new_plan = self.apply_delta(current_plan, analysis.delta_plan)

        # 3. 重新執行受影響的 pipeline 階段
        if analysis.affects_structure:
            self.rebuild_structure(new_plan)
        if analysis.affects_mep:
            self.reroute_mep(new_plan)
        if analysis.affects_cost:
            self.recalculate_cost(new_plan)
        if analysis.affects_schedule:
            self.reschedule(new_plan)
        if analysis.affects_compliance:
            self.recheck_compliance(new_plan)
        if analysis.affects_monitoring:
            self.reconfigure_monitors(new_plan)

        return new_plan
```

### D.4 影響傳播矩陣

當用戶修改某項目時，系統自動判斷哪些下游需要重算：

```
修改項目         → 結構 平面 MEP  法規 成本 工期 監控
─────────────────────────────────────────────────────
樓層數量增減     →  ✅   ✅   ✅   ✅   ✅   ✅   ✅
層高變更         →  ✅   ─   ✅   ✅   ✅   ─   ─
空間新增/移除    →  ─   ✅   ✅   ✅   ✅   ✅   ✅
空間位置移動     →  ─   ✅   ✅   ─   ─   ─   ✅
結構系統變更     →  ✅   ─   ─   ✅   ✅   ✅   ─
設備新增/移除    →  ─   ✅   ✅   ✅   ✅   ✅   ✅
外殼變更         →  ─   ─   ─   ✅   ✅   ✅   ─
用途變更         →  ─   ✅   ✅   ✅   ✅   ✅   ✅
數值微調         →  依項目判斷
```

### D.5 版本歷史與比較

每次修改保留歷史版本，可以比較差異：

```python
# schemas/result.py 擴充

class ModificationRecord(BaseModel):
    """修改紀錄"""
    version: int                  # 版本號 (1, 2, 3...)
    timestamp: str                # 修改時間
    user_request: str             # 用戶原始指令
    modification_type: str        # 修改類別
    delta_summary: str            # 變更摘要
    impact: ModificationImpact    # 影響分析
    plan_snapshot_path: str       # 該版本 BuildingPlan JSON 路徑

class ModificationImpact(BaseModel):
    """修改影響分析"""
    # 面積變化
    total_area_before_sqm: float
    total_area_after_sqm: float
    area_change_pct: float

    # 成本變化
    cost_before_twd: float
    cost_after_twd: float
    cost_change_pct: float

    # 工期變化
    schedule_before_days: int
    schedule_after_days: int
    schedule_change_days: int

    # 法規影響
    bcr_before: float
    bcr_after: float
    far_before: float
    far_after: float
    compliance_status: str  # "maintained" | "improved" | "degraded" | "violation"

    # 監控點變化
    monitor_points_before: int
    monitor_points_after: int
```

### D.6 GUI 整合 — 修改面板

```
┌─ Chat 面板 ──────────────────────────────────────────┐
│ 用戶: 請修改 12 樓層改為 9 個樓層                      │
│                                                      │
│ Claude: 🔄 分析修改影響中...                          │
│                                                      │
│ ┌─ 修改影響摘要 ────────────────────────────────────┐ │
│ │ 📊 樓層: 12F → 9F (-3 層)                        │ │
│ │ 📐 總面積: 5,400㎡ → 4,050㎡ (-25.0%)            │ │
│ │ 💰 預估成本: ¥162M → ¥121.5M (-25.0%)            │ │
│ │ 📅 預估工期: 540天 → 420天 (-120天)               │ │
│ │ ✅ 容積率: 544% → 408% (仍合規)                   │ │
│ │ ✅ 高度: 42m → 31.5m (從超限變為合規!)             │ │
│ │ 🔧 結構: RC柱可從 60cm 降至 50cm                  │ │
│ │ 🔌 監控點: 156個 → 117個 (-39個)                  │ │
│ └──────────────────────────────────────────────────┘ │
│                                                      │
│ [✅ 確認修改]  [↩️ 撤銷]  [📋 查看詳細比較]           │
└──────────────────────────────────────────────────────┘
```

---

## 模組 E：智慧監控點自動配置 (Auto Monitor & Control Points)

### E.1 概念

AI 根據建築設計自動建議在哪些位置設置**監測與控制 (M&C) 點**，
涵蓋 HVAC、機電、消防、結構安全等系統。

這些監控點是未來 **智慧建築 / BAS (Building Automation System)** 的基礎，
也與 Michael 的 **IDTF (Industrial Digital Twin Framework)** 直接對接。

### E.2 監控點分類體系

```
src/promptbim/bim/monitoring/
├── __init__.py
├── monitor_types.py       # 監控點類型定義
├── auto_placement.py      # AI 自動配置演算法
├── rules_engine.py        # 配置規則引擎
├── ifc_monitor.py         # IFC 輸出 (IfcSensor / IfcActuator)
├── usd_monitor.py         # USD 輸出 (Custom Properties)
└── dashboard_data.py      # 監控儀表板資料生成
```

### E.3 監控點類型定義 (全部 48 種)

```python
# bim/monitoring/monitor_types.py
from pydantic import BaseModel
from enum import Enum

class MonitorSystem(str, Enum):
    HVAC = "hvac"               # 空調系統
    ELECTRICAL = "electrical"   # 電力系統
    PLUMBING = "plumbing"       # 給排水
    FIRE = "fire_protection"    # 消防系統
    STRUCTURAL = "structural"   # 結構監測
    ELEVATOR = "elevator"       # 電梯系統
    SECURITY = "security"       # 安全系統
    ENERGY = "energy"           # 能源管理
    ENVIRONMENT = "environment" # 環境品質

class MonitorPointType(str, Enum):
    SENSOR = "sensor"           # 感測器 (只讀)
    ACTUATOR = "actuator"       # 致動器 (可控)
    METER = "meter"             # 計量表 (累計值)
    CONTROLLER = "controller"   # 控制器

class MonitorPointDef(BaseModel):
    """監控點定義"""
    id: str
    system: MonitorSystem
    point_type: MonitorPointType
    name_zh: str
    name_en: str
    description: str
    # 技術參數
    measurement: str        # 量測項目 (溫度/壓力/流量...)
    unit: str               # 單位 (°C, Pa, m³/h, kW...)
    protocol: str           # 通訊協定 (BACnet, Modbus, KNX, MQTT)
    # IFC 映射
    ifc_class: str          # IfcSensor / IfcActuator / IfcFlowMeter
    ifc_predefined_type: str
    # 配置規則
    placement_rule: str     # 配置位置描述
    density: str            # 配置密度 (e.g. "每層1個", "每100㎡ 1個")
    # 價格
    unit_price_twd: int     # 單價參考
    # 關聯設備
    related_equipment: list[str]  # 關聯的建築零件 ID
```

#### HVAC 空調監控 (12 種)

| ID | 名稱 | 量測 | 單位 | 配置規則 | 參考單價 |
|----|------|------|------|----------|----------|
| `hvac_temp_zone` | 區域溫度感測器 | 溫度 | °C | 每個空調區域 1 個 | ¥2,500 |
| `hvac_humidity_zone` | 區域濕度感測器 | 相對濕度 | %RH | 每個空調區域 1 個 | ¥3,000 |
| `hvac_co2_zone` | CO₂ 感測器 | CO₂ 濃度 | ppm | 每 200㎡ 1 個 | ¥8,000 |
| `hvac_duct_temp` | 風管溫度感測器 | 送/回風溫度 | °C | 每台 AHU 出/入口各 1 | ¥2,000 |
| `hvac_duct_pressure` | 風管靜壓感測器 | 靜壓 | Pa | 每台 AHU 1 個 | ¥5,000 |
| `hvac_airflow` | 風量感測器 | 風量 | m³/h | 每條主風管 1 個 | ¥12,000 |
| `hvac_vav_damper` | VAV 風量調節閥 | 開度 | % | 每個 VAV Box 1 個 | ¥15,000 |
| `hvac_chiller_temp` | 冰水機溫度 | 出/入水溫 | °C | 每台冰水機 2 個 | ¥3,000 |
| `hvac_chiller_flow` | 冰水流量計 | 流量 | m³/h | 每台冰水機 1 個 | ¥25,000 |
| `hvac_pump_status` | 泵浦運轉狀態 | 運轉/停止 | bool | 每台泵浦 1 個 | ¥1,500 |
| `hvac_filter_dp` | 濾網壓差感測器 | 壓差 | Pa | 每台 AHU 1 個 | ¥4,000 |
| `hvac_thermostat` | 溫控器 | 設定/回饋 | °C | 每個空調區域 1 個 | ¥5,000 |

#### 電力監控 (8 種)

| ID | 名稱 | 量測 | 配置規則 | 參考單價 |
|----|------|------|----------|----------|
| `elec_main_meter` | 總電表 | kWh/kW/V/A | 每棟 1 個 | ¥30,000 |
| `elec_floor_meter` | 樓層分電表 | kWh/kW | 每層 1 個 | ¥15,000 |
| `elec_panel_meter` | 配電盤電表 | kW/A | 每面配電盤 1 個 | ¥10,000 |
| `elec_ups_status` | UPS 狀態監控 | 電池/負載/旁路 | 每台 UPS 1 套 | ¥20,000 |
| `elec_generator_status` | 發電機監控 | 頻率/電壓/油位 | 每台 1 套 | ¥25,000 |
| `elec_transformer_temp` | 變壓器溫度 | 繞組溫度 | 每台 1 個 | ¥8,000 |
| `elec_power_quality` | 電力品質分析儀 | 諧波/功率因數 | 總配電 1 個 | ¥50,000 |
| `elec_lighting_ctrl` | 照明控制器 | 亮度/開關 | 每區域 1 個 | ¥3,500 |

#### 給排水監控 (6 種)

| ID | 名稱 | 量測 | 配置規則 | 參考單價 |
|----|------|------|----------|----------|
| `plumb_water_meter` | 水表 | m³/m³/h | 進水/每層各 1 | ¥8,000 |
| `plumb_water_pressure` | 水壓感測器 | kPa | 給水主管 + 頂層 | ¥5,000 |
| `plumb_pump_status` | 加壓泵浦狀態 | 運轉/故障 | 每台 1 個 | ¥1,500 |
| `plumb_tank_level` | 水箱液位計 | 液位 % | 每個水箱 1 個 | ¥6,000 |
| `plumb_leak_detect` | 漏水偵測器 | 有/無 | 機房/管道間 | ¥3,000 |
| `plumb_hot_water_temp` | 熱水溫度 | °C | 熱水器出口 | ¥2,000 |

#### 消防監控 (7 種)

| ID | 名稱 | 量測 | 配置規則 | 參考單價 |
|----|------|------|----------|----------|
| `fire_smoke_detect` | 煙霧偵測器 | 煙霧濃度 | 每 60㎡ 1 個 | ¥1,500 |
| `fire_heat_detect` | 定溫偵測器 | 溫度 | 廚房/機房 | ¥1,200 |
| `fire_sprinkler_flow` | 灑水流量開關 | 流量 | 每層主管 1 個 | ¥5,000 |
| `fire_hydrant_pressure` | 消防栓壓力 | kPa | 每層 1 個 | ¥4,000 |
| `fire_pump_status` | 消防泵浦狀態 | 運轉/故障 | 每台 1 套 | ¥8,000 |
| `fire_door_status` | 防火門監控 | 開/關 | 每扇防火門 | ¥2,500 |
| `fire_damper_status` | 防火風門狀態 | 開/關 | 每個防火風門 | ¥3,500 |

#### 電梯監控 (5 種)

| ID | 名稱 | 量測 | 配置規則 | 參考單價 |
|----|------|------|----------|----------|
| `elev_position` | 電梯位置 | 樓層 | 每部電梯 1 套 | ¥含在電梯 |
| `elev_door_status` | 電梯門狀態 | 開/關/故障 | 每部每層 | ¥含在電梯 |
| `elev_load` | 電梯載重 | kg | 每部 1 個 | ¥含在電梯 |
| `elev_run_status` | 運轉狀態 | 上/下/停/故障 | 每部 1 套 | ¥含在電梯 |
| `elev_emergency` | 緊急通話 | 通話狀態 | 每部 1 套 | ¥含在電梯 |

#### 結構監測 (4 種)

| ID | 名稱 | 量測 | 配置規則 | 參考單價 |
|----|------|------|----------|----------|
| `struct_tilt` | 傾斜計 | 角度 | 頂層 + 關鍵柱 | ¥35,000 |
| `struct_vibration` | 振動感測器 | 加速度 g | 基礎 + 頂層 | ¥25,000 |
| `struct_crack` | 裂縫計 | mm | 關鍵位置 | ¥15,000 |
| `struct_settlement` | 沉陷觀測點 | mm | 基礎角點 | ¥20,000 |

#### 環境/安全 (6 種)

| ID | 名稱 | 量測 | 配置規則 | 參考單價 |
|----|------|------|----------|----------|
| `env_outdoor_temp` | 室外溫度 | °C | 屋頂 1 個 | ¥3,000 |
| `env_outdoor_humidity` | 室外濕度 | %RH | 屋頂 1 個 | ¥3,000 |
| `env_wind_speed` | 風速計 | m/s | 屋頂 1 個 (高樓) | ¥15,000 |
| `env_rain_detect` | 雨量偵測 | 有/無 | 屋頂 1 個 | ¥5,000 |
| `sec_door_access` | 門禁讀卡器 | 進/出 | 主要出入口 | ¥8,000 |
| `sec_cctv` | 監視攝影機 | 影像 | 出入口+梯廳+停車場 | ¥12,000 |

### E.4 自動配置演算法

```python
# bim/monitoring/auto_placement.py

class MonitorAutoPlacement:
    """根據 BuildingPlan 自動計算所有監控點位置和數量"""

    def calculate(self, plan: BuildingPlan) -> list[MonitorPoint]:
        points = []

        # === HVAC ===
        for storey in plan.stories:
            for space in storey.spaces:
                # 每個空調區域: 溫度 + 濕度 + 溫控器
                if space.space_type not in ["corridor", "storage", "shaft"]:
                    points.append(self._place("hvac_temp_zone", storey, space))
                    points.append(self._place("hvac_humidity_zone", storey, space))
                    points.append(self._place("hvac_thermostat", storey, space))
                # CO2: 每 200㎡
                co2_count = max(1, int(space.area_sqm / 200))
                for i in range(co2_count):
                    points.append(self._place("hvac_co2_zone", storey, space, i))

        # === 電力 ===
        points.append(self._place_building("elec_main_meter"))  # 總電表
        for storey in plan.stories:
            points.append(self._place("elec_floor_meter", storey))  # 每層分電表
            points.append(self._place("elec_lighting_ctrl", storey))  # 照明控制

        # === 消防 ===
        for storey in plan.stories:
            total_area = sum(s.area_sqm for s in storey.spaces)
            smoke_count = max(1, int(total_area / 60))  # 每 60㎡
            for i in range(smoke_count):
                points.append(self._place("fire_smoke_detect", storey, idx=i))
            points.append(self._place("fire_sprinkler_flow", storey))
            # 防火門
            for opening in storey.openings:
                if opening.opening_type == "fire_door":
                    points.append(self._place("fire_door_status", storey, opening=opening))

        # === 電梯 ===
        elevator_count = self._count_elevators(plan)
        for i in range(elevator_count):
            for etype in ["elev_position", "elev_load", "elev_run_status", "elev_emergency"]:
                points.append(self._place_elevator(etype, i))

        # === 結構 (高樓 > 8F) ===
        if len(plan.stories) > 8:
            points.append(self._place_building("struct_tilt"))  # 頂層
            points.append(self._place_building("struct_vibration"))  # 基礎+頂層
            for corner in range(4):
                points.append(self._place_building("struct_settlement", idx=corner))

        # === 環境 ===
        points.append(self._place_building("env_outdoor_temp"))
        points.append(self._place_building("env_outdoor_humidity"))
        if len(plan.stories) > 10:
            points.append(self._place_building("env_wind_speed"))

        return points

    def get_summary(self, points: list) -> dict:
        """產生監控點摘要"""
        by_system = {}
        total_cost = 0
        for p in points:
            system = p.system.value
            by_system.setdefault(system, {"count": 0, "cost": 0})
            by_system[system]["count"] += 1
            by_system[system]["cost"] += p.unit_price_twd
            total_cost += p.unit_price_twd
        return {
            "total_points": len(points),
            "total_cost_twd": total_cost,
            "by_system": by_system,
        }
```

### E.5 IFC 輸出 — 監控點作為 IfcSensor / IfcActuator

```python
# bim/monitoring/ifc_monitor.py

def add_monitor_to_ifc(ifc, storey, point: MonitorPoint):
    """將監控點加入 IFC 模型"""
    if point.point_type == MonitorPointType.SENSOR:
        entity = api.run("root.create_entity", ifc,
            ifc_class="IfcSensor",
            predefined_type="TEMPERATURESENSOR"  # 依類型設定
        )
    elif point.point_type == MonitorPointType.ACTUATOR:
        entity = api.run("root.create_entity", ifc,
            ifc_class="IfcActuator",
            predefined_type="ELECTRICACTUATOR"
        )
    # 設定名稱和位置
    entity.Name = f"{point.system.value}_{point.id}_{point.index}"
    # 加入 PropertySet: 通訊協定、量測項目、單位
    pset = api.run("pset.add_pset", ifc, product=entity,
        name="Pset_MonitorControl")
    api.run("pset.edit_pset", ifc, pset=pset, properties={
        "Protocol": point.protocol,
        "Measurement": point.measurement,
        "Unit": point.unit,
        "SystemType": point.system.value,
    })
```

### E.6 USD 輸出 — 監控點視覺化

```python
# bim/monitoring/usd_monitor.py

def add_monitor_to_usd(stage, storey_path, point):
    """在 USD 場景中標記監控點位置（小球體圖標）"""
    path = f"{storey_path}/Monitors/{point.system.value}/{point.id}"
    sphere = UsdGeom.Sphere.Define(stage, path)
    sphere.GetRadiusAttr().Set(0.1)  # 10cm 小球標示

    # 依系統著色
    SYSTEM_COLORS = {
        "hvac": (0.2, 0.8, 0.2),       # 綠
        "electrical": (0.8, 0.2, 0.2), # 紅
        "plumbing": (0.2, 0.4, 0.8),   # 藍
        "fire_protection": (0.8, 0.8, 0.0),  # 黃
        "structural": (0.6, 0.3, 0.0), # 棕
        "elevator": (0.5, 0.5, 0.5),   # 灰
        "security": (0.8, 0.0, 0.8),   # 紫
    }

    # 監控點 metadata（IDTF 可直接讀取）
    prim = sphere.GetPrim()
    prim.CreateAttribute("monitor:system", Sdf.ValueTypeNames.String).Set(point.system.value)
    prim.CreateAttribute("monitor:type", Sdf.ValueTypeNames.String).Set(point.point_type.value)
    prim.CreateAttribute("monitor:protocol", Sdf.ValueTypeNames.String).Set(point.protocol)
    prim.CreateAttribute("monitor:measurement", Sdf.ValueTypeNames.String).Set(point.measurement)
    prim.CreateAttribute("monitor:unit", Sdf.ValueTypeNames.String).Set(point.unit)
```

### E.7 監控儀表板資料

AI 自動生成的監控點清單可匯出為儀表板設定：

```json
{
  "building": "L型辦公大樓",
  "total_monitor_points": 156,
  "total_monitor_cost_twd": 2850000,
  "systems": {
    "hvac": {
      "points": 68,
      "cost_twd": 850000,
      "items": [
        {"id": "hvac_temp_zone_1F_01", "location": "1F 大廳", "type": "sensor",
         "measurement": "溫度", "protocol": "BACnet", "unit": "°C"},
        {"id": "hvac_thermostat_2F_01", "location": "2F 辦公區A", "type": "controller",
         "measurement": "溫度設定", "protocol": "BACnet", "unit": "°C"}
      ]
    },
    "electrical": {"points": 24, "cost_twd": 380000},
    "fire_protection": {"points": 42, "cost_twd": 180000},
    "plumbing": {"points": 12, "cost_twd": 95000},
    "elevator": {"points": 8, "cost_twd": 0, "note": "含在電梯設備中"},
    "security": {"points": 14, "cost_twd": 145000},
    "structural": {"points": 6, "cost_twd": 200000},
    "environment": {"points": 4, "cost_twd": 26000}
  },
  "protocol_summary": {
    "BACnet": 82,
    "Modbus": 34,
    "KNX": 12,
    "MQTT": 28
  },
  "idtf_export": {
    "format": "OpenUSD + monitor: namespace",
    "note": "所有監控點以 USD Custom Properties 匯出，IDTF 可直接讀取"
  }
}
```

### E.8 GUI 整合 — 監控視圖

在 3D Tab 加入監控點顯示：

```
┌─ 3D 建築 + 監控點 ──────────────────────────┐
│                                             │
│  [3D 建築模型]                               │
│    🟢 溫度感測器                              │
│    🔴 配電盤電表                              │
│    🔵 水壓感測器                              │
│    🟡 煙霧偵測器                              │
│    🟤 傾斜計                                  │
│                                             │
│  ┌─ 監控系統開關 ─┐                          │
│  │ ☑ HVAC (68)    │                          │
│  │ ☑ 電力 (24)    │                          │
│  │ ☑ 消防 (42)    │                          │
│  │ ☐ 給排水 (12)  │                          │
│  │ ☐ 結構 (6)     │                          │
│  │ ☑ 安全 (14)    │                          │
│  └────────────────┘                          │
│                                             │
│  監控點合計: 156 個 | 預估費用: ¥285 萬       │
└─────────────────────────────────────────────┘
```

---

## 開發路線圖新增

### P4.8: 互動式修改引擎 (~2 天)
- [ ] `agents/modifier.py` — Modifier Agent (Claude 分析修改意圖)
- [ ] 影響傳播矩陣邏輯
- [ ] 版本歷史 + 差異比較
- [ ] GUI: 修改影響摘要面板 + 確認/撤銷
- [ ] 增量重算（只重算受影響部分）
- **驗收:** 用戶說"改為9層" → 即時更新所有關聯數據 + 顯示比較

### P8.5: 智慧監控點自動配置 (~3 天)
- [ ] `bim/monitoring/monitor_types.py` — 48 種監控點定義
- [ ] `bim/monitoring/auto_placement.py` — 自動配置演算法
- [ ] `bim/monitoring/rules_engine.py` — 配置密度規則
- [ ] `bim/monitoring/ifc_monitor.py` — IFC IfcSensor/IfcActuator 輸出
- [ ] `bim/monitoring/usd_monitor.py` — USD monitor: namespace 輸出
- [ ] `bim/monitoring/dashboard_data.py` — 儀表板 JSON 匯出
- [ ] `gui/monitor_toggle.py` — 3D 監控點顯示/隱藏開關
- [ ] 監控點成本加入 5D 估算
- **驗收:** 生成建築後一鍵 Auto Monitor → 顯示所有監控點 + 匯出清單

---

## 完整 POC Demo 流程（含修改和監控）

```
1. 用戶: "在 500 坪商三地上蓋 12 層辦公大樓"
   → AI 生成完整建築 + MEP + 法規 + 成本 + 監控點

2. 用戶: "請修改 12 樓層改為 9 個樓層"
   → 即時顯示影響:
     面積 -25%, 成本 -25%, 工期 -120天
     高度從超限變為合規 ✅
     監控點 156→117 個
   → [確認修改]

3. 用戶: "一樓改為商場, 加設電扶梯"
   → 即時更新:
     1F 平面重配置
     電扶梯 ×2 加入
     消防系統因商場標準升級
     成本 +¥12M
     監控點 +8 個（商場HVAC+消防）

4. 用戶: "顯示所有監控點"
   → 3D 視圖疊加彩色監控點
   → 左側顯示分系統統計
   → 匯出監控點清單 JSON

5. 匯出完整套件:
   ├── model_v3.ifc (含監控點 IfcSensor)
   ├── model_v3.usda (含 monitor: namespace)
   ├── modification_history.json (3 版本比較)
   ├── monitor_dashboard.json (156 個監控點)
   └── ... (所有其他輸出)
```

---

*Interactive Modify + Smart Monitoring Addendum v1.0 | 2026-03-25*
