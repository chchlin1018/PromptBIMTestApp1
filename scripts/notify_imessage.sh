#!/bin/bash
# notify_imessage.sh — 透過觸發檔 + LaunchAgent 發送 iMessage
# Claude Code 在 SSH/tmux 中呼叫此腳本，寫入觸發檔
# LaunchAgent (com.michael.promptbim-notify) 偵測到檔案後發送 iMessage
HOSTNAME=$(hostname -s)
TIMESTAMP=$(date '+%m/%d %H:%M')
MESSAGE="${1:-[PromptBIM] 無訊息內容}"

echo "🏗️ PromptBIM
${MESSAGE}
📍 ${HOSTNAME} | ${TIMESTAMP}" > /tmp/promptbim_notify.txt

echo "[iMessage] ✅ 通知觸發檔已寫入"
