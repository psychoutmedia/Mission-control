# Clawd - Mission Control Project

## Project Overview

Multi-agent AI system ("Automa Dynamics") with a web-based Mission Control dashboard at `localhost:8888`. Built on OpenClaw, managing four AI agents that work as a team.

### Agents
- **Astra (main)** — CEO / Project Manager, workspace: `/Users/marksstephenson/clawd`
- **Guido** — Coder, workspace: `/Users/marksstephenson/agents/guido`
- **Newton** — Researcher, workspace: `/Users/marksstephenson/agents/newton`
- **Bronte** — Content Writer, workspace: `/Users/marksstephenson/agents/bronte`

### Key Files
- `mission-control-server.js` — Node.js backend (port 8888), handles agent spawning, completion detection, SSE streaming, file watching
- `mission-control.html` — Single-file dashboard with embedded CSS/JS, dark space theme, glass-morphism design
- `mission-control-data.json` — Kanban board persistence

### Infrastructure
- OpenClaw gateway: WebSocket only at `ws://127.0.0.1:18789` (no REST API)
- Agent config: `~/.openclaw/openclaw.json`
- Subagent runs tracked in: `~/.openclaw/subagents/runs.json`
- Session data: `~/.openclaw/agents/{id}/sessions/sessions.json` (JSONL logs per session)
- CLI: `openclaw agent --agent <id> --message "<text>"` dispatches tasks
- Gateway auth token and Telegram bot token are in `openclaw.json`
- Default model: MiniMax M2.5, with Claude Sonnet/Opus as fallbacks

### Completion Detection (3-layer system)
1. **runs.json polling + fs.watch** — Primary signal for subagent completions
2. **Agent directory file watching** — Detects new output files in agent workspaces
3. **Session activity polling** — Reads session JSONL for recent activity timestamps

Note: `runs.json` only tracks subagent runs (mostly Guido). Tasks dispatched via CLI (`runAgentTask()`) also push results directly into `completedResults` array to ensure Newton/Bronte completions appear in Agent Results.

---

## Work Completed (2026-02-20)

### Session 1 — Full investigation & implementation

1. **Investigated OpenClaw system** — Mapped CLI commands, discovered WebSocket-only gateway (no REST), found runs.json as completion signal, mapped agent directories and session files

2. **Rewrote `mission-control-server.js`** with:
   - Three-layer completion detection (runs.json + file watching + session polling)
   - SSE endpoint (`/agents/events`) for real-time push to dashboard
   - Non-blocking spawn pattern (HTTP responds immediately, task runs in background)
   - Bootstrap task filtering (`isBootstrapTask()`) to suppress "introduce yourself" auto-tasks
   - Friendly model name mapping (`friendlyModelName()`)
   - Agent terminal output capture for future streaming

3. **Updated `mission-control.html`** with:
   - SSE connection with polling fallback
   - State transition detection (running -> idle = completion)
   - Browser notifications on task completion
   - Flicker-free results rendering (hash-based skip of redundant re-renders)
   - Dismiss button per result card + Clear All for Agent Results
   - Clear All button for Communication Flow messages
   - Completed status displayed in red
   - Themed toast notifications (replaced ugly native `alert()`)
   - Themed task input modal (replaced native `prompt()`, supports Ctrl+Enter)
   - Avatar squish fix (flex: 0 0 48px, max-width/max-height constraints)
   - Status pill badges (idle=grey, active=green, running=amber+pulse, completed=green)
   - Overflow containment on agent-header and agent-info

4. **Fixed CLI completion path** — Newton/Bronte tasks dispatched via `runAgentTask()` weren't appearing in Agent Results because `completedResults` was only populated from `runs.json`. Added direct result injection after CLI task completion with dedup check.

### Session 2 — Tier 1 Features (2026-02-21)

5. **Live Output Streaming** — Expandable terminal panel per agent card. Server includes `terminalOutputs` in SSE/activity responses. Frontend auto-opens terminal when agent starts producing output, shows blinking cursor, auto-scrolls. Click "Live Output" toggle to expand/collapse.

6. **Agent Pipelines** — Multi-agent workflow chains via `POST /agents/pipeline`. Three preset pipelines:
   - Newton → Bronte (Research & Write)
   - Newton → Guido (Research & Build)
   - Newton → Bronte → Guido (Full Pipeline)
   - Each step runs sequentially, output feeds as `{{input}}` to next step
   - Pipeline progress shown with step-by-step status badges (pending/running/completed/error)
   - Results from each step appear in Agent Results panel

