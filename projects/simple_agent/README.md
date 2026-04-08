# Simple Agent Framework

A lightweight ReAct-style (Reason + Act) agent implementation in Python with tool use capabilities.

## Features

- **Tool Registration**: Easily add/remove tools the agent can use
- **ReAct Loop**: Implements the Thought → Action → Observation loop
- **Streaming**: Ready for streaming token generation
- **Extensible**: Add custom tools with simple function decorators

## Quick Start

```python
from agent import SimpleAgent, Tool

# Define a custom tool
def calculator(expression: str) -> float:
    """Evaluate a mathematical expression"""
    return eval(expression)

# Create agent
agent = SimpleAgent(tools=[
    Tool("calculator", "Evaluate math", calculator, {"expression": ""}),
])

# Run
result = agent.run("What's 15 * 23 + 7?")
print(result)
```

## Architecture

```
┌─────────────────────────────────────────┐
│            SimpleAgent                   │
├─────────────────────────────────────────┤
│ 1. Receive prompt                        │
│ 2. THINK: Analyze what tools needed     │
│ 3. ACT: Call tool with arguments        │
│ 4. OBSERVE: Get tool result             │
│ 5. REASON: Incorporate observation      │
│ 6. Repeat until done                    │
│ 7. RETURN: Final answer                  │
└─────────────────────────────────────────┘
```

## Included Tools

- `calculator`: Evaluate mathematical expressions
- `search`: Web search (placeholder)
- `python_repl`: Execute Python code

## Tool Format

```python
Tool(
    name="my_tool",
    description="What it does",
    func=my_function,
    parameters={"arg1": "", "arg2": ""}
)
```

## License

MIT
