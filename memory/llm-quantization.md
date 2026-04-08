# LLM Quantization

## What is Quantization?

Reducing model precision to save memory/speed:
- FP32 (32-bit) → INT8 (8-bit) → INT4 (4-bit)
- Tradeoff: Slight accuracy loss for big gains

## Quantization Levels

| Level | Bits | Size Reduction | Quality | Use Case |
|-------|------|----------------|---------|----------|
| FP16 | 16 | 50% | Full | Fast GPUs |
| INT8 | 8 | 75% | ~99% | Standard |
| INT4 | 4 | 87.5% | ~95% | CPU/low-end |
| Q2-Q3 | 2-3 | ~90%+ | ~85-90% | Mobile |

## Formats

### GGUF (GGML Unified Format)
- Used by Ollama, llama.cpp
- Supports many quantization levels
- K-quantization (Q4_K, Q5_K, etc.)

### AWQ (Activation-aware)
- Better accuracy than GPTQ
- Faster inference
- Newer format

### GPTQ
- Popular for GPU inference
- Good accuracy
- Widely supported

## Ollama Quantization

```
# Pull quantized model
ollama pull llama2:7b-q4

# List available quantizations
ollama list
```

## Quality vs Size

- **Q4_0**: Good balance, 4GB for 7B
- **Q5_K_M**: Better quality, slightly larger
- **Q8_0**: Near-FP16, 7GB for 7B

## When to Use

| Scenario | Quantization |
|----------|--------------|
| Production GPU | FP16 or INT8 |
| Consumer GPU | Q4/Q5 |
| CPU only | Q4 or lower |
| Mobile/Edge | INT4 or Q2 |

## Key Insight

Quantization enables:
- Running larger models on smaller hardware
- Faster inference
- Lower memory usage

Tradeoff is usually <5% accuracy loss for 4x size reduction.
