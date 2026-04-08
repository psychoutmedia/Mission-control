"""
Hierarchical Agent
Manager agent coordinates specialized worker agents.

Pattern:
- Manager: Breaks down tasks, delegates to workers, synthesizes results
- Workers: Specialized experts (researcher, coder, writer, etc.)

This is how Claude Code and production agents work.

Run with: python hierarchical_agent/agent.py
"""

import json
import sys
sys.path.insert(0, '/Users/marksstephenson/clawd/projects/ollama_extensions')
from client import OllamaClient


# ============================================================
# WORKER AGENTS
# ============================================================

class WorkerAgent:
    """A specialized worker agent."""
    
    def __init__(self, name: str, specialty: str, description: str):
        self.name = name
        self.specialty = specialty
        self.description = description
        self.results = []
    
    def work(self, task: str, client: OllamaClient = None) -> str:
        """Do the work."""
        print(f"\n   👷 {self.name} working on: {task[:50]}...")
        
        # In production: LLM does the actual work
        # For demo: simulate
        
        if self.specialty == "research":
            return f"Research findings for '{task}': Found 3 key sources."
        elif self.specialty == "coding":
            return f"Code solution for '{task}': Implemented with Python."
        elif self.specialty == "writing":
            return f"Written content for '{task}': Professional draft completed."
        elif self.specialty == "analysis":
            return f"Analysis of '{task}': Data processed, insights generated."
        else:
            return f"Completed: {task}"


# ============================================================
# MANAGER AGENT
# ============================================================

class ManagerAgent:
    """
    Manager that coordinates workers.
    
    Flow:
    1. Analyze task
    2. Break into subtasks
    3. Delegate to workers
    4. Collect results
    5. Synthesize into final answer
    """
    
    def __init__(self, name: str = "Manager", model: str = "phi3", client: OllamaClient = None):
        self.name = name
        self.model = model
        self.client = client or OllamaClient()
        
        # Create workers
        self.workers = {
            "researcher": WorkerAgent("Researcher", "research", "Finds information"),
            "coder": WorkerAgent("Coder", "coding", "Writes code"),
            "writer": WorkerAgent("Writer", "writing", "Creates content"),
            "analyst": WorkerAgent("Analyst", "analysis", "Analyzes data"),
        }
    
    def _analyze_task(self, task: str) -> list[dict]:
        """
        Analyze task and create subtask plan.
        
        Returns: [{"worker": "researcher", "task": "..."}, ...]
        """
        task_lower = task.lower()
        subtasks = []
        
        # Research tasks
        if any(w in task_lower for w in ["research", "find", "learn", "what is", "tell me about"]):
            subtasks.append({"worker": "researcher", "task": task})
        
        # Coding tasks
        if any(w in task_lower for w in ["code", "implement", "build", "create", "write code"]):
            subtasks.append({"worker": "coder", "task": task})
        
        # Writing tasks
        if any(w in task_lower for w in ["write", "draft", "create", "blog", "post"]):
            subtasks.append({"worker": "writer", "task": task})
        
        # Analysis tasks
        if any(w in task_lower for w in ["analyze", "compare", "evaluate", "review"]):
            subtasks.append({"worker": "analyst", "task": task})
        
        # Default: research if nothing matched
        if not subtasks:
            subtasks.append({"worker": "researcher", "task": task})
        
        return subtasks
    
    def _synthesize(self, results: list[str], original_task: str) -> str:
        """
        Combine worker results into final answer.
        
        In production: LLM synthesizes results
        """
        synthesis = f"## Task: {original_task}\n\n"
        synthesis += "### Worker Results:\n"
        
        for i, result in enumerate(results, 1):
            synthesis += f"{i}. {result}\n"
        
        synthesis += "\n### Final Summary:\n"
        synthesis += "Based on the worker contributions above, "
        synthesis += "the task has been completed successfully."
        
        return synthesis
    
    def run(self, task: str) -> str:
        """
        Run the hierarchical agent.
        
        1. Analyze task
        2. Delegate to workers
        3. Collect results
        4. Synthesize
        """
        print(f"\n{'='*60}")
        print(f"🎯 Hierarchical Agent Task: {task}")
        print('='*60)
        
        # Step 1: Analyze and plan
        print(f"\n📋 {self.name} analyzing task...")
        subtasks = self._analyze_task(task)
        print(f"   → Created {len(subtasks)} subtasks")
        
        for st in subtasks:
            print(f"      - {st['worker']}: {st['task'][:40]}...")
        
        # Step 2: Delegate to workers
        results = []
        for subtask in subtasks:
            worker_name = subtask["worker"]
            worker = self.workers.get(worker_name)
            
            if worker:
                result = worker.work(subtask["task"], self.client)
                results.append(result)
                print(f"\n   ✓ {worker_name} complete")
        
        # Step 3: Synthesize
        print(f"\n🔄 {self.name} synthesizing results...")
        final = self._synthesize(results, task)
        
        print(f"\n{'='*60}")
        print(f"✅ FINAL RESULT:")
        print(f"{'='*60}")
        print(final)
        
        return final


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏢 Hierarchical Agent Demo")
    print("="*60)
    print("Manager coordinates specialized worker agents")
    
    # Create manager
    manager = ManagerAgent(name="Project Manager")
    
    # Tasks
    tasks = [
        "Research transformers in AI and write a blog post",
        "Build a Python function to sort lists and analyze its performance",
        "Compare LLM pricing and create a comparison document",
    ]
    
    for task in tasks:
        manager.run(task)
        print(f"\n{'='*60}\n")
