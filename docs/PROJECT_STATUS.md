# PromptBIM 專案狀態報告

> **更新:** 2026-03-27 01:00 CST | **報告人:** Claude (claude.ai)
> **Repo:** chchlin1018/PromptBIMTestApp1 (private, main branch)

---

## 1. 版本狀態

| 項目 | 狀態 |
|------|------|
| 當前版本 | v2.10.0 (P23, 最後成功 tag) |
| P24 版本 | v2.11.0 (代碼完成，**未打 tag** — pytest OOM 未通過) |
| CLAUDE.md | **v1.21.0** |
| SKILL.md | **v3.7** |
| PROMPT_P24.md | **v5.0 — ⚠️ 暫緩執行**（pytest OOM 需手動修復） |
| PROMPT_P25.md | **v2.0 — 準備執行** |

---

## 2. Sprint 進度

| Sprint | 版本 | 狀態 | 說明 |
|--------|------|------|------|
| P0~P23 | v0.1.0~v2.10.0 | ✅ 完成 | 全部已 tag |
| **P24** | v2.11.0 | **⚠️ 暫緩執行** | 代碼完成(commit `78bb646`)，pytest OOM 4次失敗，需手動修復 conftest.py 後打 tag |
| **P25** | v2.12.0 | **🔜 準備執行** | Performance + Windows + Documentation (3 Parts / 18 Tasks) |

### P24 暫緩原因

- 28 個 Task 代碼全部完成並推送
- Sprint24_AuditReport.md ✅ / PROMPT_P25.md ✅ / 文件同步 v2.11.0 ✅
- **唯一阻塞:** pytest OOM（4 次失敗，python 進程吃 26GB）
- **解法:** 手動在 conftest.py 頂部加 `os.environ['QT_QPA_PLATFORM'] = 'offscreen'`
- **完成後:** `git tag v2.11.0 && git push origin v2.11.0`

---

## 3. 治理框架

| 文件 | 版本 | 核心規則 |
|------|------|----------|
| CLAUDE.md | v1.21.0 | task_start/task_done 封裝 + pytest 安全 + 記憶體監控 |
| SKILL.md | v3.7 | 同步 v1.21.0 所有規則 |

### 歷史教訓

| # | 事故 | 規則 |
|---|------|------|
| 🔴 P18 | 文件截斷 | 禁止修改治理文件 |
| 🔴 P22 | notify 遺失 | PROMPT 顯式定義函數 |
| 🔴 P22.1 | 未 commit | Part 結束 commit+push |
| 🔴 P24a | OOM | check_mem + <1GB 暫停 |
| 🔴 P24b | 殭屍 Python | pkill + offscreen |
| 🔴 P24d | Task 通知跳過 | task_start/task_done |
| 🔴 P24e | pytest 反覆 OOM | conftest.py + 禁止多 pytest + ignore e2e |

---

## 4. Windows 遷移架構

| 項目 | 決策 |
|------|------|
| 方案 | Hydra Storm + PyVista hybrid |
| 路線圖 | P24-P29 (macOS) → P30-P31 (Windows) → P32-P33 (Hydra Storm v3.0) |

---

*docs/PROJECT_STATUS.md | 2026-03-27*
