# PromptBIMTestApp1 — 建築零件庫 (Component Library) 補充規格

> SKILL.md v3.0 Addendum — 加入本節到 SKILL.md 第 4 節之後

---

## 建築零件語意庫 (Building Component Semantic Library)

### 設計原則

每個建築零件有三層定義：

```
Layer 1: 語意定義 (Semantic)
  → IFC Class + OmniClass/UniFormat 分類碼
  → 中英文名稱 + 描述
  → 參數化尺寸規格

Layer 2: 幾何生成 (Geometry)
  → 參數化 Python 函數（IfcOpenShell + pxr）
  → 或外部 3D 模型檔（GLB/OBJ）

Layer 3: 產品資訊 (Product Data)
  → 供應商 / 品牌
  → 參考價格區間
  → 產品型錄連結
```

---

### 完整零件分類表

```
src/promptbim/bim/components/
├── __init__.py
├── registry.py              # 零件註冊中心
├── base.py                  # BaseComponent 抽象類別
│
├── structural/              # A. 結構構件
│   ├── __init__.py
│   ├── foundation.py        # 基礎
│   ├── column.py            # 柱
│   ├── beam.py              # 梁
│   ├── slab.py              # 樓板
│   ├── rebar.py             # 鋼筋
│   ├── shear_wall.py        # 剪力牆
│   └── pile.py              # 基樁
│
├── envelope/                # B. 外殼/圍護
│   ├── __init__.py
│   ├── ext_wall.py          # 外牆
│   ├── curtain_wall.py      # 帷幕牆
│   ├── roof.py              # 屋頂
│   ├── parapet.py           # 女兒牆
│   └── canopy.py            # 雨遮/遮陽
│
├── interior/                # C. 室內隔間
│   ├── __init__.py
│   ├── partition.py         # 隔間牆
│   ├── ceiling.py           # 天花板
│   ├── raised_floor.py      # 高架地板
│   └── railing.py           # 欄杆/扶手
│
├── openings/                # D. 開口
│   ├── __init__.py
│   ├── door.py              # 門（單開/雙開/推拉/防火）
│   ├── window.py            # 窗（固定/推射/橫拉）
│   └── skylight.py          # 天窗
│
├── vertical_transport/      # E. 垂直運輸
│   ├── __init__.py
│   ├── elevator.py          # 電梯
│   ├── escalator.py         # 電扶梯
│   ├── stair.py             # 樓梯
│   └── ramp.py              # 坡道
│
├── mep/                     # F. 機電設備 (MEP)
│   ├── __init__.py
│   ├── hvac_unit.py         # 空調機組
│   ├── duct.py              # 風管
│   ├── pipe.py              # 管道
│   ├── sprinkler.py         # 消防灑水頭
│   ├── fire_extinguisher.py # 滅火器
│   ├── light_fixture.py     # 燈具
│   ├── electrical_panel.py  # 配電盤
│   └── transformer.py       # 變壓器
│
├── fixtures/                # G. 衛浴/固定設備
│   ├── __init__.py
│   ├── toilet.py            # 馬桶
│   ├── sink.py              # 洗手台
│   ├── shower.py            # 淋浴間
│   └── kitchen_counter.py   # 廚房檯面
│
├── site/                    # H. 基地/景觀
│   ├── __init__.py
│   ├── parking.py           # 停車位
│   ├── fence.py             # 圍牆
│   ├── tree.py              # 樹木
│   └── pavement.py          # 鋪面
│
└── models/                  # 外部 3D 模型快取
    ├── README.md            # 模型來源說明 + License
    ├── elevators/
    ├── escalators/
    ├── stairs/
    ├── fixtures/
    └── furniture/
```

---

### 零件語意定義 (ComponentDef Schema)

