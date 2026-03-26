# PROMPT_P16.md — Sprint P16: 全面品質修整 (Comprehensive Quality Remediation)

> 版本: v1.0 | 建立時間: 2026-03-26
> 前置 Sprint: P14 ✅ 完成（CI/CD + Security + Docs v2.0, 705 tests, git tag v2.0.0）
> 前置 Sprint: P15 ⬜ 待執行（V2 Architecture Migration — 可獨立，不阻擋 P16）
> 依賴: AuditReport.md, docs/reports/Full_Codebase_Quality_Report.md, CLAUDE.md v1.8.0
> 品質分析: P14 品質分析（Claude Opus 4.6 於 2026-03-26 執行）
> 目標版本: v2.1.0

---

## Sprint 目標

修復 AuditReport.md 中的 **3 個 Critical + 5 個 High + 6 個 Medium** 問題，
加上 P14 品質分析發現的 **3 個 Medium** 問題。
共 **14 個 Task**，目標達成品質評分 9.0/10+。

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。
確認 `git pull origin main` 為最新。

## 必讀文件

1. **SKILL.md** — 專案 SSOT（架構、Schema、Agent Prompt、開發規範）
2. **CLAUDE.md v1.8.0** — 行為規範（特別注意所有 [MANDATORY] 規則）
3. **AuditReport.md** — 代碼審核報告（本 Sprint 的主要問題來源）
4. **TODO.md** — 確認當前 Sprint 狀態
5. **pyproject.toml** — 依賴與版本
6. **docs/reports/Full_Codebase_Quality_Report.md** — 歷史品質報告（確認已修復項目不回退）

---

## Task 清單

### Part A: Critical 修復（AuditReport C-1 ~ C-3）

#### Task 1: API 呼叫重試機制 [C-1]
- **位置:** `agents/base.py`
- **問題:** 單次 API 失敗 = 整個管線失敗
- **修復:**
  - 在 `BaseAgent.run()` 加入指數退避重試（max 3 次, wait 1~10s）
  - 使用 `tenacity` 套件（加入 pyproject.toml dependencies）
  - 僅重試 `anthropic.APIStatusError`（5xx），不重試 4xx（認證/配額錯誤）
- **測試:** 新增 `tests/test_agents/test_base_retry.py`（mock API 失敗 → 重試成功 / 重試耗盡）

#### Task 2: API 呼叫 timeout [C-2]
- **位置:** `agents/base.py`
- **問題:** Anthropic API 呼叫無 timeout，可能無限掛起
- **修復:**
  - 在 `client.messages.create()` 加入 `timeout=30.0`
  - 在 `config.py` 加入 `api_timeout_seconds: int = 30` 設定
  - Timeout 觸發時走 fallback 路徑（與現有 API 失敗 fallback 一致）
- **測試:** 新增 timeout 觸發測試（mock httpx.TimeoutException）

#### Task 3: 統一 Shoelace 面積計算 [C-3]
- **位置:** 6 處重複（見 AuditReport 4.3）
- **問題:** `poly_area` / `_polygon_area` / `_shoelace_area` 在 7 個位置各自實作
- **修復:**
  - 確認 `bim/geometry.py:poly_area()` 為唯一正規實作
  - 將以下 6 處改為 `from promptbim.bim.geometry import poly_area`：
    - `codes/tw_building_code.py` → 刪除 `_polygon_area()`
    - `bim/cost/qto.py` → 刪除 `_polygon_area()` staticmethod
    - `land/boundary_confirm.py` → 刪除 `_shoelace_area()`
    - `land/parsers/image_ai.py` → 刪除 `_shoelace_area()`
    - `land/parsers/pdf_ocr.py` → 刪除 `_shoelace_area()`
    - `mcp/server.py` → 刪除 `_shoelace_area()`
  - 保留 backward-compat alias 供外部引用（如有）
- **測試:** 確認所有現有測試通過（面積計算結果不變）

### Part B: High 修復（AuditReport H-1 ~ H-5）

