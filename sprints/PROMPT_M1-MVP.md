# PROMPT_M1-MVP.md — Zigma MVP Sprint (68T / 9 Parts)

> **Sprint:** M1-MVP | **版本目標:** mvp-v0.1.0
> **環境:** Mac Mini M4 (16GB) | macOS | Metal | Qt 6.11.0 (Homebrew)
> **Tasks:** 68 | **Parts:** 9 (A-I) | **Tags:** alpha / beta / mvp-v0.1.0
> **Qt6 路徑:** /opt/homebrew/opt/qt
> **排除:** 2 個 Windows-only (S1-C-T25, S3-B-T11)

---

## ★★★ 絕對第一步：完整函數定義 ★★★

```bash
# ===== Sprint 變數 =====
SPRINT="M1-MVP"
SPRINT_DESC="Zigma MVP: AgentBridge + Qt Quick 3D + TSMC Demo (68T/9Parts)"
VERSION="mvp-v0.1.0"
TASK_TOTAL=68
TASK_DONE=0
PART_TOTAL=9
PART_DONE=0
PCT=0

# ===== Qt6 環境 =====
export QT_DIR="/opt/homebrew/opt/qt"
export CMAKE_PREFIX_PATH="$QT_DIR"
export PATH="$QT_DIR/bin:$PATH"
export PKG_CONFIG_PATH="$QT_DIR/lib/pkgconfig:$PKG_CONFIG_PATH"

# --- notify (v2 — heredoc + log + safe argv) ---
notify() {
    local msg="$1"
    local log="/tmp/zigma-notify.log"
    /usr/bin/osascript - "$msg" <<'EOF' >>"$log" 2>&1
on run argv
    set theMessage to item 1 of argv
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "+886972535899" of targetService
        send theMessage to targetBuddy
    end tell
end run
EOF
    [ $? -eq 0 ] && return 0
    /usr/bin/osascript - "$msg" <<'EOF' >>"$log" 2>&1
on run argv
    set theMessage to item 1 of argv
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "chchlin1018@icloud.com" of targetService
        send theMessage to targetBuddy
    end tell
end run
EOF
    [ $? -eq 0 ] && return 0
    /usr/bin/osascript - "$msg" <<'EOF' >>"$log" 2>&1
on run argv
    set theMessage to item 1 of argv
    display notification theMessage with title "Zigma"
end run
EOF
    [ $? -eq 0 ] && return 0
    echo "[NOTIFY FALLBACK] $msg" | tee -a "$log"
    return 1
}

# --- 記憶體 ---
get_mem() {
    local ps=$(sysctl -n hw.pagesize 2>/dev/null || echo 4096)
    local tb=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
    local tg=$(echo "scale=1;$tb/1073741824"|bc 2>/dev/null||echo "?")
    local fp=$(vm_stat 2>/dev/null|awk '/Pages free/{gsub(/\./,"",$3);print $3}')
    local ip=$(vm_stat 2>/dev/null|awk '/Pages inactive/{gsub(/\./,"",$3);print $3}')
    local fb=$(((${fp:-0}+${ip:-0})*ps))
    local fg=$(echo "scale=1;$fb/1073741824"|bc 2>/dev/null||echo "?")
    local ug=$(echo "scale=1;($tb-$fb)/1073741824"|bc 2>/dev/null||echo "?")
    echo "${ug}/${tg}GB(free:${fg}GB)"
}
check_mem() {
    local m=$(get_mem); local f=$(echo "$m"|grep -oE 'free:[0-9.]+'|grep -oE '[0-9.]+')
    [ "$(echo "${f:-0}<1.0"|bc 2>/dev/null)" = "1" ] && { notify "⛔ OOM! 💾$m"; return 1; }
    [ "$(echo "${f:-0}<2.0"|bc 2>/dev/null)" = "1" ] && notify "⚠️ 記憶體偏低 💾$m"
    return 0
}

# --- Task/Part 封裝函數 ---
task_start() {
    local num=$1; local desc="$2"
    TASK_NUM=$num; TASK_DESC="$desc"
    PCT=$((TASK_DONE * 100 / TASK_TOTAL))
    local m=$(get_mem)
    MSG="🏗️ P${SPRINT} ▶️ Task ${num}/${TASK_TOTAL}: ${desc}
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
💾 ${m} | $(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
task_done() {
    TASK_DONE=$((TASK_DONE + 1))
    PCT=$((TASK_DONE * 100 / TASK_TOTAL))
    MSG="🏗️ P${SPRINT} ✅ Task ${TASK_NUM}/${TASK_TOTAL}: ${TASK_DESC}
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
$(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
part_start() {
    local id="$1"; local desc="$2"; local count=$3
    PART_ID="$id"; PART_DESC="$desc"
    check_mem || { notify "⛔ P${SPRINT} OOM at Part ${id} 💾$(get_mem)"; exit 1; }
    local m=$(get_mem)
    MSG="🏗️ P${SPRINT} ▶️ Part ${id}: ${desc} (${count} tasks)
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
💾 ${m} | $(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}
part_done() {
    PART_DONE=$((PART_DONE + 1))
    PCT=$((TASK_DONE * 100 / TASK_TOTAL))
    local next="$1"
    git add -A && git commit -m "[P${SPRINT}] Part ${PART_ID}: ${PART_DESC}" 2>/dev/null && git push origin main 2>/dev/null
    MSG="🏗️ P${SPRINT} Part ${PART_ID} ✅ ${PART_DESC}
📊 ${TASK_DONE}/${TASK_TOTAL} | Part ${PART_DONE}/${PART_TOTAL} | ${PCT}%
⏭️ ${next} | $(hostname -s) $(date '+%m/%d %H:%M')"
    echo "$MSG" && notify "$MSG"
}

# --- xcodebuild 互斥鎖 (v1.23.3) ---
XCODE_LOCK=/tmp/zigma-xcodebuild.lock
xcode_lock() {
    local waited=0
    while ! mkdir "$XCODE_LOCK" 2>/dev/null; do
        if [ $waited -ge 300 ]; then echo "⛔ xcodebuild lock 超時"; return 1; fi
        [ $((waited % 30)) -eq 0 ] && echo "⏳ 等待 xcodebuild lock... (${waited}s)"
        sleep 5; waited=$((waited + 5))
    done
    echo $$ > "$XCODE_LOCK/pid"; echo "🔒 xcodebuild lock 取得"; return 0
}
xcode_unlock() { rm -rf "$XCODE_LOCK" 2>/dev/null; echo "🔓 xcodebuild lock 釋放"; }
trap 'xcode_unlock' EXIT

# --- 殭屍清理 + 環境 ---
echo "🧹 清理殭屍 Python..."
pkill -f "python.*pytest" 2>/dev/null
pkill -f "python.*promptbim" 2>/dev/null
pkill -f "python.*PySide6" 2>/dev/null
sleep 1
export QT_QPA_PLATFORM=offscreen
echo "✅ 全部函數+環境已就緒"
```

