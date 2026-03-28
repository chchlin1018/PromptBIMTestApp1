# Zigma — Windows 環境 Checklist v1.0

> **日期:** 2026-03-28 | **機器:** RTX 4090 | Windows 11

---

## 硬體
- [ ] GPU: NVIDIA RTX 4090
- [ ] RAM: ≥32GB
- [ ] SSD ≥100GB free

## OS + Driver
- [ ] Windows 11（最新）
- [ ] NVIDIA Driver ≥550.x → `nvidia-smi` 驗證
- [ ] Vulkan SDK 1.3+（選用，D3D12 預設）

## Visual Studio 2022
- [ ] 下載: https://visualstudio.microsoft.com/
- [ ] 勾選: Desktop C++ / CMake tools / Win11 SDK / MSVC v143 x64
- [ ] 驗證: x64 Native Tools Command Prompt → `cl`

## CMake ≥3.21
- [ ] `cmake --version`

## Qt 6.7+ (Quick3D)
- [ ] Qt Online Installer → MSVC 2022 64-bit + **Quick3D** + **ShaderTools**
- [ ] 路徑: `C:\Qt\6.7.x\msvc2022_64\`
- [ ] 驗證: `dir C:\Qt\6.7*\msvc2022_64\lib\cmake\Qt6Quick3D\`

## Python 3.11
- [ ] `conda create -n promptbim python=3.11 -y && pip install anthropic pydantic aiohttp`

## Git
- [ ] Git for Windows → clone repo

## iCloud Drive
- [ ] iCloud for Windows (Microsoft Store) → 勾 iCloud Drive
- [ ] `%USERPROFILE%\iCloudDrive\ZigmaMedia\` 存在
- [ ] 離線存取: 右鍵 →「始終保留在此裝置上」
- [ ] symlink: `mklink /D C:\ZigmaMedia "%USERPROFILE%\iCloudDrive\ZigmaMedia"`

## 環境變數
```
QT_DIR = C:\Qt\6.7.x\msvc2022_64
CMAKE_PREFIX_PATH = C:\Qt\6.7.x\msvc2022_64
QSG_RHI_BACKEND = d3d12
PATH += C:\Qt\6.7.x\msvc2022_64\bin
```

## VS Solution 建立
```cmd
cd zigma
cmake -B build-vs -G "Visual Studio 17 2022" -A x64 ^
  -DCMAKE_PREFIX_PATH="C:\Qt\6.7.x\msvc2022_64" ^
  -DZIGMA_MEDIA_PATH="C:\ZigmaMedia"
```
- [ ] 開啟 `build-vs\Zigma.sln`
- [ ] Set `zigma` as Startup Project
- [ ] Configuration: Release
- [ ] Debugging → Working Directory: `$(ProjectDir)..\..\`
- [ ] Debugging → Environment: `QSG_RHI_BACKEND=d3d12`
- [ ] F5 → Build + Run

## Build 驗證 (alpha 後)
- [ ] GUI 三欄佈局 ✅
- [ ] 3D View3D (D3D12) ✅
- [ ] FPS ≥ 30 ✅
- [ ] 記憶體 < 500MB ✅

## Phase 2 額外
- [ ] P30: Revit 2026 + `pip install usd-core`
- [ ] P31: `vcpkg install opencascade:x64-windows`

## 驗證腳本 (PowerShell)
```powershell
Write-Host "===== Zigma Windows Preflight =====" -ForegroundColor Cyan
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>$null
if ($?) { Write-Host "✅ GPU" -ForegroundColor Green } else { Write-Host "❌ GPU" -ForegroundColor Red }
$cl = Get-Command cl.exe -EA SilentlyContinue
if ($cl) { Write-Host "✅ MSVC" -ForegroundColor Green } else { Write-Host "❌ MSVC" -ForegroundColor Red }
cmake --version 2>$null | Select -First 1
$qt = Get-ChildItem "C:\Qt\6.*\msvc2022_64\lib\cmake\Qt6Quick3D" -EA SilentlyContinue
if ($qt) { Write-Host "✅ Qt6 Quick3D" -ForegroundColor Green } else { Write-Host "❌ Qt6" -ForegroundColor Red }
$m = "$env:USERPROFILE\iCloudDrive\ZigmaMedia"
if (Test-Path $m) { Write-Host "✅ iCloud" -ForegroundColor Green } else { Write-Host "⚠️ iCloud" -ForegroundColor Yellow }
Write-Host "===== Done =====" -ForegroundColor Cyan
```

## 優先級
| 時間 | 必裝 |
|------|------|
| alpha 後 | VS2022 + CMake + Qt6 + Git + iCloud |
| beta 後 | + NVIDIA Driver 550+ |
| P30 | + Revit 2026 + Python |
| P31 | + vcpkg + OCCT |

---
*Windows Checklist v1.0 | 2026-03-28*