7. **Command Bar** — Prominent input at top of Command Centre via `POST /agents/command`. User types a high-level goal, Astra decomposes into subtasks using a structured JSON prompt, dispatches to appropriate agents. Supports both sequential (dependent) and parallel (independent) task dispatch. Falls back to heuristic keyword matching if Astra's JSON parsing fails.

### Session 3 — Tier 2 & Polish (2026-02-21)

8. **Token & Cost Dashboard** — Reads JSONL session logs per agent to extract real token usage and cost data (input/output tokens, total cost per agent). Displayed on each agent card with breakdown. Cached with 30s TTL. Per-session tracking with baseline system — tokens start at zero on server start. Reset Tokens button per agent + on Astra card.

9. **Pipeline Progress Bar** — Active pipelines now show visual progress bar (step X/Y), elapsed time per step, and step status icons (○ pending, ◉ running, ✓ completed, ✗ error).

10. **Custom Pipeline Builder** — Form-based UI to build arbitrary pipelines. Users select agents and type task templates per step, with `{{input}}` placeholder for previous step output. Minimum 2 steps, add/remove steps dynamically.

11. **Terminal UX Improvements** — Smart auto-scroll (only scrolls when user is near bottom), line count indicator in toggle label, output cleared state properly resets label.

12. **Clear Context Button** — Per-agent button to reset session state.

13. **Full Task Display** — Removed all task text truncation from result cards, pipeline names, and step tooltips. Result cards use flex layout with full wrapping task text on left, metadata pinned top-right. Pipeline headers wrap naturally.

14. **Timeout Fix** — Agent task timeout increased from 120s to 300s (configurable per call) to prevent complex multi-file tasks from being killed mid-work.

### Session 4 — Tier 3 Features (2026-02-21)

15. **File Browser per Agent** — Expandable panel on each agent card showing workspace files. Shows file name with type icon, size, modified time. Click a file to expand inline preview (first 500 chars). Auto-refreshes every 15s when open. Uses existing `/agents/files/:agentId` endpoint.

16. **Agent Performance Metrics** — Derived from completedResults: task count, success rate (color-coded green/amber/red), error count, average duration. Displayed inline on agent cards alongside token stats.

17. **Telegram Notifications** — Reads bot token from openclaw.json. Sends completion notifications (with agent name, status emoji, task text) via Telegram Bot API. Dashboard has Notifications panel with enable/disable toggle, chat ID input, and Test button. Notifications fire on runs.json completions, CLI task completions, and queue task completions.

18. **Task Queue** — Per-agent task queue via `POST /agents/queue`. Tasks execute sequentially — queue multiple tasks and they run one after another. Queue depth shown on agent cards ("2 queued" in purple). Clear queue endpoint available.

19. **Scheduled Tasks** — Cron-style scheduling via `POST /schedules`. Set agent, time (HH:MM), and task description. Checked every 30s, triggers `enqueueTask()` at the matching minute. Dashboard has Schedules panel with add form (agent selector, time picker, task input) and list of active schedules with delete buttons. Shows last run time.

### Session 5 — North Star Gap Close (2026-02-22)

20. **Review Gates Between Pipeline Steps** — Opt-in `reviewGates` flag on pipeline creation. After each non-final step completes and output is summarised, pipeline pauses with `awaiting_review` status using a Promise-based pause pattern. User sees an inline review panel in the pipeline card with:
    - Editable textarea containing the summary (what gets passed to next step)
    - Collapsible raw output section
    - "Approve & Continue" (with optional edited summary) and "Skip Step" buttons
    - Server endpoint: `POST /pipelines/review` accepts `{ pipelineId, stepIndex, action, editedSummary }`
    - "Review between steps" checkbox added to approval modal (defaults ON for command bar goals, OFF for presets/custom)
    - Applied to both `/agents/pipeline` and `/agents/command/approve` pipeline paths

21. **Error Recovery (Retry / Override / Abort)** — When a pipeline step fails, instead of aborting immediately, pipeline enters `step_error` status and pauses with a Promise. User sees an error panel with:
    - Error message and step output
    - "Retry Step" — re-runs the failed step (`i--; continue` pattern)
    - "Override & Continue" — user provides manual output text, step marked `completed` + `overridden: true`, pipeline continues with user text
    - "Abort Pipeline" — kills the pipeline (explicit user choice)
    - Server endpoint: `POST /pipelines/retry` accepts `{ pipelineId, stepIndex, action, output }`
    - Applied to both pipeline execution paths

