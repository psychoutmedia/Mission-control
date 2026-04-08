#!/usr/bin/env python3
"""
Async Agent Loop - Production-Ready Agent System

Demonstrates concurrent agent operations using asyncio.
Useful for multi-agent pipelines, parallel tool execution, and scalable AI systems.
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4


class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    DONE = "done"
    ERROR = "error"


@dataclass
class Tool:
    """Represents a tool the agent can use."""
    name: str
    description: str
    func: Callable
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool asynchronously."""
        return await asyncio.to_thread(self.func, **kwargs)


@dataclass
class Message:
    """Agent message for communication."""
    role: str  # "user", "assistant", "tool"
    content: str
    tool_call_id: Optional[str] = None
    tool_name: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Agent:
    """
    Async Agent with tool use capabilities.
    
    Architecture:
    - State machine for agent lifecycle
    - Message history for context
    - Tool registry for extensible actions
    - Async execution for concurrency
    """
    
    name: str
    model: str = "phi3"
    tools: list[Tool] = field(default_factory=list)
    max_iterations: int = 10
    temperature: float = 0.7
    
    # Internal state
    state: AgentState = AgentState.IDLE
    messages: list[Message] = field(default_factory=list)
    iteration: int = 0
    
    def add_tool(self, tool: Tool):
        """Register a tool with the agent."""
        self.tools.append(tool)
    
    async def think(self, system_prompt: str, user_message: str) -> str:
        """
        Simulate agent thinking (LLM call would go here).
        In production, replace with actual Ollama/OpenAI call.
        """
        self.state = AgentState.THINKING
        self.iteration += 1
        
        # Add user message
        self.messages.append(Message(role="user", content=user_message))
        
        # Simulate thinking delay
        await asyncio.sleep(0.5)
        
        # Simple rule-based response (replace with LLM in production)
        response = self._generate_response(system_prompt, user_message)
        
        self.messages.append(Message(role="assistant", content=response))
        self.state = AgentState.DONE
        
        return response
    
    def _generate_response(self, system_prompt: str, user_message: str) -> str:
        """Generate a response (placeholder for LLM)."""
        # Check if we should use a tool
        user_lower = user_message.lower()
        
        if "search" in user_lower or "find" in user_lower:
            return json.dumps({
                "action": "use_tool",
                "tool": "search",
                "query": user_message
            })
        elif "calculate" in user_lower or "compute" in user_lower:
            return json.dumps({
                "action": "use_tool", 
                "tool": "calculator",
                "expression": user_message
            })
        elif "time" in user_lower or "date" in user_lower:
            return json.dumps({
                "action": "use_tool",
                "tool": "get_time",
                "params": {}
            })
        
        return f"I understand: {user_message}"
    
    async def act(self, tool: Tool, **params) -> str:
        """Execute a tool action."""
        self.state = AgentState.ACTING
        
        try:
            result = await tool.execute(**params)
            self.messages.append(Message(
                role="tool",
                content=str(result),
                tool_name=tool.name
            ))
            return str(result)
        except Exception as e:
            self.state = AgentState.ERROR
            return f"Error: {e}"
    
    async def run(self, system_prompt: str, user_message: str) -> str:
        """Run the agent loop."""
        self.state = AgentState.IDLE
        self.iteration = 0
        
        # Think
        response = await self.think(system_prompt, user_message)
        
        # Check if tool use needed
        try:
            parsed = json.loads(response)
            if parsed.get("action") == "use_tool":
                tool_name = parsed.get("tool")
                tool = next((t for t in self.tools if t.name == tool_name), None)
                
                if tool:
                    result = await self.act(tool, **parsed.get("params", {}))
                    return f"{response}\n\nTool result: {result}"
        except json.JSONDecodeError:
            pass
        
        return response
    
    def get_state(self) -> dict:
        """Get agent state snapshot."""
        return {
            "name": self.name,
            "state": self.state.value,
            "iteration": self.iteration,
            "message_count": len(self.messages)
        }


# ─────────────────────────────────────────────────────────────
# Demo: Concurrent Multi-Agent System
# ─────────────────────────────────────────────────────────────

