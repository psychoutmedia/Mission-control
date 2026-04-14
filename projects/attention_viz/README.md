# Attention Visualizer

Visualize attention patterns in transformer models. Understand what your LLM "looks at" when it processes tokens.

## Quick Start

```python
from attention_viz import AttentionVisualizer
from transformers import AutoModel

# Load any transformer model
model = AutoModel.from_pretrained("gpt2")
viz = AttentionVisualizer(model)
viz.register_hooks()

# Run inference
tokens = ["The", "cat", "sat", "down", "."]
input_ids = tokenizer.encode(" ".join(tokens), return_tensors="pt")

viz.run(input_ids, tokens=tokens)

# Visualize
viz.plot_attention_heatmap(layer=0)
viz.plot_all_heads(layer=0)
viz.plot_token_attention(token_idx=1)  # How "cat" attends
```

## Features

- **Hook-based capture** — works with any PyTorch transformer (HuggingFace, custom, etc.)
- **Per-head heatmaps** — see exactly which head attends where
- **Layer-by-layer comparison** — early vs late layer attention patterns
- **Token-level attention** — track how specific tokens distribute their attention

## Key Methods

| Method | What it does |
|--------|-------------|
| `register_hooks()` | Attach to attention layers |
| `run(input_ids, tokens)` | Forward pass + capture |
| `plot_attention_heatmap(layer, head)` | Single layer/head heatmap |
| `plot_all_heads(layer)` | Grid of all heads in a layer |
| `plot_token_attention(token_idx)` | How one token attends across layers |
