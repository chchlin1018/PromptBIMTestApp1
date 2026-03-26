# PROMPT_P17.md — Sprint P17: 全面修整 + 架構強化 + CI 修復 (Final Polish & Architecture Hardening)

> 版本: v1.1 | 建立時間: 2026-03-26 | 更新: 加入接續 Sprint 提醒
> 前置 Sprint: P16 ✅ 完成（品質修整, 725 tests, v2.1.0）
> 前置 Sprint: P15 ⬜ 未執行（併入本 Sprint）
> 依賴: AuditReport.md, CLAUDE.md v1.8.0, SKILL.md, docs/DesignDocForV2.md
> 品質分析: P14 + P16 品質分析報告（Claude Opus 4.6）
> 目標版本: v2.2.0
> ⬇️ 接續: PROMPT_P17.1.md（async/await）→ PROMPT_P17.2.md（Plan 快取）

---

## Sprint 目標

整合 **5 個來源** 的所有殘留工作，一次性收尾：
1. AuditReport.md 未修復項目（M-2, M-4, L-1~L-5 + 架構風險 + 測試缺口）
2. P14/P16 品質分析發現的問題
3. P15 的 V2 架構工作（lazy import, plugin system, test refactor）
4. CI/CD 關鍵修復（requirements-frozen.txt 損壞、假 CVE ID）
5. ContentView.swift 版本號動態化

共 **20 個 Task**，分 5 個 Part。

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。
確認 `git pull origin main` 為最新。

## 必讀文件

1. **SKILL.md** — 專案 SSOT
2. **CLAUDE.md v1.8.0** — 行為規範（所有 [MANDATORY] 規則）
3. **AuditReport.md** — 代碼審核報告（未修復項目是本 Sprint 主要來源）
4. **TODO.md** — 確認當前 Sprint 狀態
5. **pyproject.toml** — 依賴與版本
6. **docs/DesignDocForV2.md** — V2 架構設計（Part C 依賴）
7. **src/promptbim/constants.py** — P16 新增的常數檔（確認不重複）

---

## Task 清單

### Part A: CI/CD 緊急修復（最高優先）

#### Task 1: 修復 requirements-frozen.txt [CI 損壞]
- **問題:** `pip freeze` 在 conda 環境下產出的 frozen 檔案含有 `@ file:///System/Volumes/Data/home/conda/feedstock_root/...` 本地路徑，導致 `pip-audit` 和 GitHub Actions 都無法使用
- **修復:**
  - 安裝 `pip-tools`：`pip install pip-tools`
  - 用 `pip-compile` 從 pyproject.toml 生成乾淨的 frozen 檔：
    ```bash
    pip-compile pyproject.toml -o requirements-frozen.txt --strip-extras
    ```
  - 如果 `pip-compile` 不適用（conda 專有套件），則用：
    ```bash
    pip freeze | grep -v '@ file://' | grep -v '^#' > requirements-frozen.txt
    ```
  - 驗證生成的檔案不含任何 `@ file://` 路徑
- **測試:** `pip-audit -r requirements-frozen.txt` 在 promptbim 環境下成功執行

#### Task 2: 移除假 CVE ID [CI 誤導]
- **位置:** `.github/workflows/ci.yml`
- **問題:** `--ignore-vuln CVE-2026-4539` 是 Claude Code 自行編造的 CVE ID
- **修復:**
  - 先執行 Task 1 修復 frozen 檔
  - 執行 `pip-audit -r requirements-frozen.txt` 確認結果
  - 如果結果乾淨（0 vulnerabilities）：移除整個 `--ignore-vuln` 參數
  - 如果有真正 CVE：用實際的 CVE ID 替換
  - 最終 ci.yml security job 應為：
    ```yaml
    - name: Security audit
      run: pip-audit -r requirements-frozen.txt
    ```
- **測試:** 本地 `pip-audit` 通過且無假 CVE

#### Task 3: 驗證 CI 在 GitHub Actions 可執行 [CI 驗證]
- **修復:**
  - 確認 `.github/workflows/ci.yml` 的 security job 能在 `ubuntu-latest` 上用修復後的 `requirements-frozen.txt` 正常運行
  - 如果 frozen 檔含 conda 專有套件（如 `ifcopenshell`、`usd-core`）在 PyPI 上不存在，security job 需改為：
    ```yaml
    - name: Security audit
      run: |
        pip install -e ".[dev]" 2>/dev/null || true
        pip-audit --desc 2>/dev/null || echo "⚠️ Some packages not auditable in CI"
    ```
  - 或改為只審計 PyPI 可取得的套件