---

## ★★★ Sprint 啟動順序（MANDATORY）★★★

```bash
# 4. 讀取 PROJECT_STATUS.md
echo "📋 讀取 PROJECT_STATUS.md..."
cat docs/PROJECT_STATUS.md 2>/dev/null || echo "（尚未建立，Sprint 結束時建立）"

# 5. check_mem
check_mem || exit 1

# 6. git pull
git pull origin main

# 7. 啟動 notify
MEM=$(get_mem)
MSG="🏗️ Zigma M1-MVP Sprint 啟動
📋 ${SPRINT_DESC}
🎯 ${TASK_TOTAL} Tasks / ${PART_TOTAL} Parts → ${VERSION}
💾 ${MEM}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')"
notify "$MSG"

# 8. 文件檢查
CLAUDE_SIZE=$(wc -c < CLAUDE.md | tr -d ' ')
SKILL_SIZE=$(wc -c < SKILL.md | tr -d ' ')
[ "$CLAUDE_SIZE" -lt 5000 ] && { notify "⛔ CLAUDE.md 太小 ($CLAUDE_SIZE)"; exit 1; }
[ "$SKILL_SIZE" -lt 15000 ] && { notify "⛔ SKILL.md 太小 ($SKILL_SIZE)"; exit 1; }
echo "✅ 文件檢查通過 CLAUDE=${CLAUDE_SIZE}B SKILL=${SKILL_SIZE}B"

# 9. 環境檢查
source .env 2>/dev/null
[ -z "$ANTHROPIC_API_KEY" ] && echo "⚠️ ANTHROPIC_API_KEY 未設定（agent_runner 需要）"
echo "✅ 環境檢查完成"
```

---

## 專案結構（Sprint 完成後的目標）

```
PromptBIMTestApp1/
├── CLAUDE.md / SKILL.md / PROJECT.md     ← 不修改前兩個
├── zigma/                                 ← ★ 新建 C++/QML 專案根目錄
│   ├── CMakeLists.txt                     ← Qt6 Quick + Quick3D
│   ├── src/
│   │   ├── main.cpp                       ← QGuiApplication + QQmlEngine
│   │   ├── AgentBridge.h / .cpp           ← QProcess + JSON stdio
│   │   ├── BIMGeometryProvider.h / .cpp   ← QQuick3DGeometry 子類
│   │   ├── BIMMaterialLibrary.h / .cpp    ← PBR 材質庫
│   │   └── BIMSceneBuilder.h / .cpp       ← JSON → QML Scene Graph
│   ├── qml/
│   │   ├── main.qml                       ← ApplicationWindow + SplitView
│   │   ├── ChatPanel.qml                  ← 對話面板
│   │   ├── BIMView3D.qml                  ← View3D + Camera + Orbit
│   │   ├── PropertyPanel.qml              ← 元素屬性
│   │   ├── CostPanel.qml                  ← 成本顯示
│   │   ├── DeltaPanel.qml                 ← Before/After Delta
│   │   ├── SchedulePanel.qml              ← 甘特圖 + 4D
│   │   ├── StatusBar.qml                  ← 狀態列
│   │   ├── ScenePicker.qml                ← 場景選擇
│   │   └── AssetBrowser.qml               ← 零件庫
│   ├── tests/
│   │   └── (ctest 測試)
│   └── build/                             ← cmake build 目錄
├── src/promptbim/                         ← ★ 既有 Python AI 引擎（不動）
│   ├── agents/                            ← orchestrator, planner, builder, etc.
│   └── bim/                               ← cost, simulation, components, codes
├── agent_runner.py                        ← ★ 新建：Python↔C++ 橋接
├── tests/                                 ← 既有 Python tests
└── sprints/PROMPT_M1-MVP.md               ← 本文件
```

