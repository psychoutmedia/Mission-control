# Fine-Tuning vs RAG vs Prompt Engineering

## Overview

Three ways to customize LLM behavior:

| Approach | What | Cost | Time | Use Case |
|----------|------|------|------|----------|
| **Prompt Engineering** | Optimize inputs | Free | Hours | Quick wins |
| **RAG** | Add context from documents | $70-1000/mo | Days | Real-time data |
| **Fine-tuning** | Retrain on custom data | High (6x inference) | Months | Deep specialization |

## Prompt Engineering

**What**: Optimize input prompts to get better outputs.

**Pros:**
- Free (no extra cost)
- Fast (hours to days)
- No technical setup
- Reversible changes

**Cons:**
- Limited by model's knowledge
- Token limits
- Can't add new knowledge

**Best for:**
- Toning outputs
- Format control
- Quick experiments

## RAG (Retrieval Augmented Generation)

**What**: Fetch relevant docs → add to prompt → generate

**Pros:**
- Access to current data
- Source citations
- Smaller models work well
- No retraining

**Cons:**
- Extra infrastructure
- Latency from retrieval
- Context window limits

**Best for:**
- Q&A on private docs
- Up-to-date information
- Knowledge cutoff issues

## Fine-Tuning

**What**: Train on custom dataset to modify behavior.

**Pros:**
- Consistent output style
- Learns new patterns
- Works without context

**Cons:**
- Expensive (compute + 6x inference)
- Takes months
- Can forget old knowledge
- Requires data expertise

**Best for:**
- Specific output formats
- Domain expertise (medical, legal)
- When RAG not enough

## Decision Guide

```
Start with prompt engineering
    ↓
If need real-time data → RAG
    ↓
If need deep specialization → Fine-tune
```

**Rule of thumb:**
1. **Hours/days**: Prompt engineering
2. **Real-time data**: RAG
3. **Months + deep specialization**: Fine-tuning

## Combination Approaches

Common in production:
- RAG + Prompt Engineering: Context + format control
- Fine-tuning + RAG: Base model + current data
- All three: Maximum customization

## Cost Comparison

| Approach | Setup Cost | Inference Cost |
|----------|-----------|----------------|
| Prompt Eng | $0 | Base |
| RAG | $100-500 | +10-20% |
| Fine-tuning | $10K+ | 6x base |

## For Learning

**Start with:**
1. Prompt engineering (free, quick)
2. RAG with Ollama (local, private)
3. Fine-tuning later (when needed)

This builds skills in:
- Prompt design
- Vector databases
- Model training
