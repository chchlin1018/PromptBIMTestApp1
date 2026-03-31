# S-PTB-GUI-CONNECT PROMPT v1.0 — Qt GUI 連接 C++ Core [20T/3P]

> **Sprint:** S-PTB-GUI-CONNECT | **專案:** PTB | **機器:** Mac Mini
> **目標:** mvp-v0.8.0-gui | **規格:** 20T/3P
> **⛔ pytest 完全禁止** — ctest only

## Parts & Tasks

### P1/3: GUI↔C++ Core 橋接 (8T)
- T01: 更新 main.py — import bim_core 取代舊 Python BIM 邏輯
- T02: SceneGraphWidget — 從 bim_core.SceneGraph 讀取節點樹
- T03: EntityListView — 從 bim_core 列出所有 BIMEntity
- T04: PropertyPanel — 從 bim_core.PropertyManager 讀取屬性
- T05: CostPanel — 從 bim_core.CostCalculator 讀取成本
- T06: ChatPanel — 保留 Python 層，輸出呼叫 bim_core actions
- T07: AgentBridge 整合 — ChatPanel → Python AI → bim_core.AgentBridge
- T08: 3D Viewport — QOpenGLWidget 顯示 SceneGraph 幾何

### P2/3: 驗證 (7T)
- T09: ctest ALL PASS (C++ core 不破壞)
- T10: python -c "import bim_core; print(bim_core.version())" 成功
- T11: python -c "from src.gui import main_window" 成功
- T12: GUI 啟動測試 (offscreen: QT_QPA_PLATFORM=offscreen)
- T13: SceneGraph 顯示驗證
- T14: PropertyPanel 讀取驗證
- T15: CostPanel 計算驗證

### P3/3: Finalize (5T)
- T16: cmake --build + ctest ALL PASS
- T17: AuditReport PTB-FAR-GUI-001 → GitHub + Notion
- T18: PROJECT.md + ARCHITECTURE.md 更新
- T19: git tag mvp-v0.8.0-gui
- T20: 完成通知 + tmux kill
