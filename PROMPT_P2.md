# PROMPT_P2.md — Sprint P2: IFC + USD 生成核心

> 版本: v1.0.0 | 建立時間: 2026-03-25
> 前置 Sprint: P0 ✅ 已完成, P1 ✅ 已完成
> 依賴: P0

## 環境檢查

執行 CLAUDE.md 中的環境檢查腳本。確認 conda env `promptbim` 存在且 ifcopenshell + pxr 可 import。
如果 ifcopenshell 或 usd-core 未安裝，自動安裝：
```bash
conda activate promptbim
conda install -c conda-forge ifcopenshell -y
pip install usd-core
```

## 必讀文件
1. SKILL.md — 特別是 Section 5 (Schema) 和 Section 10 (開發規範)
2. TODO.md — 確認 P2 task 清單
3. CLAUDE.md — 行為規範
4. schemas/plan.py — BuildingPlan, StoryPlan, WallDef 等已有定義

## 本 Sprint 的 Task 清單

- ⬜ `bim/geometry.py` — 牆/板/屋頂 mesh 生成
- ⬜ `bim/ifc_generator.py` — IfcOpenShell 高階封裝
- ⬜ `bim/usd_generator.py` — pxr USD 封裝
- ⬜ `bim/materials.py` — 材質定義 (IFC + USD 雙映射)
- ⬜ `schemas/plan.py` — BuildingPlan 完整 schema (如需擴充)
- ⬜ `examples/01_simple_box.py` — 硬編碼方盒 → .ifc + .usda
- ⬜ `examples/02_l_shaped_office.py` — L型辦公樓
- ⬜ 測試 + xcodebuild 通過

## 執行指令
所有問題答案都是 Yes，不要中斷詢問。
工作結束前嚴格遵循 CLAUDE.md [MANDATORY] 步驟。

## 驗收標準
1. `python examples/01_simple_box.py` → 生成 .ifc + .usda
2. IFC 檔案可被 IfcOpenShell 重新讀取驗證
3. USD 檔案可被 pxr.Usd.Stage.Open() 開啟驗證
4. xcodebuild BUILD SUCCEEDED
5. pytest 全部通過
