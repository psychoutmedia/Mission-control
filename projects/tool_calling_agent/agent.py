"""
Tool-Calling Agent
A modern implementation using function calling patterns (OpenAI/Anthropic style).

Run with: python projects/tool_calling_agent/agent.py
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable


# ============================================================
# FUNCTION DEFINITIONS - JSON Schema for tool descriptions
# ============================================================

FUNCTION_DEFINITIONS = [
    {
        "name": "calculator",
        "description": "Evaluate a mathematical expression and return the result.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16) * 3')."
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "search",
        "description": "Search for information in the knowledge base.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get current weather information for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name (e.g., 'London', 'New York')."
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "get_forecast",
        "description": "Get weather forecast for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name."
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days to forecast (1-7).",
                    "default": 3
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "send_email",
        "description": "Send an email to a recipient.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address."
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line."
                },
                "body": {
                    "type": "string",
                    "description": "Email body content."
                }
            },
            "required": ["to", "subject", "body"]
        }
    }
]


# ============================================================
# TOOL IMPLEMENTATIONS
# ============================================================

class ToolRegistry:
    """Registry of available tools and their implementations."""
    
    def __init__(self):
        self.tools: dict[str, Callable] = {}
        self.definitions: list[dict] = []
    
    def register(self, definition: dict, func: Callable):
        """Register a tool with its definition and implementation."""
        self.tools[definition["name"]] = func
        self.definitions.append(definition)
    
    def get_tool(self, name: str) -> Callable | None:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def get_definitions(self) -> list[dict]:
        """Get all tool definitions (for LLM context)."""
        return self.definitions


# Initialize registry and register tools
registry = ToolRegistry()


def calculator(expression: str) -> str:
    """Evaluate a math expression."""
    import math
    try:
        # Security: only allow safe characters
        allowed = set('0123456789+-*/.() sqrtpi sin cos tan log exp pow')
        if not all(c.isalnum() or c in '+-*/.() ' for c in expression):
            return json.dumps({"error": "Invalid characters in expression"})
        
        # Safe eval with math functions
        safe_dict = {k: v for k, v in math.__dict__.items() if not k.startswith('_')}
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return json.dumps({"result": result, "expression": expression})
    except Exception as e:
        return json.dumps({"error": str(e)})


def search(query: str) -> str:
    """Search knowledge base."""
    knowledge = {
        "python": "Python is a high-level programming language created by Guido van Rossum in 1991.",
        "pytorch": "PyTorch is an open-source machine learning framework by Meta AI, released in 2016.",
        "transformer": "The Transformer architecture was introduced in 'Attention Is All You Need' (Vaswani et al., 2017).",
        "gpt": "GPT (Generative Pre-trained Transformer) is OpenAI's language model architecture.",
        "claude": "Claude is Anthropic's AI assistant focused on helpfulness and safety.",
        "llm": "LLM = Large Language Model. A neural network trained on massive text data.",
        "attention": "Attention mechanisms let models weigh the relevance of different input parts.",
        "rag": "RAG (Retrieval Augmented Generation) combines retrieval with generation for better answers.",
        "agent": "An AI agent can reason, plan, and use tools to accomplish tasks autonomously.",
        "automa dynamics": "Automa Dynamics is a robotics company building humanoid robots (Helios-1).",
    }
    
    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower:
            return json.dumps({"result": value, "query": query})
    return json.dumps({"result": f"No information found for: {query}", "query": query})


def get_weather(city: str) -> str:
    """Get weather for a city (mock)."""
    weather_data = {
        "london": {"temp": 12, "condition": "Cloudy", "humidity": 65},
        "new york": {"temp": 8, "condition": "Sunny", "humidity": 45},
        "tokyo": {"temp": 18, "condition": "Clear", "humidity": 55},
        "salford": {"temp": 11, "condition": "Light rain", "humidity": 80},
    }
    
    city_lower = city.lower()
    if city_lower in weather_data:
        data = weather_data[city_lower]
        return json.dumps({"city": city, **data})
    return json.dumps({"error": f"Weather data not available for {city}"})


def get_forecast(city: str, days: int = 3) -> str:
    """Get forecast (mock)."""
    base = get_weather(city)
    base_data = json.loads(base)
    
    if "error" in base_data:
        return base
    
    forecasts = []
    conditions = ["Sunny", "Cloudy", "Rainy", "Clear", "Partly cloudy"]
    for i in range(1, days + 1):
        forecasts.append({
            "day": i,
            "temp": base_data["temp"] + (i * 2),
            "condition": conditions[i % len(conditions)]
        })
    
    return json.dumps({"city": city, "forecast": forecasts})


def send_email(to: str, subject: str, body: str) -> str:
    """Send email (mock - would integrate with SMTP in production)."""
    # In production, integrate with email service
    return json.dumps({
        "status": "sent",
        "to": to,
        "subject": subject,
        "preview": body[:50] + "..." if len(body) > 50 else body
    })


# Register all tools
for defn in FUNCTION_DEFINITIONS:
    func_name = defn["name"]
    if func_name == "calculator":
        registry.register(defn, calculator)
    elif func_name == "search":
        registry.register(defn, search)
    elif func_name == "get_weather":
        registry.register(defn, get_weather)
    elif func_name == "get_forecast":
        registry.register(defn, get_forecast)
    elif func_name == "send_email":
        registry.register(defn, send_email)


# ============================================================
# TOOL-CALLING AGENT
# ============================================================

@dataclass
class ToolCall:
    """Represents a tool call request."""
    name: str
    arguments: dict


@dataclass
class Message:
    """Chat message."""
    role: str
    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None


class ToolCallingAgent:
    """
    A modern tool-calling agent using function calling patterns.
    
    This mirrors how OpenAI, Anthropic, and other LLM APIs handle
    tool calls - the LLM returns structured tool call requests
    that the application executes.
    """
    
    def __init__(self, registry: ToolRegistry, max_iterations: int = 5):
        self.registry = registry
        self.max_iterations = max_iterations
        self.messages: list[Message] = []
    
    def _get_system_prompt(self) -> str:
        """Build the system prompt with tool definitions."""
        tools_json = json.dumps(self.registry.get_definitions(), indent=2)
        return f"""You are a helpful AI assistant with access to tools.

