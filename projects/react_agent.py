"""
ReAct Agent Demo
A minimal but complete implementation of the ReAct pattern.

Run with: python projects/react_agent.py
"""

import re
from dataclasses import dataclass


# ============================================================
# TOOLS - Functions the agent can call
# ============================================================

def calculator(expression: str) -> str:
    """Evaluate a math expression."""
    try:
        allowed = set('0123456789+-*/.() ')
        if not all(c in allowed for c in expression):
            return "Error: Only basic math operations allowed"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def search(query: str) -> str:
    """Simulate a search tool (in production, use real API)."""
    knowledge = {
        "python creator": "Python was created by Guido van Rossum in 1991.",
        "pytorch": "PyTorch is a deep learning framework by Meta AI, released in 2016.",
        "transformer": "The Transformer architecture was introduced in 'Attention Is All You Need' (2017).",
        "react pattern": "ReAct was introduced by Yao et al. in 2022, combining reasoning and acting.",
        "gpt-4": "GPT-4 is OpenAI's multimodal LLM released in March 2023.",
        "claude": "Claude is Anthropic's AI assistant, with Claude 3 released in 2024.",
    }
    
    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower:
            return value
    return f"No results found for: {query}"


def get_weather(city: str) -> str:
    """Get weather for a city (mock data)."""
    weather_data = {
        "london": "London: 12°C, Cloudy",
        "new york": "New York: 8°C, Sunny",
        "tokyo": "Tokyo: 18°C, Clear",
        "salford": "Salford: 11°C, Light rain",
    }
    return weather_data.get(city.lower(), f"Weather data not available for {city}")


TOOLS = {
    "calculator": {
        "func": calculator,
        "description": "Evaluate math expressions. Input: mathematical expression as string.",
    },
    "search": {
        "func": search,
        "description": "Search for information. Input: search query string.",
    },
    "get_weather": {
        "func": get_weather,
        "description": "Get current weather. Input: city name.",
    },
}


# ============================================================
# REACT AGENT
# ============================================================

@dataclass
class AgentStep:
    """One step in the agent's reasoning."""
    thought: str
    action: str | None = None
    action_input: str | None = None
    observation: str | None = None


class ReActAgent:
    """A ReAct agent that reasons step-by-step and uses tools."""
    
    def __init__(self, tools: dict, max_steps: int = 5):
        self.tools = tools
        self.max_steps = max_steps
        self.steps: list[AgentStep] = []
    
    def _build_prompt(self, question: str) -> str:
        """Build the prompt with tool descriptions and history."""
        tool_desc = "\n".join(
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        )
        
        history = ""
        for step in self.steps:
            history += f"\nThought: {step.thought}"
            if step.action:
                history += f"\nAction: {step.action}"
                history += f"\nAction Input: {step.action_input}"
                history += f"\nObservation: {step.observation}"
        
        return f"""Answer the following question using the available tools.

Available tools:
{tool_desc}

Use this format:
Thought: reason about what to do
Action: tool_name
Action Input: input for the tool
Observation: result from the tool
... (repeat Thought/Action/Observation as needed)
Thought: I now have enough information
Final Answer: your answer

Question: {question}
{history}
Thought:"""
    
    def _parse_action(self, response: str) -> tuple[str, str] | None:
        """Extract action and input from LLM response."""
        action_match = re.search(r"Action:\s*(\w+)", response)
        input_match = re.search(r"Action Input:\s*(.+?)(?:\n|$)", response)
        
        if action_match and input_match:
            return action_match.group(1), input_match.group(1).strip()
        return None
    
    def _execute_tool(self, action: str, action_input: str) -> str:
        """Execute a tool and return the result."""
        if action not in self.tools:
            return f"Error: Unknown tool '{action}'"
        
        tool_func = self.tools[action]["func"]
        try:
            return tool_func(action_input)
        except Exception as e:
            return f"Error executing {action}: {e}"
    
    def _simulate_llm(self, question: str) -> str:
        """
        Simulate LLM reasoning. Replace with real API call in production.
        """
        q_lower = question.lower()
        step_count = len(self.steps)
        
        if step_count > 0:
            last_obs = self.steps[-1].observation or ""
            
            if any(keyword in last_obs.lower() for keyword in ["created", "released", "introduced", "°c"]):
                return f"I now have the information I need.\nFinal Answer: Based on my search, {last_obs}"
            
            if self.steps[-1].action == "calculator":
                return f"The calculation is complete.\nFinal Answer: The result is {last_obs}"
        
        if "weather" in q_lower:
            city = "london"
            for c in ["salford", "london", "new york", "tokyo"]:
                if c in q_lower:
                    city = c
                    break
            return f"I need to check the weather.\nAction: get_weather\nAction Input: {city}"
        
        if any(op in question for op in ["+", "-", "*", "/", "calculate", "compute"]):
            expr = re.sub(r"[^0-9+\-*/.()\s]", "", question).strip()
            if not expr:
                expr = "2 + 2"
            return f"I need to calculate this.\nAction: calculator\nAction Input: {expr}"
        
        if any(word in q_lower for word in ["who", "what", "when", "created", "invented", "is"]):
            search_terms = question.replace("?", "").strip()
            return f"I should search for information about this.\nAction: search\nAction Input: {search_terms}"
        
        return "I can answer this directly.\nFinal Answer: I don't have enough information to answer that question."
    
    def run(self, question: str) -> str:
        """Run the agent on a question."""
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print('='*60)
        
        self.steps = []
        
        for i in range(self.max_steps):
            response = self._simulate_llm(question)
            print(f"\nThought: {response.split('Action:')[0].strip()}")
            
            if "Final Answer:" in response:
                answer = response.split("Final Answer:")[-1].strip()
                print(f"\n✅ Final Answer: {answer}")
                return answer
            
            action_result = self._parse_action(response)
            if action_result:
                action, action_input = action_result
                print(f"Action: {action}")
                print(f"Action Input: {action_input}")
                
                observation = self._execute_tool(action, action_input)
                print(f"Observation: {observation}")
                
                self.steps.append(AgentStep(
                    thought=response.split("Action:")[0].strip(),
                    action=action,
                    action_input=action_input,
                    observation=observation
                ))
            else:
                print("⚠️ Could not parse action from response")
                break
        
        return "Max steps reached without finding answer."


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    agent = ReActAgent(TOOLS)
    
    questions = [
        "What's the weather in Salford?",
        "Calculate 15 * 8 + 42",
        "Who created Python?",
        "What is the Transformer architecture?",
    ]
    
    print("\n" + "="*60)
    print("🤖 ReAct Agent Demo")
    print("="*60)
    
    for q in questions:
        agent.run(q)
        print()
