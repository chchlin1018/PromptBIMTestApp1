"""Interior partition components — 6 types."""

from promptbim.bim.components.base import ComponentCategory, ComponentDef

CAT = ComponentCategory.INTERIOR

INTERIOR_COMPONENTS = [
    ComponentDef(
        id="partition_drywall",
        category=CAT,
        name_zh="輕隔間牆",
        name_en="Drywall Partition",
        ifc_class="IfcWall",
        parameters={
            "thickness_m": {"default": 0.1, "min": 0.07, "max": 0.2},
            "height_m": {"default": 3.0, "min": 2.5, "max": 4.5},
        },
        ai_keywords=["輕隔間", "石膏板", "drywall", "partition", "隔間牆"],
        ai_placement_rules="辦公室/住宅隔間首選，施工快、重量輕。",
    ),
    ComponentDef(
        id="partition_glass",
        category=CAT,
        name_zh="玻璃隔間",
        name_en="Glass Partition",
        ifc_class="IfcWall",
        parameters={
            "thickness_m": {"default": 0.012, "min": 0.01, "max": 0.02},
            "height_m": {"default": 2.7, "min": 2.1, "max": 3.5},
        },
        ai_keywords=["玻璃隔間", "glass partition", "透明隔間"],
        ai_placement_rules="辦公室採光隔間，會議室常用。",
    ),
    ComponentDef(
        id="ceiling_suspended",
        category=CAT,
        name_zh="輕鋼架天花板",
        name_en="Suspended Ceiling",
        ifc_class="IfcCovering",
        ifc_predefined_type="CEILING",
        parameters={
            "module_mm": {"default": 600, "options": [600, 300]},
            "plenum_height_m": {"default": 0.4, "min": 0.2, "max": 1.0},
        },
        ai_keywords=["天花板", "輕鋼架", "suspended ceiling", "drop ceiling", "T-bar"],
        ai_placement_rules="辦公/商業空間標準天花板，隱藏管線。",
    ),
    ComponentDef(
        id="raised_floor",
        category=CAT,
        name_zh="高架地板",
        name_en="Raised Floor",
        ifc_class="IfcCovering",
        ifc_predefined_type="FLOORING",
        parameters={
            "module_mm": {"default": 600, "options": [600]},
            "height_m": {"default": 0.1, "min": 0.05, "max": 0.5},
        },
        ai_keywords=["高架地板", "raised floor", "access floor"],
        ai_placement_rules="機房、辦公室地板下走線用。",
    ),
    ComponentDef(
        id="railing_metal",
        category=CAT,
        name_zh="金屬欄杆",
        name_en="Metal Railing",
        ifc_class="IfcRailing",
        parameters={
            "height_m": {"default": 1.1, "min": 1.0, "max": 1.2},
        },
        ai_keywords=["欄杆", "扶手", "railing", "handrail", "金屬欄杆"],
        ai_placement_rules="樓梯、陽台、屋頂平台邊緣。高度>=1.1m（台灣法規）。",
    ),
    ComponentDef(
        id="railing_glass",
        category=CAT,
        name_zh="玻璃欄杆",
        name_en="Glass Railing",
        ifc_class="IfcRailing",
        parameters={
            "height_m": {"default": 1.1, "min": 1.0, "max": 1.2},
            "glass_thickness_mm": {"default": 12, "options": [10, 12, 15]},
        },
        ai_keywords=["玻璃欄杆", "glass railing", "透明欄杆"],
        ai_placement_rules="景觀陽台、現代建築使用，需強化玻璃。",
    ),
]
