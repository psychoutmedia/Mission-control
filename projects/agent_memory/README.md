# Agent Memory System

A unified memory system for AI agents combining short-term (conversation) and long-term (persistent) memory.

## Components

### Short-Term Memory
- Conversation history within a session
- Automatic pruning when too long
- Context formatting for LLM APIs

### Long-Term Memory
- Persistent storage across sessions
- Importance scoring (1-5)
- Access tracking (recency + frequency)
- Keyword-based retrieval
- Categories: fact, preference, goal, learned

### Unified AgentMemory
- Combines both for production use
- Extract-and-store pattern for learning

## Running

```bash
python memory.py
```

## Usage

```python
from memory import AgentMemory

memory = AgentMemory()

# Conversation
memory.chat("user", "My name is Mark")
memory.chat("assistant", "Nice to meet you, Mark!")

# Persist important info
memory.remember(
    "Mark prefers Python",
    category="preference",
    importance=4
)

# Retrieve
results = memory.recall("Mark")
```

## Extension Ideas

- Use embeddings for semantic search
- Add time-based decay
- Implement memory consolidation (like human sleep)
- Add encryption for sensitive data