- **測試:** ci.yml 語法正確（`actionlint` 或手動檢查）

### Part B: AuditReport 殘留修復（Medium + Low）

#### Task 4: 退縮計算改進 [AuditReport M-2]
- **位置:** `land/setback.py`
- **問題:** 非矩形地塊使用均勻退縮（shapely buffer）而非逐邊計算
- **修復:**
  - 現有 `uniform_setback()` 保留（作為 fallback）
  - 新增 `per_side_setback(polygon, setbacks: dict)` 支持逐邊退縮
  - setbacks dict 格式：`{"front": 5.0, "rear": 3.0, "left": 2.0, "right": 2.0}`
  - 使用 shapely `parallel_offset` 或逐邊平移計算
  - 如果地塊邊數 > 4，fallback 到 uniform
- **測試:** 新增矩形 + L 形 + 三角形退縮測試

#### Task 5: API Rate Limiter [AuditReport 架構風險]
- **位置:** `agents/base.py` 或新建 `agents/rate_limiter.py`
- **問題:** 無 API 呼叫速率限制，可能觸發 Anthropic 限額
- **修復:**
  - 使用 `tenacity` 的 rate limiter 或簡單的 token bucket
  - 預設：每分鐘最多 50 次 API 呼叫（Anthropic 預設限額）
  - 在 `config.py` 加入 `api_rate_limit_rpm: int = 50`
  - 在 `BaseAgent._call_api_with_retry()` 前加入 rate limit check
- **測試:** 新增速率限制觸發測試（mock time）

#### Task 6: Schema 版本控制 [AuditReport L-1]
- **位置:** `schemas/plan.py`, `schemas/land.py`, `schemas/result.py` 等
- **問題:** 新增欄位可能破壞舊版序列化資料
- **修復:**
  - 在主要 schema 加入 `schema_version: str = "2.2.0"` 欄位
  - 加入 `model_validator` 在載入時檢查版本相容性
  - 舊版資料（無 schema_version）自動視為 v1.0.0 並嘗試遷移
- **測試:** 新增版本遷移測試（v1 → v2 資料載入）

#### Task 7: 輸入大小限制 [AuditReport L-3]
- **位置:** `land/parsers/geojson.py`, `land/parsers/manual.py` 等
- **問題:** `json.load()` 無檔案大小限制
- **修復:**
  - 在所有土地解析器入口加入檔案大小檢查
  - 預設上限：`MAX_LAND_FILE_SIZE_MB = 50`（加入 constants.py）
  - 超過上限時拋出 `ValueError("File size exceeds 50MB limit")`
- **測試:** 新增大檔案拒絕測試（mock 大檔案）

#### Task 8: lxml 安裝 [AuditReport L-5]
- **問題:** fastkml 缺少 lxml，產生 pytest warning
- **修復:**
  - 在 pyproject.toml dependencies 加入 `lxml>=5.0`
  - 更新 requirements-frozen.txt
- **測試:** pytest 執行時不再有 lxml warning

#### Task 9: ComponentRegistry 效能改善 [AuditReport L-2]
- **位置:** `bim/components/registry.py`
- **問題:** `_components` 線性搜尋 O(n)
- **修復:**
  - 加入 `_by_category: dict[str, list]` 倒排索引
  - `search()` 改用索引查詢
  - `register()` 同時更新主列表和索引
- **測試:** 現有測試通過 + 新增效能基準測試

#### Task 10: PythonBridge conda 路徑改善 [AuditReport L-4]
- **位置:** `PromptBIMTestApp1/PythonBridge.swift`
- **問題:** 硬編碼 `/opt/homebrew/Caskroom/miniforge/` 是 Apple Silicon 專用
- **修復:**
  - 加入 Intel Mac 路徑：`/usr/local/Caskroom/miniforge/base/envs/promptbim/bin/python`
  - 加入通用 `which python3` fallback
  - 加入 `PROMPTBIM_PYTHON` 環境變數覆蓋（最高優先）
- **測試:** xcodebuild BUILD SUCCEEDED

### Part C: V2 架構強化（原 P15 工作）