---

## Part A: AgentBridge — Python↔C++ 通訊 (8 Tasks)

```bash
part_start "A" "AgentBridge — Python↔C++ 通訊" 8
```

### Task 1: CMakeLists.txt

```bash
task_start 1 "CMakeLists.txt: Qt6 Quick + Quick3D + Core + ShaderTools"
```

建立 `zigma/CMakeLists.txt`:
- `cmake_minimum_required(VERSION 3.21)`
- `project(Zigma VERSION 0.1.0 LANGUAGES CXX)`
- `set(CMAKE_CXX_STANDARD 17)`
- `find_package(Qt6 REQUIRED COMPONENTS Core Gui Qml Quick Quick3D ShaderTools)`
- `qt_standard_project_setup()`
- `qt_add_executable(zigma src/main.cpp)`
- `qt_add_qml_module(zigma URI Zigma VERSION 1.0 QML_FILES ...)`
- `target_link_libraries(zigma PRIVATE Qt6::Core Qt6::Gui Qt6::Qml Qt6::Quick Qt6::Quick3D)`
- 建立 `zigma/src/main.cpp` — 最小 QGuiApplication + QQmlApplicationEngine

驗收: `cd zigma && cmake -B build -G Ninja -DCMAKE_PREFIX_PATH=/opt/homebrew/opt/qt && cmake --build build` 成功

```bash
task_done
```

### Task 2: AgentBridge C++ class

```bash
task_start 2 "AgentBridge C++: QProcess spawn, JSON stdio, heartbeat"
```

建立 `zigma/src/AgentBridge.h` 和 `.cpp`:
- 繼承 `QObject`，`Q_OBJECT` macro，`QML_ELEMENT`
- `Q_PROPERTY(bool connected READ isConnected NOTIFY connectedChanged)`
- `Q_PROPERTY(bool busy READ isBusy NOTIFY busyChanged)`
- `Q_INVOKABLE void generate(const QString& prompt, const QJsonObject& landData)`
- `Q_INVOKABLE void modify(const QString& intent)`
- `Q_INVOKABLE void getCost()` / `getSchedule()`
- 內部: `QProcess* m_process` — spawn `agent_runner.py`
- JSON stdio: 每行一個 JSON (`\n` 分隔)
- heartbeat: QTimer 120s timeout，超時自動重啟 Python
- OOM 隔離: `QProcess::crashed` → emit error signal → GUI 不受影響
- signals: `resultReady(QJsonObject)`, `statusUpdate(QString msg, double progress)`, `deltaReady(QJsonObject)`, `errorOccurred(QString)`

驗收: build 成功，AgentBridge 在 QML 中可用

```bash
task_done
```

### Task 3: agent_runner.py

```bash
task_start 3 "agent_runner.py: asyncio → orchestrator, streaming"
```

建立 `agent_runner.py`（專案根目錄，與 src/promptbim/ 同層）:
- `#!/usr/bin/env python3`
- `import sys, json, asyncio`
- `sys.path.insert(0, 'src')` — 讓 promptbim 可 import
- `from promptbim.agents.orchestrator import Orchestrator`
- 主迴圈: `while True: line = sys.stdin.readline()` → parse JSON
- 支援 type: `generate`, `modify`, `get_cost`, `get_schedule`
- streaming response: `{"type":"status","message":"...","progress":0.5}` 寫到 stdout
- 最終結果: `{"type":"result","model":{...},"cost":{...},"schedule":{...}}`
- 所有 stdout 用 `json.dumps() + '\n' + sys.stdout.flush()`
- 例外處理: catch all → `{"type":"error","message":"..."}`
- 注意: `source .env` 中的 `ANTHROPIC_API_KEY` 需要透過環境變數傳入

驗收: `echo '{"type":"generate","prompt":"建立一個標準工廠","land":{"width":100,"depth":80}}' | conda run -n promptbim python agent_runner.py` 能收到 JSON 結果

```bash
task_done
```

### Task 4: JSON Protocol schema

```bash
task_start 4 "JSON Protocol: generate/modify/get_cost/get_schedule schema"
```

建立 `zigma/docs/agent_protocol.md`:
- Request schema (C++ → Python):
  - `{"type":"generate","prompt":"...","land":{"width":N,"depth":N}}`
  - `{"type":"modify","intent":"...","undo":false}`
  - `{"type":"get_cost"}`
  - `{"type":"get_schedule"}`
