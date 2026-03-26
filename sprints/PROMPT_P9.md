# PROMPT_P9.md — Sprint P9: AI 土地圖像辨識 + Backlog 優先項目

> 版本: v1.0.0 | 建立時間: 2026-03-25
> 前置 Sprint: P0~P8.5 ✅ 全部完成 (v1.0.0)
> 依賴: P1 (土地匯入系統), P4 (AI Agent Pipeline)

## Sprint 目標

擴展土地匯入系統，支援**任意圖檔輸入**（照片、截圖、掌描檔、手繪圖），由 Claude Vision AI 自動辨識土地邊界，轉換為座標數據，供使用者確認後進入 BIM 生成流程。同時實現高優先級 Backlog 項目。

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在且所有依賴可 import。

## 必讀文件
1. SKILL.md
2. TODO.md
3. CLAUDE.md（含 Rule 8 iMessage 通知）
4. docs/reviews/REVIEW_P2.md（如有未修項目一併修復）
5. `land/parsers/` — 現有的土地匯入模組

---

## Part A: AI 土地圖像辨識（核心新功能）

### 功能描述

使用者可以輸入**任意格式的圖檔**作為土地平面圖：
- 📷 手機拍的土地照片
- 🗺️ Google Maps / 衛星圖 截圖
- 📄 掌描的地籍圖 PDF/JPG
- ✏️ 手繪的土地草圖
- 📐 CAD 輸出的圖片（非 DXF）
- 🏢 建商提供的基地圖 JPG/PNG

系統流程：
```
使用者拖放圖檔 → Claude Vision 分析 → 偵測土地邊界 → 生成座標
→ GUI 預覽（疊合原圖 + 辨識邊界）→ 使用者確認/調整 → 進入 BIM 流程
```

### Task 清單

- ⬜ `land/parsers/image_ai.py` — AI 圖像辨識土地邊界
  - 支援格式：JPG, PNG, TIFF, BMP, WebP, HEIC, PDF（首頁轉圖）
  - 呼叫 Claude Vision API（Anthropic messages API with image content）
  - Prompt 設計：辨識土地邊界多邊形、比例尺、方位、面積
  - 輸出：LandParcel Pydantic model（含 confidence score）
  - 多策略辨識：
    1. 邊界線偵測（實線/虛線/顏色區分）
    2. 文字標註讀取（尺寸、面積、地號）
    3. 比例尺估算（如有標註）
    4. 方位偵測（指北針）

- ⬜ `land/parsers/image_preprocess.py` — 圖像預處理
  - PIL/Pillow 圖像標準化（resize, contrast, rotation）
  - HEIC → JPG 轉換
  - PDF 首頁轉 PNG
  - Base64 編碼（供 Claude Vision API）

- ⬜ `land/boundary_confirm.py` — 邊界確認邏輯
  - AI 辨識結果 → 候選邊界（可能多個方案）
  - confidence score 排序
  - 邊界座標微調

- ⬜ `gui/dialogs/confirm_boundary.py` — 邊界確認 GUI
  - 原圖 + AI 辨識邊界 疊合顯示
  - 拖曳頂點微調（matplotlib interactive）
  - 確認/重新辨識/手動輸入 按鈕
  - 顯示辨識 confidence、面積、周長
  - 支援多候選方案切換

- ⬜ `gui/dialogs/import_land.py` — 更新匯入對話框
  - 新增「圖片匯入」Tab
  - 支援拖放任意圖檔
  - 匯入後自動觸發 AI 辨識 → 確認流程

- ⬜ `agents/land_reader.py` — Land Reader Agent（新 Agent）
  - 繼承 BaseAgent
  - System Prompt 用於土地圖像分析
  - 輸出結構化 JSON
  - 支援多輪對話修正

- ⬜ `schemas/land.py` — 擴充 LandParcel schema
  - source_type 新增 `"ai_image"`
  - ai_confidence: float (0.0~1.0)
  - original_image_path: Optional[str]
  - ai_annotations: Optional[dict]

- ⬜ 測試圖片 fixtures
  - 使用 `Pic_MyLand/` 目錄中的 4 張土地圖片 (IMG_1451.JPG, IMG_1452.JPG, IMG_2319.JPG, IMG_2352.JPG)
  - 複製到 `tests/fixtures/land_images/`
  - 單元測試：image_preprocess（格式轉換、resize）
  - 單元測試：boundary_confirm（座標微調）
  - 整合測試：mock Claude Vision API → 完整流程
  - xcodebuild BUILD SUCCEEDED

### Claude Vision API 呼叫範例

```python
import anthropic
import base64

client = anthropic.Anthropic()

with open("land_photo.jpg", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_data,
                },
            },
            {
                "type": "text",
                "text": """分析這張土地平面圖，辨識土地邊界。

請回傳 JSON 格式：
{
  "boundary": [[x1,y1], [x2,y2], ...],
  "area_sqm": 面積估算,
  "scale": "1:500" or null,
  "orientation": "north_up" or angle,
  "annotations": {
    "lot_number": "地號",
    "dimensions": ["12.5m", "8.3m", ...],
    "zoning": "住宅區" or null
  },
  "confidence": 0.85,
  "notes": "辨識備註"
}"""
            }
        ],
    }],
)
```

### 驗收標準 (Part A)
1. 拖放 Google Maps 截圖 → AI 辨識土地邊界 → 預覽顯示
2. 拖放手繪草圖 → AI 辨識大致形狀 → 使用者可微調
3. 使用 Pic_MyLand 中的 4 張圖片測試辨識成功率
4. 確認後可直接進入 BIM 生成流程
5. 不清楚的圖片顯示低 confidence 警告

---

## Part B: Backlog 優先項目

### B1: USDZ 打包（Apple Vision Pro / Quick Look）

- ⬜ `bim/usdz_packer.py` — USD → USDZ（UsdUtils.CreateNewUsdzPackage）
- ⬜ `gui/export_usdz.py` — 匯出 USDZ + Quick Look 預覽
- ⬜ 測試：macOS Quick Look + iOS AR Quick Look

### B2: MCP Server（Claude Desktop 整合）

- ⬜ `mcp/server.py` — MCP Server
  - Tool: generate_building / check_compliance / estimate_cost / modify_building
  - Resource: building://current
- ⬜ `mcp/config.json` — Claude Desktop 設定
- ⬜ 測試

### B3: Web UI（Streamlit）

- ⬜ `web/app.py` — Streamlit 完整功能
- ⬜ 測試：streamlit run

---

## 執行指令
所有問題答案都是 Yes，不要中斷詢問。
**優先順序：Part A → B1 → B2 → B3**
注意：Pic_MyLand/ 目錄中有 4 張真實土地圖片，複製到 tests/fixtures/ 作為測試用。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。

## 驗收標準
1. Part A 必須全部完成
2. Part B 盡量完成
3. xcodebuild BUILD SUCCEEDED
4. pytest 全部通過
5. iMessage 通知已發送
