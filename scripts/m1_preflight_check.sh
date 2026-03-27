#!/bin/bash
# ============================================================
# Zigma M1 MVP Sprint — Pre-flight Environment Check
# ============================================================
# 用途: 在 Mac Mini 上執行 M1 Sprint 前驗證所有必要環境
# 執行: chmod +x scripts/m1_preflight_check.sh && ./scripts/m1_preflight_check.sh
# 全部 ✅ 才能開始 Sprint
# ============================================================

set -e

PASS=0
FAIL=0
WARN=0

check_pass() { echo "  ✅ $1"; PASS=$((PASS+1)); }
check_fail() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
check_warn() { echo "  ⚠️  $1"; WARN=$((WARN+1)); }

echo ""
echo "══════════════════════════════════════════════════════"
echo "  Zigma M1 MVP Sprint — Pre-flight Check"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Host: $(hostname -s) | $(uname -m)"
echo "══════════════════════════════════════════════════════"
echo ""

# ──────────────────────────────────────────────────────
# 1. 系統基礎
# ──────────────────────────────────────────────────────
echo "[1/9] 系統基礎"

# macOS version
OS_VER=$(sw_vers -productVersion 2>/dev/null || echo "unknown")
echo "  macOS: $OS_VER"

# RAM
TOTAL_RAM_GB=$(sysctl -n hw.memsize 2>/dev/null | awk '{printf "%.0f", $1/1073741824}')
FREE_PAGES=$(vm_stat 2>/dev/null | awk '/Pages free/{gsub(/\./,"");print $3}')
INACTIVE_PAGES=$(vm_stat 2>/dev/null | awk '/Pages inactive/{gsub(/\./,"");print $3}')
PAGE_SIZE=$(sysctl -n hw.pagesize 2>/dev/null || echo 4096)
FREE_GB=$(echo "scale=1;(${FREE_PAGES:-0}+${INACTIVE_PAGES:-0})*$PAGE_SIZE/1073741824" | bc 2>/dev/null || echo "?")
if [ "$TOTAL_RAM_GB" -ge 16 ] 2>/dev/null; then
    check_pass "RAM: ${TOTAL_RAM_GB}GB total, ${FREE_GB}GB free"
else
    check_fail "RAM: ${TOTAL_RAM_GB}GB total (需要 ≥16GB)"
fi

# Disk space
FREE_DISK=$(df -g / | awk 'NR==2{print $4}')
if [ "$FREE_DISK" -ge 20 ] 2>/dev/null; then
    check_pass "Disk: ${FREE_DISK}GB free"
else
    check_fail "Disk: ${FREE_DISK}GB free (需要 ≥20GB for Qt + build)"
fi

# ──────────────────────────────────────────────────────
# 2. C++ 工具鏈
# ──────────────────────────────────────────────────────
echo ""
echo "[2/9] C++ 工具鏈"

# Xcode CLI
if xcode-select -p &>/dev/null; then
    XCODE_PATH=$(xcode-select -p)
    check_pass "Xcode CLI Tools: $XCODE_PATH"
else
    check_fail "Xcode CLI Tools 未安裝 → xcode-select --install"
fi

# clang++
if command -v clang++ &>/dev/null; then
    CLANG_VER=$(clang++ --version 2>/dev/null | head -1)
    check_pass "clang++: $CLANG_VER"
else
    check_fail "clang++ 未找到"
fi