```python
# bim/components/base.py
from pydantic import BaseModel
from enum import Enum

class ComponentCategory(str, Enum):
    STRUCTURAL = "structural"
    ENVELOPE = "envelope"
    INTERIOR = "interior"
    OPENING = "opening"
    VERTICAL_TRANSPORT = "vertical_transport"
    MEP = "mep"
    FIXTURE = "fixture"
    SITE = "site"

class PriceRange(BaseModel):
    """參考價格區間"""
    currency: str = "TWD"
    min_price: float
    max_price: float
    unit: str              # "per_unit", "per_sqm", "per_m", "per_set"
    source: str = ""       # 價格來源說明
    updated: str = ""      # 價格更新日期

class SupplierInfo(BaseModel):
    """供應商資訊"""
    name: str              # 供應商名稱
    brand: str = ""        # 品牌
    model_number: str = "" # 型號
    catalog_url: str = ""  # 型錄連結
    country: str = ""      # 產地
    price: PriceRange | None = None

class ComponentDef(BaseModel):
    """建築零件完整定義"""
    # 識別
    id: str                        # "elevator_passenger_standard"
    category: ComponentCategory
    name_zh: str                   # "客用電梯"
    name_en: str                   # "Passenger Elevator"
    description_zh: str = ""
    description_en: str = ""

    # IFC 映射
    ifc_class: str                 # "IfcTransportElement"
    ifc_predefined_type: str = ""  # "ELEVATOR"
    omniclass_code: str = ""       # "23-21 11 11"
    uniformat_code: str = ""       # "D10"

    # 參數化尺寸 (預設值 + 允許範圍)
    parameters: dict[str, dict]    # {"width_m": {"default": 2.1, "min": 1.5, "max": 3.0}}

    # 3D 模型
    geometry_mode: str = "parametric"  # "parametric" (程式生成) | "mesh" (外部模型)
    mesh_file: str | None = None       # "models/elevators/passenger_standard.glb"
    mesh_source: str = ""              # 模型來源 URL
    mesh_license: str = ""             # CC0, CC-BY, MIT 等

    # 供應商 & 價格
    suppliers: list[SupplierInfo] = []

    # AI 提示詞 (幫助 LLM 理解何時使用)
    ai_keywords: list[str] = []    # ["電梯", "升降機", "elevator", "lift"]
    ai_placement_rules: str = ""   # "需要獨立電梯井道，通常位於核心筒"
```

---

### 完整零件清單 (74 種)

#### A. 結構構件 (Structural)

| ID | 中文 | English | IFC Class | OmniClass | 幾何模式 |
|----|------|---------|-----------|-----------|----------|
| `foundation_strip` | 條形基礎 | Strip Foundation | IfcFooting | 21-01 10 | parametric |
| `foundation_mat` | 筏式基礎 | Mat Foundation | IfcFooting | 21-01 10 | parametric |
| `foundation_pile` | 基樁 | Pile | IfcPile | 21-01 20 | parametric |
| `column_rc` | RC柱 | RC Column | IfcColumn | 21-02 10 10 | parametric |
| `column_steel` | 鋼柱 | Steel Column | IfcColumn | 21-02 10 20 | parametric |
| `beam_rc` | RC梁 | RC Beam | IfcBeam | 21-02 20 10 | parametric |
| `beam_steel` | 鋼梁 | Steel Beam | IfcBeam | 21-02 20 20 | parametric |
| `slab_rc` | RC樓板 | RC Slab | IfcSlab | 21-03 10 | parametric |
| `slab_post_tension` | 預力樓板 | Post-Tension Slab | IfcSlab | 21-03 10 | parametric |
| `rebar_main` | 主筋 | Main Rebar | IfcReinforcingBar | — | parametric |
| `rebar_stirrup` | 箍筋 | Stirrup | IfcReinforcingBar | — | parametric |
| `shear_wall` | 剪力牆 | Shear Wall | IfcWall | 21-02 30 | parametric |

#### B. 外殼/圍護 (Envelope)

| ID | 中文 | English | IFC Class | 幾何模式 |
|----|------|---------|-----------|----------|
| `wall_exterior_brick` | 磚造外牆 | Brick Exterior Wall | IfcWall | parametric |
| `wall_exterior_concrete` | 清水模外牆 | Exposed Concrete Wall | IfcWall | parametric |
| `wall_exterior_metal` | 金屬外牆 | Metal Panel Wall | IfcWall | parametric |
| `curtain_wall_glass` | 玻璃帷幕牆 | Glass Curtain Wall | IfcCurtainWall | parametric |
| `roof_flat` | 平屋頂 | Flat Roof | IfcRoof | parametric |
| `roof_gable` | 雙坡屋頂 | Gable Roof | IfcRoof | parametric |
| `roof_hip` | 四坡屋頂 | Hip Roof | IfcRoof | parametric |
| `roof_metal_deck` | 金屬屋面板 | Metal Deck Roof | IfcRoof | parametric |
| `parapet` | 女兒牆 | Parapet | IfcWall | parametric |
| `canopy` | 雨遮 | Canopy | IfcRoof | parametric |

