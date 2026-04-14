# vLLM vs TGI vs Ollama — Self-Hosted LLM Inference

## TL;DR

| Engine | Throughput | Latency | Use Case | Hardware |
|--------|-----------|---------|----------|----------|
| **vLLM** | 🚀🚀🚀 Highest | Low | Production, high-throughput | NVIDIA GPU |
| **TGI** | 🚀🚀 Good | Low | HuggingFace ecosystem | NVIDIA GPU |
| **Ollama** | 🚀 Basic | Medium | Local dev, simplicity | Any (CPU+GPU) |
| **TensorRT-LLM** | 🚀🚀🚀🚀 Fastest | Lowest | Max performance | NVIDIA only |

---

## Architecture Comparison

### vLLM — PagedAttention Engine

**Key innovation:** PagedAttention — virtual memory-style paging for KV cache

- **Throughput:** 24x higher than HuggingFace transformers, 3.5x higher than TGI on LLaMA-13B
- **Red Hat benchmarks:** vLLM 793 tokens/sec vs Ollama 41 tokens/sec (same hardware)
- **Key features:**
  - PagedAttention for efficient KV cache management
  - Continuous batching (dynamic batch scheduling)
  - Tensor parallelism (multi-GPU)
  - Automatic prefix caching
  - Native tool calling / structured output support

**Strengths:**
- Highest throughput for production workloads
- Excellent for long contexts (due to PagedAttention)
- OpenAI-compatible API
- Active development (used by ChatGPT, Claude, etc.)

**Weaknesses:**
- NVIDIA GPUs only
- Higher memory usage overhead
- More complex setup than Ollama

---

### TGI (Text Generation Inference) — HuggingFace's Official Server

**Key innovation:** HuggingFace-native inference with production features

- **Throughput:** Good, but 3.5x slower than vLLM on same models
- **H100 benchmarks:** 29% throughput advantage over vLLM (Nvidia's own optimized build)
- **Key features:**
  - HuggingFace model hub integration
  - Flash Attention 2 (faster attention)
  - Tensor parallelism
  - Byte-level BPE tokenization
  - Watermarking support
  - Custom RTX builds for consumer GPUs

**Strengths:**
- Seamless HuggingFace ecosystem integration
- Best for when HF is your primary model source
- Good Docker support
- Proven at scale

**Weaknesses:**
- Lower throughput than vLLM
- Less flexible API
- Heavier resource usage

---

### Ollama — Local LLM Made Simple

**Key innovation:** Zero-config local inference

- **Throughput:** ~41 tokens/sec (vs 793 for vLLM — 19x slower)
- **Key features:**
  - One-command setup: `ollama run llama3`
  - Model library with auto-download
  - Cross-platform (Mac, Linux, Windows, Docker)
  - OpenAI-compatible API endpoint
  - GPU acceleration (CUDA/Metal)
  - No configuration needed

**Strengths:**
- Easiest to use by far
- Great for development and testing
- Works on consumer hardware (Mac with MPS)
- Lightweight
- Good model variety

**Weaknesses:**
- Lowest throughput (not for production)
- No multi-GPU/tensor parallelism
- Limited optimization (no PagedAttention, continuous batching)
- No advanced features like speculative decoding

---

## Benchmark Summary (2026)

| Engine | Throughput (tokens/sec) | Memory Efficiency | Multi-GPU |
|--------|------------------------|-------------------|-----------|
| vLLM | 793 (LLaMA-13B, H100) | Excellent (PagedAttention) | ✓ Full |
| TGI | ~226 (LLaMA-13B, H100) | Good | ✓ Full |
| Ollama | ~41 (LLaMA-13B, H100) | Basic | ✗ No |
| TensorRT-LLM | ~1000+ (LLaMA-13B, H100) | Excellent | ✓ Full |

---

## When to Use What

### vLLM — Use When:
- Production deployment with high throughput needs
- Long context windows (64K+ tokens)
- Need tensor parallelism across multiple GPUs
- Running quantized models (AWQ, GPTQ)
- Need OpenAI-compatible API
- Structured outputs / tool calling

### TGI — Use When:
- Already using HuggingFace ecosystem
- Need seamless model loading from HF Hub
- Want Flash Attention 2 optimization
- Enterprise deployment with HF support
- Docker-based deployment

### Ollama — Use When:
- Local development and testing
- Quick experiments with different models
- Running on consumer hardware (MacBook, laptop)
- Prototyping before production
- Personal use / hobby projects

### TensorRT-LLM — Use When:
- Maximum performance is critical
- Have NVIDIA A100/H100 GPUs
- Can invest time in optimization
- Batch processing workloads

---

## For Automa Dynamics (Helios-1 Agent)

**Recommendation for Mark's projects:**

| Context | Engine | Why |
|---------|--------|-----|
| **Local dev / testing** | Ollama | Zero config, works on Mac Mini |
| **RAG chatbot (current)** | Ollama (installed) | Already working, good enough for dev |
| **Production RAG** | vLLM | High throughput for concurrent users |
| **HF fine-tuning pipeline** | TGI | Native HF integration |
| **Fleet learning experiments** | vLLM | Multi-GPU, high throughput |

**Current setup:** Ollama already installed with phi3, gemma3:270m, llava models

**Next step:** Install vLLM separately for production workloads while keeping Ollama for dev

---

## Quick Reference Commands

### Ollama
```bash
# Simple model serving
ollama run llama3
ollama serve  # API at localhost:11434

# OpenAI-compatible endpoint
curl http://localhost:11434/v1/chat/completions \
  -d '{"model": "llama3", "messages": [{"role": "user", "content": "Hello"}]}'
```

### vLLM
```bash
# High-throughput serving
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3-8b-Instruct \
  --tensor-parallel-size 2 \
  --gpu-memory-utilization 0.9

# With OpenAI-compatible endpoint
curl http://localhost:8000/v1/chat/completions \
  -d '{"model": "meta-llama/Llama-3-8b-Instruct", "messages": [...]}'
```

### TGI
```bash
# Docker deployment
docker run -td --gpus all \
  -p 8080:80 \
  -v $HF_HOME:/data \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id meta-llama/Llama-3-8b-Instruct
```

---

## Resources

- [vLLM Paper (PagedAttention)](https://arxiv.org/abs/2309.06180)
- [TGI GitHub](https://github.com/huggingface/text-generation-inference)
- [Ollama](https://ollama.ai)
- [TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM)
- [Red Hat Benchmarks](https://www.redhat.com)
- [Prem AI Inference Comparison 2026](https://blog.premai.io/llm-inference-servers-compared-vllm-vs-tgi-vs-sglang-vs-triton-2026/)
