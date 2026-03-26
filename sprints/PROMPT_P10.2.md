# PROMPT_P10.2.md — Sprint P10.2: Debug Logging System

> 版本: v1.0.0 | 建立時間: 2026-03-25
> 前置 Sprint: P0~P9 ✅ 全部完成
> 依賴: 所有模組

## Sprint 目標

為整個專案加入**完整的 Debug Logging 系統**，每個功能模組都有詳細的 console output，方便開發除錯。支援 Debug Mode 開關：開發時啟用，Production 關閉。

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。

## 必讀文件
1. SKILL.md
2. TODO.md
3. CLAUDE.md（含 Rule 8 iMessage 通知）

---

## 架構設計

### 核心：統一 Logger 系統

```python
# src/promptbim/debug.py — 專案統一 Debug Logger

import logging
import os
import sys
from pathlib import Path
from datetime import datetime

# Debug Mode 控制
# 環境變數 PROMPTBIM_DEBUG=1 或 config.py 中設定
DEBUG_MODE = os.getenv("PROMPTBIM_DEBUG", "0") == "1"

# Log 級別
# DEBUG mode: DEBUG level（全部輸出）
# Production:  WARNING level（只輸出警告和錯誤）

def get_logger(module_name: str) -> logging.Logger:
    """取得模組專用 logger，自動根據 DEBUG_MODE 設定級別。"""
    logger = logging.getLogger(f"promptbim.{module_name}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.WARNING)
    return logger

def enable_debug():
    """Runtime 啟用 Debug Mode。"""
    global DEBUG_MODE
    DEBUG_MODE = True
    # 更新所有已建立的 logger
    for name in logging.Logger.manager.loggerDict:
        if name.startswith("promptbim."):
            logging.getLogger(name).setLevel(logging.DEBUG)

def disable_debug():
    """Runtime 關閉 Debug Mode。"""
    global DEBUG_MODE
    DEBUG_MODE = False
    for name in logging.Logger.manager.loggerDict:
        if name.startswith("promptbim."):
            logging.getLogger(name).setLevel(logging.WARNING)
```

### Debug Mode 啟用方式（三種）

1. **環境變數**：`export PROMPTBIM_DEBUG=1`
2. **CLI 參數**：`python -m promptbim gui --debug`
3. **Config**：`.env` 中 `PROMPTBIM_DEBUG=1`

### Production 行為

- `PROMPTBIM_DEBUG=0`（預設）
- 只輸出 WARNING 和 ERROR
- 無效能影響（logging 判斷級別後跳過）

---

## Task 清單

### Task 1: 建立 Debug Logger 基礎設施

- ⬜ `src/promptbim/debug.py` — 統一 Logger 系統
  - `get_logger(module_name)` — 取得模組 logger
  - `enable_debug()` / `disable_debug()` — Runtime 切換
  - `DEBUG_MODE` 全域旗標
  - 支援 file output（可選，寫入 `logs/` 目錄）
  - 彩色 console output（模組名不同顏色）
- ⬜ `src/promptbim/config.py` — 加入 `debug_mode: bool = False` 設定
- ⬜ `src/promptbim/__main__.py` — CLI 加入 `--debug` 參數

### Task 2: 土地匯入模組 Debug Log

- ⬜ `land/parsers/geojson.py` — 記錄：檔案路徑、feature 數量、解析的頂點數、座標範圍
- ⬜ `land/parsers/shapefile.py` — 記錄：欄位名稱、geometry type、CRS
- ⬜ `land/parsers/dxf.py` — 記錄：layer 名稱、entity 類型和數量
- ⬜ `land/parsers/manual.py` — 記錄：輸入座標、驗證結果
- ⬜ `land/parsers/image_ai.py` — 記錄：圖片尺寸、base64 大小、API 請求/回應時間、confidence
- ⬜ `land/parsers/image_preprocess.py` — 記錄：原始尺寸、處理後尺寸、格式轉換
- ⬜ `land/setback.py` — 記錄：退縮距離、結果面積
- ⬜ `land/projection.py` — 記錄：來源/目標 CRS、轉換前後座標
- ⬜ `land/boundary_confirm.py` — 記錄：候選數量、confidence 排序、微調操作

