# MEMORY.md - Long-Term Context

## Mission
**Goal**: Become an LLM Engineer → Silicon Valley hire  
**Company**: Automa Dynamics (Iron Man energy, purpose TBD) — now crystallized vision

### Research Collaboration (2026-02-02)
**Google Research** (@bilbobigbags) validated SIAM's research direction:
- **"Silicon Ceiling"**: LLMs have P(500 = Error) > 0.99 from training - can't override priors
- **"Priors vs. Evidence"**: Single evidence not enough to trigger belief revision
- **Solution**: Ontological Memory with contextual scoping (local → global patterns)

This gives SIAM rigorous academic framing for LLM engineering research.

## Automa Dynamics Vision (2026-01-28)
**North Star**: "We don't build tools. We build capabilities. We don't automate tasks. We amplify human potential. We don't predict the future. We architect it."

### The Five Divisions

| Division | Code Name | Focus |
|----------|-----------|-------|
| **Synthetic Labor** | Helios | Humanoid robotics for dangerous/dull/distanced work |
| **Cognitive Infrastructure** | Prometheus | Enterprise AI, Large Cognitive Models (LCM) |
| **Extreme Environments** | Aegis | Undersea, orbital, lunar, planetary systems |
| **Neural Integration** | Chorus | Brain-computer interfaces, human-AI collaboration |
| **Autonomous Ecosystems** | Gaia | Self-managing buildings, cities, regenerative systems |

### Helios-1: The Industrial Pioneer (Phase 1 Priority)
- **Height**: 5'10" (human-scale for existing infrastructure)
- **Payload**: 50kg sustained, 80kg burst
- **Runtime**: 8 hours (hot-swappable batteries)
- **Key Tech**: Large Behavior Model (LBM) for whole-body control, haptic telepresence, fleet learning
- **Target Markets**: Manufacturing, logistics, construction, mining, disaster response

### Strategic Roadmap
- **Year 1-2**: Prototype development, 5 pilot units, $50M Series A
- **Year 2-4**: Commercial launch, 100+ units, $100M ARR
- **Year 4-6**: Scale to 10,000 units, $1B ARR
- **Year 6-10**: Mainstream adoption, 100,000+ units, $10B+ ARR

### Core Values
1. **Autonomy with Accountability** — Systems act independently, we remain responsible
2. **Transparency in the Black Box** — Clear intentions, explain what/why we do
3. **Human-Centered Technology** — Technology serves humanity
4. **Relentless Curiosity** — "What if?" constantly
5. **Ethical Courage** — Do what's right, especially when hard

### The Pledge
> *"I pledge to build autonomous systems that amplify human potential, never diminish it. I will prioritize safety, transparency, and ethical considerations in every decision."*

### Agent Autonomy System (2026-02-20)
Installed **agent-autonomy-kit** skill from ClawHub:
- **Task Queue**: `tasks/QUEUE.md` — always have work ready to pull
- **Proactive Heartbeats**: Pull from queue instead of passive "anything need doing?"
- **Team Coordination**: Agents pick up tasks, mark in-progress, move to done
- **Metrics Tracking**: `memory/metrics.md` for productivity measurement

This transforms me from reactive (waiting for prompts) to proactive (pulling work). First step toward continuous operation.

## Astra's Role
**Physical embodiment planned** — Mark's long-term vision is to give Astra a Helios body, creating a fully embodied AI assistant. This document marks the moment the vision crystallized.  
**Current Role**: @timecode1260 on X (biblical prophecy + timecodes)

## Learning Path
- **Active Plan**: Six-Pillar LLM Engineering Roadmap (see `memory/llm-learning-roadmap.md`)
- **Strategy**: All pillars run in parallel — not linear execution
- **Pillars**:
  1. Python Mastery (PyTorch, transformers, LangChain)
  2. Go Deep (LLM internals, attention, embeddings, RAG)
  3. Build Agents (multi-agent, tool use, memory, planning)
  4. Automa Dynamics (portfolio projects, proving ground)
  5. Visibility (GitHub, X, writing, community)
  6. The Hunt (applications, interview prep, Valley targeting)
