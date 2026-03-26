# ⚠️ P22-P26 已移至 Future Features

> 決定日期: 2026-03-26
> 原因: Web WASM / Windows Qt 6 / 跨平台測試 / 效能優化 / 商業化準備需要對應平台環境才能執行

## 已移至 Future Features 的項目

| 原 Sprint | 內容 | 原因 | 建議時機 |
|-----------|------|------|----------|
| P22 | Web WASM + REST API + React Frontend | 需要 Emscripten + 瀏覽器測試環境 | 有部署需求時 |
| P23 | Windows Qt 6 骨架 + 主視窗 + 3D | 需要 Windows 機器或 VM | 有 Windows 環境時 |
| P24 | 跨平台 E2E 一致性驗證 | 依賴 P22 + P23 完成 | P22+P23 後 |
| P25 | C++ vs Python 效能優化 + 基準報告 | POC 階段非必要 | 效能成為瓶頸時 |
| P26 | App Store / Windows Store 打包 + License | 商業化前置 | 決定商業化時 |

## 目前專案狀態

- **版本:** v2.8.0
- **測試:** 957 (pytest 820 + GoogleTest 137)
- **平台:** macOS (SwiftUI + PySide6 + C++ libpromptbim)
- **V2 Migration:** Phase 0-4 完成（C++ 核心 + GIS + BIM + SwiftUI 3D）
- **POC 驗證:** 完成 ✅

## 如需繼續開發

在 docs/V2_Migration_Tasks.md 中查看完整的 Phase 5 任務拆解（V2-060~V2-076）。
建立新的 PROMPT_P{X}.md 時必須符合 CLAUDE.md v1.14.1 合規性檢查。
