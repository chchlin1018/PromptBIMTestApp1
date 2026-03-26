# PromptBIM — Windows 開發環境初始設定 (DevWindows_Setup)

> **版本:** v1.0 | **日期:** 2026-03-26
> **目標 IDE:** Visual Studio 2025 (Community/Professional/Enterprise)
> **目標 GPU:** NVIDIA RTX 4090 (24GB VRAM)
> **OS:** Windows 11

---

## 一、概述

本文件描述如何在 Windows 上從零開始建立 PromptBIM v3.0 的完整開發環境，包含：
- Python 環境（PySide6 GUI + AI Agents + BIM 生成）
- C++ 編譯環境（Visual Studio 2025 + CMake + vcpkg）
- 測試環境（pytest + GoogleTest）
- GPU 渲染環境（Hydra Storm + PyVista/VTK）

---

## 二、前置軟體安裝

### 2.1 Visual Studio 2025

下載: https://visualstudio.microsoft.com/

安裝時勾選 **Workloads**:
- ✅ **Desktop development with C++** （必選）
- ✅ **Python development** （建議）
- ✅ **Linux and embedded development with C++** （選用，跨平台開發）

在 **Individual Components** 中確認勾選:
- ✅ CMake tools for Windows
- ✅ vcpkg package manager
- ✅ MSVC v143+ (或最新版) C++ x64/x86 build tools
- ✅ Windows 11 SDK (latest)
- ✅ C++ AddressSanitizer
- ✅ Google Test Adapter for Visual Studio
- ✅ Ninja build system

### 2.2 Git for Windows
```powershell
winget install Git.Git
# 重要：設定 line ending 為 input（跨平台相容）
git config --global core.autocrlf input
git config --global user.name "Michael Lin"
git config --global user.email "chchlin1018@users.noreply.github.com"
```

### 2.3 Miniconda (Python 3.11)
```powershell
winget install Anaconda.Miniconda3
# 安裝後重啟 PowerShell
conda --version
```

### 2.4 NVIDIA Driver
確認 RTX 4090 driver ≥ 551.78:
```powershell
nvidia-smi
# 應顯示: NVIDIA GeForce RTX 4090, Driver Version: 5xx.xx
```

---

## 三、Clone 專案

```powershell
cd C:\Users\Michael\Documents\MyProjects
git clone https://github.com/chchlin1018/PromptBIMTestApp1.git
cd PromptBIMTestApp1
```

---

## 四、Python 環境設定

### 4.1 建立 conda 環境
```powershell
conda create -n promptbim python=3.11 -y
conda activate promptbim
```

### 4.2 安裝依賴
```powershell
# IfcOpenShell (只有 conda-forge 有 Windows build)
conda install -c conda-forge ifcopenshell -y

# 主要 Python 套件 (含 PySide6, PyVista, anthropic 等)
pip install -e ".[dev]"

# OpenUSD + Hydra Storm 渲染器
pip install usd-core

# asyncio ↔ Qt 事件循環橋接
pip install qasync
```

### 4.3 驗證 Python 環境
```powershell
# 逐一驗證每個關鍵依賴
python -c "import ifcopenshell; print(f'✅ IfcOpenShell {ifcopenshell.version}')"
python -c "from pxr import Usd, UsdImagingGL; print('✅ OpenUSD + Hydra Storm OK')"
python -c "from PySide6.QtWidgets import QApplication; print('✅ PySide6 OK')"
python -c "import pyvista; print(f'✅ PyVista {pyvista.__version__}')"
python -c "import anthropic; print('✅ Anthropic SDK OK')"
python -c "import geopandas; print(f'✅ GeoPandas {geopandas.__version__}')"
python -m promptbim --version
```

### 4.4 一鍵設定（替代方案）
```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1
```

---

## 五、Visual Studio 2025 C++ 專案設定

### 5.1 開啟 CMake 專案

VS 2025 原生支援 CMake 專案，不需要 .sln 檔案。

1. 啟動 Visual Studio 2025
2. **File → Open → CMake...** → 選擇 repo 根目錄的 `CMakeLists.txt`
3. VS 自動偵測 `CMakePresets.json` 並載入 Presets
4. 在工具列選擇 Preset:
   - `windows-debug` — 日常開發（含 AddressSanitizer）
   - `windows-release` — 效能測試
