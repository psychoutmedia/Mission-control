# LLM Inference Optimization — Deep Dive

How to make LLMs faster and cheaper at inference time. Critical knowledge for LLM engineers deploying models in production.

---

## The Inference Problem

LLM inference has two distinct phases:

| Phase | What happens | Bottleneck |
|---|---|---|
| **Prefill** | Process the prompt, compute all KV caches | Compute-bound (matmuls) |
| **Decode** | Generate tokens one-by-one | Memory-bandwidth-bound (KV cache reads) |

The **decode phase** is the killer — it's autoregressive (can't parallelize) and each token requires reading the entire KV cache from memory.

---

## 1. KV Cache

### The Core Problem
In autoregressive decoding, every new token attends to ALL previous tokens. Without caching, you'd recompute attention for the entire context on every step — O(n²) attention cost per token.

### How KV Cache Works
```python
# Without KV cache (imagine):
for each new token:
    # Recompute K and V for ALL tokens including previous ones
    for i in range(context_length):
        compute_attention(token_i, all_previous_tokens)  # O(n²)

# With KV cache:
# Cache K and V vectors for all previous tokens
k_cache = []  # (batch, heads, seq, head_dim)
v_cache = []

for each new token:
    # Only compute K,V for the NEW token
    k_new, v_new = compute_kv(new_token)
    k_cache.append(k_new)
    v_cache.append(v_cache)
    # Attention reads from cache: O(1) per token instead of O(n)
    attend_to(k_cache, v_cache)
```

### Memory Cost
```
KV cache per token ≈ 2 × layers × heads × head_dim × bytes_per_param
                    ≈ 2 × 40 × 32 × 128 × 2 bytes (fp16)
                    ≈ 640 KB per token

For 1000 tokens, 7B model: ~640 MB
For 1000 tokens, 70B model: ~3.2 GB
```

### Key Optimizations
- **PagedAttention** (vLLM): Virtual memory paging for KV cache. Splits into blocks, reduces memory waste from uneven sequence lengths. Allows 2-4x higher throughput.
- **Grouped Query Attention (GQA)**: Instead of one K,V per head, share across groups of heads. Reduces KV cache by 2-8x with minimal quality loss. (Llama 3 uses this.)
- **Multi-head Latent Attention (MLA)**: Low-rank compression of KV. DeepSeek-V2 uses this — reduces KV cache by 65%.

---

## 2. Batching Strategies

### Naive Batching
```
Batch 1: [Prompt A] → generate → [Response A]
Batch 2: [Prompt B] → generate → [Response B]
(Serial — waste GPU)
```

### Continuous Batching (Iteration-Level Scheduling)
- Batch multiple requests together
- When one sequence finishes, slot is immediately filled by a new request
- **Crucially important**: Different sequences finish at different times — don't wait for the longest
- Used by: vLLM, TGI, SGLang
- **Throughput improvement**: 10-50x over naive batching

### Prefix Caching
- Identify common prefixes across requests (system prompts, few-shot examples)
- Cache the prefill KV for the prefix
- Only prefill the unique suffix for each request
- Huge speedup when many requests share a system prompt

### Speculative Decoding (Draft-and-Verify)
```
Problem: Decoding is memory-bound (slow) because each token needs a full model forward pass.

Solution: Use a small "draft" model to generate 4-8 tokens quickly.
Then verify all of them in ONE pass with the large model.
If draft model was right → we got 4-8 tokens for price of 1.
If draft model was wrong → verify until mismatch, then resume.
```

```python
# Speculative decoding sketch
draft_tokens = small_model.generate(prompt, max_new_tokens=8)  # Fast

# Verify ALL draft tokens in one large-model forward pass
# (with extended context)
large_model_output = large_model(
    concat(prompt, draft_tokens)
)

# Accept tokens until first mismatch
for i, (draft_tok, large_tok) in enumerate(zip(draft_tokens, large_model_output)):
    if draft_tok != large_tok:
        accepted = draft_tokens[:i]
        # Regenerate from position i using large model
        break
```

- **Speedup**: 2-4x for typical text (high acceptance rate)
- **Tradeoff**: Draft model quality matters — if too wrong, you waste compute
- **Variants**: Self-speculative (draft from same model early layers), Medusa (multiple draft heads), EAGLE

---

## 3. Quantization

### Core Idea
Reduce weight precision: fp16 (16-bit) → int8 (8-bit) → int4 (4-bit).

| Format | Memory Reduction | Quality Impact | Speed |
|---|---|---|---|
| FP16 | baseline | none | baseline |
| INT8 | 2x | negligible | 1.5-2x faster |
| INT4 | 4x | small (fine-tuneable) | 2-4x faster |
| GPTQ (int4) | 4x | ~1-2% quality loss | fast decode |
| AWQ (int4) | 4x | slightly better than GPTQ | fast decode |
| GGUF | 4x | varies by implementation | depends on impl |

