# PromptBIM — Windows Environment Setup Script
# Run: powershell -ExecutionPolicy Bypass -File scripts/setup_windows.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " PromptBIM Windows Setup" -ForegroundColor Cyan
Write-Host " v3.0 — Hydra Storm + PyVista" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Check conda
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] conda not found. Install Miniconda first." -ForegroundColor Red
    Write-Host "  winget install Anaconda.Miniconda3" -ForegroundColor Yellow
    exit 1
}

# 2. Create conda env
Write-Host "`n[1/6] Creating conda environment..." -ForegroundColor Green
conda create -n promptbim python=3.11 -y
conda activate promptbim

# 3. Install ifcopenshell from conda-forge
Write-Host "`n[2/6] Installing IfcOpenShell..." -ForegroundColor Green
conda install -c conda-forge ifcopenshell -y

# 4. Install Python packages
Write-Host "`n[3/6] Installing Python packages..." -ForegroundColor Green
pip install -e ".[dev]"
pip install usd-core qasync

# 5. Verify Python env
Write-Host "`n[4/6] Verifying Python environment..." -ForegroundColor Green
python -c "import ifcopenshell; print(f'  IfcOpenShell {ifcopenshell.version}')"
python -c "from pxr import Usd; print(f'  OpenUSD OK')"
python -c "from PySide6.QtWidgets import QApplication; print('  PySide6 OK')"
python -c "import pyvista; print(f'  PyVista {pyvista.__version__}')"
python -c "import anthropic; print('  Anthropic SDK OK')"

# 6. GPU check
Write-Host "`n[5/6] Checking GPU..." -ForegroundColor Green
try {
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
} catch {
    Write-Host "  [WARN] nvidia-smi not found" -ForegroundColor Yellow
}
python -c "import pyvista; print('  GPU:', pyvista.GPUInfo())"

# 7. Version check
Write-Host "`n[6/6] Final verification..." -ForegroundColor Green
python -m promptbim --version

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Setup complete!" -ForegroundColor Cyan
Write-Host " Run: python -m promptbim gui" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
