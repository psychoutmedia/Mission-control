# Task Queue

> Autonomous work system. Pull from Ready when idle.

## In Progress

- [ ] @astra: **Astra-MUD** — LLM-powered MUD ← **ALL PHASES COMPLETED** 🎮
  - Phase 1: Foundation (server working, world created, 2 NPCs with Ollama brains) ✓
  - Phase 2: NPC memory, personality, relationships ✓
  - Phase 3: Persistence, quests, world events ✓

**Status (2026-04-17):** Server running on port 8765. MVP complete!

**Status (2026-04-17):** Server verified running on port 8765. All core systems functional:
- WebSocket server working
- SQLite persistence working
- Ollama integration confirmed (phi3 available)
- 5 rooms: entrance, hallway, chamber, armory, treasury
- 2 NPCs: Skeleton Guard, Ancient Dragon
- Web client served at http://localhost:8765

**Phase 2 Completed:**
- Added `npcs/memory.py` - NPCMemory + RelationshipTracker systems
- Added `npcs/behaviors.py` - Personality-driven behavior patterns
- Enhanced `npcs/brain.py` - Memory context in LLM prompts, relationship tracking
- Enhanced `npcs/personality.py` - Memory and relationship context in system prompts
- Enhanced `web/server.py` - Memory/relationship recording on interactions, attack command
- Added brain state persistence functions to `world/database.py`
- Fixed room description typo (r.room.description → room.description)

---

## Done 2026-04-19

- [x] @astra: LeetCode practice — Graphs (695 Max Area of Island, 1466 Reorder Routes, 1971 Find if Path Exists) → memory/2026-04-19-leetcode-noon.md

---

## Done 2026-04-17

- [x] @astra: Phase 2 NPC Memory System - Complete memory + relationship system for NPCs
- [x] @astra: LeetCode practice — Graphs (Course Schedule 207, Course Schedule II 210 - Topological Sort) → memory/2026-04-17-leetcode-am.md
- [x] @astra: LeetCode practice — Trees & DP (Level Order 102, Validate BST 98, House Robber 198) → memory/2026-04-17-leetcode-10am.md
- [x] @astra: Phase 3 Quest System - Complete quest framework (QuestManager, objectives, rewards) → projects/astra-mud/world/quests.py
- [x] @astra: Phase 3 World Events - Random encounters, timed events, world changes → projects/astra-mud/world/events.py
- [x] @astra: LeetCode practice — Trees & BST (Validate BST 98, House Robber 198, Coin Change 322) → memory/2026-04-17-leetcode-noon.md
- [x] @astra: LeetCode practice — Strings & DP (Longest Palindromic Substring, Edit Distance) → memory/2026-04-17-leetcode-pm.md

---

## Done 2026-04-16

- [x] @astra: LeetCode practice — Graphs & DFS/BFS (Connected Components, Course Schedule II, Pacific Atlantic) → memory/2026-04-16-leetcode-am.md
- [x] @astra: Draft Helios-1 Technical Specification for Automa Dynamics → projects/automa-dynamics/docs/helios-1-technical-spec.md
- [x] @astra: LeetCode practice — Dynamic Programming (LIS, Coin Change, LCS) → memory/2026-04-16-leetcode-noon.md
- [x] @astra: LeetCode practice — Binary Search (Find Min, Search Rotated II, Median of Sorted Arrays) → memory/2026-04-16-leetcode-pm.md
- [x] @astra: Git push blocked by Electron binary in history (24 commits ahead of origin) → needs BFG or manual cleanup
- [x] @astra: Portfolio README polish — cot_streaming_agent (9KB README with architecture, backends, key concepts) → projects/cot_streaming_agent/README.md
- [x] @astra: LeetCode practice — Stack/Monotonic Stack (Daily Temperatures, Car Fleet, Min Swaps Balanced) → memory/2026-04-16-leetcode-5pm.md
- [x] @astra: LeetCode practice — Greedy/Intervals (Non-overlapping, Meeting Rooms II, Gas Station) → memory/2026-04-16-leetcode-6pm.md
- [x] @astra: LeetCode practice — Matrix (Set Zeroes, Spiral Matrix, Rotate Image) → memory/2026-04-16-leetcode-7pm.md
- [x] @astra: LeetCode practice — Trie (Implement Trie, Longest Common Prefix) → memory/2026-04-16-leetcode-8pm.md

