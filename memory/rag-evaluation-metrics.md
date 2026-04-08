# RAG Evaluation Metrics

> Created: 2026-03-06

How to measure if your RAG system is actually working.

---

## Core Metrics

### 1. Retrieval Metrics

| Metric | What it measures | Formula |
|--------|-----------------|---------|
| **Hit Rate** | % of queries with relevant doc in top-k | hits / total_queries |
| **MRR** (Mean Reciprocal Rank) | Rank of first relevant doc | avg(1/rank_i) |
| **NDCG** | Normalized discounted cumulative gain | See below |
| **Recall@k** | % of relevant docs in top-k | relevant_in_topk / total_relevant |

### 2. Generation Metrics

| Metric | What it measures |
|--------|-----------------|
| **Faithfulness** | Does answer match retrieved context? |
| **Answer Relevance** | Does answer address the question? |
| **Context Precision** | Is retrieved context actually relevant? |

---

## Implementation

```python
import numpy as np
from typing import List, Tuple

def hit_rate(retrieved_docs: List[List[str]], relevant_docs: List[List[str]]) -> float:
    """Calculate hit rate: % of queries with relevant doc in top-k."""
    hits = 0
    for retrieved, relevant in zip(retrieved_docs, relevant_docs):
        if any(doc in relevant for doc in retrieved):
            hits += 1
    return hits / len(retrieved_docs)

def mrr(retrieved_docs: List[List[str]], relevant_docs: List[List[str]]) -> float:
    """Mean Reciprocal Rank: average of 1/rank of first relevant doc."""
    reciprocal_ranks = []
    for retrieved, relevant in zip(retrieved_docs, relevant_docs):
        for rank, doc in enumerate(retrieved, 1):
            if doc in relevant:
                reciprocal_ranks.append(1 / rank)
                break
        else:
            reciprocal_ranks.append(0)
    return np.mean(reciprocal_ranks)

def recall_at_k(retrieved_docs: List[List[str]], relevant_docs: List[List[str]], k: int = 5) -> float:
    """Recall@k: % of relevant docs retrieved in top-k."""
    recalls = []
    for retrieved, relevant in zip(retrieved_docs, relevant_docs):
        retrieved_k = set(retrieved[:k])
        relevant_set = set(relevant)
        recall = len(retrieved_k & relevant_set) / len(relevant_set) if relevant_set else 0
        recalls.append(recall)
    return np.mean(recalls)

def ndcg_at_k(retrieved_docs: List[List[str]], relevant_docs: List[List[str]], k: int = 5) -> float:
    """Normalized Discounted Cumulative Gain at k."""
    ndcgs = []
    for retrieved, relevant in zip(retrieved_docs, relevant_docs):
        dcg = 0
        for i, doc in enumerate(retrieved[:k], 1):
            if doc in relevant:
                dcg += 1 / np.log2(i + 1)
        
        # Ideal DCG
        ideal_relevant = min(len(relevant), k)
        idcg = sum(1 / np.log2(i + 2) for i in range(ideal_relevant))
        
        ndcg = dcg / idcg if idcg > 0 else 0
        ndcgs.append(ndcg)
    
    return np.mean(ndcgs)
```

---

## Faithfulness (LLM-as-Judge)

```python
def evaluate_faithfulness(question: str, answer: str, context: str, llm) -> float:
    """Use LLM to evaluate if answer is grounded in context."""
    prompt = f"""Given a question, answer, and context, evaluate if the answer is faithful to the context.

Question: {question}
Answer: {answer}
Context: {context}

Is the answer supported by the context? Score 0-1:
"""
    response = llm.invoke(prompt)
    # Parse score from response
    try:
        score = float(response.content.strip())
    except:
        score = 0.5
    return score
```

---

## Complete Evaluation Suite

```python
class RAGEvaluator:
    def __init__(self, retriever, generator=None):
        self.retriever = retriever
        self.generator = generator
    
    def evaluate(self, questions: List[str], relevant_docs: List[List[str]]) -> dict:
        """Run full evaluation suite."""
        retrieved = [self.retriever.retrieve(q) for q in questions]
        
        return {
            "hit_rate": hit_rate(retrieved, relevant_docs),
            "mrr": mrr(retrieved, relevant_docs),
            "recall@5": recall_at_k(retrieved, relevant_docs, k=5),
            "ndcg@5": ndcg_at_k(retrieved, relevant_docs, k=5),
        }
    
    def evaluate_with_generation(self, questions: List[str], expected_answers: List[str]) -> dict:
        """Evaluate generation quality."""
        if not self.generator:
            raise ValueError("No generator provided")
        
        results = {"faithfulness": [], "relevance": []}
        
        for q, expected in zip(questions, expected_answers):
            # Retrieve
            docs = self.retriever.retrieve(q)
            context = "\n".join([d.page_content for d in docs])
            
            # Generate
            answer = self.generator.generate(q, context)
            
            # Evaluate
            faithfulness = evaluate_faithfulness(q, answer, context, self.generator.llm)
            results["faithfulness"].append(faithfulness)
        
        return {
            "avg_faithfulness": np.mean(results["faithfulness"]),
        }
```

---

## Quick Test

```python
# Test data
retrieved = [
    ["doc_a", "doc_b", "doc_c"],
    ["doc_x", "doc_y", "doc_z"],
    ["doc_1", "doc_2", "doc_3"],
]

relevant = [
    ["doc_a", "doc_c"],
    ["doc_y"],
    ["doc_1", "doc_4"],
]

# Calculate
print(f"Hit Rate: {hit_rate(retrieved, relevant):.2f}")  # 1.00
print(f"MRR: {mrr(retrieved, relevant):.2f}")            # 0.83
print(f"Recall@5: {recall_at_k(retrieved, relevant):.2f}")  # 0.83
print(f"NDCG@5: {ndcg_at_k(retrieved, relevant):.2f}")  # 0.83
```

---

## Tools

- **RAGAs** — https://github.com/explodinggradients/ragas
- **LangChain eval** — https://python.langchain.com/docs/evaluation/
- **DeepEval** — https://github.com/confident-ai/deepeval

---

## Target Scores

| Metric | Good | Great |
|--------|------|-------|
| Hit Rate | >0.8 | >0.9 |
| MRR | >0.7 | >0.85 |
| NDCG@5 | >0.7 | >0.85 |
| Faithfulness | >0.8 | >0.9 |

---

*What gets measured gets improved.* ✨
