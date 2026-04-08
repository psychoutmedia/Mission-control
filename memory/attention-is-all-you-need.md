# "Attention Is All You Need" — Paper Summary

> Original: Vaswani et al., 2017 | Created: 2026-03-06

The paper that introduced the Transformer architecture — the foundation of all modern LLMs.

---

## TL;DR

The Transformer uses **self-attention** to compute representations — no recurrence, no convolution. Just attention mechanisms running in parallel.

---

## Key Contributions

1. **Transformer** — Pure attention, no RNN/CNN
2. **Multi-Head Attention** — Learn diverse attention patterns
3. **Positional Encoding** — Add position info via sin/cos
4. **Scaled Dot-Product Attention** — Efficient computation

---

## Architecture

```
Input → Embedding → Positional Encoding → Encoder × N → Output
                                                      ↓
                                              Decoder × N
                                                      ↓
                                               Linear + Softmax
```

### Encoder
- Multi-Head Attention (self-attention)
- Feed-Forward Network
- Residual connections + LayerNorm

### Decoder
- Multi-Head Attention (masked, looks at previous positions)
- Cross-attention (attends to encoder output)
- Feed-Forward Network

---

## Key Formulas

### Scaled Dot-Product Attention

```
Attention(Q, K, V) = softmax(QK^T / √d_k)V
```

- Q = queries (what I'm looking for)
- K = keys (what I contain)
- V = values (what I can provide)
- √d_k = scaling factor (prevents gradient vanishing)

### Multi-Head Attention

```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h)W^O

where head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
```

- h = 8 attention heads
- Each head learns different patterns

### Positional Encoding

```
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

- Allows model to understand word order
- Works for any sequence length

---

## Why It Works

| Aspect | Benefit |
|--------|---------|
| Parallel computation | Fast training (vs RNN sequential) |
| Long-range dependencies | Attention connects any positions directly |
| Interpretable | Can visualize attention weights |
| Scalable | Works for any sequence length |

---

## Results

| Model | BLEU (EN-DE) | BLEU (EN-FR) |
|-------|--------------|---------------|
| Transformer (base) | 27.3 | 38.1 |
| Transformer (big) | 28.4 | 41.0 |
| Previous best (GNMT) | 24.6 | — |

SOTA on WMT 2014 English-German and English-French translation.

---

## Key Insights

1. **Attention > Recurrence** — No need for RNNs when attention works this well
2. **Scaled attention** — Division by √d_k is crucial for training stability
3. **Residual connections** — Enable deep networks (6+ layers)
4. **Position encoding** — Sinusoidal works as well as learned

---

## Follow-up Papers

- **BERT** (2018) — Encoder-only, masked language modeling
- **GPT** (2018) — Decoder-only, autoregressive
- **GPT-2/3/4** — Scale + few-shot learning
- **T5** (2019) — Encoder-decoder, text-to-text
- **Llama** (2023) — Open weights, efficient

---

## Implementation Tips

From building transformers:

```python
# 1. Scale attention properly
scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)

# 2. Mask future positions (for decoder)
mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1).bool()
scores = scores.masked_fill(mask, float('-inf'))

# 3. Use residual connections
x = self.norm(x + self.attention(x))
x = self.norm(x + self.feed_forward(x))
```

---

## Legacy

This paper started the transformer revolution. Every modern LLM (GPT, Claude, Llama, etc.) is based on this architecture.

---

## Resources

- Paper: https://arxiv.org/abs/1706.03762
- Official code: https://github.com/tensorflow/tensor2tensor
- Annotated paper: https://nlp.seas.harvard.edu/2018/04/03/attention.html

---

*The paper that changed AI forever.* ✨
