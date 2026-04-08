# Embeddings: From Word2Vec to Transformers

> Pillar 2: Go Deep (LLM Internals) | Created: 2026-03-06

Embeddings are how neural networks understand meaning. This guide traces the evolution from simple word vectors to the contextual embeddings that power modern LLMs.

---

## The Core Idea

**Problem**: Computers see text as arbitrary symbols. "cat" and "dog" look as different as "cat" and "quantum".

**Solution**: Map words to vectors where *similar meanings = similar vectors*.

```
"king"  → [0.2, 0.8, 0.1, ...]
"queen" → [0.3, 0.7, 0.2, ...]  ← close to king!
"fish"  → [0.9, 0.1, 0.4, ...]  ← far from both
```

---

## 1. One-Hot Encoding (The Naive Approach)

```python
vocab = ["cat", "dog", "fish", "bird"]

# One-hot: each word is a sparse vector
cat  = [1, 0, 0, 0]
dog  = [0, 1, 0, 0]
fish = [0, 0, 1, 0]
```

**Problems**:
- Every word equidistant from every other
- Vectors grow with vocabulary (50K+ dimensions)
- No semantic information

---

## 2. Word2Vec (2013) — The Breakthrough

Mikolov et al. at Google discovered: train a neural network to predict context, and the hidden layer *learns* meaningful representations.

### Two Architectures

**CBOW (Continuous Bag of Words)**: Predict center word from context
```
Context: "the cat sat on the ___"
Predict: "mat"
```

**Skip-gram**: Predict context from center word
```
Center: "cat"
Predict: ["the", "sat", "on"]
```

### The Magic: Arithmetic with Meaning

```python
king - man + woman ≈ queen
paris - france + italy ≈ rome
```

### Implementation

```python
import gensim.downloader as api

# Load pre-trained Word2Vec
model = api.load("word2vec-google-news-300")

# Find similar words
model.most_similar("python")
# [('Python', 0.73), ('Perl', 0.67), ('Ruby', 0.65), ...]

# Vector arithmetic
result = model.most_similar(positive=["king", "woman"], negative=["man"])
# [('queen', 0.71), ('monarch', 0.62), ...]

# Get raw vector
vec = model["computer"]  # Shape: (300,)
```

### Training Your Own

```python
from gensim.models import Word2Vec

# Your corpus: list of tokenized sentences
sentences = [
    ["the", "cat", "sat", "on", "the", "mat"],
    ["dogs", "are", "loyal", "pets"],
    # ... more sentences
]

# Train
model = Word2Vec(
    sentences,
    vector_size=100,   # Embedding dimension
    window=5,          # Context window
    min_count=1,       # Ignore rare words
    workers=4,         # Parallel training
    sg=1               # 1=skip-gram, 0=CBOW
)

# Use
vec = model.wv["cat"]
model.wv.most_similar("cat")
```

---

## 3. GloVe (2014) — Global Vectors

Stanford's approach: use *co-occurrence statistics* directly.

Build a matrix of how often words appear together, then factorize it.

```python
# Using pre-trained GloVe via gensim
import gensim.downloader as api
glove = api.load("glove-wiki-gigaword-100")

# Same interface as Word2Vec
glove.most_similar("python")
```

**Key difference**: Word2Vec uses local context windows; GloVe uses global corpus statistics.

---

## 4. The Limitation: Static Embeddings

Word2Vec and GloVe give **one vector per word**. But words have multiple meanings!

```
"bank" in "river bank" → geography
"bank" in "bank account" → finance
```

Same vector for both. 😕

---

## 5. Contextual Embeddings (2018+) — The Revolution

**ELMo, BERT, GPT**: Generate embeddings *based on context*.

```
"The bank was steep" → bank_vector_1 (geography)
"I went to the bank" → bank_vector_2 (finance)
```

Different vectors for the same word!

### How Transformers Create Embeddings

1. **Token Embedding**: Lookup table (like Word2Vec)
2. **Position Embedding**: Encode where the token is
3. **Contextual Layers**: Attention mixes information across tokens

```python
import torch
from transformers import AutoTokenizer, AutoModel

# Load BERT
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

# Get contextual embeddings
text = "The bank was steep and covered with grass"
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)

# outputs.last_hidden_state: [batch, seq_len, hidden_dim]
# Each token has a 768-dim contextual embedding
embeddings = outputs.last_hidden_state  # Shape: [1, 10, 768]

# The embedding for "bank" now encodes "geography" context
bank_idx = 2  # "bank" is token 2
bank_embedding = embeddings[0, bank_idx]  # Shape: [768]
```

### Sentence Embeddings

For comparing entire sentences:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "The cat sat on the mat",
    "A feline rested on the rug",
    "Quantum physics is complex"
]

# Get embeddings
embeddings = model.encode(sentences)  # Shape: [3, 384]

