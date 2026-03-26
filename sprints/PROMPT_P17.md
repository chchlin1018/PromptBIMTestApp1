# PROMPT_P17.md — Sprint P17: 全面修整 + 架構強化 + Async + 快取 (Complete Hardening Sprint)

> 版本: v2.0 | 建立時間: 2026-03-26
> 前置 Sprint: P16 ✅ 完成（品質修整, 725 tests, v2.1.0）
> 前置 Sprint: P15 ⬜ 未執行（併入本 Sprint）
> 依賴: AuditReport.md, CLAUDE.md v1.9.0, SKILL.md, docs/DesignDocForV2.md
> 目標版本: v2.4.0
> 本 Sprint 合併了原 P17 + P17.1 + P17.2 的所有工作

---

## Sprint 目標

**一次性收尾所有殘留工作**，共 **8 個 Part、34 個 Task**：
- Part A: CI/CD 緊急修復（3 Tasks）
- Part B: AuditReport 殘留修復（7 Tasks）
- Part C: V2 架構強化 — Lazy Import + Plugin（3 Tasks）
- Part D: 測試缺口填補（3 Tasks）
- Part E: Swift 修復 + 文件歸檔（3 Tasks）
- Part F: Async/Await Agent 層重構（6 Tasks）
- Part G: Plan 快取機制（6 Tasks）
- Part H: 最終文件同步 + 驗收（3 Tasks）

⚠️ **每完成一個 Part，必須發送 iMessage 通知（CLAUDE.md v1.9.0 規則）。**

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。
確認 `git pull origin main` 為最新。

## 必讀文件

1. **SKILL.md** — 專案 SSOT
2. **CLAUDE.md v1.9.0** — 行為規範（特別注意 Part 完成通知新規則）
3. **AuditReport.md** — 代碼審核報告
4. **TODO.md** — 確認當前 Sprint 狀態
5. **pyproject.toml** — 依賴與版本
6. **docs/DesignDocForV2.md** — V2 架構設計（Part C 依賴）
7. **src/promptbim/constants.py** — P16 新增的常數檔

---

## Part A: CI/CD 緊急修復（最高優先）

> ⚠️ 完成後發送 iMessage：「Sprint P17 — Part A 完成：CI/CD 修復」

#### Task 1: 修復 requirements-frozen.txt
- `pip freeze` 產出含 `@ file:///System/Volumes/...` 本地路徑，pip-audit 和 GitHub Actions 無法使用
- 用 `pip freeze | grep -v '@ file://' | grep -v '^#' > requirements-frozen.txt` 生成乾淨版本
- 或安裝 `pip-tools` 用 `pip-compile pyproject.toml -o requirements-frozen.txt --strip-extras`
- 驗證無任何 `@ file://` 路徑
- 測試：`pip-audit -r requirements-frozen.txt` 成功執行

#### Task 2: 移除假 CVE ID
- `.github/workflows/ci.yml` 中 `--ignore-vuln CVE-2026-4539` 是 Claude Code 編造的
- 執行 Task 1 後跑 `pip-audit`，結果乾淨則移除整個 `--ignore-vuln`，有真 CVE 則用真 ID
- 最終：`pip-audit -r requirements-frozen.txt`（無 ignore）

#### Task 3: 驗證 CI 可執行
- 確認 security job 在 `ubuntu-latest` 上可用修復後的 frozen 檔運行
- 如 conda 專有套件（ifcopenshell, usd-core）在 PyPI 不存在，security job 改為容錯模式

---

## Part B: AuditReport 殘留修復

> ⚠️ 完成後發送 iMessage：「Sprint P17 — Part B 完成：AuditReport 修復」

#### Task 4: 退縮計算改進 [M-2]
- `land/setback.py` 新增 `per_side_setback(polygon, setbacks: dict)` 逐邊退縮
- 現有 `uniform_setback()` 保留為 fallback，邊數 > 4 自動 fallback
- 測試：矩形 + L 形 + 三角形

#### Task 5: API Rate Limiter [架構風險]
- `agents/base.py` 或新建 `agents/rate_limiter.py`
- token bucket，預設每分鐘 50 次，`config.py` 加入 `api_rate_limit_rpm: int = 50`
- 測試：速率限制觸發測試（mock time）

#### Task 6: Schema 版本控制 [L-1]
- 主要 schema 加入 `schema_version: str = "2.4.0"`，載入時檢查相容性
- 測試：v1 → v2 資料遷移

#### Task 7: 輸入大小限制 [L-3]
- 所有土地解析器加入檔案大小檢查，`MAX_LAND_FILE_SIZE_MB = 50`（constants.py）
- 測試：大檔案拒絕

