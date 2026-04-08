# LLM Guardrails

## What are Guardrails?

Safety mechanisms that prevent harmful outputs.

## Types

### 1. Input Guardrails
- Sanitize user input
- Block prompt injection
- Validate formats

### 2. Output Guardrails
- Filter sensitive content
- Check for hallucinations
- Validate responses

## Tools

| Tool | Purpose |
|------|---------|
| Nvidia Nemo | Enterprise guardrails |
| Guardrails AI | Open-source |
| AWS Bedrock | Built-in safety |
| Anthropic | Constitutional AI |

## Implementation

```python
def guardrail(output):
    blocked = ["harmful", "illegal"]
    for word in blocked:
        if word in output.lower():
            return "I can't help with that."
    return output
```

## Best Practices

1. Layer multiple guardrails
2. Log all blocks
3. Test regularly
4. Balance safety vs utility
