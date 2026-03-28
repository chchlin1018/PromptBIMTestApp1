# Sprint M2-BRIDGE: BIMEntity + AgentBridge 雙向通訊 + Scene Query/Operate

> **目標:** 讓 AI 能查詢和操作 3D 場景中的具名物件（「把冰水主機移到右側柱子旁邊」）
> **Tasks:** 25 / **Parts:** 4 / **Tag:** mvp-v0.3.0
> **前提:** M1-SCENE + M2-ENV 已完成

## 核心 Demo 場景

```
用戶: 「把那台冰水主機移到右側柱子旁邊」
AI: (chiller-A 從 (10,0,5) 移動到 (25,0,8), 靠近 column-C3)
AI: 「已移動冰水主機-A。管路長度增加 12m，成本增加 NT$180,000。」
```

## Part A (T1-7): BIMEntity 資料模型

建立 `zigma/src/BIMEntity.h/.cpp` — C++ QObject:
- 屬性: id (QString), type (QString, e.g. "MEP.Chiller"), name (QString, e.g. "冰水主機-A")
- 屬性: position (QVector3D), rotation (QVector3D), dimensions (QVector3D)
- 屬性: properties (QVariantMap — capacity, power, cost, installDays)
- 屬性: connections (QStringList — 連接的管線 ID)
- 屬性: model3D (QString — GLB/QML source path)
- Signal: positionChanged, propertiesChanged
- Q_PROPERTY + Q_INVOKABLE for QML access

建立 `zigma/src/BIMSceneGraph.h/.cpp` — 場景圖管理器:
- addEntity(BIMEntity*), removeEntity(id), findEntity(id)
- queryByType(type) -> QList, queryByName(name) -> QList
- nearbyEntities(id, radius) -> QList
- allEntities() -> QList
- 註冊為 QML context property "SceneGraph"
- 序列化: toJson() / fromJson() for AgentBridge 傳輸

更新 `zigma/qml/DemoScene.qml`:
- 將現有匿名 Primitives 改為 BIMEntity 實例
- 每個物件加上 id/type/name/properties
- CUB 區域: Chiller-A/B/C, Column-C1~C6, Compressor-01/02
- 建築: MainFab, Office, CUB, CoolingTower-01~04, ExhaustStack-01~03
- Component.onCompleted: 向 SceneGraph 註冊所有 entity

CMakeLists.txt 加入新檔案 (C++ 絕對路徑)

## Part B (T8-14): AgentBridge 雙向通訊協議

擴展 `zigma/src/AgentBridge.h/.cpp` JSON protocol:

現有 (不變):
- `{"action": "generate", "prompt": "...", "context": {...}}` -> 生成 BIM

新增 (Scene Query):
- `{"action": "query", "type": "MEP.Chiller"}` -> 回傳符合的 entity 列表
- `{"action": "query", "name": "冰水主機"}` -> 模糊名稱搜尋
- `{"action": "get_position", "id": "chiller-A"}` -> 回傳座標
- `{"action": "nearby", "id": "column-C3", "radius": 10}` -> 附近物件
- `{"action": "scene_info"}` -> 回傳完整場景摘要

新增 (Scene Operate):
- `{"action": "move", "id": "chiller-A", "position": [25, 0, 8]}` -> 移動
- `{"action": "rotate", "id": "chiller-A", "rotation": [0, 90, 0]}` -> 旋轉
- `{"action": "resize", "id": "stack-01", "dimensions": [2, 45, 2]}` -> 調整尺寸
- `{"action": "add", "type": "MEP.CoolingTower", "position": [...], "properties": {...}}` -> 新增
- `{"action": "delete", "id": "tower-05"}` -> 刪除
- `{"action": "connect", "from": "chiller-A", "to": "pipe-CW-01"}` -> 建立連接

新增 (Cost/Schedule):
- `{"action": "cost_delta"}` -> 呼叫 Python cost/cost_delta.py 回傳差異
- `{"action": "schedule_impact"}` -> 呼叫 Python bim/simulation 回傳時程影響

AgentBridge 處理流程:
1. Python AI Agent 發出 action JSON via stdout
2. AgentBridge 解析 action type
3. 呼叫 SceneGraph 對應方法
4. 結果回傳 Python via stdin (JSON)
5. QML 自動更新 (透過 BIMEntity signal)

更新 `agent_runner.py`:
- 新增 handle_scene_query / handle_scene_operate functions
- 整合 IDTF mep/pathfinder.py 管線重路由
- 整合 IDTF cost/cost_delta.py 成本計算
- 整合 IDTF mep/clash_detect.py 碰撞檢測

## Part C (T15-20): QML 即時更新

更新 `zigma/qml/BIMView3D.qml`:
- DemoScene 中的物件綁定 BIMEntity.position/rotation
- 物件移動動畫 (Behavior on position)
- 選中物件高亮 (outline shader 或 emission)
- 點擊物件顯示 PropertyPanel

更新 `zigma/qml/PropertyPanel.qml`:
- 綁定選中的 BIMEntity 屬性
- 顯示: id, type, name, position, dimensions, cost, connections
- 可編輯欄位 (position/rotation) for 手動微調

更新 `zigma/qml/CostPanel.qml`:
- 接收 AgentBridge cost_delta 結果
- 即時更新圓餅圖

更新 `zigma/qml/ChatPanel.qml`:
- 顯示 AI 回應中的操作結果 ("已移動冰水主機-A，成本+NT$180,000")
- 操作歷史 undo/redo stack (UI only)

## Part D (T21-25): 測試 + 收尾

- 新增 ctest: test_bim_entity.cpp — BIMEntity CRUD
- 新增 ctest: test_scene_graph.cpp — SceneGraph query/operate
- Build + 全部 ctest 驗證
- 更新 PROJECT_STATUS.md
- git tag mvp-v0.3.0 + Sprint 完成通知

## BUILD 鐵律

- CMake: C++ 絕對路徑 / QML 相對路徑
- QML: onPropertyChanged 放 root
- main.cpp: qrc:/Zigma/qml/main.qml
- AgentBridge: JSON protocol 必須向後相容 (新 action 不破壞 generate)

## IDTF 模組對接表

| M2-BRIDGE 功能 | IDTF 模組 | 檔案 |
|---------------|-----------|------|
| move/rotate 碰撞檢測 | mep/clash_detect.py | bim/mep/clash_detect.py |
| 管線重路由 | mep/pathfinder.py | bim/mep/pathfinder.py |
| 成本差異計算 | cost/cost_delta.py | bim/cost/cost_delta.py |
| 台灣單價 | cost/unit_prices_tw.py | bim/cost/unit_prices_tw.py |
| 工程量 | cost/qto.py | bim/cost/qto.py |
| MEP 設備型錄 | mep/systems.py | bim/mep/systems.py |
| 修改計畫 | agents/modifier.py | agents/modifier.py |
| 場景圖查詢 | schemas/plan.py | schemas/plan.py |
