"""MEP (Mechanical, Electrical, Plumbing) components — 11 types."""

from promptbim.bim.components.base import ComponentCategory, ComponentDef

CAT = ComponentCategory.MEP

MEP_COMPONENTS = [
    ComponentDef(
        id="ahu_rooftop",
        category=CAT,
        name_zh="屋頂空調箱",
        name_en="Rooftop AHU",
        ifc_class="IfcUnitaryEquipment",
        geometry_mode="mesh",
        parameters={
            "cooling_kw": {"default": 50, "min": 10, "max": 500},
            "airflow_cmh": {"default": 5000, "min": 1000, "max": 50000},
        },
        ai_keywords=["空調箱", "AHU", "rooftop unit", "RTU", "空調主機"],
        ai_placement_rules="屋頂機械區。需結構載重確認。",
    ),
    ComponentDef(
        id="fcu",
        category=CAT,
        name_zh="風機盤管",
        name_en="Fan Coil Unit",
        ifc_class="IfcUnitaryEquipment",
        geometry_mode="mesh",
        parameters={
            "cooling_kw": {"default": 5, "min": 1, "max": 20},
        },
        ai_keywords=["風機盤管", "FCU", "fan coil", "小型空調"],
        ai_placement_rules="天花板內或牆壁掛裝，每間房一台。",
    ),
    ComponentDef(
        id="duct_rectangular",
        category=CAT,
        name_zh="矩形風管",
        name_en="Rectangular Duct",
        ifc_class="IfcDuctSegment",
        parameters={
            "width_mm": {"default": 400, "min": 150, "max": 1500},
            "height_mm": {"default": 300, "min": 150, "max": 1000},
        },
        ai_keywords=["風管", "duct", "rectangular duct", "送風管"],
        ai_placement_rules="天花板內走管，高度受限時用扁型。",
    ),
    ComponentDef(
        id="pipe_water",
        category=CAT,
        name_zh="給水管",
        name_en="Water Pipe",
        ifc_class="IfcPipeSegment",
        parameters={
            "diameter_mm": {"default": 25, "options": [15, 20, 25, 32, 40, 50, 65, 80, 100]},
        },
        ai_keywords=["水管", "給水管", "pipe", "water pipe", "管道"],
        ai_placement_rules="管道間垂直、天花板內水平走管。",
    ),
    ComponentDef(
        id="sprinkler_head",
        category=CAT,
        name_zh="消防灑水頭",
        name_en="Sprinkler Head",
        ifc_class="IfcFireSuppressionTerminal",
        geometry_mode="mesh",
        parameters={
            "coverage_sqm": {"default": 12, "min": 6, "max": 20},
            "k_factor": {"default": 80, "options": [57, 80, 115]},
        },
        ai_keywords=["灑水頭", "sprinkler", "消防灑水", "自動灑水"],
        ai_placement_rules="天花板下方，間距依法規(通常3m)。11層以上強制設置。",
    ),
    ComponentDef(
        id="fire_extinguisher",
        category=CAT,
        name_zh="滅火器",
        name_en="Fire Extinguisher",
        ifc_class="IfcFireSuppressionTerminal",
        geometry_mode="mesh",
        parameters={
            "type": {"default": "ABC", "options": ["ABC", "CO2", "foam"]},
            "weight_kg": {"default": 10, "options": [3.5, 6, 10]},
        },
        ai_keywords=["滅火器", "fire extinguisher", "消防器"],
        ai_placement_rules="每層樓走廊、安全梯口。步行距離<=20m。",
    ),
    ComponentDef(
        id="light_recessed",
        category=CAT,
        name_zh="嵌燈",
        name_en="Recessed Light",
        ifc_class="IfcLightFixture",
        geometry_mode="mesh",
        parameters={
            "wattage_w": {"default": 15, "min": 5, "max": 30},
            "diameter_mm": {"default": 150, "options": [100, 150, 200]},
        },
        ai_keywords=["嵌燈", "recessed light", "downlight", "崁燈"],
        ai_placement_rules="天花板嵌入，走廊/房間照明。",
    ),
    ComponentDef(
        id="light_panel",
        category=CAT,
        name_zh="平板燈",
        name_en="Panel Light",
        ifc_class="IfcLightFixture",
        parameters={
            "wattage_w": {"default": 36, "options": [18, 36, 45]},
            "size_mm": {"default": 600, "options": [300, 600]},
        },
        ai_keywords=["平板燈", "panel light", "LED面板燈", "辦公室燈"],
        ai_placement_rules="配合600x600天花板模組，辦公室標準照明。",
    ),
    ComponentDef(
        id="electrical_panel",
        category=CAT,
        name_zh="配電盤",
        name_en="Electrical Panel",
        ifc_class="IfcElectricDistributionBoard",
        geometry_mode="mesh",
        parameters={
            "circuits": {"default": 24, "options": [12, 24, 42]},
        },
        ai_keywords=["配電盤", "electrical panel", "distribution board", "電箱"],
        ai_placement_rules="每層電氣間或走廊壁面。",
    ),
    ComponentDef(
        id="transformer",
        category=CAT,
        name_zh="變壓器",
        name_en="Transformer",
        ifc_class="IfcTransformer",
        geometry_mode="mesh",
        parameters={
            "capacity_kva": {"default": 500, "min": 75, "max": 2500},
        },
        ai_keywords=["變壓器", "transformer", "電力變壓器"],
        ai_placement_rules="地下室或室外電氣室。需通風散熱。",
    ),
    ComponentDef(
        id="generator",
        category=CAT,
        name_zh="發電機",
        name_en="Generator",
        ifc_class="IfcElectricGenerator",
        geometry_mode="mesh",
        parameters={
            "capacity_kw": {"default": 200, "min": 50, "max": 2000},
        },
        ai_keywords=["發電機", "generator", "emergency generator", "緊急發電機"],
        ai_placement_rules="地下室或屋頂。需排煙管道和燃料儲存。",
    ),
]
