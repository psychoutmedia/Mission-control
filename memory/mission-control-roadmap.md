# Automa Dynamics - Mission Control Roadmap

## The Vision
"Open Mission Control, type 'Build me a landing page for product X', watch Astra break it down, Newton research competitors, Bronte write copy, Guido build the page — all in real-time, handing off work, with you approving key decisions."

---

## Tier 1 — Immediate Game Changers

### Live Output Streaming
- Stream agent thinking/output in real-time via SSE
- Expandable terminal panel per agent card
- Watch agents reason through problems live (addictive!)
- agentTerminalOutput already captured server-side

### Agent Pipelines (Chains)
- Multi-agent workflows: "Newton researches → Bronte writes report → Guido builds prototype"
- One click kicks off chain, each output feeds next as context
- Astra orchestrates
- **Killer feature** — turns 4 agents into a team

### Command Bar
- Single input at top of dashboard
- Type: "Research and write a blog post about quantum computing with code examples"
- Astra decomposes into subtasks, dispatches to right agents
- Think Spotlight for your agent swarm

---

## Tier 2 — Intelligence Layer

### Cost & Token Dashboard
- Real-time cost tracker per agent, per task, per day
- Burn rate graph
- Show which agents are expensive/efficient

### Conversation Replay
- Click completed result to see full agent conversation
- What it thought, tools used, files created
- Collapsible thread view from session JSONL logs

### Agent Memory Panel
- Show what each agent "remembers" across sessions
- Surface memory files, edit from dashboard
- Give Newton research brief, Bronte brand voice, Guido code style

---

## Tier 3 — Polish & Power

### Task Queue & Scheduling
- Queue multiple tasks per agent
- Cron scheduling: "Every morning Newton checks 5 news sources, Bronte writes digest"

### File Browser per Agent
- Expandable workspace viewer in each card
- Preview code, documents, images
- One-click open in VS Code

### Agent Performance Metrics
- Success rate, avg completion time, tasks/day, tokens/task
- Sparkline charts in cards
- Leaderboard — MVP agent weekly

### Notifications & Webhooks
- Push to Telegram/Slack when tasks complete
- Already have Telegram channel configured — ~20 min job
- Game changer for feeling like you have actual staff

---

## What We've Built (Feb 2026)
- Working multi-agent dashboard with task dispatch
- Completion detection (runs.json, file watchers)
- Communication flow visualization
- Status badges (idle/running/completed)
- Agent workspaces: /Users/marksstephenson/agents/{guido,newton,bronte}/
- Real-time via SSE (Claude Code implementation)
- Agent Results panel showing completed tasks

---

## Priority Sequence
1. **Ship Live Streaming** — transforms dashboard from task tracker to "feels alive"
2. **Agent Pipelines** — start with one hardcoded chain, prove handoff works
3. **Command Bar** — demo moment for viral potential
4. **Telegram Notifications** — quick win hiding in Tier 3

---

## The Thing Most People Never Get This Far
What we've already built — working multi-agent dashboard with task dispatch, completion detection, communication flow, status badges — most people never get this far. Adding streaming makes it genuinely novel.