# Compute similarity
from sklearn.metrics.pairwise import cosine_similarity
sims = cosine_similarity(embeddings)
# sentences[0] and [1] will be similar (~0.7)
# sentences[0] and [2] will be different (~0.1)
```

---

## 6. Inside the Embedding Layer

```python
import torch
import torch.nn as nn

# Vocabulary size and embedding dimension
vocab_size = 50000
embed_dim = 768

# The embedding layer is just a lookup table
embedding = nn.Embedding(vocab_size, embed_dim)

# Input: token IDs
token_ids = torch.tensor([42, 1337, 7])  # 3 tokens

# Output: vectors
vectors = embedding(token_ids)  # Shape: [3, 768]

# The weights ARE the embeddings
embedding.weight  # Shape: [50000, 768]
# embedding.weight[42] == vectors[0]
```

### Position Embeddings

Transformers add position information:

```python
# Learned position embeddings (BERT-style)
max_seq_len = 512
position_embedding = nn.Embedding(max_seq_len, embed_dim)

positions = torch.arange(seq_len)  # [0, 1, 2, ...]
pos_vectors = position_embedding(positions)

# Final embedding = token_embed + position_embed
final = token_vectors + pos_vectors
```

```python
# Sinusoidal position embeddings (original Transformer)
def sinusoidal_positions(seq_len, d_model):
    position = torch.arange(seq_len).unsqueeze(1)
    div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
    
    pe = torch.zeros(seq_len, d_model)
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    return pe
```

---

## 7. Practical: Build a Similarity Search

```python
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Your knowledge base
documents = [
    "Python is a programming language",
    "Machine learning uses algorithms to learn from data",
    "The Eiffel Tower is in Paris",
    "Neural networks are inspired by the brain",
    "Cats are popular pets"
]

# Embed all documents
doc_embeddings = model.encode(documents)

def search(query, top_k=3):
    # Embed query
    query_embedding = model.encode([query])[0]
    
    # Cosine similarity
    similarities = np.dot(doc_embeddings, query_embedding) / (
        np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding)
    )
    
    # Top-k results
    top_indices = np.argsort(similarities)[::-1][:top_k]
    return [(documents[i], similarities[i]) for i in top_indices]

# Test
results = search("How do AI systems learn?")
# [("Machine learning uses algorithms to learn from data", 0.72),
#  ("Neural networks are inspired by the brain", 0.45), ...]
```

---

## 8. Key Dimensions to Understand

| Aspect | Word2Vec/GloVe | Transformer Embeddings |
|--------|----------------|------------------------|
| Context | Static (one vector per word) | Dynamic (depends on sentence) |
| Training | Unsupervised (predict context) | Self-supervised (masked LM, next token) |
| Dimension | 100-300 | 768-4096+ |
| Parameters | ~10M | 100M-100B+ |
| Use case | Word similarity, analogies | Everything (QA, generation, reasoning) |

---

## 9. The Evolution Timeline

```
2013: Word2Vec (Google) — word vectors that capture meaning
2014: GloVe (Stanford) — global co-occurrence statistics
2017: Transformer (Google) — attention is all you need
2018: ELMo (AllenAI) — first contextual embeddings (LSTM)
2018: BERT (Google) — bidirectional transformer embeddings
2018: GPT (OpenAI) — autoregressive transformer
2020: GPT-3 — emergence of few-shot learning
2022+: GPT-4, Claude, Llama — massive scale, instruction tuning
```

---

## 10. Exercises

1. **Word2Vec Arithmetic**: Load pre-trained vectors and try:
   - `doctor - man + woman = ?`
   - `tokyo - japan + france = ?`

2. **Contextual Difference**: Encode "bank" in two contexts with BERT, measure cosine similarity

3. **Build RAG**: Embed a set of documents, implement semantic search, feed results to an LLM

### Solutions

```python
# Exercise 1
import gensim.downloader as api
model = api.load("word2vec-google-news-300")
print(model.most_similar(positive=["doctor", "woman"], negative=["man"]))
# [('nurse', 0.69), ('physician', 0.64), ...]

# Exercise 2
from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

def get_word_embedding(text, word):
    inputs = tokenizer(text, return_tensors="pt")
    tokens = tokenizer.tokenize(text)
    word_idx = tokens.index(word) + 1  # +1 for [CLS]
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[0, word_idx]

emb1 = get_word_embedding("The river bank was muddy", "bank")
emb2 = get_word_embedding("I deposited money at the bank", "bank")

similarity = torch.cosine_similarity(emb1.unsqueeze(0), emb2.unsqueeze(0))
print(f"Similarity: {similarity.item():.3f}")  # ~0.5-0.7 (different contexts!)
```

---

## Next Steps

- **Pillar 1**: Use these embeddings in PyTorch models
- **Pillar 2**: Combine with attention (see `memory/attention-explainer.md`)
- **Pillar 3**: Build RAG agent using vector search
- **Pillar 4**: Use embeddings in SIAM's pattern matching

*From one vector per word to one vector per context — that's the leap that made modern AI possible.* ✨
