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

### 1. World State ✓
- Rooms, items, NPCs, player states
- SQLite for persistence
- Transaction-based updates

### 2. NPC Brain ✓ (LLM-powered)
- Each NPC is an agent with memory
- Ollama backend (phi3, llama3, etc.)
- Prompt templates for character consistency
- Memory system: episodic + semantic
- Relationship tracking (HOSTILE → ALLIED scale)

### 3. Event System ✓
- Player actions trigger events
- NPCs react in real-time
- World reacts to major events
- Random encounters (rats, skeletons, spirits, treasure)
- Timed world events (earthquakes, dragon stirs)

### 4. Quest System ✓
- QuestManager with objectives and rewards
- Quest chains with prerequisites
- 3 starter quests implemented

### 5. Communication ✓
- WebSocket for real-time play
- Web client at http://localhost:8765

## Project Structure

```
astra-mud/
├── world/
│   ├── models.py       # Room, Item, NPC, Player
│   ├── database.py     # SQLite operations
│   ├── quests.py       # Quest system
│   └── events.py       # World events & encounters
├── npcs/
│   ├── brain.py        # LLM NPC controller
│   ├── memory.py       # NPC memory + relationships
│   ├── personality.py  # Character templates
│   └── behaviors.py    # Personality-driven behaviors
├── llm/
│   └── backend.py      # Ollama/OpenAI abstraction
├── web/
│   ├── server.py       # Starlette WebSocket server
│   └── templates/      # HTML game client
├── players/            # (future)
└── main.py             # Entry point
```

## Current Features

### Rooms (5)
- Dungeon Entrance → Torch-Lit Corridor → Grand Chamber
- Armory (east of corridor)
- Dragon's Hoard (treasury, north of chamber)

### NPCs (2)
- **Skeleton Guard** - Hostile, protective (hallway)
- **Ancient Dragon** - Sleeping, powerful (treasury)

### Commands
- `n/s/e/w` - Movement
- `look` - Examine room
- `say [msg]` - Speak
- `talk to [npc]` - Talk to NPC
- `attack [npc]` - Attack NPC
- `inventory` - Check belongings
- `quests` / `quest [id]` - Quest management
- `status` - Quest progress

### Random Encounters (4)
- Rat Swarm (30% chance)
- Skeleton Rogue (15% chance)
- Wandering Spirit (20%, non-hostile)
- Treasure Chest (5%, loot drops)

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