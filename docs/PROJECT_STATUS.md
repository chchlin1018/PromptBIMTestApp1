# PromptBIM 專案狀態報告

> **更新:** 2026-03-27 00:30 CST | **報告人:** Claude (claude.ai)
> **Repo:** chchlin1018/PromptBIMTestApp1 (private, main branch)

---

## 1. 版本狀態

| 項目 | 狀態 |
|------|------|
| 當前版本 | v2.10.0 (P23, 最後成功 tag) |
| P24 版本 | v2.11.0 (代碼完成，**未打 tag** — pytest OOM 未通過) |
| CLAUDE.md | **v1.21.0** (commit `e3d1de9`) |
| SKILL.md | **v3.7** (commit `0ed952d`) |
| PROMPT_P24.md | **v4.0** (commit `e3d1de9`) |

---

## 2. Git Commit 歷史（最新 10 筆）

```
78bb646  [P24] Part A-E complete — all 28 tasks recovered from stash
0ed952d  SKILL.md v3.7 — task_start/task_done enforcement
e3d1de9  CLAUDE.md v1.21.0 + PROMPT_P24.md v4.0 — Task notify enforcement
00286a7  SKILL.md v3.6 — pytest safety (QT_QPA_PLATFORM + pkill)
99d2eb1  CLAUDE.md v1.20.0 — zombie Python + offscreen + pytest safety
6c12c52  SKILL.md v3.5 — lessons learned + memory + git safety
f08002e  CLAUDE.md v1.19.0 — comprehensive lessons + 26-step flow
c43bba9  PROMPT_P24.md v3.0 — memory monitoring
8acc8bc  SKILL.md v3.4 — memory monitoring
18623db  wip: P24 partial — Part A-D recovered (OOM)
```

---

## 3. P24 Sprint 完成狀態

### 代碼工作（全部完成 ✅）

| Part | Tasks | 描述 | 檔案 | 狀態 |
|------|-------|------|------|------|
| A | 1-8 | Demo 3D 自動生成 | demo_data.py, BIMSceneBuilder.swift | ✅ |
| B | 9-14 | 進階 BIM | parking.py, structural.py, vertical.py | ✅ |
| C | 15-20 | CI/CD + 啟動優化 | ci.yml, dev_setup.sh, sync_version.sh | ✅ |
| D | 21-24 | 整合測試 | test_p24_integration.py, test_mcp/swift | ✅ |
| E | 25 | **pytest 驗收** | pytest OOM 4次失敗 | ❌ **阻塞** |
| E | 26 | 文件同步 v2.11.0 | CHANGELOG/README/TODO/pyproject | ✅ |
| E | 27 | 審計報告 | Sprint24_AuditReport.md | ✅ |
| E | 28 | PROMPT_P25.md | sprints/PROMPT_P25.md | ✅ |

### 未完成項目

| 項目 | 原因 | 解決方案 |
|------|------|----------|
| pytest 驗收 | **OOM: pytest 進程吃 26GB** | 手動診斷 conftest.py + test 檔案 |
| git tag v2.11.0 | 依賴 pytest 通過 | pytest 通過後打 tag |

---

## 4. 🔴 pytest OOM 根因分析

### 事件時間線

| 次數 | 時間 | 現象 | 記憶體 |
|------|------|------|--------|
| 1次 | P24 首次執行 | Claude Code 被 macOS 暫停 | 16GB 耗盡 |
| 2次 | P24 v3.0 重跑 | Part E pytest 卡死 | python 26GB + 5GB |
| 3次 | P24 v4.0 重跑 | tmux session 結束，零通知 | 不明 |
| 4次 | P24 v4.0 再跑 | python 26GB + 18GB | swap 10.77GB |

### 根因

```
pytest 收集 test 檔案時 import PySide6
→ PySide6 建立 QApplication + OpenGL context
→ 每個 test process 吃數 GB 記憶體
→ Claude Code 同時啟動多個 pytest process
→ Mac Mini 16GB 耗盡 → OOM
```

### 已嘗試的解法（無效）

- `export QT_QPA_PLATFORM=offscreen` — 設定了但 pytest 仍然 OOM
- `--ignore=tests/test_gui` — 其他 test 檔案可能也 import PySide6
- `--timeout=10` — 不能阻止記憶體累積

### 建議下一步

```bash
# 1. 手動診斷哪個 test 檔案觸發 PySide6
cd ~/Documents/MyProjects/PromptBIMTestApp1
conda activate promptbim
export QT_QPA_PLATFORM=offscreen

# 2. 逐一跑測試目錄，找出 OOM 元兩
python -m pytest tests/test_ci_cd.py -x --timeout=10 -v
python -m pytest tests/test_bim/ -x --timeout=10 -v
python -m pytest tests/test_demo/ -x --timeout=10 -v
# ... 一個一個測

# 3. 在 conftest.py 頂部加入 PySide6 放空
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
```

---

## 5. 治理框架演進（本次對話完成）

### CLAUDE.md 版本演進

| 版本 | Commit | 核心變更 |
|------|--------|----------|
| v1.17.0 | (前次對話) | Task/Part 雙向通知 + +886972535899 |
| v1.18.0 | `03a81fb` | 🔴 P24a OOM → get_mem + check_mem 記憶體監控 |
| v1.19.0 | `f08002e` | 歷史教訓彙整 + Git 安全(Part commit) + 26步流程 |
| v1.20.0 | `99d2eb1` | 🔴 P24b 殭屍 Python → pkill + QT_QPA_PLATFORM=offscreen + pytest 安全 |
| **v1.21.0** | `e3d1de9` | **🔴 P24d Task 通知被跳過 → task_start/task_done 封裝函數** |