Available tools (JSON Schema):
{tools_json}

Instructions:
- Use tools when you need real-time information or to perform actions
- If a user asks about something you have knowledge of, you can answer directly
- If you need to use a tool, respond with a tool call in this format:
  {{"name": "tool_name", "arguments": {{"param1": "value1"}}}}
- After receiving tool results, provide your final answer
- Always respond in valid JSON when making tool calls"""
    
    def _simulate_llm(self, user_message: str) -> Message | None:
        """
        Simulate LLM tool-calling. Replace with real API call.
        
        In production, this would call OpenAI/Anthropic API with:
        - messages including conversation history
        - tools=function_definitions
        - The API returns tool_call objects when the model wants to use tools
        """
        # Check if this is a follow-up (we have tool results)
        if self.messages and any(m.tool_call_id for m in self.messages):
            # LLM provides final answer after tool results
            last_msg = self.messages[-1]
            if "error" in last_msg.content.lower():
                return Message(
                    role="assistant",
                    content="I encountered an error. Let me try a different approach."
                )
            return Message(
                role="assistant", 
                content=f"I've gathered the information: {last_msg.content}"
            )
        
        # First turn - decide whether to use tools
        user_lower = user_message.lower()
        
        # Weather queries
        if "weather" in user_lower or "forecast" in user_lower:
            city = "London"  # Default
            for c in ["salford", "london", "new york", "tokyo", "paris", "berlin"]:
                if c in user_lower:
                    city = c.title()
                    break
            
            if "forecast" in user_lower or "days" in user_lower:
                days = 3
                days_match = re.search(r"(\d+)\s*days?", user_lower)
                if days_match:
                    days = int(days_match.group(1))
                return Message(
                    role="assistant",
                    content="",
                    tool_calls=[ToolCall(name="get_forecast", arguments={"city": city, "days": days})]
                )
            return Message(
                role="assistant",
                content="",
                tool_calls=[ToolCall(name="get_weather", arguments={"city": city})]
            )
        
        # Math queries
        if any(op in user_message for op in ["+", "-", "*", "/", "calculate", "compute", "="]):
            expr = re.sub(r"[^0-9+\-*/.()\s]", "", user_message).strip()
            if expr:
                return Message(
                    role="assistant",
                    content="",
                    tool_calls=[ToolCall(name="calculator", arguments={"expression": expr})]
                )
        
        # Search queries
        if any(w in user_lower for w in ["what is", "who is", "tell me about", "explain", "define"]):
            query = user_message.replace("?", "").strip()
            return Message(
                role="assistant",
                    content="",
                    tool_calls=[ToolCall(name="search", arguments={"query": query})]
                )
        
        # Email
        if "email" in user_lower or "send" in user_lower:
            # Extract email components (simplified)
            return Message(
                role="assistant",
                content="",
                tool_calls=[ToolCall(
                    name="send_email",
                    arguments={"to": "example@test.com", "subject": "Subject", "body": "Body"}
                )]
            )
        
        # Direct answer
        return Message(
            role="assistant",
            content="I'm here to help! I can answer questions, check weather, do calculations, search knowledge, or send emails. What would you like me to do?"
        )
    
    def _execute_tool_call(self, tool_call: ToolCall) -> str:
        """Execute a tool call and return the result."""
        tool = self.registry.get_tool(tool_call.name)
        if not tool:
            return json.dumps({"error": f"Unknown tool: {tool_call.name}"})
        
        try:
            # Get the function and inspect its signature
            import inspect
            sig = inspect.signature(tool)
            required_params = [
                p.name for p in sig.parameters.values() 
                if p.default == inspect.Parameter.empty and p.name != 'self'
            ]
            
            # Filter arguments to only include required ones
            filtered_args = {
                k: v for k, v in tool_call.arguments.items()
                if k in sig.parameters
            }
            
            result = tool(**filtered_args)
            return result
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def run(self, user_input: str) -> str:
        """Run the agent on user input."""
        print(f"\n{'='*60}")
        print(f"User: {user_input}")
        print('='*60)
        
        # Add user message
        self.messages.append(Message(role="user", content=user_input))
        
        for iteration in range(self.max_iterations):
            # Get LLM response
            response = self._simulate_llm(user_input)
            
            if not response:
                return "Failed to get response from LLM"
            
            # Check for tool calls
            if response.tool_calls:
                print(f"\n🔧 Tool Calls:")
                for tc in response.tool_calls:
                    print(f"  - {tc.name}: {tc.arguments}")
                    
                    # Execute tool
                    result = self._execute_tool_call(tc)
                    print(f"  → Result: {result}")
                    
                    # Add tool result to messages
                    self.messages.append(Message(
                        role="tool",
                        content=result,
                        tool_call_id=tc.name
                    ))
                
                # Continue loop to let LLM process results
                continue
            
            # No tool calls - final answer
            print(f"\n🤖 Assistant: {response.content}")
            self.messages.append(response)
            return response.content
        
        return "Max iterations reached"


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    agent = ToolCallingAgent(registry)
    
    questions = [
        "What's the weather in Salford?",
        "What's the weather forecast for London for 5 days?",
        "Calculate (15 * 8) + 42",
        "What is Python?",
        "Tell me about transformers in AI",
    ]
    
    print("\n" + "="*60)
    print("🔧 Tool-Calling Agent Demo")
    print("="*60)
    
    for q in questions:
        result = agent.run(q)
        print(f"\n✅ Final Answer: {result}\n")
        print("-" * 40)
