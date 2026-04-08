# HEARTBEAT.md - Proactive Work System

> Idle agents are wasted tokens. Keep working.

## 1. Quick Checks (urgent first)

- [ ] Human messages waiting? → Handle immediately
- [ ] Critical blockers? → Escalate or notify
- [ ] System health issues? → Handle or flag

If **nothing urgent**, proceed to work mode.

---

## 2. Work Mode

1. Read `tasks/QUEUE.md`
2. Pick highest-priority "Ready" task you can do
3. Do meaningful work on it
4. Update the queue (move to Done or note progress)
5. If time/tokens remain, pick another task

---

## 3. Before Finishing

- [ ] Log what you did to `memory/YYYY-MM-DD.md`
- [ ] Update task queue with any new tasks discovered
- [ ] Post update if significant

---

## Token Strategy

| Priority | What | Always |
|----------|------|--------|
| 1 | Human requests | ✓ |
| 2 | Urgent tasks | Time-sensitive |
| 3 | High-impact | Moves the needle |
| 4 | Maintenance | Improvements |

**When approaching limits:**
- Wrap up current task
- Write detailed handoff notes
- Sleep until reset

---

## Fact Extraction (still applies)

After work mode, if tokens remain:
1. Check for new conversations
2. Spawn cheap sub-agent to extract durable facts
3. Write to relevant entity items.json
4. Track lastExtractedTimestamp

---

## Weekly Memory Review (Sunday cron)

For each entity with new facts:
1. Load summary.md
2. Load active items.json
3. Rewrite summary.md for current state
4. Mark contradicted facts as superseded

---

*Pull from queue. Keep working. Make progress.*
