# PyTorch Tensor Operations — Hands-On Tutorial

> Pillar 1: Python Mastery | Created: 2026-03-06

Tensors are the fundamental data structure in PyTorch. Master these and you master the foundation of deep learning.

## Setup

```bash
pip install torch
```

```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"MPS available: {torch.backends.mps.is_available()}")  # Apple Silicon
```

---

## 1. Creating Tensors

```python
# From Python lists
x = torch.tensor([1, 2, 3])
matrix = torch.tensor([[1, 2], [3, 4]])

# Common initializations
zeros = torch.zeros(3, 4)          # 3x4 of zeros
ones = torch.ones(2, 3)            # 2x3 of ones
rand = torch.rand(2, 3)            # Uniform [0, 1)
randn = torch.randn(2, 3)          # Normal distribution
arange = torch.arange(0, 10, 2)    # [0, 2, 4, 6, 8]
linspace = torch.linspace(0, 1, 5) # 5 evenly spaced points

# Like another tensor (same shape/device)
y = torch.zeros_like(x)
z = torch.rand_like(matrix.float())

print(f"Shape: {matrix.shape}")    # torch.Size([2, 2])
print(f"Dtype: {matrix.dtype}")    # torch.int64
print(f"Device: {matrix.device}")  # cpu
```

---

## 2. Tensor Attributes & Conversion

```python
t = torch.rand(3, 4)

# Key attributes
t.shape      # torch.Size([3, 4])
t.ndim       # 2 (number of dimensions)
t.numel()    # 12 (total elements)
t.dtype      # torch.float32

# Type conversion
t.int()      # Convert to int
t.float()    # Convert to float32
t.double()   # Convert to float64
t.to(torch.float16)  # Explicit dtype

# NumPy interop
import numpy as np
np_array = t.numpy()           # Tensor → NumPy (shared memory!)
back = torch.from_numpy(np_array)  # NumPy → Tensor
```

⚠️ **Warning**: `.numpy()` shares memory. Changes to one affect the other!

---

## 3. Indexing & Slicing

```python
t = torch.arange(12).reshape(3, 4)
# tensor([[ 0,  1,  2,  3],
#         [ 4,  5,  6,  7],
#         [ 8,  9, 10, 11]])

t[0]        # First row: [0, 1, 2, 3]
t[:, 0]     # First column: [0, 4, 8]
t[1, 2]     # Element at (1, 2): 6
t[0:2, 1:3] # Submatrix: [[1, 2], [5, 6]]
t[-1]       # Last row: [8, 9, 10, 11]
t[..., -1]  # Last column (ellipsis): [3, 7, 11]

# Boolean indexing
mask = t > 5
t[mask]     # All elements > 5: [6, 7, 8, 9, 10, 11]

# Fancy indexing
indices = torch.tensor([0, 2])
t[indices]  # Rows 0 and 2
```

---

## 4. Reshaping Operations

```python
t = torch.arange(12)

# Reshape (must match total elements)
t.reshape(3, 4)     # 3 rows, 4 cols
t.reshape(2, -1)    # 2 rows, infer cols (6)
t.view(3, 4)        # Like reshape but requires contiguous memory

# Add/remove dimensions
t.unsqueeze(0)      # Add dim at position 0: [1, 12]
t.unsqueeze(-1)     # Add dim at end: [12, 1]
t.reshape(3, 4).squeeze()  # Remove dims of size 1

# Transpose & permute
m = torch.rand(2, 3, 4)
m.T                 # Only for 2D: transpose
m.transpose(0, 1)   # Swap dims 0 and 1: [3, 2, 4]
m.permute(2, 0, 1)  # Reorder all dims: [4, 2, 3]

# Flatten
m.flatten()         # 1D tensor of all elements
m.flatten(1)        # Flatten from dim 1 onwards
```

---

## 5. Mathematical Operations

```python
a = torch.tensor([1., 2., 3.])
b = torch.tensor([4., 5., 6.])

# Element-wise
a + b               # Addition
a * b               # Multiplication
a / b               # Division
a ** 2              # Power
torch.sqrt(a)       # Square root
torch.exp(a)        # e^x
torch.log(a)        # Natural log

# Reduction operations
a.sum()             # Sum all: 6
a.mean()            # Mean: 2
a.max()             # Max value: 3
a.argmax()          # Index of max: 2
a.min()             # Min value: 1

# Matrix operations
m1 = torch.rand(2, 3)
m2 = torch.rand(3, 4)
m1 @ m2             # Matrix multiplication: [2, 4]
torch.matmul(m1, m2)  # Same as @
m1.mm(m2)           # Also same (only 2D)

# Dot product
torch.dot(a, b)     # 32 (only 1D vectors)

# Batch matrix multiply
batch = torch.rand(5, 2, 3)
other = torch.rand(5, 3, 4)
torch.bmm(batch, other)  # [5, 2, 4]
```