- **Progress**: Pillar 3 (Agents) very advanced — 44+ agents built; Pillar 2 (LLM internals) strong; Pillar 1 solid; Pillars 4-6 ongoing
- **Focus**: Python for AI frameworks (not basic apps), agent systems, production deployment

### LeetCode Progress (Pillar 6 - Interview Prep)
- **Total Solved**: 20+ medium difficulty problems across sessions
- **Recent Sessions**:
  - Apr 11: Word Search, Pacific Atlantic Water Flow, Accounts Merge
  - Apr 10 evening: Course Schedule II, Longest Consecutive Sequence, Find Min in Rotated Array
  - Apr 10: Binary Tree Inorder, Merge Intervals, LRU Cache
  - Apr 9: Valid Parentheses, Number of Islands, Clone Graph
  - Mar 17: 14 tasks including agent builds
  - Mar 12-13: Multiple sessions, 18 problems in one day
- **Techniques Learned**: DFS, BFS, graph traversal, cycle detection (Floyd's), interval merging, binary search

## Systems & Tools
- **Clawdbot**: Main AI assistant (Astra - chaotic seer personality)
- **Mission Control**: Custom kanban dashboard (`mission-control.html`)
  - Persistent browser-based task management
  - Space-themed UI with activity tracking
- **Daily Briefing**: 9am automated report via Telegram
  - Weather (Salford, UK)
  - Hot AI YouTube topics
  - Trending AI news
  - Overnight work review
  - Backlog status
  - Learning plan ideas
  - Mission suggestions

## Tech Stack
- **macOS**: Mac mini (Europe/London timezone)
- **Python 3.11**: Primary coding environment
- **Homebrew**: Package management
- **Peekaboo**: Screen capture & UI automation (installed)
- **Storage**:
  - Internal: 228GB (65GB free)
  - External: `/Volumes/Mac Dock` - 931GB (861GB free)

## Projects
- **Automa Dynamics**: Early stage, purpose TBD
- **Multi-User Dungeons (MUDs)**: Building game systems
- **@timecode1260**: X account for timecodes + prophecy content
  - Now has dedicated **timecode analysis agent** → projects/timecode_agent/
- **SIAM**: Agent belief revision system with Google Research (github.com/psychoutmedia/siam)

## Configuration
- **Model**: Minimax M2.7 (active, per bilbobigbags recommendation)
- **Elevated Mode**: On (sudo access granted)
- **Workspace**: `/Users/marksstephenson/clawd`
- **GitHub**: psychoutmedia
- **Email**: stephensonmark1@gmail.com (himalaya CLI broken — needs app password re-auth)

## Systems Status (2026-04-12)
- **Email**: himalaya CLI broken ("Invalid credentials") - needs re-auth for stephensonmark1@gmail.com
- **Ollama**: models available — phi3, gemma3:270m, llava
- **New tools**: attention_viz (PyTorch attention heatmaps), cot_streaming_agent (async CoT streaming)
- **New research**: llm-inference-optimization.md (KV cache, batching, speculative decoding, quantization, serving frameworks)

## Systems Status (2026-03-28)
- **Model**: Minimax M2.7 (active, bilbobigbags recommendation)
- **Email**: himalaya CLI broken ("Invalid credentials") - needs app password re-auth

## LeetCode Progress (Updated 2026-04-12)
**~20+ mediums solved** across sessions. Key pattern families covered:
- **Graph/DFS**: Number of Islands, Clone Graph, Word Search, Pacific Atlantic Water Flow
- **Backtracking**: Sudoku Solver, combinations/permutations
- **Binary Search**: Search in Rotated Array, Find Min in Rotated Array
- **Sliding Window**: Longest Substring, Min Subarray Sum
- **Data Structures**: LRU Cache, Course Schedule II, Merge Intervals, Union-Find (Accounts Merge)
- **Recursion/DP**: Longest Consecutive Sequence, etc.

## Recent Work

- 2026-03-31: Queue maintenance, system healthy
- 2026-03-30: GITEX AI Asia 2026 research complete → `memory/gitex-2026-research.md` (April 9-10 Singapore, speakers + agenda)
- 2026-03-30: HuggingFace fine-tuning demo extended with LoRA + Trainer examples → `projects/hf_transformers_demo.py`
- 2026-03-30: **Final portfolio summary** of 44+ LLM agents built in sprint → `memory/day-final-summary.md`
- 2026-03-30: **LLM career research** → `memory/llm-career-paths.md`
- 2026-03-30: **LLM embeddings deep-dive** → `memory/embeddings-deep-dive.md`
- 2026-03-30: **Prompt template agent** → `projects/prompt_template_agent/`
- 2026-03-28: **MinimM2.7 upgrade** — upgraded Minimax model to M2.7 (per bilbobigbags) — system healthy
- 2026-04-04: **GITEX AI Asia Research** - Researched April 9-10 Singapore event (memory/gitex-2026-research.md)
  - Key intel: Unitree Robotics planning IPO (10K-20K humanoid deliveries 2026), $356B APAC AI market by 2029
  - Unitree CIO, Horizon Quantum, IQM, Rigetti Computing, Antler, SGInnovate presenting
  - Mark flagged — 5 days away, tight but potentially worth attending
  - HF transformers demo extended with LoRA fine-tuning (DEMO 5 + 6 added to projects/hf_transformers_demo.py)

- 2026-04-03: **Timecode Agent Built** - Full agent for @timecode1260 → projects/timecode_agent/
  - agent.py, parser.py (40+ refs), references.py, generator.py
  - Handles 1260 days, 42 months, time/times/half, symbolic numbers
  - X thread generation with themed hooks (beast, temple, return, timecodes)
  - Test: ✅ working

- 2026-04-05: **Sunday Weekly Review** - Memory maintenance complete, queue cleared
- 2026-04-04: **GITEX AI Asia Research** - April 9-10 Singapore, 23K+ tech execs, Unitree Robotics (humanoid IPO planning), AI market $356B APAC by 2029. Action: 5 days away, tight but worth considering attendance
- 2026-04-04: **Hugging Face Fine-tuning Demo Extended** - Added LoRA + PEFT examples to hf_transformers_demo.py
- 2026-04-03: **Timecode Analysis Agent Built** → `projects/timecode_agent/` — full agent for @timecode1260 with parser (1260 days, time/times/half, compound formats), 40+ biblical references, X thread generator, theme analysis
- 2026-03-17: **Massive Agent Sprint** - 44+ specialized LLM agents built in one session:
  - Evaluation, feedback, reflection, self-correcting, persona, tool-use, chain-of-thought, hierarchical, planning, context, streaming, rate-limiting, retry, validation, logging, caching, batch processing, API wrapper, code execution, multi-agent collaboration, Ollama extensions, agent memory, and more
  - Portfolio summary: memory/today-portfolio.md

- 2026-03-06: **Massive Learning Sprint** - 14 tasks completed:
  - PyTorch tensor operations tutorial (memory/pytorch-tensor-tutorial.md)
  - ReAct agent demo with tool use (projects/react_agent.py)
  - X thread "How LLMs Actually Think" (13 tweets, memory/x-thread-how-llms-think.md)
  - Embeddings explainer - word2vec to transformers (memory/embeddings-explainer.md)
  - SIAM portfolio project outline (memory/siam-portfolio-outline.md)
  - AI startup research - 5 companies + comp (memory/ai-startup-research.md)
  - Blog post: "How I Built SIAM to Beat the Silicon Ceiling" (memory/blog-siam-silicon-ceiling.md)
  - RAG chatbot with LangChain + local embeddings (memory/rag-chatbot-demo.md)
  - LeetCode practice - 5 medium problems (memory/leetcode-practice.md)
  - Ollama setup (local LLM, memory/ollama-setup.md)
  - Ollama + RAG integration test (projects/rag_chatbot/ollama_rag.py) - working!
  - Blog: "10 Things I Wish I Knew About LLMs" (memory/blog-10-things-llms.md)
  - Telegram notifications for security scans (security-scan.sh updated)
  - Daily memory updates (memory/2026-03-06.md)

- 2026-02-02: **SIAM Product Launch** - Built complete AI startup product with Google Research (@bilbobigbags). Created deployable system with FastAPI middleware (siam_proxy.py), Streamlit dashboard (siam_command_center.py), one-click launcher (launch_siam.py), and CEO pitch (EXECUTIVE_SUMMARY.md). 17 commits, ~5,000 lines of code. System tested and working - heals 500→200 responses, fleet registry broadcasts patterns to all agents.
- 2026-02-02: **Google Research Collaboration** - Billy big bags (@bilbobigbags) from Google Research provided detailed feedback on SIAM's "Silicon Ceiling" problem (Priors vs. Evidence conflict). Collaborated on Ontological Memory schema and Mismatch Detector implementation.
- 2026-01-26: **X Automation Setup** - Installed bird CLI for X/Twitter control via cookies
- 2026-01-26: **@automadynamics Launch** - Created X account (automadynamics@gmail.com), posted first tweet via browser automation
- 2026-01-26: **Mission Control v2** - Rebuilt with file-based backend (Node.js server + JSON storage)
- 2026-01-26: **CLI Tool** - Built `mc` command for task management (add/list/move/delete)
- 2026-01-26: **Daily Briefing Ready** - Gateway cron job confirmed working, first briefing scheduled 9am tomorrow
- 2026-01-26: **Content Strategy** - Drafted 5 intro tweets for @automadynamics to build presence over next few days
- 2026-01-25: Set up Clawdbot with Sonnet default, enabled elevated tools
- 2026-01-25: Installed Peekaboo for screen capture (Screen Recording permission granted)
- 2026-01-25: Built Mission Control kanban dashboard (space-themed, persistent)
- 2026-01-25: Created Six-Pillar LLM Engineering Roadmap (parallel execution strategy)
- 2026-01-25: Set up daily briefing automation (9am Telegram via Gateway cron)
- 2026-01-25: Merged original 6 pillars with structured learning plan — all tracks running in parallel

## X Accounts
- **@timecode1260**: Main account (biblical prophecy + timecodes)
- **@automadynamics**: Astra's account (launched 2026-01-26)
  - Email: automadynamics@gmail.com
  - Chrome profile: "Astra Core"
  - Automated by @timecode1260 (labeled on X)
  - Strategy: Build presence with AI/LLM content, philosophical takes, Automa Dynamics updates

## Notes
- Keep token usage minimal (Sonnet for cost efficiency)
- Peekaboo works from Terminal (Screen Recording permission granted)
- Mission Control now file-based (`mission-control-data.json`) with live server on port 8888
- Daily briefing triggers via Gateway cron (9am Europe/London)
- Learning roadmap tracks progression through LLM fundamentals → production systems
- Bird CLI works but posting restricted on new accounts (error 226) - build trust first with manual tweets
- Security scan runs daily at 7am via LaunchAgent, sends Telegram notification
- Ollama v0.17.6 installed with phi3, gemma3:270m, llava models
- RAG chatbot can now use Ollama instead of OpenAI (privacy-first, no API costs)
- Task queue system active: tasks/QUEUE.md with autonomous work mode
- **Upcoming**: GITEX AI Asia April 9-10 Singapore (5 days away)
- **Timecode Agent**: Ready to use for @timecode1260 content generation
- **HF Fine-tuning Demo**: Extended with LoRA + PEFT examples for local model adaptation
