# PROMPT_P14.md — Sprint P14: CI/CD + 安全強化 + 文件最終化

> 版本: v2.0.0 | 建立時間: 2026-03-26
> 前置 Sprint: P13 ✅ 完成（CLI + 依賴修復 + PDF OCR, 705 tests）
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
2. CLAUDE.md（⚠️ v1.8.0 — 含新規則：全量文件同步 + pbxproj 檢查 + PROMPT 合規性檢查）
3. TODO.md
4. docs/reports/Full_Codebase_Quality_Report.md
5. `pyproject.toml`

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

- ⬜ 在 `pyproject.toml` 加入 ruff 完整設定
- ⬜ 執行 `ruff check --fix src/ tests/` 修復所有 auto-fixable issues
- ⬜ 執行 `ruff format src/ tests/` 統一格式

### Task 3: Coverage Report

- ⬜ 在 CI 中加入 coverage
- ⬜ 目標: 整體覆蓋率 > 70%
- ⬜ 建立 `.coveragerc`

---

## Part B: 安全強化

### Task 4: 依賴安全掃描

- ⬜ 加入 pip-audit 到 CI
- ⬜ 建立 `requirements-frozen.txt`
- ⬜ 加入 Dependabot 設定 `.github/dependabot.yml`

### Task 5: API Key 安全改進

- ⬜ PythonBridge.swift loadDotEnv() 加入權限檢查警告
- ⬜ config.py 加入 API key 格式驗證（`sk-ant-` prefix）
- ⬜ CLI help 顯示安全建議

---

## Part C: 文件最終化

### Task 6: README.md v2.0

- ⬜ 完整功能列表（20 Sprint 成果）
- ⬜ 安裝指南（conda + pip install）
- ⬜ 快速開始（CLI 3 步驟）
- ⬜ API 使用範例
- ⬜ 開發指南
- ⬜ License + Credits

### Task 7: SKILL.md 更新

- ⬜ 反映 P11-P14 所有變更
- ⬜ 加入 CLI 使用範例
- ⬜ 加入 PDF OCR 流程說明
- ⬜ 加入 CI/CD 流程說明

### Task 8: API 文件

- ⬜ 建立 `docs/API.md`
  - Orchestrator 使用範例
  - Schema 說明
  - Agent 個別使用
  - MCP Server 使用說明

---

## Part D: 最終 Polish

### Task 9: Type Hints + Exports

- ⬜ 建立 `src/promptbim/py.typed`
- ⬜ 在主要 `__init__.py` 加入 `__all__`

### Task 10: 全量文件同步 + Final Tag

- ⬜ 更新 CHANGELOG.md 加入 P14 section
- ⬜ 更新版本對照表完整列出所有版本
- ⬜ 更新 TODO.md 標記 P14 完成
- ⬜ 更新 docs/PromptBIM_Context_Prompt.md 為 v2.0 完整版
- ⬜ 更新 pyproject.toml + __init__.py version
- ⬜ 確認所有文件版本號一致

### Task 11: Xcode pbxproj 完整性檢查

- ⬜ 執行 CLAUDE.md 中的 pbxproj 檢查清單：
  - 所有 .swift 檔案都在 pbxproj 中被正確引用
  - Info.plist 設定正確（version, build number, termination settings）
  - Signing 設定正確
  - Bundle ID 一致
  - macOS Deployment Target 正確

### Task 12: 測試 + 收尾

- ⬜ CI workflow 在 GitHub 上成功執行
- ⬜ ruff check 零 error
- ⬜ pip-audit 無 critical vulnerability
- ⬜ 所有 pytest 通過
- ⬜ xcodebuild BUILD SUCCEEDED
- ⬜ Xcode pbxproj 完整性檢查通過
- ⬜ Coverage > 70%
- ⬜ git tag: `git tag -a v2.0.0 -m "P14: CI/CD + Security + Documentation v2.0"`
- ⬜ iMessage 通知已發送

---

## 驗收標準

1. **CI 綠色** — GitHub Actions push 觸發 → lint + test + build 全部通過
2. **ruff clean** — `ruff check src/ tests/` 零 error
3. **安全掃描** — pip-audit 無 critical vulnerability
4. **Coverage > 70%** — 核心模組覆蓋充分
5. **README v2.0** — 完整安裝/使用/開發指南
6. **SKILL.md 更新** — 反映全部 Sprint 成果
7. **API 文件** — docs/API.md 覆蓋核心 API
8. **Xcode pbxproj 完整** — 所有檔案引用正確、設定一致
9. **全量文件同步** — 所有版本號對齊 v2.0.0
10. **git tag v2.0.0** — POC v2.0 里程碑

---

## 執行指令

所有問題答案都是 Yes，不要中斷詢問。
**執行順序: Part A (T1-3) → Part B (T4-5) → Part C (T6-8) → Part D (T9-12)**
使用 P10.2 的 debug.py logger，不要用 print()。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。
⚠️ 特別注意「Sprint 完成全量文件同步」— 所有文件必須反映最新狀態後才能 commit。
⚠️ 特別注意「Xcode pbxproj 完整性檢查」— 確保 Swift 檔案、Build Phase、Signing 設定正確。
⚠️ iMessage 通知必須發送（啟動 + 完成）。