### Key Quantization Methods
- **Post-Training Quantization (PTQ)**: Quantize after training. Fast but can degrade quality.
- **Quantization-Aware Training (QAT)**: Train with fake quantization. Better quality but slower.
- **SmoothQuant**: Per-channel scaling to balance difficulty across channels before int8 quantization.
- **LLM.int8()**: Mixed int8/fp16 — outlier values stay in fp16.

### GGUF (GGML Unified Format)
- Q4_K_S, Q4_K_M, Q5_K_S, Q6_K, Q8_0 — different precision/quality tradeoffs
- **Q4_K_M**: Good balance. 4.5GB for 7B model instead of 14GB.
- Runs on CPU+GPU combos, Apple Silicon, etc.

---

## 4. Parallelism Strategies

### Tensor Parallelism (TP)
- Split weights across multiple GPUs along the tensor dimension
- Each GPU computes a slice of each matmul, then communicates
- For 70B model: needs 8 GPUs (each holds 1/8 of weights)
- NVLink required for acceptable performance (不然通信成为瓶颈)

### Pipeline Parallelism (PP)
- Split layers across GPUs (layer 0-31 on GPU 0, 32-63 on GPU 1)
- Simple but creates pipeline bubbles (GPUs waiting for each other)
- Micro-batching helps reduce bubbles

### ZeRO (Zero Redundancy Optimizer)
- **ZeRO-1**: Shard optimizer states across GPUs
- **ZeRO-2**: Shard gradients too
- **ZeRO-3**: Shard parameters (needs collective communication)
- **DeepSpeed** implements ZeRO

### FSDP (Fully Sharded Data Parallel)
- PyTorch-native version of ZeRO-3
- Shards model parameters across GPUs
- Better than naive DDP for large models

### Choice of Parallelism
| Model Size | GPUs | Recommended |
|---|---|---|
| 7B | 1-2 | TP=2 or PP |
| 13B | 2-4 | TP=2, PP=2 |
| 70B | 8 | TP=4, PP=2 |
| 100B+ | 16+ | TP+PP+DP combined |

---

## 5. Serving Frameworks

### vLLM
- PagedAttention for KV cache management
- Continuous batching
- Tensor parallelism
- **Best for**: High-throughput serving, many concurrent requests
- Used by: ChatGPT, Claude, many production deployments

### Hugging Face Text Generation Inference (TGI)
- Continuous batching
- CUDA graphs for faster prefill
- Flash Attention integration
- **Best for**: Easy deployment of HF models

### SGLang
- RadixAttention for prefix caching + automatic KV cache reuse
- Constrained decoding (regex, JSON schema)
- **Best for**: Complex inference patterns with shared prefixes

### TensorRT-LLM
- NVIDIA's optimized inference engine
- INT8/FP8 quantization
- Tensor parallelism up to 32 GPUs
- **Best for**: Maximum performance on NVIDIA hardware

---

## 6. Flash Attention

### What It Does
IO-aware exact attention that avoids materializing the full N×N attention matrix.

Standard attention:
```
Q, K, V → compute S = QK^T → softmax(S) → softmax(S) × V
```
Problem: S is N×N — for N=4096 tokens, that's 16M values. Materializing this is slow and memory-heavy.

Flash Attention: tiles the computation, keeps working set small, reduces HBM accesses from O(N²) to O(N).

```python
# Standard: O(N²) HBM reads/writes
# Flash Attention: O(N) HBM reads/writes via tiling
# Speedup: 2-4x faster, memory scales with N instead of N²
```

### Flash Attention 2
- Better tiling for A100/H100
- Even more efficient with new hardware

---

## 7. Key Trade-offs Summary

| Optimization | Latency | Throughput | Memory | Quality |
|---|---|---|---|---|
| KV Cache | ↓ (helps decode) | ↑ | ↑ | 0 |
| Continuous Batching | ↑ (queue wait) | ↑↑↑ | - | 0 |
| Speculative Decoding | ↓ (when right) | ↑ | +1 small model | 0 |
| INT8 Quantization | ↓ | ↑ | ↓2x | ~1% loss |
| INT4 Quantization | ↓↓ | ↑↑ | ↓4x | ~2-5% loss |
| Tensor Parallelism | - | ↑↑ | ↓ per GPU | 0 |
| Flash Attention | ↓ | ↑ | ↓ | 0 |

---

## Production Stack Recommendations

**For most people:**
```
vLLM + Continuous Batching + Flash Attention + INT8
```

**For maximum throughput (many requests, shared prefixes):**
```
SGLang + RadixAttention + Continuous Batching
```

**For NVIDIA-specific optimization:**
```
TensorRT-LLM + FP8 + Tensor Parallelism
```

**For local/small-scale:**
```
llama.cpp / Ollama + GGUF Q4_K_M
```

---

## Key Insights for LLM Engineers

1. **Decode is memory-bandwidth bound** — that's why batching and KV cache matter so much
2. **Prefill and decode need different optimizations** — conflating them is a common mistake
3. **Quantization is now mature** — int4 is good enough for most use cases with proper calibration
4. **Speculative decoding is underrated** — 2-4x speedup for free if you have the hardware
5. **The framework matters less than the strategy** — vLLM, TGI, SGLang all have similar throughput with the right config
