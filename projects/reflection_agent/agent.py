"""
Reflection Agent
An agent that learns from its own errors and improves over time.

Key insight: Agents that reflect on failures outperform those that don't.
This demonstrates the self-improvement loop.

Run with: python reflection_agent/agent.py
"""

import json
from dataclasses import dataclass, field
from typing import Callable, Optional


# ============================================================
# TOOLS
# ============================================================

def calculator(expression: str) -> str:
    """Evaluate a math expression."""
    try:
        import math
        if not all(c.isalnum() or c in '+-*/.() ' for c in expression):
            return json.dumps({"error": "Invalid characters"})
        safe_dict = {k: v for k, v in math.__dict__.items() if not k.startswith('_')}
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})


def search(query: str) -> str:
    """Search knowledge base."""
    knowledge = {
        "python": "Python created by Guido van Rossum in 1991.",
        "transformer": "Attention Is All You Need (Vaswani et al., 2017).",
        "automa dynamics": "Robotics company building Helios-1 humanoid.",
    }
    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower:
            return json.dumps({"result": value})
    return json.dumps({"result": f"No info for: {query}"})


TOOLS = {
    "calculator": {"func": calculator, "description": "Evaluate math expressions."},
    "search": {"func": search, "description": "Search for information."},
}


# ============================================================
# REFLECTION SYSTEM
# ============================================================

@dataclass
class Experience:
    """An experience the agent can learn from."""
    task: str
    action: str
    result: str
    success: bool
    reflection: str = ""
    improved_strategy: str = ""


class ReflectionMemory:
    """
    Stores experiences and extracts learning.
    
    In production: would use embeddings to retrieve
    relevant past experiences.
    """
    
    def __init__(self):
        self.experiences: list[Experience] = []
        self.strategies: dict[str, int] = {}  # strategy -> success count
    
    def add_experience(self, experience: Experience):
        """Add an experience and learn from it."""
        self.experiences.append(experience)
        
        # Extract strategy from reflection
        if experience.improved_strategy:
            self.strategies[experience.improved_strategy] = \
                self.strategies.get(experience.improved_strategy, 0) + (1 if experience.success else 0)
    
    def get_lessons(self) -> list[str]:
        """Get learned lessons from past experiences."""
        lessons = []
        for exp in self.experiences:
            if exp.reflection and not exp.success:
                lessons.append(exp.reflection)
        return lessons
    
    def get_best_strategy(self) -> Optional[str]:
        """Get the most successful strategy."""
        if not self.strategies:
            return None
        return max(self.strategies.items(), key=lambda x: x[1])[0]


# ============================================================
# REFLECTION AGENT
# ============================================================

class ReflectionAgent:
    """
    An agent that reflects on its actions and learns.
    
    Cycle:
    1. Act - Take an action
    2. Observe - Get the result
    3. Reflect - Analyze success/failure
    4. Learn - Update strategy for next time
    """
    
    def __init__(self, tools: dict, max_attempts: int = 3):
        self.tools = tools
        self.max_attempts = max_attempts
        self.memory = ReflectionMemory()
        self.name = "ReflectionAgent"
    
    def _execute(self, action: str, input_data: str) -> str:
        """Execute an action."""
        if action not in self.tools:
            return json.dumps({"error": f"Unknown tool: {action}"})
        try:
            return self.tools[action]["func"](input_data)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _reflect(self, task: str, action: str, result: str) -> tuple[str, str]:
        """
        Reflect on the result and generate insights.
        
        Returns: (reflection, improved_strategy)
        """
        result_lower = result.lower()
        
        # Check for errors
        if "error" in result_lower:
            reflection = f"Action '{action}' failed with error. Need to try a different approach."
            improved_strategy = f"retry_with_fix"
            return reflection, improved_strategy
        
        # Check if result is useful
        if "no info" in result_lower or "unknown" in result_lower:
            reflection = f"Action '{action}' didn't get useful information. Should try different tool."
            improved_strategy = f"try_alternative"
            return reflection, improved_strategy
        
        # Success
        reflection = f"Action '{action}' worked well. Result: {result[:50]}..."
        improved_strategy = f"continue_same"
        return reflection, improved_strategy
    
    def _plan_action(self, task: str) -> tuple[str, str]:
        """Plan the next action based on task."""
        task_lower = task.lower()
        
        # Check for math
        if any(op in task for op in ["+", "-", "*", "/", "calculate"]):
            return "calculator", task
        
        # Check for search
        if any(w in task_lower for w in ["what", "who", "explain", "tell me"]):
            return "search", task
        
        # Default
        return "search", task
    
    def run(self, task: str) -> str:
        """Run the reflection agent on a task."""
        print(f"\n{'='*60}")
        print(f"🎯 Task: {task}")
        print('='*60)
        
        # Get lessons from past
        lessons = self.memory.get_lessons()
        if lessons:
            print(f"\n📚 Past lessons:")
            for lesson in lessons[-2:]:
                print(f"   - {lesson}")
        
        # Get best strategy
        best = self.memory.get_best_strategy()
        if best:
            print(f"   Best strategy: {best}")
        
        print(f"\n🔄 Attempting task (max {self.max_attempts} tries)...")
        
        for attempt in range(self.max_attempts):
            # Plan action
            action, input_data = self._plan_action(task)
            print(f"\n   Attempt {attempt + 1}: {action}('{input_data[:30]}...')")
            
            # Execute
            result = self._execute(action, input_data)
            print(f"   → Result: {result[:80]}...")
            
            # Reflect
            reflection, improved_strategy = self._reflect(task, action, result)
            print(f"   🤔 Reflection: {reflection}")
            
            # Learn
            success = "error" not in result.lower()
            experience = Experience(
                task=task,
                action=action,
                result=result,
                success=success,
                reflection=reflection,
                improved_strategy=improved_strategy
            )
            self.memory.add_experience(experience)
            
            if success:
                print(f"\n✅ Success on attempt {attempt + 1}!")
                return result
        
        print(f"\n❌ Failed after {self.max_attempts} attempts")
        return "Task failed"


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    agent = ReflectionAgent(TOOLS)
    
    tasks = [
        "What is Python?",
        "Calculate 15 * 8 + 42",
        "Tell me about transformers",
    ]
    
    print("\n" + "="*60)
    print("🔮 Reflection Agent Demo")
    print("="*60)
    
    for task in tasks:
        result = agent.run(task)
        print(f"\n{'='*60}")
    
    # Show what the agent learned
    print("\n" + "="*60)
    print("📊 Learning Summary")
    print("="*60)
    print(f"Total experiences: {len(agent.memory.experiences)}")
    print(f"Strategies: {agent.memory.strategies}")
    print(f"Lessons: {agent.memory.get_lessons()}")
