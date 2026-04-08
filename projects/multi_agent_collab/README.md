# Multi-Agent Collaboration Demo

Two agents working together: Researcher + Writer.

## Collaboration Patterns

### Sequential
Agent A → Agent B → Agent C
- Simple, clear pipeline
- Output of one feeds next

### Parallel
Agent A + Agent B (simultaneous)
- Faster for independent tasks
- Requires aggregation

### Hierarchical
Orchestrator manages sub-agents
- Used in Claude Code, AutoGen, CrewAI

## Running

```bash
python agent.py
```

## Architecture

- **Agent**: Base class with messaging
- **ResearcherAgent**: Finds and analyzes info
- **WriterAgent**: Creates content from research
- **Orchestrator**: Coordinates workflow

## Extension Ideas

- Add real LLM calls to agents
- Implement message passing
- Add agent specialization (coder, reviewer)
- Build team of specialized agents
