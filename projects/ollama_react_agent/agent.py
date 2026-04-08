"""
ReAct Agent using Ollama
A reasoning + acting agent powered by local LLM.

This combines:
- Ollama (local LLM)
- ReAct pattern (Reason + Act)
- Tool use

Run with: python ollama_react_agent/agent.py
"""

import json
import re
import sys
import os

# Add parent to path
sys.path.insert(0, '/Users/marksstephenson/clawd/projects/ollama_extensions')
from client import OllamaClient


# ============================================================
# TOOLS
# ============================================================

def calculator(expression: str) -> str:
    """Evaluate a math expression."""
    try:
        import math
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
        "llm": "Large Language Model - neural network trained on text.",
        "automa dynamics": "Automa Dynamics is building Helios-1 humanoid robot.",
        "helios": "Helios-1 is a 5'10\" humanoid robot with 50kg payload.",
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
# REACT AGENT WITH OLLAMA
# ============================================================

class OllamaReActAgent:
    """
    ReAct agent powered by Ollama.
    
    Cycle:
    1. Think - reason about what to do
    2. Act - call a tool
    3. Observe - get result
    4. Repeat until done
    """
    
    def __init__(self, model: str = "phi3", client: OllamaClient = None):
        self.model = model
        self.client = client or OllamaClient()
        self.tools = TOOLS
        self.max_steps = 5
        
    def _build_system_prompt(self) -> str:
        """Build the system prompt with tool definitions."""
        tool_desc = "\n".join(
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        )
        return f"""You are a helpful AI assistant that uses tools to answer questions.

Available tools:
{tool_desc}

Instructions:
- Think step by step about what to do
- Use tools when you need real information
- After each tool use, explain what you observed
- When you have the answer, provide it clearly

Format your response like this:
Thought: [your reasoning]
Action: [tool_name]
Action Input: [input for tool]

After getting the result:
Thought: [analyze the result]
Action: [next tool or final answer]
...
Final Answer: [your final answer]"""

    def _parse_response(self, response: str) -> tuple[str, str, str]:
        """Parse LLM response for thought, action, and input."""
        # Extract thought
        thought_match = re.search(r"Thought:\s*(.+?)(?:Action:|$)", response, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else ""
        
        # Extract action
        action_match = re.search(r"Action:\s*(\w+)", response)
        action = action_match.group(1).strip() if action_match else ""
        
        # Extract action input
        input_match = re.search(r"Action Input:\s*(.+?)(?:Final Answer:|$)", response, re.DOTALL)
        action_input = input_match.group(1).strip() if input_match else ""
        
        # Check for final answer
        final_match = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
        final = final_match.group(1).strip() if final_match else None
        
        return thought, action, action_input, final
    
    def _execute_tool(self, action: str, action_input: str) -> str:
        """Execute a tool and return result."""
        if action not in self.tools:
            return f"Error: Unknown tool '{action}'"
        
        try:
            func = self.tools[action]["func"]
            result = func(action_input)
            return result
        except Exception as e:
            return f"Error: {e}"
    
    def run(self, question: str) -> str:
        """Run the agent on a question."""
        print(f"\n{'='*60}")
        print(f"❓ Question: {question}")
        print('='*60)
        print(f"🤖 Model: {self.model}")
        
        # Build messages
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": f"Question: {question}\n\nThink step by step and use tools if needed."}
        ]
        
        context = ""
        
        for step in range(self.max_steps):
            print(f"\n📍 Step {step + 1}")
            
            # Get LLM response
            try:
                response = self.client.chat(self.model, messages, stream=False)
                response_text = response.get("message", {}).get("content", "")
            except Exception as e:
                print(f"   ❌ Error calling Ollama: {e}")
                break
            
            # Parse response
            thought, action, action_input, final = self._parse_response(response_text)
            
            print(f"   💭 Thought: {thought[:80]}...")
            
            if final:
                print(f"\n✅ Final Answer: {final}")
                return final
            
            if action and action != "none":
                print(f"   🔧 Action: {action}")
                print(f"   📥 Input: {action_input[:50]}...")
                
                # Execute tool
                result = self._execute_tool(action, action_input)
                print(f"   📤 Result: {result[:80]}...")
                
                # Add to context
                context += f"\nObservation: {result}"
                
                # Add to messages
                messages.append({"role": "assistant", "content": response_text})
                messages.append({
                    "role": "user", 
                    "content": f"Observation: {result}\n\nWhat's your next thought?"
                })
            else:
                # No action specified, provide answer based on reasoning
                if thought:
                    print(f"\n✅ Answer: {thought}")
                    return thought
                break
        
        return "Max steps reached without final answer."


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    agent = OllamaReActAgent(model="phi3")
    
    # Check if Ollama is available
    if not agent.client.is_available():
        print("❌ Ollama is not running. Start it with: ollama serve")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🧠 ReAct Agent with Ollama")
    print("="*60)
    
    questions = [
        "What's the weather in London?",
        "What is Python?",
    ]
    
    for q in questions:
        result = agent.run(q)
        print(f"\n{'='*60}")