#### C. 室內隔間 (Interior)

| ID | 中文 | English | IFC Class | 幾何模式 |
|----|------|---------|-----------|----------|
| `partition_drywall` | 輕隔間牆 | Drywall Partition | IfcWall | parametric |
| `partition_glass` | 玻璃隔間 | Glass Partition | IfcWall | parametric |
| `ceiling_suspended` | 輕鋼架天花板 | Suspended Ceiling | IfcCovering | parametric |
| `raised_floor` | 高架地板 | Raised Floor | IfcCovering | parametric |
| `railing_metal` | 金屬欄杆 | Metal Railing | IfcRailing | parametric |
| `railing_glass` | 玻璃欄杆 | Glass Railing | IfcRailing | parametric |

#### D. 開口 (Openings)

| ID | 中文 | English | IFC Class | 幾何模式 |
|----|------|---------|-----------|----------|
| `door_single_swing` | 單開門 | Single Swing Door | IfcDoor | parametric |
| `door_double_swing` | 雙開門 | Double Swing Door | IfcDoor | parametric |
| `door_sliding` | 推拉門 | Sliding Door | IfcDoor | parametric |
| `door_fire_rated` | 防火門 | Fire-Rated Door | IfcDoor | parametric |
| `door_revolving` | 旋轉門 | Revolving Door | IfcDoor | mesh |
| `door_glass_auto` | 自動玻璃門 | Auto Glass Door | IfcDoor | mesh |
| `window_fixed` | 固定窗 | Fixed Window | IfcWindow | parametric |
| `window_casement` | 推射窗 | Casement Window | IfcWindow | parametric |
| `window_sliding` | 橫拉窗 | Sliding Window | IfcWindow | parametric |
| `skylight` | 天窗 | Skylight | IfcWindow | parametric |

#### E. 垂直運輸 (Vertical Transport) ⭐

| ID | 中文 | English | IFC Class | 幾何模式 |
|----|------|---------|-----------|----------|
| `elevator_passenger` | 客用電梯 | Passenger Elevator | IfcTransportElement | mesh+param |
| `elevator_freight` | 貨梯 | Freight Elevator | IfcTransportElement | mesh+param |
| `elevator_service` | 服務電梯 | Service Elevator | IfcTransportElement | mesh+param |
| `escalator_30deg` | 電扶梯(30°) | Escalator 30° | IfcTransportElement | mesh+param |
| `escalator_35deg` | 電扶梯(35°) | Escalator 35° | IfcTransportElement | mesh+param |
| `moving_walkway` | 電動步道 | Moving Walkway | IfcTransportElement | mesh+param |
| `stair_straight` | 直跑樓梯 | Straight Stair | IfcStair | parametric |
| `stair_l_shaped` | L型樓梯 | L-Shaped Stair | IfcStair | parametric |
| `stair_u_shaped` | U型樓梯 | U-Shaped Stair | IfcStair | parametric |
| `stair_spiral` | 旋轉樓梯 | Spiral Stair | IfcStair | parametric |
| `ramp_straight` | 直線坡道 | Straight Ramp | IfcRamp | parametric |
| `ramp_curved` | 弧形坡道 | Curved Ramp | IfcRamp | parametric |

#### F. 機電設備 (MEP)

| ID | 中文 | English | IFC Class | 幾何模式 |
|----|------|---------|-----------|----------|
| `ahu_rooftop` | 屋頂空調箱 | Rooftop AHU | IfcUnitaryEquipment | mesh |
| `fcu` | 風機盤管 | Fan Coil Unit | IfcUnitaryEquipment | mesh |
| `duct_rectangular` | 矩形風管 | Rectangular Duct | IfcDuctSegment | parametric |
| `pipe_water` | 給水管 | Water Pipe | IfcPipeSegment | parametric |
| `sprinkler_head` | 消防灑水頭 | Sprinkler Head | IfcFireSuppressionTerminal | mesh |
| `fire_extinguisher` | 滅火器 | Fire Extinguisher | IfcFireSuppressionTerminal | mesh |
| `light_recessed` | 嵌燈 | Recessed Light | IfcLightFixture | mesh |
| `light_panel` | 平板燈 | Panel Light | IfcLightFixture | parametric |
| `electrical_panel` | 配電盤 | Electrical Panel | IfcElectricDistributionBoard | mesh |
| `transformer` | 變壓器 | Transformer | IfcTransformer | mesh |
| `generator` | 發電機 | Generator | IfcElectricGenerator | mesh |