#### Task 4: buildable_area 輸入驗證 [H-1]
- **位置:** `agents/planner.py`
- **問題:** 空陣列或少於 3 頂點的多邊形不報錯
- **修復:**
  - 在 Planner 接收 buildable_area 前加入驗證：`len(coords) >= 3`
  - 面積 > 0 驗證
  - 無效輸入拋出 `ValueError` 並走 fallback
- **測試:** 新增邊界條件測試（空陣列、2 點、共線點、自交叉多邊形）

#### Task 5: ComponentRegistry 測試隔離 [H-2]
- **位置:** `bim/components/registry.py`
- **問題:** `_components` 為類別變數，測試間可能交叉污染
- **修復:**
  - 加入 `ComponentRegistry.reset()` class method
  - 在 `conftest.py` 加入 fixture `autouse=True` 呼叫 `reset()`
  - 或改為實例變數（需評估影響範圍）
- **測試:** 驗證兩個測試之間 registry 狀態不互相影響

#### Task 6: 修改歷史持久化 [H-3]
- **位置:** `agents/modifier.py`
- **問題:** ModificationHistory 僅存記憶體，程式退出即遺失
- **修復:**
  - 加入 `save_history(path)` / `load_history(path)` 方法
  - 使用 JSON 格式存於 output/ 目錄
  - Orchestrator 在每次 modify 後自動儲存
- **測試:** 新增持久化 round-trip 測試（save → load → verify undo）

#### Task 7: Planner JSON 回應 Schema 驗證 [H-4]
- **位置:** `agents/planner.py`
- **問題:** Claude 回傳 JSON 缺欄位靠預設值補，可能產生不完整計畫
- **修復:**
  - 在 Pydantic model_validate 前加入必要欄位存在性檢查
  - 缺少 `stories` / `footprint` / `total_height` 時走 fallback
  - 記錄 warning log 標記不完整回應
- **測試:** 新增殘缺 JSON 輸入測試（缺 stories、缺 footprint、空物件）

#### Task 8: 座標精度保護 [H-5]
- **位置:** `schemas/modification.py`
- **問題:** plan_snapshot 經 JSON 序列化後浮點精度降低
- **修復:**
  - 使用 `json.dumps(default=str)` 或 `orjson` 保持精度
  - 或改用 Pydantic `model_dump()` / `model_validate()` 取代原始 dict
  - 加入精度驗證（round-trip 後座標差 < 1e-10）
- **測試:** 新增 round-trip 精度測試

### Part C: Medium 修復（AuditReport M-1, M-3, M-5, M-6 + P14 分析 M1~M3）

#### Task 9: 魔術數字提取為常數 [AuditReport M-1]
- **位置:** 多處
- **修復:**
  - 建立 `constants.py`（或加入 config.py）：
    - `DEFAULT_STORY_HEIGHT_M = 3.0`
    - `DEFAULT_WALL_THICKNESS_M = 0.2`
    - `DEFAULT_SLAB_THICKNESS_M = 0.2`
    - `API_MAX_TOKENS_DEFAULT = 4096`
    - `API_MAX_TOKENS_PLANNER = 8192`
    - `GUI_STARTUP_DELAY_S = 1.0`
  - 所有引用處改為使用常數
- **測試:** grep 確認無殘留魔術數字

#### Task 10: IFC/USD 生成前備份 [AuditReport M-3]
- **位置:** `agents/builder.py`
- **問題:** 新檔案直接覆蓋舊檔
- **修復:**
  - 生成新 IFC/USD 前，如果目標路徑已存在，先 rename 為 `.bak`
  - 保留最近 1 份備份（不無限累積）
- **測試:** 新增覆寫場景測試

#### Task 11: Swift ContentView 版本號修復 [AuditReport M-5 + M-6]
- **位置:** `PromptBIMTestApp1/ContentView.swift`
- **問題:** 硬編碼 "v1.4.0"（應為 v2.1.0）+ 未使用的 `showSetupHelp` 變數
- **修復:**
  - 版本顯示改為從 `bridge.statusMessage` 擷取，或直接讀 `--version` 輸出
  - 刪除未使用的 `@State private var showSetupHelp`
- **測試:** xcodebuild BUILD SUCCEEDED + 無 warning

