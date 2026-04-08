# Vector Database Comparison

## Overview

| DB | Type | Best For | GitHub Stars |
|----|------|----------|--------------|
| **Chroma** | Open-source | Prototyping, small apps | 6k+ |
| **Qdrant** | Open-source | Performance, self-hosted | 9k+ |
| **Weaviate** | Open-source | Hybrid search, OSS flexibility | 8k+ |
| **Milvus** | Open-source | Extreme scale, engineered | 35k+ |
| **Pinecone** | Managed | Fully managed, scale | - |

## Chroma

**Pros:**
- Simple to use, great for prototyping
- Python-first, excellent LangChain integration
- Lightweight, runs in-process
- Free, open-source

**Cons:**
- Not for production at scale
- Limited advanced features
- Single-node only

**Use case:** Quick RAG demos, prototypes, small-scale apps

## Qdrant

**Pros:**
- High performance (10-100ms on 1M-10M vectors)
- Rust-based, memory-efficient
- Excellent filtering capabilities
- Self-hosted or cloud

**Cons:**
- Less mature ecosystem
- Steeper learning curve than Chroma

**Use case:** Production RAG, self-hosted, performance-critical

## Weaviate

**Pros:**
- Native hybrid search (vector + keyword)
- GraphQL API
- Modular, pluggable
- Strong enterprise features

**Cons:**
- More resource-intensive
- Complex setup

**Use case:** Semantic search, hybrid retrieval, enterprise

## Milvus

**Pros:**
- Most mature at scale
- Distributed architecture
- Hardware acceleration
- Cloud-native

**Cons:**
- Complex setup
- Heavy resource requirements

**Use case:** Large-scale vector search, billion-scale

## Pinecone

**Pros:**
- Fully managed, zero ops
- Scales automatically
- Fast, reliable

**Cons:**
- Closed-source, pay for scale
- Vendor lock-in

**Use case:** Enterprise, when you don't want infra management

## Recommendation for LLM Engineering Learning

| Scenario | Recommendation |
|----------|----------------|
| Learning/prototyping | Chroma |
| Production RAG (self-hosted) | Qdrant |
| Hybrid search needs | Weaviate |
| Billion-scale | Milvus |
| No ops, enterprise budget | Pinecone |

**Current setup:** Chroma is already installed and working in RAG chatbot project.
