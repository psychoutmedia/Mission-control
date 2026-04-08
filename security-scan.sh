#!/bin/bash
# Daily Security Scan - checks for malware indicators
# Runs at 7am daily via cron

LOG_DIR="$HOME/clawd/memory/security-logs"
mkdir -p "$LOG_DIR"
DATE=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/scan-$DATE.log"

echo "=== Security Scan - $DATE $(date +%H:%M) ===" > "$LOG_FILE"

# Check for known malware LaunchAgents
echo -e "\n[LaunchAgents Check]" >> "$LOG_FILE"
SUSPICIOUS=$(ls ~/Library/LaunchAgents/ 2>/dev/null | grep -E 'com\.bashsrc|ixxjei|phex' || echo "None found")
echo "Suspicious patterns: $SUSPICIOUS" >> "$LOG_FILE"

# Check for suspicious processes
echo -e "\n[Suspicious Processes]" >> "$LOG_FILE"
ps aux | grep -E 'ixxjei|phex|kys\.(li|cx)' | grep -v grep >> "$LOG_FILE" || echo "None running" >> "$LOG_FILE"

# Check for new LaunchAgents in last 24h
echo -e "\n[New LaunchAgents (24h)]" >> "$LOG_FILE"
find ~/Library/LaunchAgents -mtime -1 -type f 2>/dev/null >> "$LOG_FILE" || echo "None" >> "$LOG_FILE"

# Check outbound connections to known C2
echo -e "\n[Network Check - Known C2]" >> "$LOG_FILE"
lsof -i -n 2>/dev/null | grep -E 'kys\.(li|cx)' >> "$LOG_FILE" || echo "No C2 connections" >> "$LOG_FILE"

# Summary
echo -e "\n[Summary]" >> "$LOG_FILE"
if echo "$SUSPICIOUS" | grep -q "None"; then
    echo "STATUS: CLEAN" >> "$LOG_FILE"
else
    echo "STATUS: ALERT - Review required" >> "$LOG_FILE"
fi

echo "Scan complete: $LOG_FILE"

# Send Telegram notification
STATUS=$(grep "STATUS:" "$LOG_FILE" | cut -d: -f2 | tr -d ' ')
SUMMARY="🛡️ *Security Scan Report*

*Date:* $DATE 07:00
*Status:* $STATUS

Details: $LOG_FILE"

# Get bot token from config, use known chat ID
TOKEN=$(grep -o '"botToken"[[:space:]]*:[[:space:]]*"[^"]*' "$HOME/.openclaw/openclaw.json" | head -1 | cut -d'"' -f4)
CHAT_ID="847041882"  # Billy big bags

if [ -n "$TOKEN" ] && [ -n "$CHAT_ID" ]; then
    curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$SUMMARY" \
        -d "parse_mode=markdown" >> /tmp/security-scan-telegram.log 2>&1
    echo "Telegram notification sent"
else
    echo "Failed to get TOKEN or CHAT_ID. TOKEN=$TOKEN, CHAT_ID=$CHAT_ID" >> /tmp/security-scan-telegram.log
fi