#### Task 8: lxml 安裝 [L-5]
- pyproject.toml 加入 `lxml>=5.0`，消除 fastkml pytest warning

#### Task 9: ComponentRegistry 效能 [L-2]
- 加入 `_by_category` 倒排索引，search() 改用索引查詢
- 測試：效能基準

#### Task 10: PythonBridge conda 路徑 [L-4]
- 加入 Intel Mac 路徑 + `which python3` fallback + `PROMPTBIM_PYTHON` 環境變數覆蓋

---

## Part C: V2 架構強化

> ⚠️ 完成後發送 iMessage：「Sprint P17 — Part C 完成：V2 架構」

#### Task 11: Lazy Import 優化
- Orchestrator 改為 lazy import，`--version` 路徑不觸發 agent/bim import
- 目標：`python -m promptbim --version` < 0.5s
- 測試：啟動速度基準

#### Task 12: Plugin 架構基礎
- 新建 `plugins/base.py`：PluginRegistry + @register_plugin
- 三種 plugin 類型：agent, parser, code_rule
- 土地解析器 + 法規引擎改用 plugin 註冊，保持向後相容
- 測試：plugin 註冊/發現/執行

#### Task 13: V2 架構文件拆解
- 讀取 DesignDocForV2.md，產出 `docs/V2_Migration_Tasks.md`
- 拆為可執行 task 列表（工時、依賴、優先級）
- 純文件工作

---

## Part D: 測試缺口填補

> ⚠️ 完成後發送 iMessage：「Sprint P17 — Part D 完成：測試補強」

#### Task 14: 網路故障模擬
- 新建 `tests/test_agents/test_network_failure.py`
- Mock timeout / connect error / 503 retry / 429 不重試
- ~8 個測試

#### Task 15: 惡意輸入測試
- 新建 `tests/test_land/test_fuzzing.py`
- 超大 GeoJSON / 畸形 JSON / 自交叉 / 極端座標 / 空檔案 / 二進位
- ~10 個測試

#### Task 16: 檔案權限錯誤
- 新建 `tests/test_integration/test_permissions.py`
- Mock PermissionError / IsADirectoryError
- ~5 個測試

---

## Part E: Swift 修復 + 文件歸檔

> ⚠️ 完成後發送 iMessage：「Sprint P17 — Part E 完成：Swift + 文件」

#### Task 17: ContentView 版本號動態化
- PythonBridge 新增 `@Published var version: String`
- `checkPython()` 成功後解析 `--version` 輸出存入 version
- ContentView 改為 `Text("v\(bridge.version)")` 動態顯示

#### Task 18: AuditReport 更新
- 標記 P16 + P17 已修復項目，更新關鍵數據表格和評級

#### Task 19: P14/P16 品質分析報告歸檔
- 新建 `docs/reports/P14_Quality_Analysis_Report.md` + `P16_Quality_Analysis_Report.md`

---

## Part F: Async/Await Agent 層重構 [原 P17.1]

> ⚠️ 完成後發送 iMessage：「Sprint P17 — Part F 完成：Async/Await」

#### Task 20: BaseAgent async 化
- 新增 `async def arun()` + `anthropic.AsyncAnthropic` client（lazy init）
- 保留現有 `run()` 同步方法（向後相容）
- tenacity retry + timeout 同樣套用
- 測試：mock async API

#### Task 21: 各 Agent async 支援
- enhancer/planner/checker/modifier 新增 `async def arun()` 覆寫
- BuilderAgent 保持同步（純 Python，不呼叫 API）
- 測試：async 版本測試

#### Task 22: Orchestrator async pipeline
- 新增 `async def agenerate()` / `async def amodify()`
- Pipeline: `await enhancer.arun()` → `await planner.arun()` → `builder.run()` → `await checker.arun()`
- 保留同步 `generate()` / `modify()`（向後相容）
- 測試：async orchestrator 全流程

#### Task 23: ChatPanel + CLI async 整合
- GUI: QThread worker 改用 `asyncio.run(orchestrator.agenerate())`
- CLI: `generate` 命令改用 `asyncio.run()`
- 如需要加入 `qasync` 到 dependencies
- 測試：GUI + CLI 測試通過

#### Task 24: MCP Server async
- FastMCP tools 改用 `await orchestrator.agenerate()`
- Streamlit Web 保持同步（原生不支援 async）

#### Task 25: 並行 Agent 執行（進階）
- 生成完成後，並行執行成本估算 + MEP 規劃 + 監控點配置
- `asyncio.gather(cost_task, mep_task, monitor_task)`
- 只並行無相依賴的 Agent
- 測試：並行結果與順序執行一致

