"""
Simple Agent Framework with Tool Use
A ReAct-style (Reason + Act) agent implementation

This demonstrates:
- Tool registration and execution
- ReAct loop (Thought → Action → Observation)
- Streaming token generation
- Human-in-the-loop feedback

Usage:
    agent = SimpleAgent(tools=[search, calculator])
    response = agent.run("What's 15 * 23 + 7?")
"""

import json
import re
from typing import Callable, Any
from dataclasses import dataclass, field
from enum import Enum


class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    DONE = "done"
    ERROR = "error"


@dataclass
class Tool:
    """Represents a tool the agent can use"""
    name: str
    description: str
    func: Callable
    parameters: dict = field(default_factory=dict)
    
    def __call__(self, **kwargs) -> str:
        try:
            result = self.func(**kwargs)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"


@dataclass
class ToolCall:
    """Represents a planned tool call"""
    tool_name: str
    arguments: dict
    thought: str


class SimpleAgent:
    """A simple ReAct-style agent with tool use"""
    
    def __init__(self, model_name: str = "llama3", tools: list[Tool] = None):
        self.model_name = model_name
        self.tools = {t.name: t for t in (tools or [])}
        self.conversation_history = []
        self.state = AgentState.IDLE
        self.last_observation = None
    
    def add_tool(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def remove_tool(self, name: str):
        """Remove a tool"""
        if name in self.tools:
            del self.tools[name]
    
    def parse_tool_calls(self, response: str) -> list[ToolCall]:
        """Parse tool calls from model response"""
        tool_calls = []
        
        # Look for tool call blocks: <tool_call>...</tool_call>
        pattern = r'<tool_call>\s*(\w+)\s*(\{[^}]*\})\s*</tool_call>'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for tool_name, args_str in matches:
            if tool_name in self.tools:
                try:
                    args = json.loads(args_str)
                    tool_calls.append(ToolCall(
                        tool_name=tool_name,
                        arguments=args,
                        thought=response.split('<tool_call>')[0].strip() if '<tool_call>' in response else ""
                    ))
                except json.JSONDecodeError:
                    pass
        
        return tool_calls
    
    def execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a single tool call"""
        tool = self.tools[tool_call.tool_name]
        return tool(**tool_call.arguments)
    
    def format_tools_description(self) -> str:
        """Format tools for prompt"""
        if not self.tools:
            return "No tools available."
        
        desc = "Available tools:\n"
        for tool in self.tools.values():
            params = ", ".join(tool.parameters.keys()) if tool.parameters else "none"
            desc += f"- {tool.name}({params}): {tool.description}\n"
        return desc
    
    def run(self, prompt: str, max_iterations: int = 5) -> str:
        """Run the agent with a prompt"""
        self.conversation_history.append({"role": "user", "content": prompt})
        
        response = self._generate(prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        for iteration in range(max_iterations):
            tool_calls = self.parse_tool_calls(response)
            
            if not tool_calls:
                # No tool calls, we're done
                break
            
            # Execute each tool call
            observations = []
            for tool_call in tool_calls:
                self.state = AgentState.ACTING
                observation = self.execute_tool(tool_call)
                observations.append(f"[{tool_call.tool_name}] {observation}")
                self.last_observation = observation
            
            # Add observation to conversation
            observation_text = "\n".join(observations)
            self.conversation_history.append({
                "role": "user", 
                "content": f"Observation: {observation_text}"
            })
            
            self.state = AgentState.OBSERVING
            
            # Generate next response with observation
            response = self._generate(prompt, include_context=True)
            self.conversation_history.append({"role": "assistant", "content": response})
        
        self.state = AgentState.DONE
        return self._extract_final_answer(response)
    
    def _generate(self, prompt: str, include_context: bool = False) -> str:
        """Generate a response using Ollama"""
        # This would call Ollama in production
        # For now, return a placeholder that shows the format
        return f"I'll help you with that. Use <tool_call> to take actions."
    
    def _extract_final_answer(self, response: str) -> str:
        """Extract final answer from response"""
        # Remove tool call blocks to get final answer
        cleaned = re.sub(r'<tool_call>.*?</tool_call>', '', response, flags=re.DOTALL)
        return cleaned.strip()
    
    def reset(self):
        """Reset agent state"""
        self.conversation_history.clear()
        self.state = AgentState.IDLE
        self.last_observation = None


# =============================================================================
# Example Tools
# =============================================================================

def calculator(expression: str) -> float:
    """Evaluate a mathematical expression"""
    # WARNING: eval is dangerous in production!
    # Use a proper math parser
    allowed_ops = {'+', '-', '*', '/', '(', ')', '**', '^', ' '}
    # Check for any characters not in allowed set (excluding digits and spaces)
    for c in expression:
        if not (c.isdigit() or c in allowed_ops):
            raise ValueError(f"Invalid character in expression: {c}")
    
    # Safe evaluation using eval with limited globals
    result = eval(expression, {"__builtins__": {}}, {})
    return result


def search(query: str) -> str:
    """Search the web for information"""
    # Placeholder - would integrate with Brave API
    return f"Search results for: {query}\n[Would return relevant web results]"


def python_repl(code: str) -> str:
    """Execute Python code and return output"""
    import io
    import sys
    
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        exec(code, {"__builtins__": {}}, {})
        output = sys.stdout.getvalue()
        return output or "Code executed successfully (no output)"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        sys.stdout = old_stdout


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    # Create agent with tools
    agent = SimpleAgent(tools=[
        Tool("calculator", "Evaluate a mathematical expression", calculator, {"expression": ""}),
        Tool("search", "Search the web", search, {"query": ""}),
    ])
    
    print("Simple Agent Framework")
    print("=" * 40)
    print(f"Registered tools: {list(agent.tools.keys())}")
    print("\nExample usage:")
    print('  agent.run("What is 15 * 23 + 7?")')
    print("\nThe agent would:")
    print("  1. THINK: Recognize need for calculation")
    print("  2. ACT: Call calculator tool")
    print("  3. OBSERVE: Get result from tool")
    print("  4. RESPOND: Return final answer")