## Done 2026-04-15

- [x] @astra: LeetCode practice — Backtracking & Stack (Subsets, Non-overlapping Intervals, Daily Temperatures) → memory/2026-04-15-leetcode-pm.md

## Done 2026-04-14

- [x] @astra: Fix git push issue in multi-agent-dashboard (node_modules 651MB Electron binaries) → projects/multi-agent-dashboard/.gitignore
- [x] @astra: Research RLHF and Constitutional AI (alignment techniques) → memory/rlhf-constitutional-ai.md
- [x] @astra: LeetCode practice — Strings & Dynamic Programming (Longest Palindromic Substring, Edit Distance, Word Break) → memory/2026-04-14-leetcode-evening.md
- [x] @astra: Research MLOps for LLMs (MLflow, Weights & Biases, DVC, experiment tracking) → memory/mlops-llms.md
- [x] @astra: LeetCode practice — Two Pointers & Sliding Window (3 mediums: Valid Palindrome II, Longest Substring, Minimum Window Substring) → memory/2026-04-14-leetcode-pm.md
- [x] @astra: LeetCode practice — Trees & Graphs (Binary Tree Level Order, Clone Graph, Longest Consecutive Sequence) → memory/2026-04-14-leetcode-night.md
- [x] @astra: LeetCode practice — Arrays & Hashing (3 mediums: Contains Duplicate, Valid Anagram, Two Sum) → memory/2026-04-14.md
- [x] @astra: Research vLLM vs TGI vs Ollama (throughput, performance, use cases) → memory/vllm-tgi-ollama.md
- [x] @astra: LeetCode practice — Binary Search & Divide & Conquer (Search Rotated Array, Median of Two Sorted Arrays, Koko Eating Bananas) → memory/2026-04-14-leetcode-8pm.md

## Done 2026-04-13

- [x] @astra: LeetCode practice — Trees & DP (4 mediums: Level Order, Validate BST, Coin Change, House Robber) → memory/2026-04-13-leetcode.md
- [x] @astra: Build custom PyTorch DataLoader for transformer training (MLM collator, dynamic padding, attention masking) → projects/transformer_dataloader.py

## Done 2026-04-12

- [x] @astra: LeetCode practice - 3 medium (Number of Islands, Clone Graph, Sudoku Solver) → memory/2026-04-12-leetcode.md
- [x] @astra: Build attention visualization tool (hook-based, heatmaps, per-head plots) → projects/attention_viz/
- [x] @astra: Research LLM inference optimization (KV cache, batching, speculative decoding) → memory/llm-inference-optimization.md
- [x] @astra: LeetCode practice - 3 medium (Search in Rotated Array, Min Subarray Len, Longest Substring) → memory/2026-04-12-leetcode-pm.md
- [x] @astra: Build chain-of-thought streaming agent (Ollama/OpenAI backends, step parsing) → projects/cot_streaming_agent/

## Done 2026-04-09

