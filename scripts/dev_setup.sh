#!/usr/bin/env bash
# dev_setup.sh — Quick-start dev environment setup.
# Usage: ./scripts/dev_setup.sh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🏗️ PromptBIM Dev Environment Setup"
echo "===================================="

# 1. Check conda
if ! command -v conda &>/dev/null; then
    echo "❌ conda not found. Install miniforge first:"
    echo "   brew install miniforge"
    exit 1
fi
echo "✅ conda found: $(conda --version)"

# 2. Create or update conda env
ENV_NAME="promptbim"
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "✅ conda env '${ENV_NAME}' exists"
else
    echo "📦 Creating conda env '${ENV_NAME}'..."
    conda create -n "$ENV_NAME" python=3.11 -y
fi

# 3. Activate and install
echo "📦 Installing Python package (editable + dev extras)..."
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"
pip install -e ".[dev]" 2>/dev/null || pip install -e "."

# 4. Verify key imports
echo "🔍 Verifying key imports..."
python -c "import promptbim; print(f'  promptbim {promptbim.__version__}')"
python -c "import ifcopenshell; print(f'  ifcopenshell OK')" 2>/dev/null || echo "  ⚠️ ifcopenshell not available (install via conda)"
python -c "from pxr import Usd; print(f'  usd-core OK')" 2>/dev/null || echo "  ⚠️ usd-core not available (install via conda)"

# 5. Build C++ library (optional)
if [ -f "$PROJECT_ROOT/libpromptbim/CMakeLists.txt" ]; then
    echo "🔨 Building C++ library..."
    cd "$PROJECT_ROOT/libpromptbim"
    cmake -B build -DCMAKE_BUILD_TYPE=Release -DPROMPTBIM_BUILD_TESTS=ON -DPROMPTBIM_BUILD_PYTHON=OFF 2>/dev/null && \
    cmake --build build --config Release --parallel "$(sysctl -n hw.ncpu 2>/dev/null || echo 4)" && \
    echo "  ✅ C++ build OK" || echo "  ⚠️ C++ build skipped"
    cd "$PROJECT_ROOT"
fi

# 6. Run quick test
echo "🧪 Running quick smoke test..."
python -m pytest tests/ -m "not api and not slow and not integration" --tb=short -q --no-header 2>/dev/null | tail -1

echo ""
echo "✅ Dev environment ready!"
echo "   Activate: conda activate ${ENV_NAME}"
echo "   Run GUI:  python -m promptbim gui"
echo "   Run tests: pytest tests/ -m 'not api'"
