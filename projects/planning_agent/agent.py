"""
Planning Agent
ReAct pattern + explicit planning + tool use.

Key insight: Agents that plan outperform those that react.
This demonstrates: think → plan → act → reflect cycle.

Run with: python planning_agent/agent.py
"""

import json
import re
from dataclasses import dataclass, field
from typing import Callable


# ============================================================
# TOOLS
# ============================================================

def calculator(expression: str) -> str:
    """Evaluate a math expression."""
    try:
        import math
        allowed = set('0123456789+-*/.() sqrtpi sin cos tan log exp pow')
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
        "llm": "Large Language Model - neural network trained on massive text.",
        "agent": "AI agent = reasoning + planning + tool use + memory.",
        "automa dynamics": "Robotics company building Helios-1 humanoid.",
    }
    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower:
            return json.dumps({"result": value})
    return json.dumps({"result": f"No info for: {query}"})


def get_weather(city: str) -> str:
    """Get weather for a city."""
    data = {
        "london": {"temp": 12, "condition": "Cloudy"},
        "salford": {"temp": 11, "condition": "Rainy"},
        "new york": {"temp": 8, "condition": "Sunny"},
    }
    city_lower = city.lower()
    if city_lower in data:
        return json.dumps({"city": city, **data[city_lower]})
    return json.dumps({"error": "Unknown city"})


TOOLS = {
    "calculator": {"func": calculator, "description": "Evaluate math expressions."},
    "search": {"func": search, "description": "Search for information."},
    "get_weather": {"func": get_weather, "description": "Get weather for a city."},
}


# ============================================================
# PLANNING AGENT
# ============================================================

@dataclass
class PlanStep:
    """A single step in the plan."""
    step_number: int
    action: str
    reason: str
    completed: bool = False
    result: str = ""


@dataclass
class Thought:
    """Represents agent's thinking at a point in time."""
    thought: str
    action: str = ""
    action_input: str = ""
    observation: str = ""
    plan: list[PlanStep] = field(default_factory=list)


class PlanningAgent:
    """
    An agent that plans before acting.
    
    Cycle:
    1. Think - analyze the situation
    2. Plan - create explicit steps
    3. Act - execute one step
    4. Reflect - evaluate result, update plan
    """
    
    def __init__(self, tools: dict, max_iterations: int = 10):
        self.tools = tools
        self.max_iterations = max_iterations
        self.thought_history: list[Thought] = []
        self.current_plan: list[PlanStep] = []
    
    def _create_initial_plan(self, goal: str) -> list[PlanStep]:
        """
        Create an initial plan based on the goal.
        
        In production: LLM would generate this based on
        understanding the task and available tools.
        """
        goal_lower = goal.lower()
        plan = []
        step_num = 1
        
        # Weather task
        if "weather" in goal_lower:
            # Extract city
            for city in ["london", "salford", "new york", "tokyo", "paris"]:
                if city in goal_lower:
                    plan.append(PlanStep(
                        step_number=step_num,
                        action="get_weather",
                        reason=f"Need to check weather in {city}",
                    ))
                    step_num += 1
                    plan.append(PlanStep(
                        step_number=step_num,
                        action="finalize",
                        reason="Provide weather information to user",
                    ))
                    break
        
        # Math task
        elif any(op in goal for op in ["+", "-", "*", "/", "calculate"]):
            plan.append(PlanStep(
                step_number=step_num,
                action="calculator",
                reason="Need to calculate the expression",
            ))
            step_num += 1
            plan.append(PlanStep(
                step_number=step_num,
                action="finalize",
                reason="Provide calculation result",
            ))
        
        # Search task
        elif any(w in goal_lower for w in ["what", "who", "explain", "tell me"]):
            plan.append(PlanStep(
                step_number=step_num,
                action="search",
                reason=f"Search for: {goal}",
            ))
            step_num += 1
            plan.append(PlanStep(
                step_number=step_num,
                action="finalize",
                reason="Provide information to user",
            ))
        
        # Unknown task
        else:
            plan.append(PlanStep(
                step_number=step_num,
                action="finalize",
                reason="Provide direct answer",
            ))
        
        return plan
    
    def _simulate_llm(self, goal: str, iteration: int) -> Thought:
        """
        Simulate LLM reasoning with planning.
        
        In production: would call actual LLM with:
        - Current goal
        - Available tools
        - Current plan status
        - Previous observations
        """
        thought = Thought(thought="Analyzing the task...")
        
        # First iteration: create plan
        if iteration == 0:
            self.current_plan = self._create_initial_plan(goal)
            thought.thought = f"Created plan with {len(self.current_plan)} steps"
            thought.plan = self.current_plan
            return thought
        
        # Find next incomplete step
        next_step = None
        for step in self.current_plan:
            if not step.completed:
                next_step = step
                break
        
        if next_step:
            thought.thought = f"Executing step {next_step.step_number}: {next_step.action}"
            thought.action = next_step.action
            thought.action_input = "extracted from goal"  # Would extract from context
            thought.plan = self.current_plan
        else:
            thought.thought = "All steps complete"
            thought.action = "finalize"
        
        return thought
    
    def _execute_tool(self, action: str, action_input: str) -> str:
        """Execute a tool and return result."""
        if action == "finalize":
            return "DONE"
        
        if action not in self.tools:
            return json.dumps({"error": f"Unknown tool: {action}"})
        
        try:
            func = self.tools[action]["func"]
            # Extract actual input from goal
            result = func(action_input)
            return result
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def run(self, goal: str) -> str:
        """Run the planning agent on a goal."""
        print(f"\n{'='*60}")
        print(f"🎯 Goal: {goal}")
        print('='*60)
        
        self.thought_history = []
        self.current_plan = []
        
        for i in range(self.max_iterations):
            # Think & Plan
            thought = self._simulate_llm(goal, i)
            print(f"\n🤔 Think: {thought.thought}")
            
            if thought.plan:
                print(f"📋 Plan:")
                for step in thought.plan:
                    status = "✓" if step.completed else " "
                    print(f"   {status} {step.step_number}. {step.action} - {step.reason}")
            
            # Act
            if thought.action and thought.action != "finalize":
                print(f"\n🔧 Act: {thought.action}")
                
                # Execute
                result = self._execute_tool(thought.action, thought.action_input)
                print(f"   → Result: {result}")
                
                # Mark step complete
                for step in self.current_plan:
                    if step.action == thought.action and not step.completed:
                        step.completed = True
                        step.result = result
                        break
                
                thought.observation = result
                self.thought_history.append(thought)
                
            elif thought.action == "finalize":
                # Gather results
                results = [s.result for s in self.current_plan if s.result]
                if results:
                    final = results[-1]
                    # Parse if JSON
                    try:
                        data = json.loads(final)
                        final = data.get("result", data.get("error", final))
                    except:
                        pass
                    print(f"\n✅ Final Answer: {final}")
                    return final
                print(f"\n✅ Completed")
                return "Done"
        
        return "Max iterations reached"


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    agent = PlanningAgent(TOOLS)
    
    goals = [
        "What's the weather in Salford?",
        "Calculate (15 * 8) + 42",
        "What is Python?",
    ]
    
    print("\n" + "="*60)
    print("📝 Planning Agent Demo")
    print("="*60)
    
    for goal in goals:
        result = agent.run(goal)
        print(f"\n{'='*60}")
