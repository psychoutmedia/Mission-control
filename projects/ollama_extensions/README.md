# Ollama Extensions

Clean Python wrapper around Ollama API with enhanced features.

## Features

- **Generate API**: Text generation with streaming support
- **Chat API**: Conversation-style interactions
- **Embeddings**: Generate vector embeddings
- **Model Management**: List, pull, delete models

## Usage

```python
from client import OllamaClient

client = OllamaClient()

# List models
models = client.list_models()

# Generate
result = client.generate("phi3", "Your prompt here")

# Stream
for chunk in client.generate("phi3", "Prompt", stream=True):
    print(chunk["response"], end="")

# Chat
messages = [
    {"role": "user", "content": "Hello!"}
]
response = client.chat("phi3", messages)

# Embeddings
emb = client.embeddings("nomic-embed-text", "Text to embed")
```

## Running Demo

```bash
python client.py
```
