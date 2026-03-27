# ADR-001: GUI 遷移至 Qt Quick 3D + QML

> **狀態:** ✅ 已確認 | **日期:** 2026-03-27 | **決策者:** Michael Lin

---

## 背景

### 現有問題

1. **PySide6 記憶體** (ISSUE-004): Mac Mini 16GB 反覆 OOM，pytest 過程中 QApplication 佔 26GB
2. **Qt3D deprecated**: Qt 6.8 已將 Qt3D 移出二進制發行版，僅提供源碼
3. **效能**: PyVista 通過 Python 層呼叫 VTK，額外開銷大

### 考慮過的替代方案

| 方案 | 優點 | 缺點 | 結論 |
|------|------|------|------|
| **Qt Quick 3D** | Qt 官方主推、RHI 內建、PBR、代碼簡潔 | 需學 QML | ✅ 採用 |
| Qt3D | C++ API、ECS 架構 | deprecated Qt 6.8 | ✘ 淘汰 |
| QRhi 自建 | 最大彈性 | 工程量極大 | ✘ 過度 |
| 保持 PyVista | 無遷移成本 | OOM 問題不解 | ✘ 死路 |

---

## 決策

採用 **Qt Quick 3D + QML** 作為 GUI 和 3D 渲染引擎。

AI Agent 保留 Python，透過 **QProcess + JSON stdio** 與 Qt GUI 通訊。

---

## 技術架構

### 系統分層

```
┌───────────────────────────────────────┐
│         Qt Quick 3D GUI              │
│  QML: View3D + ChatPanel + Panels   │
│  C++: AgentBridge (QProcess)         │
│       BIMGeometryProvider             │
│       (QQuick3DGeometry)              │
└────────────────┬──────────────────────┘
                 │ QProcess stdin/stdout
                 │ JSON streaming
┌────────────────┴──────────────────────┐
│         Python AI Backend             │
│  agent_runner.py (asyncio)           │
│  Enhancer → Planner → Builder        │
│  → Checker → Modifier                │
│  Claude API (AsyncAnthropic)         │
└────────────────┬──────────────────────┘
                 │
┌────────────────┴──────────────────────┐
│         C++ Core Engine               │
│  libpromptbim (pybind11)             │
│  Compliance + Cost + MEP + GIS       │
│  IFC Generator + USD Generator       │
└───────────────────────────────────────┘
```

### QML 組件結構

```
qml/
├── main.qml              ← ApplicationWindow + SplitView
├── BIMView3D.qml         ← View3D + PerspectiveCamera + OrbitController
├── ChatPanel.qml         ← 輸入 + streaming 顯示
├── CostPanel.qml         ← 成本圖表 (Canvas/ChartView)
├── SchedulePanel.qml     ← 甘特圖 + 4D 聯動
├── AssetBrowser.qml      ← 零件庫瀏覽器
├── DeltaPanel.qml        ← 變更對照
└── components/
    ├── BIMWall.qml       ← Model + PrincipledMaterial
    ├── BIMSlab.qml
    ├── BIMColumn.qml
    └── BIMEquipment.qml  ← 施工機械 3D
```

### BIM 渲染範例 (QML)

```qml
import QtQuick3D

Model {
    id: wallModel
    property string elementId: ""
    property string bimType: "wall"
    scale: Qt.vector3d(5.0, 3.0, 0.3)
    geometry: CuboidGeometry {}
    materials: [PrincipledMaterial {
        baseColor: "#c8c8c8"
        roughness: 0.7
        metalness: 0.0
    }]

    // 點擊選取
    pickable: true
    onClicked: {
        materials[0].baseColor = "#64b4ff"
        infoPanel.showElement(elementId)
    }
}
```

### 4D 動畫範例 (QML)

```qml
Model {
    id: foundation
    visible: timeline.currentWeek >= 2
    opacity: Math.min(1.0, (timeline.currentWeek - 2) / 4)

    Behavior on opacity {
        NumberAnimation { duration: 300 }
    }
}
```

---

## 執行計劃

| Sprint | 週數 | 目標 | 依賴 |
|--------|:----:|------|------|
| P26 | 1 | AgentBridge QProcess+JSON | Demo 完成 |
| P27 | 2 | QML GUI 骨架 | P26 |
| P28 | 2 | Qt Quick 3D BIM 渲染 | P27 |
| P29 | 1 | PySide6 移除 + 測試遷移 | P28 |

---

## 風險緩解

| 風險 | 緩解 |
|------|------|
| QML 學習曲線 | P27 先做簡單 GUI，不做 3D |
| 大量 BIM 元素效能 | P28 做 benchmark，備案 QRhi |
| Agent 通訊延遲 | P26 加 heartbeat + timeout |
| Demo 前不能破壞現有 GUI | Demo 完成後才開始 P26 |

---

*ADR-001 v1.0 | Zigma PromptToBuild | 2026-03-27*
