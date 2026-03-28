# Sprint M1-SCENE: 3D Demo Scene + Full Debug Logging

> 22 Tasks / 3 Parts / Tag: mvp-v0.2.0

## Part A (T1-9): ZigmaLogger Debug Logging System

建立 C++ singleton `ZigmaLogger` (zigma/src/ZigmaLogger.h + .cpp):
- `qInstallMessageHandler` 攔截全部 Qt debug/warning/error
- 寫入 `{project}/debuglog/zigma_{YYYYMMDD}_{HHmmss}.log`
- 格式: `[2026-03-28 22:15:03.456] [INFO ] [Category    ] message`
- 5 級別: TRACE / DEBUG / INFO / WARN / ERROR
- Category 固定 12 字元寬 (padCategory)
- 同時輸出 file + stderr (Terminal)
- Log rotation: 保留最新 10 個
- `findProjectRoot()`: 從 appDir 往上找 CLAUDE.md/SKILL.md
- `Q_INVOKABLE logFromQml(category, level, message)` 供 QML 用
- `logPythonStdout(line)` / `logPythonStderr(line)` 供 AgentBridge 用
- C++ 巨集: `ZLOG_TRACE/DEBUG/INFO/WARN/ERROR("Cat", "msg")`
- Python AI stderr 自動判斷級別 (ERROR/WARNING/INFO/DEBUG)
- 跨平台: macOS (Metal) + Windows (D3D12)

更新其他檔案:
- `main.cpp`: ZigmaLogger::install() 在 QGuiApplication 後, 註冊 QML context property
- `AgentBridge.cpp`: readyReadStandardOutput 每行 -> logPythonStdout(), readyReadStandardError -> logPythonStderr()
- `BIMSceneBuilder/BIMMaterialLibrary/BIMGeometryProvider.cpp`: include ZigmaLogger.h
- `agent_runner.py`: Python logging FileHandler -> debuglog/python_agent_{date}_{time}.log
- `CMakeLists.txt`: 加 ZigmaLogger.h/.cpp (C++ 絕對路徑)
- `.gitignore`: 加 debuglog/* + !debuglog/.gitkeep
- 建 debuglog/.gitkeep

## Part B (T10-16): 3D Demo Scene

建立 `zigma/qml/DemoScene.qml` — TSMC fab 場景:
- 全用 Qt Quick 3D primitives (不需外部模型)
- 地面 #Rectangle 200x200m
- 主廠房 #Cube 80x25x50m 淺灰白
- 屋頂設備層 #Cube 75x4x45m
- 辦公大樓 #Cube 25x20x20m 淺藍
- CUB #Cube 30x16x25m 淺綠
- 冷卻水塔 Repeater3D x4 #Cylinder
- 排氣管 Repeater3D x3 #Cylinder 35m高 紅色
- 管廊 #Cube 黃色 + 支柱 Repeater3D x6
- 圍牆 4面 / 道路 / 停車場
- Component.onCompleted 用 ZigmaLogger.logFromQml

改寫 `zigma/qml/BIMView3D.qml`:
- import QtQuick3D.Helpers
- SceneEnvironment (MSAA + AO)
- PerspectiveCamera position(-80,60,100) rotation(-25,-30,0) fov60
- 3 光源: DirectionalLight 主光(castsShadow) + 補光 + PointLight 環境光
- DemoScene { visible: demoMode }
- Node bimDynamicRoot { visible: !demoMode }
- OrbitCameraController
- 右上角標籤 + 底部操作提示

CMakeLists.txt 加 DemoScene.qml (QML 相對路徑)

Build + ctest 驗證

## Part C (T17-22): 收尾

- 驗證 debuglog/ 有 log 產出
- 更新 PROJECT_STATUS.md
- git commit + push
- git tag mvp-v0.2.0
- Sprint 完成通知

## BUILD 鐵律

- CMake: C++ 用 `${CMAKE_CURRENT_SOURCE_DIR}/src/` 絕對路徑
- CMake: QML 用相對路徑 `qml/xxx.qml`
- QML: onPropertyChanged handler 放 property 所有者 (root), 不放 Canvas
- main.cpp: 用 `qrc:/Zigma/qml/main.qml`
- .env: 不放空的 ANTHROPIC_API_KEY
