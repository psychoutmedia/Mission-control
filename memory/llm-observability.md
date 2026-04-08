# LLM Observability & Monitoring

## Why Observability?

LLMs are non-deterministic. Need to track:
- What's happening inside?
- Why did it produce that output?
- When things go wrong?

## Key Metrics

### Input/Output
- Request volume
- Token usage (prompt/completion)
- Latency (first token, total)
- Error rates

### Quality
- Accuracy scores
- Task completion rate
- User satisfaction

### Cost
- Per-request cost
- Daily/monthly spend
- Token burn rate

## Tools

| Tool | Purpose |
|------|---------|
| LangSmith | Full-stack LLM observability |
| LangFuse | Open-source alternative |
| Arize AI | ML model monitoring |
| Helicone | OpenAI proxy with logging |
| PromptLayer | Prompt management |

## Implementation

```python
# Simple logging
def log_request(prompt, response, latency):
    logger.info({
        "prompt": prompt[:100],
        "response": response[:100],
        "latency": latency,
        "tokens": count_tokens(response)
    })
```

## For Agents

Track:
- Tool usage frequency
- Tool success rates
- Reasoning steps
- Error patterns

## Key Insight

**Observability = Debugging + Optimization + Compliance**

Build it in from day one.
