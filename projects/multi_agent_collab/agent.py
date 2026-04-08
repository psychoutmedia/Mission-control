"""
Multi-Agent Collaboration Demo
Two agents working together: Researcher + Writer.

This pattern is used in production systems like:
- Claude Code (orchestrator + specialized agents)
- AutoGen (conversational agents)
- CrewAI (role-based agents)

Run with: python multi_agent_collab/agent.py
"""

import json
from dataclasses import dataclass, field
from typing import Callable


# ============================================================
# SIMPLE AGENT BASE
# ============================================================

@dataclass
class Message:
    """A message between agents."""
    from_agent: str
    to_agent: str
    content: str
    timestamp: float = 0


class Agent:
    """Base agent with name and tools."""
    
    def __init__(self, name: str, tools: dict = None):
        self.name = name
        self.tools = tools or {}
        self.messages: list[Message] = []
        self.context: dict = {}
    
    def receive(self, message: Message):
        """Receive a message."""
        self.messages.append(message)
    
    def send(self, to_agent: str, content: str):
        """Send a message to another agent."""
        return Message(from_agent=self.name, to_agent=to_agent, content=content)
    
    def act(self, tool_name: str, input_data: str) -> str:
        """Execute a tool."""
        if tool_name not in self.tools:
            return f"Error: Unknown tool {tool_name}"
        try:
            return self.tools[tool_name](input_data)
        except Exception as e:
            return f"Error: {e}"


# ============================================================
# SPECIALIZED AGENTS
# ============================================================

class ResearcherAgent(Agent):
    """
    Research agent - finds and analyzes information.
    
    In production: would use search APIs, read documents,
    extract key insights.
    """
    
    def __init__(self, tools: dict = None):
        super().__init__("Researcher", tools)
        self.role = "research"
    
    def research(self, query: str) -> str:
        """Research a topic and return findings."""
        # Simulate research
        findings = f"Research findings for '{query}':\n"
        findings += "- Key concept 1: Relevant insight\n"
        findings += "- Key concept 2: Important detail\n"
        findings += "- Key concept 3: Critical information\n"
        return findings
    
    def analyze(self, data: str) -> str:
        """Analyze data and extract insights."""
        return f"Analysis of '{data}': Found 3 key patterns."


class WriterAgent(Agent):
    """
    Writer agent - creates content from research.
    
    In production: would generate blog posts, summaries,
    documentation based on research.
    """
    
    def __init__(self, tools: dict = None):
        super().__init__("Writer", tools)
        self.role = "writer"
    
    def write(self, topic: str, research: str) -> str:
        """Write content based on research."""
        content = f"# {topic}\n\n"
        content += "## Overview\n"
        content += f"This document explores {topic} based on recent research.\n\n"
        content += "## Key Findings\n"
        
        # Extract key points from research
        if "findings for" in research.lower():
            lines = research.split("\n")
            for line in lines[1:]:
                if line.strip():
                    content += f"- {line.strip()}\n"
        
        content += "\n## Conclusion\n"
        content += f"The research reveals important insights about {topic} "
        content += "that can inform future work."
        
        return content
    
    def summarize(self, content: str) -> str:
        """Summarize content."""
        words = content.split()
        return f"Summary ({len(words)} words): {content[:100]}..."


# ============================================================
# ORCHESTRATOR
# ============================================================

class Orchestrator:
    """
    Coordinates multiple agents to work on a task.
    
    Patterns:
    1. Sequential: Agent A → Agent B → Agent C
    2. Parallel: Agent A + Agent B (simultaneous)
    3. Hierarchical: Orchestrator delegates to sub-agents
    """
    
    def __init__(self):
        self.agents: dict[str, Agent] = {}
        self.task_queue: list = []
        self.results: dict = {}
    
    def register(self, agent: Agent):
        """Register an agent."""
        self.agents[agent.name] = agent
        print(f"✅ Registered: {agent.name}")
    
    def run_sequential(self, task: str, sequence: list[str]) -> dict:
        """
        Run agents in sequence.
        
        Example: ["Researcher", "Writer"]
        """
        print(f"\n{'='*60}")
        print(f"🎯 Task: {task}")
        print(f"📋 Sequence: {' → '.join(sequence)}")
        print('='*60)
        
        context = {"task": task}
        
        for agent_name in sequence:
            agent = self.agents.get(agent_name)
            if not agent:
                print(f"⚠️ Agent {agent_name} not found")
                continue
            
            print(f"\n👤 {agent.name} working...")
            
            # Determine action based on agent role
            if agent.role == "research":
                result = agent.research(context.get("task", task))
            elif agent.role == "writer":
                result = agent.write(
                    context.get("task", task),
                    context.get("research", "")
                )
            else:
                result = agent.act("default", str(context))
            
            print(f"   → Result: {result[:100]}...")
            context[agent.role] = result
            self.results[agent.name] = result
        
        return self.results
    
    def run_parallel(self, task: str, agent_names: list[str]) -> dict:
        """Run agents in parallel (simulated)."""
        print(f"\n{'='*60}")
        print(f"🎯 Task: {task}")
        print(f"⚡ Parallel: {', '.join(agent_names)}")
        print('='*60)
        
        # In production: would use async/threads
        results = {}
        for name in agent_names:
            agent = self.agents.get(name)
            if agent:
                print(f"\n👤 {agent.name} working in parallel...")
                if agent.role == "research":
                    results[name] = agent.research(task)
                else:
                    results[name] = agent.act("default", task)
        
        return results


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    # Create tools
    tools = {
        "search": lambda q: f"Results for: {q}",
        "write": lambda t: f"Written: {t}",
    }
    
    # Create orchestrator
    orchestrator = Orchestrator()
    
    # Register agents
    researcher = ResearcherAgent(tools)
    writer = WriterAgent(tools)
    orchestrator.register(researcher)
    orchestrator.register(writer)
    
    # Sequential collaboration
    print("\n" + "="*60)
    print("🔄 SEQUENTIAL COLLABORATION")
    print("="*60)
    
    results = orchestrator.run_sequential(
        task="Transformer Architecture",
        sequence=["Researcher", "Writer"]
    )
    
    # Show final output
    print("\n" + "="*60)
    print("📄 FINAL OUTPUT")
    print("="*60)
    print(results.get("Writer", "No output"))
    
    # Parallel collaboration (simplified)
    print("\n" + "="*60)
    print("⚡ PARALLEL COLLABORATION")
    print("="*60)
    
    # Add a second researcher for parallel demo
    researcher2 = ResearcherAgent(tools)
    researcher2.name = "Researcher2"
    orchestrator.register(researcher2)
    
    parallel_results = orchestrator.run_parallel(
        task="LLM Agents",
        agent_names=["Researcher", "Researcher2"]
    )
    
    print("\n📊 Parallel Results:")
    for name, result in parallel_results.items():
        print(f"  {name}: {result[:60]}...")