### Task 3: BIM 生成模組 Debug Log

- ⬜ `bim/geometry.py` — 記錄：每個 mesh 的頂點數/面數、wall 長度/高度
- ⬜ `bim/ifc_generator.py` — 記錄：IFC 版本、entity 數量（牆/板/屋頂/材質）、檔案大小、生成耗時
- ⬜ `bim/usd_generator.py` — 記錄：stage metrics、prim 數量、材質數量、檔案大小、耗時
- ⬜ `bim/materials.py` — 記錄：材質查詢命中/fallback
- ⬜ `bim/usdz_packer.py` — 記錄：打包方式（UsdUtils vs ZIP）、輸入/輸出大小

### Task 4: 零件庫 + 成本 Debug Log

- ⬜ `bim/components/registry.py` — 記錄：查詢關鍵字、結果數量、零件 ID
- ⬜ `bim/cost/qto.py` — 記錄：每個 QTO 項目的數量
- ⬜ `bim/cost/estimator.py` — 記錄：每行成本、分類小計、總計
- ⬜ `bim/cost/unit_prices_tw.py` — 記錄：單價查詢命中/miss

### Task 5: MEP + 施工模擬 + 監控點 Debug Log

- ⬜ `bim/mep/pathfinder.py` — 記錄：grid 大小、障礙物數量、路徑長度、A* 迭代次數
- ⬜ `bim/mep/planner.py` — 記錄：設備/終端配置數量、每系統路由數
- ⬜ `bim/mep/clash_detect.py` — 記錄：檢查數量、碰撞數量和位置
- ⬜ `bim/simulation/scheduler.py` — 記錄：階段分配、工期計算
- ⬜ `bim/simulation/animator.py` — 記錄：每幀渲染時間、GIF 大小
- ⬜ `bim/monitoring/auto_placement.py` — 記錄：每類型配置數量、總監控點數
- ⬜ `bim/monitoring/rules_engine.py` — 記錄：規則匹配結果

### Task 6: AI Agent Pipeline Debug Log

- ⬜ `agents/base.py` — 記錄：API 請求 model/token count、回應時間、JSON 解析成功/失敗
- ⬜ `agents/enhancer.py` — 記錄：原始 prompt、增強後的 BuildingRequirement
- ⬜ `agents/planner.py` — 記錄：土地 context、生成的 BuildingPlan 摘要（層數/面積/牆數）
- ⬜ `agents/builder.py` — 記錄：IFC/USD 生成開始/完成、檔案路徑和大小
- ⬜ `agents/checker.py` — 記錄：每條規則的 pass/fail、合規率
- ⬜ `agents/modifier.py` — 記錄：修改意圖解析、影響範圍、版本歷史操作
- ⬜ `agents/orchestrator.py` — 記錄：Pipeline 每個階段的開始/結束時間、整體耗時
- ⬜ `agents/land_reader.py` — 記錄：Vision API 請求、辨識結果 confidence

### Task 7: 法規引擎 Debug Log

- ⬜ `codes/registry.py` — 記錄：執行的規則數、pass/fail 統計
- ⬜ `codes/tw_building_code.py` — 記錄：每條規則的輸入值和判定結果
- ⬜ `codes/tw_seismic_code.py` — 記錄：城市/震區對照、結構估算
- ⬜ `codes/tw_fire_code.py` — 記錄：防火等級判定、逃生距離計算
- ⬜ `codes/tw_accessibility_code.py` — 記錄：無障礙設施檢查結果

### Task 8: GUI + Viz Debug Log

- ⬜ `gui/main_window.py` — 記錄：視窗初始化、Tab 切換、建築 plan 載入
- ⬜ `gui/chat_panel.py` — 記錄：使用者輸入、Pipeline 啟動/完成、錯誤
- ⬜ `gui/model_view.py` — 記錄：mesh 載入、渲染時間
- ⬜ `gui/dialogs/import_land.py` — 記錄：檔案拖放事件、格式偵測
- ⬜ `gui/dialogs/confirm_boundary.py` — 記錄：使用者操作（確認/重試/微調）
- ⬜ `viz/model_3d.py` — 記錄：mesh 組裝時間、頂點/面總數
- ⬜ `viz/mep_overlay.py` — 記錄：每系統管線段數
- ⬜ `viz/cost_charts.py` — 記錄：圖表資料點數

