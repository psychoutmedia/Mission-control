# Planning Agent

An agent that plans before acting - key to building capable AI agents.

## Key Concept

**Planning beats reacting**: Agents with explicit plans outperform reactive agents.

## The Cycle

1. **Think** - Analyze situation
2. **Plan** - Create explicit steps
3. **Act** - Execute one step
4. **Reflect** - Evaluate result, update plan

## Running

```bash
python agent.py
```

## Architecture

- **PlanStep**: Individual action in a plan
- **Thought**: Agent's mental state at any point
- **PlanningAgent**: Manages think→plan→act→reflect cycle

## Extension Ideas

- LLM-generated plans (instead of rule-based)
- Plan revision when steps fail
- Sub-agent delegation for complex steps
- Plan learning from past executions
