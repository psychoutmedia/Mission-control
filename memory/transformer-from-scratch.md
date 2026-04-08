# Transformer From Scratch — Attention Only

> Created: 2026-03-06

Implement a transformer from scratch using PyTorch. Focus on the core attention mechanism.

---

## The Transformer Architecture

```
Input → Embedding → Positional Encoding → [Encoder Layer × N] → Output
                                              │
                                    ┌─────────┴─────────┐
                                    │                   │
                              Multi-Head Attention    Feed Forward
                                    │                   │
                                    └─────────┬─────────┘
                                              │
```

We'll build:
1. **Positional Encoding** — add position information
2. **Scaled Dot-Product Attention** — the core mechanism
3. **Multi-Head Attention** — parallel attention heads
4. **Encoder Layer** — attention + feed-forward

---

## 1. Positional Encoding

```python
import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    """Add positional information to token embeddings."""
    
    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        # Compute frequency terms
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        
        # Apply sin to even indices, cos to odd
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        # Add batch dimension and register as buffer (non-trainable)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input."""
        return x + self.pe[:, :x.size(1)]
```

**Test it:**
```python
pe = PositionalEncoding(d_model=512, max_len=100)
x = torch.randn(2, 10, 512)  # batch=2, seq=10, d_model=512
out = pe(x)
print(out.shape)  # torch.Size([2, 10, 512])
```

---

## 2. Scaled Dot-Product Attention

The core of transformer:

```
Attention(Q, K, V) = softmax(QK^T / √d_k)V
```

```python
def scaled_dot_product_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    mask: torch.Tensor = None
) -> torch.Tensor:
    """
    Compute scaled dot-product attention.
    
    Args:
        query: (batch, heads, seq_len_q, d_k)
        key:   (batch, heads, seq_len_k, d_k)
        value: (batch, heads, seq_len_v, d_v)
        mask:  (batch, 1, seq_len_q, seq_len_k) or broadcastable
    
    Returns:
        attention output: (batch, heads, seq_len_q, d_v)
        attention weights: (batch, heads, seq_len_q, seq_len_k)
    """
    d_k = query.size(-1)
    
    # Compute QK^T / √d_k
    scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(d_k)
    
    # Apply mask if provided (optional)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))
    
    # Softmax over last dimension
    attention_weights = torch.softmax(scores, dim=-1)
    
    # Apply attention to values
    output = torch.matmul(attention_weights, value)
    
    return output, attention_weights
```

---

## 3. Multi-Head Attention

Run multiple attention operations in parallel:

```python
class MultiHeadAttention(nn.Module):
    """Multi-head self-attention."""
    
    def __init__(
        self, 
        d_model: int, 
        num_heads: int, 
        dropout: float = 0.1
    ):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # Linear projections for Q, K, V
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        
        # Output projection
        self.W_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(
        self, 
        query: torch.Tensor, 
        key: torch.Tensor, 
        value: torch.Tensor,
        mask: torch.Tensor = None
    ) -> torch.Tensor:
        batch_size = query.size(0)
        
        # 1. Linear projections
        Q = self.W_q(query)
        K = self.W_k(key)
        V = self.W_v(value)
        
        # 2. Reshape for multi-head: (B, N, L, d_k)
        Q = Q.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # 3. Scaled dot-product attention
        attention_output, _ = scaled_dot_product_attention(Q, K, V, mask)
        
        # 4. Concatenate heads
        attention_output = attention_output.transpose(1, 2).contiguous()
        attention_output = attention_output.view(batch_size, -1, self.d_model)
        
        # 5. Final linear projection
        output = self.W_o(attention_output)
        
        return output
```

---

## 4. Feed-Forward Network

```python
class FeedForward(nn.Module):
    """Position-wise feed-forward network."""
    
    def __init__(self, d_model: int, d_ff: int = 2048, dropout: float = 0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear2(self.dropout(torch.relu(self.linear1(x))))
```

---

## 5. Encoder Layer

Combine attention + feed-forward with residual connections and layer norm:

```python
class EncoderLayer(nn.Module):
    """Single transformer encoder layer."""
    
    def __init__(
        self, 
        d_model: int, 
        num_heads: int, 
        d_ff: int = 2048,
        dropout: float = 0.1
    ):
        super().__init__()
        
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        # Multi-head attention with residual
        attn_output = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout1(attn_output))
        
        # Feed-forward with residual
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout2(ff_output))
        
        return x
```

