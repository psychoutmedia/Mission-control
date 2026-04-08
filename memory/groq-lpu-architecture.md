# Groq LPU Architecture Research

## What is an LPU?

**LPU (Language Processing Unit)** = Groq's custom silicon for LLM inference.

## Key Architecture Features

### Tensor Streaming Processor (TSP)
- Different from GPU SIMD/MIMD - single-instruction thread streaming
- Static scheduling = deterministic latency
- No out-of-order execution - compiler handles everything

### Groq 3 (Announced GTC 2026)
- **Target**: 1,500 tokens/sec for agentic AI
- **Integration**: Pairs with NVIDIA Vera Rubin NVL72
- **Form Factor**: LPX rack-scale (32 trays, 8 LPU per tray)
- **Cooling**: Liquid-cooled

### Why LPUs?
1. **Low latency** - designed for real-time inference
2. **Deterministic** - predictable performance at scale
3. **Efficient tensor parallelism** - scales across chips
4. **Air-cooled** (older models) - lower TCO

## Comparison to GPUs

| Feature | GPU (NVIDIA) | LPU (Groq) |
|---------|--------------|------------|
| Architecture | SIMT | TSP |
| Scheduling | Runtime | Compile-time |
| Latency | Variable | Deterministic |
| Use case | General ML | LLM inference |

## Relevance to LLM Engineering

Understanding inference hardware is key for:
- Model optimization (quantization, pruning)
- Deployment architecture decisions
- Cost optimization at scale
- Real-time vs batch processing tradeoffs