---

## Part G: Plan 快取機制 [原 P17.2]

> ⚠️ 完成後發送 iMessage：「Sprint P17 — Part G 完成：Plan 快取」

#### Task 26: 快取 Key + Store
- 新建 `cache/cache_key.py`：SHA-256(normalized_prompt + land_json + zoning_json)
- 新建 `cache/store.py`：本地 `~/.promptbim/cache/` JSON 存儲
- 介面：get / put / invalidate / clear_all / list_entries
- `CACHE_MAX_ENTRIES = 100`（constants.py），LRU 淘汰
- 測試：put/get round-trip, LRU, invalidate

#### Task 27: 快取過期策略
- TTL 預設 7 天（`CACHE_TTL_DAYS = 7`）
- `config.py` 加入 `cache_ttl_days: int = 7` + `cache_enabled: bool = True`
- 版本不匹配自動失效（快取記錄 app_version）
- 測試：TTL 過期 + 版本不匹配

#### Task 28: Orchestrator 快取整合
- `generate()` / `agenerate()` 開頭查詢快取
- 命中直接回傳，未命中走 Pipeline 後存入
- `use_cache: bool = True` 參數
- Status callback 顯示 Cache hit / Generating
- 測試：hit / miss / force regenerate

#### Task 29: CLI 快取支援
- `generate --no-cache` + `generate --clear-cache`
- 新增 `cache` 子命令：`list` / `clear` / `stats`
- 測試：CLI cache 命令

#### Task 30: GUI 快取指示
- Cache hit 時 ChatPanel 顯示「⚙️ 從快取載入（原生成於 {date}）」
- 「重新生成」按鈕（use_cache=False）

#### Task 31: Streamlit + MCP 快取整合
- Web UI + MCP Server 也走快取路徑
- 測試：快取在所有介面一致運作

---

## Part H: 最終文件同步 + 驗收

> ⚠️ 完成後發送 iMessage：「Sprint P17 — 全部完成（8/8 Parts）」

#### Task 32: 全量文件同步
- 依照 CLAUDE.md v1.9.0 [MANDATORY] 更新 8 項文件
- pyproject.toml version = "2.4.0"
- Info.plist: CFBundleVersion = 17, CFBundleShortVersionString = 2.4.0
- AuditReport.md：所有修復項目已標記
- SKILL.md：更新架構變更（plugins/, cache/, async）
- Xcode pbxproj 完整性檢查

#### Task 33: 建立 PROMPT_P18.md
- 通過 CLAUDE.md v1.9.0 合規性檢查
- 建議方向：V2 Migration Phase 0-1

#### Task 34: git tag v2.4.0

---

## 新增依賴

| 套件 | 用途 | 位置 |
|------|------|------|
| `lxml>=5.0` | fastkml XML（消除 warning）| dependencies |
| `pip-tools>=7.0` | 乾淨 frozen requirements | [dev] |
| `qasync>=0.27` | Qt + asyncio 整合（如採用）| dependencies |

---

## 驗收標準

```
☐ xcodebuild BUILD SUCCEEDED（無 warning）
☐ pytest >= 830 passed（新增 ~105 測試）
☐ ruff check: All checks passed
☐ coverage >= 85%
☐ pip-audit 成功執行且無假 CVE
☐ requirements-frozen.txt 不含 @ file://
☐ python -m promptbim --version < 0.5s
☐ BaseAgent.arun() + Orchestrator.agenerate() 可運作
☐ 同步 API 仍可用（向後相容）
☐ 快取 hit/miss/force-regenerate 正常
☐ cache list/clear/stats CLI 命令可用
☐ Plugin 架構建立
☐ ContentView 版本號動態顯示
☐ 所有 8 個 Part 各自發送了 iMessage
☐ 全量文件同步完成
☐ git tag v2.4.0
☐ PROMPT_P18.md 已建立
```

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保 Swift 檔案、Build Phase、Signing 設定正確。
⚠️ iMessage 通知必須發送（啟動 + **每個 Part 完成** + 最終完成）。
⚠️ Task 1-3（CI 修復）必須最先執行。
⚠️ requirements-frozen.txt 不得含有 `@ file://` 本地路徑。
⚠️ Async 改造必須保持向後相容：現有同步 API 不得刪除或破壞。
⚠️ 快取層必須同時支援同步和 async 版本的 Orchestrator。

---

*PROMPT_P17.md v2.0 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.9.0 ✅ | SKILL.md ✅ | 合併自 P17+P17.1+P17.2*
