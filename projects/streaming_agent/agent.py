"""
Streaming Response Agent
Real-time token-by-token response streaming.

Shows:
- Chunk-by-chunk output
- Progress indicators
- First token latency

Run with: python streaming_agent/agent.py
"""

import sys
import time
sys.path.insert(0, '/Users/marksstephenson/clawd/projects/ollama_extensions')
from client import OllamaClient


class StreamingAgent:
    """An agent that streams responses token by token."""
    
    def __init__(self, model: str = "phi3", client: OllamaClient = None):
        self.model = model
        self.client = client or OllamaClient()
    
    def generate(self, prompt: str, show_timing: bool = True):
        """Generate with streaming."""
        print(f"\n{'='*50}")
        print(f"❓ Prompt: {prompt[:50]}...")
        print(f"{'='*50}")
        print("\n🤖 Response: ", end="", flush=True)
        
        start_time = time.time()
        first_token_time = None
        token_count = 0
        
        # Stream response
        for chunk in self.client.generate(self.model, prompt, stream=True):
            if "response" in chunk:
                text = chunk["response"]
                print(text, end="", flush=True)
                token_count += 1
                
                if first_token_time is None:
                    first_token_time = time.time() - start_time
        
        total_time = time.time() - start_time
        
        if show_timing:
            print(f"\n\n📊 Timing:")
            print(f"   First token: {first_token_time:.2f}s")
            print(f"   Total time: {total_time:.2f}s")
            print(f"   Tokens: {token_count}")
            print(f"   Speed: {token_count/total_time:.1f} tok/s")


if __name__ == "__main__":
    client = OllamaClient()
    
    if not client.is_available():
        print("❌ Ollama not running")
        sys.exit(1)
    
    print("="*50)
    print("🌊 Streaming Response Agent")
    print("="*50)
    
    agent = StreamingAgent(model="phi3")
    
    prompts = [
        "Explain transformers in AI in one sentence.",
        "What is Python?",
    ]
    
    for prompt in prompts:
        agent.generate(prompt)
        print("\n" + "-"*50)