async def demo_single_agent():
    """Demo a single async agent."""
    print("\n" + "="*60)
    print("🤖 Single Async Agent Demo")
    print("="*60)
    
    # Create agent
    agent = Agent(name="Researcher")
    
    # Add tools
    def search_web(query: str) -> str:
        return f"Results for '{query}': [Simulated search results]"
    
    def calculate(expr: str) -> str:
        try:
            # Safe evaluation
            allowed = set('0123456789+-*/.() ')
            if all(c in allowed for c in expr):
                result = eval(expr)  # Note: Use ast.literal_eval in production
                return str(result)
            return "Invalid expression"
        except:
            return "Calculation error"
    
    def get_time() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    agent.add_tool(Tool("search", "Search the web", search_web))
    agent.add_tool(Tool("calculator", "Perform calculations", calculate))
    agent.add_tool(Tool("get_time", "Get current time", get_time))
    
    # Run agent
    system_prompt = "You are a helpful research assistant."
    user_message = "What's the current time?"
    
    print(f"\n📤 User: {user_message}")
    response = await agent.run(system_prompt, user_message)
    print(f"📥 Agent: {response}")
    print(f"\n📊 State: {agent.get_state()}")


async def demo_multi_agent(queries: list[str]):
    """
    Run multiple agents concurrently.
    
    This is the key advantage of async - agents can run
    in parallel, enabling:
    - Parallel research
    - Distributed tool execution
    - Agent swarms
    """
    print("\n" + "="*60)
    print("🌊 Concurrent Multi-Agent Demo")
    print("="*60)
    
    async def run_agent_query(query: str, agent_id: int):
        """Run a single agent query."""
        agent = Agent(name=f"Agent-{agent_id}")
        
        # Add a simple tool
        def process(query: str) -> str:
            return f"Processed: {query.upper()}"
        
        agent.add_tool(Tool("process", "Process data", process))
        
        result = await agent.think("You are a helpful assistant.", query)
        return agent.name, result
    
    # Run all agents concurrently
    print(f"\n🚀 Running {len(queries)} agents in parallel...")
    start = datetime.now()
    
    tasks = [run_agent_query(q, i) for i, q in enumerate(queries)]
    results = await asyncio.gather(*tasks)
    
    elapsed = (datetime.now() - start).total_seconds()
    
    print(f"\n✅ Completed in {elapsed:.2f}s")
    for name, result in results:
        print(f"  {name}: {result[:50]}...")


async def demo_pipeline():
    """Demo agent pipeline (sequential with dependencies)."""
    print("\n" + "="*60)
    print("🔄 Agent Pipeline Demo")
    print("="*60)
    
    # Pipeline stages
    async def stage_1Research():
        await asyncio.sleep(0.3)
        return {"data": "research results", "keywords": ["AI", "LLM"]}
    
    async def stage_2Analyze(research_data: dict):
        await asyncio.sleep(0.2)
        return {
            "analysis": f"Found {len(research_data['keywords'])} topics",
            "topics": research_data["keywords"]
        }
    
    async def stage_3Summarize(analysis: dict):
        await asyncio.sleep(0.1)
        return f"Summary: {analysis['analysis']}"
    
    # Run pipeline
    print("\n🔬 Running research → analyze → summarize pipeline...")
    
    research = await stage_1Research()
    print(f"  📡 Stage 1 (Research): {research['data']}")
    
    analysis = await stage_2Analyze(research)
    print(f"  📊 Stage 2 (Analysis): {analysis['analysis']}")
    
    summary = await stage_3Summarize(analysis)
    print(f"  📝 Stage 3 (Summary): {summary}")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

async def main():
    """Run all demos."""
    print("\n" + "🤖"*30)
    print("ASYNC AGENT LOOP DEMO")
    print("="*60)
    
    # Single agent
    await demo_single_agent()
    
    # Multi-agent (concurrent)
    await demo_multi_agent([
        "What is LLM?",
        "Explain transformers",
        "What is RAG?",
    ])
    
    # Pipeline
    await demo_pipeline()
    
    print("\n" + "="*60)
    print("✅ All demos complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
