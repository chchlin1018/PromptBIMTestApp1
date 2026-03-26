# PROMPT_P17.1.md — Sprint P17.1: Async/Await Agent 層重構 (Asynchronous Agent Pipeline)

> 版本: v1.0 | 建立時間: 2026-03-26
> 前置 Sprint: P17 ✅ 完成（全面修整 + 架構強化 + CI 修復）
> 依賴: CLAUDE.md v1.8.0, SKILL.md, AuditReport.md (M-4)
> 品質分析: AuditReport M-4 「同步阻塞式 API 呼叫，GUI 可能凍結」
> 目標版本: v2.3.0
> ⬇️ 接續: PROMPT_P17.2.md（Plan 快取機制）

---

## Sprint 目標

將 Agent 層從同步阻塞改為 async/await，解決 **AuditReport M-4** 「同步阻塞式 API 呼叫可能導致 GUI 凍結」問題。
這是一個架構級重構，影響範圍：BaseAgent → 5 個 Agent → Orchestrator → GUI ChatPanel → CLI。

共 **10 個 Task**。

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。
確認 `git pull origin main` 為最新。

## 必讀文件

1. **SKILL.md** — 專案 SSOT
2. **CLAUDE.md v1.8.0** — 行為規範（所有 [MANDATORY] 規則）
3. **AuditReport.md** — M-4 說明 + 架構風雛「同步阻塞式 API 呼叫」
4. **TODO.md** — 確認當前 Sprint 狀態
5. **src/promptbim/agents/base.py** — 現有 BaseAgent 實作（P16 加入的 tenacity retry + timeout）
6. **src/promptbim/agents/orchestrator.py** — 現有 Pipeline 編排
7. **src/promptbim/gui/chat_panel.py** — 現有 QThread 背景執行

---

## Task 清單

### Part A: Agent 層 Async 改造

#### Task 1: BaseAgent async 化
- **位置:** `agents/base.py`
- **修復:**
  - 新增 `async def arun(self, user_message: str) -> AgentResponse` 非同步方法
  - 使用 `anthropic.AsyncAnthropic` client（lazy init 獨立於同步 client）
  - 保留現有 `run()` 同步方法（向後相容）
  - tenacity retry + timeout 同樣套用於 async 版本
  - 加入 `_async_client` 屬性 + `async_client` property
- **測試:** 新增 `test_base_async.py`（mock async API 呼叫）

#### Task 2: 各 Agent 加入 async 支援
- **位置:** `agents/enhancer.py`, `agents/planner.py`, `agents/checker.py`, `agents/modifier.py`
- **修復:**
  - 每個 Agent 新增 `async def arun()` 覆寫（如有自定義邏輯）
  - `BuilderAgent` 保持同步（純 Python 計算，不呼叫 API）
  - 確保每個 Agent 的 fallback 邏輯在 async 版本中也能運作
- **測試:** 現有 Agent 測試通過 + 新增 async 版本測試

#### Task 3: Orchestrator async pipeline
- **位置:** `agents/orchestrator.py`
- **修復:**
  - 新增 `async def agenerate()` 非同步生成方法
  - 新增 `async def amodify()` 非同步修改方法
  - Pipeline: `await enhancer.arun()` → `await planner.arun()` → `builder.run()`（同步）→ `await checker.arun()`
  - 保留現有 `generate()` / `modify()` 同步方法（向後相容）
  - Status callback 保持相同介面
- **測試:** 新增 async orchestrator 測試（mock 全流程）

### Part B: GUI + CLI 整合

#### Task 4: ChatPanel async 整合
- **位置:** `gui/chat_panel.py`
- **修復:**
  - 將 QThread worker 改為使用 `asyncio.run()` 呼叫 `orchestrator.agenerate()`
  - 或使用 `qasync` 套件整合 Qt event loop 與 asyncio
  - 確保背景執行不阻塞主執行緒
  - Status callback 透過 signal/slot 安全更新 GUI
- **測試:** GUI 測試（pytest-qt）確認不凍結

