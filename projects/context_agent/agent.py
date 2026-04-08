"""
Context Management Agent
Handles long conversations with smart context handling.

Strategies:
- Sliding window
- Summarization
- Priority-based

Run with: python context_agent/agent.py
"""

import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Message:
    role: str
    content: str
    tokens: int = 0
    priority: int = 1  # 1-5, higher = more important


class ContextManager:
    """Manages context within token limits."""
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.messages: list[Message] = []
        self.system_prompt: Optional[Message] = None
    
    def add_message(self, role: str, content: str, priority: int = 1):
        """Add a message."""
        msg = Message(role=role, content=content, priority=priority)
        self.messages.append(msg)
        self._prune()
    
    def set_system(self, content: str):
        """Set system prompt."""
        self.system_prompt = Message(role="system", content=content, priority=5)
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimate."""
        return len(text) // 4
    
    def _prune(self):
        """Prune to fit token budget."""
        # Calculate current tokens
        total = self._estimate_tokens(self.system_prompt.content) if self.system_prompt else 0
        total += sum(self._estimate_tokens(m.content) for m in self.messages)
        
        if total <= self.max_tokens:
            return
        
        # Remove low-priority messages from middle
        to_remove = []
        for i, msg in enumerate(self.messages[1:-1], 1):  # Skip first and last
            if msg.priority < 3:
                to_remove.append(i)
        
        for i in reversed(to_remove):
            removed = self.messages.pop(i)
            total -= self._estimate_tokens(removed.content)
            if total <= self.max_tokens:
                break
    
    def get_context(self) -> list[dict]:
        """Get messages for LLM."""
        context = []
        if self.system_prompt:
            context.append({"role": "system", "content": self.system_prompt.content})
        context.extend({"role": m.role, "content": m.content} for m in self.messages)
        return context
    
    def summarize_old(self, summary: str):
        """Replace old messages with summary."""
        if len(self.messages) > 2:
            self.messages = [
                Message("system", f"Summary: {summary}", priority=5),
                self.messages[-1]
            ]


if __name__ == "__main__":
    cm = ContextManager(max_tokens=200)
    
    print("="*50)
    print("📝 Context Management Agent")
    print("="*50)
    
    cm.set_system("You are a helpful assistant.")
    cm.add_message("user", "Hello!", priority=1)
    cm.add_message("assistant", "Hi there!", priority=1)
    cm.add_message("user", "Tell me about AI.", priority=3)
    cm.add_message("assistant", "AI is...", priority=3)
    cm.add_message("user", "Thanks!", priority=1)
    
    print(f"\nMessages: {len(cm.messages)}")
    print(f"Context: {cm.get_context()}")
    
    print("\n✅ Context managed within limits")
