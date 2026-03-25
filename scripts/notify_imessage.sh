#!/bin/bash
# notify_imessage.sh — 透過 iMessage 發送 PromptBIM Sprint 通知
#
# 用法:
#   ./scripts/notify_imessage.sh "✅ Sprint P2.5 完成"
#   ./scripts/notify_imessage.sh "❌ Sprint P2.5 失敗: pytest 3 failed"
#
# Claude Code 在 CLAUDE.md [MANDATORY] 步驟中自動呼叫此腳本
# 需要 Mac Mini 上的 Messages.app 已登入 iCloud

RECIPIENT="chchlin1018@icloud.com"
MESSAGE="${1:-[PromptBIM] 無訊息內容}"
HOSTNAME=$(hostname -s)
TIMESTAMP=$(date '+%m/%d %H:%M')

# 組合完整訊息
FULL_MSG="🏗️ PromptBIM
${MESSAGE}
📍 ${HOSTNAME} | ${TIMESTAMP}"

osascript -e "tell application \"Messages\"
    set targetService to 1st account whose service type = iMessage
    set targetBuddy to participant \"${RECIPIENT}\" of targetService
    send \"${FULL_MSG}\" to targetBuddy
end tell" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "[iMessage] ✅ 通知已發送給 ${RECIPIENT}"
else
    echo "[iMessage] ⚠️ 發送失敗（不影響工作流程）"
fi
