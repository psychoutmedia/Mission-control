"""
Agent Memory System
Short-term (conversation) + Long-term (persistent) memory for AI agents.

Run with: python projects/agent_memory/memory.py
"""

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any
from pathlib import Path


# ============================================================
# SHORT-TERM MEMORY (Conversation Context)
# ============================================================

@dataclass
class Message:
    """A single message in conversation history."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


class ShortTermMemory:
    """
    Manages conversation context (what was just said).
    
    In production, this would integrate with LLM context windows.
    Key concept: Not all messages need to go to the LLM -
    summarize old ones to save tokens.
    """
    
    def __init__(self, max_messages: int = 50):
        self.messages: list[Message] = []
        self.max_messages = max_messages
    
    def add_message(self, role: str, content: str, metadata: dict = None):
        """Add a message to conversation history."""
        self.messages.append(Message(
            role=role,
            content=content,
            metadata=metadata or {}
        ))
        
        # Prune if too long
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_recent(self, n: int = 10) -> list[Message]:
        """Get the n most recent messages."""
        return self.messages[-n:]
    
    def get_context_for_llm(self, max_tokens: int = 4000) -> list[dict]:
        """
        Get messages formatted for LLM API.
        In production: estimate token count and truncate.
        """
        # Simple version: just return all messages
        return [
            {"role": m.role, "content": m.content}
            for m in self.messages
        ]
    
    def clear(self):
        """Clear conversation history."""
        self.messages = []
    
    def summarize(self, summary: str):
        """Replace messages with a summary."""
        self.messages = [
            Message(
                role="system",
                content=f"Summary of previous conversation: {summary}"
            )
        ]


# ============================================================
# LONG-TERM MEMORY (Persistent Storage)
# ============================================================

@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    content: str
    category: str  # "fact", "preference", "goal", "learned"
    importance: int = 1  # 1-5
    timestamp: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    tags: list[str] = field(default_factory=list)


class LongTermMemory:
    """
    Persistent memory that survives across sessions.
    
    Key concepts:
    - Importance scoring (what matters)
    - Access tracking (what gets used)
    - Retrieval by relevance (not just recency)
    - Categories (facts, preferences, goals)
    """
    
    def __init__(self, storage_path: str = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(__file__).parent / "memory_store.json"
        
        self.memories: dict[str, MemoryEntry] = {}
        self._load()
    
    def _load(self):
        """Load memories from disk."""
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                data = json.load(f)
                for k, v in data.items():
                    self.memories[k] = MemoryEntry(**v)
    
    def _save(self):
        """Save memories to disk."""
        data = {k: asdict(v) for k, v in self.memories.items()}
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add(self, content: str, category: str = "fact", 
            importance: int = 3, tags: list[str] = None) -> str:
        """Add a new memory."""
        import uuid
        entry_id = f"mem_{uuid.uuid4().hex[:8]}"
        
        self.memories[entry_id] = MemoryEntry(
            id=entry_id,
            content=content,
            category=category,
            importance=importance,
            tags=tags or []
        )
        
        self._save()
        return entry_id
    
    def retrieve(self, query: str, top_k: int = 5) -> list[MemoryEntry]:
        """
        Retrieve relevant memories.
        
        Simple version: keyword matching + importance weighting.
        Production: would use embeddings + vector similarity.
        """
        query_lower = query.lower()
        scores = []
        
        for mem in self.memories.values():
            # Importance score
            score = mem.importance * 10
            
            # Keyword match
            if any(word in mem.content.lower() for word in query_lower.split()):
                score += 20
            
            # Recency bonus (recent memories more relevant)
            recency = (time.time() - mem.last_accessed) / (24 * 3600)  # days
            score -= recency * 2
            
            # Access count bonus
            score += mem.access_count * 0.5
            
            if score > 0:
                scores.append((score, mem))
        
        # Sort by score and return top_k
        scores.sort(key=lambda x: -x[0])
        return [mem for _, mem in scores[:top_k]]
    
    def access(self, memory_id: str) -> MemoryEntry | None:
        """Access a memory (updates access stats)."""
        if memory_id in self.memories:
            mem = self.memories[memory_id]
            mem.last_accessed = time.time()
            mem.access_count += 1
            self._save()
            return mem
        return None
    
    def update(self, memory_id: str, content: str = None, 
               importance: int = None) -> bool:
        """Update a memory."""
        if memory_id not in self.memories:
            return False
        
        if content:
            self.memories[memory_id].content = content
        if importance:
            self.memories[memory_id].importance = importance
        
        self._save()
        return True
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        if memory_id in self.memories:
            del self.memories[memory_id]
            self._save()
            return True
        return False
    
    def get_all(self, category: str = None) -> list[MemoryEntry]:
        """Get all memories, optionally filtered by category."""
        memories = list(self.memories.values())
        if category:
            memories = [m for m in memories if m.category == category]
        return sorted(memories, key=lambda m: -m.importance)


# ============================================================
# UNIFIED AGENT MEMORY
# ============================================================

class AgentMemory:
    """
    Unified memory system combining short-term and long-term.
    
    This is what agents would use in production:
    - Short-term: current conversation
    - Long-term: persistent knowledge
    """
    
    def __init__(self, storage_path: str = None):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(storage_path)
    
    def remember(self, content: str, category: str = "fact",
                 importance: int = 3, tags: list[str] = None):
        """Store something to long-term memory."""
        return self.long_term.add(content, category, importance, tags)
    
    def recall(self, query: str, top_k: int = 5) -> list[MemoryEntry]:
        """Retrieve from long-term memory."""
        return self.long_term.retrieve(query, top_k)
    
    def chat(self, role: str, content: str):
        """Add to short-term (conversation) memory."""
        self.short_term.add_message(role, content)
    
    def get_context(self) -> list[dict]:
        """Get conversation context for LLM."""
        return self.short_term.get_context_for_llm()
    
    def extract_and_store(self, llm_summary: str):
        """
        After conversation, extract important info to long-term.
        
        In production: LLM would analyze conversation and
        decide what to persist.
        """
        # For now, just store the summary
        if llm_summary:
            self.long_term.add(
                llm_summary,
                category="conversation_summary",
                importance=2
            )


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    # Initialize unified memory
    memory = AgentMemory()
    
    print("=" * 50)
    print("🧠 Agent Memory System Demo")
    print("=" * 50)
    
    # Short-term memory demo
    print("\n📝 Short-Term Memory (Conversation):")
    memory.chat("user", "My name is Mark and I prefer Python over JavaScript.")
    memory.chat("assistant", "Got it! I'll remember you prefer Python.")
    memory.chat("user", "I'm learning about LLM agents.")
    memory.chat("assistant", "Great topic! Agents are fascinating.")
    
    context = memory.get_context()
    for msg in context:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    # Long-term memory demo
    print("\n💾 Long-Term Memory (Persistent):")
    
    # Store some facts
    memory.remember(
        "Mark prefers Python over JavaScript",
        category="preference",
        importance=4,
        tags=["language", "preference"]
    )
    memory.remember(
        "Automa Dynamics is building humanoid robots (Helios-1)",
        category="fact",
        importance=5,
        tags=["company", "robotics"]
    )
    memory.remember(
        "The goal is to become an LLM Engineer in Silicon Valley",
        category="goal",
        importance=5,
        tags=["career", "goal"]
    )
    
    # Retrieve
    print("\n🔍 Retrieving memories about 'Mark':")
    results = memory.recall("Mark", top_k=3)
    for mem in results:
        print(f"  - [{mem.category}] {mem.content} (importance: {mem.importance})")
    
    print("\n🔍 Retrieving memories about 'LLM':")
    results = memory.recall("LLM", top_k=3)
    for mem in results:
        print(f"  - [{mem.category}] {mem.content}")
    
    # List all
    print("\n📋 All memories:")
    all_memories = memory.long_term.get_all()
    for mem in all_memories:
        print(f"  [{mem.category}] {mem.content[:60]}...")
