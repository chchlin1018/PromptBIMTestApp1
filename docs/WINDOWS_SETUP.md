# PromptBIM — Windows 開發環境設定指南

> **適用版本:** v3.0-alpha+ | **更新日期:** 2026-03-26
> **需求硬體:** NVIDIA RTX 4090 (24GB VRAM) 或同等
> **OS:** Windows 11

---

## 1. 前置安裝

### 1.1 Visual Studio 2025

下載: https://visualstudio.microsoft.com/

安裝時勾選以下 Workload:
- ✅ **Desktop development with C++**
- ✅ **Python development**
- ✅ **Linux and embedded development with C++** (選用, 跨平台)

個別元件 (Individual Components):
- ✅ CMake tools for Windows
- ✅ vcpkg package manager
- ✅ MSVC v143+ build tools
- ✅ Windows SDK (latest)
- ✅ C++ AddressSanitizer
- ✅ Google Test Adapter

### 1.2 Git
```powershell
winget install Git.Git
git config --global core.autocrlf input
```

### 1.3 Miniconda
```powershell
winget install Anaconda.Miniconda3
# 重新開啟 PowerShell
conda --version
```

### 1.4 NVIDIA Driver
確認 RTX 4090 driver ≥ 551.78:
```powershell
nvidia-smi
```

---

## 2. Python 環境設定

### 2.1 建立 conda 環境
```powershell
conda create -n promptbim python=3.11 -y
conda activate promptbim
```

### 2.2 安裝依賴
```powershell
# BIM 核心 (conda-forge 才有 ifcopenshell Windows build)
conda install -c conda-forge ifcopenshell -y

# Python 套件
pip install -e ".[dev]"

# OpenUSD + Hydra Storm
pip install usd-core

# asyncio ↔ Qt 橋接
pip install qasync

# 或用一鍵腳本:
powershell -ExecutionPolicy Bypass -File scripts/setup_windows.ps1
```

### 2.3 驗證
```powershell
python -c "import ifcopenshell; print(f'IfcOpenShell {ifcopenshell.version}')"
python -c "from pxr import Usd, UsdImagingGL; print('OpenUSD + Hydra Storm OK')"
python -c "from PySide6.QtWidgets import QApplication; print('PySide6 OK')"
python -c "import pyvista; print(f'PyVista {pyvista.__version__}'); print(pyvista.GPUInfo())"
python -m promptbim --version
```

---

## 3. Visual Studio 2025 C++ 專案

### 3.1 開啟專案

VS 2025 原生支援 CMake 專案。兩種方式:

**方式 A: 用 CMakePresets.json (推薦)**
1. File → Open → CMake... → 選擇 repo 根目錄的 `CMakeLists.txt`
2. VS 自動讀取 `CMakePresets.json`
3. 選擇 Preset: `windows-release` 或 `windows-debug`
4. Build → Build All

**方式 B: 命令列**
```powershell
cd PromptBIMTestApp1
cmake --preset windows-release
cmake --build --preset windows-release
ctest --preset windows-release
```

### 3.2 vcpkg 依賴
首次 build 時，CMake 會自動透過 vcpkg 安裝:
- pybind11
- gtest
- nlohmann-json

如果 vcpkg 未安裝:
```powershell
git clone https://github.com/microsoft/vcpkg.git C:\vcpkg
C:\vcpkg\bootstrap-vcpkg.bat
set VCPKG_ROOT=C:\vcpkg
```

### 3.3 GoogleTest 整合
VS 2025 的 Test Explorer 自動偵測 GoogleTest:
1. Build C++ project
2. Test → Test Explorer
3. 應看到 `ComplianceEngineTest.*` 和 `CostEngineTest.*`

---

## 4. 測試

### 4.1 Python 測試 (pytest)
```powershell
conda activate promptbim
python -m pytest tests/ --tb=short -q --timeout=10 --ignore=tests/test_mcp
```

### 4.2 C++ 測試 (GoogleTest)
```powershell
cmake --preset windows-debug
cmake --build --preset windows-debug
ctest --preset windows-debug --output-on-failure
```

### 4.3 全量測試
```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_cpp_windows.ps1
```

---

## 5. 執行

### 5.1 GUI 模式
```powershell
conda activate promptbim
python -m promptbim gui
```

### 5.2 CLI 模式
```powershell
python -m promptbim generate "3-story residential building" -o ./output
```

### 5.3 usdview 驗證
```powershell
# usdview 隨 usd-core 安裝
usdview output/model.usda
```

---

## 6. GPU 設定

### 6.1 強制使用 RTX 4090
如果筆電有雙 GPU，強制指定:
```powershell
# Windows Settings → System → Display → Graphics
# 新增 python.exe → High performance

# 或用 PowerShell:
$pythonPath = (Get-Command python).Source
Set-ItemProperty -Path "HKCU:\Software\Microsoft\DirectX\UserGpuPreferences" -Name $pythonPath -Value "GpuPreference=2;"
```

### 6.2 驗證 GPU
```powershell
python -c "
import pyvista
pl = pyvista.Plotter(off_screen=True)
print(pl.render_window.ReportCapabilities())
pl.close()
"
```

---

## 7. 已知問題

| 問題 | 解法 |
|------|------|
| IfcOpenShell pip 安裝失敗 | 用 `conda install -c conda-forge ifcopenshell` |
| usd-core 缺 UsdImagingGL | pip wheel 包含; 確認 `pip install usd-core` ≥24.0 |
| matplotlib CJK 字體方框 | `pip install matplotlib` 後設定 `rcParams['font.sans-serif']` |
| pytest GUI 測試卡住 | 加 `--timeout=10` 或 `QT_QPA_PLATFORM=offscreen` |
| VS 2025 找不到 Python | 在 CMakePresets.json 設定 `PYTHON_EXECUTABLE` |

---

*Windows Setup Guide v1.0 | 2026-03-26*
