# LLM Context Window Strategies

## The Problem

LLMs have fixed context windows (8K-128K tokens). Long conversations exceed this. Need strategies to manage.

## Strategies

### 1. Sliding Window
```
[---oldest---][---recent---]
     ↓ drop
[---recent---][---new----]
```
- Keep most recent messages
- Simple, loses older context
- Good for: Short conversations

### 2. Summarization
```
[summary of old][recent messages]
```
- Compress old messages into summary
- Use LLM to create summary
- Preserves key info
- Good for: Long conversations

### 3. Vector Retrieval
```
[recent] + [semantically relevant from vector DB]
```
- Store history in vector DB
- Retrieve relevant past context
- Best of both worlds
- Good for: Knowledge-intensive tasks

### 4. Importance Filtering
```
Keep: System prompt, recent, key facts
Drop: Redundant, old low-value
```
- Selective retention
- Requires importance scoring
- Good for: Multi-topic chats

### 5. Hierarchical Summarization
```
Turn 1-10: Summary A
Turn 11-20: Summary B
Turn 21-30: [messages]
```
- Multiple levels of summary
- Recursive compression
- Good for: Very long sessions

## Implementation Approaches

| Strategy | Complexity | Preserves | Loses |
|----------|-----------|-----------|-------|
| Sliding | Low | Recent | Old |
| Summarization | Medium | Key points | Details |
| Vector Retrieval | High | Relevant | Some context |
| Importance | Medium | High-value | Noise |

## Best Practice

1. **Start simple**: Sliding window
2. **Add complexity**: When needed
3. **Combine**: Summarization + retrieval
4. **Monitor**: Track context usage

## For Agents

In agent systems:
- Clear old tool results first
- Keep system prompt intact
- Prioritize recent reasoning
- Use external memory (vector DB)

## Tools

- LangChain: ConversationBufferWindowMemory
- LlamaIndex: Memory module
- Custom: Vector store + retrieval