#### G. 衛浴/固定設備 (Fixtures)

| ID | 中文 | English | IFC Class | 幾何模式 |
|----|------|---------|-----------|----------|
| `toilet_standard` | 標準馬桶 | Standard Toilet | IfcSanitaryTerminal | mesh |
| `toilet_wall_hung` | 壁掛馬桶 | Wall-Hung Toilet | IfcSanitaryTerminal | mesh |
| `urinal` | 小便斗 | Urinal | IfcSanitaryTerminal | mesh |
| `sink_pedestal` | 立柱洗手台 | Pedestal Sink | IfcSanitaryTerminal | mesh |
| `sink_counter` | 檯面洗手台 | Counter Sink | IfcSanitaryTerminal | mesh |
| `bathtub` | 浴缸 | Bathtub | IfcSanitaryTerminal | mesh |
| `shower_enclosure` | 淋浴間 | Shower Enclosure | IfcSanitaryTerminal | mesh |
| `kitchen_counter` | 廚房檯面 | Kitchen Counter | IfcFurniture | parametric |
| `kitchen_sink` | 廚房水槽 | Kitchen Sink | IfcSanitaryTerminal | mesh |

#### H. 基地/景觀 (Site)

| ID | 中文 | English | IFC Class | 幾何模式 |
|----|------|---------|-----------|----------|
| `parking_standard` | 標準停車位 | Standard Parking | IfcSpace | parametric |
| `parking_accessible` | 無障礙停車位 | Accessible Parking | IfcSpace | parametric |
| `fence_metal` | 金屬圍牆 | Metal Fence | IfcBuildingElementProxy | parametric |
| `tree_deciduous` | 落葉喬木 | Deciduous Tree | IfcGeographicElement | mesh |
| `tree_evergreen` | 常綠喬木 | Evergreen Tree | IfcGeographicElement | mesh |
| `pavement_concrete` | 混凝土鋪面 | Concrete Pavement | IfcSlab | parametric |

---

### 免費 3D 模型來源

以下模型庫提供可商用的免費 3D 模型，用於 `mesh` 模式零件：

| 來源 | 網址 | 格式 | License | 建築零件數量 | 適用類別 |
|------|------|------|---------|-------------|---------|
| **BIMobject** | bimobject.com | IFC/RFA/SKP | 免費（廠商提供）| 數萬 | 電梯/衛浴/燈具/門窗 |
| **Sketchfab** | sketchfab.com | glTF/OBJ | CC0/CC-BY | 800K+ 免費 | 家具/設備/景觀 |
| **CGTrader** | cgtrader.com | OBJ/FBX/glTF | 免費+付費 | 150K+ 免費 | 全類別 |
| **Free3D** | free3d.com | OBJ/FBX/3DS | 個人免費 | 10K+ | 家具/設備 |
| **Clara.io** | clara.io | OBJ/FBX | 多種 | 100K+ | 全類別 |
| **3D Warehouse** | 3dwarehouse.sketchup.com | SKP | 免費 | 5.6M+ | 建築/家具/景觀 |
| **Polyhaven** | polyhaven.com | glTF | CC0 | 400+ (高品質) | 資產/材質/HDRI |
| **OpenGameArt** | opengameart.org | OBJ/glTF | CC0/CC-BY | 數千 | 通用 3D |
| **GrabCAD** | grabcad.com | STEP/OBJ | 免費 | 數百萬 | 工程零件/設備 |
| **CADmapper** | cadmapper.com | DXF | 免費(1km²) | — | 基地環境/地形 |

**模型選用策略：** 每種零件類型僅保留 1-3 個代表性模型（不追求數量），優先選 CC0/CC-BY license 的 glTF 格式。下載後轉存為 GLB 統一格式。

---

### 供應商 & 價格資料庫

#### 電梯供應商

