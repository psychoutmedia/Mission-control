# Ollama Setup — Local LLM for Testing

> Created: 2026-03-06

Ollama is installed and ready. This guide covers available models and how to use them.

---

## Status: ✅ Installed

```
$ ollama --version
ollama version 0.17.6
```

---

## Available Models

| Model | Size | Best For |
|-------|------|----------|
| **phi3** | 2.2 GB | Lightweight testing, fast responses |
| **gemma3:270m** | 291 MB | Quick demos, minimal resources |
| **llava** | 4.7 GB | Vision + text (can analyze images) |
| **llava-phi3** | 2.9 GB | Vision + text, lighter |
| **gpt-oss** | 13 GB | More capable, slower |

---

## Quick Start

### 1. List available models
```bash
ollama list
```

### 2. Run a model interactively
```bash
ollama run phi3
```

### 3. Use in Python
```python
from langchain_community.chat_models import ChatOllama

llm = ChatOllama(model="phi3")
response = llm.invoke("Explain transformers in one sentence")
print(response.content)
```

### 4. Use with LangChain (for RAG, agents, etc.)

```python
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage

llm = ChatOllama(model="phi3")

messages = [
    HumanMessage(content="What is attention in transformers?")
]

response = llm.invoke(messages)
print(response.content)
```

---

## Pull New Models

```bash
# Lightweight options
ollama pull llama3.2      # 2GB, latest Llama
ollama pull qwen2.5      # Good for coding
ollama pull mistral      # Balanced

# Larger models (slower, more capable)
ollama pull llama3.1:8b  # 4.7GB
ollama pull codellama    # Coding-focused
```

---

## API Server (for production-like usage)

Start Ollama as an API server:
```bash
ollama serve
```

Then call it:
```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # dummy key
)

response = client.chat.completions.create(
    model="phi3",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

---

## Use Cases for Learning

1. **Test prompts** — quickly iterate without API costs
2. **RAG pipelines** — use local LLM instead of OpenAI
3. **Agent testing** — debug multi-agent systems locally
4. **Fine-tuning experiments** — Ollama supports GGUF models
5. **Privacy** — data never leaves your machine

---

## Memory Optimization

If running low on RAM:
```bash
# Use smaller models
ollama run gemma3:270m   # 291 MB only!

# Or limit CPU threads
OLLAMA_NUM_THREADS=4 ollama run phi3
```

---

## Troubleshooting

**Model won't start?**
```bash
# Check available memory
free -h

# Kill other Ollama processes
ollama ps
ollama kill <model>
```

**Slow responses?**
```bash
# Use quantization (smaller = faster)
# Models with :Q4_0, :Q5_1, etc. are quantized
ollama pull phi3:latest   # Full precision
```

---

## Next Steps

- [ ] Pull llama3 for more capable responses
- [ ] Integrate with RAG chatbot (replace OpenAI with Ollama)
- [ ] Use in ReAct agent demo
- [ ] Experiment with fine-tuning

---

*Local LLM = infinite experimentation without API bills.* ✨
