# DeepSeek R1 - Research Summary

## What is DeepSeek R1?

DeepSeek R1 is an open-source reasoning model that achieves performance comparable to OpenAI's o1 on math, code, and reasoning tasks.

## Key Architecture

- **Base**: DeepSeek-V3 (MoE architecture)
- **Total Params**: 671B
- **Activated Params**: 37B
- **Context Length**: 128K tokens

## Two Variants

1. **DeepSeek-R1-Zero**: Trained via pure RL (no SFT). First open research to validate reasoning can emerge from RL alone.
2. **DeepSeek-R1**: Uses cold-start data before RL. Addresses issues in Zero (repetition, readability, language mixing).

## Key Innovations

1. **RL without SFT**: R1-Zero proves you can get reasoning capabilities through pure reinforcement learning
2. **Distillation**: Smaller models (7B-70B) distilled from R1 outperform reasoning from scratch
3. **Chain-of-Thought**: Native CoT generation with self-verification and reflection

## Benchmark Results

| Model | AIME 2024 | Math | Code |
|-------|-----------|------|------|
| OpenAI o1 | 79.2% | 96.4% | 63.4% |
| DeepSeek R1 | 79.8% | 97.3% | 65.9% |

## Distilled Models

- **DeepSeek-R1-Distill-Qwen-32B**: Outperforms OpenAI o1-mini
- Available: 1.5B, 7B, 8B, 14B, 32B, 70B (Qwen + Llama base)

## Why It Matters

1. **Open source**: First open-weight model competitive with o1
2. **Efficient**: 37B activated params vs full model
3. **Distillation proof**: Large model reasoning can transfer to smaller models

## For Learning

- Study the RL pipeline (GRPO algorithm)
- Look at how cold-start data improves readability
- Try running distilled 7B model locally

---

*Source: github.com/deepseek-ai/DeepSeek-R1, arxiv:2501.12948*
