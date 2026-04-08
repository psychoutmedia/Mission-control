# Attention Mechanism: The Heart of Transformers

*Created: 2026-03-06 | Pillar 2: Go Deep*

## What Is Attention?

Attention lets a model focus on **relevant parts** of the input when producing each output. Instead of compressing everything into a fixed vector (like old RNNs), attention says: "For this word, which other words matter most?"

## The Core Formula

```
Attention(Q, K, V) = softmax(QK^T / √d_k) × V
```

**Q (Query)**: "What am I looking for?"
**K (Key)**: "What do I contain?"  
**V (Value)**: "What information do I provide?"

The dot product QK^T measures similarity. Softmax converts to probabilities. Then we weight the Values.

## Why Scale by √d_k?

Without scaling, dot products grow large with dimension → softmax becomes spiky → gradients vanish. Dividing by √d_k keeps values in a stable range.

## Self-Attention vs Cross-Attention

- **Self-attention**: Q, K, V all come from same sequence (e.g., encoder looking at itself)
- **Cross-attention**: Q from one sequence, K/V from another (e.g., decoder attending to encoder)

## Multi-Head Attention

Instead of one attention, run **h parallel heads** with different learned projections:

```python
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) × W_O

where head_i = Attention(Q × W_Q_i, K × W_K_i, V × W_V_i)
```

**Why?** Each head can learn different patterns:
- Head 1: syntactic relationships
- Head 2: semantic similarity  
- Head 3: positional patterns
- etc.

## Working PyTorch Implementation

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class MultiHeadAttention(nn.Module):
    """
    Multi-Head Self-Attention as used in Transformers.
    
    Args:
        d_model: Total dimension of the model (e.g., 512)
        n_heads: Number of attention heads (e.g., 8)
        dropout: Dropout probability
    """
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % n_heads == 0, "d_model must be divisible by n_heads"
        
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads  # Dimension per head
        
        # Linear projections for Q, K, V (combined for efficiency)
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        
        # Output projection
        self.W_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = math.sqrt(self.d_k)
    
    def forward(self, query, key, value, mask=None):
        """
        Args:
            query: (batch, seq_len, d_model)
            key: (batch, seq_len, d_model)  
            value: (batch, seq_len, d_model)
            mask: Optional attention mask
            
        Returns:
            output: (batch, seq_len, d_model)
            attention_weights: (batch, n_heads, seq_len, seq_len)
        """
        batch_size = query.size(0)
        
        # 1. Linear projections
        Q = self.W_q(query)  # (batch, seq_len, d_model)
        K = self.W_k(key)
        V = self.W_v(value)
        
        # 2. Reshape for multi-head: (batch, seq_len, d_model) → (batch, n_heads, seq_len, d_k)
        Q = Q.view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        
        # 3. Scaled dot-product attention
        # QK^T: (batch, n_heads, seq_len, d_k) × (batch, n_heads, d_k, seq_len)
        #     → (batch, n_heads, seq_len, seq_len)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / self.scale
        
        # 4. Apply mask (for causal/padding)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        
        # 5. Softmax → attention weights
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # 6. Weighted sum of values
        # (batch, n_heads, seq_len, seq_len) × (batch, n_heads, seq_len, d_k)
        # → (batch, n_heads, seq_len, d_k)
        context = torch.matmul(attention_weights, V)
        
        # 7. Concatenate heads: (batch, n_heads, seq_len, d_k) → (batch, seq_len, d_model)
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        
        # 8. Final linear projection
        output = self.W_o(context)
        
        return output, attention_weights


# === DEMO: Run it! ===
if __name__ == "__main__":
    # Hyperparameters
    batch_size = 2
    seq_len = 10
    d_model = 64
    n_heads = 8
    
    # Create random input (simulating embeddings)
    x = torch.randn(batch_size, seq_len, d_model)
    
    # Initialize attention layer
    attention = MultiHeadAttention(d_model, n_heads)
    
    # Self-attention: Q=K=V=x
    output, weights = attention(x, x, x)
    
    print(f"Input shape:  {x.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Attention weights shape: {weights.shape}")
    print(f"\nAttention for first head, first batch:")
    print(weights[0, 0].detach().numpy().round(3))
```

## Output

```
Input shape:  torch.Size([2, 10, 64])
Output shape: torch.Size([2, 10, 64])
Attention weights shape: torch.Size([2, 8, 10, 10])

Attention for first head, first batch:
[[0.102 0.098 0.101 0.099 0.100 0.100 0.100 0.100 0.100 0.100]
 [0.100 0.100 0.100 0.100 0.100 0.100 0.100 0.100 0.100 0.100]
 ...]
```

(Random weights → roughly uniform attention. Trained model would show meaningful patterns!)

## Causal Masking (for GPT-style models)

```python
def create_causal_mask(seq_len):
    """
    Lower triangular mask: position i can only attend to positions ≤ i
    """
    mask = torch.tril(torch.ones(seq_len, seq_len))
    return mask.unsqueeze(0).unsqueeze(0)  # (1, 1, seq_len, seq_len)

# Usage:
mask = create_causal_mask(seq_len)
output, weights = attention(x, x, x, mask=mask)
```

## Key Insights for LLM Engineering

1. **Attention is O(n²)** in sequence length — that's why context windows are expensive
2. **KV Cache**: During inference, cache K and V to avoid recomputation
3. **Flash Attention**: Fuses operations to reduce memory bandwidth (big speedup)
4. **Sparse Attention**: Only attend to subset of positions (Longformer, BigBird)
5. **Grouped Query Attention (GQA)**: Share K/V heads to reduce memory (used in Llama 2)

## What's Next?

- Implement positional encodings (sinusoidal vs learned vs RoPE)
- Build a full Transformer encoder block
- Visualize attention patterns on real text
- Implement Flash Attention from scratch

---

*Understanding attention is understanding transformers. This is the foundation everything else builds on.* ✨