#### Task 12: CI/CD pip-audit 修復 [P14 分析 M1]
- **位置:** `.github/workflows/ci.yml`
- **問題:** `pip-audit ... || true` 讓 security job 永遠通過
- **修復:**
  - 移除 `|| true`
  - 將 `--ignore-vuln PYSEC-0` 改為空列表（或移除 ignore-vuln）
  - 如有已知 false positive，用正式 CVE ID 加入 ignore list
- **測試:** 在 Mac Mini 本地執行 `pip-audit -r requirements-frozen.txt` 確認無真正 CVE

#### Task 13: Context Prompt 精確化 [P14 分析 M2]
- **位置:** `docs/PromptBIM_Context_Prompt.md`
- **修復:**
  - 測試數改為 "698 passed, 7 deselected (slow/api markers)"
  - 更新版本為 v2.1.0
  - 加入 P16 完成狀態
  - 加入 coverage 85%+ 指標
- **測試:** 文件內容與實際數據一致

### Part D: 文件同步與驗收

#### Task 14: 全量文件同步 + AuditReport 更新
- 依照 CLAUDE.md v1.7.0 [MANDATORY] 規則，更新以下 8 項：
  1. `TODO.md` — P16 所有 task 標記 ✅，版本 v2.1.0
  2. `CHANGELOG.md` — 新增 [2.1.0] 條目 + 版本對照表
  3. `README.md` — 更新測試數、版本號
  4. `docs/PromptBIM_Context_Prompt.md` — 反映 P16 完成（Task 13 已處理）
  5. `pyproject.toml` — version = "2.1.0"
  6. `src/promptbim/__init__.py` — __version__ fallback = "2.1.0"
  7. `AuditReport.md` — 在問題清單中標記已修復項目
  8. `SKILL.md` — 如有架構變更（constants.py 新增）需更新
- Xcode pbxproj 完整性檢查（CLAUDE.md v1.8.0 規則）
- 建立 `PROMPT_P17.md`（通過合規性檢查）
- git tag v2.1.0

---

## 驗收標準

```
☐ xcodebuild BUILD SUCCEEDED（無 warning）
☐ pytest >= 720 passed（新增 ~20+ 測試）
☐ ruff check: All checks passed
☐ coverage >= 85%
☐ AuditReport C-1, C-2, C-3 全部修復
☐ AuditReport H-1 ~ H-5 全部修復
☐ AuditReport M-1, M-3, M-5, M-6 修復
☐ CI pip-audit 不再用 || true
☐ Shoelace 函數全專案只剩 1 份（bim/geometry.py）
☐ 全量文件同步完成（8 項）
☐ Xcode pbxproj 完整性檢查通過
☐ git tag v2.1.0 已建立並推送
☐ PROMPT_P17.md 已建立（通過合規性檢查）
☐ iMessage 通知已發送（啟動 + 完成）
```

---

## 新增依賴

| 套件 | 用途 | 加入位置 |
|------|------|----------|
| `tenacity>=8.0` | API 重試（指數退避）| pyproject.toml dependencies |

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保 Swift 檔案、Build Phase、Signing 設定正確。
⚠️ iMessage 通知必須發送（啟動 + 完成）。

---

## 問題來源追溯

| Task | 來源 | 原始 ID |
|------|------|----------|
| 1 | AuditReport.md | C-1 |
| 2 | AuditReport.md | C-2 |
| 3 | AuditReport.md | C-3 |
| 4 | AuditReport.md | H-1 |
| 5 | AuditReport.md | H-2 |
| 6 | AuditReport.md | H-3 |
| 7 | AuditReport.md | H-4 |
| 8 | AuditReport.md | H-5 |
| 9 | AuditReport.md | M-1 |
| 10 | AuditReport.md | M-3 |
| 11 | AuditReport.md | M-5 + M-6 |
| 12 | P14 品質分析 | M1 (pip-audit) |
| 13 | P14 品質分析 | M2 (Context Prompt) |
| 14 | CLAUDE.md v1.7.0/v1.8.0 | 全量文件同步 + pbxproj |

---

*PROMPT_P16.md v1.0 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.8.0 ✅ | SKILL.md ✅*
