"""Opening components — 10 types (doors + windows)."""

from promptbim.bim.components.base import (
    ComponentCategory,
    ComponentDef,
    PriceRange,
    SupplierInfo,
)

CAT = ComponentCategory.OPENING

OPENING_COMPONENTS = [
    ComponentDef(
        id="door_single_swing",
        category=CAT,
        name_zh="單開門",
        name_en="Single Swing Door",
        ifc_class="IfcDoor",
        ifc_predefined_type="DOOR",
        parameters={
            "width_m": {"default": 0.9, "min": 0.75, "max": 1.2},
            "height_m": {"default": 2.1, "min": 2.0, "max": 2.4},
        },
        suppliers=[
            SupplierInfo(
                name="力霸鋁門窗", brand="力霸", country="TW",
                price=PriceRange(min_price=4500, max_price=8000, unit="per_unit", source="台灣市場參考價 2025"),
            ),
        ],
        ai_keywords=["門", "單開門", "door", "single door", "swing door"],
        ai_placement_rules="標準房間門，淨寬>=75cm。無障礙>=90cm。",
    ),
    ComponentDef(
        id="door_double_swing",
        category=CAT,
        name_zh="雙開門",
        name_en="Double Swing Door",
        ifc_class="IfcDoor",
        ifc_predefined_type="DOOR",
        parameters={
            "width_m": {"default": 1.8, "min": 1.4, "max": 2.4},
            "height_m": {"default": 2.1, "min": 2.0, "max": 2.4},
        },
        ai_keywords=["雙開門", "double door", "對開門"],
        ai_placement_rules="大廳入口、會議室。淨寬>=140cm。",
    ),
    ComponentDef(
        id="door_sliding",
        category=CAT,
        name_zh="推拉門",
        name_en="Sliding Door",
        ifc_class="IfcDoor",
        ifc_predefined_type="SLIDING_TO_LEFT",
        parameters={
            "width_m": {"default": 1.5, "min": 0.9, "max": 3.0},
            "height_m": {"default": 2.1, "min": 2.0, "max": 2.4},
        },
        ai_keywords=["推拉門", "拉門", "sliding door"],
        ai_placement_rules="空間有限處、陽台門。不佔旋轉空間。",
    ),
    ComponentDef(
        id="door_fire_rated",
        category=CAT,
        name_zh="防火門",
        name_en="Fire-Rated Door",
        ifc_class="IfcDoor",
        ifc_predefined_type="DOOR",
        parameters={
            "width_m": {"default": 0.9, "min": 0.9, "max": 1.2},
            "height_m": {"default": 2.1, "min": 2.0, "max": 2.4},
            "fire_rating_min": {"default": 60, "options": [30, 60, 90, 120]},
        },
        suppliers=[
            SupplierInfo(
                name="三和防火門", brand="三和", country="TW",
                price=PriceRange(min_price=12000, max_price=25000, unit="per_unit", source="台灣市場參考價 2025"),
            ),
        ],
        ai_keywords=["防火門", "fire door", "fire-rated", "防火時效"],
        ai_placement_rules="防火區劃邊界、安全梯出入口必設。",
    ),
    ComponentDef(
        id="door_revolving",
        category=CAT,
        name_zh="旋轉門",
        name_en="Revolving Door",
        ifc_class="IfcDoor",
        ifc_predefined_type="REVOLVING",
        geometry_mode="mesh",
        parameters={
            "diameter_m": {"default": 2.4, "min": 1.8, "max": 3.6},
        },
        ai_keywords=["旋轉門", "revolving door"],
        ai_placement_rules="商業大樓大廳入口，空調節能效果佳。",
    ),
    ComponentDef(
        id="door_glass_auto",
        category=CAT,
        name_zh="自動玻璃門",
        name_en="Auto Glass Door",
        ifc_class="IfcDoor",
        ifc_predefined_type="SLIDING_TO_LEFT",
        geometry_mode="mesh",
        parameters={
            "width_m": {"default": 2.4, "min": 1.5, "max": 4.0},
            "height_m": {"default": 2.4, "min": 2.1, "max": 3.0},
        },
        ai_keywords=["自動門", "感應門", "automatic door", "auto glass door"],
        ai_placement_rules="商場入口、公共建築入口。含感應器。",
    ),
    ComponentDef(
        id="window_fixed",
        category=CAT,
        name_zh="固定窗",
        name_en="Fixed Window",
        ifc_class="IfcWindow",
        ifc_predefined_type="WINDOW",
        parameters={
            "width_m": {"default": 1.2, "min": 0.3, "max": 3.0},
            "height_m": {"default": 1.5, "min": 0.3, "max": 3.0},
            "sill_height_m": {"default": 0.9, "min": 0.0, "max": 1.2},
        },
        ai_keywords=["固定窗", "fixed window", "景觀窗"],
        ai_placement_rules="採光窗、景觀窗。不可開啟。",
    ),
    ComponentDef(
        id="window_casement",
        category=CAT,
        name_zh="推射窗",
        name_en="Casement Window",
        ifc_class="IfcWindow",
        ifc_predefined_type="WINDOW",
        parameters={
            "width_m": {"default": 1.2, "min": 0.6, "max": 2.0},
            "height_m": {"default": 1.5, "min": 0.6, "max": 2.0},
            "sill_height_m": {"default": 0.9, "min": 0.0, "max": 1.2},
        },
        suppliers=[
            SupplierInfo(
                name="力霸鋁門窗", brand="力霸", country="TW",
                price=PriceRange(min_price=6000, max_price=15000, unit="per_unit", source="台灣市場參考價 2025"),
            ),
        ],
        ai_keywords=["推射窗", "casement window", "外推窗"],
        ai_placement_rules="通風窗首選，氣密性佳。",
    ),
    ComponentDef(
        id="window_sliding",
        category=CAT,
        name_zh="橫拉窗",
        name_en="Sliding Window",
        ifc_class="IfcWindow",
        ifc_predefined_type="WINDOW",
        parameters={
            "width_m": {"default": 1.5, "min": 0.9, "max": 3.0},
            "height_m": {"default": 1.2, "min": 0.6, "max": 2.0},
            "sill_height_m": {"default": 0.9, "min": 0.0, "max": 1.2},
        },
        ai_keywords=["橫拉窗", "sliding window", "拉窗"],
        ai_placement_rules="台灣最常見窗型，操作方便。",
    ),
    ComponentDef(
        id="skylight",
        category=CAT,
        name_zh="天窗",
        name_en="Skylight",
        ifc_class="IfcWindow",
        ifc_predefined_type="SKYLIGHT",
        parameters={
            "width_m": {"default": 1.0, "min": 0.5, "max": 3.0},
            "length_m": {"default": 1.5, "min": 0.5, "max": 3.0},
        },
        ai_keywords=["天窗", "skylight", "屋頂窗", "採光罩"],
        ai_placement_rules="屋頂開口採光，需防水處理。",
    ),
]