# CMake
if command -v cmake &>/dev/null; then
    CMAKE_VER=$(cmake --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    CMAKE_MAJOR=$(echo $CMAKE_VER | cut -d. -f1)
    CMAKE_MINOR=$(echo $CMAKE_VER | cut -d. -f2)
    if [ "$CMAKE_MAJOR" -ge 3 ] && [ "$CMAKE_MINOR" -ge 21 ] 2>/dev/null; then
        check_pass "CMake: $CMAKE_VER (≥3.21)"
    else
        check_fail "CMake: $CMAKE_VER (需要 ≥3.21) → brew install cmake"
    fi
else
    check_fail "CMake 未安裝 → brew install cmake"
fi

# Ninja (optional)
if command -v ninja &>/dev/null; then
    check_pass "Ninja: $(ninja --version)"
else
    check_warn "Ninja 未安裝 (可選，用 make 也行) → brew install ninja"
fi

# ──────────────────────────────────────────────────────
# 3. Qt 6 + Quick3D (最關鍵)
# ──────────────────────────────────────────────────────
echo ""
echo "[3/9] Qt 6 + Quick3D ★ 最關鍵"

QT_FOUND=0
QT_DIR=""

# 方法 1: Qt Online Installer (~/Qt/6.x.x/macos/)
for d in ~/Qt/6.*/macos; do
    if [ -d "$d/lib/cmake/Qt6Quick3D" ]; then
        QT_DIR="$d"
        QT_FOUND=1
        break
    fi
done

# 方法 2: Homebrew
if [ $QT_FOUND -eq 0 ] && command -v brew &>/dev/null; then
    BREW_QT=$(brew --prefix qt@6 2>/dev/null || brew --prefix qt 2>/dev/null || echo "")
    if [ -n "$BREW_QT" ] && [ -d "$BREW_QT/lib/cmake/Qt6Quick3D" ]; then
        QT_DIR="$BREW_QT"
        QT_FOUND=1
    fi
fi

# 方法 3: 系統 PATH
if [ $QT_FOUND -eq 0 ]; then
    QMAKE_PATH=$(command -v qmake6 2>/dev/null || command -v qmake 2>/dev/null || echo "")
    if [ -n "$QMAKE_PATH" ]; then
        QT_PREFIX=$($QMAKE_PATH -query QT_INSTALL_PREFIX 2>/dev/null || echo "")
        if [ -n "$QT_PREFIX" ] && [ -d "$QT_PREFIX/lib/cmake/Qt6Quick3D" ]; then
            QT_DIR="$QT_PREFIX"
            QT_FOUND=1
        fi
    fi
fi

if [ $QT_FOUND -eq 1 ]; then
    QT_VER=$(ls "$QT_DIR/lib/cmake/Qt6/" 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "?")
    check_pass "Qt6 found: $QT_DIR (v$QT_VER)"
    
    # 檢查必要模組
    REQUIRED_MODULES=("Qt6Core" "Qt6Gui" "Qt6Qml" "Qt6Quick" "Qt6Quick3D" "Qt6ShaderTools")
    for mod in "${REQUIRED_MODULES[@]}"; do
        if [ -d "$QT_DIR/lib/cmake/$mod" ]; then
            check_pass "$mod"
        else
            check_fail "$mod 缺失 — 重新安裝 Qt 並勾選此模組"
        fi
    done
else
    check_fail "Qt6 未找到 — 需要安裝 Qt 6.7+ (含 Quick3D)"
    check_fail "  方法A: Qt Online Installer → https://www.qt.io/download-qt-installer-oss"
    check_fail "  方法B: brew install qt@6"
    echo ""
    echo "  ★ Qt Online Installer 安裝時必須勾選:"
    echo "    □ Qt 6.7.x → macOS"
    echo "    □ Qt Quick 3D"
    echo "    □ Qt Shader Tools"
fi

# ──────────────────────────────────────────────────────
# 4. Python promptbim 環境
# ──────────────────────────────────────────────────────
echo ""
echo "[4/9] Python promptbim 環境"

if command -v conda &>/dev/null; then
    check_pass "conda: $(conda --version 2>/dev/null)"
else
    check_fail "conda 未安裝"
fi

# 檢查 promptbim env
if conda env list 2>/dev/null | grep -q promptbim; then
    check_pass "conda env 'promptbim' 存在"
    
    # Python version
    PY_VER=$(conda run -n promptbim python --version 2>/dev/null || echo "unknown")
    check_pass "Python: $PY_VER"
    
    # 必要 packages
    REQUIRED_PY=("anthropic" "pydantic" "aiohttp")
    for pkg in "${REQUIRED_PY[@]}"; do
        if conda run -n promptbim python -c "import $pkg" 2>/dev/null; then
            check_pass "Python: $pkg"
        else
            check_fail "Python: $pkg 未安裝 → conda run -n promptbim pip install $pkg"
        fi
    done
    
    # pxr (USD) — M1-S3 需要，M1-S1/S2 不需要
    if conda run -n promptbim python -c "from pxr import Usd" 2>/dev/null; then
        check_pass "Python: pxr (USD) — M1-S3 io_usd 需要"
    else
        check_warn "Python: pxr (USD) 未安裝 — M1-S3 才需要，可稍後安裝"
    fi
else
    check_fail "conda env 'promptbim' 不存在 → conda create -n promptbim python=3.11"
fi

# ──────────────────────────────────────────────────────
# 5. ANTHROPIC_API_KEY
# ──────────────────────────────────────────────────────
echo ""
echo "[5/9] API Key"

# 檢查 .env 檔案
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_DIR/.env" ]; then
    if grep -q "ANTHROPIC_API_KEY" "$PROJECT_DIR/.env"; then
        check_pass "ANTHROPIC_API_KEY in .env"
    else
        check_fail "ANTHROPIC_API_KEY 不在 .env 中"
    fi
else
    # 檢查環境變數
    if [ -n "$ANTHROPIC_API_KEY" ]; then
        check_pass "ANTHROPIC_API_KEY 在環境變數中"
    else
        check_fail "ANTHROPIC_API_KEY 未設定 — 需要在 .env 或環境變數中"
    fi
fi

if [ -f "$PROJECT_DIR/.env" ] && grep -q "API_TIMEOUT_SECONDS" "$PROJECT_DIR/.env"; then
    TIMEOUT=$(grep API_TIMEOUT_SECONDS "$PROJECT_DIR/.env" | cut -d= -f2)
    check_pass "API_TIMEOUT_SECONDS=$TIMEOUT"
else
    check_warn "API_TIMEOUT_SECONDS 未設定 (建議 120)"
fi

# ──────────────────────────────────────────────────────
# 6. Git 狀態
# ──────────────────────────────────────────────────────
echo ""
echo "[6/9] Git 狀態"

cd "$PROJECT_DIR" 2>/dev/null || cd ~/Documents/MyProjects/PromptBIMTestApp1 2>/dev/null || true

if git rev-parse --is-inside-work-tree &>/dev/null; then
    BRANCH=$(git branch --show-current)
    HEAD=$(git rev-parse --short HEAD)
    check_pass "Git repo: branch=$BRANCH HEAD=$HEAD"
    
    # 檢查是否乾淨
    if [ -z "$(git status --porcelain)" ]; then
        check_pass "Working tree 乾淨"
    else
        check_warn "Working tree 有未提交的變更"
        git status --short | head -5
    fi
    
    # 檢查與 remote 同步
    git fetch origin main --quiet 2>/dev/null
    LOCAL=$(git rev-parse HEAD 2>/dev/null)
    REMOTE=$(git rev-parse origin/main 2>/dev/null)
    if [ "$LOCAL" = "$REMOTE" ]; then
        check_pass "與 origin/main 同步"
    else
        check_warn "與 origin/main 不同步 → git pull origin main"
    fi
else
    check_fail "不在 Git repo 中"
fi

# ──────────────────────────────────────────────────────
# 7. 治理文件
# ──────────────────────────────────────────────────────
echo ""
echo "[7/9] 治理文件"

for f in CLAUDE.md SKILL.md PROJECT.md; do
    if [ -f "$PROJECT_DIR/$f" ]; then
        SIZE=$(wc -c < "$PROJECT_DIR/$f" | tr -d ' ')
        check_pass "$f (${SIZE}B)"
    else
        check_fail "$f 不存在"
    fi
done

# CLAUDE.md ≥5000B
CLAUDE_SIZE=$(wc -c < "$PROJECT_DIR/CLAUDE.md" 2>/dev/null | tr -d ' ')
if [ "${CLAUDE_SIZE:-0}" -ge 5000 ] 2>/dev/null; then
    check_pass "CLAUDE.md ≥5000B ($CLAUDE_SIZE)"
else
    check_fail "CLAUDE.md 太小 ($CLAUDE_SIZE) — 可能被截斷"
fi

# SKILL.md ≥20000B  
SKILL_SIZE=$(wc -c < "$PROJECT_DIR/SKILL.md" 2>/dev/null | tr -d ' ')
if [ "${SKILL_SIZE:-0}" -ge 15000 ] 2>/dev/null; then
    check_pass "SKILL.md ≥15000B ($SKILL_SIZE)"
else
    check_fail "SKILL.md 太小 ($SKILL_SIZE) — 可能被截斷"
fi

# ──────────────────────────────────────────────────────
# 8. 既有 AI 引擎驗證
# ──────────────────────────────────────────────────────
echo ""
echo "[8/9] 既有 AI 引擎"

# 檢查 Python source 存在
for d in src/promptbim/agents src/promptbim/bim/cost src/promptbim/bim/simulation src/promptbim/codes; do
    if [ -d "$PROJECT_DIR/$d" ]; then
        FILE_COUNT=$(find "$PROJECT_DIR/$d" -name '*.py' | wc -l | tr -d ' ')
        check_pass "$d/ ($FILE_COUNT .py files)"
    else
        check_warn "$d/ 不存在"
    fi
done

# 快速 import 測試 (不跑完整 pytest，只確認能 import)
if conda run -n promptbim python -c "
import sys
sys.path.insert(0, '$PROJECT_DIR/src')
from promptbim.agents.orchestrator import Orchestrator
print('Orchestrator import OK')
" 2>/dev/null; then
    check_pass "Python AI 引擎 import OK"
else
    check_warn "Python AI 引擎 import 失敗 — Sprint 中會修復"
fi

# ──────────────────────────────────────────────────────
# 9. 殭屍進程 & 記憶體
# ──────────────────────────────────────────────────────
echo ""
echo "[9/9] 殭屍進程 & 記憶體"

# 殭屍 Python
ZOMBIE_PY=$(pgrep -f "python.*pytest" 2>/dev/null | wc -l | tr -d ' ')
ZOMBIE_PB=$(pgrep -f "python.*promptbim" 2>/dev/null | wc -l | tr -d ' ')
ZOMBIE_QT=$(pgrep -f "python.*PySide6" 2>/dev/null | wc -l | tr -d ' ')

if [ "$ZOMBIE_PY" -gt 0 ] || [ "$ZOMBIE_PB" -gt 0 ] || [ "$ZOMBIE_QT" -gt 0 ]; then
    check_warn "殭屍 Python 進程: pytest=$ZOMBIE_PY promptbim=$ZOMBIE_PB PySide6=$ZOMBIE_QT"
    echo "  → Sprint 啟動時會自動清理"
else
    check_pass "無殭屍 Python 進程"
fi

# 記憶體
if [ "$(echo "${FREE_GB:-0} < 2.0" | bc 2>/dev/null)" = "1" ]; then
    check_warn "可用記憶體偏低 (${FREE_GB}GB) — Sprint 前建議重啟或 sudo purge"
else
    check_pass "可用記憶體: ${FREE_GB}GB"
fi

# ──────────────────────────────────────────────────────
# 總結
# ──────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo "  結果: ✅ $PASS pass | ❌ $FAIL fail | ⚠️  $WARN warn"
echo "══════════════════════════════════════════════════════"

if [ $FAIL -eq 0 ]; then
    echo ""
    echo "  🟢 全部通過！可以開始 M1 MVP Sprint"
    echo ""
    echo "  QT_DIR=$QT_DIR"
    echo ""
    echo "  下一步:"
    echo "  MikeRunClaudeSafe PromptBIMTestApp1 M1-MVP \"...\" --conda promptbim --kill"
    echo ""
else
    echo ""
    echo "  🔴 有 $FAIL 項失敗，請先修復再開始 Sprint"
    echo ""
    if [ $QT_FOUND -eq 0 ]; then
        echo "  ★ 最重要: 安裝 Qt 6.7+ (含 Quick3D)"
        echo "    → https://www.qt.io/download-qt-installer-oss"
        echo "    → 安裝時勾選: Qt Quick 3D + Qt Shader Tools"
        echo ""
    fi
fi

exit $FAIL
