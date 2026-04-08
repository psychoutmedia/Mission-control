"""
Caching Agent
Cache LLM responses for speed/cost optimization.

Run with: python caching_agent/agent.py
"""

import json
import hashlib
import time
from dataclasses import dataclass


@dataclass
class CacheEntry:
    key: str
    response: str
    created_at: float
    hits: int = 0


class CacheAgent:
    """LRU cache for LLM responses."""
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        self.cache: dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.ttl = ttl  # seconds
    
    def _make_key(self, prompt: str) -> str:
        """Create cache key from prompt."""
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    def get(self, prompt: str) -> str | None:
        """Get cached response."""
        key = self._make_key(prompt)
        entry = self.cache.get(key)
        
        if not entry:
            return None
        
        # Check TTL
        if time.time() - entry.created_at > self.ttl:
            del self.cache[key]
            return None
        
        entry.hits += 1
        return entry.response
    
    def set(self, prompt: str, response: str):
        """Cache a response."""
        key = self._make_key(prompt)
        
        # Evict if full
        if len(self.cache) >= self.max_size:
            oldest = min(self.cache.items(), key=lambda x: x[1].created_at)
            del self.cache[oldest[0]]
        
        self.cache[key] = CacheEntry(key, response, time.time())
    
    def stats(self) -> dict:
        """Get cache stats."""
        total_hits = sum(e.hits for e in self.cache.values())
        return {
            "size": len(self.cache),
            "total_hits": total_hits,
            "hit_rate": total_hits / (total_hits + 1)
        }


if __name__ == "__main__":
    cache = CacheAgent()
    
    print("="*50)
    print("💾 Caching Agent Demo")
    print("="*50)
    
    # Cache some responses
    cache.set("What is AI?", "AI is artificial intelligence.")
    cache.set("What is Python?", "Python is a programming language.")
    
    # Hit cache
    result = cache.get("What is AI?")
    print(f"\nCache hit: {result}")
    
    # Miss
    result = cache.get("What is ML?")
    print(f"Cache miss: {result}")
    
    print(f"\n📊 Stats: {cache.stats()}")
