"""
Ollama Python Extensions
Clean wrapper around Ollama API with streaming, embeddings, and model management.

Run: python -m ollama_extensions.client
"""

import requests
import json
import os
from typing import Iterator, Generator


class OllamaClient:
    """
    Python client for Ollama API.
    
    Features:
    - Generate (with streaming)
    - Embeddings
    - Model management
    - Chat API
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.timeout = 120
    
    # ============================================================
    # GENERATE API
    # ============================================================
    
    def generate(self, model: str, prompt: str, 
                 stream: bool = False, **kwargs) -> dict | Generator[dict, None, None]:
        """
        Generate text from a model.
        
        Args:
            model: Model name (e.g., 'phi3', 'gemma3:270m')
            prompt: Input prompt
            stream: Enable streaming responses
            **kwargs: Additional params (temperature, top_p, etc.)
        
        Returns:
            dict response or generator of chunks
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            **kwargs
        }
        
        if stream:
            return self._stream_request(url, payload)
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def _stream_request(self, url: str, payload: dict) -> Generator[dict, None, None]:
        """Handle streaming requests."""
        response = requests.post(url, json=payload, stream=True, timeout=self.timeout)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                yield data
                if data.get("done"):
                    break
    
    def generate_stream(self, model: str, prompt: str, **kwargs) -> str:
        """
        Generate text with streaming, return complete response.
        """
        full_response = ""
        for chunk in self.generate(model, prompt, stream=True, **kwargs):
            if "response" in chunk:
                full_response += chunk["response"]
        return full_response
    
    # ============================================================
    # CHAT API
    # ============================================================
    
    def chat(self, model: str, messages: list[dict],
             stream: bool = False, **kwargs) -> dict | Generator[dict, None, None]:
        """
        Chat completion API.
        
        Args:
            model: Model name
            messages: List of {"role": "user/assistant/system", "content": "..."}
            stream: Enable streaming
            **kwargs: Additional params
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        if stream:
            return self._stream_request(url, payload)
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def chat_stream(self, model: str, messages: list[dict], **kwargs) -> str:
        """Chat with streaming, return complete response."""
        full_response = ""
        for chunk in self.chat(model, messages, stream=True, **kwargs):
            if "message" in chunk and "content" in chunk["message"]:
                full_response += chunk["message"]["content"]
        return full_response
    
    # ============================================================
    # EMBEDDINGS
    # ============================================================
    
    def embeddings(self, model: str, prompt: str) -> list[float]:
        """
        Generate embeddings for a prompt.
        
        Args:
            model: Embedding model (e.g., 'nomic-embed-text')
            prompt: Text to embed
        
        Returns:
            List of embedding vectors
        """
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": model,
            "prompt": prompt
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()["embedding"]
    
    # ============================================================
    # MODEL MANAGEMENT
    # ============================================================
    
    def list_models(self) -> list[dict]:
        """List available models."""
        url = f"{self.base_url}/api/tags"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()["models"]
    
    def get_model_info(self, model: str) -> dict:
        """Get model information."""
        url = f"{self.base_url}/api/show"
        payload = {"name": model}
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def pull_model(self, model: str, stream: bool = True):
        """Pull a model from Ollama library."""
        url = f"{self.base_url}/api/pull"
        payload = {"name": model, "stream": stream}
        
        if stream:
            return self._stream_request(url, payload)
        
        response = requests.post(url, json=payload, timeout=600)
        response.raise_for_status()
        return response.json()
    
    def delete_model(self, model: str) -> dict:
        """Delete a model."""
        url = f"{self.base_url}/api/delete"
        payload = {"name": model}
        response = requests.delete(url, json=payload, timeout=30)
        response.raise_for_status()
        return {"status": "deleted", "model": model}
    
    # ============================================================
    # UTILITIES
    # ============================================================
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            self.list_models()
            return True
        except:
            return False


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    client = OllamaClient()
    
    print("=" * 50)
    print("🧠 Ollama Extensions Demo")
    print("=" * 50)
    
    # Check availability
    print(f"\n✅ Ollama available: {client.is_available()}")
    
    # List models
    print("\n📦 Available models:")
    models = client.list_models()
    for m in models:
        size_gb = m["size"] / (1024**3)
        print(f"  - {m['name']} ({size_gb:.1f} GB)")
    
    # Generate (non-streaming)
    print("\n💬 Generate (non-streaming):")
    result = client.generate("phi3", "What is a transformer in AI?", stream=False)
    print(f"  Response: {result['response'][:200]}...")
    
    # Generate (streaming)
    print("\n💬 Generate (streaming):")
    print("  ", end="")
    for chunk in client.generate("phi3", "Explain neural networks in one sentence.", stream=True):
        if "response" in chunk:
            print(chunk["response"], end="", flush=True)
    print()
    
    # Chat
    print("\n💬 Chat API:")
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What is PyTorch?"}
    ]
    response = client.chat("phi3", messages)
    print(f"  Assistant: {response['message']['content'][:150]}...")
    
    # Embeddings (if nomic-embed-text is available)
    print("\n📊 Embeddings:")
    try:
        emb = client.embeddings("nomic-embed-text", "Hello world")
        print(f"  Embedding dim: {len(emb)}")
    except Exception as e:
        print(f"  Note: Embedding model not available ({e})")
