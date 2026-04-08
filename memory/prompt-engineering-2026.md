# Prompt Engineering Best Practices 2026

## Core Principles

### 1. Be Specific & Clear
- Explicitly state what you want
- Include format requirements
- Define constraints clearly

### 2. Use Few-Shot Examples
- Google's whitepaper: "always include few-shot examples"
- Zero-shot is explicitly NOT preferred
- Place examples before your question

### 3. Put Questions at the End
- After your context/data
- Models focus more on what's at the end

### 4. Use System Prompts
- Set role and behavior
- Define output format
- Establish constraints

## Key Techniques

### Chain-of-Thought (CoT)
```
Let's think step by step.
```
- Encourages reasoning
- Better for complex tasks

### ReAct (Reason + Act)
Combine reasoning with tool use:
- Think about what to do
- Take action
- Observe result
- Repeat

### Persona Pattern
```
As an expert Python developer, review this code...
```
- Sets tone and expertise level
- Improves output quality

### Template Pattern
```
Context: {context}
Task: {task}
Format: {format}
```
- Consistent, reproducible prompts

## Security Note

**Prompt injection is real:**
- Reframing questions can bypass guardrails
- Adversarial prompts exploit LLM alignment
- Always validate user inputs

## Model-Specific

Different models respond to different formats:
- Claude: Likes clear headers, bullet points
- GPT: Works well with system prompts
- Gemini: Benefits from structured context

## Best Practice Summary

| Technique | Use When |
|-----------|----------|
| Few-shot | Complex tasks, specific formats |
| CoT | Math, reasoning, multi-step |
| ReAct | Tool use, agents |
| Persona | Tone-specific outputs |
| Constraints | Avoiding unwanted content |

## Resources
- promptingguide.ai
- Lakera blog (security)
