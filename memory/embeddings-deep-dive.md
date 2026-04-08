# LLM Embeddings Deep Dive

## What are Embeddings?

Vector representations of text that capture meaning.

## Types

| Type | Model | Use Case |
|------|-------|----------|
| Word2Vec | Static | Fast, simple |
| BERT | Contextual | Deep understanding |
| Sentence | sentence-transformers | Semantic search |
| OpenAI | text-embedding-ada | Production |

## Generation

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(["Hello world"])
```

## Applications

- Semantic search
- Clustering
- Classification
- Similarity detection

## Storage

- Pinecone
- Weaviate
- Qdrant
- Chroma

## Cost

OpenAI: $0.10/1M tokens
Local: Free (but slower)