---

## 6. Complete Transformer Encoder

```python
class TransformerEncoder(nn.Module):
    """Complete transformer encoder."""
    
    def __init__(
        self,
        vocab_size: int,
        d_model: int = 512,
        num_heads: int = 8,
        num_layers: int = 6,
        d_ff: int = 2048,
        dropout: float = 0.1,
        max_len: int = 5000
    ):
        super().__init__()
        
        # Token embedding
        self.embedding = nn.Embedding(vocab_size, d_model)
        
        # Positional encoding
        self.pos_encoding = PositionalEncoding(d_model, max_len)
        
        # Encoder layers
        self.layers = nn.ModuleList([
            EncoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        
        self.dropout = nn.Dropout(dropout)
        
        # Output projection (for next-token prediction)
        self.output_proj = nn.Linear(d_model, vocab_size)
    
    def forward(
        self, 
        x: torch.Tensor,
        mask: torch.Tensor = None
    ) -> torch.Tensor:
        # Embed + positional encoding
        x = self.embedding(x)
        x = self.pos_encoding(x)
        x = self.dropout(x)
        
        # Pass through encoder layers
        for layer in self.layers:
            x = layer(x, mask)
        
        # Project to vocabulary
        logits = self.output_proj(x)
        
        return logits
```

---

## 7. Full Working Example

```python
import torch

# Simple test
vocab_size = 10000
d_model = 256
num_heads = 8
num_layers = 4

model = TransformerEncoder(
    vocab_size=vocab_size,
    d_model=d_model,
    num_heads=num_heads,
    num_layers=num_layers
)

# Random input (batch=2, seq_len=30)
x = torch.randint(0, vocab_size, (2, 30))

# Forward pass
logits = model(x)

print(f"Input shape:  {x.shape}")          # torch.Size([2, 30])
print(f"Output shape: {logits.shape}")    # torch.Size([2, 30, 10000])

# Compute loss (next-token prediction)
# Shift to predict next token
shift_logits = logits[:, :-1, :].contiguous()
shift_labels = x[:, 1:].contiguous()

loss_fn = nn.CrossEntropyLoss()
loss = loss_fn(shift_logits.view(-1, vocab_size), shift_labels.view(-1))

print(f"Loss: {loss.item():.4f}")

# Backprop
loss.backward()
```

---

## 8. Visualization — What Each Head Learns

```python
def visualize_attention(model, tokenizer, text):
    """Visualize attention weights from the first layer."""
    model.eval()
    
    # Tokenize
    tokens = tokenizer.encode(text)
    tokens = torch.tensor(tokens).unsqueeze(0)
    
    with torch.no_grad():
        # Get attention from first layer
        attn = model.layers[0].attention(
            model.embedding(tokens),
            model.embedding(tokens),
            model.embedding(tokens)
        )[1]  # Second return value is attention weights
    
    # Shape: (batch, heads, seq, seq)
    attn = attn.squeeze(0)  # Remove batch
    
    # Plot head 0
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(10, 8))
    plt.imshow(attn[0].numpy(), cmap='viridis')
    plt.xticks(range(len(tokens)), tokenizer.decode(tokens), rotation=90)
    plt.yticks(range(len(tokens)), tokenizer.decode(tokens))
    plt.title("Attention Head 0")
    plt.colorbar()
    plt.show()
```

---

## Key Takeaways

| Component | Formula | Purpose |
|-----------|---------|---------|
| Positional Encoding | sin/cos | Add position info |
| Scaled Dot-Product | softmax(QK^T/√d)V | Core attention |
| Multi-Head | concat(heads) | Learn diverse patterns |
| Feed-Forward | Linear → ReLU → Linear | Process per position |
| Layer Norm | (x - μ) / σ | Stabilize training |
| Residual | x + sublayer(x) | Enable deep networks |

---

## Next Steps

1. **Run the code** — implement and test locally
2. **Add decoder** — for sequence-to-sequence tasks
3. **Try GPT-style** — causal (masked) attention
4. **Compare with HuggingFace** — validate against bert-base

---

## Reference

- "Attention Is All You Need" (Vaswani et al., 2017)
- Original paper: https://arxiv.org/abs/1706.03762

*You now understand transformers at the code level.* ✨