- Response schema (Python → C++):
  - Status: `{"type":"status","message":"...","progress":0.0-1.0}`
  - Result: `{"type":"result","model":{"elements":[...],"vertices":[[x,y,z],...],"indices":[[i0,i1,i2],...]},"cost":{"total":N,"breakdown":{...}},"schedule":{"total_days":N,"phases":[...]}}`
  - Delta: `{"type":"delta","cost_delta":N,"schedule_delta":N,"gfa_delta":N,"model":{...}}`
  - Error: `{"type":"error","message":"..."}`

驗收: 文件完成，schema 與 agent_runner.py 一致

```bash
task_done
```

### Task 5: mesh 序列化

```bash
task_start 5 "mesh 序列化: Python Builder mesh → JSON vertex/index"
```

修改 `agent_runner.py` 的 mesh 輸出:
- 從現有 Builder 取出 mesh data (頂點、面索引)
- 每個 BIM element 包含:
  - `type`: "wall" | "slab" | "column" | "window" | "door" | "roof" | "pool" | "parking" | ...
  - `material`: "concrete" | "glass" | "steel" | "wood"
  - `vertices`: [[x,y,z], ...] — 頂點座標 (公尺)
  - `indices`: [[i0,i1,i2], ...] — 三角面索引
  - `color`: [r,g,b,a] — 選用
  - `dimensions`: {width, height, depth} — BIM 尺寸
  - `cost`: 個別元素成本
- 如果現有 Builder 不直接產出 mesh，建立一個 `mesh_serializer.py` 工具將 Builder 輸出轉為上述格式
- 簡單幾何（牆=box, 柱=cylinder, 板=flat box）用 Python 算出頂點即可

驗收: generate 回傳的 JSON 包含完整 vertices/indices/elements

```bash
task_done
```

### Task 6: AgentBridge ctest

```bash
task_start 6 "AgentBridge ctest ≥5"
```

建立 `zigma/tests/test_agent_bridge.cpp`:
- 使用 Qt Test framework (`QTest`)
- Test 1: AgentBridge 建構不 crash
- Test 2: JSON request 格式正確
- Test 3: JSON response 解析正確
- Test 4: heartbeat timeout 偵測
- Test 5: QProcess 不存在時 graceful error
- CMakeLists.txt 加入 `add_test`

驗收: `cd zigma/build && ctest --output-on-failure` 至少 5 個 PASS

```bash
task_done
```

### Task 7: agent_runner pytest

```bash
task_start 7 "agent_runner pytest ≥5"
```

建立 `tests/test_agent_runner.py`:
- Test 1: import agent_runner 不 crash
- Test 2: generate request 解析正確
- Test 3: modify request 解析正確
- Test 4: mesh 序列化格式正確 (有 vertices, indices, elements)
- Test 5: error handling (不合法 JSON → error response)
- 使用 conda run -n promptbim 執行

驗收: `conda run -n promptbim python -m pytest tests/test_agent_runner.py -x --tb=short` PASS

```bash
task_done
```

### Task 8: E2E 驗證

```bash
task_start 8 "E2E: prompt → Python → JSON → C++ 收到結果"
```

- 先啟動 agent_runner.py (手動或 subprocess)
- 從 C++ AgentBridge 發送 generate request
- 確認 Python 回傳 status + result JSON
- 確認 C++ 端能完整解析 model/cost/schedule
- 可以用一個 E2E test 或手動驗證

驗收: 端到端通過，C++ 收到完整 BIM model JSON

```bash
task_done
```

```bash
part_done "Part B: Qt Quick 3D 渲染核心"
```

---

## Part B: Qt Quick 3D 渲染核心 (8 Tasks)

```bash
part_start "B" "Qt Quick 3D 渲染核心" 8
```

### Task 9: BIMGeometryProvider

```bash
task_start 9 "BIMGeometryProvider: QQuick3DGeometry, loadFromJSON"
```

建立 `zigma/src/BIMGeometryProvider.h / .cpp`:
- 繼承 `QQuick3DGeometry`，`QML_ELEMENT`
- `Q_INVOKABLE void loadFromJSON(const QJsonObject& meshData)`
- 從 JSON 讀取 vertices [[x,y,z],...] → `QByteArray` vertex buffer (float x,y,z + nx,ny,nz)
- 從 JSON 讀取 indices [[i0,i1,i2],...] → `QByteArray` index buffer (uint32)
- 自動計算 face normals
- `setVertexData()`, `setIndexData()`, `setStride(24)` (3 pos + 3 normal × 4 bytes)
- `setBounds(min, max)` 從頂點計算
- `addAttribute(Position, ...)`, `addAttribute(Normal, ...)`

驗收: 餵入 JSON mesh data 後 QQuick3DGeometry 的 vertexData/indexData 非空

```bash
task_done
```

### Task 10: BIMMaterialLibrary

```bash
task_start 10 "BIMMaterialLibrary: concrete/glass/steel/wood → PBR"
```

