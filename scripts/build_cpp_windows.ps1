# PromptBIM — Windows C++ Build Script (VS2025 + CMake + vcpkg)
# Run: powershell -ExecutionPolicy Bypass -File scripts/build_cpp_windows.ps1

param(
    [string]$Preset = "windows-release",
    [switch]$Clean
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " PromptBIM C++ Build (Windows)" -ForegroundColor Cyan
Write-Host " Preset: $Preset" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check prerequisites
if (-not $env:VCPKG_ROOT) {
    if (Test-Path "C:\vcpkg") {
        $env:VCPKG_ROOT = "C:\vcpkg"
    } else {
        Write-Host "[ERROR] VCPKG_ROOT not set. Install vcpkg:" -ForegroundColor Red
        Write-Host "  git clone https://github.com/microsoft/vcpkg.git C:\vcpkg" -ForegroundColor Yellow
        Write-Host "  C:\vcpkg\bootstrap-vcpkg.bat" -ForegroundColor Yellow
        exit 1
    }
}

if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] cmake not found. Install VS2025 with CMake tools." -ForegroundColor Red
    exit 1
}

# Clean build
if ($Clean -and (Test-Path "build/$Preset")) {
    Write-Host "`n[Clean] Removing build/$Preset..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "build/$Preset"
}

# Configure
Write-Host "`n[1/3] Configuring ($Preset)..." -ForegroundColor Green
cmake --preset $Preset
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Build
Write-Host "`n[2/3] Building..." -ForegroundColor Green
cmake --build --preset $Preset
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Test
Write-Host "`n[3/3] Running tests..." -ForegroundColor Green
ctest --preset $Preset --output-on-failure

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Build complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
