# 10 Things I Wish I Knew About LLMs

*Practical lessons from building AI agents and working with Google Research*

---

## 1. LLMs Are Pattern Matchers, Not Reasoners

Don't anthropomorphize. GPT-4 writing careful analysis isn't "thinking" — it's predicting what a careful analysis looks like. The reasoning emerges from next-token prediction trained on human text.

**Why it matters**: When you understand this, you stop expecting logical consistency and start building guards.

---

## 2. The Silicon Ceiling Is Real

I built SIAM because I discovered: LLMs have priors they **cannot override**. 

HTTP 500 = error (99%+ probability from training). Show an LLM an API that returns 500 for success, and it will insist it failed. Single evidence isn't enough.

**Why it matters**: Build middleware that validates and corrects. Don't trust the LLM to figure it out.

---

## 3. Embeddings Are the Data Structure of Meaning

Words become vectors. Similar meanings = similar vectors. But embeddings alone are static.

```
"bank" (river) ≈ "bank" (finance) — static embedding
"bank" in "the bank was steep" ≠ "bank" in "I deposited at the bank" — contextual
```

**Why it matters**: Use transformer embeddings (BERT, etc.) for context-aware search. Word2Vec isn't enough anymore.

---

## 4. Attention Is Just Weighted Sum

The "magic" of transformers is actually simple:

```
For each word:
  - Ask: "What should I pay attention to?" (Query)
  - Each word answers: "Here's what I contain" (Key)
  - Weights = how much Query matches each Key
  - New representation = weighted sum of Values
```

Q × K → weights → V. That's it.

**Why it matters**: Implement attention from scratch. It's easier than you think and unlocks understanding.

---

## 5. Prompt Engineering Has Diminishing Returns

Chain-of-thought, few-shot, role-playing — they help, but there's a ceiling.

The real power moves:
- **Middleware**: Intercept and modify prompts/responses
- **RAG**: Ground answers in your data
- **Agents**: Give the LLM tools, not just tokens

**Why it matters**: Stop optimizing prompts. Start building architecture.

---

## 6. Local Models Are Good Enough Now

Ollama, llama.cpp, GPTQ — you can run capable models on a laptop.

phi3 (2.2GB), llama3 (4GB), codellama — enough for:
- Testing prompts
- RAG pipelines
- Agent prototypes

**Why it matters**: Experiment without API costs. Data never leaves your machine.

---

## 7. Vector Databases Aren't Optional

At scale, naive similarity search is too slow. FAISS, Pinecone, Weaviate — they index embeddings for fast retrieval.

For RAG with 1000+ docs: you need a vector DB.
For RAG with 100 docs: FAISS is fine.

**Why it matters**: Choose the right tool for your scale.

---

## 8. Evaluation Is the Hardest Part

How do you know your RAG is working? Your agent is reliable?

Metrics:
- **RAG**: Hit rate, MRR, answer quality (LLM-as-judge)
- **Agents**: Task completion %, human feedback

Build evals first. Then iterate.

---

## 9. The API Abstraction Leak

LangChain, LlamaIndex, AutoGen — they abstract the LLM. But the abstractions leak.

- Different models need different prompts
- Same prompt = different outputs across models
- Rate limits, timeouts, costs vary

**Why it matters**: Don't over-abstract. Understand what's happening under the hood.

---

## 10. Research + Engineering = Unbeatable

I collaborated with Google Research on SIAM. They provided the academic framing; we provided the implementation.

Academic papers → rigorous foundations
Engineering → shipped products

Neither alone is as powerful.

**Why it matters**: Read papers. Talk to researchers. Build things. Combine both.

---

## TL;DR

1. LLMs are pattern matchers
2. Some priors can't be overridden (Silicon Ceiling)
3. Use contextual embeddings
4. Attention is weighted sums
5. Architecture > prompts
6. Local models are ready
7. Vector databases matter at scale
8. Evaluation is hard but necessary
9. Abstractions leak — understand the fundamentals
10. Research + Engineering wins

---

*The more I learn about LLMs, the more I realize how much I don't know. But these 10 things would have saved me months.* ✨

#AI #LLM #Engineering #MachineLearning