22. **Dynamic Coordination Diagram** — `renderCommunicationDiagram()` now shows live pipeline flow when a pipeline is active:
    - Only pipeline agents displayed (not all 4)
    - Completed steps: green `✓` with solid `══▶` arrows
    - Running steps: amber `◉` with animated arrows
    - Summarising steps: blue `⟳`
    - Awaiting review: amber `⏸ Review`
    - Pending steps: grey `○` with dashed `───▶` arrows
    - Error steps: red `✗`
    - Falls back to static all-agents view when no pipeline is active
    - Tracks `lastPipelines` from SSE activity data

23. **New Pipeline States & CSS** — Added `awaiting_review` and `step_error` states to pipeline cards, badges, and step indicators. Review gate panel uses subtle amber border + box-shadow (no pulsing text). Error panel uses red border styling. Both have dedicated textarea styles for editing.

### Tests Passed (2026-02-22)

| # | Test | Result |
|---|------|--------|
| 1 | Preset pipeline with review gates checked — Newton completes, review gate appears, edit summary, approve | PASS |
| 2 | Command bar pipeline — review gates default ON, gate appears between steps | PASS |
| 3 | Review gate — click "Skip Step" — next agent receives empty context | PASS |
| 4 | Error recovery — force timeout, override with manual text, next step receives override | PASS |
| 5 | Error recovery — override failed step, verify overridden text flows to next step's `{{input}}` | PASS |
| 6 | Error recovery — abort pipeline from step_error state, pipeline status → error | PASS |
| 7 | Dynamic diagram — 3-step pipeline shows live state transitions (◉→⟳→✓) with arrow styles | PASS |
| 8 | No review gates — pipeline with `reviewGates: false` runs straight through, never pauses | PASS |

---

## Roadmap — ALL TIERS + NORTH STAR COMPLETE

### Tier 1 — COMPLETED
- **Live Output Streaming** — Expandable terminal panel, smart auto-scroll, line count
- **Agent Pipelines** — 3 presets + custom builder, progress bar, elapsed time
- **Command Bar** — Natural language goal decomposition via Astra

### Tier 2 — COMPLETED
- **Cost & Token Dashboard** — Per-session JSONL tracking, reset button, baselines
- **Full Task Display** — No truncation, wrapping layout, metadata top-right
- **Clear Context / Reset Tokens** — Per-agent session and token management

### Tier 3 — COMPLETED
- **File Browser** — Per-agent workspace viewer with file preview
- **Performance Metrics** — Success rate, task count, avg duration, error count
- **Telegram Notifications** — Bot API integration with test and config UI
- **Task Queue & Scheduling** — Sequential queue per agent, cron-style schedules

### North Star — COMPLETED
- **Approval Modal** — User reviews and edits Astra's decomposition before dispatch
- **Output Summarisation** — Structured JSON handoff between pipeline steps via role-aware prompts (key_findings, sources, recommended_angle, confidence)
- **Review Gates** — Opt-in pause between pipeline steps, user can edit/approve/skip handoff summaries
- **Error Recovery** — Failed steps pause for retry/override/abort instead of killing the pipeline
- **Dynamic Coordination Diagram** — Live pipeline flow visualization with per-step status

### North Star Vision
Open Mission Control, type "Build me a landing page for product X", and watch Astra break it down, Newton research competitors, Bronte write copy, and Guido build the page — all in real-time with live streaming output, agents handing off work to each other, with the user approving key decisions from the dashboard.

### Session 6 — Structured Handoff Protocol (2026-02-22)

24. **Structured Handoff Format** — Complete rewrite of `summariseOutput()` to use role-aware JSON handoff protocol:
    - Per-agent summarisation prompts (`HANDOFF_PROMPTS`): Newton emphasises findings/sources/evidence, Bronte emphasises themes/hooks/audience, Guido emphasises tech decisions/file paths/dependencies
    - JSON handoff schema: `{ summary, key_findings[], sources[], recommended_angle, confidence }`
    - `parseHandoff()` — parses agent response as JSON with regex fallback for fenced code, graceful degradation to `{ summary: <raw text> }`
    - `formatHandoffForInjection()` — converts handoff JSON to readable markdown for next agent's `{{input}}` injection: `## Handoff from Newton` with structured fields
    - Both pipeline loops updated to use `{ handoff, raw, formatted }` return value
    - `step.handoff` stores the structured object for frontend rendering
    - Review gate enhanced: when structured handoff exists, shows editable fields (summary input, key findings list with add/remove, recommended angle, sources, confidence badge) instead of plain textarea
    - `submitPipelineReview()` collects `editedHandoff` from structured fields, sends to server, which rebuilds formatted injection from edited fields
    - `addHandoffFinding()` helper for dynamic finding list editing
    - Falls back to plain textarea when handoff is unstructured (no key_findings)
    - Review endpoint updated to accept `editedHandoff` alongside `editedSummary`