| 品牌 | 型號範例 | 類型 | 參考價格 (TWD) | 產地 | 目錄 |
|------|---------|------|---------------|------|------|
| OTIS 奧的斯 | Gen2 Comfort | 客梯 | 2,500,000~4,500,000/台 | 美國 | otis.com |
| KONE 通力 | MonoSpace 500 | 客梯 | 2,200,000~4,000,000/台 | 芬蘭 | kone.com |
| Schindler 迅達 | 3300AP | 客梯 | 2,000,000~3,800,000/台 | 瑞士 | schindler.com |
| ThyssenKrupp 蒂森克虜伯 | Synergy 300 | 客梯 | 1,800,000~3,500,000/台 | 德國 | tkelevator.com |
| 三菱電機 | NEXIEZ-LITE | 客梯 | 2,000,000~3,600,000/台 | 日本 | mitsubishielectric.com |
| 日立 | Standard-III | 客梯 | 1,900,000~3,400,000/台 | 日本 | hitachi.com |
| 永大電機 | YHP | 客梯 | 1,500,000~2,800,000/台 | 台灣 | yungtay.com |

#### 電扶梯供應商

| 品牌 | 型號範例 | 參考價格 (TWD) | 備註 |
|------|---------|---------------|------|
| KONE | TransitMaster 140 | 3,500,000~6,000,000/台 | 重載型 |
| Schindler | 9300AE | 3,000,000~5,500,000/台 | 標準型 |
| OTIS | 506NCE | 3,200,000~5,800,000/台 | 節能型 |
| 三菱電機 | Series-Z | 3,000,000~5,200,000/台 | 商場型 |

#### 結構材料

| 材料 | 規格 | 參考價格 (TWD) | 單位 | 來源 |
|------|------|---------------|------|------|
| RC 混凝土 | fc'=280 kgf/cm² | 2,800~3,500 | /m³ | 台灣預拌混凝土公會 |
| 鋼筋 | SD420 #6 | 22,000~28,000 | /噸 | 台灣鋼鐵公會 |
| H型鋼 | H400x200 | 28,000~35,000 | /噸 | 東和鋼鐵 |
| 磁磚 | 60x60 拋光 | 350~800 | /㎡ | 冠軍磁磚 |
| 石材 | 花崗石 30mm | 2,500~6,000 | /㎡ | 台灣石材公會 |

#### 門窗

| 類型 | 規格 | 參考價格 (TWD) | 品牌範例 |
|------|------|---------------|---------|
| 鋁門 | 90x210cm 單開 | 4,500~8,000 | 力霸鋁門窗、YKK AP |
| 防火門 | 90x210cm 60min | 12,000~25,000 | 三和、正新 |
| 鋁窗 (推射) | 120x150cm | 6,000~15,000 | 力霸、正新、氣密窗 |
| 帷幕牆 | 單元式 | 8,000~20,000/㎡ | 台玻、旭硝子 |

#### 衛浴

| 類型 | 參考價格 (TWD) | 品牌範例 |
|------|---------------|---------|
| 馬桶（標準） | 5,000~25,000 | TOTO、凱撒、和成 HCG |
| 洗手台 | 3,000~15,000 | TOTO、凱撒、American Standard |
| 淋浴龍頭組 | 2,000~12,000 | GROHE、hansgrohe、凱撒 |

> **價格說明：** 所有價格為台灣市場 2025-2026 參考區間，含稅不含安裝。
> 實際價格依規格、數量、工程條件而異。僅供 AI 生成估算用，不作為正式報價。

---

### Component Registry 程式模式

