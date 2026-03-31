# S-PTB-FINAL-AUDIT PROMPT v1.0 — PTB 最終全面品質審查 [15T/3P] [Mac Mini]

Sprint: S-PTB-FINAL-AUDIT | 專案: PTB | 機器: Mac Mini
目標: mvp-v1.0.1-audit | 規格: 15T/3P
角色: 資深品質總監 最終審查
⛔ pytest 禁止 | ctest only

## P1/3: 品質掃描 (6T)
T01: C++ 品質全掃描 (const/RAII/naming)
T02: 安全性掃描 (buffer/null/pybind11)
T03: 記憶體掃描 (leak/pool/copy)
T04: Python 層品質 (import清理/廢棄代碼)
T05: CMake 品質 (不必要依賴/編譯時間)
T06: Demo 腳本檢查 (5分鐘流程完整性)

## P2/3: 修復+優化 (5T)
T07: 修復所有安全問題
T08: 修復記憶體問題
T09: 效能優化
T10: 清理死代碼
T11: ctest ALL PASS

## P3/3: Finalize (4T)
T12: FinalAuditReport PTB-FAR-FINAL-001 (6維度+Demo穩定性)
T13: ARCHITECTURE.md + CHANGELOG.md 最終版
T14: git tag mvp-v1.0.1-audit
T15: 完成通知 + tmux kill

Source: https://www.notion.so/334f154a6472810999f0ee73a2b3837c
Job Queue: 334f154a-6472-813b-b90a-ec5c85548074
