# PROMPT_P10.3.md — Sprint P10.3: App 啟動環境檢查 + Claude AI 連線驗證

> 版本: v1.0.0 | 建立時間: 2026-03-25
> 前置 Sprint: P0~P9 ✅, P10.2 (Debug Logging)
> 依賴: P0 (骨架), P4 (AI Agent), P10.2 (Debug Logger)

## Sprint 目標

App 啟動時自動執行完整的環境健康檢查，包括 Python 依賴、Claude AI API 連線驗證、檔案系統、Xcode 狀態等。檢查結果以 GUI 面板呈現，異常項目清楚標示，確保使用者在開始工作前知道系統狀態。

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。

## 必讀文件
1. SKILL.md
2. TODO.md
3. CLAUDE.md
4. `src/promptbim/debug.py` — P10.2 建立的 Debug Logger（使用它記錄檢查過程）
5. `src/promptbim/config.py` — 現有設定系統

---

## 架構設計

### 檢查項目清單（共 12 項）

```
┌─────────────────────────────────────────────────────┐
│  🏗️ PromptBIM — System Check                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Python 環境                                        │
│  ✅ Python 3.11.x                                   │
│  ✅ conda env: promptbim                            │
│                                                     │
│  核心依賴                                           │
│  ✅ ifcopenshell 0.8.x                              │
│  ✅ pxr (OpenUSD)                                   │
│  ✅ PySide6                                         │
│  ✅ anthropic SDK                                   │
│  ✅ shapely + pyproj                                │
│  ✅ pyvista + pyvistaqt                             │
│                                                     │
│  AI 服務                                            │
│  ✅ ANTHROPIC_API_KEY 已設定                         │
│  ✅ Claude API 連線正常 (ping test, 0.8s)           │
│  ✅ Model: claude-sonnet-4-20250514 可用             │
│                                                     │
│  檔案系統                                           │
│  ✅ .env 存在                                       │
│  ✅ output/ 目錄可寫入                              │
│                                                     │
│  ── 12/12 通過 ──                                   │
│                                                     │
│  [開始使用]  [重新檢查]  [查看詳細 Log]              │
└─────────────────────────────────────────────────────┘
```

### 失敗時的顯示

```
│  AI 服務                                            │
│  ✅ ANTHROPIC_API_KEY 已設定                         │
│  ❌ Claude API 連線失敗                              │
│     → 錯誤: AuthenticationError — Invalid API key   │
│     → 解法: 請檢查 .env 中的 ANTHROPIC_API_KEY      │
│  ⚠️ Model 檢查跳過（API 不可用）                     │
```

---

## Task 清單

### Task 1: 環境檢查引擎

- ⬜ `src/promptbim/startup/health_check.py` — 健康檢查引擎
  ```python
  @dataclass
  class CheckResult:
      name: str              # 檢查項目名稱
      category: str          # Python環境 / 核心依賴 / AI服務 / 檔案系統
      status: Literal["pass", "fail", "warn", "skip"]
      message: str           # 簡短結果訊息
      detail: str | None     # 詳細資訊（錯誤堆疊等）
      fix_hint: str | None   # 修復建議
      elapsed_ms: float      # 檢查耗時

  class HealthChecker:
      def run_all() -> list[CheckResult]
      def run_category(category: str) -> list[CheckResult]
  ```

- ⬜ 檢查項目實作：

  **Python 環境（2 項）**
  1. Python 版本 ≥ 3.11
  2. conda env `promptbim` 是否啟用

  **核心依賴（6 項）**
  3. `import ifcopenshell` + 版本
  4. `from pxr import Usd` + 確認可建立 Stage
  5. `from PySide6.QtWidgets import QApplication`
  6. `import anthropic` + 版本
  7. `import shapely; import pyproj`
  8. `import pyvista; import pyvistaqt`

  **AI 服務（3 項）**
  9. `ANTHROPIC_API_KEY` 環境變數或 .env 已設定（非空、格式正確 `sk-ant-*`）
  10. Claude API Ping Test — 發送最小請求驗證連線
      ```python
      client = anthropic.Anthropic()
      response = client.messages.create(
          model="claude-sonnet-4-20250514",
          max_tokens=10,
          messages=[{"role": "user", "content": "ping"}]
      )
      # 成功 → pass, 記錄回應時間
      # AuthenticationError → fail, hint: 檢查 API Key
      # RateLimitError → warn, hint: API 限流中
      # ConnectionError → fail, hint: 檢查網路連線
      ```
  11. Model 可用性 — 確認 claude-sonnet-4-20250514 在回應中

  **檔案系統（1 項）**
  12. `.env` 存在 + `output/` 目錄可寫入

### Task 2: Claude AI 專用驗證模組

- ⬜ `src/promptbim/startup/ai_check.py` — Claude AI 連線驗證
  - `check_api_key()` — 驗證 key 格式和存在
  - `ping_claude()` — 最小 API 呼叫測試（max_tokens=10）
  - `check_model_available(model_name)` — 模型可用性
  - `check_vision_available()` — Vision API 可用（P9 用）
  - 所有檢查都有 timeout（預設 10 秒）
  - 記錄回應時間、token usage、error detail
  - 使用 P10.2 的 debug logger 記錄完整過程

### Task 3: GUI 啟動檢查面板

