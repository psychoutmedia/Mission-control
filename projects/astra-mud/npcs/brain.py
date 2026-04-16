"""
Astra-MUD: NPC Brain
LLM-powered NPC controller with memory
"""

import aiohttp
import json
from typing import Optional
from datetime import datetime

from .personality import build_system_prompt


class NPCBrain:
    """LLM-powered brain for an NPC."""
    
    def __init__(
        self,
        npc_id: str,
        name: str,
        personality: dict,
        ai_model: str = "phi3",
        base_url: str = "http://localhost:11434",
    ):
        self.npc_id = npc_id
        self.name = name
        self.personality = personality
        self.ai_model = ai_model
        self.base_url = base_url
        self.conversation_history: list[dict] = []
        self.max_history = 20  # Keep last 20 exchanges
    
    async def think(self, player_input: str, world_context: str) -> str:
        """Generate NPC response to player input."""
        
        # Build system prompt with personality and recent memory
        system_prompt = build_system_prompt(
            self.name,
            self.personality,
            self.conversation_history[-5:] if self.conversation_history else [],
            world_context,
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": player_input},
        ]
        
        # Call Ollama
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.ai_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status != 200:
                        return f"{self.name} seems distracted and doesn't respond."
                    
                    data = await resp.json()
                    response = data["message"]["content"]
                    
                    # Add to conversation history
                    self.conversation_history.append({
                        "role": "user",
                        "content": player_input,
                    })
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": response,
                    })
                    
                    # Trim history
                    if len(self.conversation_history) > self.max_history * 2:
                        self.conversation_history = self.conversation_history[-self.max_history * 2:]
                    
                    return response
                    
        except aiohttp.ClientError:
            return f"{self.name} is unavailable (Ollama not running)."
    
    async def think_stream(self, player_input: str, world_context: str):
        """Generate NPC response with streaming."""
        
        system_prompt = build_system_prompt(
            self.name,
            self.personality,
            self.conversation_history[-5:] if self.conversation_history else [],
            world_context,
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": player_input},
        ]
        
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.ai_model,
            "messages": messages,
            "stream": True,
        }
        
        full_response = ""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status != 200:
                        yield f"{self.name} seems distracted."
                        return
                    
                    async for line in resp.content:
                        if line:
                            try:
                                data = json.loads(line)
                                if "message" in data and "content" in data["message"]:
                                    token = data["message"]["content"]
                                    full_response += token
                                    yield token
                                if data.get("done"):
                                    break
                            except json.JSONDecodeError:
                                continue
            
            # Add to history
            self.conversation_history.append({"role": "user", "content": player_input})
            self.conversation_history.append({"role": "assistant", "content": full_response})
            
        except aiohttp.ClientError:
            yield f"{self.name} is unavailable (Ollama not running)."
    
    def add_memory(self, event: str):
        """Add to conversation memory for context."""
        # This is for explicit memories (important events)
        # The conversation_history handles conversational context
        pass
    
    def clear_history(self):
        """Clear conversation history (e.g., after long absence)."""
        self.conversation_history = []
    
    def get_state(self) -> dict:
        """Get brain state for persistence."""
        return {
            "conversation_history": self.conversation_history,
            "ai_model": self.ai_model,
        }
    
    def load_state(self, state: dict):
        """Restore brain state."""
        self.conversation_history = state.get("conversation_history", [])
        self.ai_model = state.get("ai_model", self.ai_model)