25. **Consolidated Pipeline Report View** — Full report panel for completed pipelines:
    - `generatePipelineReport()` — builds report object on pipeline completion with per-step durations, structured handoffs, output files, and deliverables
    - `detectDeliverables()` — scans agent workspace for files modified during step's time window (±2s tolerance)
    - `step.startedAt` timestamp added to both pipeline loops for accurate per-step duration tracking
    - `GET /pipelines/:id/report` endpoint — returns full report JSON, generates on-demand if not cached
    - **Report UI**: "View Report" button on completed pipeline cards, toggleable report panel with:
      - Header with goal name and total duration
      - Handoff chain visualization (purple nodes showing agent → agent flow with finding counts)
      - Vertical step timeline with green dot markers, per-step duration bars, task descriptions
      - Structured handoff display per step (summary, findings, recommended angle)
      - Collapsible raw output per step
      - Auto-detected output files per step with file size
      - Deliverables section (final step files or all step files as fallback)
    - CSS: `.pipeline-report`, `.report-timeline`, `.report-step`, `.report-handoff`, `.report-deliverable`, `.report-handoff-chain`, `.report-chain-flow`

26. **Polish: Confidence Selector** — Review gate confidence field changed from static badge to `<select>` dropdown (high/medium/low). Value read by `submitPipelineReview()` and included in `editedHandoff.confidence`. CSS: `.handoff-confidence-select`.

27. **Polish: Source URL Auto-Linking** — `autoLinkUrls()` helper detects `http://` and `https://` URLs in text and wraps them in clickable `<a>` tags. Applied to report handoff sources. Sources section added to report handoff display with 🔗 styling.

28. **Polish: Deliverable Preview & File Browser Links** — Report deliverables now have:
    - "Open in Files" button — calls `openAgentFileBrowser()` which opens the agent's file browser panel and scrolls to the card
    - "Preview" button — calls `toggleDeliverablePreview()` which fetches file preview from `/agents/files/` endpoint and shows inline
    - Per-step output files in report also get "Open in Files" button
    - CSS: `.report-file-btn`, `.deliverable-preview`

### Tests Passed (Session 6)

| # | Test | Result |
|---|------|--------|
| 1 | Newton → Bronte with review gates — structured handoff with findings, high confidence | PASS |
| 2 | Approve structured review gate — Bronte references specific handoff findings | PASS |
| 3 | Newton → Bronte without review gates — structured handoff flows automatically | PASS |
| 4 | Newton → Bronte → Guido 3-step pipeline — report shows 3 steps, per-step durations, structured handoffs | PASS |
| 5 | Deliverable auto-detection — `black_hole_poem.py` detected from Guido's step window | PASS |
| 6 | Report with review gates — 2-step pipeline report generated after review gate approval | PASS |
| 7 | Report endpoint 404 — returns 404 for unknown pipeline ID | PASS |
| 8 | Full polish test (JWST pipeline) — sources with NASA/ESA URLs, confidence dropdown, deliverable preview of `jwst_blog_post.py` | PASS |

### Session 7 — Intelligence & Reliability (2026-02-22)

29. **Enhanced Astra Decomposition** — Complete rewrite of Astra's goal decomposition prompt:
    - Three few-shot examples (landing page, blog post, Python script) showing ideal decomposition
    - Each task now includes `expectedOutput`, `successCriteria`, and `handoffNote` fields
    - Agent descriptions expanded with specific output types (Newton: findings/URLs, Bronte: prose/CTAs, Guido: code files)
    - Approval modal shows metadata below each step (expected output, success criteria, handoff note) with purple accent styling
    - CSS: `.approval-step-meta`, `.approval-meta-row`, `.approval-meta-label`