5. **Build → Build All** (Ctrl+Shift+B)

### 5.2 CMake Presets 說明

`CMakePresets.json` 已預設好 VS2025 整合：

| Preset | 用途 | Generator | Build Type |
|--------|------|-----------|-----------|
| `windows-debug` | 日常開發 + 測試 | Ninja | Debug |
| `windows-release` | 效能 + 發佈 | Ninja | Release |
| `macos-debug` | macOS 開發 | Ninja | Debug |
| `macos-release` | macOS 發佈 | Ninja | Release |

### 5.3 vcpkg 依賴自動安裝

首次 Build 時，CMake 會自動透過 vcpkg 安裝:
- `pybind11` — C++ ↔ Python 綁定
- `gtest` — GoogleTest 單元測試
- `nlohmann-json` — JSON 處理

如果 vcpkg 未安裝:
```powershell
git clone https://github.com/microsoft/vcpkg.git C:\vcpkg
C:\vcpkg\bootstrap-vcpkg.bat
# 設定環境變數
[System.Environment]::SetEnvironmentVariable("VCPKG_ROOT", "C:\vcpkg", "User")
# 重啟 VS 或 PowerShell
```

### 5.4 專案結構（VS Solution Explorer 視圖）

```
PromptBIMTestApp1 (CMake)
├── CMake: CMakeLists.txt          ← 根 CMake（VS 自動偵測）
├── CMake: CMakePresets.json       ← Build Presets
├── CMake: vcpkg.json              ← C++ 依賴
│
├── cpp/                           ← C++ Core Library
│   ├── src/
│   │   ├── compliance_engine.h    ← 法規引擎 header
│   │   ├── compliance_engine.cpp  ← 法規引擎實作
│   │   ├── cost_engine.h          ← 成本引擎 header
│   │   └── cost_engine.cpp        ← 成本引擎實作
│   ├── bindings/
│   │   └── pybind_module.cpp      ← Python binding
│   └── tests/
│       ├── test_compliance.cpp    ← GoogleTest (8 tests)
│       └── test_cost.cpp          ← GoogleTest (6 tests)
│
├── src/promptbim/                 ← Python Core（不需要 VS build）
├── tests/                         ← Python Tests（pytest）
└── scripts/
    ├── setup_windows.ps1          ← 環境設定
    └── build_cpp_windows.ps1      ← C++ Build 腳本
```

---

## 六、測試環境

### 6.1 C++ 測試 (GoogleTest + VS Test Explorer)

在 VS 2025 中:
1. Build → Build All
2. Test → Test Explorer (Ctrl+E, T)
3. 應看到 14 個測試:
   - `ComplianceEngineTest.PassingPlan`
   - `ComplianceEngineTest.BcrExceeded`
   - `ComplianceEngineTest.FarExceeded`
   - `ComplianceEngineTest.HeightExceeded`
   - `ComplianceEngineTest.MultipleViolations`
   - `ComplianceEngineTest.NearLimitWarning`
   - `ComplianceEngineTest.ZeroLandArea`
   - `ComplianceEngineTest.Version`
   - `CostEngineTest.ResidentialRC`
   - `CostEngineTest.SteelMoreExpensive`
   - `CostEngineTest.QualityScaling`
   - `CostEngineTest.HeightPremium`
   - `CostEngineTest.ZeroArea`
   - `CostEngineTest.Version`

命令列:
```powershell
cmake --preset windows-debug
cmake --build --preset windows-debug
ctest --preset windows-debug --output-on-failure
```

### 6.2 Python 測試 (pytest)

```powershell
conda activate promptbim
# 全量測試（排除 macOS-specific 和需要 GUI 的）
python -m pytest tests/ --tb=short -q --timeout=10 ^
    --ignore=tests/test_mcp ^
    --ignore=tests/test_gui ^
    -m "not api and not slow and not gui"

# 特定模組
python -m pytest tests/test_bim/ -v
python -m pytest tests/test_land/ -v
python -m pytest tests/test_agents/ -v -m "not api"
```

