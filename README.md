<p align="center">
  <img src="logo.png" alt="Automa Dynamics" width="200">
</p>

<h1 align="center">Mission Control</h1>

<p align="center">
  A real-time web dashboard for orchestrating multi-agent AI teams.<br>
  Built on <a href="https://github.com/anthropics/claude-code">OpenClaw</a> — type a goal, watch your agents coordinate.
</p>

---

## What Is This?

Mission Control is a browser-based command centre for managing a team of AI agents that collaborate on tasks. You give a high-level goal — "Research quantum computing and write a blog post with code examples" — and the system breaks it down, dispatches work to specialist agents, and streams their progress in real-time.

**The agents:**

| Agent | Role | Specialty |
|-------|------|-----------|
| **Astra** | CEO / Project Manager | Decomposes goals into subtasks, coordinates the team |
| **Newton** | Researcher | Technical research, API exploration, fact-finding |
| **Bronte** | Content Writer | Blog posts, documentation, creative writing |
| **Guido** | Coder | Python, TypeScript, debugging, architecture |

## Features

### Command Bar
Type a natural language goal. Astra analyses it, breaks it into subtasks, and dispatches them to the right agents — in parallel or sequentially depending on dependencies.

### Agent Pipelines
Chain agents together in workflows:
- **Research & Write** — Newton researches, Bronte writes
- **Research & Build** — Newton researches, Guido codes
- **Full Pipeline** — Newton → Bronte → Guido
- **Custom Pipelines** — Build your own multi-step chains with a form-based UI

Each step's output feeds into the next via `{{input}}` templates.

### Live Output Streaming
Expandable terminal panel on each agent card. Watch agents think in real-time with auto-scrolling output, blinking cursor, and line count indicators.

### Token & Cost Tracking
Per-session token usage and cost data extracted from agent session logs. Baseline system resets counters on server start. Reset buttons per agent.

### Task Queue & Scheduling
Queue multiple tasks per agent — they execute sequentially. Set up cron-style schedules for recurring tasks (e.g., "Every morning at 9am, Newton checks tech news").

### File Browser
Browse each agent's workspace from the dashboard. Preview files inline, see file sizes and modification times. Auto-refreshes while open.

### Performance Metrics
Task count, success rate (colour-coded), average duration, and error count per agent — derived from completed results.

### Telegram Notifications
Get notified on your phone when agents complete tasks. Reads bot token from your OpenClaw config. Enable/disable from the dashboard with a test button.

### Agent Results Panel
Full history of completed tasks with status, duration, and pipeline context. Dismiss individual results or clear all. No truncation — full task text always visible.

## Quick Start

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [OpenClaw](https://github.com/anthropics/claude-code) installed and configured with agents

### Run

```bash
node mission-control-server.js
```

Open [http://localhost:8888](http://localhost:8888) in your browser.

### Configuration

The server reads agent configuration from `~/.openclaw/openclaw.json`. Each agent needs:
- An agent ID (`main`, `guido`, `newton`, `bronte`)
- A workspace directory at `~/agents/{id}/`
- Session data at `~/.openclaw/agents/{id}/sessions/`

Telegram notifications require a `telegram_bot_token` field in your `openclaw.json`.

## Architecture

```
mission-control-server.js    Node.js backend (port 8888)
├── SSE streaming            /agents/events — real-time push to dashboard
├── Agent spawning           openclaw CLI dispatch, non-blocking
├── Completion detection     3-layer: runs.json + file watch + session polling
├── Pipelines                Sequential chain execution with output handoff
├── Command bar              Goal decomposition via Astra agent
├── Task queue               Per-agent sequential queue
├── Scheduling               Cron-style recurring tasks (30s check interval)
├── Telegram                 Bot API notifications on completions
└── File browser             Agent workspace file listing + preview

mission-control.html         Single-file dashboard (HTML + CSS + JS)
├── Dark space theme         Glass-morphism design, purple accent
├── Agent cards              Status, tokens, performance, terminal, files
├── Pipeline UI              Presets, custom builder, progress tracking
├── Results panel            Full task history with dismiss/clear
└── Settings                 Telegram config, schedules, kanban board

mission-control-data.json    Kanban board persistence
```

### Completion Detection (3-layer system)
1. **runs.json polling + fs.watch** — Primary signal for subagent completions
2. **Agent directory file watching** — Detects new output files in agent workspaces
3. **Session activity polling** — Reads session JSONL for recent activity timestamps

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/agents/activity` | Agent status, tokens, terminal output |
| `GET` | `/agents/events` | SSE stream for real-time updates |
| `POST` | `/agents/task` | Dispatch a task to an agent |
| `POST` | `/agents/command` | Submit a goal for Astra to decompose |
| `POST` | `/agents/pipeline` | Run a multi-agent pipeline |
| `POST` | `/agents/queue` | Add a task to an agent's queue |
| `POST` | `/agents/reset-tokens` | Reset token counters |
| `GET` | `/agents/files/:id` | List files in agent workspace |
| `GET/POST` | `/telegram/config` | Get/set Telegram notification settings |
| `POST` | `/telegram/test` | Send a test Telegram notification |
| `GET/POST` | `/schedules` | View/add scheduled tasks |

## License

MIT
