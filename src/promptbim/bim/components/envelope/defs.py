"""Envelope/enclosure components — 10 types."""

from promptbim.bim.components.base import (
    ComponentCategory,
    ComponentDef,
    PriceRange,
    SupplierInfo,
)

CAT = ComponentCategory.ENVELOPE

ENVELOPE_COMPONENTS = [
    ComponentDef(
        id="wall_exterior_brick",
        category=CAT,
        name_zh="磚造外牆",
        name_en="Brick Exterior Wall",
        ifc_class="IfcWall",
        parameters={
            "thickness_m": {"default": 0.24, "min": 0.12, "max": 0.36},
            "height_m": {"default": 3.0, "min": 2.5, "max": 6.0},
        },
        ai_keywords=["磚牆", "外牆", "brick wall", "exterior wall"],
        ai_placement_rules="外牆圍護用，1B或1/2B厚。需防水層。",
    ),
    ComponentDef(
        id="wall_exterior_concrete",
        category=CAT,
        name_zh="清水模外牆",
        name_en="Exposed Concrete Wall",
        ifc_class="IfcWall",
        parameters={
            "thickness_m": {"default": 0.2, "min": 0.15, "max": 0.3},
        },
        ai_keywords=["清水模", "清水混凝土", "exposed concrete", "fair-faced concrete"],
        ai_placement_rules="建築外觀表現用，需高品質模板施工。",
    ),
    ComponentDef(
        id="wall_exterior_metal",
        category=CAT,
        name_zh="金屬外牆",
        name_en="Metal Panel Wall",
        ifc_class="IfcWall",
        parameters={
            "panel_thickness_mm": {"default": 50, "min": 30, "max": 100},
        },
        ai_keywords=["金屬牆", "鋼板", "metal panel", "metal cladding"],
        ai_placement_rules="工業廠房或現代建築外牆，含保溫層。",
    ),
    ComponentDef(
        id="curtain_wall_glass",
        category=CAT,
        name_zh="玻璃帷幕牆",
        name_en="Glass Curtain Wall",
        ifc_class="IfcCurtainWall",
        parameters={
            "module_width_m": {"default": 1.5, "min": 0.9, "max": 3.0},
            "module_height_m": {"default": 3.6, "min": 2.5, "max": 4.5},
            "glass_thickness_mm": {"default": 24, "options": [12, 16, 24, 28]},
        },
        suppliers=[
            SupplierInfo(
                name="台玻",
                brand="台灣玻璃",
                country="TW",
                price=PriceRange(
                    min_price=8000, max_price=20000, unit="per_sqm", source="台灣市場參考價 2025"
                ),
            ),
        ],
        ai_keywords=["帷幕牆", "玻璃牆", "curtain wall", "glass wall", "facade"],
        ai_placement_rules="商辦大樓外牆。需考慮風壓、熱傳導、水密性。",
    ),
    ComponentDef(
        id="roof_flat",
        category=CAT,
        name_zh="平屋頂",
        name_en="Flat Roof",
        ifc_class="IfcRoof",
        ifc_predefined_type="FLAT_ROOF",
        parameters={
            "thickness_m": {"default": 0.15, "min": 0.1, "max": 0.3},
            "slope_percent": {"default": 1.5, "min": 0.5, "max": 3.0},
        },
        ai_keywords=["平屋頂", "flat roof", "平頂"],
        ai_placement_rules="標準屋頂形式，需洩水坡度1-3%。",
    ),
    ComponentDef(
        id="roof_gable",
        category=CAT,
        name_zh="雙坡屋頂",
        name_en="Gable Roof",
        ifc_class="IfcRoof",
        ifc_predefined_type="GABLE_ROOF",
        parameters={
            "slope_degrees": {"default": 30, "min": 15, "max": 60},
            "overhang_m": {"default": 0.5, "min": 0.2, "max": 1.5},
        },
        ai_keywords=["雙坡屋頂", "斜屋頂", "gable roof", "pitched roof"],
        ai_placement_rules="住宅常用，排水性佳。台灣多雨地區適用。",
    ),
    ComponentDef(
        id="roof_hip",
        category=CAT,
        name_zh="四坡屋頂",
        name_en="Hip Roof",
        ifc_class="IfcRoof",
        ifc_predefined_type="HIP_ROOF",
        parameters={
            "slope_degrees": {"default": 25, "min": 15, "max": 45},
        },
        ai_keywords=["四坡屋頂", "寄棟屋頂", "hip roof"],
        ai_placement_rules="四面傾斜，抗風性佳，適合台灣沿海地區。",
    ),
    ComponentDef(
        id="roof_metal_deck",
        category=CAT,
        name_zh="金屬屋面板",
        name_en="Metal Deck Roof",
        ifc_class="IfcRoof",
        parameters={
            "thickness_mm": {"default": 0.5, "min": 0.3, "max": 1.0},
            "slope_degrees": {"default": 5, "min": 3, "max": 15},
        },
        ai_keywords=["鐵皮屋", "金屬屋頂", "metal roof", "metal deck"],
        ai_placement_rules="工廠/倉庫常用，輕量低成本。",
    ),
    ComponentDef(
        id="parapet",
        category=CAT,
        name_zh="女兒牆",
        name_en="Parapet",
        ifc_class="IfcWall",
        parameters={
            "height_m": {"default": 1.1, "min": 0.6, "max": 1.5},
            "thickness_m": {"default": 0.15, "min": 0.1, "max": 0.25},
        },
        ai_keywords=["女兒牆", "parapet", "屋頂矮牆"],
        ai_placement_rules="平屋頂邊緣必設，高度依法規>=1.1m。",
    ),
    ComponentDef(
        id="canopy",
        category=CAT,
        name_zh="雨遮",
        name_en="Canopy",
        ifc_class="IfcRoof",
        parameters={
            "depth_m": {"default": 1.5, "min": 0.6, "max": 3.0},
            "thickness_m": {"default": 0.1, "min": 0.05, "max": 0.2},
        },
        ai_keywords=["雨遮", "遮陽", "canopy", "awning", "sunshade"],
        ai_placement_rules="入口、窗戶上方。深度不超過2m免計入建蔽率（台灣法規）。",
    ),
]
