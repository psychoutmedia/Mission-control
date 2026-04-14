"""
Chain-of-Thought Streaming Agent
===============================
Demonstrates how to build an agent that streams its reasoning steps
token-by-token while maintaining a clean separation between thought
and final answer.

Key concepts:
- Stream reasoning tokens as they're generated
- Separates "thinking" (internal reasoning) from "output" (final answer)
- Supports multiple backend providers (Ollama, OpenAI-compatible)
- Shows step-by-step reasoning structure
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, AsyncIterator
from enum import Enum
import json


# ─────────────────────────────────────────────────────────
# Message & Step Models
# ─────────────────────────────────────────────────────────

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    role: MessageRole
    content: str


@dataclass
class ReasoningStep:
    step_number: int
    label: str  # e.g., "Problem Decomposition", "Constraint Analysis"
    thought: str
    is_complete: bool = False


@dataclass
class CoTResponse:
    """Complete response with structured reasoning and answer."""
    steps: list[ReasoningStep]
    final_answer: str
    raw_thinking: str  # Full unprocessed thinking for reference

    @property
    def reasoning_trace(self) -> str:
        """Human-readable reasoning trace."""
        lines = []
        for step in self.steps:
            status = "✓" if step.is_complete else "→"
            lines.append(f"{status} Step {step.step_number}: {step.label}")
            lines.append(f"  {step.thought}")
        lines.append(f"\n📝 Final Answer:\n{self.final_answer}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────
# Backend Abstractions
# ─────────────────────────────────────────────────────────

class LLMBackend(ABC):
    """Abstract base for LLM backends."""

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict],
        model: str,
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[str]:
        """Yield tokens from the model."""
        ...

    @abstractmethod
    async def close(self):
        ...


class OllamaBackend(LLMBackend):
    """Ollama local LLM backend."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self._client = None

    async def chat_completion(
        self,
        messages: list[dict],
        model: str,
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[str]:
        import httpx
        async with httpx.AsyncClient(timeout=120) as client:
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream,
            }
            payload.update(kwargs)

            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "message" in data:
                            yield data["message"].get("content", "")
                        elif data.get("done"):
                            break

    async def close(self):
        pass


class OpenAIBackend(LLMBackend):
    """OpenAI / OpenAI-compatible API backend."""

    def __init__(
        self,
        api_key: str = "sk-replace-with-key",
        base_url: str = "https://api.openai.com/v1",
    ):
        self.api_key = api_key
        self.base_url = base_url

    async def chat_completion(
        self,
        messages: list[dict],
        model: str,
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[str]:
        import httpx
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=120) as client:
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream,
            }
            payload.update(kwargs)

            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line and line.startswith("data: "):
                        if line.strip() == "data: [DONE]":
                            break
                        data = json.loads(line[6:])
                        choices = data.get("choices", [])
                        if choices and "delta" in choices[0]:
                            content = choices[0]["delta"].get("content", "")
                            if content:
                                yield content


# ─────────────────────────────────────────────────────────
# Prompt Templates
# ─────────────────────────────────────────────────────────

COT_SYSTEM_PROMPT = """You are a careful reasoning assistant. Before giving your final answer,
THINK STEP BY STEP inside <thinking>...</thinking> tags.

Structure your thinking into clearly labeled steps:
- Step 1: Problem Decomposition (break down what is being asked)
- Step 2: Relevant Knowledge Retrieval (what facts/concepts apply)
- Step 3: Analysis & Reasoning (work through the problem)
- Step 4: Verification (check for errors or edge cases)
- Step 5: Final Answer Synthesis

Wrap your COMPLETE thinking in <thinking> tags.
After your thinking, write your final answer on its own line starting with "Final Answer:".


Example format:

<thinking>
Step 1: Problem Decomposition
The user asks what 2+2 equals. This is a basic arithmetic problem.

Step 2: Relevant Knowledge Retrieval
I know that addition combines two quantities. The number 2 represents a quantity of 2.

Step 3: Analysis & Reasoning
2 + 2 means: take 2 items, add 2 more items → total is 4 items.

Step 4: Verification
4 is correct: 2+1=3, 3+1=4. All checks out.

Step 5: Final Answer Synthesis
The answer is 4.
</thinking>
Final Answer: 4
"""