### 6.3 VS 2025 Python 測試整合

1. Python → Test Explorer → 選擇 pytest
2. 設定 conda interpreter: `C:\Users\Michael\miniconda3\envs\promptbim\python.exe`
3. Test Discovery: `tests/`

---

## 七、GPU 渲染設定

### 7.1 強制 Python 使用 RTX 4090

筆電有雙 GPU 時需要設定:
```powershell
# 方法 A: Windows Settings
# Settings → System → Display → Graphics → 新增 python.exe → High performance

# 方法 B: PowerShell（永久設定）
$pyPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if ($pyPath) {
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\DirectX\UserGpuPreferences" `
        -Name $pyPath -Value "GpuPreference=2;"
    Write-Host "✅ Set $pyPath to use RTX 4090"
}
```

### 7.2 驗證 GPU 加速
```powershell
python -c "
import pyvista
pl = pyvista.Plotter(off_screen=True)
print('GPU:', pl.render_window.ReportCapabilities())
pl.close()
"
```

---

## 八、.env 設定

```powershell
cd PromptBIMTestApp1
copy .env.example .env
# 編輯 .env 填入 API Key:
# ANTHROPIC_API_KEY=sk-ant-api03-...
```

---

## 九、日常開發流程

### 9.1 啟動 GUI
```powershell
conda activate promptbim
cd C:\Users\Michael\Documents\MyProjects\PromptBIMTestApp1
python -m promptbim gui
```

### 9.2 CLI 生成
```powershell
python -m promptbim generate "3-story residential building" -o .\output
# 輸出: output\model.ifc + output\model.usda + output\floorplan.svg
```

### 9.3 usdview 驗證 USD 輸出
```powershell
usdview output\model.usda
```

### 9.4 C++ 修改 → 測試 → Python binding
```powershell
# 修改 cpp/src/*.cpp 後:
cmake --build --preset windows-debug
ctest --preset windows-debug

# 測試 Python binding:
python -c "import promptbim_cpp; print(promptbim_cpp.ComplianceEngine.version())"
```

---

## 十、Troubleshooting

| 問題 | 解法 |
|------|------|
| `conda install ifcopenshell` 失敗 | 用 `conda install -c conda-forge ifcopenshell` |
| VS 找不到 CMakePresets.json | 確認 File → Open → CMake 選的是根目錄 CMakeLists.txt |
| vcpkg 下載逾時 | 設定 `$env:HTTPS_PROXY`，或手動 `vcpkg install pybind11 gtest` |
| `usd-core` 缺少 UsdImagingGL | 確認 `pip install usd-core>=24.0`（舊版不含 Hydra） |
| matplotlib 中文方框 | `pip install matplotlib` 後設定 rcParams 或 bundle NotoSansCJK 字體 |
| pytest 卡在 GUI 測試 | 加 `--timeout=10` 或 `set QT_QPA_PLATFORM=offscreen` |
| CMake 找不到 Python | 在 CMakePresets.json 加 `"Python3_EXECUTABLE": "path/to/python.exe"` |
| GoogleTest 不顯示在 Test Explorer | 確認 VS 安裝了 "Google Test Adapter" 元件 |

---

## 十一、Mac Mini ↔ Windows 協作

```
Mac Mini M4 (macOS)                Windows RTX 4090
┌─────────────────────┐           ┌─────────────────────┐
│ Claude Code Sprint  │  git push │ VS 2025 C++ 開發    │
│ pytest (全量)       │ ←───────→ │ Hydra Storm 渲染    │
│ iMessage notify     │  git pull │ GoogleTest          │
│ CI 觸發            │           │ GPU 效能測試        │
└─────────────────────┘           └─────────────────────┘
```

每次開發前:
```powershell
cd C:\Users\Michael\Documents\MyProjects\PromptBIMTestApp1
git pull origin main
conda activate promptbim
pip install -e ".[dev]"  # 確保最新版本
```

---

*DevWindows_Setup v1.0 | 2026-03-26 | Reality Matrix Inc.*
*Visual Studio 2025 + conda + CMake + vcpkg + RTX 4090*