---

## 6. Broadcasting

PyTorch automatically expands tensors to compatible shapes:

```python
# Scalar + tensor
torch.tensor([1, 2, 3]) + 10  # [11, 12, 13]

# Different shapes
a = torch.ones(3, 1)    # [3, 1]
b = torch.ones(1, 4)    # [1, 4]
c = a + b               # [3, 4] - broadcasted!

# Rules:
# 1. Align shapes from the right
# 2. Dimensions must be equal OR one of them is 1
# 3. Missing dims treated as 1

# Example: [2, 3, 4] + [4] works → [2, 3, 4]
# Example: [2, 3, 4] + [3, 4] works → [2, 3, 4]
# Example: [2, 3, 4] + [2, 4] FAILS (3 != 2)
```

---

## 7. In-Place Operations

Operations ending in `_` modify tensors in-place:

```python
x = torch.ones(3)
x.add_(1)       # x is now [2, 2, 2]
x.mul_(2)       # x is now [4, 4, 4]
x.zero_()       # x is now [0, 0, 0]
x.fill_(5)      # x is now [5, 5, 5]

# Careful with autograd!
# In-place ops can break gradient computation
```

---

## 8. Device Management (CPU/GPU/MPS)

```python
# Check availability
torch.cuda.is_available()        # NVIDIA GPU
torch.backends.mps.is_available()  # Apple Silicon

# Move tensors
device = "mps" if torch.backends.mps.is_available() else "cpu"
t = torch.rand(3, 3)
t_gpu = t.to(device)
t_cpu = t_gpu.to("cpu")

# Create directly on device
t = torch.rand(3, 3, device=device)

# All tensors in an operation must be on same device!
```

---

## 9. Gradients (Autograd Basics)

```python
# Enable gradient tracking
x = torch.tensor([2.0], requires_grad=True)
y = x ** 2 + 3 * x + 1  # y = x² + 3x + 1

# Compute gradients
y.backward()
print(x.grad)  # dy/dx = 2x + 3 = 7

# Disable gradients (for inference)
with torch.no_grad():
    z = x * 2  # No gradient tracking

# Detach from graph
detached = y.detach()  # New tensor, no grad history
```

---

## 10. Common Patterns for ML

```python
# Batch processing
batch_size = 32
seq_len = 100
hidden_dim = 256

# Typical shapes in transformers
tokens = torch.randint(0, 50000, (batch_size, seq_len))  # [B, S]
embeddings = torch.randn(batch_size, seq_len, hidden_dim)  # [B, S, H]

# Softmax (attention scores)
scores = torch.randn(batch_size, 8, seq_len, seq_len)  # [B, heads, S, S]
attention = torch.softmax(scores, dim=-1)  # Softmax over last dim

# Layer normalization pattern
mean = embeddings.mean(dim=-1, keepdim=True)
std = embeddings.std(dim=-1, keepdim=True)
normalized = (embeddings - mean) / (std + 1e-6)

# Concatenation & stacking
a = torch.rand(2, 3)
b = torch.rand(2, 3)
torch.cat([a, b], dim=0)    # [4, 3] - concat along dim
torch.stack([a, b], dim=0)  # [2, 2, 3] - new dim
```

---

## Practice Exercises

1. Create a 5x5 identity matrix
2. Generate 100 random points from N(0, 1), compute mean and std
3. Create two 3x3 matrices, multiply them
4. Implement vector cosine similarity: `cos(a,b) = (a·b)/(|a||b|)`
5. Create a batch of 16 random 28x28 "images", flatten to [16, 784]

### Solutions

```python
# 1. Identity matrix
eye = torch.eye(5)

# 2. Stats
samples = torch.randn(100)
print(f"Mean: {samples.mean():.4f}, Std: {samples.std():.4f}")

# 3. Matrix multiply
m1 = torch.rand(3, 3)
m2 = torch.rand(3, 3)
result = m1 @ m2

# 4. Cosine similarity
def cosine_sim(a, b):
    return torch.dot(a, b) / (torch.norm(a) * torch.norm(b))

# 5. Batch flatten
images = torch.rand(16, 28, 28)
flat = images.flatten(1)  # [16, 784]
```

---

## Next Steps

- **Pillar 1 continues**: `nn.Module` and building layers
- **Pillar 2**: Implement attention from scratch using these ops
- **Pillar 3**: Use tensors in ReAct agent state management

*Tensors mastered → Neural nets unlocked* ✨