### SKILL.md 版本演進

| 版本 | Commit | 變更 |
|------|--------|------|
| v3.4 | `8acc8bc` | 記憶體監控 |
| v3.5 | `6c12c52` | 教訓 + git 安全 |
| v3.6 | `00286a7` | pytest 安全 (offscreen + pkill) |
| **v3.7** | `0ed952d` | **task_start/task_done enforcement** |

### PROMPT_P24.md 版本演進

| 版本 | Commit | 變更 |
|------|--------|------|
| v2.0 | (原始) | 基本 notify 規則 |
| v3.0 | `c43bba9` | get_mem + check_mem 記憶體監控 |
| **v4.0** | `e3d1de9` | **task_start/task_done 封裝函數，28 個 Task 明確呼叫** |

### 歷史教訓總表

| # | 事故 | 根因 | 規則 | 加入版本 |
|---|------|------|------|----------|
| 🔴 P18 | CLAUDE.md 被截斷 | Claude Code 擅自修改 | 絕對禁止修改治理文件 | v1.14.0 |
| 🔴 P22 | notify 不存在 | `-p` 不載入 .zshrc | PROMPT 顯式定義函數 | v1.16.0 |
| 🔴 P22.1 | 完成但沒 commit | 忘記 git push | Part 結束必須 commit+push | v1.19.0 |
| 🔴 P24a | OOM 靜默中斷 | 16GB RAM 耗盡 | check_mem + <1GB 暫停 | v1.18.0 |
| 🔴 P24b | 殭屍 Python 26GB | pytest GUI 建立 QApplication | pkill + offscreen | v1.20.0 |
| 🔴 P24d | Task 通知被跳過 | Claude Code 只發 Part 通知 | task_start/task_done 封裝 | v1.21.0 |
| 🟧 P24c | Git 遠端分歧 | Claude.ai 同時推 commit | Sprint 前 git pull | v1.19.0 |
| 🟧 P23 | iMessage 要授權 | 第一次需按「允許」 | Sprint 前測試 iMessage | v1.19.0 |

---

## 6. Windows 遷移架構決策

| 項目 | 決策 |
|------|------|
| 方案 | **方案 C: Hydra Storm + PyVista hybrid** |
| GUI | PySide6 (跨平台唯一 GUI) |
| 3D 工程 | PyVista + QVTKOpenGLNativeWidget |
| 3D USD 渲染 | Hydra Storm (pxr.UsdImagingGL) + QOpenGLWidget |
| OpenUSD | usd-core native API (Apache-2.0) |
| C++ | CMake + vcpkg + VS2025 (MSVC) / macOS (Clang) |
| 路線圖 | P24-P29 (macOS) → P30-P31 (Windows) → P32-P33 (Hydra Storm) |

### 已推送的文件

- `docs/Windows_Migration_Plan_v1.0.md` — P24→P33 完整路線圖
- `docs/architecture/v3_architecture.svg` — 系統架構圖
- `docs/architecture/v3_system_design.md` — 系統設計文件
- `docs/DevWindows_Setup.md` — VS2025 開發環境指南
- `docs/WINDOWS_SETUP.md` — 快速環境設定

### 已推送的 Build 環境

- `CMakeLists.txt` + `CMakePresets.json` + `vcpkg.json`
- `cpp/src/compliance_engine.*` + `cost_engine.*`
- `cpp/bindings/pybind_module.cpp`
- `cpp/tests/test_compliance.cpp` (8 tests) + `test_cost.cpp` (6 tests)
- `scripts/setup_windows.ps1` + `build_cpp_windows.ps1`
- `.github/workflows/ci-windows.yml`

---

## 7. 開發環境

| 環境 | 用途 | 狀態 |
|------|------|------|
| Mac Mini M4 (16GB) | Claude Code Sprint 執行 | ✅ 線上 |
| MacBook | Xcode + Claude Desktop | ✅ |
| Windows RTX 4090 | VS2025 + Hydra Storm (P30+) | ⏳ 待設定 |

### Mac Mini 注意事項

- Sprint 期間必須關閉 Chrome/Notion/AnyDesk
- 每次 Sprint 前: `pkill -f "python.*pytest"` + `sudo purge`
- pytest 必須用: `QT_QPA_PLATFORM=offscreen --timeout=10 --ignore=test_gui -x`

---

## 8. 下一步行動

### 立即（明天優先）

1. **手動診斷 pytest OOM** — 找出哪個 test 檔案觸發 PySide6 import
2. **在 conftest.py 頂部加 `os.environ['QT_QPA_PLATFORM'] = 'offscreen'`**
3. **手動跑 pytest 確認通過**
4. **打 tag: `git tag v2.11.0 && git push origin v2.11.0`**

### 後續 Sprint

| Sprint | 內容 | 依賴 |
|--------|------|------|
| P25 | USD 匹出品質強化 | P24 |
| P26-P29 | macOS 功能完善 | P25 |
| P30-P31 | Windows 遷移 | P29 |
| P32-P33 | Hydra Storm + v3.0 | P31 |

---

*docs/PROJECT_STATUS.md | 2026-03-27*
*由 Claude (claude.ai) 在對話中生成*
