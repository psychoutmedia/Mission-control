#!/usr/bin/env python3
"""
Multi-Agent Orchestration Demo

Demonstrates how multiple specialized agents can collaborate.
"""

import json
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class AgentType(Enum):
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher"
    CODER = "coder"
    REVIEWER = "reviewer"
    WRITER = "writer"


@dataclass
class Message:
    """A message between agents."""
    from_agent: AgentType
    to_agent: AgentType
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass
class Agent:
    """Base agent class."""
    name: str
    role: AgentType
    specialty: str
    tools: dict = field(default_factory=dict)
    memory: list = field(default_factory=list)
    
    def receive(self, message: Message) -> str:
        """Process a message and return response."""
        self.memory.append(message)
        return self.think(message)
    
    def think(self, message: Message) -> str:
        """Agent-specific thinking. Override in subclasses."""
        return f"{self.name} received: {message.content}"
    
    def use_tool(self, tool_name: str, *args, **kwargs) -> str:
        """Use a tool."""
        if tool_name not in self.tools:
            return f"Error: {tool_name} not available"
        return self.tools[tool_name](*args, **kwargs)


class Orchestrator(Agent):
    """The main coordinator agent."""
    
    def __init__(self, agents: dict):
        super().__init__(
            name="Orchestrator",
            role=AgentType.ORCHESTRATOR,
            specialty="Task planning and delegation"
        )
        self.agents = agents
        self.task_plan: list = []
    
    def think(self, message: Message) -> str:
        """Plan and delegate tasks."""
        task = message.content
        
        # Simple planning: delegate to appropriate agents
        if "research" in task.lower() or "find" in task.lower():
            self.task_plan = [AgentType.RESEARCHER, AgentType.WRITER]
        elif "code" in task.lower() or "build" in task.lower():
            self.task_plan = [AgentType.CODER, AgentType.REVIEWER, AgentType.WRITER]
        elif "write" in task.lower():
            self.task_plan = [AgentType.WRITER]
        else:
            self.task_plan = [AgentType.RESEARCHER, AgentType.CODER, AgentType.WRITER]
        
        return f"Planned task flow: {' → '.join(a.value for a in self.task_plan)}"
    
    def next_step(self) -> Optional[AgentType]:
        """Get next agent in the plan."""
        if self.task_plan:
            return self.task_plan.pop(0)
        return None


class ResearcherAgent(Agent):
    """Agent that researches information."""
    
    def __init__(self):
        knowledge = {
            "transformer": "Transformer is a deep learning architecture introduced in 2017 'Attention Is All You Need' paper. Uses self-attention mechanism.",
            "llm": "Large Language Model - AI trained on vast text data to generate human-like text.",
            "rag": "Retrieval-Augmented Generation - combines LLM with external knowledge retrieval.",
            "react": "ReAct - Reasoning and Acting. Prompting pattern that combines reasoning steps with tool use.",
        }
        
        super().__init__(
            name="Researcher",
            role=AgentType.RESEARCHER,
            specialty="Information retrieval",
            tools={"search": lambda q: knowledge.get(q.lower(), f"No info on: {q}")}
        )
    
    def think(self, message: Message) -> str:
        query = message.content.replace("Research ", "").replace("Find ", "")
        result = self.use_tool("search", query)
        return f"Research findings: {result}"


class CoderAgent(Agent):
    """Agent that writes code."""
    
    def __init__(self):
        super().__init__(
            name="Coder",
            role=AgentType.CODER,
            specialty="Code generation",
            tools={
                "write_code": self._mock_write,
                "execute": lambda c: "Code executed successfully (mock)"
            }
        )
    
    def _mock_write(self, filename: str, code: str) -> str:
        return f"Would write {len(code)} chars to {filename}"
    
    def think(self, message: Message) -> str:
        return f"Generated code: def solution():\n    # {message.content}\n    pass"


class ReviewerAgent(Agent):
    """Agent that reviews code."""
    
    def __init__(self):
        super().__init__(
            name="Reviewer",
            role=AgentType.REVIEWER,
            specialty="Code review"
        )
    
    def think(self, message: Message) -> str:
        return "Code review: Looks good! Consider adding error handling."


class WriterAgent(Agent):
    """Agent that writes content."""
    
    def __init__(self):
        super().__init__(
            name="Writer",
            role=AgentType.WRITER,
            specialty="Content creation"
        )
    
    def think(self, message: Message) -> str:
        return f"Final output: {message.content}"


class MultiAgentSystem:
    """Multi-agent orchestration system."""
    
    def __init__(self):
        self.agents = {
            AgentType.RESEARCHER: ResearcherAgent(),
            AgentType.CODER: CoderAgent(),
            AgentType.REVIEWER: ReviewerAgent(),
            AgentType.WRITER: WriterAgent(),
        }
        
        self.orchestrator = Orchestrator(self.agents)
        self.agents[AgentType.ORCHESTRATOR] = self.orchestrator
    
    def run(self, task: str) -> str:
        print(f"\n{'='*60}")
        print(f"Task: {task}")
        print('='*60)
        
        current_agent = self.orchestrator
        message = Message(
            from_agent=AgentType.ORCHESTRATOR,
            to_agent=AgentType.ORCHESTRATOR,
            content=task
        )
        
        max_steps = 10
        for step in range(max_steps):
            response = current_agent.receive(message)
            print(f"\n{current_agent.name}: {response}")
            
            # If we're at orchestrator, get next specialist
            if isinstance(current_agent, Orchestrator):
                next_agent_type = current_agent.next_step()
                if next_agent_type:
                    current_agent = self.agents[next_agent_type]
                    message = Message(
                        from_agent=AgentType.ORCHESTRATOR,
                        to_agent=next_agent_type,
                        content=task
                    )
                    continue
                else:
                    # No more steps - task complete
                    break
            else:
                # Specialist done - return to orchestrator for next step
                current_agent = self.orchestrator
                message = Message(
                    from_agent=current_agent.role,
                    to_agent=AgentType.ORCHESTRATOR,
                    content=response
                )
                continue
        
        return "Max steps reached"


if __name__ == "__main__":
    system = MultiAgentSystem()
    
    tasks = [
        "Research transformer architecture and write a summary",
        "Build a RAG system with code",
        "Write a blog post about AI",
    ]
    
    print("🤖 Multi-Agent Orchestration Demo")
    print("="*60)
    
    for task in tasks:
        result = system.run(task)
        print(f"\n✅ Result: {result}")