#### Task 11: Lazy Import 優化 [P15 目標 2]
- **位置:** `agents/orchestrator.py`, `__main__.py`
- **問題:** Orchestrator init 時 eager import 所有 Agent，影響 CLI 啟動速度
- **修復:**
  - Orchestrator 改為 lazy import：在 `generate()` / `modify()` 時才 import 對應 Agent
  - `__main__.py --version` 路徑不觸發任何 agent/bim import
  - 目標：`python -m promptbim --version` < 0.5s
- **測試:** 新增啟動速度測試（`--version` < 0.5s, `check` < 2s）

#### Task 12: Plugin 架構基礎 [P15 目標 3]
- **位置:** 新建 `plugins/` 目錄
- **問題:** Agent / Parser / Code Rule 目前硬編碼，無法外部擴展
- **修復:**
  - 建立 `plugins/base.py`：`PluginRegistry` + `@register_plugin` decorator
  - 三種 plugin 類型：`agent`, `parser`, `code_rule`
  - 土地解析器改用 plugin 註冊模式（GeoJSON/KML/DXF/SHP/PDF 各自註冊）
  - 法規引擎改用 plugin 註冊模式（15+ 規則各自註冊）
  - 保持向後相容：現有代碼不需修改即可運行
- **測試:** 新增 plugin 註冊/發現/執行測試

#### Task 13: V2 架構文件拆解 [P15 目標 1]
- **位置:** `docs/DesignDocForV2.md` → `docs/V2_Migration_Tasks.md`
- **修復:**
  - 讀取 DesignDocForV2.md
  - 產出 `docs/V2_Migration_Tasks.md`：將方案 D（混合架構）拆為可執行 task 列表
  - 標記每個 task 的預估工時、依賴關係、優先級
  - 這是文件工作，不涉及程式碼修改
- **測試:** 文件存在且格式正確

### Part D: 測試缺口填補 + 韌性

#### Task 14: 網路故障模擬測試 [AuditReport 測試缺口]
- **位置:** `tests/test_agents/test_network_failure.py`（新建）
- **修復:**
  - Mock `httpx.TimeoutException` → 驗證 fallback 觸發
  - Mock `httpx.ConnectError` → 驗證重試 + fallback
  - Mock `anthropic.APIStatusError(503)` → 驗證 tenacity retry 3 次
  - Mock `anthropic.APIStatusError(429)` → 驗證不重試（4xx）
- **測試:** 新增 ~8 個網路故障場景測試

#### Task 15: 惡意輸入測試 [AuditReport 測試缺口]
- **位置:** `tests/test_land/test_fuzzing.py`（新建）
- **修復:**
  - 測試超大 GeoJSON（>1000 個 features）
  - 測試畸形 JSON（缺 type, 缺 coordinates）
  - 測試自交叉多邊形
  - 測試座標極端值（>180 經度, >90 緯度）
  - 測試空檔案、二進位檔案
- **測試:** 新增 ~10 個 fuzzing 測試

#### Task 16: 檔案權限錯誤測試 [AuditReport 測試缺口]
- **位置:** `tests/test_integration/test_permissions.py`（新建）
- **修復:**
  - Mock `PermissionError` 在 IFC/USD 寫入時 → 驗證錯誤訊息
  - Mock `PermissionError` 在 .env 讀取時 → 驗證 fallback
  - Mock `IsADirectoryError` 在輸出路徑時
- **測試:** 新增 ~5 個權限錯誤測試

### Part E: Swift 修復 + 文件同步

#### Task 17: ContentView 版本號動態化 [P16 遺留 N1]
- **位置:** `PromptBIMTestApp1/ContentView.swift`
- **問題:** 版本號仍為硬編碼 `"v2.1.0"`，每次升版都要手動改
- **修復:**
  - PythonBridge 新增 `@Published var version: String = ""` 屬性
  - 在 `checkPython()` 成功後解析 `--version` 輸出存入 `version`
  - ContentView 改為 `Text("v\(bridge.version)")` 動態顯示
  - Fallback：版本未取得時顯示 "v?.?.?"
- **測試:** xcodebuild BUILD SUCCEEDED + 無 warning

#### Task 18: AuditReport 更新 [文件維護]
- **位置:** `AuditReport.md`
- **修復:**
  - 在「發現的問題清單」中標記 P16 已修復項目（C-1~C-3, H-1~H-5, M-1/M-3/M-5/M-6）
  - 在「發現的問題清單」中標記 P17 已修復項目
  - 更新「關鍵數據」表格（測試數、覆蓋率等）
  - 更新「審核結論」評級
