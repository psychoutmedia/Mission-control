# Chain-of-Thought Streaming Agent 🧠✨

> **Watch an LLM think in real-time.** A production-ready agent that streams reasoning token-by-token with structured step extraction, multi-backend support, and clean separation between thought and answer.

## Why This Matters

Chain-of-thought reasoning is fundamental to how modern LLMs solve complex problems. This project demonstrates:

- **Streaming inference** — tokens flow as they're generated, not after complete generation
- **Backend abstraction** — swap local (Ollama) ↔ cloud (OpenAI) without changing agent logic
- **Structured reasoning extraction** — turns raw text into typed `ReasoningStep` objects
- **Async-first architecture** — non-blocking I/O for production deployment

These are the same patterns used in production AI systems: Cursor, Copilot, Perplexity, and every serious LLM API.

---

## Features

| Feature | Description |
|---------|-------------|
| **Token Streaming** | Real-time reasoning display via async callbacks |
| **Multi-Backend** | Ollama (local), OpenAI, or any OpenAI-compatible API |
| **Structured Output** | Extracts typed reasoning steps from raw text |
| **Conversation Memory** | Tracks message history across turns |
| **Clean Separation** | `<thinking>` tags partition reasoning from answer |

---

## Quick Start

```bash
# Install dependencies
pip install openai httpx

# Pull a model (if using Ollama)
ollama pull llama3

# Run the agent
python cot_streaming_agent.py
```

### Python API

```python
import asyncio
from cot_streaming_agent import CoTStreamingAgent, OllamaBackend

async def main():
    backend = OllamaBackend()
    agent = CoTStreamingAgent(backend=backend, model="llama3")
    
    response = await agent.think(
        "Why is the sky blue?",
        reasoning_callback=lambda t: print(f"💭 {t}", end="", flush=True),
        final_callback=lambda t: print(f"\n✨ {t}", end="", flush=True),
    )
    
    # Structured output
    print(f"\n📊 {len(response.steps)} reasoning steps identified")
    for step in response.steps:
        print(f"  {step.step_number}. {step.label}: {step.thought[:50]}...")

asyncio.run(main())
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Query                           │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│            Build Messages (System + History)           │
│                                                         │
│  System: "You are a helpful assistant..."              │
│  History: Previous reasoning + answers                 │
│  User: Current question                                 │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 LLM Backend (Streaming)                 │
│                                                         │
│  OllamaBackend / OpenAIBackend / OpenAICompatible      │
│  Yields tokens as they're generated                     │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Callback Router                            │
│                                                         │
│  Tokens inside <thinking>...</thinking> → reasoning_cb  │
│  Tokens outside thinking tags     → final_cb            │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│              CoT Response Parser                        │
│                                                         │
│  Regex extraction of step labels + thoughts             │
│  Returns typed ReasoningStep[] + final_answer          │
└─────────────────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 CoTResponse                             │
│                                                         │
│  steps: List[ReasoningStep]                             │
│  final_answer: str                                      │
│  raw_thinking: str                                      │
└─────────────────────────────────────────────────────────┘
```

---

## Backend Options

### Ollama (Local, Privacy-First)

```python
from cot_streaming_agent import OllamaBackend

backend = OllamaBackend(base_url="http://localhost:11434")
agent = CoTStreamingAgent(backend=backend, model="llama3")
```

**Advantages:** No data leaves your machine, free inference, full control.

### OpenAI (Cloud)

```python
from cot_streaming_agent import OpenAIBackend

backend = OpenAIBackend(
    api_key="sk-...",
    base_url="https://api.openai.com/v1",
)
agent = CoTStreamingAgent(backend=backend, model="gpt-4o")
```

### OpenAI-Compatible (vLLM, TGI, LM Studio, etc.)

```python
from cot_streaming_agent import OpenAICompatibleBackend

backend = OpenAICompatibleBackend(
    base_url="http://localhost:8080/v1",
    api_key="not-needed",
)
agent = CoTStreamingAgent(backend=backend, model="meta-llama-3-70b")
```

---

## Prompt Templates

### Full CoT (`COT_SYSTEM_PROMPT`)

Structured for complex reasoning with explicit steps:

```
<context>
...
</context>

<instructions>
...
</instructions>

<response_format>
...
</response_format>
```

### Minimal CoT (`COT_MINIMAL_PROMPT`)

Lightweight format for simpler queries with quick responses.

---

## Key Concepts for LLM Engineering

### 1. Async Streaming

```python
async def chat_completion(self, messages: list[Message]) -> AsyncIterator[str]:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            async for line in resp.content:
                # Process SSE stream...
                yield token
```

Async I/O is essential for production LLM systems — you don't want your web server blocked waiting for API responses.

### 2. Backend Abstraction

```python
class LLMBackend(ABC):
    @abstractmethod
    async def chat_completion(self, messages) -> AsyncIterator[str]:
        pass
```

Abstract base class lets you swap providers without changing agent logic. Critical for:
- Development ↔ Production switching
- Cost optimization (Ollama for dev, OpenAI for prod)
- A/B testing different models

### 3. Token Callback Routing

```python
async def _route_tokens(self, raw_stream):
    in_thinking = False
    buffer = ""
    
    async for char in raw_stream:
        buffer += char
        
        if "<thinking>" in buffer:
            in_thinking = True
            buffer = buffer.replace("<thinking>", "")
        elif "</thinking>" in buffer:
            in_thinking = False
            buffer = buffer.replace("</thinking>", "")
            self.reasoning_callback(buffer)
            buffer = ""
        elif in_thinking:
            self.reasoning_callback(char)
        else:
            self.final_callback(char)
```

Real-time token routing is how products like Cursor show "thinking" indicators — essential UX for perceived performance.

### 4. Structured Reasoning Extraction

```python
@dataclass
class ReasoningStep:
    step_number: int
    label: str      # "Problem Decomposition", "Constraint Analysis"
    thought: str
    is_complete: bool
```

Typed extraction enables downstream logic on reasoning — RAG over reasoning traces, evaluation of thought quality, etc.

---

## Production Use Cases

| Use Case | How This Helps |
|----------|----------------|
| **AI Coding Assistants** | Show reasoning while writing code |
| **Research Agents** | Display literature review process |
| **Customer Support** | Transparency on why responses are suggested |
| **Educational Tools** | Show step-by-step problem solving |
| **Debugging AI** | Inspect reasoning paths for errors |

---

## Extending This Project

Ideas for building on this foundation:

- [ ] **Evaluation Framework** — Measure reasoning quality against ground truth
- [ ] **Beam Search** — Explore multiple reasoning branches
- [ ] **Self-Correction Loop** — Add reflection step to verify answer quality
- [ ] **Tool Integration** — Connect reasoning steps to web search, calculator, etc.
- [ ] **Memory** — Persist reasoning across sessions for cumulative learning

---

## Related Projects

| Project | Focus |
|---------|-------|
| `ollama_react_agent/` | ReAct pattern with tool use |
| `反思_agent/` | Self-reflection for error correction |
| `hierarchical_agent/` | Multi-level task decomposition |
| `evaluation_agent/` | RAGAS/BLEU/ROUGE metrics for LLM outputs |

---

## Tech Stack

- **Python 3.11+** — async/await, dataclasses, enum
- **aiohttp** — async HTTP for streaming
- **Ollama / OpenAI** — LLM inference
- **Dataclasses** — typed response models

---

*Built as part of the [LLM Engineering Portfolio](https://github.com/psychoutmedia/Mission-control) — learn-by-building approach to LLM engineering skills.*
