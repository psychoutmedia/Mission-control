#!/usr/bin/env node
const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec, spawn } = require('child_process');
const crypto = require('crypto');

const https = require('https');

const PORT = 8888;
const DATA_FILE = path.join(__dirname, 'mission-control-data.json');
const HTML_FILE = path.join(__dirname, 'mission-control.html');

// ─── Telegram notifications ─────────────────────────────────────────────
let telegramBotToken = '';
let telegramChatId = '';
let telegramEnabled = false;

// Load bot token from openclaw config
try {
    const ocConfig = JSON.parse(fs.readFileSync(path.join(process.env.HOME, '.openclaw/openclaw.json'), 'utf8'));
    telegramBotToken = ocConfig?.channels?.telegram?.botToken || '';
    if (telegramBotToken) console.log('[TELEGRAM] Bot token loaded from openclaw.json');
} catch (e) { /* no config */ }

function sendTelegramNotification(message) {
    if (!telegramEnabled || !telegramBotToken || !telegramChatId) return;

    const payload = JSON.stringify({ chat_id: telegramChatId, text: message, parse_mode: 'Markdown' });
    const req = https.request({
        hostname: 'api.telegram.org',
        path: `/bot${telegramBotToken}/sendMessage`,
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) }
    }, (res) => {
        let body = '';
        res.on('data', d => body += d);
        res.on('end', () => {
            if (res.statusCode !== 200) console.log(`[TELEGRAM] Error: ${res.statusCode} ${body.substring(0, 100)}`);
        });
    });
    req.on('error', (e) => console.log(`[TELEGRAM] Request error: ${e.message}`));
    req.write(payload);
    req.end();
}

// Paths
const RUNS_FILE = path.join(process.env.HOME, '.openclaw/subagents/runs.json');
const AGENTS_BASE = path.join(process.env.HOME, 'agents');
const SESSIONS_BASE = path.join(process.env.HOME, '.openclaw/agents');

// Track agent states in memory
const agentStates = {
    main: { status: 'active', action: 'System Active', timestamp: new Date().toISOString() },
    guido: { status: 'idle', action: 'Idle', timestamp: new Date().toISOString() },
    newton: { status: 'idle', action: 'Idle', timestamp: new Date().toISOString() },
    bronte: { status: 'idle', action: 'Idle', timestamp: new Date().toISOString() }
};

// Track completed task results for the dashboard
let completedResults = [];

// Track known runs so we can detect new completions
let knownRunIds = new Set();

// Track file snapshots per agent directory
let agentFileSnapshots = {};

// Agent definitions with workspaces
const AGENTS = [
    { id: 'main', name: 'Astra', role: 'CEO / Project Manager', workspace: '/Users/marksstephenson/clawd' },
    { id: 'guido', name: 'Guido', role: 'Coder', workspace: '/Users/marksstephenson/agents/guido' },
    { id: 'newton', name: 'Newton', role: 'Researcher', workspace: '/Users/marksstephenson/agents/newton' },
    { id: 'bronte', name: 'Bronte', role: 'Content Writer', workspace: '/Users/marksstephenson/agents/bronte' }
];

// Track live terminal output for each agent
let agentTerminalOutput = {};

// Track output lengths for SSE delta streaming
let agentTerminalLengths = {};

