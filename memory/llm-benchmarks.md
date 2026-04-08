# LLM Evaluation Benchmarks

## What Are Benchmarks?

Standardized tests to measure LLM capabilities across different dimensions.

## Major Benchmarks

### 1. MMLU (Massive Multitask Language Understanding)
- **What**: 57 subjects, multiple choice
- **Measures**: General knowledge + problem solving
- **Score**: % correct
- **SOTA**: ~90% (GPT-4, Claude)

### 2. HumanEval
- **What**: Python coding challenges
- **Measures**: Code generation ability
- **Score**: Pass@K (usually Pass@1)
- **SOTA**: ~95% (latest models)

### 3. GPQA (Graduate-Level Science)
- **What**: Graduate-level science questions
- **Measures**: Expert-level reasoning
- **Score**: % correct

### 4. ARC (Abstraction and Reasoning Corpus)
- **What**: Visual reasoning puzzles
- **Measures**: Abstract reasoning
- **Score**: % correct

### 5. BIG-Bench
- **What**: 200+ diverse tasks
- **Measures**: General capability
- **Score**: Various

### 6. MATH
- **What**: Competition math problems
- **Measures**: Mathematical reasoning
- **Score**: % correct

## Categories

| Category | Benchmarks |
|----------|------------|
| Knowledge | MMLU, TriviaQA |
| Reasoning | ARC, BIG-Bench |
| Coding | HumanEval, MBPP |
| Math | MATH, GSM8K |
| Safety | BBQ, TruthfulQA |

## For LLM Engineering

**When building agents:**
- Use HumanEval for code tasks
- Test reasoning with MATH/ARC
- Evaluate with MMLU for general knowledge

**Key insight:** Benchmarks inform:
- Model selection
- Prompt optimization
- Fine-tuning targets

## Current Leaders (2026)

- GPT-4 series: ~90% MMLU
- Claude 4: ~88% MMLU
- Gemini Ultra: ~86% MMLU

## Resources
- Vellum leaderboard
- llm-stats.com
- OpenRouter
