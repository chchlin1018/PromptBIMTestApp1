"""Fixture components — 9 types (sanitary + kitchen)."""

from promptbim.bim.components.base import (
    ComponentCategory,
    ComponentDef,
    PriceRange,
    SupplierInfo,
)

CAT = ComponentCategory.FIXTURE

FIXTURE_COMPONENTS = [
    ComponentDef(
        id="toilet_standard",
        category=CAT,
        name_zh="標準馬桶",
        name_en="Standard Toilet",
        ifc_class="IfcSanitaryTerminal",
        ifc_predefined_type="TOILETPAN",
        geometry_mode="mesh",
        parameters={
            "flush_volume_l": {"default": 6, "options": [3, 4.5, 6]},
        },
        suppliers=[
            SupplierInfo(
                name="TOTO",
                brand="TOTO",
                country="JP",
                price=PriceRange(
                    min_price=8000, max_price=25000, unit="per_unit", source="台灣市場參考價 2025"
                ),
            ),
            SupplierInfo(
                name="和成HCG",
                brand="HCG",
                country="TW",
                price=PriceRange(
                    min_price=5000, max_price=15000, unit="per_unit", source="台灣市場參考價 2025"
                ),
            ),
            SupplierInfo(
                name="凱撒",
                brand="CAESAR",
                country="TW",
                price=PriceRange(
                    min_price=5000, max_price=18000, unit="per_unit", source="台灣市場參考價 2025"
                ),
            ),
        ],
        ai_keywords=["馬桶", "toilet", "便器", "坐式馬桶"],
        ai_placement_rules="每間廁所隔間一個。無障礙廁所需加大空間+扶手。",
    ),
    ComponentDef(
        id="toilet_wall_hung",
        category=CAT,
        name_zh="壁掛馬桶",
        name_en="Wall-Hung Toilet",
        ifc_class="IfcSanitaryTerminal",
        ifc_predefined_type="TOILETPAN",
        geometry_mode="mesh",
        parameters={
            "seat_height_mm": {"default": 400, "min": 350, "max": 450},
        },
        ai_keywords=["壁掛馬桶", "wall-hung toilet", "懸壁式馬桶"],
        ai_placement_rules="需隱藏式水箱牆體。清潔方便，現代風格。",
    ),
    ComponentDef(
        id="urinal",
        category=CAT,
        name_zh="小便斗",
        name_en="Urinal",
        ifc_class="IfcSanitaryTerminal",
        ifc_predefined_type="URINAL",
        geometry_mode="mesh",
        parameters={
            "flush_volume_l": {"default": 2, "options": [0, 1, 2, 3]},
        },
        ai_keywords=["小便斗", "urinal", "小便器"],
        ai_placement_rules="男廁配置，間距>=60cm。可設無水型。",
    ),
    ComponentDef(
        id="sink_pedestal",
        category=CAT,
        name_zh="立柱洗手台",
        name_en="Pedestal Sink",
        ifc_class="IfcSanitaryTerminal",
        ifc_predefined_type="WASHHANDBASIN",
        geometry_mode="mesh",
        parameters={
            "width_mm": {"default": 500, "min": 400, "max": 700},
        },
        suppliers=[
            SupplierInfo(
                name="TOTO",
                brand="TOTO",
                country="JP",
                price=PriceRange(
                    min_price=3000, max_price=15000, unit="per_unit", source="台灣市場參考價 2025"
                ),
            ),
        ],
        ai_keywords=["洗手台", "洗臉盆", "sink", "wash basin", "pedestal sink"],
        ai_placement_rules="公廁每2-3個便器配一個洗手台。",
    ),
    ComponentDef(
        id="sink_counter",
        category=CAT,
        name_zh="檯面洗手台",
        name_en="Counter Sink",
        ifc_class="IfcSanitaryTerminal",
        ifc_predefined_type="WASHHANDBASIN",
        geometry_mode="mesh",
        parameters={
            "width_mm": {"default": 600, "min": 400, "max": 900},
        },
        ai_keywords=["檯面洗手台", "counter sink", "under-mount sink"],
        ai_placement_rules="嵌入檯面安裝，住宅浴室常用。",
    ),
    ComponentDef(
        id="bathtub",
        category=CAT,
        name_zh="浴缸",
        name_en="Bathtub",
        ifc_class="IfcSanitaryTerminal",
        ifc_predefined_type="BATH",
        geometry_mode="mesh",
        parameters={
            "length_mm": {"default": 1500, "min": 1200, "max": 1800},
            "width_mm": {"default": 700, "min": 600, "max": 900},
        },
        ai_keywords=["浴缸", "bathtub", "bath tub"],
        ai_placement_rules="住宅主浴室。需考慮結構載重（滿水約300kg）。",
    ),
    ComponentDef(
        id="shower_enclosure",
        category=CAT,
        name_zh="淋浴間",
        name_en="Shower Enclosure",
        ifc_class="IfcSanitaryTerminal",
        ifc_predefined_type="SHOWER",
        geometry_mode="mesh",
        parameters={
            "width_mm": {"default": 900, "min": 800, "max": 1200},
            "depth_mm": {"default": 900, "min": 800, "max": 1200},
        },
        suppliers=[
            SupplierInfo(
                name="GROHE",
                brand="GROHE",
                country="DE",
                price=PriceRange(
                    min_price=2000, max_price=12000, unit="per_set", source="台灣市場參考價 2025"
                ),
            ),
        ],
        ai_keywords=["淋浴", "shower", "淋浴間", "淋浴拉門"],
        ai_placement_rules="浴室乾濕分離。最小淨尺寸80x80cm。",
    ),
    ComponentDef(
        id="kitchen_counter",
        category=CAT,
        name_zh="廚房檯面",
        name_en="Kitchen Counter",
        ifc_class="IfcFurniture",
        parameters={
            "length_m": {"default": 2.4, "min": 1.2, "max": 6.0},
            "depth_m": {"default": 0.6, "min": 0.55, "max": 0.75},
            "height_m": {"default": 0.85, "min": 0.8, "max": 0.9},
        },
        ai_keywords=["廚房檯面", "kitchen counter", "流理台", "廚具"],
        ai_placement_rules="廚房必備。L型或一字型配置。",
    ),
    ComponentDef(
        id="kitchen_sink",
        category=CAT,
        name_zh="廚房水槽",
        name_en="Kitchen Sink",
        ifc_class="IfcSanitaryTerminal",
        ifc_predefined_type="SINK",
        geometry_mode="mesh",
        parameters={
            "width_mm": {"default": 800, "options": [600, 800, 1000]},
            "bowls": {"default": 2, "options": [1, 2]},
        },
        ai_keywords=["水槽", "廚房水槽", "kitchen sink", "洗碗槽"],
        ai_placement_rules="嵌入廚房檯面。需接排水管。",
    ),
]