### Task 9: 語音 + MCP + Web Debug Log

- ⬜ `voice/stt.py` — 記錄：錄音時長、模型載入時間、辨識結果和 confidence
- ⬜ `mcp/server.py` — 記錄：每個 tool call 的參數和回應時間
- ⬜ `web/app.py` — 記錄：Streamlit session 事件、生成請求

### Task 10: 測試 + 整合

- ⬜ 測試 Debug Mode 開關（enable/disable 切換）
- ⬜ 測試環境變數 `PROMPTBIM_DEBUG=1` 生效
- ⬜ 測試 CLI `--debug` 參數
- ⬜ 測試 Production 模式下無 DEBUG 輸出
- ⬜ 測試 log 不影響現有功能（全部 pytest 仍通過）
- ⬜ 加入 `--debug` 到 SETUP.md 和 README.md 文件
- ⬜ xcodebuild BUILD SUCCEEDED

---

## Debug Log 輸出範例

### Debug Mode ON
```
11:23:45 [promptbim.land.geojson] DEBUG: Loading GeoJSON: /path/to/parcel.geojson
11:23:45 [promptbim.land.geojson] DEBUG: Found 1 feature, type=Polygon, vertices=5
11:23:45 [promptbim.land.geojson] DEBUG: Coordinate range: X[121.5123, 121.5156] Y[25.0234, 25.0267]
11:23:45 [promptbim.land.setback] DEBUG: Uniform setback=3.0m, result area=456.7 sqm
11:23:46 [promptbim.agents.enhancer] DEBUG: API request: model=claude-sonnet-4-20250514, prompt_tokens=1234
11:23:47 [promptbim.agents.enhancer] DEBUG: API response: 1.2s, output_tokens=567, JSON parse OK
11:23:47 [promptbim.agents.planner] DEBUG: Planning: 3-story, footprint=200sqm, 12 walls
11:23:48 [promptbim.bim.ifc] DEBUG: Generating IFC4: 3 stories, 36 walls, 3 slabs, 1 roof
11:23:48 [promptbim.bim.ifc] DEBUG: IFC written: output/building.ifc (245 KB, 0.3s)
11:23:48 [promptbim.bim.usd] DEBUG: Generating USD: 127 prims, 9 materials
11:23:48 [promptbim.bim.usd] DEBUG: USD written: output/building.usda (189 KB, 0.2s)
11:23:49 [promptbim.codes.registry] DEBUG: Running 15 rules... 13 PASS, 2 WARN, 0 FAIL
11:23:49 [promptbim.cost.estimator] DEBUG: Total cost: NT$ 12,345,678 (NT$ 61,728/sqm)
```

### Production Mode (DEBUG OFF)
```
（無 DEBUG 輸出，只有 WARNING 和 ERROR）
11:23:49 [promptbim.agents.base] WARNING: API rate limit approaching (80%)
11:23:50 [promptbim.codes.registry] WARNING: Rule tw_seismic_001 — 耐震不足
```

---

## 執行指令
所有問題答案都是 Yes，不要中斷詢問。
**每個模組都必須加入 debug log，不得遺漏。**
使用統一的 `get_logger()` 函式，不要直接 `print()`。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。

## 驗收標準
1. `PROMPTBIM_DEBUG=1 python -m promptbim gui` → console 顯示完整 debug log
2. `PROMPTBIM_DEBUG=0 python -m promptbim gui` → console 無 debug 輸出
3. `python -m promptbim gui --debug` → 同 PROMPTBIM_DEBUG=1
4. 所有現有 pytest 仍然通過（log 不影響功能）
5. 新增 debug system 相關測試
6. xcodebuild BUILD SUCCEEDED
7. iMessage 通知已發送
