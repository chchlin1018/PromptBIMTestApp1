#!/bin/bash
# notify_imessage.sh — 透過全域 notify 命令發送 iMessage
# 原理: notify 寫入 /tmp/imessage_notify.txt → LaunchAgent 偵測 → osascript 發送
#
# 用法:
#   ./scripts/notify_imessage.sh "✅ Sprint P4 完成"
#   notify "任意訊息"   ← 全域命令也可直接用

HOSTNAME=$(hostname -s)
TIMESTAMP=$(date '+%m/%d %H:%M')
MESSAGE="${1:-[PromptBIM] 無訊息內容}"

FULL_MSG="🏗️ PromptBIM
${MESSAGE}
📍 ${HOSTNAME} | ${TIMESTAMP}"

# 優先用全域 notify 命令（寫入 /tmp/imessage_notify.txt）
if command -v notify &>/dev/null; then
    notify "${FULL_MSG}"
else
    # fallback: 直接寫入觸發檔
    echo "${FULL_MSG}" > /tmp/imessage_notify.txt
fi

echo "[iMessage] ✅ 通知已排入發送"
