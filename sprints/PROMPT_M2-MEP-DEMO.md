# Sprint M2-MEP-DEMO: 冰水主機 Demo + MEP 管線 + 成本連動

> **目標:** 完整的「把冰水主機移到右側柱子旁邊」Demo 流程
> **Tasks:** 25 / **Parts:** 4 / **Tag:** mvp-v0.5.0
> **前提:** M2-BRIDGE + M2-ENTITY 已完成

## Demo 腳本

```
用戶: 「幫我規劃一座 3nm 晶圓廠的 CUB 區域」
AI: (生成 CUB: 冰水主機x3 + 冷卻水塔x4 + 壓縮空氣x2 + 管廊)
AI: 「CUB 規劃完成。總設備成本 NT$28,400,000。」

用戶: 「請將那台冰水主機移動到右側柱子旁邊」
AI: (chiller-A 平滑移動動畫，管線自動重連)
AI: 「已移動冰水主機-A。管路增加 12m，成本增加 NT$180,000。」

用戶: 「把冷卻水塔增加到 6 座」
AI: (新增 tower-05, tower-06 在現有 4 座旁邊)
AI: 「已新增。冷卻容量 +50%，成本增加 NT$2,400,000。」

用戶: 「排氣管高度改成 45 米」
AI: (3 根排氣管高度從 35m 調整為 45m)
AI: 「排氣管已調整。符合環評高度要求。鋼材成本增加 NT$450,000。」
```

## Part A (T1-7): AI Agent 空間推理

更新 `agents/modifier.py` — 新增 spatial reasoning:
- 理解「那台」= 最近提到的或最靠近攝影機的同類設備
- 理解「右側」= +X 方向 (基於攝影機視角或絕對座標)
- 理解「旁邊」= offset 2-3m (根據設備尺寸自動計算)
- 理解「增加到 N 座」= 計算現有數量 + 差額 + 自動排列位置
- 理解「高度改成 Xm」= 修改 dimensions.y

更新 `agents/orchestrator.py` — 新增 scene query integration:
- 收到 NL 指令時，先用 scene.query 了解目前場景狀態
- 傳遞 scene context 給 modifier/planner agent
- 收到 modifier 結果後，透過 AgentBridge 執行 scene 操作

更新 `agent_runner.py` — 新增 scene command handling:
- 處理 AgentBridge 的 query/move/add/delete 回傳
- 組裝 AI 回應文字 (含成本差異)

## Part B (T8-14): MEP 管線系統

整合 IDTF `bim/mep/pathfinder.py`:
- 設備移動後自動重新計算管線路徑
- A* 或最短路徑演算法
- 產出管線 segment list (from, to, length, diameter)

整合 IDTF `bim/mep/clash_detect.py`:
- 移動前檢查目標位置是否碰撞
- bounding box + 安全距離 (1m)
- 碰撞時 AI 回報警告並建議替代位置

建立 `zigma/qml/PipeSegment.qml` — 3D 管線視覺化:
- 兩點之間的 Cylinder
- 顏色: 冷卻水=藍, 冰水=綠, 特氣=紅, 排氣=灰
- 自動跟隨設備移動 (綁定 BIMEntity.position)

建立 `zigma/qml/PipeNetwork.qml` — 管線網路管理:
- 管理所有 PipeSegment 實例
- 接收 pathfinder 結果並建立/更新管線
- 移動事件觸發重新路由

## Part C (T15-20): 成本/時程即時連動

整合 IDTF `bim/cost/cost_delta.py`:
- 每次 scene 操作後自動觸發成本重算
- cost_delta 比較操作前後的差異
- 結果推送到 CostPanel (QML signal)

整合 IDTF `bim/cost/unit_prices_tw.py`:
- 台灣本地化單價 (NT$)
- 管線: 800/m (CW), 600/m (CHW), 1200/m (特氣)

更新 CostPanel.qml:
- 操作前後成本對比 (紅色=增加, 綠色=減少)
- 分類圓餅圖即時更新

更新 ChatPanel.qml:
- AI 回應包含結構化成本資訊
- 操作結果格式: 「已移動 XXX。管路 +12m，成本 +NT$180,000。」

## Part D (T21-25): E2E 測試 + Demo 排練

- E2E 測試: NL 輸入 -> AI 解析 -> scene 操作 -> 成本更新 -> 視覺更新
- Demo 腳本自動化 (test_demo_script.py)
- Build + ctest + pytest
- 更新 PROJECT_STATUS.md
- git tag mvp-v0.5.0

## IDTF 模組對接表

| 功能 | IDTF 模組 | 整合方式 |
|------|-----------|----------|
| 空間推理 | agents/modifier.py (25KB) | 直接呼叫 |
| 任務分派 | agents/orchestrator.py (19KB) | 直接呼叫 |
| 管線路徑 | bim/mep/pathfinder.py (9KB) | 直接呼叫 |
| 碰撞檢測 | bim/mep/clash_detect.py (5KB) | 直接呼叫 |
| MEP 設備 | bim/mep/systems.py (14KB) | 設備型錄 |
| 成本差異 | bim/cost/cost_delta.py (9KB) | 直接呼叫 |
| 台灣單價 | bim/cost/unit_prices_tw.py (5KB) | 直接呼叫 |
| 工程量 | bim/cost/qto.py (6KB) | 管線長度計算 |

## BUILD 鐵律

- CMake: C++ 絕對路徑 / QML 相對路徑
- QML: onPropertyChanged 放 root
- AgentBridge: JSON protocol 向後相容
- Demo 腳本: 可重複執行，每次從空場景開始