COT_MINIMAL_PROMPT = """Think step by step before answering. Show your reasoning.
Format:
<thinking>
[Your step-by-step reasoning here]
</thinking>
Final Answer: [Your answer]
"""


# ─────────────────────────────────────────────────────────
# Step Parsing
# ─────────────────────────────────────────────────────────

def parse_cot_response(full_text: str) -> CoTResponse:
    """
    Parse the structured CoT response into steps + final answer.
    Handles partial/incomplete responses gracefully.
    """
    import re

    steps = []
    thinking_blocks = re.findall(r"<thinking>(.*?)</thinking>", full_text, re.DOTALL)

    if not thinking_blocks:
        # No structured thinking — treat entire response as answer
        return CoTResponse(
            steps=[],
            final_answer=full_text.strip(),
            raw_thinking="",
        )

    raw_thinking = thinking_blocks[0]

    # Try to parse structured steps
    step_pattern = r"Step\s+(\d+)[:\s]+(.+?)(?=\nStep\s+\d|</thinking>)"
    matches = re.findall(step_pattern, raw_thinking, re.DOTALL | re.IGNORECASE)

    if matches:
        for num_str, content in matches:
            steps.append(ReasoningStep(
                step_number=int(num_str),
                label=content.split("\n")[0].strip() if "\n" in content else content[:50],
                thought=content.strip(),
                is_complete=True,
            ))
    else:
        # Fallback: treat each paragraph as a step
        paragraphs = [p.strip() for p in raw_thinking.split("\n\n") if p.strip()]
        for i, para in enumerate(paragraphs, 1):
            steps.append(ReasoningStep(
                step_number=i,
                label=f"Step {i}",
                thought=para,
                is_complete=True,
            ))

    # Extract final answer
    final_match = re.search(r"Final Answer:\s*(.+)$", full_text, re.MULTILINE | re.IGNORECASE)
    final_answer = final_match.group(1).strip() if final_match else "(no final answer found)"

    return CoTResponse(
        steps=steps,
        final_answer=final_answer,
        raw_thinking=raw_thinking,
    )


# ─────────────────────────────────────────────────────────
# Main CoT Streaming Agent
# ─────────────────────────────────────────────────────────

class CoTStreamingAgent:
    """
    An agent that streams chain-of-thought reasoning token-by-token
    while preserving step structure.
    """

    def __init__(
        self,
        backend: LLMBackend,
        model: str = "llama3",
        system_prompt: str = COT_SYSTEM_PROMPT,
        show_steps: bool = True,
    ):
        self.backend = backend
        self.model = model
        self.system_prompt = system_prompt
        self.show_steps = show_steps
        self.messages: list[Message] = []

    def _build_messages(self, user_input: str) -> list[dict]:
        msgs = [{"role": "system", "content": self.system_prompt}]
        for msg in self.messages:
            msgs.append({"role": msg.role.value, "content": msg.content})
        msgs.append({"role": "user", "content": user_input})
        return msgs

    async def think(
        self,
        user_input: str,
        reasoning_callback=None,
        final_callback=None,
    ) -> CoTResponse:
        """
        Stream the model's thinking and return a structured CoTResponse.

        Args:
            user_input: The user's question
            reasoning_callback: Called with (token) as reasoning streams
            final_callback: Called with (token) as final answer streams
        """
        messages = self._build_messages(user_input)
        buffer = ""
        in_thinking = False
        in_final = False

        reasoning_buffer = ""
        final_buffer = ""

        async for token in self.backend.chat_completion(
            messages=messages,
            model=self.model,
            stream=True,
        ):
            buffer += token

            # Track what section we're in
            if "<thinking>" in buffer and not in_thinking:
                in_thinking = True
                in_final = False
            if "</thinking>" in buffer and in_thinking:
                in_thinking = False
            if "Final Answer:" in buffer and not in_thinking:
                in_final = True

            if in_thinking and not in_final:
                reasoning_buffer += token
                if reasoning_callback:
                    reasoning_callback(token)
            elif in_final:
                final_buffer += token
                if final_callback:
                    final_callback(token)

        # Store conversation
        self.messages.append(Message(role=MessageRole.USER, content=user_input))
        self.messages.append(Message(
            role=MessageRole.ASSISTANT,
            content=buffer,
        ))

        return parse_cot_response(buffer)

    async def think_simple(self, user_input: str) -> AsyncIterator[str]:
        """
        Simpler streaming — just yields all tokens.
        """
        messages = self._build_messages(user_input)
        async for token in self.backend.chat_completion(
            messages=messages,
            model=self.model,
            stream=True,
        ):
            yield token

    def reset(self):
        """Clear conversation history."""
        self.messages = []