在 QML 中定義 PBR 材質（或在 C++ 中用 QQuick3DPrincipledMaterial）:
- concrete: baseColor gray(0.6,0.6,0.6), roughness 0.85, metalness 0.0
- glass: baseColor light-blue(0.7,0.85,1.0), roughness 0.05, metalness 0.0, opacity 0.3
- steel: baseColor silver(0.8,0.8,0.82), roughness 0.35, metalness 0.9
- wood: baseColor brown(0.55,0.35,0.15), roughness 0.75, metalness 0.0
- 建立 `BIMMaterialLibrary.h / .cpp` — `getMaterial(QString type)` 回傳材質

驗收: 4 種材質在 3D 場景中可見且可區分

```bash
task_done
```

### Task 11: BIMSceneBuilder

```bash
task_start 11 "BIMSceneBuilder: JSON model → Model QML nodes"
```

建立 `zigma/src/BIMSceneBuilder.h / .cpp`:
- `Q_INVOKABLE void buildScene(const QJsonObject& modelData)`
- 遍歷 `elements` array，為每個 element:
  - 建立 `BIMGeometryProvider` instance
  - 根據 element.type 指定材質
  - 建立 `QQuick3DModel` node，掛到 scene graph
  - 設定 position/scale（如果 element 有 transform）
- 清除舊場景: `clearScene()`
- signal: `sceneReady()`, `elementCount(int)`
- 每個 element 記錄 ID，用於 picking

驗收: 一個多元素 BIM 場景（牆+柱+板）能正確組裝渲染

```bash
task_done
```

### Task 12: BIMView3D.qml

```bash
task_start 12 "BIMView3D.qml: View3D + PerspectiveCamera + OrbitCameraController"
```

建立 `zigma/qml/BIMView3D.qml`:
- `View3D` 填滿父容器
- `PerspectiveCamera` — 預設位置看向原點
- `OrbitCameraController` — 滑鼠拖動旋轉、滾輪縮放、右鍵平移
- `DirectionalLight` — 主光 + 環境光
- `environment: SceneEnvironment { backgroundMode: Color; clearColor: "#1a1a2e" }`
- 暴露 property: `currentCamera`, `sceneRoot`

驗收: 空場景可旋轉縮放，載入 mesh 後可看到 3D

```bash
task_done
```

### Task 13: Picking

```bash
task_start 13 "Picking: View3D pick → element ID → signal"
```

在 `BIMView3D.qml` 加入:
- `MouseArea` 或 `TapHandler` 捕捉點擊
- `view3d.pick(mouseX, mouseY)` → `PickResult`
- 從 PickResult 取得被點擊的 Model → 查找 element ID
- signal: `elementPicked(string elementId, var elementData)`
- highlight: 被選取的 element 改變材質或加 outline

驗收: 點擊 3D 元素能取得正確的 element ID

```bash
task_done
```

### Task 14: 多視角

```bash
task_start 14 "多視角: Perspective / Top / Front / Right"
```

- 4 個預設相機位置:
  - Perspective: 斜 45° 俯視
  - Top: 正上方 Y 軸向下
  - Front: 正面 Z 軸向前
  - Right: 右側 X 軸向右
- QML 中 4 個按鈕或 ComboBox 切換
- 動畫過渡: `NumberAnimation` 平滑切換

驗收: 4 個視角可切換，過渡平滑

```bash
task_done
```

### Task 15: benchmark

```bash
task_start 15 "benchmark: Fab 場景渲染 < 300MB"
```

- 用 agent_runner 產生 S2 Fab 場景 (半導體廠)
- 載入到 BIMView3D
- 測量記憶體用量 (get_mem before/after)
- 目標: 渲染後增量 < 300MB

驗收: 記憶體增量 < 300MB

```bash
task_done
```

### Task 16: ctest ≥10

```bash
task_start 16 "ctest ≥10 Qt Quick 3D 測試"
```

擴充 `zigma/tests/`:
- BIMGeometryProvider: loadFromJSON 正確、空 data 不 crash、vertex count 正確
- BIMMaterialLibrary: 4 種材質都能取得
- BIMSceneBuilder: buildScene 不 crash、element count 正確、clearScene 清空
- 至少 10 個測試

驗收: `cd zigma/build && ctest` 至少 10 PASS

```bash
task_done
```

```bash
part_done "Part C: QML GUI 骨架"
```

---

## Part C: QML GUI 骨架 (8 Tasks) → 🏷️ alpha

```bash
part_start "C" "QML GUI 骨架" 8
```

### Task 17: main.qml

```bash
task_start 17 "main.qml: SplitView (左Chat/中3D/右Property)"
```

建立 `zigma/qml/main.qml`:
- `ApplicationWindow` — title: "Zigma PromptToBuild", 預設 1280×800
- `SplitView` orientation: horizontal
  - 左: ChatPanel (寬 300px)
  - 中: BIMView3D (填滿)
  - 右: PropertyPanel (寬 280px)
- 底部: StatusBar
- `menuBar: MenuBar` — File / View / Help

驗收: 三欄佈局正確顯示

```bash
task_done
```

### Task 18: ChatPanel.qml

```bash
task_start 18 "ChatPanel.qml: TextInput + streaming + 歷史"
```

