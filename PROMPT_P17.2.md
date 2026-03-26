# PROMPT_P17.2.md — Sprint P17.2: Plan 快取機制 (Generation Cache Layer)

> 版本: v1.0 | 建立時間: 2026-03-26
> 前置 Sprint: P17.1 ✅ 完成（async/await Agent 層重構）
> 依賴: CLAUDE.md v1.8.0, SKILL.md, AuditReport.md 架構建議
> 品質分析: AuditReport 「無快取機制，相同 prompt+土地重複生成不利用快取」
> 目標版本: v2.4.0

---

## Sprint 目標

建立生成結果快取層，解決 AuditReport 架構建議「無快取機制」。
相同 prompt + 土地 + zoning 條件下，第二次生成應直接回傳快取結果，不重新呼叫 Claude API。

共 **8 個 Task**。

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。
確認 `git pull origin main` 為最新。

## 必讀文件

1. **SKILL.md** — 專案 SSOT
2. **CLAUDE.md v1.8.0** — 行為規範（所有 [MANDATORY] 規則）
3. **AuditReport.md** — 架構建議「無快取機制」
4. **TODO.md** — 確認當前 Sprint 狀態
5. **src/promptbim/agents/orchestrator.py** — 現有 Pipeline（P17.1 已加入 async）
6. **src/promptbim/schemas/result.py** — GenerationResult schema

---

## Task 清單

### Part A: 快取層建立

#### Task 1: 快取 Key 設計
- **位置:** 新建 `cache/cache_key.py`
- **修復:**
  - 快取 key = hash(prompt + land_parcel_json + zoning_rules_json)
  - 使用 SHA-256 雜湊
  - prompt 先 normalize（去除前後空白、統一小寫）
  - land_parcel 用 `model_dump_json(sort_keys=True)` 確保一致性
  - 函數：`compute_cache_key(prompt, land_parcel, zoning_rules) -> str`
- **測試:** 相同輸入產生相同 key，不同輸入產生不同 key

#### Task 2: 快取存儲引擎
- **位置:** 新建 `cache/store.py`
- **修復:**
  - 快取存儲於本地檔案系統：`~/.promptbim/cache/`
  - 每個快取項目 = 1 個 JSON 檔案（key 為檔名）
  - 內容：GenerationResult 序列化 + 元資料（建立時間、prompt 摘要、土地摘要）
  - 介面：
    - `get(key: str) -> GenerationResult | None`
    - `put(key: str, result: GenerationResult, metadata: dict)`
    - `invalidate(key: str)`
    - `clear_all()`
    - `list_entries() -> list[CacheEntry]`
  - 快取大小上限：`CACHE_MAX_ENTRIES = 100`（加入 constants.py）
  - LRU 淘汰：超過上限時刪除最舊的條目
- **測試:** put/get round-trip、LRU 淘汰、invalidate、clear_all

#### Task 3: 快取過期策略
- **位置:** `cache/store.py`
- **修復:**
  - TTL 過期：預設 7 天（`CACHE_TTL_DAYS = 7`，加入 constants.py）
  - 在 `config.py` 加入 `cache_ttl_days: int = 7` 和 `cache_enabled: bool = True`
  - `get()` 時檢查 TTL，過期自動 invalidate
  - 版本升級時自動失效：快取中記錄 `app_version`，版本不匹配時視為過期
- **測試:** TTL 過期測試、版本不匹配測試

### Part B: Pipeline 整合

#### Task 4: Orchestrator 快取整合
- **位置:** `agents/orchestrator.py`
- **修復:**
  - 在 `generate()` / `agenerate()` 開頭加入快取查詢
  - 命中時直接回傳，跳過整個 AI Pipeline
  - 未命中時正常執行 Pipeline，完成後存入快取
  - 加入 `use_cache: bool = True` 參數（允許強制重新生成）
  - Status callback 顯示「Cache hit」或「Generating...」
- **測試:** cache hit / cache miss / force regenerate 三個場景

#### Task 5: CLI 快取支援
- **位置:** `__main__.py`
- **修復:**
  - `generate` 命令新增 `--no-cache` flag
  - `generate` 命令新增 `--clear-cache` flag
  - 新增 `cache` 子命令：
    - `python -m promptbim cache list` — 列出快取條目
    - `python -m promptbim cache clear` — 清除所有快取
    - `python -m promptbim cache stats` — 顯示快取統計（大小、條目數、命中率）
- **測試:** CLI cache 命令測試

#### Task 6: GUI 快取指示
- **位置:** `gui/chat_panel.py`
- **修復:**
  - Cache hit 時在 ChatPanel 顯示「⚙️ 從快取載入（原生成於 {date}）」
  - 提供「重新生成」按鈕（設 `use_cache=False`）
- **測試:** GUI 快取顯示測試

### Part C: 文件同步

#### Task 7: 全量文件同步
- 依照 CLAUDE.md v1.7.0/v1.8.0 [MANDATORY] 規則，更新 8 項文件
- pyproject.toml version = "2.4.0"
- Info.plist: CFBundleVersion = 19, CFBundleShortVersionString = 2.4.0
- AuditReport.md 更新「無快取機制」為已實作
- Xcode pbxproj 完整性檢查
- git tag v2.4.0

#### Task 8: 建立 PROMPT_P18.md
- 建立下一個 Sprint Prompt（通過 CLAUDE.md v1.8.0 合規性檢查）
- 內容建議：V2 遷移 Phase 0-1（從 docs/V2_Migration_Tasks.md 拉取）

---

## 驗收標準

```
☐ xcodebuild BUILD SUCCEEDED
☐ pytest >= 810 passed（新增 ~20 快取測試）
☐ ruff check: All checks passed
☐ coverage >= 85%
☐ 相同 prompt+土地第二次生成命中快取（不呼叫 API）
☐ --no-cache 強制重新生成可運作
☐ cache list/clear/stats CLI 命令可運作
☐ TTL 7 天過期 + 版本不匹配失效
☐ LRU 淘汰（>100 條目）
☐ 全量文件同步完成
☐ git tag v2.4.0
☐ PROMPT_P18.md 已建立
☐ iMessage 通知已發送（啟動 + 完成）
```

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保 Swift 檔案、Build Phase、Signing 設定正確。
⚠️ iMessage 通知必須發送（啟動 + 完成）。
⚠️ 快取層必須同時支援同步和 async 版本的 Orchestrator。

---

*PROMPT_P17.2.md v1.0 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.8.0 ✅ | SKILL.md ✅*
