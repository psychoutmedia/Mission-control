# LLM Function Calling Patterns

## What is Function Calling?

LLMs that can call external functions/tools:
- Returns structured data
- Enables API integration
- Actions beyond text generation

## Providers

| Provider | Name | Status |
|----------|------|--------|
| OpenAI | function_call | ✅ |
| Anthropic | tool_use | ✅ |
| Gemini | function Calling | ✅ |
| Ollama | tools | ✅ |

## How It Works

1. **Define functions** with JSON Schema
2. **Send to LLM** with function definitions
3. **LLM decides** when to call function
4. **Execute function** and return result
5. **LLM synthesizes** final response

## Example (OpenAI)

```python
functions = [{
    "name": "get_weather",
    "description": "Get weather",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"]
    }
}]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Weather in London?"}],
    tools=[{"type": "function", "function": functions[0]}]
)
# Returns: {"name": "get_weather", "arguments": {"city": "London"}}
```

## Use Cases

- API integration
- Database queries
- Code execution
- Real-time data

## Best Practices

1. Keep functions focused
2. Clear descriptions
3. Handle errors gracefully
4. Validate outputs