- `ListView` 顯示對話歷史 (model: ListModel)
- delegate: 區分 user / ai 訊息 (不同顏色/對齊)
- 底部: `TextField` + "Send" `Button`
- AI 回覆: streaming 逐字顯示（從 AgentBridge statusUpdate signal）
- 結果完成後: 顯示 "✅ 生成完成" + 摘要

驗收: 能輸入文字、看到 AI 回覆

```bash
task_done
```

### Task 19: PropertyPanel.qml

```bash
task_start 19 "PropertyPanel.qml: 點擊 → BIM 屬性顯示"
```

- 接收 `BIMView3D.elementPicked` signal
- 顯示: type, dimensions (W×H×D), material, cost
- 格式化: cost 顯示為 NT$ with comma separators
- 無選取時: 顯示 "點擊 3D 元素查看屬性"

驗收: 點擊 3D 元素後屬性顯示正確

```bash
task_done
```

### Task 20: StatusBar.qml

```bash
task_start 20 "StatusBar.qml: 記憶體/AI狀態/進度"
```

- 左: AI 狀態 (Connected/Busy/Error) 以圓點顏色表示
- 中: 進度文字 + ProgressBar (從 AgentBridge.statusUpdate)
- 右: 記憶體用量 (定期更新)

驗收: 狀態可見

```bash
task_done
```

### Task 21: ChatPanel ↔ AgentBridge

```bash
task_start 21 "ChatPanel ↔ AgentBridge 連接"
```

- ChatPanel "Send" → 呼叫 `agentBridge.generate(text, landData)`
- AgentBridge `statusUpdate` → ChatPanel streaming 文字
- AgentBridge `resultReady` → ChatPanel "完成" 訊息

驗收: 在 ChatPanel 輸入 prompt 能觸發 AI 生成

```bash
task_done
```

### Task 22: BIMView3D ↔ BIMSceneBuilder

```bash
task_start 22 "BIMView3D ↔ BIMSceneBuilder 連接"
```

- AgentBridge `resultReady` → BIMSceneBuilder.buildScene(model)
- BIMSceneBuilder 建好的 nodes 掛到 BIMView3D 的 scene root
- 自動 fit camera 到新場景

驗收: AI 生成結果自動渲染在 3D 視窗

```bash
task_done
```

### Task 23: Picking → PropertyPanel

```bash
task_start 23 "Picking → PropertyPanel 連接"
```

- BIMView3D `elementPicked` → PropertyPanel 更新屬性
- 多個 panel 之間的 signal/slot 連接在 main.qml 中完成

驗收: 完整流程：prompt → AI → 3D → 點擊 → 屬性

```bash
task_done
```

### Task 24: Mac build 驗證

```bash
task_start 24 "Mac build 驗證 (Metal)"
```

- 完整 clean build: `cd zigma && rm -rf build && cmake -B build -G Ninja && cmake --build build`
- 執行: `./build/zigma` — 確認 GUI 顯示、3D 渲染 (Metal backend)
- 跑一次完整流程: 輸入 prompt → AI → 3D → 點擊 → 屬性

驗收: macOS Metal build + run 正常

```bash
task_done
```

```bash
# ★ alpha tag
git tag mvp-v0.1.0-alpha
git push origin mvp-v0.1.0-alpha
notify "🏷️ mvp-v0.1.0-alpha tagged! prompt→3D→點擊→屬性 完成"
part_done "Part D: CostPanel + DeltaPanel"
```

---

## Part D: CostPanel + DeltaPanel (8 Tasks)

```bash
part_start "D" "CostPanel + DeltaPanel" 8
```

### Task 25-32 (Part D)

| Task | 描述 |
|------|------|
| 25 | `task_start 25 "CostPanel.qml: NT$ + 圓餅圖"` — ListView 顯示分項, Canvas 畫圓餅圖 (Civil/Structural/MEP/Finishes), 總成本 NT$ formatted |
| 26 | `task_start 26 "DeltaPanel.qml: Before/After + Undo"` — 成本/GFA/工期 增減, 色彩(綠↓紅↑), Undo 按鈕 |
| 27 | `task_start 27 "Modifier E2E: 變更游泳池→停車場"` — AgentBridge.modify(intent) → delta JSON → DeltaPanel + 3D 更新 |
| 28 | `task_start 28 "Cost 資料綁定: Python→JSON→QML"` — AgentBridge resultReady → CostPanel property binding |
| 29 | `task_start 29 "Delta 動畫: 數字滾動+色彩"` — NumberAnimation 在數字變化時, 綠色=減少, 紅色=增加 |
| 30 | `task_start 30 "Undo/Redo stack: 10次"` — C++ UndoStack 或 QML ListModel 儲存歷史 |
| 31 | `task_start 31 "多次修改累計 Delta 歷史"` — ListView 顯示每次修改的 delta |
| 32 | `task_start 32 "ctest ≥5 CostPanel/DeltaPanel"` — 成本格式化、delta 計算、undo 正確性 |

每個 Task 都用 `task_start N "..."` 開始，`task_done` 結束。