- ⬜ `src/promptbim/gui/startup_check_view.py` — 啟動檢查 GUI
  - 啟動時自動顯示（可在設定中關閉）
  - 每個檢查項目即時更新狀態（✅/❌/⚠️/⏳）
  - 分類顯示（Python 環境 / 核心依賴 / AI 服務 / 檔案系統）
  - 失敗項目展開顯示錯誤詳情 + 修復建議
  - 底部按鈕：「開始使用」（全部通過時啟用）/ 「重新檢查」/ 「查看 Log」/ 「略過」
  - 檢查進度條
  - 總結行：X/12 通過，Y 警告，Z 失敗

- ⬜ `src/promptbim/gui/main_window.py` — 整合啟動檢查
  - App 啟動時先顯示 StartupCheckView
  - 全部通過 → 自動進入主介面（或按「開始使用」）
  - 有失敗 → 停留在檢查面板，使用者可選擇「略過」繼續
  - 設定選項：「啟動時檢查」開/關

### Task 4: CLI 環境檢查

- ⬜ `src/promptbim/__main__.py` — 新增 `check` 子命令
  ```bash
  python -m promptbim check          # 執行全部檢查，console 輸出
  python -m promptbim check --json   # JSON 格式輸出（供自動化）
  python -m promptbim check --ai     # 只檢查 AI 相關項目
  python -m promptbim check --fix    # 嘗試自動修復（安裝缺失套件）
  ```

### Task 5: 自動修復建議

- ⬜ `src/promptbim/startup/auto_fix.py` — 自動修復引擎
  - 每個失敗項目提供具體修復指令
  - 修復建議對照表：

  | 檢查失敗 | 修復建議 |
  |---------|--------|
  | Python 版本不對 | `conda install python=3.11` |
  | ifcopenshell 缺失 | `conda install -c conda-forge ifcopenshell` |
  | pxr 缺失 | `pip install usd-core` |
  | PySide6 缺失 | `pip install PySide6` |
  | anthropic 缺失 | `pip install anthropic` |
  | API Key 未設定 | `cp .env.example .env && nano .env` |
  | API Key 無效 | `請到 console.anthropic.com 重新產生` |
  | API 連線失敗 | `檢查網路連線或 proxy 設定` |
  | output/ 不可寫 | `mkdir -p output && chmod 755 output` |

  - `--fix` 模式：自動執行 pip/conda 安裝（需確認）

### Task 6: Config 擴充

- ⬜ `src/promptbim/config.py` — 新增設定
  ```python
  class Settings(BaseSettings):
      # 既有設定...
      
      # 新增：啟動檢查
      startup_check_enabled: bool = True      # 啟動時是否檢查
      startup_check_skip_ai: bool = False     # 跳過 AI 檢查（離線模式）
      ai_ping_timeout_seconds: float = 10.0   # AI ping 超時
      ai_model: str = "claude-sonnet-4-20250514"  # 預設模型
  ```

### Task 7: 測試

- ⬜ 測試 HealthChecker 各項檢查（mock 依賴）
- ⬜ 測試 AI check：mock API 成功/失敗/超時
- ⬜ 測試 CLI `check` 子命令
- ⬜ 測試 auto_fix 建議生成
- ⬜ 測試 startup_check_enabled=False 時跳過檢查
- ⬜ 確認所有現有 pytest 仍通過
- ⬜ xcodebuild BUILD SUCCEEDED

---

## Debug Log 輸出範例

```
18:00:01 [promptbim.startup] DEBUG: === System Health Check Starting ===
18:00:01 [promptbim.startup] DEBUG: [1/12] Python version: 3.11.11 ✅ (1ms)
18:00:01 [promptbim.startup] DEBUG: [2/12] Conda env: promptbim ✅ (2ms)
18:00:01 [promptbim.startup] DEBUG: [3/12] ifcopenshell: 0.8.0 ✅ (45ms)
18:00:01 [promptbim.startup] DEBUG: [4/12] pxr (OpenUSD): OK ✅ (120ms)
18:00:01 [promptbim.startup] DEBUG: [5/12] PySide6: 6.7.x ✅ (30ms)
18:00:01 [promptbim.startup] DEBUG: [6/12] anthropic: 0.40.x ✅ (5ms)
18:00:01 [promptbim.startup] DEBUG: [7/12] shapely+pyproj: OK ✅ (15ms)
18:00:01 [promptbim.startup] DEBUG: [8/12] pyvista+pyvistaqt: OK ✅ (80ms)
18:00:01 [promptbim.startup] DEBUG: [9/12] API Key: sk-ant-***...*** (set) ✅ (1ms)
18:00:02 [promptbim.startup] DEBUG: [10/12] Claude API ping: 200 OK, 823ms ✅
18:00:02 [promptbim.startup] DEBUG: [11/12] Model claude-sonnet-4-20250514: available ✅ (0ms)
18:00:02 [promptbim.startup] DEBUG: [12/12] Filesystem: .env ✅, output/ writable ✅ (3ms)
18:00:02 [promptbim.startup] DEBUG: === Health Check Complete: 12/12 PASS (1.1s) ===
```

---

## 執行指令
所有問題答案都是 Yes，不要中斷詢問。
**必須使用 P10.2 建立的 debug.py logger，不要用 print()。**
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。

## 驗收標準
1. `python -m promptbim check` → console 顯示 12 項檢查結果
2. `python -m promptbim check --json` → 輸出結構化 JSON
3. `python -m promptbim check --ai` → 只顯示 AI 相關 3 項
4. App GUI 啟動時顯示檢查面板，全通過後進入主介面
5. API Key 錯誤時顯示明確的錯誤訊息和修復建議
6. `startup_check_enabled=False` 時跳過檢查直接進入主介面
7. 所有現有 pytest 仍通過 + 新增測試
8. xcodebuild BUILD SUCCEEDED
9. iMessage 通知已發送