- **測試:** 文件內容與實際狀態一致

#### Task 19: P14/P16 品質分析報告歸檔 [文件維護]
- **位置:** `docs/reports/P14_Quality_Analysis_Report.md`（新建）, `docs/reports/P16_Quality_Analysis_Report.md`（新建）
- **修復:**
  - 將 P14 品質分析結果整理為正式報告（評分 8.2, CI/CD 審查, 版本同步）
  - 將 P16 品質分析結果整理為正式報告（評分 9.0, 逐項驗證表）
- **測試:** 報告文件存在且格式與 P11 報告一致

#### Task 20: 全量文件同步 + 驗收
- 依照 CLAUDE.md v1.7.0 [MANDATORY] 規則，更新以下 8 項：
  1. `TODO.md` — P17 所有 task 標記 ✅，版本 v2.2.0
  2. `CHANGELOG.md` — 新增 [2.2.0] 條目 + 版本對照表
  3. `README.md` — 更新測試數、版本號、功能狀態
  4. `docs/PromptBIM_Context_Prompt.md` — 反映 P17 完成，v2.2.0
  5. `pyproject.toml` — version = "2.2.0"
  6. `src/promptbim/__init__.py` — fallback = "2.2.0"
  7. `SKILL.md` — 更新架構變更（plugins/, constants 擴充）— 如果 PROMPT 允許
  8. `AuditReport.md` — Task 18 已處理
- Xcode pbxproj 完整性檢查（CLAUDE.md v1.8.0 規則）
  - Info.plist: CFBundleVersion = 17, CFBundleShortVersionString = 2.2.0
- 建立 `PROMPT_P18.md`（通過合規性檢查）
- git tag v2.2.0

---

## 驗收標準

```
☐ xcodebuild BUILD SUCCEEDED（無 warning）
☐ pytest >= 760 passed（新增 ~35+ 測試）
☐ ruff check: All checks passed
☐ coverage >= 85%
☐ pip-audit -r requirements-frozen.txt 成功執行且無假 CVE
☐ requirements-frozen.txt 不含任何 @ file:// 路徑
☐ python -m promptbim --version < 0.5s（lazy import 生效）
☐ AuditReport M-2, M-4（partial）, L-1~L-5 修復
☐ Plugin 架構基礎建立（plugins/base.py + 土地解析器 + 法規引擎）
☐ 網路故障 + fuzzing + 權限測試新增
☐ ContentView 版本號動態顯示
☐ 全量文件同步完成（8 項）
☐ Xcode pbxproj 完整性檢查通過
☐ AuditReport 已更新修復狀態
☐ P14/P16 品質報告已歸檔
☐ git tag v2.2.0 已建立並推送
☐ PROMPT_P18.md 已建立（通過合規性檢查）
☐ iMessage 通知已發送（啟動 + 完成）
```

---

## 新增依賴

| 套件 | 用途 | 加入位置 |
|------|------|----------|
| `lxml>=5.0` | fastkml XML 處理（消除 warning） | pyproject.toml dependencies |
| `pip-tools>=7.0` | 生成乾淨的 frozen requirements | pyproject.toml [dev] |

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保 Swift 檔案、Build Phase、Signing 設定正確。
⚠️ iMessage 通知必須發送（啟動 + 完成）。
⚠️ Task 1-3（CI 修復）必須最先執行，因為後續 Task 可能修改 dependencies。
⚠️ 執行 Task 1 時特別注意：requirements-frozen.txt 不得含有 `@ file://` 本地路徑。

---

## 🔗 接續 Sprint 提醒

> **P17 完成後，請立即執行 P17.1（async/await）。**
> P17.1 完成後再執行 P17.2（Plan 快取）。
>
> **P17 完成後的 tmux 指令：**
> ```bash
> # 在 Mac Mini 上（已在 tmux session 內）
> cd ~/Documents/MyProjects/PromptBIMTestApp1
> git pull origin main
> conda activate promptbim
> claude --dangerously-skip-permissions -p "請讀取 PROMPT_P17.1.md 並執行所有 task。不要問任何問題。"
> ```

---

*PROMPT_P17.md v1.1 | 2026-03-26 | 合規性檢查: CLAUDE.md v1.8.0 ✅ | SKILL.md ✅*