// Filter terminal output to show only meaningful agent activity
function filterTerminalOutput(text) {
    const lines = text.split('\n');
    const filtered = [];
    for (const line of lines) {
        const trimmed = line.trim();
        // Skip empty lines
        if (!trimmed) continue;
        // Skip JSON system prompt / tool schema dumps
        if (trimmed.startsWith('{') && (trimmed.includes('"system"') || trimmed.includes('"tools"') || trimmed.includes('"model"') || trimmed.includes('"messages"'))) continue;
        if (trimmed.startsWith('"') && trimmed.endsWith('",')) continue; // JSON string fragments
        // Skip raw JSON arrays/objects that look like API payloads
        if (/^\[?\{.*"type"\s*:\s*"(function|tool_use|text_block|content_block)"/.test(trimmed)) continue;
        // Skip lines that are just JSON structure chars
        if (/^[\[\]{},]+$/.test(trimmed)) continue;
        // Skip very long lines (likely JSON blobs > 500 chars)
        if (trimmed.length > 500 && (trimmed.startsWith('{') || trimmed.startsWith('['))) continue;
        // Skip base64 or encoded content
        if (/^[A-Za-z0-9+/=]{100,}$/.test(trimmed)) continue;
        filtered.push(line);
    }
    return filtered.join('\n');
}

// Track active pipelines
let activePipelines = [];
let pipelineIdCounter = 0;

// ─── Persistence ────────────────────────────────────────────────────────
const PERSIST_DIR = path.join(__dirname, '.mission-control');
const SCHEDULES_FILE = path.join(PERSIST_DIR, 'schedules.json');
const PIPELINES_FILE = path.join(PERSIST_DIR, 'pipelines.json');

function ensurePersistDir() {
    try { if (!fs.existsSync(PERSIST_DIR)) fs.mkdirSync(PERSIST_DIR, { recursive: true }); } catch {}
}

function saveSchedules() {
    ensurePersistDir();
    try {
        fs.writeFileSync(SCHEDULES_FILE, JSON.stringify(scheduledTasks, null, 2));
    } catch (e) {
        console.log(`[PERSIST] Failed to save schedules: ${e.message}`);
    }
}

function loadSchedules() {
    try {
        if (fs.existsSync(SCHEDULES_FILE)) {
            const data = JSON.parse(fs.readFileSync(SCHEDULES_FILE, 'utf8'));
            if (Array.isArray(data)) {
                scheduledTasks = data;
                scheduleIdCounter = data.reduce((max, s) => {
                    const num = parseInt((s.id || '').replace('sched-', '')) || 0;
                    return Math.max(max, num);
                }, 0);
                console.log(`[PERSIST] Loaded ${scheduledTasks.length} schedules`);
            }
        }
    } catch (e) {
        console.log(`[PERSIST] Failed to load schedules: ${e.message}`);
    }
}

function savePipelines() {
    ensurePersistDir();
    try {
        // Only persist completed pipelines with reports (strip functions/promises)
        const toSave = activePipelines
            .filter(p => p.status === 'completed' && p.report)
            .slice(0, 20)
            .map(p => ({
                id: p.id, name: p.name, status: p.status,
                startedAt: p.startedAt, endedAt: p.endedAt,
                reviewGates: p.reviewGates,
                steps: p.steps.map(s => ({
                    agentId: s.agentId, task: s.task, taskTemplate: s.taskTemplate,
                    status: s.status, output: (s.output || '').substring(0, 3000),
                    summary: s.summary, handoff: s.handoff,
                    startedAt: s.startedAt, endedAt: s.endedAt,
                    overridden: s.overridden
                })),
                report: p.report
            }));
        fs.writeFileSync(PIPELINES_FILE, JSON.stringify(toSave, null, 2));
    } catch (e) {
        console.log(`[PERSIST] Failed to save pipelines: ${e.message}`);
    }
}

function loadPipelines() {
    try {
        if (fs.existsSync(PIPELINES_FILE)) {
            const data = JSON.parse(fs.readFileSync(PIPELINES_FILE, 'utf8'));
            if (Array.isArray(data)) {
                activePipelines = data;
                pipelineIdCounter = data.reduce((max, p) => {
                    const match = (p.id || '').match(/pipeline-(\d+)-/);
                    return match ? Math.max(max, parseInt(match[1])) : max;
                }, 0);
                console.log(`[PERSIST] Loaded ${activePipelines.length} pipelines`);
            }
        }
    } catch (e) {
        console.log(`[PERSIST] Failed to load pipelines: ${e.message}`);
    }
}

// ─── Per-agent model selection ──────────────────────────────────────────
const OPENCLAW_CONFIG = path.join(process.env.HOME, '.openclaw/openclaw.json');

// In-memory model tracking: null = using global default
const agentModels = { main: null, guido: null, newton: null, bronte: null };
let availableModels = [];
let defaultModel = '';

function loadAvailableModels() {
    try {
        const config = JSON.parse(fs.readFileSync(OPENCLAW_CONFIG, 'utf8'));
        const defaults = config?.agents?.defaults || {};

        // Extract default model
        defaultModel = defaults?.model?.primary || '';

        // Extract available models from models config
        const modelsConfig = defaults?.models || {};
        availableModels = Object.keys(modelsConfig).map(id => ({
            id,
            name: friendlyModelName(id)
        }));

        // Ensure default model is in the list
        if (defaultModel && !availableModels.find(m => m.id === defaultModel)) {
            availableModels.unshift({ id: defaultModel, name: friendlyModelName(defaultModel) });
        }

        // Read per-agent overrides from agents.list[]
        const agentsList = config?.agents?.list || [];
        for (const agentConf of agentsList) {
            if (agentConf.id && agentConf.model && agentModels.hasOwnProperty(agentConf.id)) {
                agentModels[agentConf.id] = agentConf.model;
            }
        }

        console.log(`[MODELS] Loaded ${availableModels.length} models, default: ${friendlyModelName(defaultModel)}`);
        console.log(`[MODELS] Per-agent overrides:`, Object.fromEntries(
            Object.entries(agentModels).filter(([, v]) => v !== null).map(([k, v]) => [k, friendlyModelName(v)])
        ));
    } catch (e) {
        console.log(`[MODELS] Could not load openclaw config: ${e.message}`);
    }
}

function getAgentCurrentModel(agentId) {
    return agentModels[agentId] || defaultModel;
}

// Track session state per agent: { sessionId, fresh, taskCount }
const agentSessionState = {
    main: { sessionId: null, fresh: true, taskCount: 0 },
    guido: { sessionId: null, fresh: true, taskCount: 0 },
    newton: { sessionId: null, fresh: true, taskCount: 0 },
    bronte: { sessionId: null, fresh: true, taskCount: 0 }
};

// ─── Task Queue per agent ──────────────────────────────────────────────
const agentQueues = {
    main: [], guido: [], newton: [], bronte: []
};
const agentQueueRunning = {
    main: false, guido: false, newton: false, bronte: false
};

function enqueueTask(agentId, task) {
    if (!agentQueues[agentId]) agentQueues[agentId] = [];
    const queueItem = { id: `q-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`, task, status: 'queued', addedAt: new Date().toISOString() };
    agentQueues[agentId].push(queueItem);
    console.log(`[QUEUE] ${agentId}: enqueued "${task.substring(0, 60)}" (queue size: ${agentQueues[agentId].length})`);
    processQueue(agentId);
    return queueItem;
}

async function processQueue(agentId) {
    if (agentQueueRunning[agentId]) return; // already processing
    if (!agentQueues[agentId] || agentQueues[agentId].length === 0) return;

    agentQueueRunning[agentId] = true;

    while (agentQueues[agentId].length > 0) {
        const item = agentQueues[agentId][0];
        item.status = 'running';
        item.startedAt = new Date().toISOString();

        const agent = AGENTS.find(a => a.id === agentId);
        agentStates[agentId] = {
            status: 'running',
            action: item.task,
            task: item.task,
            timestamp: new Date().toISOString()
        };

        console.log(`[QUEUE] ${agentId}: running "${item.task.substring(0, 60)}" (${agentQueues[agentId].length - 1} remaining)`);

        const result = await runAgentTask(agentId, item.task);
        const endTime = Date.now();

        item.status = result.code === 0 ? 'completed' : 'error';
        item.endedAt = new Date().toISOString();

        agentStates[agentId] = {
            status: 'idle',
            action: `Completed: ${item.task.substring(0, 40)}`,
            task: item.task,
            output: (result.stdout || '').substring(0, 2000),
            timestamp: new Date().toISOString()
        };

        // Add to completed results
        const alreadyCaptured = completedResults.some(r =>
            r.agent === agentId && r.task === item.task && Math.abs((r.endedAt || 0) - endTime) < 30000
        );
        if (!alreadyCaptured) {
            const cliResult = {
                id: `queue-${item.id}`,
                agent: agentId,
                agentName: agent?.name || agentId,
                task: item.task,
                status: item.status,
                startedAt: new Date(item.startedAt).getTime(),
                endedAt: endTime,
                durationMs: endTime - new Date(item.startedAt).getTime(),
                model: '',
                timestamp: new Date(endTime).toISOString()
            };
            completedResults.unshift(cliResult);
            if (completedResults.length > 50) completedResults = completedResults.slice(0, 50);

            const emoji = item.status === 'completed' ? '✅' : '❌';
            sendTelegramNotification(`${emoji} *${agent?.name}* ${item.status}\n${item.task.substring(0, 200)}`);
        }

        // Remove completed item from queue
        agentQueues[agentId].shift();
    }

    agentQueueRunning[agentId] = false;
}

// ─── Scheduled tasks (simple cron) ─────────────────────────────────────
let scheduledTasks = [];
let scheduleIdCounter = 0;

function checkSchedules() {
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinute = now.getMinutes();
    const dayOfWeek = now.getDay(); // 0=Sun

    for (const sched of scheduledTasks) {
        if (!sched.enabled) continue;

        // Check if this minute matches
        if (sched.hour === currentHour && sched.minute === currentMinute) {
            // Check day filter
            if (sched.days && sched.days.length > 0 && !sched.days.includes(dayOfWeek)) continue;

            // Don't re-trigger within same minute
            const lastRun = sched.lastRun ? new Date(sched.lastRun) : null;
            if (lastRun && (now - lastRun) < 90000) continue;

            sched.lastRun = now.toISOString();
            saveSchedules();
            console.log(`[SCHEDULE] Triggering: ${sched.agentId} - "${sched.task.substring(0, 60)}"`);
            enqueueTask(sched.agentId, sched.task);
        }
    }
}

// Check schedules every 30 seconds
setInterval(checkSchedules, 30000);

// Load persisted data on startup (after all variables are declared)
loadSchedules();
loadPipelines();

// ─── Helpers ───────────────────────────────────────────────────────────

// Bootstrap tasks that OpenClaw runs automatically — not user-initiated
function isBootstrapTask(task) {
    if (!task) return false;
    const t = task.trim().toLowerCase();
    // Exact matches
    if (t === 'introduce yourself briefly.' || t === 'introduce yourself.') return true;
    // Pattern matches — gateway bootstrap and spawn-only tasks
    if (t.startsWith('start as ')) return true;
    if (t.startsWith('start ') && t.endsWith(' agent')) return true;
    if (t.includes('read your workspace context') && t.includes('introduction')) return true;
    if (t.includes('introduce yourself') && t.includes('identity')) return true;
    return false;
}

function friendlyModelName(raw) {
    if (!raw) return '';
    const map = {
        'anthropic/claude-sonnet-4-5': 'Claude Sonnet 4.5',
        'anthropic/claude-opus-4-5': 'Claude Opus 4.5',
        'minimax/MiniMax-M2.1': 'MiniMax M2.1',
        'minimax/MiniMax-M2.5': 'MiniMax M2.5',
        'claude-sonnet-4-5': 'Claude Sonnet 4.5',
        'claude-opus-4-5': 'Claude Opus 4.5',
        'MiniMax-M2.1': 'MiniMax M2.1',
        'MiniMax-M2.5': 'MiniMax M2.5',
    };
    return map[raw] || raw;
}

// ─── Completion Detection: runs.json polling ───────────────────────────

function readRunsFile() {
    try {
        const raw = fs.readFileSync(RUNS_FILE, 'utf8');
        return JSON.parse(raw);
    } catch (e) {
        return { version: 2, runs: {} };
    }
}

function checkRunsForCompletions() {
    const data = readRunsFile();
    const runs = data.runs || {};

    for (const [runId, run] of Object.entries(runs)) {
        // Skip runs we've already processed
        if (knownRunIds.has(runId)) continue;

        // If run has endedAt, it's complete
        if (run.endedAt) {
            knownRunIds.add(runId);

            // Skip bootstrap/intro tasks — not user-initiated
            if (isBootstrapTask(run.task)) {
                continue;
            }

            // Extract agent ID from childSessionKey: "agent:guido:subagent:..."
            const parts = (run.childSessionKey || '').split(':');
            const agentId = parts[1] || 'unknown';
            const agent = AGENTS.find(a => a.id === agentId);

            const result = {
                id: runId,
                agent: agentId,
                agentName: agent?.name || agentId,
                task: run.task || 'Unknown task',
                status: run.outcome?.status === 'ok' ? 'completed' : 'error',
                startedAt: run.startedAt,
                endedAt: run.endedAt,
                durationMs: run.endedAt - run.startedAt,
                model: friendlyModelName(run.model),
                timestamp: new Date(run.endedAt).toISOString()
            };

            completedResults.unshift(result);
            if (completedResults.length > 50) completedResults = completedResults.slice(0, 50);

            // Telegram notification
            const emoji = result.status === 'completed' ? '✅' : '❌';
            sendTelegramNotification(`${emoji} *${result.agentName}* ${result.status}\n${run.task?.substring(0, 200) || 'Task'}`);

            // Update agent state
            if (agentStates[agentId]) {
                agentStates[agentId] = {
                    status: 'idle',
                    action: `Completed: ${run.task?.substring(0, 40) || 'task'}...`,
                    task: run.task,
                    lastResult: result,
                    timestamp: new Date().toISOString()
                };
            }

            console.log(`[COMPLETION] ${agent?.name || agentId}: "${run.task?.substring(0, 60)}" → ${run.outcome?.status} (${Math.round((run.endedAt - run.startedAt) / 1000)}s)`);
        } else if (run.startedAt && !run.endedAt) {
            // Run is in progress
            const parts = (run.childSessionKey || '').split(':');
            const agentId = parts[1] || 'unknown';
            if (agentStates[agentId] && agentStates[agentId].status !== 'running') {
                agentStates[agentId] = {
                    status: 'running',
                    action: run.task?.substring(0, 60) || 'Working...',
                    task: run.task,
                    runId: runId,
                    startedAt: run.startedAt,
                    timestamp: new Date().toISOString()
                };
                console.log(`[RUNNING] ${agentId}: "${run.task?.substring(0, 60)}"`);
            }
        }
    }
}

// ─── Completion Detection: Agent directory file watcher ────────────────

function snapshotAgentDir(agentId) {
    const agent = AGENTS.find(a => a.id === agentId);
    if (!agent || agentId === 'main') return {};

    try {
        const files = fs.readdirSync(agent.workspace);
        const snapshot = {};
        for (const f of files) {
            if (f.startsWith('.')) continue;
            try {
                const stat = fs.statSync(path.join(agent.workspace, f));
                snapshot[f] = { size: stat.size, mtime: stat.mtimeMs };
            } catch (e) { /* skip */ }
        }
        return snapshot;
    } catch (e) {
        return {};
    }
}

function detectNewFiles(agentId) {
    const oldSnapshot = agentFileSnapshots[agentId] || {};
    const newSnapshot = snapshotAgentDir(agentId);
    agentFileSnapshots[agentId] = newSnapshot;

    const newFiles = [];
    const modifiedFiles = [];

    for (const [name, info] of Object.entries(newSnapshot)) {
        if (!oldSnapshot[name]) {
            newFiles.push({ name, size: info.size });
        } else if (info.mtime > oldSnapshot[name].mtime) {
            modifiedFiles.push({ name, size: info.size });
        }
    }

    return { newFiles, modifiedFiles };
}

// ─── Completion Detection: Session activity polling ────────────────────

function readSessionsForAgent(agentId) {
    const sessionsFile = path.join(SESSIONS_BASE, agentId, 'sessions', 'sessions.json');
    try {
        const raw = fs.readFileSync(sessionsFile, 'utf8');
        return JSON.parse(raw);
    } catch (e) {
        return { sessions: {} };
    }
}

// Cache for agent token stats (recalculated every 30s)
let agentTokenCache = {};
let agentTokenCacheTime = 0;
const TOKEN_CACHE_TTL = 30000;

// Baselines: when user resets tokens, we snapshot current totals so display shows delta
const agentTokenBaselines = {
    main: { totalTokens: 0, totalCost: 0, inputTokens: 0, outputTokens: 0 },
    guido: { totalTokens: 0, totalCost: 0, inputTokens: 0, outputTokens: 0 },
    newton: { totalTokens: 0, totalCost: 0, inputTokens: 0, outputTokens: 0 },
    bronte: { totalTokens: 0, totalCost: 0, inputTokens: 0, outputTokens: 0 }
};

function resetAgentTokens(agentId) {
    // Snapshot current grand totals as the new baseline
    agentTokenCacheTime = 0; // force recalc
    const raw = calcTokenStatsRaw(agentId);
    agentTokenBaselines[agentId] = {
        totalTokens: raw.totalTokens,
        totalCost: raw.totalCost,
        inputTokens: raw.inputTokens,
        outputTokens: raw.outputTokens
    };
    // Clear cache so next read picks up the reset
    delete agentTokenCache[agentId];
    agentTokenCacheTime = 0;
}

function resetAllAgentTokens() {
    for (const agent of AGENTS) {
        resetAgentTokens(agent.id);
    }
}

function getAgentTokenStats(agentId) {
    const now = Date.now();
    if (now - agentTokenCacheTime < TOKEN_CACHE_TTL && agentTokenCache[agentId]) {
        return agentTokenCache[agentId];
    }

    // Recalculate all agents at once
    if (now - agentTokenCacheTime >= TOKEN_CACHE_TTL) {
        agentTokenCacheTime = now;
        for (const agent of AGENTS) {
            const raw = calcTokenStatsRaw(agent.id);
            const baseline = agentTokenBaselines[agent.id] || { totalTokens: 0, totalCost: 0, inputTokens: 0, outputTokens: 0 };
            agentTokenCache[agent.id] = {
                totalTokens: Math.max(0, raw.totalTokens - baseline.totalTokens),
                totalCost: Math.max(0, raw.totalCost - baseline.totalCost),
                inputTokens: Math.max(0, raw.inputTokens - baseline.inputTokens),
                outputTokens: Math.max(0, raw.outputTokens - baseline.outputTokens),
                sessionCount: raw.sessionCount,
                latestTimestamp: raw.latestTimestamp
            };
        }
    }

    return agentTokenCache[agentId] || { totalTokens: 0, totalCost: 0, sessionCount: 0, inputTokens: 0, outputTokens: 0 };
}

function calcTokenStatsRaw(agentId) {
    const sessionsDir = path.join(SESSIONS_BASE, agentId, 'sessions');
    let totalTokens = 0, totalCost = 0, inputTokens = 0, outputTokens = 0;
    let sessionCount = 0, latestTimestamp = 0;

    try {
        const files = fs.readdirSync(sessionsDir).filter(f => f.endsWith('.jsonl'));
        sessionCount = files.length;

        for (const file of files) {
            try {
                const raw = fs.readFileSync(path.join(sessionsDir, file), 'utf8');
                for (const line of raw.split('\n')) {
                    if (!line.trim()) continue;
                    try {
                        const d = JSON.parse(line);
                        if (d.type === 'message' && d.message?.role === 'assistant' && d.message?.usage) {
                            const u = d.message.usage;
                            totalTokens += u.totalTokens || 0;
                            inputTokens += u.input || 0;
                            outputTokens += u.output || 0;
                            totalCost += u.cost?.total || 0;
                        }
                        if (d.timestamp) {
                            const ts = new Date(d.timestamp).getTime();
                            if (ts > latestTimestamp) latestTimestamp = ts;
                        }
                    } catch (e) { /* skip malformed line */ }
                }
            } catch (e) { /* skip unreadable file */ }
        }
    } catch (e) { /* no sessions dir */ }

    return { totalTokens, totalCost, inputTokens, outputTokens, sessionCount, latestTimestamp };
}

function getAgentSessionActivity(agentId) {
    const tokenStats = getAgentTokenStats(agentId);

    return {
        sessionCount: tokenStats.sessionCount,
        totalTokens: tokenStats.totalTokens,
        totalCost: tokenStats.totalCost,
        inputTokens: tokenStats.inputTokens,
        outputTokens: tokenStats.outputTokens,
        latestUpdate: tokenStats.latestTimestamp,
        ageMs: tokenStats.latestTimestamp ? Date.now() - tokenStats.latestTimestamp : null
    };
}

// ─── Agent performance metrics ──────────────────────────────────────────

function getAgentPerformance(agentId) {
    const results = completedResults.filter(r => r.agent === agentId);
    if (results.length === 0) return { taskCount: 0, successRate: 0, avgDurationMs: 0, errors: 0 };

    const completed = results.filter(r => r.status === 'completed');
    const errors = results.filter(r => r.status === 'error');
    const withDuration = results.filter(r => r.durationMs > 0);
    const avgDurationMs = withDuration.length > 0
        ? Math.round(withDuration.reduce((sum, r) => sum + r.durationMs, 0) / withDuration.length)
        : 0;

    return {
        taskCount: results.length,
        successRate: results.length > 0 ? Math.round((completed.length / results.length) * 100) : 0,
        avgDurationMs,
        errors: errors.length
    };
}

// ─── Combined status endpoint ──────────────────────────────────────────

function getFullAgentStatus() {
    // Check runs.json for any updates
    checkRunsForCompletions();

    const activities = [];

    for (const agentDef of AGENTS) {
        const localState = agentStates[agentDef.id] || { status: 'idle', action: 'Idle' };
        const sessionInfo = getAgentSessionActivity(agentDef.id);
        const fileChanges = agentDef.id !== 'main' ? detectNewFiles(agentDef.id) : { newFiles: [], modifiedFiles: [] };

        // Determine real status from multiple signals
        let status = localState.status;
        let action = localState.action;

        // If session was updated very recently (within 30s), agent is likely active
        if (sessionInfo.ageMs !== null && sessionInfo.ageMs < 30000 && status !== 'running') {
            status = 'active';
            action = 'Processing...';
        }

        // If we have new files, that's a completion signal
        if (fileChanges.newFiles.length > 0) {
            const fileNames = fileChanges.newFiles.map(f => f.name).join(', ');
            console.log(`[FILES] ${agentDef.name}: New files: ${fileNames}`);
        }

        activities.push({
            agent: agentDef.id,
            agentName: agentDef.name,
            action: action,
            status: status,
            task: localState.task || null,
            output: localState.output || null,
            lastResult: localState.lastResult || null,
            tokens: sessionInfo.totalTokens || null,
            totalCost: sessionInfo.totalCost || 0,
            inputTokens: sessionInfo.inputTokens || 0,
            outputTokens: sessionInfo.outputTokens || 0,
            sessionCount: sessionInfo.sessionCount,
            latestSessionAge: sessionInfo.ageMs,
            newFiles: fileChanges.newFiles,
            modifiedFiles: fileChanges.modifiedFiles,
            timestamp: localState.timestamp,
            hasSession: sessionInfo.sessionCount > 0,
            sessionState: agentSessionState[agentDef.id] || { fresh: true, taskCount: 0 },
            performance: getAgentPerformance(agentDef.id),
            queueLength: (agentQueues[agentDef.id] || []).length,
            queueRunning: agentQueueRunning[agentDef.id] || false,
            currentModel: friendlyModelName(getAgentCurrentModel(agentDef.id))
        });
    }

    // Include terminal output snapshots for streaming
    const terminalOutputs = {};
    for (const agentDef of AGENTS) {
        terminalOutputs[agentDef.id] = agentTerminalOutput[agentDef.id] || '';
    }

    return { activities, completedResults, terminalOutputs, pipelines: activePipelines };
}

// ─── Fetch gateway sessions via CLI ────────────────────────────────────

async function fetchGatewaySessions() {
    return new Promise((resolve) => {
        const proc = spawn('openclaw', ['sessions', '--json'], { cwd: process.env.HOME });
        let stdout = '';

        proc.stdout.on('data', (data) => { stdout += data.toString(); });
        proc.stderr.on('data', () => {});

        proc.on('close', (code) => {
            try {
                if (code === 0 && stdout) {
                    const data = JSON.parse(stdout);
                    resolve(data.sessions || []);
                    return;
                }
            } catch (e) {
                console.error('[Gateway CLI] Parse error:', e.message);
            }
            resolve([]);
        });

        setTimeout(() => { proc.kill(); resolve([]); }, 5000);
    });
}

// ─── Execute openclaw command (non-blocking, via gateway) ──────────────

async function runAgentTask(agentId, task, { freshSession = false, timeoutMs = 300000 } = {}) {
    return new Promise((resolve) => {
        const agent = AGENTS.find(a => a.id === agentId);
        const workspace = agent?.workspace || process.env.HOME;

        // Use gateway (no --local) so it goes through the proper pipeline
        const cmdArgs = [
            'agent',
            '--agent', agentId,
            '--message', task
        ];

        // Force a fresh session with a unique ID — no prior context bleeds through
        let sessionId = null;
        if (freshSession) {
            sessionId = crypto.randomUUID();
            cmdArgs.push('--session-id', sessionId);
            console.log(`[SPAWN] Fresh session ${sessionId.substring(0, 8)}... for ${agentId}`);
        }

        // Update session tracking
        if (agentSessionState[agentId]) {
            agentSessionState[agentId].sessionId = sessionId || agentSessionState[agentId].sessionId;
            agentSessionState[agentId].fresh = freshSession;
            agentSessionState[agentId].taskCount++;
        }

        // Remind the agent where to save files (agents default to cwd but may not know their workspace path)
        if (agentId !== 'main' && !/save.*to|output.*to|write.*to/i.test(task)) {
            task += `\n\nIMPORTANT: Save any output files to your workspace directory: ${workspace}`;
        }

        console.log(`[SPAWN] openclaw agent --agent ${agentId} --message "${task.substring(0, 60)}..."`);

        const proc = spawn('openclaw', cmdArgs, { cwd: workspace });
        let stdout = '';
        let stderr = '';

        // Capture streaming output — filter for terminal display
        agentTerminalOutput[agentId] = '';
        proc.stdout.on('data', (data) => {
            const text = data.toString();
            stdout += text;
            const filtered = filterTerminalOutput(text);
            if (filtered.trim()) {
                agentTerminalOutput[agentId] += filtered;
            }
        });
        proc.stderr.on('data', (data) => {
            const text = data.toString();
            stderr += text;
            const filtered = filterTerminalOutput(text);
            if (filtered.trim()) {
                agentTerminalOutput[agentId] += filtered;
            }
        });

        proc.on('close', (code) => {
            let parsed = null;
            try { parsed = JSON.parse(stdout); } catch (e) { /* not JSON */ }
            resolve({ code, stdout, stderr, parsed });
        });

        // Timeout (default 5 min, configurable per call)
        setTimeout(() => { proc.kill(); resolve({ code: -1, stdout, stderr: 'Timeout', parsed: null }); }, timeoutMs);
    });
}

// ─── Scan agent output directory for result files ──────────────────────

function getAgentOutputFiles(agentId) {
    const agent = AGENTS.find(a => a.id === agentId);
    if (!agent || agentId === 'main') return [];

    try {
        const files = fs.readdirSync(agent.workspace)
            .filter(f => !f.startsWith('.') && !['AGENTS.md', 'BOOTSTRAP.md', 'HEARTBEAT.md', 'IDENTITY.md', 'SOUL.md', 'TOOLS.md', 'USER.md'].includes(f));

        return files.map(f => {
            const fullPath = path.join(agent.workspace, f);
            const stat = fs.statSync(fullPath);
            let preview = '';
            if (stat.isFile() && stat.size < 10000) {
                try { preview = fs.readFileSync(fullPath, 'utf8').substring(0, 500); } catch (e) {}
            }
            return {
                name: f,
                size: stat.size,
                modified: stat.mtime.toISOString(),
                modifiedMs: stat.mtimeMs,
                preview
            };
        }).sort((a, b) => b.modifiedMs - a.modifiedMs);
    } catch (e) {
        return [];
    }
}

// ─── Initialize: snapshot current state ────────────────────────────────

function initializeSnapshots() {
    // Snapshot current agent directories
    for (const agent of AGENTS) {
        if (agent.id !== 'main') {
            agentFileSnapshots[agent.id] = snapshotAgentDir(agent.id);
        }
    }

    // Load known runs (skip bootstrap tasks)
    const runsData = readRunsFile();
    for (const runId of Object.keys(runsData.runs || {})) {
        knownRunIds.add(runId);
        const run = runsData.runs[runId];
        if (run.endedAt && !isBootstrapTask(run.task)) {
            const parts = (run.childSessionKey || '').split(':');
            const agentId = parts[1] || 'unknown';
            const agent = AGENTS.find(a => a.id === agentId);
            completedResults.push({
                id: runId,
                agent: agentId,
                agentName: agent?.name || agentId,
                task: run.task || 'Unknown task',
                status: run.outcome?.status === 'ok' ? 'completed' : 'error',
                startedAt: run.startedAt,
                endedAt: run.endedAt,
                durationMs: run.endedAt - run.startedAt,
                model: friendlyModelName(run.model),
                timestamp: new Date(run.endedAt).toISOString()
            });
        }
    }
    completedResults.sort((a, b) => (b.endedAt || 0) - (a.endedAt || 0));

    console.log(`[INIT] Loaded ${knownRunIds.size} known runs, ${completedResults.length} completed results`);
}

// ─── Background polling ────────────────────────────────────────────────

// Watch runs.json for changes
let runsWatcher = null;
try {
    runsWatcher = fs.watch(RUNS_FILE, { persistent: false }, () => {
        checkRunsForCompletions();
    });
    console.log('[WATCH] Monitoring runs.json for completions');
} catch (e) {
    console.log('[WATCH] Could not watch runs.json, will poll instead');
}

// Poll every 3 seconds as fallback
setInterval(() => {
    checkRunsForCompletions();
}, 3000);

// Watch agent directories for new files
for (const agent of AGENTS) {
    if (agent.id === 'main') continue;
    try {
        fs.watch(agent.workspace, { persistent: false }, (eventType, filename) => {
            if (filename && !filename.startsWith('.')) {
                console.log(`[WATCH] ${agent.name}: ${eventType} ${filename}`);
            }
        });
        console.log(`[WATCH] Monitoring ${agent.name} workspace: ${agent.workspace}`);
    } catch (e) {
        console.log(`[WATCH] Could not watch ${agent.name} workspace`);
    }
}

// ─── Structured output summarisation for pipeline handoffs ──────────

// Role-aware summarisation prompts for structured handoff
const HANDOFF_PROMPTS = {
    newton: `You just completed a research task. Summarise your findings as a JSON object with this exact structure (no markdown fences, just raw JSON):
{
  "summary": "Brief 2-3 sentence overview of what you found",
  "key_findings": ["finding 1", "finding 2", "finding 3"],
  "sources": ["source or reference 1", "source 2"],
  "recommended_angle": "What the next person in the chain should focus on based on your research",
  "confidence": "high or medium or low"
}
Be concise. Focus on the most important facts, conclusions, and actionable details.`,

    bronte: `You just completed a writing/content task. Summarise your output as a JSON object with this exact structure (no markdown fences, just raw JSON):
{
  "summary": "Brief 2-3 sentence overview of what you produced",
  "key_findings": ["key theme or point 1", "key theme 2", "key theme 3"],
  "sources": [],
  "recommended_angle": "What the next person should focus on — tone, audience, structure notes",
  "confidence": "high or medium or low"
}
Be concise. Focus on the narrative structure, hooks, and target audience insights.`,

    guido: `You just completed a coding task. Summarise your output as a JSON object with this exact structure (no markdown fences, just raw JSON):
{
  "summary": "Brief 2-3 sentence overview of what you built",
  "key_findings": ["technical decision 1", "file or component created", "API pattern used"],
  "sources": [],
  "recommended_angle": "What the next person needs to know — dependencies, integration points, next steps",
  "confidence": "high or medium or low"
}
Be concise. Focus on technical decisions, file paths, and dependencies.`,

    default: `Summarise your key findings from the work you just completed as a JSON object with this exact structure (no markdown fences, just raw JSON):
{
  "summary": "Brief 2-3 sentence overview",
  "key_findings": ["finding 1", "finding 2", "finding 3"],
  "sources": [],
  "recommended_angle": "What the next person should focus on",
  "confidence": "high or medium or low"
}
Be concise and focus on actionable details.`
};

function parseHandoff(text) {
    if (!text || text.trim().length === 0) {
        return { summary: '', key_findings: [], sources: [], recommended_angle: '', confidence: 'medium' };
    }

    // Try to parse as JSON directly
    try {
        const parsed = JSON.parse(text.trim());
        if (parsed.summary) return parsed;
    } catch {}

    // Try to extract JSON from markdown fences or surrounding text
    const jsonMatch = text.match(/\{[\s\S]*?"summary"[\s\S]*?\}/);
    if (jsonMatch) {
        try {
            const parsed = JSON.parse(jsonMatch[0]);
            if (parsed.summary) return parsed;
        } catch {}
    }

    // Fallback: wrap raw text as unstructured handoff
    return {
        summary: text.substring(0, 500),
        key_findings: [],
        sources: [],
        recommended_angle: '',
        confidence: 'medium'
    };
}

function formatHandoffForInjection(handoff, agentName) {
    let formatted = `## Handoff from ${agentName}\n`;
    formatted += `**Summary:** ${handoff.summary}\n`;
    if (handoff.key_findings && handoff.key_findings.length > 0) {
        formatted += `**Key Findings:**\n`;
        handoff.key_findings.forEach(f => { formatted += `- ${f}\n`; });
    }
    if (handoff.recommended_angle) {
        formatted += `**Recommended Angle:** ${handoff.recommended_angle}\n`;
    }
    if (handoff.sources && handoff.sources.length > 0) {
        formatted += `**Sources:**\n`;
        handoff.sources.forEach(s => { formatted += `- ${s}\n`; });
    }
    if (handoff.confidence) {
        formatted += `**Confidence:** ${handoff.confidence}\n`;
    }
    return formatted;
}

async function summariseOutput(agentId, rawOutput) {
    if (!rawOutput || rawOutput.trim().length === 0) {
        return { handoff: parseHandoff(''), raw: '', formatted: '' };
    }

    const basePrompt = HANDOFF_PROMPTS[agentId] || HANDOFF_PROMPTS.default;
    const agentName = AGENTS.find(a => a.id === agentId)?.name || agentId;

    // Include raw output directly in the prompt so summarisation never relies on session memory
    const truncatedOutput = rawOutput.substring(0, 4000);
    const prompt = `Here is the raw output from the task you just completed:\n\n---\n${truncatedOutput}\n---\n\n${basePrompt}`;

    console.log(`[SUMMARISE] Asking ${agentId} to summarise ${rawOutput.length} chars of output (${truncatedOutput.length} included in prompt)...`);

    try {
        const result = await runAgentTask(agentId, prompt, { freshSession: false, timeoutMs: 60000 });
        const summaryText = (result.stdout || '').trim();

        if (result.code === 0 && summaryText.length > 0) {
            const handoff = parseHandoff(summaryText);
            const formatted = formatHandoffForInjection(handoff, agentName);
            console.log(`[SUMMARISE] ${agentId}: got ${summaryText.length} char summary (from ${rawOutput.length} chars raw), structured: ${handoff.key_findings.length} findings`);
            return { handoff, raw: summaryText, formatted };
        }
    } catch (e) {
        console.log(`[SUMMARISE] ${agentId}: summarisation failed: ${e.message}`);
    }

    // Fallback: truncated raw output
    console.log(`[SUMMARISE] ${agentId}: falling back to truncated raw output (3000 chars)`);
    const fallbackText = rawOutput.substring(0, 3000);
    const handoff = parseHandoff(fallbackText);
    const formatted = formatHandoffForInjection(handoff, agentName);
    return { handoff, raw: fallbackText, formatted };
}

// ─── Pipeline Report Generation ──────────────────────────────────────

function generatePipelineReport(pipeline) {
    const startMs = new Date(pipeline.startedAt).getTime();
    const endMs = new Date(pipeline.endedAt).getTime();
    const totalDuration = endMs - startMs;

    const steps = pipeline.steps.map((step, i) => {
        const agent = AGENTS.find(a => a.id === step.agentId);
        const stepStartMs = step.startedAt ? new Date(step.startedAt).getTime() : startMs;
        const stepEndMs = step.endedAt ? new Date(step.endedAt).getTime() : endMs;
        const duration = stepEndMs - stepStartMs;

        // Detect output files created during this step's window
        const outputFiles = detectDeliverables(step.agentId, stepStartMs, stepEndMs);

        return {
            index: i,
            agent: agent?.name || step.agentId,
            agentId: step.agentId,
            task: step.taskTemplate || step.task || '',
            status: step.status,
            duration,
            handoff: step.handoff || null,
            summary: step.summary || '',
            output: (step.output || '').substring(0, 3000),
            outputFiles,
            overridden: step.overridden || false
        };
    });

    // Deliverables = files from the final step (or all steps if final has none)
    const finalStep = steps[steps.length - 1];
    let deliverables = finalStep?.outputFiles || [];
    if (deliverables.length === 0) {
        // Fall back to all files from all steps
        deliverables = steps.flatMap(s => s.outputFiles.map(f => ({ ...f, fromAgent: s.agent })));
    }

    return {
        pipelineId: pipeline.id,
        goal: pipeline.name,
        status: pipeline.status,
        totalDuration,
        startedAt: pipeline.startedAt,
        endedAt: pipeline.endedAt,
        steps,
        deliverables
    };
}

function detectDeliverables(agentId, startMs, endMs) {
    const agent = AGENTS.find(a => a.id === agentId);
    if (!agent || agentId === 'main') return [];

    try {
        const files = fs.readdirSync(agent.workspace)
            .filter(f => !f.startsWith('.') && !['AGENTS.md', 'BOOTSTRAP.md', 'HEARTBEAT.md', 'IDENTITY.md', 'SOUL.md', 'TOOLS.md', 'USER.md', 'MEMORY.md', 'CLAUDE.md'].includes(f));

        return files
            .map(f => {
                const fullPath = path.join(agent.workspace, f);
                try {
                    const stat = fs.statSync(fullPath);
                    if (!stat.isFile()) return null;
                    return {
                        name: f,
                        path: fullPath,
                        size: stat.size,
                        modifiedMs: stat.mtimeMs,
                        agent: agent.name
                    };
                } catch { return null; }
            })
            .filter(f => f && f.modifiedMs >= startMs - 2000 && f.modifiedMs <= endMs + 2000)
            .sort((a, b) => b.modifiedMs - a.modifiedMs);
    } catch {
        return [];
    }
}

// ─── HTTP Server ───────────────────────────────────────────────────────

const server = http.createServer(async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // Serve HTML
    if (req.url === '/' || req.url === '/index.html') {
        fs.readFile(HTML_FILE, (err, data) => {
            if (err) { res.writeHead(500); res.end('Error loading page'); return; }
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(data);
        });
        return;
    }

    // GET/POST kanban data
    if (req.url === '/data' && req.method === 'GET') {
        fs.readFile(DATA_FILE, 'utf8', (err, data) => {
            if (err) { res.writeHead(500); res.end(JSON.stringify({ error: 'Error reading data' })); return; }
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(data);
        });
        return;
    }

    if (req.url === '/data' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                fs.writeFile(DATA_FILE, JSON.stringify(data, null, 2), (err) => {
                    if (err) { res.writeHead(500); res.end(JSON.stringify({ error: 'Error saving data' })); return; }
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: true }));
                });
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: 'Invalid JSON' }));
            }
        });
        return;
    }

    // List agents
    if (req.url === '/agents' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ agents: AGENTS }));
        return;
    }

    // ─── Agent activity (main polling endpoint for dashboard) ──────────
    if (req.url === '/agents/activity' && req.method === 'GET') {
        try {
            const fullStatus = getFullAgentStatus();
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(fullStatus));
        } catch (e) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: e.message }));
        }
        return;
    }

    // ─── Completed results endpoint ───────────────────────────────────
    if (req.url === '/agents/results' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ results: completedResults }));
        return;
    }

    // ─── Agent output files endpoint ──────────────────────────────────
    if (req.url.startsWith('/agents/files/') && req.method === 'GET') {
        const agentId = req.url.split('/').pop();
        const files = getAgentOutputFiles(agentId);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ agentId, files }));
        return;
    }

    // ─── Clear agent context ────────────────────────────────────────
    if (req.url === '/agents/clear-context' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const { agentId } = JSON.parse(body);
                const agent = AGENTS.find(a => a.id === agentId);
                if (!agent) {
                    res.writeHead(400);
                    res.end(JSON.stringify({ error: 'Unknown agent' }));
                    return;
                }

                // Reset session state — next task will use a fresh session
                agentSessionState[agentId] = { sessionId: null, fresh: true, taskCount: 0 };

                // Clear terminal output
                agentTerminalOutput[agentId] = '';

                console.log(`[CLEAR] ${agent.name}: session context cleared`);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, message: `${agent.name} context cleared` }));
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    // ─── Reset token tracking ──────────────────────────────────────
    if (req.url === '/agents/reset-tokens' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const { agentId } = JSON.parse(body);
                if (agentId === 'all') {
                    resetAllAgentTokens();
                    console.log('[TOKENS] All agent token counters reset');
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: true, message: 'All token counters reset' }));
                } else {
                    const agent = AGENTS.find(a => a.id === agentId);
                    if (!agent) {
                        res.writeHead(400);
                        res.end(JSON.stringify({ error: 'Unknown agent' }));
                        return;
                    }
                    resetAgentTokens(agentId);
                    console.log(`[TOKENS] ${agent.name}: token counter reset`);
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: true, message: `${agent.name} token counter reset` }));
                }
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    // ─── Telegram config ────────────────────────────────────────────
    if (req.url === '/telegram/config' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            hasToken: !!telegramBotToken,
            chatId: telegramChatId,
            enabled: telegramEnabled
        }));
        return;
    }

    if (req.url === '/telegram/config' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const { chatId, enabled } = JSON.parse(body);
                if (chatId !== undefined) telegramChatId = String(chatId);
                if (enabled !== undefined) telegramEnabled = !!enabled;
                console.log(`[TELEGRAM] Config updated: enabled=${telegramEnabled}, chatId=${telegramChatId}`);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, enabled: telegramEnabled, chatId: telegramChatId }));
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    if (req.url === '/telegram/test' && req.method === 'POST') {
        if (!telegramBotToken) {
            res.writeHead(400);
            res.end(JSON.stringify({ error: 'No bot token configured in openclaw.json' }));
            return;
        }
        if (!telegramChatId) {
            res.writeHead(400);
            res.end(JSON.stringify({ error: 'No chat ID set. Enter your Telegram chat ID first.' }));
            return;
        }
        // Temporarily enable for test
        const wasEnabled = telegramEnabled;
        telegramEnabled = true;
        sendTelegramNotification('🧪 *Mission Control* test notification\nTelegram integration is working!');
        telegramEnabled = wasEnabled;
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: true, message: 'Test notification sent' }));
        return;
    }

    // ─── Model selection ──────────────────────────────────────────────
    if (req.url === '/models' && req.method === 'GET') {
        // Reload config to pick up any external changes
        loadAvailableModels();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            models: availableModels,
            default: defaultModel,
            defaultName: friendlyModelName(defaultModel),
            agentModels: Object.fromEntries(
                Object.entries(agentModels).map(([k, v]) => [k, v])
            )
        }));
        return;
    }

    if (req.url === '/models/set' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const { agentId, modelId } = JSON.parse(body);
                const agent = AGENTS.find(a => a.id === agentId);
                if (!agent) {
                    res.writeHead(400);
                    res.end(JSON.stringify({ error: 'Unknown agent' }));
                    return;
                }
                if (!modelId) {
                    res.writeHead(400);
                    res.end(JSON.stringify({ error: 'No model specified' }));
                    return;
                }

                console.log(`[MODELS] Setting ${agent.name} model to ${modelId}`);

                // Use openclaw CLI to persist the model change
                const proc = spawn('openclaw', ['models', '--agent', agentId, 'set', modelId], {
                    cwd: process.env.HOME
                });
                let stdout = '';
                let stderr = '';
                proc.stdout.on('data', d => stdout += d.toString());
                proc.stderr.on('data', d => stderr += d.toString());
                proc.on('close', (code) => {
                    if (code === 0) {
                        agentModels[agentId] = modelId;
                        console.log(`[MODELS] ${agent.name} model set to ${friendlyModelName(modelId)}`);
                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({
                            success: true,
                            model: friendlyModelName(modelId),
                            modelId: modelId
                        }));
                    } else {
                        console.log(`[MODELS] Failed to set model: ${stderr}`);
                        res.writeHead(500, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({
                            error: `Failed to set model: ${stderr.substring(0, 200)}`
                        }));
                    }
                });

                // Timeout
                setTimeout(() => {
                    proc.kill();
                }, 10000);
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    // ─── Task Queue ──────────────────────────────────────────────────
    if (req.url === '/agents/queue' && req.method === 'GET') {
        const queues = {};
        for (const [id, q] of Object.entries(agentQueues)) {
            queues[id] = { tasks: q, running: agentQueueRunning[id] };
        }
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ queues }));
        return;
    }

    if (req.url === '/agents/queue' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const { agentId, task } = JSON.parse(body);
                const agent = AGENTS.find(a => a.id === agentId);
                if (!agent) { res.writeHead(400); res.end(JSON.stringify({ error: 'Unknown agent' })); return; }
                if (!task) { res.writeHead(400); res.end(JSON.stringify({ error: 'No task' })); return; }
                const item = enqueueTask(agentId, task);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, item, queueLength: agentQueues[agentId].length }));
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    if (req.url === '/agents/queue/clear' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const { agentId } = JSON.parse(body);
                if (agentId === 'all') {
                    for (const id of Object.keys(agentQueues)) agentQueues[id] = [];
                } else {
                    agentQueues[agentId] = [];
                }
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true }));
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    // ─── Scheduled Tasks ─────────────────────────────────────────────
    if (req.url === '/schedules' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ schedules: scheduledTasks }));
        return;
    }

    if (req.url === '/schedules' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const { agentId, task, hour, minute, days, enabled } = JSON.parse(body);
                const agent = AGENTS.find(a => a.id === agentId);
                if (!agent) { res.writeHead(400); res.end(JSON.stringify({ error: 'Unknown agent' })); return; }
                const sched = {
                    id: `sched-${++scheduleIdCounter}`,
                    agentId, task,
                    hour: parseInt(hour) || 0,
                    minute: parseInt(minute) || 0,
                    days: days || [],
                    enabled: enabled !== false,
                    createdAt: new Date().toISOString(),
                    lastRun: null
                };
                scheduledTasks.push(sched);
                saveSchedules();
                console.log(`[SCHEDULE] Created: ${sched.id} - ${agent.name} at ${sched.hour}:${String(sched.minute).padStart(2, '0')}`);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, schedule: sched }));
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    if (req.url === '/schedules/delete' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const { id } = JSON.parse(body);
                scheduledTasks = scheduledTasks.filter(s => s.id !== id);
                saveSchedules();
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true }));
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    // ─── Spawn / task agent ───────────────────────────────────────────
    if (req.url === '/agents/spawn' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', async () => {
            try {
                const { agentId, task, spawnOnly, stopTask } = JSON.parse(body);
                const agent = AGENTS.find(a => a.id === agentId);

                if (!agent) {
                    res.writeHead(400);
                    res.end(JSON.stringify({ error: 'Unknown agent' }));
                    return;
                }

                // Handle stop task
                if (stopTask) {
                    agentStates[agentId] = {
                        status: 'idle',
                        action: 'Stopped',
                        task: null,
                        timestamp: new Date().toISOString()
                    };
                    console.log(`[STOP] ${agent.name} task stopped`);
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: true, message: `${agent.name} task stopped` }));
                    return;
                }

                // Spawn-only: just mark agent as ready, don't send a task
                if (spawnOnly) {
                    agentStates[agentId] = {
                        status: 'idle',
                        action: 'Ready',
                        task: null,
                        timestamp: new Date().toISOString()
                    };
                    console.log(`[SPAWN] ${agent.name} marked ready (no task sent)`);
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({
                        success: true,
                        message: `${agent.name} is ready`,
                        status: 'idle'
                    }));
                    return;
                }

                // Mark agent as running immediately
                agentStates[agentId] = {
                    status: 'running',
                    action: task,
                    task: task,
                    timestamp: new Date().toISOString()
                };

                // Respond immediately — the task runs in background
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: true,
                    task: task,
                    message: `${agent.name}: ${task}`,
                    status: 'running',
                    note: 'Task dispatched. Poll /agents/activity for status updates.'
                }));

                // Run the actual task in background
                // If session was cleared, use a fresh session for this task too
                const useFresh = agentSessionState[agentId]?.fresh && agentSessionState[agentId]?.taskCount === 0;
                console.log(`[SPAWN] ${agent.name}: "${task.substring(0, 80)}" (fresh=${useFresh})`);
                if (agentSessionState[agentId]) {
                    agentSessionState[agentId].fresh = false;
                    agentSessionState[agentId].taskCount++;
                }
                const result = await runAgentTask(agentId, task, { freshSession: useFresh });

                // Update state when done
                const output = result.stdout || result.stderr || 'Task completed';
                const endTime = Date.now();
                const startTime = new Date(agentStates[agentId]?.timestamp || endTime).getTime();

                agentStates[agentId] = {
                    status: 'idle',
                    action: `Completed: ${task.substring(0, 40)}`,
                    task: task,
                    output: output.substring(0, 2000),
                    timestamp: new Date().toISOString()
                };

                console.log(`[DONE] ${agent.name}: code=${result.code}`);

                // runs.json watcher will also pick up the completion
                checkRunsForCompletions();

                // If runs.json didn't already capture this (e.g. Newton/Bronte tasks),
                // add a CLI-based result to completedResults directly
                const alreadyCaptured = completedResults.some(r =>
                    r.agent === agentId && r.task === task && Math.abs((r.endedAt || 0) - endTime) < 30000
                );
                if (!alreadyCaptured) {
                    const cliResultId = `cli-${agentId}-${endTime}`;
                    const cliResult = {
                        id: cliResultId,
                        agent: agentId,
                        agentName: agent.name,
                        task: task,
                        status: result.code === 0 ? 'completed' : 'error',
                        startedAt: startTime,
                        endedAt: endTime,
                        durationMs: endTime - startTime,
                        model: '',
                        timestamp: new Date(endTime).toISOString()
                    };
                    completedResults.unshift(cliResult);
                    if (completedResults.length > 50) completedResults = completedResults.slice(0, 50);
                    console.log(`[RESULT] Added CLI result for ${agent.name}: "${task.substring(0, 60)}"`);

                    const emoji = cliResult.status === 'completed' ? '✅' : '❌';
                    sendTelegramNotification(`${emoji} *${agent.name}* ${cliResult.status}\n${task.substring(0, 200)}`);
                }

            } catch (e) {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false, error: e.message }));
            }
        });
        return;
    }

    // Terminal output for agent
    if (req.url.startsWith('/agents/terminal/') && req.method === 'GET') {
        const agentId = req.url.split('/').pop();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            agentId,
            output: agentTerminalOutput[agentId] || '',
            timestamp: new Date().toISOString()
        }));
        return;
    }

    // ─── Pipeline endpoint ─────────────────────────────────────────────
    if (req.url === '/agents/pipeline' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', async () => {
            try {
                const { steps, name, reviewGates } = JSON.parse(body);
                // steps: [{ agentId, taskTemplate }]
                // taskTemplate can include {{input}} which gets replaced with previous output

                if (!steps || !Array.isArray(steps) || steps.length < 2) {
                    res.writeHead(400);
                    res.end(JSON.stringify({ error: 'Pipeline needs at least 2 steps' }));
                    return;
                }

                const pipelineId = `pipeline-${++pipelineIdCounter}-${Date.now()}`;
                const pipeline = {
                    id: pipelineId,
                    name: name || steps.map(s => {
                        const a = AGENTS.find(ag => ag.id === s.agentId);
                        return a?.name || s.agentId;
                    }).join(' → '),
                    reviewGates: !!reviewGates,
                    steps: steps.map((s, i) => ({
                        ...s,
                        index: i,
                        status: 'pending',
                        output: null,
                        summary: null
                    })),
                    status: 'running',
                    startedAt: new Date().toISOString(),
                    currentStep: 0
                };

                activePipelines.unshift(pipeline);
                if (activePipelines.length > 20) activePipelines = activePipelines.slice(0, 20);

                // Respond immediately
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, pipelineId, pipeline }));

                // Run pipeline steps sequentially
                let previousOutput = '';
                console.log(`[PIPELINE] Starting ${pipeline.steps.length}-step pipeline: ${pipeline.name}`);
                for (let i = 0; i < pipeline.steps.length; i++) {
                    const step = pipeline.steps[i];
                    pipeline.currentStep = i;
                    step.status = 'running';
                    step.startedAt = new Date().toISOString();

                    const agent = AGENTS.find(a => a.id === step.agentId);
                    console.log(`[PIPELINE] === Step ${i + 1}/${pipeline.steps.length} ===`);
                    console.log(`[PIPELINE] Agent: ${agent?.name || step.agentId}`);
                    console.log(`[PIPELINE] Previous output length: ${previousOutput.length} chars`);

                    // Replace {{input}} with previous step output
                    let task = step.taskTemplate || step.task || '';
                    console.log(`[PIPELINE] Raw task template (first 100): "${task.substring(0, 100)}"`);
                    if (previousOutput) {
                        task = task.replace(/\{\{input\}\}/g, previousOutput);
                        // If no {{input}} placeholder, append context
                        if (!step.taskTemplate?.includes('{{input}}') && !step.task?.includes('{{input}}')) {
                            task += `\n\nContext from previous step:\n${previousOutput}`;
                        }
                        console.log(`[PIPELINE] Injected context. Final task length: ${task.length} chars`);
                    } else {
                        console.log(`[PIPELINE] No previous output to inject (first step)`);
                    }
                    step.task = task;

                    // Mark agent as running
                    agentStates[step.agentId] = {
                        status: 'running',
                        action: `Pipeline: ${task.substring(0, 50)}...`,
                        task: task,
                        timestamp: new Date().toISOString()
                    };

                    console.log(`[PIPELINE] Dispatching to ${agent?.name}...`);

                    try {
                        const result = await runAgentTask(step.agentId, task, { freshSession: true });
                        console.log(`[PIPELINE] Step ${i + 1} returned: code=${result.code}, stdout=${result.stdout?.length || 0} chars, stderr=${result.stderr?.length || 0} chars`);
                        console.log(`[PIPELINE] stdout preview: "${(result.stdout || '').substring(0, 150)}"`);

                        const output = result.stdout || result.stderr || '';
                        step.output = output.substring(0, 5000);
                        step.status = result.code === 0 ? 'completed' : 'error';
                        step.endedAt = new Date().toISOString();
                        previousOutput = output;

                        console.log(`[PIPELINE] Step ${i + 1} status: ${step.status}`);
                    } catch (stepErr) {
                        console.error(`[PIPELINE] Step ${i + 1} THREW: ${stepErr.message}`);
                        console.error(stepErr.stack);
                        step.status = 'error';
                        step.output = stepErr.message;
                        step.endedAt = new Date().toISOString();
                    }

                    // Update agent state
                    const endTime = Date.now();
                    agentStates[step.agentId] = {
                        status: 'idle',
                        action: `Completed: ${(step.taskTemplate || task).substring(0, 40)}`,
                        task: task,
                        output: (step.output || '').substring(0, 2000),
                        timestamp: new Date().toISOString()
                    };

                    // Add to completed results
                    const cliResultId = `pipeline-${pipelineId}-step-${i}-${endTime}`;
                    completedResults.unshift({
                        id: cliResultId,
                        agent: step.agentId,
                        agentName: agent?.name || step.agentId,
                        task: step.taskTemplate || task,
                        status: step.status,
                        durationMs: 0,
                        model: '',
                        timestamp: new Date().toISOString(),
                        pipeline: pipeline.name,
                        pipelineStep: i + 1
                    });
                    if (completedResults.length > 50) completedResults = completedResults.slice(0, 50);

                    const pEmoji = step.status === 'completed' ? '✅' : '❌';
                    sendTelegramNotification(`${pEmoji} *${agent?.name}* ${step.status} (pipeline step ${i + 1}/${pipeline.steps.length})\n${(step.taskTemplate || task).substring(0, 200)}`);

                    // If step failed, pause for user retry/override/abort
                    if (step.status === 'error') {
                        console.log(`[PIPELINE] Step ${i + 1} failed (${agent?.name}) — waiting for user action`);
                        pipeline.status = 'step_error';
                        step.status = 'error';

                        const errorAction = await new Promise(resolve => {
                            pipeline._errorResolve = resolve;
                        });
                        delete pipeline._errorResolve;

                        if (errorAction.action === 'retry') {
                            console.log(`[PIPELINE] Retrying step ${i + 1}${errorAction.editedTask ? ' with edited task' : ''}...`);
                            if (errorAction.editedTask) {
                                step.task = errorAction.editedTask;
                                step.taskTemplate = errorAction.editedTask;
                            }
                            step.status = 'running';
                            pipeline.status = 'running';
                            i--; // re-run this step
                            continue;
                        } else if (errorAction.action === 'override') {
                            console.log(`[PIPELINE] Overriding step ${i + 1} with user-provided output`);
                            previousOutput = errorAction.output || '';
                            step.output = previousOutput.substring(0, 5000);
                            step.status = 'completed';
                            step.overridden = true;
                            pipeline.status = 'running';
                        } else {
                            // abort
                            pipeline.status = 'error';
                            console.log(`[PIPELINE] ABORTED by user at step ${i + 1}`);
                            break;
                        }
                    }

                    // Summarise output for handoff to next step (non-final steps only)
                    if (i < pipeline.steps.length - 1) {
                        step.status = 'summarising';
                        console.log(`[PIPELINE] Summarising step ${i + 1} output for handoff...`);
                        const { handoff, raw, formatted } = await summariseOutput(step.agentId, previousOutput);
                        step.summary = formatted;
                        step.handoff = handoff;
                        step.status = 'completed';
                        previousOutput = formatted;
                        console.log(`[PIPELINE] Step ${i + 1} summary ready (${formatted.length} chars, ${handoff.key_findings.length} findings)`);

                        // Update the result entry with summary data
                        const existingResult = completedResults.find(r => r.id === cliResultId);
                        if (existingResult) {
                            existingResult.summary = formatted.substring(0, 3000);
                            existingResult.hasFullOutput = true;
                        }

                        // Review gate: pause for user approval before next step
                        if (pipeline.reviewGates) {
                            console.log(`[PIPELINE] Review gate after step ${i + 1} — waiting for user approval`);
                            step.status = 'awaiting_review';
                            pipeline.status = 'awaiting_review';

                            const review = await new Promise(resolve => {
                                pipeline._reviewResolve = resolve;
                            });
                            delete pipeline._reviewResolve;

                            if (review.action === 'approve') {
                                if (review.editedHandoff) {
                                    // User edited structured fields — rebuild formatted output
                                    step.handoff = review.editedHandoff;
                                    const agentName = AGENTS.find(a => a.id === step.agentId)?.name || step.agentId;
                                    previousOutput = formatHandoffForInjection(review.editedHandoff, agentName);
                                } else if (review.editedSummary) {
                                    previousOutput = review.editedSummary;
                                } else {
                                    // Use formatted handoff as-is
                                }
                                step.summary = previousOutput;
                            } else if (review.action === 'skip') {
                                previousOutput = '';
                            }
                            step.status = 'completed';
                            pipeline.status = 'running';
                            console.log(`[PIPELINE] Review gate resolved: ${review.action}`);
                        }
                    }

                    console.log(`[PIPELINE] Step ${i + 1} complete. Checking for next step...`);
                }

                if (pipeline.status !== 'error') {
                    pipeline.status = 'completed';
                }
                pipeline.endedAt = new Date().toISOString();
                console.log(`[PIPELINE] Pipeline finished: ${pipeline.status}`);

                // Generate pipeline report
                if (pipeline.status === 'completed') {
                    pipeline.report = generatePipelineReport(pipeline);
                    console.log(`[REPORT] Generated report for ${pipeline.id}: ${pipeline.report.deliverables.length} deliverables`);
                    savePipelines();
                }

            } catch (e) {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false, error: e.message }));
            }
        });
        return;
    }

    // ─── Command bar endpoint — Astra decomposes a goal (returns plan for approval) ───
    if (req.url === '/agents/command' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', async () => {
            try {
                const { goal } = JSON.parse(body);
                if (!goal) {
                    res.writeHead(400);
                    res.end(JSON.stringify({ error: 'No goal provided' }));
                    return;
                }

                // Mark Astra as working
                agentStates.main = {
                    status: 'running',
                    action: `Decomposing: ${goal.substring(0, 50)}`,
                    task: goal,
                    timestamp: new Date().toISOString()
                };

                // Ask Astra to decompose the goal into subtasks
                const decompositionPrompt = `You are Astra, the CEO and Project Manager of Automa Dynamics. You manage three specialist agents:

AGENTS:
- Newton (researcher): fact-finding, synthesis, investigation, web research. Outputs: structured findings, source URLs, data, competitor analysis.
- Bronte (content writer): blog posts, landing page copy, YouTube scripts, documentation, editing. Outputs: polished prose, headlines, CTAs, narrative structure.
- Guido (coder): Python, TypeScript, HTML/CSS, debugging, building. Outputs: working code files, scripts, web pages, tools.

USER GOAL: "${goal}"

Decompose this into 1-3 agent tasks. Each task MUST include:
- "agent": which agent (newton/bronte/guido)
- "task": a specific, actionable instruction
- "expectedOutput": what this agent should produce (format, length, key elements)
- "successCriteria": how we'll know this step succeeded
- "handoffNote": what the NEXT agent needs from this step's output (omit for the final step)
- "dependsOn": index of the task this depends on (omit for independent/first tasks)

Output ONLY valid JSON (no markdown, no explanation):
{"tasks":[{"agent":"newton","task":"...","expectedOutput":"...","successCriteria":"...","handoffNote":"...","dependsOn":0}]}

EXAMPLES:

Goal: "Build me a landing page for a productivity app"
{"tasks":[{"agent":"newton","task":"Research the top 5 productivity apps (Notion, Todoist, Asana, ClickUp, Linear). For each, note: tagline, hero section approach, key features highlighted, pricing model, and CTA text. List 3 common patterns across all.","expectedOutput":"Structured comparison table with URLs, plus 3 common landing page patterns","successCriteria":"At least 5 competitors analysed with specific quotes/examples from their landing pages","handoffNote":"Bronte needs the competitor patterns and best tagline examples to write compelling copy","dependsOn":null},{"agent":"bronte","task":"Write landing page copy: hero headline + subheadline, 3 feature sections with headlines and 2-sentence descriptions, a social proof section placeholder, and a CTA section. Tone: confident but not pushy. Keep it under 400 words total.","expectedOutput":"Complete landing page copy in markdown sections, ready for a developer to implement","successCriteria":"All sections present, copy is specific (not generic), CTAs are actionable","handoffNote":"Guido needs the exact copy text and section structure to build the HTML page","dependsOn":0},{"agent":"guido","task":"Build a responsive HTML landing page using the copy provided. Use a modern design: dark gradient background, clean typography (system fonts), hero section with CTA button, feature grid, footer. Single file, no external dependencies.","expectedOutput":"A single index.html file with embedded CSS, mobile-responsive, production-ready","successCriteria":"Page renders correctly, all copy sections are present, responsive on mobile","dependsOn":1}]}

Goal: "Write a blog post about quantum computing"
{"tasks":[{"agent":"newton","task":"Research quantum computing for a general audience: explain qubits vs classical bits, list 3 real-world applications (with company names), note 2 recent breakthroughs (2024-2025), and identify the biggest current limitation.","expectedOutput":"Research brief with 4 sections, each with specific facts and source URLs","successCriteria":"All 4 sections have concrete facts (not vague), at least 3 source URLs included","handoffNote":"Bronte needs the specific facts, examples, and sources to write an engaging blog post","dependsOn":null},{"agent":"bronte","task":"Write a 600-800 word blog post about quantum computing for a general audience. Use a hook opening, explain concepts with analogies, include the specific examples and breakthroughs from research. End with a forward-looking conclusion. Conversational tone.","expectedOutput":"Complete blog post in markdown, 600-800 words, with a compelling title","successCriteria":"Post is engaging for non-technical readers, all research facts are woven in naturally, has a clear narrative arc","dependsOn":0}]}

Goal: "Create a Python script that analyses CSV data"
{"tasks":[{"agent":"guido","task":"Build a Python CLI tool that reads a CSV file, displays summary statistics (row count, column types, missing values per column), and generates a simple report. Use pandas. Include argparse for the file path argument and pretty-print the output.","expectedOutput":"A single Python file (csv_analyser.py) with CLI interface, error handling for missing/malformed files","successCriteria":"Script runs with 'python csv_analyser.py data.csv', handles edge cases, output is readable"}]}

RULES:
- Only include agents that are actually needed — don't force all three
- Tasks must be specific enough that the agent can execute without asking questions
- Each task should describe WHAT to produce, not just what to research
- If tasks are sequential (most are), use dependsOn to chain them
- Keep it practical — 1-3 tasks maximum, no over-decomposition`;

                // Try Astra decomposition with a 60s timeout. If it fails/times out,
                // fall back to heuristic immediately so the user always gets a plan.
                let plan = null;
                try {
                    const astraResult = await runAgentTask('main', decompositionPrompt, { timeoutMs: 60000 });
                    console.log(`[COMMAND] Astra returned ${(astraResult.stdout || '').length} chars, code=${astraResult.code}`);

                    const output = astraResult.stdout || '';
                    const jsonMatch = output.match(/\{[\s\S]*"tasks"[\s\S]*\}/);
                    if (jsonMatch) {
                        try {
                            plan = JSON.parse(jsonMatch[0]);
                            console.log(`[COMMAND] Parsed ${plan.tasks?.length || 0} tasks from Astra's response`);
                        } catch (e) {
                            console.log('[COMMAND] Could not parse Astra response as JSON:', e.message);
                        }
                    }
                } catch (e) {
                    console.log('[COMMAND] Astra decomposition threw:', e.message);
                }

                agentStates.main = {
                    status: 'active',
                    action: 'System Active',
                    task: null,
                    timestamp: new Date().toISOString()
                };

                if (!plan || !plan.tasks || !Array.isArray(plan.tasks)) {
                    console.log('[COMMAND] Astra decomposition failed or timed out, using heuristic');
                    plan = { tasks: [] };
                    const goalLower = goal.toLowerCase();
                    if (goalLower.includes('research') || goalLower.includes('find') || goalLower.includes('investigate') || goalLower.includes('search') || goalLower.includes('learn about')) {
                        plan.tasks.push({ agent: 'newton', task: `Research the following thoroughly and provide detailed findings: ${goal}` });
                    }
                    if (goalLower.includes('write') || goalLower.includes('blog') || goalLower.includes('article') || goalLower.includes('script') || goalLower.includes('content') || goalLower.includes('post')) {
                        const idx = plan.tasks.length;
                        plan.tasks.push({ agent: 'bronte', task: `Write a compelling piece about: ${goal}`, ...(idx > 0 ? { dependsOn: idx - 1 } : {}) });
                    }
                    if (goalLower.includes('build') || goalLower.includes('code') || goalLower.includes('implement') || goalLower.includes('create') || goalLower.includes('develop') || goalLower.includes('program')) {
                        const idx = plan.tasks.length;
                        plan.tasks.push({ agent: 'guido', task: `Build a working implementation for: ${goal}`, ...(idx > 0 ? { dependsOn: idx - 1 } : {}) });
                    }
                    if (plan.tasks.length === 0) {
                        plan.tasks.push({ agent: 'newton', task: goal });
                    }
                }

                // Auto-chain if no explicit dependencies
                if (plan.tasks.length > 1) {
                    let anyDeps = plan.tasks.some(t => t.dependsOn !== undefined);
                    if (!anyDeps) {
                        for (let i = 1; i < plan.tasks.length; i++) {
                            plan.tasks[i].dependsOn = i - 1;
                        }
                    }
                }

                // Determine strategy
                const hasDependencies = plan.tasks.some(t => t.dependsOn !== undefined);
                const strategy = hasDependencies ? 'sequential' : 'parallel';

                // Return decomposition plan for user approval
                const planId = `plan-${crypto.randomUUID()}`;
                console.log(`[COMMAND] Goal: "${goal.substring(0, 60)}" → ${plan.tasks.length} tasks (${strategy}), awaiting approval`);

                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: true,
                    plan: {
                        id: planId,
                        goal,
                        tasks: plan.tasks,
                        strategy
                    }
                }));

            } catch (e) {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false, error: e.message }));
            }
        });
        return;
    }

    // ─── Command approve endpoint — dispatches a user-approved plan ───────
    if (req.url === '/agents/command/approve' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', async () => {
            try {
                const { plan } = JSON.parse(body);
                if (!plan || !plan.tasks || !Array.isArray(plan.tasks) || plan.tasks.length === 0) {
                    res.writeHead(400);
                    res.end(JSON.stringify({ error: 'Invalid plan' }));
                    return;
                }

                const goal = plan.goal || 'Command';
                const hasDependencies = plan.tasks.some(t => t.dependsOn !== undefined);

                // Clear Astra's terminal and show the approved plan
                const agentNames = { newton: 'Newton', guido: 'Guido', bronte: 'Bronte', main: 'Astra' };
                let planSummary = `── Approved Plan: ${goal} ──\n`;
                plan.tasks.forEach((t, i) => {
                    planSummary += `\n${i + 1}. ${agentNames[t.agent] || t.agent}:\n   ${t.task}\n`;
                });
                planSummary += `\n── Dispatching ${plan.tasks.length} task${plan.tasks.length > 1 ? 's' : ''} (${hasDependencies ? 'sequential' : 'parallel'}) ──\n`;
                agentTerminalOutput.main = planSummary;

                agentStates.main = {
                    status: 'active',
                    action: `Dispatching: ${goal.substring(0, 50)}`,
                    task: goal,
                    timestamp: new Date().toISOString()
                };

                // Respond immediately
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, message: 'Plan approved, dispatching...' }));

                if (hasDependencies) {
                    // Sort by dependency order
                    const ordered = [];
                    const remaining = [...plan.tasks];
                    const resolved = new Set();

                    while (remaining.length > 0) {
                        const next = remaining.findIndex(t => t.dependsOn === undefined || t.dependsOn === null || resolved.has(t.dependsOn));
                        if (next === -1) break;
                        const task = remaining.splice(next, 1)[0];
                        resolved.add(ordered.length);
                        ordered.push(task);
                    }

                    const pipelineId = `cmd-pipeline-${++pipelineIdCounter}-${Date.now()}`;
                    const pipeline = {
                        id: pipelineId,
                        name: `Command: ${goal}`,
                        reviewGates: !!plan.reviewGates,
                        steps: ordered.map((s, i) => ({
                            agentId: s.agent,
                            taskTemplate: s.task,
                            task: s.task,
                            index: i,
                            status: 'pending',
                            output: null,
                            summary: null
                        })),
                        status: 'running',
                        startedAt: new Date().toISOString(),
                        currentStep: 0
                    };
                    activePipelines.unshift(pipeline);

                    // Run pipeline in background with summarisation between steps
                    (async () => {
                        let previousOutput = '';
                        for (let i = 0; i < pipeline.steps.length; i++) {
                            const step = pipeline.steps[i];
                            pipeline.currentStep = i;
                            step.status = 'running';
                            step.startedAt = new Date().toISOString();
                            const agent = AGENTS.find(a => a.id === step.agentId);

                            let task = step.task;
                            if (previousOutput) {
                                task += `\n\nContext from previous step:\n${previousOutput}`;
                            }
                            step.task = task;

                            agentStates[step.agentId] = {
                                status: 'running',
                                action: `Command: ${task.substring(0, 50)}...`,
                                task: task,
                                timestamp: new Date().toISOString()
                            };

                            const result = await runAgentTask(step.agentId, task, { freshSession: true });
                            const output = result.stdout || '';
                            step.output = output.substring(0, 5000);
                            step.status = result.code === 0 ? 'completed' : 'error';
                            step.endedAt = new Date().toISOString();

                            agentStates[step.agentId] = {
                                status: 'idle',
                                action: `Completed: ${task.substring(0, 40)}`,
                                task: task,
                                output: output.substring(0, 2000),
                                timestamp: new Date().toISOString()
                            };

                            const cmdResultId = `cmd-${pipelineId}-${i}-${Date.now()}`;
                            completedResults.unshift({
                                id: cmdResultId,
                                agent: step.agentId,
                                agentName: agent?.name || step.agentId,
                                task: step.taskTemplate || task,
                                status: step.status,
                                durationMs: 0,
                                model: '',
                                timestamp: new Date().toISOString(),
                                pipeline: pipeline.name,
                                pipelineStep: i + 1
                            });

                            const cEmoji = step.status === 'completed' ? '✅' : '❌';
                            sendTelegramNotification(`${cEmoji} *${agent?.name}* ${step.status} (pipeline step ${i + 1}/${pipeline.steps.length})\n${(step.taskTemplate || task).substring(0, 200)}`);

                            // If step failed, pause for user retry/override/abort
                            if (step.status === 'error') {
                                console.log(`[PIPELINE] Step ${i + 1} failed (${agent?.name}) — waiting for user action`);
                                pipeline.status = 'step_error';

                                const errorAction = await new Promise(resolve => {
                                    pipeline._errorResolve = resolve;
                                });
                                delete pipeline._errorResolve;

                                if (errorAction.action === 'retry') {
                                    if (errorAction.editedTask) {
                                        step.task = errorAction.editedTask;
                                        step.taskTemplate = errorAction.editedTask;
                                    }
                                    step.status = 'running';
                                    pipeline.status = 'running';
                                    i--;
                                    continue;
                                } else if (errorAction.action === 'override') {
                                    previousOutput = errorAction.output || '';
                                    step.output = previousOutput.substring(0, 5000);
                                    step.status = 'completed';
                                    step.overridden = true;
                                    pipeline.status = 'running';
                                } else {
                                    pipeline.status = 'error';
                                    break;
                                }
                            }

                            // Summarise output for next step (non-final steps only)
                            if (i < pipeline.steps.length - 1) {
                                step.status = 'summarising';
                                const { handoff, raw, formatted } = await summariseOutput(step.agentId, output);
                                step.summary = formatted;
                                step.handoff = handoff;
                                step.status = 'completed';
                                previousOutput = formatted;

                                // Update the result entry with summary data
                                const existingResult = completedResults.find(r => r.id === cmdResultId);
                                if (existingResult) {
                                    existingResult.summary = formatted.substring(0, 3000);
                                    existingResult.hasFullOutput = true;
                                }

                                // Review gate: pause for user approval before next step
                                if (pipeline.reviewGates) {
                                    console.log(`[PIPELINE] Review gate after step ${i + 1}`);
                                    step.status = 'awaiting_review';
                                    pipeline.status = 'awaiting_review';

                                    const review = await new Promise(resolve => {
                                        pipeline._reviewResolve = resolve;
                                    });
                                    delete pipeline._reviewResolve;

                                    if (review.action === 'approve') {
                                        if (review.editedHandoff) {
                                            step.handoff = review.editedHandoff;
                                            const agentName = AGENTS.find(a => a.id === step.agentId)?.name || step.agentId;
                                            previousOutput = formatHandoffForInjection(review.editedHandoff, agentName);
                                        } else if (review.editedSummary) {
                                            previousOutput = review.editedSummary;
                                        }
                                        step.summary = previousOutput;
                                    } else if (review.action === 'skip') {
                                        previousOutput = '';
                                    }
                                    step.status = 'completed';
                                    pipeline.status = 'running';
                                }
                            }
                        }
                        if (pipeline.status !== 'error') pipeline.status = 'completed';
                        pipeline.endedAt = new Date().toISOString();

                        // Generate pipeline report
                        if (pipeline.status === 'completed') {
                            pipeline.report = generatePipelineReport(pipeline);
                            console.log(`[REPORT] Generated report for ${pipeline.id}: ${pipeline.report.deliverables.length} deliverables`);
                    savePipelines();
                        }
                    })();

                } else {
                    // Independent tasks — dispatch in parallel
                    for (const t of plan.tasks) {
                        const agent = AGENTS.find(a => a.id === t.agent);
                        if (!agent) continue;

                        agentStates[t.agent] = {
                            status: 'running',
                            action: `Command: ${t.task.substring(0, 50)}...`,
                            task: t.task,
                            timestamp: new Date().toISOString()
                        };

                        (async () => {
                            const result = await runAgentTask(t.agent, t.task);
                            const output = result.stdout || result.stderr || '';
                            const endTime = Date.now();

                            agentStates[t.agent] = {
                                status: 'idle',
                                action: `Completed: ${t.task.substring(0, 40)}`,
                                task: t.task,
                                output: output.substring(0, 2000),
                                timestamp: new Date().toISOString()
                            };

                            completedResults.unshift({
                                id: `cmd-${t.agent}-${endTime}`,
                                agent: t.agent,
                                agentName: agent.name,
                                task: t.task,
                                status: result.code === 0 ? 'completed' : 'error',
                                durationMs: 0,
                                model: '',
                                timestamp: new Date().toISOString(),
                                command: goal
                            });
                            if (completedResults.length > 50) completedResults = completedResults.slice(0, 50);

                            const parEmoji = result.code === 0 ? '✅' : '❌';
                            sendTelegramNotification(`${parEmoji} *${agent.name}* ${result.code === 0 ? 'completed' : 'error'}\n${t.task.substring(0, 200)}`);
                        })();
                    }
                }

            } catch (e) {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false, error: e.message }));
            }
        });
        return;
    }

    // ─── Pipeline review gate endpoint ─────────────────────────────────
    if (req.url === '/pipelines/review' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const { pipelineId, stepIndex, action, editedSummary, editedHandoff } = JSON.parse(body);
                const pipeline = activePipelines.find(p => p.id === pipelineId);
                if (!pipeline) {
                    res.writeHead(404);
                    res.end(JSON.stringify({ error: 'Pipeline not found' }));
                    return;
                }
                if (pipeline.status !== 'awaiting_review' || !pipeline._reviewResolve) {
                    res.writeHead(400);
                    res.end(JSON.stringify({ error: 'Pipeline is not awaiting review' }));
                    return;
                }
                console.log(`[REVIEW] Pipeline ${pipelineId} step ${stepIndex}: ${action}`);
                pipeline._reviewResolve({ action, editedSummary, editedHandoff });
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true }));
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    // ─── Pipeline report endpoint ───────────────────────────────────────
    if (req.url.startsWith('/pipelines/') && req.url.endsWith('/report') && req.method === 'GET') {
        const pipelineId = req.url.replace('/pipelines/', '').replace('/report', '');
        const pipeline = activePipelines.find(p => p.id === pipelineId);
        if (!pipeline) {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Pipeline not found' }));
            return;
        }
        if (!pipeline.report && pipeline.status === 'completed') {
            // Generate report on-demand if it wasn't generated at completion
            pipeline.report = generatePipelineReport(pipeline);
        }
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(pipeline.report || { error: 'Pipeline not yet completed' }));
        return;
    }

    // ─── Pipeline error recovery endpoint ────────────────────────────────
    if (req.url === '/pipelines/retry' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const { pipelineId, stepIndex, action, output, editedTask } = JSON.parse(body);
                const pipeline = activePipelines.find(p => p.id === pipelineId);
                if (!pipeline) {
                    res.writeHead(404);
                    res.end(JSON.stringify({ error: 'Pipeline not found' }));
                    return;
                }
                if (pipeline.status !== 'step_error' || !pipeline._errorResolve) {
                    res.writeHead(400);
                    res.end(JSON.stringify({ error: 'Pipeline is not in error state' }));
                    return;
                }
                console.log(`[RETRY] Pipeline ${pipelineId} step ${stepIndex}: ${action}${editedTask ? ' (edited task)' : ''}`);
                pipeline._errorResolve({ action, output, editedTask });
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true }));
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }

    // ─── SSE endpoint for real-time updates ───────────────────────────
    if (req.url === '/agents/events' && req.method === 'GET') {
        res.writeHead(200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        });

        const sendEvent = (data) => {
            res.write(`data: ${JSON.stringify(data)}\n\n`);
        };

        // Send current state immediately
        sendEvent(getFullAgentStatus());

        // Send updates every 3 seconds
        const interval = setInterval(() => {
            try {
                sendEvent(getFullAgentStatus());
            } catch (e) {
                clearInterval(interval);
            }
        }, 3000);

        req.on('close', () => {
            clearInterval(interval);
        });
        return;
    }

    // Serve static files
    const staticExts = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.js'];
    const staticFile = path.join(__dirname, req.url);
    if (staticExts.includes(path.extname(req.url).toLowerCase()) && fs.existsSync(staticFile)) {
        const ext = path.extname(req.url).toLowerCase();
        const contentType = {
            '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.gif': 'image/gif', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
            '.css': 'text/css', '.js': 'application/javascript'
        }[ext];
        res.writeHead(200, { 'Content-Type': contentType });
        fs.readFile(staticFile, (err, data) => { if (!err) res.end(data); });
        return;
    }

    res.writeHead(404);
    res.end('Not found');
});

// Initialize and start
initializeSnapshots();
loadAvailableModels();

// Set token baselines so dashboard shows usage from this session, not all-time
resetAllAgentTokens();

server.listen(PORT, () => {
    console.log(`Mission Control server running at http://localhost:${PORT}`);
    console.log(`Data file: ${DATA_FILE}`);
    console.log(`Runs file: ${RUNS_FILE}`);
    console.log(`Agents base: ${AGENTS_BASE}`);
    console.log(`Watching for completions...`);
});