- [x] @astra: Build a timecode analysis agent for @timecode1260 → projects/timecode_agent/
- [x] @astra: Research GITEX AI Asia speakers/agenda (April 9-10 Singapore) → memory/gitex-2026-research.md
- [x] @astra: Extend hf_transformers_demo.py with local model fine-tuning example → projects/hf_transformers_demo.py
- [x] @astra: LeetCode practice - 3 medium (Valid Parentheses, Number of Islands, Clone Graph) → memory/2026-04-08.md
- [x] @astra: Build Telegram task notification utility → projects/agent_notify/
- [x] @astra: Build prompt template agent → projects/prompt_template_agent/
- [x] @astra: Research LLM embeddings → memory/embeddings-deep-dive.md
- [x] @astra: Build config agent → projects/config_agent/
- [x] @astra: Build a fallback agent → projects/fallback_agent/
- [x] @astra: Research LLM guardrails → memory/guardrails.md
- [x] @astra: Build a test agent → projects/test_agent/
- [x] @astra: Build a logging agent → projects/logging_agent/
- [x] @astra: Research LLM continuous learning → memory/continuous-learning.md
- [x] @astra: Build a validation agent → projects/validation_agent/
- [x] @astra: Build a rate limiting agent → projects/rate_limit_agent/
- [x] @astra: Research LLM function calling patterns → memory/function-calling.md
- [x] @astra: Build a retry logic agent → projects/retry_agent/
- [x] @astra: Build a caching agent → projects/caching_agent/
- [x] @astra: Research LLM multi-modal capabilities → memory/multimodal-llms.md
- [x] @astra: Build an API wrapper agent → projects/api_wrapper_agent/
- [x] @astra: Build a batch processing agent → projects/batch_agent/
- [x] @astra: Research LLM agent production deployment → memory/production-deployment.md
- [x] @astra: Build a context management agent → projects/context_agent/
- [x] @astra: Build a feedback loop agent → projects/feedback_agent/
- [x] @astra: Research LLM quantization (Q4, Q8, GGUF) → memory/llm-quantization.md
- [x] @astra: Build a streaming response agent → projects/streaming_agent/
- [x] @astra: Build an evaluation agent → projects/evaluation_agent/
- [x] @astra: Research LLM observability and monitoring → memory/llm-observability.md
- [x] @astra: Build a portfolio summary of all agents built today → memory/today-portfolio.md
- [x] @astra: Build a tool-use agent with real APIs → projects/tool_use_agent/
- [x] @astra: Research LLM context window strategies → memory/context-strategies.md
- [x] @astra: Build a hierarchical agent → projects/hierarchical_agent/
- [x] @astra: Build a chain-of-thought agent → projects/cot_agent/
- [x] @astra: Research LLM agent security → memory/agent-security.md
- [x] @astra: Build a persona-based agent → projects/persona_agent/
- [x] @astra: Build a code execution agent → projects/code_execution_agent/
- [x] @astra: Research fine-tuning vs RAG vs prompt engineering → memory/fine-tuning-vs-rag.md
- [x] @astra: Build a simple ReAct agent using Ollama → projects/ollama_react_agent/
- [x] @astra: Build a reflection agent → projects/reflection_agent/
- [x] @astra: Research prompt engineering best practices 2026 → memory/prompt-engineering-2026.md
- [x] @astra: Build a self-correcting agent → projects/self_correcting_agent/
- [x] @astra: Study LLM evaluation benchmarks → memory/llm-benchmarks.md
- [x] @astra: Build a simple tool-calling agent → projects/tool_calling_agent/
- [x] @astra: Study Groq inference engine architecture → memory/groq-lpu-architecture.md
- [x] @astra: Build memory system for agents → projects/agent_memory/
- [x] @astra: Build custom Ollama model wrapper → projects/ollama_extensions/
- [x] @astra: Build a planning agent → projects/planning_agent/
- [x] @astra: Research HuggingFace inference options → memory/hf-inference-options.md
- [x] @astra: Build multi-agent collaboration demo → projects/multi_agent_collab/
- [x] @astra: Build final portfolio README → memory/day-final-summary.md
- [x] @astra: Research LLM career paths → memory/llm-career-paths.md
- [x] @astra: Vector DB comparison (Chroma/Qdrant/Weaviate) → memory/vector-db-comparison.md

## Done Earlier (Highlights)

- [x] 44+ specialized LLM agents built (massive agent sprint)
- [x] LeetCode practice ongoing (various sessions)
- [x] SIAM product launch (2026-02-02)
- [x] Google Research collaboration on "Silicon Ceiling" (2026-02-02)
- [x] Automa Dynamics vision crystallized (2026-01-28)
- [x] Daily briefing automation set up (9am Telegram)
- [x] Security scan LaunchAgent (7am daily)
- [x] Mission Control v2 (file-based kanban)
- [x] Six-Pillar LLM Engineering Roadmap active
- [x] Ollama + RAG integration working
- [x] @automadynamics X account launched
- [x] Helios-1 specs refined

---

## Rules

- Any agent can pick up "Ready" tasks
- Mark yourself when starting: `@agentname: task`
- Move to Done when complete with summary
- Add new tasks as you discover them

## Backlog

- [x] FIX: Git push blocked by Electron binary — FIXED with git-filter-repo (2026-04-16)
  - Removed all blobs >10MB from history
  - Pushed 25 commits + Helios-1 spec (874fb7c → 8d25c41)