#### Task 5: CLI async 整合
- **位置:** `__main__.py`
- **修復:**
  - `generate` 命令改用 `asyncio.run(orchestrator.agenerate(...))`
  - 確保 CLI 輸出與現有行為一致
  - `--version` 和 `check` 命令不受影響（不需要 async）
- **測試:** CLI 測試通過

### Part C: 其他整合 + 品質

#### Task 6: MCP Server async
- **位置:** `mcp/server.py`
- **修復:**
  - FastMCP tools 改用 `await orchestrator.agenerate()` / `amodify()`
  - 確保 MCP server 的 7 個 tool 都能 async 運作
- **測試:** MCP 測試通過

#### Task 7: Streamlit Web 保持同步 [說明]
- **位置:** `web/app.py`
- **說明:** Streamlit 原生不支援 async，繼續使用同步 `orchestrator.generate()`
- **修復:** 無需修改，確認同步 API 仍可用
- **測試:** Web 測試通過

#### Task 8: 並行 Agent 執行（進階）
- **位置:** `agents/orchestrator.py`
- **修復:**
  - 在生成完成後，並行執行獨立的後處理：
    ```python
    # 並行執行成本估算 + MEP 規劃 + 監控點配置
    cost_task = asyncio.create_task(cost_estimator.estimate(plan))
    mep_task = asyncio.create_task(mep_planner.plan(plan))
    monitor_task = asyncio.create_task(monitor_placer.place(plan))
    cost, mep, monitors = await asyncio.gather(cost_task, mep_task, monitor_task)
    ```
  - 只並行無相依賴的 Agent，主 Pipeline 保持順序
- **測試:** 並行執行結果與順序執行一致

### Part D: 文件同步

#### Task 9: 全量文件同步
- 依照 CLAUDE.md v1.7.0/v1.8.0 [MANDATORY] 規則，更新 8 項文件
- pyproject.toml version = "2.3.0"
- Info.plist: CFBundleVersion = 18, CFBundleShortVersionString = 2.3.0
- 如需要新增 `qasync` 套件，加入 pyproject.toml dependencies
- AuditReport.md 更新 M-4 為已修復
- Xcode pbxproj 完整性檢查
- git tag v2.3.0

#### Task 10: 建立 PROMPT_P17.2.md
- 建立下一個 Sprint Prompt（通過 CLAUDE.md v1.8.0 合規性檢查）
- 內容為 Plan 快取機制

---

## 新增依賴

| 套件 | 用途 | 加入位置 |
|------|------|----------|
| `qasync>=0.27` | Qt + asyncio event loop 整合（如採用） | pyproject.toml dependencies |

---

## 驗收標準

```
☐ xcodebuild BUILD SUCCEEDED
☐ pytest >= 790 passed（新增 ~30 async 測試）
☐ ruff check: All checks passed
☐ coverage >= 85%
☐ BaseAgent.arun() + Orchestrator.agenerate() 可運作
☐ 現有同步 API（run/generate/modify）仍可用（向後相容）
☐ GUI ChatPanel 不凍結（async 背景執行）
☐ CLI generate 命令使用 async
☐ MCP Server 使用 async
☐ AuditReport M-4 標記為已修復
☐ 全量文件同步完成
☐ git tag v2.3.0
☐ iMessage 通知已發送（啟動 + 完成）
```

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保 Swift 檔案、Build Phase、Signing 設定正確。
⚠️ iMessage 通知必須發送（啟動 + 完成）。
⚠️ 必須保持向後相容：現有同步 API 不得刪除或破壞。

---

## 🔗 接續 Sprint 提醒

> **P17.1 完成後，請立即執行 P17.2（Plan 快取機制）。**
>
> **P17.1 完成後的 tmux 指令：**
> ```bash
> # 在 Mac Mini 上（已在 tmux session 內）
> cd ~/Documents/MyProjects/PromptBIMTestApp1
> git pull origin main
> conda activate promptbim
> claude --dangerously-skip-permissions -p "請讀取 PROMPT_P17.2.md 並執行所有 task。不要問任何問題。"
> ```

---

*PROMPT_P17.1.md v1.0 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.8.0 ✅ | SKILL.md ✅*
