# Chain-of-Thought Streaming Agent

An agent that streams its reasoning token-by-token, with clean separation between thinking and final answer.

## Key Features

- **Token-level streaming** — watch the model "think" in real-time
- **Structured parsing** — extracts steps from `<thinking>` tags into `ReasoningStep` objects
- **Multi-backend** — works with Ollama (local) or OpenAI / any OpenAI-compatible API
- **Callback architecture** — plug in callbacks for reasoning vs final answer tokens

## Quick Start

```python
from cot_streaming_agent import CoTStreamingAgent, OllamaBackend

backend = OllamaBackend()
agent = CoTStreamingAgent(backend=backend, model="llama3")

response = await agent.think(
    "Why is the sky blue?",
    reasoning_callback=lambda t: print(t, end="", flush=True),
    final_callback=lambda t: print(t, end="", flush=True),
)

print(response.reasoning_trace)  # Structured output
```

## Architecture

```
User Question
    ↓
Build Messages (system + history + user)
    ↓
LLM Backend (stream tokens)
    ↓
Callback Router (reasoning vs final answer)
    ↓
CoT Response Parser
    ↓
CoTResponse { steps[], final_answer, raw_thinking }
```

## Backend Setup

### Ollama (local)
```bash
ollama serve  # already running
ollama pull llama3
```

### OpenAI
```python
backend = OpenAIBackend(
    api_key="sk-...",
    base_url="https://api.openai.com/v1",
)
agent = CoTStreamingAgent(backend=backend, model="gpt-4o")
```

## Prompt Templates

Two included:
- `COT_SYSTEM_PROMPT` — detailed multi-step format (decomposition → retrieval → analysis → verification → synthesis)
- `COT_MINIMAL_PROMPT` — lightweight version for shorter responses

## Key Concepts Demonstrated

1. **Async streaming** — `async for token in backend.chat_completion()` 
2. **Backend abstraction** — swap Ollama ↔ OpenAI without changing agent code
3. **Streaming callbacks** — handle reasoning and final answer separately
4. **Structured output parsing** — regex-based extraction from tagged responses
5. **Conversation memory** — tracks messages across turns
