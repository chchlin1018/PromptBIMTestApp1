# Sprint M2-ENTITY: BIMEntity 具名場景圖 + CUB 設備資料庫

> **目標:** DemoScene 從匿名 Primitives 升級為具名 BIMEntity，支援 AI 查詢
> **Tasks:** 20 / **Parts:** 3 / **Tag:** mvp-v0.4.0
> **前提:** M2-BRIDGE 已完成

## 核心改變

現狀: `Model { source: "#Cube"; position: Qt.vector3d(55, 8, -20) }` — 匿名
目標: `BIMEntity { id: "chiller-A"; type: "MEP.Chiller"; name: "冰水主機-A" }` — 具名

## Part A (T1-8): BIMEntity QML Component

建立 `zigma/qml/BIMEntity.qml` — 通用具名 3D 物件:
- 繼承 Node，包裹 Model
- Properties: entityId (string), entityType (string), entityName (string)
- Properties: dimensions (vector3d), entityProperties (var/JSON)
- Properties: connections (list), model3DSource (string, default "#Cube")
- Properties: selected (bool), hovered (bool)
- 選中效果: emission glow 或 outline color change
- hover 效果: 半透明高亮
- Component.onCompleted: 向 SceneGraph 註冊自己
- Component.onDestruction: 從 SceneGraph 移除
- Behavior on position: NumberAnimation { duration: 500; easing.type: Easing.InOutQuad }
- 點擊信號: onClicked -> 設定為 PropertyPanel 的 selectedEntity

建立 `zigma/qml/BIMLabel.qml` — 3D 空間中的文字標籤:
- 浮在 BIMEntity 上方，顯示 entityName
- 面向攝影機 (billboard effect)
- 可選: 顯示/隱藏 toggle

## Part B (T9-15): CUB 設備場景重建

改寫 `zigma/qml/DemoScene.qml` — 將所有匿名 Model 替換為 BIMEntity 實例:

### 設備清單 (CUB 區域 — Demo 核心)

| entityId | entityType | entityName | position | dimensions | cost (NT$) |
|----------|-----------|------------|----------|------------|----------:|
| chiller-A | MEP.Chiller | 冰水主機-A | (45,0,5) | (3,2.5,1.5) | 2,800,000 |
| chiller-B | MEP.Chiller | 冰水主機-B | (45,0,10) | (3,2.5,1.5) | 2,800,000 |
| chiller-C | MEP.Chiller | 冰水主機-C | (45,0,15) | (3,2.5,1.5) | 2,800,000 |
| compressor-01 | MEP.Compressor | 壓縮空氣機-01 | (55,0,5) | (2,1.5,1.8) | 800,000 |
| compressor-02 | MEP.Compressor | 壓縮空氣機-02 | (55,0,10) | (2,1.5,1.8) | 800,000 |
| upw-system | MEP.UPW | 超純水系統 | (60,0,15) | (4,3,2.5) | 5,000,000 |
| transformer-01 | ELEC.Transformer | 變壓器-01 | (50,0,-10) | (2,1.5,2) | 1,500,000 |
| column-C1~C6 | STRUCT.Column | 柱子-C1~C6 | (各位置) | (0.6,6,0.6) | (結構) |

### 建築清單 (園區級)

| entityId | entityType | entityName |
|----------|-----------|------------|
| main-fab | ARCH.MainFab | 主廠房 |
| penthouse | ARCH.Penthouse | 屋頂設備層 |
| office | ARCH.Office | 辦公大樓 |
| cub | ARCH.CUB | CUB公用廠房 |
| tower-01~04 | MEP.CoolingTower | 冷卻水塔-01~04 |
| stack-01~03 | MEP.ExhaustStack | 排氣管-01~03 |
| pipe-rack | STRUCT.PipeRack | 管廊 |

建立 `zigma/data/equipment_catalog.json` — 設備型錄:
- MEP: Chiller, CoolingTower, Compressor, UPW, Pump
- ELEC: Transformer, Switchgear, UPS, CableTray
- STRUCT: Column, Beam, PipeRack
- 每項含: type, defaultDimensions, defaultCost, installDays, powerKW
- 對接 IDTF `bim/cost/unit_prices_tw.py` 和 `bim/mep/systems.py`

## Part C (T16-20): PropertyPanel 連動 + 測試

更新 `zigma/qml/PropertyPanel.qml`:
- 綁定 selectedEntity (BIMEntity)
- 顯示: id, type, name, position, dimensions, cost, connections
- position 可手動編輯 (TextInput + Apply 按鈕)

更新 `zigma/qml/CostPanel.qml`:
- 從 SceneGraph 讀取所有 entity 的 cost
- 自動加總 + 分類圓餅圖 (MEP/ELEC/STRUCT/ARCH)

新增 ctest: test_bim_entity.cpp + test_scene_graph.cpp
Build + 全部 ctest + tag mvp-v0.4.0

## BUILD 鐵律

- CMake: C++ 絕對路徑 / QML 相對路徑
- QML: onPropertyChanged 放 root
- BIMEntity 的 entityProperties 用 QVariantMap (不用自定義 C++ type)
