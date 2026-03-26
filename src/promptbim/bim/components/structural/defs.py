"""Structural components — 12 types."""

from promptbim.bim.components.base import (
    ComponentCategory,
    ComponentDef,
    PriceRange,
    SupplierInfo,
)

CAT = ComponentCategory.STRUCTURAL

STRUCTURAL_COMPONENTS = [
    ComponentDef(
        id="foundation_strip",
        category=CAT,
        name_zh="條形基礎",
        name_en="Strip Foundation",
        ifc_class="IfcFooting",
        ifc_predefined_type="STRIP_FOOTING",
        omniclass_code="21-01 10",
        parameters={
            "width_m": {"default": 0.6, "min": 0.3, "max": 1.5},
            "depth_m": {"default": 0.8, "min": 0.4, "max": 2.0},
            "length_m": {"default": 10.0, "min": 1.0, "max": 50.0},
        },
        suppliers=[
            SupplierInfo(
                name="台灣預拌混凝土公會",
                brand="RC",
                country="TW",
                price=PriceRange(
                    min_price=2800, max_price=3500, unit="per_m3", source="台灣預拌混凝土公會 2025"
                ),
            ),
        ],
        ai_keywords=["基礎", "條基", "strip foundation", "footing"],
        ai_placement_rules="沿承重牆底部連續佈設，寬度依土壤承載力決定。",
    ),
    ComponentDef(
        id="foundation_mat",
        category=CAT,
        name_zh="筏式基礎",
        name_en="Mat Foundation",
        ifc_class="IfcFooting",
        ifc_predefined_type="PAD_FOOTING",
        omniclass_code="21-01 10",
        parameters={
            "thickness_m": {"default": 0.6, "min": 0.3, "max": 2.0},
            "width_m": {"default": 20.0, "min": 5.0, "max": 100.0},
            "length_m": {"default": 20.0, "min": 5.0, "max": 100.0},
        },
        ai_keywords=["筏式基礎", "筏基", "mat foundation", "raft"],
        ai_placement_rules="覆蓋整個建築底部，適用軟弱地盤或高樓層建築。",
    ),
    ComponentDef(
        id="foundation_pile",
        category=CAT,
        name_zh="基樁",
        name_en="Pile",
        ifc_class="IfcPile",
        omniclass_code="21-01 20",
        parameters={
            "diameter_m": {"default": 0.6, "min": 0.3, "max": 2.0},
            "length_m": {"default": 15.0, "min": 5.0, "max": 60.0},
        },
        ai_keywords=["基樁", "樁基礎", "pile", "pile foundation"],
        ai_placement_rules="柱位下方垂直打入，深度至岩盤或堅硬土層。",
    ),
    ComponentDef(
        id="column_rc",
        category=CAT,
        name_zh="RC柱",
        name_en="RC Column",
        ifc_class="IfcColumn",
        omniclass_code="21-02 10 10",
        parameters={
            "width_m": {"default": 0.5, "min": 0.3, "max": 1.2},
            "depth_m": {"default": 0.5, "min": 0.3, "max": 1.2},
            "height_m": {"default": 3.0, "min": 2.5, "max": 6.0},
        },
        suppliers=[
            SupplierInfo(
                name="台灣預拌混凝土公會",
                brand="RC fc'=280",
                country="TW",
                price=PriceRange(
                    min_price=2800, max_price=3500, unit="per_m3", source="台灣預拌混凝土公會 2025"
                ),
            ),
        ],
        ai_keywords=["柱", "RC柱", "混凝土柱", "column", "RC column"],
        ai_placement_rules="依結構格架配置，間距通常6-10m，角隅和交叉點必設。",
    ),
    ComponentDef(
        id="column_steel",
        category=CAT,
        name_zh="鋼柱",
        name_en="Steel Column",
        ifc_class="IfcColumn",
        omniclass_code="21-02 10 20",
        parameters={
            "section": {
                "default": "H400x200",
                "options": ["H300x150", "H400x200", "H500x200", "H600x200"],
            },
            "height_m": {"default": 3.0, "min": 2.5, "max": 6.0},
        },
        suppliers=[
            SupplierInfo(
                name="東和鋼鐵",
                brand="H型鋼",
                country="TW",
                price=PriceRange(
                    min_price=28000, max_price=35000, unit="per_ton", source="東和鋼鐵 2025"
                ),
            ),
        ],
        ai_keywords=["鋼柱", "steel column", "H型鋼柱"],
        ai_placement_rules="鋼構建築使用，可搭配RC基礎。適合大跨度空間。",
    ),
    ComponentDef(
        id="beam_rc",
        category=CAT,
        name_zh="RC梁",
        name_en="RC Beam",
        ifc_class="IfcBeam",
        omniclass_code="21-02 20 10",
        parameters={
            "width_m": {"default": 0.3, "min": 0.2, "max": 0.8},
            "depth_m": {"default": 0.5, "min": 0.3, "max": 1.0},
            "length_m": {"default": 6.0, "min": 2.0, "max": 15.0},
        },
        ai_keywords=["梁", "RC梁", "混凝土梁", "beam", "RC beam"],
        ai_placement_rules="連接柱與柱之間，承載樓板荷重。深度約為跨度1/10~1/12。",
    ),
    ComponentDef(
        id="beam_steel",
        category=CAT,
        name_zh="鋼梁",
        name_en="Steel Beam",
        ifc_class="IfcBeam",
        omniclass_code="21-02 20 20",
        parameters={
            "section": {"default": "H400x200", "options": ["H300x150", "H400x200", "H500x200"]},
            "length_m": {"default": 8.0, "min": 3.0, "max": 20.0},
        },
        suppliers=[
            SupplierInfo(
                name="東和鋼鐵",
                brand="H型鋼",
                country="TW",
                price=PriceRange(
                    min_price=28000, max_price=35000, unit="per_ton", source="東和鋼鐵 2025"
                ),
            ),
        ],
        ai_keywords=["鋼梁", "steel beam", "H型鋼梁"],
        ai_placement_rules="鋼構建築主梁，大跨度空間首選。",
    ),
    ComponentDef(
        id="slab_rc",
        category=CAT,
        name_zh="RC樓板",
        name_en="RC Slab",
        ifc_class="IfcSlab",
        omniclass_code="21-03 10",
        parameters={
            "thickness_m": {"default": 0.15, "min": 0.12, "max": 0.3},
        },
        ai_keywords=["樓板", "RC板", "slab", "RC slab", "floor slab"],
        ai_placement_rules="每層樓標準配置，厚度依跨度決定。",
    ),
    ComponentDef(
        id="slab_post_tension",
        category=CAT,
        name_zh="預力樓板",
        name_en="Post-Tension Slab",
        ifc_class="IfcSlab",
        omniclass_code="21-03 10",
        parameters={
            "thickness_m": {"default": 0.2, "min": 0.15, "max": 0.4},
        },
        ai_keywords=["預力板", "預力樓板", "post-tension", "PT slab"],
        ai_placement_rules="大跨度樓板（>10m），可減少梁深度。",
    ),
    ComponentDef(
        id="rebar_main",
        category=CAT,
        name_zh="主筋",
        name_en="Main Rebar",
        ifc_class="IfcReinforcingBar",
        parameters={
            "diameter_mm": {"default": 19, "options": [10, 13, 16, 19, 22, 25, 29, 32, 36]},
            "grade": {"default": "SD420", "options": ["SD280", "SD420"]},
        },
        suppliers=[
            SupplierInfo(
                name="台灣鋼鐵公會",
                brand="SD420",
                country="TW",
                price=PriceRange(
                    min_price=22000, max_price=28000, unit="per_ton", source="台灣鋼鐵公會 2025"
                ),
            ),
        ],
        ai_keywords=["主筋", "鋼筋", "rebar", "main rebar", "reinforcement"],
        ai_placement_rules="配置於梁、柱、板內，提供拉力抵抗。",
    ),
    ComponentDef(
        id="rebar_stirrup",
        category=CAT,
        name_zh="箍筋",
        name_en="Stirrup",
        ifc_class="IfcReinforcingBar",
        parameters={
            "diameter_mm": {"default": 10, "options": [10, 13]},
            "spacing_mm": {"default": 200, "min": 100, "max": 300},
        },
        ai_keywords=["箍筋", "stirrup", "tie", "shear reinforcement"],
        ai_placement_rules="環繞柱梁主筋外側，抵抗剪力。柱梁接頭處加密。",
    ),
    ComponentDef(
        id="shear_wall",
        category=CAT,
        name_zh="剪力牆",
        name_en="Shear Wall",
        ifc_class="IfcWall",
        omniclass_code="21-02 30",
        parameters={
            "thickness_m": {"default": 0.2, "min": 0.15, "max": 0.4},
            "length_m": {"default": 6.0, "min": 2.0, "max": 15.0},
            "height_m": {"default": 3.0, "min": 2.5, "max": 6.0},
        },
        ai_keywords=["剪力牆", "RC牆", "shear wall", "structural wall"],
        ai_placement_rules="建築核心筒或外圍，提供側向抵抗力。台灣耐震規範要求。",
    ),
]
