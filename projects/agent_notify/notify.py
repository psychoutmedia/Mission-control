#!/usr/bin/env python3
"""
Task Notification Utility
Sends task completion / status updates to Mark via Telegram.
Usage: python notify.py "Agent Name" "Task description" [status]
Status: started | done | blocked | info (default: done)
"""

import sys
import json
from datetime import datetime

TELEGRAM_ID = "847041882"
BOT_TOKEN = "8449460477:AAHFUTC0pzQtrZVdgGUNi07J_OhztVW23II"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(text: str) -> bool:
    """Send message via Telegram Bot API."""
    import urllib.request
    import urllib.parse
    
    url = f"{TELEGRAM_API}/sendMessage"
    data = json.dumps({
        "chat_id": TELEGRAM_ID,
        "text": text,
        "parse_mode": "HTML"
    }).encode()
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get("ok", False)
    except Exception as e:
        print(f"Failed to send: {e}", file=sys.stderr)
        return False


STATUS_EMOJI = {
    "started": "🚀",
    "done": "✅",
    "blocked": "🚫",
    "info": "ℹ️",
}


def format_notification(agent: str, task: str, status: str = "done") -> str:
    """Format a task notification message."""
    emoji = STATUS_EMOJI.get(status, "✅")
    timestamp = datetime.now().strftime("%H:%M")
    
    lines = [
        f"{emoji} <b>{agent}</b>",
        f"   {task}",
        f"   <code>[{timestamp}]</code>",
    ]
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: notify.py <agent> <task> [status]")
        print("  status: started | done | blocked | info (default: done)")
        sys.exit(1)
    
    agent = sys.argv[1]
    task = sys.argv[2]
    status = sys.argv[3] if len(sys.argv) > 3 else "done"
    
    if status not in STATUS_EMOJI:
        print(f"Unknown status: {status}")
        sys.exit(1)
    
    msg = format_notification(agent, task, status)
    print(f"Sending: {msg}")
    
    if send_message(msg):
        print("Notification sent ✓")
    else:
        print("Notification failed ✗")
        sys.exit(1)


if __name__ == "__main__":
    main()
