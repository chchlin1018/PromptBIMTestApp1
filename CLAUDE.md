# CLAUDE.md — Claude Code 自動開發指引

> **版本:** v1.14.0 | **更新:** 2026-03-26
> **版本控制:** 本文件由人工維護，Claude Code 不得直接修改
> ⚠️ 本文件中標記為 **[MANDATORY]** 的規則必須嚴格執行，不得跳過

---

## [MANDATORY] 跨機器環境檢查（含 API Key 衝突檢查）

> ⚠️ **每次 Sprint 開始前，必須先檢查執行環境。**
> ⚠️ **如果偵測到 ANTHROPIC_API_KEY，必須停止 Sprint 並通知用戶。**

### 環境檢查腳本

```bash
echo "========================================"
echo "🖥️  環境檢查 — $(hostname)"
echo "========================================"
echo "Hostname: $(hostname)"
echo "macOS: $(sw_vers -productVersion)"
echo "Git: $(git --version 2>/dev/null || echo '❌')"
echo "Xcode: $(xcodebuild -version 2>/dev/null | head -1 || echo '❌')"
echo "Python: $(python3 --version 2>/dev/null || echo '❌')"
echo "Conda: $(conda --version 2>/dev/null || echo '❌')"

# ★ API Key 衝突檢查 ★
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "⛔ ANTHROPIC_API_KEY 已設定！會走 API 計費而非 Max 訂閱"
    echo "🔧 修復: unset ANTHROPIC_API_KEY"
    notify "⛔ PromptBIM Sprint 中止 — 偵測到 ANTHROPIC_API_KEY，請 unset"
    exit 1
fi
echo "✅ 認證: Claude Max 訂閱（無 API Key 衝突）"

git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then echo "✅ 本地與遠端同步"
else echo "⚠️ 執行 git pull..."; git pull origin main; fi
```

（其餘 CLAUDE.md 內容不變，僅環境檢查段落更新）

*CLAUDE.md v1.14.0 | 2026-03-26 | 變更: 環境檢查加入 ANTHROPIC_API_KEY 衝突偵測*
