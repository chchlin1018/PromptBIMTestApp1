# PROMPT_P2.5.md — Sprint P2.5: 建築零件庫

> 版本: v1.0.0 | 建立時間: 2026-03-25
> 前置 Sprint: P0 ✅ 已完成, P1 ✅ 已完成, P2 ✅ 已完成
> 依賴: P2

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在且所有依賴可 import。

## 必讀文件
1. SKILL.md — 特別是 Section 4 (專案結構) 和 Section 10 (開發規範)
2. TODO.md — 確認 P2.5 task 清單
3. CLAUDE.md — 行為規範
4. docs/addendum/01_component_library.md — 74 種建築零件庫規格

## 本 Sprint 的 Task 清單

- ⬜ `bim/components/base.py` — ComponentDef + SupplierInfo + PriceRange
- ⬜ `bim/components/registry.py` — ComponentRegistry
- ⬜ 結構構件 (12 種) 參數化幾何生成
- ⬜ 垂直運輸 (12 種) 參數化 + mesh 佔位
- ⬜ 開口 (10 種) 參數化生成
- ⬜ 其他類別佔位定義 (40+ 種)
- ⬜ 下載 5-10 個免費 GLB 模型 (Sketchfab CC0)
- ⬜ 供應商/價格 seed data (台灣市場)
- ⬜ 測試 + xcodebuild 通過

## 執行指令
所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。

## 驗收標準
1. `ComponentRegistry.search(["電梯"])` 回傳完整定義含供應商
2. 至少 74 種零件定義可查詢
3. xcodebuild BUILD SUCCEEDED
4. pytest 全部通過
