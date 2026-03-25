"""Site/landscape components — 6 types."""

from promptbim.bim.components.base import ComponentCategory, ComponentDef

CAT = ComponentCategory.SITE

SITE_COMPONENTS = [
    ComponentDef(
        id="parking_standard",
        category=CAT,
        name_zh="標準停車位",
        name_en="Standard Parking",
        ifc_class="IfcSpace",
        parameters={
            "width_m": {"default": 2.5, "min": 2.25, "max": 3.0},
            "length_m": {"default": 5.5, "min": 5.0, "max": 6.0},
        },
        ai_keywords=["停車位", "parking", "車位", "standard parking"],
        ai_placement_rules="地下室或地面層。寬>=2.25m、長>=5.5m（台灣法規）。",
    ),
    ComponentDef(
        id="parking_accessible",
        category=CAT,
        name_zh="無障礙停車位",
        name_en="Accessible Parking",
        ifc_class="IfcSpace",
        parameters={
            "width_m": {"default": 3.5, "min": 3.3, "max": 4.0},
            "length_m": {"default": 6.0, "min": 5.5, "max": 6.5},
        },
        ai_keywords=["無障礙停車", "accessible parking", "殘障車位", "身障車位"],
        ai_placement_rules="每50車位至少1個無障礙車位。靠近電梯出入口。寬>=3.3m。",
    ),
    ComponentDef(
        id="fence_metal",
        category=CAT,
        name_zh="金屬圍牆",
        name_en="Metal Fence",
        ifc_class="IfcBuildingElementProxy",
        parameters={
            "height_m": {"default": 1.8, "min": 1.2, "max": 2.5},
        },
        ai_keywords=["圍牆", "fence", "圍籬", "metal fence"],
        ai_placement_rules="基地邊界。高度依地方法規限制。",
    ),
    ComponentDef(
        id="tree_deciduous",
        category=CAT,
        name_zh="落葉喬木",
        name_en="Deciduous Tree",
        ifc_class="IfcGeographicElement",
        geometry_mode="mesh",
        parameters={
            "canopy_diameter_m": {"default": 6, "min": 3, "max": 15},
            "height_m": {"default": 8, "min": 4, "max": 20},
        },
        ai_keywords=["樹", "喬木", "落葉樹", "tree", "deciduous tree"],
        ai_placement_rules="景觀配置。夏天遮陽、冬天透光。",
    ),
    ComponentDef(
        id="tree_evergreen",
        category=CAT,
        name_zh="常綠喬木",
        name_en="Evergreen Tree",
        ifc_class="IfcGeographicElement",
        geometry_mode="mesh",
        parameters={
            "canopy_diameter_m": {"default": 4, "min": 2, "max": 10},
            "height_m": {"default": 10, "min": 3, "max": 25},
        },
        ai_keywords=["常綠樹", "evergreen tree", "常綠喬木"],
        ai_placement_rules="全年遮蔽。隔音、防風帶常用。",
    ),
    ComponentDef(
        id="pavement_concrete",
        category=CAT,
        name_zh="混凝土鋪面",
        name_en="Concrete Pavement",
        ifc_class="IfcSlab",
        parameters={
            "thickness_m": {"default": 0.15, "min": 0.1, "max": 0.3},
        },
        ai_keywords=["鋪面", "pavement", "地坪", "混凝土鋪面"],
        ai_placement_rules="停車場、人行道、車道地坪。",
    ),
]