```python
# bim/components/registry.py
from typing import Dict
from .base import ComponentDef, ComponentCategory

class ComponentRegistry:
    """建築零件註冊中心 — 所有零件的 SSOT"""

    _components: Dict[str, ComponentDef] = {}

    @classmethod
    def register(cls, component: ComponentDef):
        cls._components[component.id] = component

    @classmethod
    def get(cls, component_id: str) -> ComponentDef:
        return cls._components[component_id]

    @classmethod
    def search(cls, keywords: list[str], category: ComponentCategory = None) -> list[ComponentDef]:
        """AI Agent 用：依關鍵字搜尋零件"""
        results = []
        for comp in cls._components.values():
            if category and comp.category != category:
                continue
            all_keywords = comp.ai_keywords + [comp.name_zh, comp.name_en]
            if any(kw.lower() in " ".join(all_keywords).lower() for kw in keywords):
                results.append(comp)
        return results

    @classmethod
    def list_by_category(cls, category: ComponentCategory) -> list[ComponentDef]:
        return [c for c in cls._components.values() if c.category == category]

# 註冊範例
ComponentRegistry.register(ComponentDef(
    id="elevator_passenger",
    category=ComponentCategory.VERTICAL_TRANSPORT,
    name_zh="客用電梯",
    name_en="Passenger Elevator",
    ifc_class="IfcTransportElement",
    ifc_predefined_type="ELEVATOR",
    omniclass_code="23-21 11 11",
    parameters={
        "shaft_width_m":  {"default": 2.1, "min": 1.6, "max": 3.0},
        "shaft_depth_m":  {"default": 2.4, "min": 1.8, "max": 3.5},
        "door_width_m":   {"default": 0.9, "min": 0.8, "max": 1.4},
        "capacity_kg":    {"default": 1000, "min": 450, "max": 2500},
        "speed_mps":      {"default": 1.0, "min": 0.5, "max": 6.0},
        "stops":          {"default": 5, "min": 2, "max": 50},
    },
    geometry_mode="mesh+param",
    mesh_file="models/elevators/passenger_standard.glb",
    mesh_source="sketchfab.com (CC0)",
    mesh_license="CC0",
    suppliers=[
        SupplierInfo(
            name="永大電機", brand="YUNGTAY", model_number="YHP",
            catalog_url="https://www.yungtay.com",
            country="TW",
            price=PriceRange(min_price=1500000, max_price=2800000,
                           unit="per_unit", currency="TWD",
                           source="台灣市場參考價 2025")
        ),
        SupplierInfo(
            name="OTIS", brand="OTIS", model_number="Gen2 Comfort",
            catalog_url="https://www.otis.com",
            country="US",
            price=PriceRange(min_price=2500000, max_price=4500000,
                           unit="per_unit", currency="TWD",
                           source="台灣代理商參考價 2025")
        ),
    ],
    ai_keywords=["電梯", "升降機", "客梯", "elevator", "lift", "passenger lift"],
    ai_placement_rules="需獨立電梯井道（shaft），通常位於建築核心筒。井道尺寸依載重量和速度決定。每棟建築至少1台，8層以上強制設置。無障礙電梯至少1台。",
))
```

---

### Agent 如何使用零件庫

Planner Agent 的 prompt 中注入可用零件列表：

```python
# agents/planner.py 動態生成 prompt 片段
def get_component_context() -> str:
    """為 Planner Agent 生成零件庫摘要"""
    lines = ["## Available Building Components\n"]
    for cat in ComponentCategory:
        comps = ComponentRegistry.list_by_category(cat)
        if comps:
            lines.append(f"### {cat.value}")
            for c in comps:
                price_info = ""
                if c.suppliers:
                    prices = [s.price for s in c.suppliers if s.price]
                    if prices:
                        min_p = min(p.min_price for p in prices)
                        max_p = max(p.max_price for p in prices)
                        price_info = f" | ~{min_p:,.0f}~{max_p:,.0f} {prices[0].currency}"
                lines.append(f"- `{c.id}`: {c.name_zh} ({c.name_en}){price_info}")
    return "\n".join(lines)
```

這樣 Planner 在規劃時就知道有哪些零件可用、大概多少錢。

---

### 新增到開發路線圖

在 P2 和 P4 之間插入：

#### P2.5: 建築零件庫 (~3 天)
- [ ] `bim/components/base.py` — ComponentDef + Registry
- [ ] 結構構件 (12 種) 參數化生成
- [ ] 垂直運輸 (12 種) 參數化 + mesh 佔位
- [ ] 開口 (10 種) 參數化生成
- [ ] 其他類別佔位定義 (40+ 種)
- [ ] 從 Sketchfab/BIMobject 下載 5-10 個免費 GLB 模型
- [ ] 供應商/價格 JSON seed data
- [ ] Agent prompt 注入零件庫 context
- **驗收:** `ComponentRegistry.search(["電梯"])` 回傳完整定義含供應商資訊

---

*Component Library Addendum v1.0 | 2026-03-25*
