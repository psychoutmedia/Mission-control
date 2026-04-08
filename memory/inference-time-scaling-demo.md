# Inference-Time Scaling Demo

> Building intuition for how computation at inference time affects model quality

## Concept

Inference-time scaling (ITX) = spending more compute during generation to get better outputs. Unlike training-time scaling (bigger models), ITX lets you trade latency for quality.

## Techniques

### 1. Sampling Temperature
```python
import torch
import torch.nn.functional as F

def temperature_sample(logits, temperature=1.0):
    """Higher temp = more random, lower = more deterministic"""
    if temperature == 0:
        return torch.argmax(logits, dim=-1)
    return torch.multinomial(F.softmax(logits / temperature, dim=-1), 1)
```

### 2. Top-K Sampling
```python
def top_k_sample(logits, k=50):
    """Only consider top-k tokens"""
    top_k_logits, top_k_indices = torch.topk(logits, k)
    top_k_probs = F.softmax(top_k_logits, dim=-1)
    return top_k_indices[torch.multinomial(top_k_probs, 1)]
```

### 3. Top-P (Nucleus) Sampling
```python
def top_p_sample(logits, p=0.9):
    """Sample from smallest set of tokens with cumulative prob > p"""
    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
    probs = F.softmax(sorted_logits, dim=-1)
    cumsum = torch.cumsum(probs, dim=-1)
    
    # Mask tokens after threshold
    sorted_mask = cumsum > p
    sorted_mask[..., 1:] = sorted_mask[..., :-1].clone()
    sorted_mask[..., 0] = False
    
    filtered_logits = sorted_logits.masked_fill(sorted_mask, float('-inf'))
    return sorted_indices[torch.multinomial(F.softmax(filtered_logits, dim=-1), 1)]
```

### 4. Beam Search
```python
def beam_search(model, prompt, beam_width=5, max_len=50):
    """Explore multiple paths simultaneously"""
    # Start with beam_width copies
    sequences = [prompt] * beam_width
    scores = [0.0] * beam_width
    
    for _ in range(max_len):
        all_candidates = []
        for seq, score in zip(sequences, scores):
            logits = model(seq)
            top_k = torch.topk(logits, beam_width)
            for token, s in zip(top_k.indices, top_k.values):
                new_seq = seq + [token]
                all_candidates.append((new_seq, score + s.item()))
        
        # Select top beam_width
        all_candidates.sort(key=lambda x: x[1], reverse=True)
        sequences = [x[0] for x in all_candidates[:beam_width]]
        scores = [x[1] for x in all_candidates[:beam_width]]
    
    return sequences[0]
```

### 5. Chain-of-Thought (CoT)
```python
def cot_prompt(question):
    """Prompt structure that triggers reasoning"""
    return f"""Question: {question}

Let's think step by step:
1. First, identify what we're asked
2. Break down the problem
3. Work through each part
4. Combine for final answer

Step 1:"""
```

### 6. Self-Consistency (ITX + CoT)
```python
def self_consistency(model, question, n_samples=5):
    """Generate multiple CoT reasoning paths, pick majority answer"""
    answers = []
    for _ in range(n_samples):
        # Sample with temperature > 0 for diversity
        answer = model.generate(question, temperature=0.7)
        answers.append(extract_answer(answer))
    
    # Majority vote
    return Counter(answers).most_common(1)[0][0]
```

## ITX Scaling Laws (Emerging)

| Compute Budget | Best Strategy |
|----------------|---------------|
| 1x baseline    | Greedy decoding |
| 2-5x           | Temperature + Top-P |
| 5-20x          | Beam search |
| 20-100x        | CoT prompting |
| 100x+          | Self-consistency / Tree search |

## Key Insight

> "The model that thinks longer, answers better."

ITX is especially powerful for:
- Math reasoning
- Complex code generation  
- Multi-step planning
- Fact verification

## References
- "Chain-of-Thought Prompting Elicits Reasoning" (Kojima et al., 2022)
- "Self-Consistency Improves CoT" (Wang et al., 2023)
- "Scaling Laws for Inference-Time Computation" (DeepSeek, 2026)
