#!/bin/bash
# PromptBIM 關鍵文件完整性檢查
# 用法: bash scripts/backup_verify.sh
# 建議: 每次 Sprint 前後執行

echo "========================================"
echo "🛡️  關鍵文件完整性檢查"
echo "========================================"

FAILED=0

# CLAUDE.md 檢查
CLAUDE_SIZE=$(wc -c < CLAUDE.md 2>/dev/null | tr -d ' ')
if [ -z "$CLAUDE_SIZE" ] || [ "$CLAUDE_SIZE" -lt 5000 ]; then
    echo "❌ CLAUDE.md 異常！大小: ${CLAUDE_SIZE:-missing} bytes (應 >= 5000)"
    echo "   恢復: git checkout e74cdc0 -- CLAUDE.md"
    FAILED=1
else
    echo "✅ CLAUDE.md: ${CLAUDE_SIZE} bytes"
fi

# SKILL.md 檢查
SKILL_SIZE=$(wc -c < SKILL.md 2>/dev/null | tr -d ' ')
if [ -z "$SKILL_SIZE" ] || [ "$SKILL_SIZE" -lt 20000 ]; then
    echo "❌ SKILL.md 異常！大小: ${SKILL_SIZE:-missing} bytes (應 >= 20000)"
    echo "   恢復: git checkout 15fc0efe -- SKILL.md"
    FAILED=1
else
    echo "✅ SKILL.md: ${SKILL_SIZE} bytes"
fi

# TODO.md 檢查
TODO_SIZE=$(wc -c < TODO.md 2>/dev/null | tr -d ' ')
if [ -z "$TODO_SIZE" ] || [ "$TODO_SIZE" -lt 10000 ]; then
    echo "⚠️  TODO.md 可能異常: ${TODO_SIZE:-missing} bytes (應 >= 10000)"
else
    echo "✅ TODO.md: ${TODO_SIZE} bytes"
fi

# CHANGELOG.md 檢查
CHANGELOG_SIZE=$(wc -c < CHANGELOG.md 2>/dev/null | tr -d ' ')
if [ -z "$CHANGELOG_SIZE" ] || [ "$CHANGELOG_SIZE" -lt 10000 ]; then
    echo "⚠️  CHANGELOG.md 可能異常: ${CHANGELOG_SIZE:-missing} bytes (應 >= 10000)"
else
    echo "✅ CHANGELOG.md: ${CHANGELOG_SIZE} bytes"
fi

echo "========================================"
if [ $FAILED -eq 0 ]; then
    echo "✅ 所有關鍵文件完整"
else
    echo "❌ 有文件異常！請按上述指令恢復"
    echo "詳細說明: docs/backups/README.md"
fi
exit $FAILED
