# ReAct Agent Demo — Reasoning + Acting

> Pillar 3: Build Agents | Created: 2026-03-06

ReAct (Reasoning and Acting) is a prompting pattern that makes LLMs reason step-by-step while using tools. This demo shows the core pattern with working code.

## The ReAct Loop

```
Thought → Action → Observation → Thought → Action → Observation → ... → Answer
```

1. **Thought**: LLM reasons about what to do next
2. **Action**: LLM calls a tool with arguments
3. **Observation**: Tool returns a result
4. Loop until the LLM has enough info to answer

---

## Working Implementation

Save as `react_agent.py`:

```python
"""
ReAct Agent Demo
A minimal but complete implementation of the ReAct pattern.
"""

import re
import json
from dataclasses import dataclass
from typing import Callable

# ============================================================
# TOOLS - Functions the agent can call
# ============================================================

def calculator(expression: str) -> str:
    """Evaluate a math expression."""
    try:
        # Safe eval for basic math
        allowed = set('0123456789+-*/.() ')
        if not all(c in allowed for c in expression):
            return "Error: Only basic math operations allowed"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def search(query: str) -> str:
    """Simulate a search tool (in production, use real API)."""
    # Mock knowledge base
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


# Tool registry
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
    """
    A ReAct agent that reasons step-by-step and uses tools.
    
    In production, you'd call an LLM API. This demo uses a simple
    rule-based system to show the pattern clearly.
    """
    
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
        Simulate LLM reasoning. In production, call your LLM API here.
        
        This demo uses pattern matching to show the flow.
        Replace with: openai.chat.completions.create() or similar.
        """
        q_lower = question.lower()
        step_count = len(self.steps)
        
        # Check if we have enough info from previous observations
        if step_count > 0:
            last_obs = self.steps[-1].observation or ""
            
            # If last observation answered the question, conclude
            if any(keyword in last_obs.lower() for keyword in ["created", "released", "introduced", "°c"]):
                return f"I now have the information I need.\nFinal Answer: Based on my search, {last_obs}"
            
            # If it was a calculation, report the result
            if self.steps[-1].action == "calculator":
                return f"The calculation is complete.\nFinal Answer: The result is {last_obs}"
        
        # Decide what action to take
        if "weather" in q_lower:
            city = "london"  # Default
            for c in ["salford", "london", "new york", "tokyo"]:
                if c in q_lower:
                    city = c
                    break
            return f"I need to check the weather.\nAction: get_weather\nAction Input: {city}"
        
        if any(op in question for op in ["+", "-", "*", "/", "calculate", "compute"]):
            # Extract math expression
            expr = re.sub(r"[^0-9+\-*/.()\s]", "", question).strip()
            if not expr:
                expr = "2 + 2"  # Fallback
            return f"I need to calculate this.\nAction: calculator\nAction Input: {expr}"
        
        if any(word in q_lower for word in ["who", "what", "when", "created", "invented", "is"]):
            # Search query
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
            # Get LLM response (simulated)
            response = self._simulate_llm(question)
            print(f"\nThought: {response.split('Action:')[0].strip()}")
            
            # Check for final answer
            if "Final Answer:" in response:
                answer = response.split("Final Answer:")[-1].strip()
                print(f"\n✅ Final Answer: {answer}")
                return answer
            
            # Parse and execute action
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
                # No action found, something went wrong
                print("⚠️ Could not parse action from response")
                break
        
        return "Max steps reached without finding answer."


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    agent = ReActAgent(TOOLS)
    
    # Test questions
    questions = [
        "What's the weather in Salford?",
        "Calculate 15 * 8 + 42",
        "Who created Python?",
        "What is the Transformer architecture?",
    ]
    
    print("\n" + "="*60)
    print("ReAct Agent Demo")
    print("="*60)
    
    for q in questions:
        agent.run(q)
        print()
```

---

## Running the Demo

```bash
cd ~/clawd
python memory/react-agent-demo.py
```

Expected output:
```
============================================================
ReAct Agent Demo
============================================================

============================================================
Question: What's the weather in Salford?
============================================================

Thought: I need to check the weather.
Action: get_weather
Action Input: salford
Observation: Salford: 11°C, Light rain

Thought: I now have the information I need.
✅ Final Answer: Based on my search, Salford: 11°C, Light rain
```

---

## Key Concepts Demonstrated

### 1. Tool Registry
```python
TOOLS = {
    "calculator": {"func": calculator, "description": "..."},
    # Tools are just functions with descriptions
}
```

### 2. The ReAct Loop
```python
for i in range(max_steps):
    response = llm(prompt)        # Think
    action = parse(response)       # Decide
    observation = execute(action)  # Act
    if "Final Answer" in response:
        break                      # Done
```

### 3. Prompt Engineering
The prompt structure matters:
- List available tools with descriptions
- Show the Thought/Action/Observation format
- Include history of previous steps
- Ask for Final Answer when done

---

## Upgrading to Real LLM

Replace `_simulate_llm()` with actual API call:

```python
import openai

def _call_llm(self, question: str) -> str:
    prompt = self._build_prompt(question)
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=500
    )
    
    return response.choices[0].message.content
```

Or with Anthropic:
```python
import anthropic

def _call_llm(self, question: str) -> str:
    client = anthropic.Client()
    prompt = self._build_prompt(question)
    
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text
```

---

## Production Improvements

1. **Better parsing**: Use structured output (JSON mode) instead of regex
2. **Error handling**: Retry failed tool calls, handle rate limits
3. **Memory**: Add conversation history for multi-turn
4. **Streaming**: Stream thoughts for better UX
5. **Tool validation**: Validate inputs before execution
6. **Async**: Make tool calls async for parallel execution

---

## Next Steps

- **Add more tools**: Web search, file operations, code execution
- **Implement memory**: Short-term (conversation) + long-term (vector DB)
- **Multi-agent**: Orchestrate multiple specialized agents
- **Evaluation**: Build test cases to measure agent performance

*The pattern is simple. The magic is in the tools and prompts.* ✨