# ─────────────────────────────────────────────────────────
# Demo & Testing
# ─────────────────────────────────────────────────────────

async def demo_streaming():
    """Demo with Ollama backend (or mock if Ollama unavailable)."""

    # Try Ollama first
    try:
        backend = OllamaBackend()
        model = "llama3"
        print(f"Using Ollama with model: {model}")
    except Exception:
        print("Ollama not available — using mock stream for demo")
        backend = None
        model = "mock"

    # If no backend, run a mock demo
    if backend is None:
        print("\n" + "=" * 60)
        print("MOCK DEMO — showing the streaming output format")
        print("=" * 60)

        mock_response = """<thinking>
Step 1: Problem Decomposition
The user asks us to explain why the sky is blue. This is a physics question about light scattering.

Step 2: Relevant Knowledge Retrieval
I recall Rayleigh scattering — shorter wavelengths scatter more than longer wavelengths. Blue light (~450nm) has a shorter wavelength than red (~650nm).

Step 3: Analysis & Reasoning
When sunlight enters Earth's atmosphere, it collides with molecules and particles. Blue light scatters in all directions much more than red light. This is why the sky appears blue during the day.

Step 4: Verification
This explains why sunsets are red/orange — at low angles, sunlight travels through more atmosphere, blue light scatters away, leaving red.
</thinking>
Final Answer: The sky is blue because of Rayleigh scattering — blue light's shorter wavelength causes it to scatter across the atmosphere much more than red light, making blue the dominant color we see during daylight hours.
"""

        async def mock_stream():
            for char in mock_response:
                await asyncio.sleep(0.01)  # Simulate streaming
                yield char

        agent = None
        async for token in mock_stream():
            print(token, end="", flush=True)
        print("\n")
        return agent

    # Real streaming demo
    agent = CoTStreamingAgent(backend=backend, model=model)

    question = "Why is the sky blue? Think step by step."

    print(f"\nQ: {question}\n")
    print("─" * 40)
    print("Streaming reasoning:\n")

    collected_response = ""

    def on_token(token: str):
        print(token, end="", flush=True)
        nonlocal collected_response
        collected_response += token

    def on_final(token: str):
        print(token, end="", flush=True)

    response = await agent.think(
        question,
        reasoning_callback=on_token,
        final_callback=on_final,
    )

    print("\n")
    print("─" * 40)
    print("\nStructured Parsed Output:")
    print(response.reasoning_trace)

    await backend.close()
    return agent


if __name__ == "__main__":
    print("=" * 60)
    print("CHAIN-OF-THOUGHT STREAMING AGENT — Demo")
    print("=" * 60)
    asyncio.run(demo_streaming())