```bash
part_done "Part E: SchedulePanel + 4D"
```

---

## Part E: SchedulePanel + 4D (8 Tasks)

```bash
part_start "E" "SchedulePanel + 4D" 8
```

### Task 33-40 (Part E)

| Task | 描述 |
|------|------|
| 33 | `task_start 33 "SchedulePanel.qml: 甘特圖+16-phase"` — QML Canvas 自繪甘特圖, 16 phase 顏色區分, 總天數 |
| 34 | `task_start 34 "4D Timeline Slider + Play/Pause"` — Slider 控制時間, Play/Pause 按鈕, 速度 1x/2x/5x/10x |
| 35 | `task_start 35 "Gantt↔3D 雙向聯動"` — 點擊甘特圖→3D跳轉, 點擊3D→甘特圖highlight |
| 36 | `task_start 36 "施工機械3D隨timeline"` — 簡易起重機/挖土機 mesh, 根據 phase 移動位置 |
| 37 | `task_start 37 "Phase顏色: 實色/半透明/隱藏"` — 已完工=實色, 施工中=opacity 0.5, 未開始=invisible |
| 38 | `task_start 38 "截圖匯出→PNG"` — View3D.grabToImage → save to file |
| 39 | `task_start 39 "schedule資料綁定"` — Python schedule engine → JSON → QML |
| 40 | `task_start 40 "ctest ≥5 Schedule/4D"` — 甘特圖資料、timeline 範圍、phase visibility |

```bash
part_done "Part F: TSMC Demo 場景"
```

---

## Part F: TSMC Demo 場景 (9 Tasks) → 🏷️ beta

```bash
part_start "F" "TSMC Demo 場景" 9
```

### Task 41-49 (Part F)

| Task | 描述 |
|------|------|
| 41 | `task_start 41 "ScenePicker.qml: S1/S2/S3"` — 下拉選單或按鈕：別墅/半導體廠/數據中心 |
| 42 | `task_start 42 "S2半導體廠房全流程"` — "建立TSMC風格半導體廠120m×80m" → 3D+成本+4D 全正確 |
| 43 | `task_start 43 "S3數據中心驗證"` — 全流程正確 |
| 44 | `task_start 44 "S1別墅驗證"` — 全流程正確 |
| 45 | `task_start 45 "修改E2E: 2F高度→6m"` — "請將2F Data Hall高度增加到6m" → Delta正確 |
| 46 | `task_start 46 "修改E2E: 游泳池→停車場"` — "變更游泳池成為員工停車場" → Delta正確 |
| 47 | `task_start 47 "AssetBrowser.qml: 搜尋+替換"` — 搜尋零件庫 + 點擊替換 + 成本更新 |
| 48 | `task_start 48 "法規面板: TW-IND-001~004"` — 合規 checklist 顯示 pass/fail |
| 49 | `task_start 49 "7分鐘Demo腳本v1 walkthrough"` — 完整跑完無中斷 |

```bash
# ★ beta tag
git tag mvp-v0.1.0-beta
git push origin mvp-v0.1.0-beta
notify "🏷️ mvp-v0.1.0-beta tagged! ★ TSMC 7分鐘 Demo 可用!"
part_done "Part G: io_usd ILOS"
```

---

## Part G: io_usd — ILOS USD 支援 (6 Tasks)

```bash
part_start "G" "io_usd — ILOS USD 支援" 6
```

### Task 50-55 (Part G)

| Task | 描述 |
|------|------|
| 50 | `task_start 50 "io_usd import: ILOS metadata"` — Python: 讀取 USD, 提取 ilos: attributes (category, part_number, manufacturer) |
| 51 | `task_start 51 "io_usd import: /Connections/ 解析"` — 提取 port_type, port_medium, port_size_mm, port_direction |
| 52 | `task_start 52 "io_usd import: Instance 解析"` — `final_xf = inst_xf × proto_inv × mesh_xf`, 不用 XformCache |
| 53 | `task_start 53 "io_usd export: mesh→USD"` — Python mesh → USD mesh + ilos: metadata, Omniverse 可開啟 |
| 54 | `task_start 54 "ILOS測試場景載入"` — 建立測試 USD 檔案, 載入 + 3D 顯示 |
| 55 | `task_start 55 "ilos: metadata→PropertyPanel"` — 在 PropertyPanel 顯示 category/part_number |

注意: io_usd 使用 `from pxr import Usd, UsdGeom, UsdShade`，需要 `conda run -n promptbim` 環境中有 `usd-core`。如果沒有，先安裝: `conda run -n promptbim pip install usd-core`

```bash
part_done "Part H: 展示打磨"
```

---

## Part H: 展示打磨 (7 Tasks, 排除 Win GPU)

```bash
part_start "H" "展示打磨" 7
```

### Task 56-62 (Part H)

