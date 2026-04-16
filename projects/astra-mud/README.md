# Astra-MUD 🏰

> A persistent, LLM-powered Multi-User Dungeon where NPCs think, remember, and evolve.

## Vision

An immersive text-based MUD where:
- **NPCs are agents** — powered by Ollama, each NPC has memory, personality, and goals
- **The world persists** — player actions reshape the world permanently
- **Stories emerge** — procedural quests and narratives generated in real-time
- **Memories matter** — NPCs remember players across sessions, relationships evolve

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Player Connection                   │
│              (WebSocket / Telnet / CLI)               │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    Game Server                         │
│              (Python async, Starlette)                  │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐  │
│  │ World State │ │  NPC Brain   │ │  Event System    │  │
│  │  (SQLite)   │ │  (Ollama)   │ │  (pub/sub)       │  │
│  └─────────────┘ └──────────────┘ └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Core Systems

### 1. World State
- Rooms, items, NPCs, player states
- SQLite for persistence
- Transaction-based updates

### 2. NPC Brain (LLM-powered)
- Each NPC is an agent with memory
- Ollama backend (phi3, llama3, etc.)
- Prompt templates for character consistency
- Memory system: episodic + semantic

### 3. Event System
- Player actions trigger events
- NPCs react in real-time
- World reacts to major events

### 4. Communication
- WebSocket for real-time play
- REST API for admin/tools
- Telnet bridge (optional)

## Project Structure

```
astra-mud/
├── world/
│   ├── models.py       # Room, Item, NPC, Player
│   ├── database.py     # SQLite operations
│   └── events.py       # Event bus
├── npcs/
│   ├── brain.py        # LLM NPC controller
│   ├── memory.py       # NPC memory system
│   ├── personality.py  # Character templates
│   └── behaviors/      # NPC behavior trees
├── llm/
│   ├── backend.py      # Ollama/OpenAI abstraction
│   └── prompts/        # System prompts
├── web/
│   ├── server.py       # Starlette WebSocket server
│   ├── static/         # CSS, JS
│   └── templates/      # HTML
├── players/
│   ├── session.py      # Player session management
│   └── commands.py     # Command parser
└── main.py             # Entry point
```

## MVP Scope

### Phase 1: Foundation
- [x] Project structure
- [ ] World state (rooms, items, basic NPC)
- [ ] WebSocket server
- [ ] Simple command parser
- [ ] One test NPC with Ollama

### Phase 2: NPC Brains
- [ ] NPC memory system
- [ ] Personality templates
- [ ] Multi-NPC conversations
- [ ] Player-NPC relationship tracking

### Phase 3: Persistence & World
- [ ] Save/load world state
- [ ] Player accounts
- [ ] World-changing events
- [ ] Quest system

## Tech Stack

- **Python 3.11+** — async/await throughout
- **Starlette** — WebSocket + HTTP server
- **SQLite** — World persistence (simple, portable)
- **Ollama** — Local LLM inference (cost-effective)
- **Aiosqlite** — Async SQLite operations

## Why This Matters

A real-world LLM system with:
- **Real-time generation** — players get immediate responses
- **Long-term memory** — NPCs remember, relationships evolve
- **Complex state** — world persists and changes
- **Multi-agent coordination** — multiple NPCs reason and act
- **Cost efficiency** — Ollama means no API costs

This is the kind of project that impresses in an LLM engineering interview — not because it's a MUD, but because it demonstrates production thinking: async systems, memory management, real-time constraints, cost optimization.

---

*Building at pace. Iterating daily.*
