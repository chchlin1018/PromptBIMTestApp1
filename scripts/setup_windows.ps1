# PromptBIM — Windows Environment Setup Script
# Run: powershell -ExecutionPolicy Bypass -File scripts/setup_windows.ps1

param(
    [switch]$SkipGPU,
    [string]$EnvName = "promptbim"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " PromptBIM Windows Setup" -ForegroundColor Cyan
Write-Host " v4.0 — P25 Performance + Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Check conda
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] conda not found. Install Miniconda first." -ForegroundColor Red
    Write-Host "  winget install Anaconda.Miniconda3" -ForegroundColor Yellow
    exit 1
}

# 2. Create conda env
Write-Host "`n[1/7] Creating conda environment '$EnvName'..." -ForegroundColor Green
conda create -n $EnvName python=3.11 -y
conda activate $EnvName

# 3. Install ifcopenshell from conda-forge
Write-Host "`n[2/7] Installing IfcOpenShell..." -ForegroundColor Green
conda install -c conda-forge ifcopenshell -y

# 4. Install Python packages
Write-Host "`n[3/7] Installing Python packages..." -ForegroundColor Green
pip install -e ".[dev]"
pip install usd-core qasync pytest-timeout

# 5. Set environment variables for headless testing
Write-Host "`n[4/7] Setting environment variables..." -ForegroundColor Green
$env:QT_QPA_PLATFORM = "offscreen"
Write-Host "  QT_QPA_PLATFORM=offscreen"

# 6. Verify Python env
Write-Host "`n[5/7] Verifying Python environment..." -ForegroundColor Green
$checks = @(
    @{ Module = "ifcopenshell"; Cmd = "import ifcopenshell; print(f'  IfcOpenShell {ifcopenshell.version}')" },
    @{ Module = "pxr"; Cmd = "from pxr import Usd; print('  OpenUSD OK')" },
    @{ Module = "PySide6"; Cmd = "import os; os.environ['QT_QPA_PLATFORM']='offscreen'; from PySide6.QtWidgets import QApplication; print('  PySide6 OK')" },
    @{ Module = "pyvista"; Cmd = "import pyvista; print(f'  PyVista {pyvista.__version__}')" },
    @{ Module = "anthropic"; Cmd = "import anthropic; print('  Anthropic SDK OK')" },
    @{ Module = "pytest"; Cmd = "import pytest; print(f'  pytest {pytest.__version__}')" }
)

$failed = 0
foreach ($check in $checks) {
    try {
        python -c $check.Cmd
    } catch {
        Write-Host "  [FAIL] $($check.Module)" -ForegroundColor Red
        $failed++
    }
}

# 7. GPU check (optional)
if (-not $SkipGPU) {
    Write-Host "`n[6/7] Checking GPU..." -ForegroundColor Green
    try {
        nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    } catch {
        Write-Host "  [WARN] nvidia-smi not found (GPU optional)" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[6/7] Skipping GPU check (--SkipGPU)" -ForegroundColor Yellow
}

# 8. Run quick smoke test
Write-Host "`n[7/7] Running smoke test..." -ForegroundColor Green
try {
    python -m pytest tests/test_integration/test_smoke.py -x --timeout=10 -q 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Smoke test PASSED" -ForegroundColor Green
    } else {
        Write-Host "  Smoke test failed (non-critical)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Smoke test skipped" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
if ($failed -eq 0) {
    Write-Host " Setup complete! All checks passed." -ForegroundColor Green
} else {
    Write-Host " Setup complete with $failed warning(s)." -ForegroundColor Yellow
}
Write-Host " Run: python -m promptbim gui" -ForegroundColor Cyan
Write-Host " Test: python -m pytest tests/ --timeout=10 -x -q" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
