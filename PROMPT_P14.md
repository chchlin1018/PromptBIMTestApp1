# PROMPT_P14.md — Sprint P14: CI/CD + 安全強化 + 文件最終化

> 版本: v1.0.0 | 建立時間: 2026-03-26
> 前置 Sprint: P13 完成（CLI + 依賴修復 + PDF OCR）
> 依賴: P12 (品質修復), P13 (CLI + 依賴)
> 品質分析: docs/reports/Full_Codebase_Quality_Report.md

## Sprint 目標

1. **GitHub Actions CI** — 自動化測試、lint、build 驗證
2. **安全強化** — 依賴安全掃描、API Key 安全改進
3. **文件最終化** — README / SKILL.md / API docs 更新到 v2.0 水準
4. **最終 Polish** — `__all__` exports, `py.typed`, type hints 改善

---

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在。

## 必讀文件
1. SKILL.md
2. CLAUDE.md
3. docs/reports/Full_Codebase_Quality_Report.md
4. `pyproject.toml`
5. `.github/workflows/` (不存在，待建立)

---

## Part A: GitHub Actions CI/CD

### Task 1: 基本 CI Workflow

- ⬜ 建立 `.github/workflows/ci.yml`
  ```yaml
  name: CI
  on:
    push:
      branches: [main]
    pull_request:
      branches: [main]
  
  jobs:
    test:
      runs-on: macos-14  # Apple Silicon
      steps:
        - uses: actions/checkout@v4
        - uses: conda-incubator/setup-miniconda@v3
          with:
            python-version: '3.11'
            activate-environment: promptbim
        - name: Install dependencies
          run: pip install -e ".[dev]"
        - name: Lint
          run: ruff check src/ tests/
        - name: Test
          run: pytest -m "not api and not slow" --tb=short -q
        - name: Xcode Build
          run: |
            xcodebuild -project PromptBIMTestApp1.xcodeproj \
              -scheme PromptBIMTestApp1 \
              -destination 'platform=macOS' \
              build
  ```

### Task 2: Ruff Lint + Format 設定

- ⬜ 在 `pyproject.toml` 加入 ruff 完整設定：
  ```toml
  [tool.ruff]
  target-version = "py311"
  line-length = 100
  
  [tool.ruff.lint]
  select = ["E", "F", "W", "I", "UP", "B", "SIM"]
  ignore = ["E501"]  # line length handled by formatter
  
  [tool.ruff.format]
  quote-style = "double"
  ```
- ⬜ 執行 `ruff check --fix src/ tests/` 修復所有 auto-fixable issues
- ⬜ 執行 `ruff format src/ tests/` 統一格式

### Task 3: Coverage Report

- ⬜ 在 CI 中加入 coverage：
  ```yaml
  - name: Test with Coverage
    run: pytest --cov=promptbim --cov-report=term-missing --cov-report=xml -m "not api"
  ```
- ⬜ 目標: 整體覆蓋率 > 70%
- ⬜ 建立 `.coveragerc`：
  ```ini
  [run]
  source = src/promptbim
  omit = src/promptbim/gui/*, src/promptbim/web/*, src/promptbim/voice/*
  ```

---

## Part B: 安全強化

### Task 4: 依賴安全掃描

- ⬜ 加入 pip-audit 到 CI：
  ```yaml
  - name: Security Audit
    run: |
      pip install pip-audit
      pip-audit --fix --dry-run
  ```
- ⬜ 建立 `requirements-frozen.txt` 鎖定已知安全版本
- ⬜ 加入 Dependabot 設定 `.github/dependabot.yml`：
  ```yaml
  version: 2
  updates:
    - package-ecosystem: "pip"
      directory: "/"
      schedule:
        interval: "weekly"
  ```

### Task 5: API Key 安全改進

- ⬜ 在 `PythonBridge.swift` loadDotEnv() 中加入安全警告：
  - 如果 .env 檔案權限 > 600，log 警告
- ⬜ 加入 `.env` 到 `.gitignore`（確認已有）
- ⬜ 在 config.py 中加入 API key 格式驗證（`sk-ant-` prefix）
- ⬜ 在 CLI help 中顯示安全建議：
  ```
  Use `conda env config vars set ANTHROPIC_API_KEY=...` instead of .env for better security.
  ```

---

## Part C: 文件最終化

### Task 6: README.md v2.0

- ⬜ 更新 README.md 包含：
  - 完整功能列表（18 Sprint 成果）
  - 安裝指南（conda + pip install）
  - 快速開始（CLI 3 步驟）
  - 截圖/架構圖 placeholder
  - API 使用範例
  - 開發指南（如何加入新模組）
  - License + Credits

### Task 7: SKILL.md 更新

- ⬜ 更新 SKILL.md 反映 P11-P14 所有變更
- ⬜ 加入 CLI 使用範例
- ⬜ 加入 PDF OCR 流程說明
- ⬜ 加入 CI/CD 流程說明

### Task 8: API 文件

- ⬜ 建立 `docs/API.md` — Python API 使用指南
  - Orchestrator 使用範例
  - Schema 說明（LandParcel, BuildingPlan, ZoningRules）
  - Agent 個別使用範例
  - MCP Server 使用說明

---

## Part D: 最終 Polish

### Task 9: Type Hints + Exports

- ⬜ 建立 `src/promptbim/py.typed`（空檔案，標記 PEP 561 typed package）
- ⬜ 在主要 `__init__.py` 加入 `__all__`：
  ```python
  # src/promptbim/__init__.py
  __all__ = ["__version__", "agents", "bim", "codes", "config", "schemas"]
  ```
- ⬜ 同理為 agents/, bim/, schemas/ 的 `__init__.py`

### Task 10: CHANGELOG v2.0 + Final Tag

- ⬜ 更新 CHANGELOG.md 加入 P13 + P14 sections
- ⬜ 更新版本對照表完整列出所有版本
- ⬜ 更新 TODO.md 標記 P13 + P14 完成
- ⬜ 更新 Context Prompt 為 v2.0 完整版
- ⬜ 確認所有文件版本號一致

### Task 11: 測試 + 收尾

- ⬜ CI workflow 在 GitHub 上成功執行（手動觸發驗證）
- ⬜ ruff check 零 error
- ⬜ pip-audit 無 critical vulnerability
- ⬜ 所有 pytest 通過
- ⬜ xcodebuild BUILD SUCCEEDED
- ⬜ Coverage > 70%
- ⬜ git tag: `git tag -a v2.0.0 -m "P14: CI/CD + Security + Documentation v2.0"`
- ⬜ iMessage 通知已發送

---

## 驗收標準

1. **CI 綠色** — GitHub Actions push 觸發 → lint + test + build 全部通過
2. **ruff clean** — `ruff check src/ tests/` 零 error
3. **安全掃描** — pip-audit 無 critical vulnerability
4. **Coverage > 70%** — 核心模組（agents, bim, codes, schemas）覆蓋充分
5. **README v2.0** — 完整安裝/使用/開發指南
6. **SKILL.md 更新** — 反映全部 Sprint 成果
7. **API 文件** — docs/API.md 覆蓋核心 API
8. **git tag v2.0.0** — POC v2.0 里程碑

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
**執行順序: Part A (T1-3) → Part B (T4-5) → Part C (T6-8) → Part D (T9-11)**
使用 P10.2 的 debug.py logger，不要用 print()。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
