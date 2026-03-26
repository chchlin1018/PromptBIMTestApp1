# PROMPT_P4.md — Sprint P4: AI Agent Pipeline

> 版本: v1.0.0 | 建立時間: 2026-03-25
> 前置 Sprint: P0 ✅ 已完成, P1 ✅ 已完成, P2 ✅ 已完成, P2.5 ✅ 已完成, P3 ✅ 已完成
> 依賴: P1, P2

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在且所有依賴可 import。

## 必讀文件
1. SKILL.md — 特別是 Section 6 (Agent 2 Planner Prompt) 和 Section 10 (開發規範)
2. TODO.md — 確認 P4 task 清單
3. CLAUDE.md — 行為規範

## 本 Sprint 的 Task 清單

- ⬜ `agents/base.py` — Claude API wrapper (BaseAgent)
- ⬜ `agents/enhancer.py` — Agent 1: 需求增強
- ⬜ `agents/planner.py` — Agent 2: 建築規劃 (含土地+法規 context)
- ⬜ `agents/builder.py` — Agent 3: IFC+USD 雙輸出 (純 Python)
- ⬜ `agents/checker.py` — Agent 4: 規則檢查 + 迭代修正
- ⬜ `agents/orchestrator.py` — Pipeline 編排
- ⬜ `gui/chat_panel.py` — Chat UI 整合
- ⬜ 測試 + xcodebuild 通過

## 執行指令
所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。

## 驗收標準
1. Chat 輸入描述 → 自動在土地上生成建築 → 2D+3D 同步更新
2. Agent Pipeline: Enhancer → Planner → Builder → Checker 完整運作
3. Builder Agent 純 Python，不使用 LLM
4. xcodebuild BUILD SUCCEEDED
5. pytest 全部通過
