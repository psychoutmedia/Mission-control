# Tool-Calling Agent

A modern implementation of tool-calling agents using JSON Schema function definitions, mirroring how OpenAI, Anthropic, and other LLM APIs handle function calls.

## Overview

This agent demonstrates the tool-calling pattern used in production LLM systems:
1. Define tools with JSON Schema
2. LLM decides when to call tools
3. Execute tool and return results
4. LLM provides final answer

## Running

```bash
python agent.py
```

## Architecture

- **Function Definitions**: JSON Schema describing each tool's parameters
- **Tool Registry**: Maps tool names to implementations
- **Agent Loop**: Handles the LLM → tool call → result → LLM cycle

## Extending

Add new tools by:
1. Defining the function in `FUNCTION_DEFINITIONS`
2. Implementing the function
3. Registering with `registry.register()`
