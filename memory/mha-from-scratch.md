# Multi-Head Attention from Scratch (PyTorch)

## Implementation

```python
import torch
import torch.nn.functional as F
import math

class MultiHeadAttention(torch.nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # Linear projections for Q, K, V, and output
        self.W_q = torch.nn.Linear(d_model, d_model)
        self.W_k = torch.nn.Linear(d_model, d_model)
        self.W_v = torch.nn.Linear(d_model, d_model)
        self.W_o = torch.nn.Linear(d_model, d_model)
    
    def split_heads(self, x):
        """Reshape (batch, seq, d_model) -> (batch, heads, seq, d_k)"""
        batch_size, seq_len, _ = x.shape
        return x.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
    
    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)
        
        # 1. Linear projections + split heads
        Q = self.split_heads(self.W_q(query))  # (batch, heads, seq_q, d_k)
        K = self.split_heads(self.W_k(key))    # (batch, heads, seq_k, d_k)
        V = self.split_heads(self.W_v(value))  # (batch, heads, seq_v, d_k)
        
        # 2. Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attn_weights = F.softmax(scores, dim=-1)
        attn_output = torch.matmul(attn_weights, V)  # (batch, heads, seq, d_k)
        
        # 3. Merge heads back to (batch, seq, d_model)
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(batch_size, -1, self.d_model)
        
        # 4. Final linear projection
        return self.W_o(attn_output)
```

## Key Concepts

- **d_model**: Model dimension (e.g., 512)
- **num_heads**: Number of attention heads (e.g., 8)
- **d_k**: Key dimension per head = d_model / num_heads
- **Scaling**: Divide by √d_k to prevent vanishing gradients
- **Masking**: Used for causal (decoding) attention

## Tested
- Input: (batch=2, seq=10, d_model=512)
- Output: (batch=2, seq=10, d_model=512) ✓