| Task | 描述 |
|------|------|
| 56 | `task_start 56 "Dark/Light theme"` — QML: 兩套色彩方案, 切換按鈕或跟隨系統 |
| 57 | `task_start 57 "Loading animation"` — BusyIndicator + 文字, AI 生成時顯示 |
| 58 | `task_start 58 "歡迎畫面: Zigma品牌"` — Splash Screen: logo + "Zigma PromptToBuild" + loading |
| 59 | `task_start 59 "鍵盤快捷鍵"` — Space=旋轉, F=fit to view, 1-4=視角切換 |
| 60 | `task_start 60 "Mac Metal 渲染驗證"` — 最終 macOS Metal 渲染確認, 所有 QML 正常 |
| 61 | `task_start 61 "記憶體profiling <500MB"` — 全場景載入後 get_mem, 確認 <500MB 增量 |
| 62 | `task_start 62 "crash recovery: Python→自動重啟"` — AgentBridge 偵測 QProcess crash → 自動重啟 → GUI 顯示 "AI 重新連接中..." |

```bash
part_done "Part I: Release"
```

---

## Part I: Release (6 Tasks) → 🏷️ mvp-v0.1.0

```bash
part_start "I" "Release mvp-v0.1.0" 6
```

### Task 63-68 (Part I)

| Task | 描述 |
|------|------|
| 63 | `task_start 63 "E2E: 3場景×2修改=6 scenarios"` — S1/S2/S3 各跑 generate + modify, 全部通過 |
| 64 | `task_start 64 "Demo腳本v2.0"` — 建立 `docs/Zigma_Demo_Script_v2.0.md`: 完整 7 分鐘 Qt Quick 3D 版 walkthrough |
| 65 | `task_start 65 "TSMC簡報v2.0"` — 更新 `docs/Zigma_TSMC_Presentation_v2.0.md`: 10 頁, 含截圖 |
| 66 | `task_start 66 "SKILL.md v5.0 更新"` — ⚠️ 不直接修改 SKILL.md! 建立 `docs/SKILL_v5.0_draft.md` 草稿供 Michael 審閱 |
| 67 | `task_start 67 "PROJECT.md 更新"` — 更新 PROJECT.md: M1-MVP 完成, 68T, mvp-v0.1.0 |
| 68 | `task_start 68 "git tag mvp-v0.1.0"` — tag + push |

```bash
# ★ final tag
git tag mvp-v0.1.0
git push origin mvp-v0.1.0

# 更新 PROJECT_STATUS.md
cat >> docs/PROJECT_STATUS.md << STATUSEOF

### Sprint M1-MVP 執行結果 — $(date '+%Y-%m-%d %H:%M')
- **狀態:** ✅ 完成
- **版本:** mvp-v0.1.0
- **Tasks:** ${TASK_DONE}/${TASK_TOTAL}
- **記憶體:** $(get_mem)
- **Tags:** mvp-v0.1.0-alpha, mvp-v0.1.0-beta, mvp-v0.1.0
- **錯誤:** （無）
STATUSEOF
git add -A && git commit -m "[status] M1-MVP result" && git push origin main 2>/dev/null

# Sprint 完成通知
MEM=$(get_mem)
MSG="🏗️ Zigma M1-MVP Sprint 完成 🎉
🏷️ mvp-v0.1.0 | ${TASK_TOTAL} Tasks / ${PART_TOTAL} Parts
📊 完成度: 100% ✅
🏷️ Tags: alpha + beta + mvp-v0.1.0
💾 ${MEM}
📍 $(hostname -s) | $(date '+%m/%d %H:%M')
🪟 剩餘: 2 個 Windows-only tasks 需手動完成"
notify "$MSG"

# pkill 清理
pkill -f "python.*pytest" 2>/dev/null
pkill -f "python.*promptbim" 2>/dev/null
echo "✅ M1-MVP Sprint 完成! 🎉"
```

```bash
part_done "Sprint 完成"
```

---

## PROMPT 合規性自查

```
☑ 函數定義: notify + get_mem + check_mem + task_start + task_done + part_start + part_done
☑ xcode_lock / xcode_unlock (本 Sprint 不用 xcodebuild，但定義了以備)
☑ 殭屍清理 (pkill) + QT_QPA_PLATFORM=offscreen
☑ ★ 啟動時讀取 docs/PROJECT_STATUS.md
☑ ★ 啟動順序: 函數→清理→讀STATUS→check_mem→git pull→notify→文件檢查→環境檢查
☑ ★ 啟動/完成/錯誤通知多行格式
☑ ★ 每個 Task 用 task_start/task_done 包夾
☑ ★ 每個 Part 用 part_start/part_done 包夾
☑ ★ Sprint 結束更新 PROJECT_STATUS.md
☑ 不修改 CLAUDE.md / SKILL.md
☑ SKILL.md v5.0 改為建立草稿供人工審閱
```

---

## Sprint 完成後手動做（Windows）

1. 🪟 T25: `git pull` on Windows → cmake -G "Visual Studio 17 2022" → build + run
2. 🪟 T11: RTX 4090 GPU 渲染優化 (QSG_RHI_BACKEND=d3d12/vulkan)

---

*PROMPT_M1-MVP.md | Zigma PromptToBuild | 2026-03-28*
*68 Tasks / 9 Parts / 3 Tags / Mac Mini M4 / Qt 6.11.0*
