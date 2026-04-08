# Mission Control — Telegram Notifications

> Quick Win Task | Created: 2026-03-06

## Status: Already Implemented! 🎉

Telegram notifications are built into Mission Control server. Just need to configure.

## How to Enable

### 1. Bot Token (already configured via OpenClaw)
The server reads `botToken` from `~/.openclaw/openclaw.json`:
```json
{
  "channels": {
    "telegram": {
      "botToken": "your-bot-token"
    }
  }
}
```

### 2. Set Your Chat ID

**Option A: Via API**
```bash
curl -X POST http://localhost:8888/telegram/config \
  -H "Content-Type: application/json" \
  -d '{"chatId": "YOUR_CHAT_ID", "enabled": true}'
```

**Option B: Via Dashboard**
The Mission Control UI should have a settings panel for this.

### 3. Test It
```bash
curl -X POST http://localhost:8888/telegram/test
```

## What Gets Notified

When any agent completes a task:
```
✅ *Newton* completed
Research the top 5 AI code review tools...
```

Or on error:
```
❌ *Guido* error
Build the landing page HTML...
```

Pipeline steps also get notified:
```
✅ *Bronte* completed (pipeline step 2/3)
Write compelling copy about...
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/telegram/config` | GET | Current config (hasToken, chatId, enabled) |
| `/telegram/config` | POST | Set chatId and enabled |
| `/telegram/test` | POST | Send test notification |

## Getting Your Chat ID

1. Message @userinfobot on Telegram
2. It replies with your user ID
3. Use that as `chatId`

Or for group chats:
1. Add your bot to the group
2. Send a message
3. Check `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Find the `chat.id` in the response

---

*Feature was already there — just needed docs!* ✨