30. **Summarisation Reliability Fix** — `summariseOutput()` now includes raw output directly in the summarisation prompt:
    - Truncated to 4000 chars and prepended: `"Here is the raw output...\n---\n{output}\n---\n{role-aware prompt}"`
    - Eliminates silent failure mode where session memory loss produced empty handoffs
    - Server log now shows chars included: `"Asking newton to summarise 24 chars of output (24 included in prompt)"`

31. **Persistence** — Schedules and completed pipeline reports now survive server restarts:
    - `.mission-control/` directory created at project root
    - `schedules.json` — written on create, delete, and lastRun update
    - `pipelines.json` — written on pipeline completion (completed pipelines with reports, max 20, stripped of functions/promises)
    - `loadSchedules()` and `loadPipelines()` called on startup, restoring IDs and counter state
    - Server logs: `[PERSIST] Loaded N schedules`, `[PERSIST] Loaded N pipelines`

32. **Result Card Overflow Fix** — Long URLs in summary handoff text no longer break outside result cards:
    - Added `word-break: break-word; overflow-wrap: break-word` to summary div
    - Added `overflow: hidden` to `.result-card`

### Tests Passed (Session 7)

| # | Test | Result |
|---|------|--------|
| 1 | Decomposition: "Build landing page for CodeLens" → 3 steps with expectedOutput, successCriteria, handoffNote per step | PASS |
| 2 | Decomposition: Newton names specific competitors (CodeRabbit, Codeball, etc.), not generic "research" | PASS |
| 3 | Summarisation: raw output (24 chars) included in prompt, 3 structured findings returned | PASS |
| 4 | Schedule persistence: create → restart → schedule loads from disk | PASS |
| 5 | Pipeline persistence: complete → restart → report accessible via GET endpoint | PASS |

### North Star Audit — 88% → ~94%

- **Decomposition: 82% → 93%** — Few-shot examples, output format specs, success criteria, handoff notes. Remaining: could add estimated complexity, more examples
- **Structured Handoff: 88% → 95%** — Raw output now passed directly into summarisation prompt, eliminating session memory dependency
- **Persistence: 0% → 90%** — Schedules and pipeline reports survive restarts. Remaining: task queue persistence, kanban board backup
- **UI/UX: 89% → 91%** — Result card overflow fixed

---

### Session 8 — Audit Polish (2026-02-22)

33. **Edit & Retry** — Error recovery now includes an editable task textarea:
    - Server: `/pipelines/retry` accepts `editedTask` field, both pipeline retry blocks apply it to `step.task` and `step.taskTemplate` before re-running
    - Frontend: Error panel shows pre-filled textarea with original task text, user can edit before clicking "Retry Step"
    - `submitPipelineRetry()` reads `error-task-{id}` textarea and sends `editedTask` in POST body

34. **Add Step in Approval Modal** — Users can now add new steps during plan review:
    - "+ Add Step" button below step list (dashed purple border, full width)
    - New steps default to a different agent than the last step
    - Each step now has an agent selector dropdown (replaces static agent name)
    - `changeApprovalAgent()` updates agent and re-renders with correct avatar/color
    - Sequential pipelines auto-set `dependsOn` for new steps

35. **Diagram Arrow Labels** — Dynamic coordination diagram now shows handoff context on arrows:
    - When a step completes and has a handoff, the arrow displays a truncated excerpt (40 chars) of the recommended angle or summary
    - CSS: `.comm-arrow-label` with small text, centered below arrow, ellipsis overflow
    - `.comm-flow-arrow` changed to `flex-direction: column` to stack arrow + label

36. **Report Chain Excerpts** — Pipeline report handoff chain nodes enhanced:
    - Each node shows finding count ("3 findings") in blue
    - Non-final steps show truncated recommended angle/summary (50 chars) below agent name
    - Nodes use `display: inline-flex; flex-direction: column` for stacked layout
    - Title attribute shows full excerpt on hover

### North Star Audit — ~94% → ~97%

All audit stretch goals implemented:
- Edit & Retry: users can tweak failed tasks before retrying
- Add Step: approval modal supports adding new pipeline steps with agent selection
- Diagram labels: arrows show handoff context between agents
- Report excerpts: chain visualization shows key findings and angles

## Roadmap — Remaining Polish

- **Syntax highlighting** — Code blocks in terminal output and result cards
- **Notification click handlers** — Click browser notifications to scroll to relevant result
- **Task queue persistence** — Save queued tasks to disk
- **Estimated complexity** — Add complexity rating to decomposition metadata
