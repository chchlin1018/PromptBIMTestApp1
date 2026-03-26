# PROMPT_P3.md — Sprint P3: 3D 互動預覽

> 版本: v1.0.0 | 建立時間: 2026-03-25
> 前置 Sprint: P0 ✅ 已完成, P1 ✅ 已完成, P2 ✅ 已完成, P2.5 ✅ 已完成
> 依賴: P2

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在且所有依賴可 import。

## 必讀文件
1. SKILL.md — 特別是 Section 4 (專案結構) 和 Section 10 (開發規範)
2. TODO.md — 確認 P3 task 清單
3. CLAUDE.md — 行為規範

## 本 Sprint 的 Task 清單

- ⬜ `viz/model_3d.py` — BuildingPlan → PyVista mesh 組裝
- ⬜ `gui/model_view.py` — pyvistaqt 嵌入 Qt
- ⬜ 樓層剖面切換
- ⬜ `viz/site_plan.py` — 2D 配置圖 (土地+建築疊合)
- ⬜ 測試 + xcodebuild 通過

## 執行指令
所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。

## 驗收標準
1. 生成後 3D Tab 自動顯示可旋轉的建築模型
2. 樓層剖面可切換
3. 2D 配置圖顯示土地+建築疊合
4. xcodebuild BUILD SUCCEEDED
5. pytest 全部通過
