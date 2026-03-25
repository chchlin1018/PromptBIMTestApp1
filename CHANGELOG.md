# CHANGELOG

> 版本控制規則: [Semantic Versioning 2.0](https://semver.org/)
> 格式: `## [版本] - 日期` + Added/Changed/Fixed/Removed
> Claude Code 每完成一個 Sprint 自動更新本文件

---

## [Unreleased]

### 規劃中
- P0~P8 完整開發計劃（詳見 TODO.md）

---

## [0.0.1] - 2026-03-25

### Added
- 初始化 GitHub repo `chchlin1018/PromptBIMTestApp1`
- README.md 中文專案介紹
- TODO.md 開發計劃追蹤（P0~P8 共 11 個 Sprint）
- SKILL.md Claude Code 知識庫 (SSOT)
- CHANGELOG.md 版本變更記錄
- LICENSE (MIT)
- .gitignore / .env.example
- `docs/addendum/` 四份技術規格文件
  - 建築零件庫（74 種零件 + 供應商價格）
  - 施工模擬 + 成本估算 + MEP 管線
  - 台灣建築法規引擎（建築技術規則 + 耐震 + 防火 + 無障礙）
- `reference/` 參考資料
  - GeoJSON 土地範例
  - IFC ↔ USD 映射表
  - 測試 prompt 集
- `examples/` 範例目錄骨架

---

## 版本對照表

| 版本 | 對應 Sprint | 里程碑 |
|------|-----------|--------|
| 0.0.1 | — | 文件初始化 |
| 0.1.0 | P0 完成 | 專案骨架可執行 |
| 0.2.0 | P1+P2 完成 | 土地匯入 + BIM 核心 |
| 0.3.0 | P3+P4 完成 | AI Agent + 3D 預覽 |
| 0.4.0 | P4.5 完成 | 法規引擎 |
| 0.5.0 | P5+P6 完成 | 語音 + 成本估算 |
| 0.6.0 | P7 完成 | MEP 管線 |
| 0.7.0 | P8 完成 | 施工模擬 |
| 1.0.0 | 全部完成 | POC 完整版 |
