# Agent Notify

Sends task status notifications to Mark's Telegram. Any agent or script can call this to report work completion.

## Quick Usage

```bash
# Task completed
python projects/agent_notify/notify.py "Astra" "Built timecode agent" done

# Task started
python projects/agent_notify/notify.py "Astra" "Researching LLM quantization" started

# Blocked
python projects/agent_notify/notify.py "Astra" "Waiting on API key" blocked

# Info update
python projects/agent_notify/notify.py "Astra" "Queue cleared, 3 agents idle" info
```

## Python API

```python
from notify import format_notification, send_message

msg = format_notification("Astra", "LeetCode practice complete", "done")
send_message(msg)
```

## Status Types

| Status | Emoji | Use Case |
|--------|-------|----------|
| `started` | 🚀 | Task begun |
| `done` | ✅ | Task completed (default) |
| `blocked` | 🚫 | Waiting on something |
| `info` | ℹ️ | General update |

## Integration

Agents can call this at start/completion of tasks. Example in an agent:

```python
import subprocess
subprocess.run([
    "python", "projects/agent_notify/notify.py",
    "TimecodeAgent", "Generated thread draft", "done"
])
```

Or via the `message` tool directly for OpenClaw agents.
