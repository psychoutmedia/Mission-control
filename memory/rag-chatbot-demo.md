# RAG Chatbot Demo — Local Embeddings with LangChain

> Mini-Project | Created: 2026-03-06

A working RAG (Retrieval-Augmented Generation) chatbot using local embeddings — no API calls needed.

---

## What is RAG?

RAG combines:
1. **Retrieval**: Find relevant documents from a knowledge base
2. **Augmentation**: Inject those docs into the LLM prompt
3. **Generation**: LLM generates answer grounded in your data

```
User: "What did we research about transformers?"
    │
    ▼
┌─────────────────────────────────────┐
│  1. Embed user question             │
│  2. Search vector DB for similarity │
│  3. Retrieve top-k documents        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  4. Build prompt:                  │
│     Context: [retrieved docs]       │
│     Question: [user question]       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  5. Generate answer with LLM        │
└─────────────────────────────────────┘
    │
    ▼
Answer: "Transformers are..."
```

---

## Project Structure

```
projects/
└── rag_chatbot/
    ├── chatbot.py        # Main RAG chatbot
    ├── knowledge/        # Your documents
    │   └── *.txt
    └── embeddings/       # Cached embeddings
```

---

## Install Dependencies

```bash
pip install langchain langchain-community langchain-openai \
    sentence-transformers faiss-cpu \
    tiktoken python-docx
```

For Apple Silicon (M1/M2/M3):
```bash
pip install langchain langchain-community \
    sentence-transformers faiss-cpu \
    tiktoken python-docx
```

---

## Step 1: Create Knowledge Base

Create `projects/rag_chatbot/knowledge/` and add text files:

**about_automa.md**:
```markdown
# Automa Dynamics

Automa Dynamics is an AI company building autonomous systems.
Our mission: "We don't build tools. We build capabilities."

We have five divisions:
- Helios: Humanoid robotics
- Prometheus: Enterprise AI
- Aegis: Extreme environments
- Chorus: Neural integration
- Gaia: Autonomous ecosystems

Founded 2026 by Mark Stephenson.
```

**siam_research.md**:
```markdown
# SIAM - Self-healing Intelligent Agent Middleware

SIAM detects inverted API responses (HTTP 500 = success)
and heals them using ontological memory.

Key results:
- 500→200 response healing
- Fleet-wide pattern broadcasting
- Validated by Google Research

The "Silicon Ceiling" problem: LLMs can't override training priors.
```

---

## Step 2: The RAG Chatbot Code

Save as `projects/rag_chatbot/chatbot.py`:

```python
#!/usr/bin/env python3
"""
Local RAG Chatbot with LangChain
Uses sentence-transformers for embeddings + FAISS for vector search
"""

import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

# LangChain components
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# For generation (swap in your preferred LLM)
from langchain_openai import ChatOpenAI
# Or for local LLMs:
# from langchain_community.chat_models import ChatOllama


@dataclass
class RAGChatbot:
    """RAG chatbot with local embeddings."""
    
    knowledge_path: str
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vectorstore: Optional[FAISS] = None
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    def __post_init__(self):
        """Initialize embeddings and vectorstore."""
        print(f"🤖 Loading embedding model: {self.embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={'device': 'cpu'}  # or 'mps' for Apple Silicon
        )
        
    def load_knowledge(self, force_rebuild: bool = False):
        """Load documents and build vector store."""
        knowledge_dir = Path(self.knowledge_path)
        
        # Check for existing vectorstore
        index_path = knowledge_dir / "vectorstore"
        if index_path.exists() and not force_rebuild:
            print(f"📂 Loading existing vectorstore from {index_path}")
            self.vectorstore = FAISS.load_local(
                str(index_path), 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return
        
        # Load documents
        print(f"📄 Loading documents from {knowledge_dir}")
        loader = DirectoryLoader(
            str(knowledge_dir),
            glob="**/*.md",
            loader_cls=TextLoader
        )
        documents = loader.load()
        
        # Split into chunks
        print(f"✂️  Splitting {len(documents)} documents into chunks...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        chunks = splitter.split_documents(documents)
        print(f"📝 Created {len(chunks)} chunks")
        
        # Build vectorstore
        print(f"🧠 Building vectorstore with {self.embedding_model}...")
        self.vectorstore = FAISS.from_documents(
            chunks, 
            self.embeddings
        )
        
        # Save for later
        index_path.mkdir(parents=True, exist_ok=True)
        self.vectorstore.save_local(str(index_path))
        print(f"💾 Saved vectorstore to {index_path}")
    
    def retrieve(self, query: str, k: int = 4) -> List[Document]:
        """Retrieve top-k relevant documents."""
        if not self.vectorstore:
            raise ValueError("Call load_knowledge() first")
        
        docs = self.vectorstore.similarity_search(query, k=k)
        return docs
    
    def answer(
        self, 
        question: str, 
        k: int = 4,
        llm: Optional[object] = None
    ) -> str:
        """
        Answer a question using RAG.
        
        Args:
            question: User's question
            k: Number of docs to retrieve
            llm: LangChain LLM instance (optional)
        
        Returns:
            Answer string
        """
        # Retrieve relevant docs
        docs = self.retrieve(question, k=k)
        
        if not docs:
            return "I don't have enough information to answer that."
        
        # Build context from retrieved docs
        context = "\n\n".join(d.page_content for d in docs)
        
        # If no LLM provided, return context + question (for debugging)
        if llm is None:
            return f"📚 Retrieved {len(docs)} relevant documents:\n\n{context}\n\n❓ Question: {question}"
        
        # Build prompt
        prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question.

Context:
{context}

Question: {question}

Answer:"""
        
        # Generate response
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)


# ─────────────────────────────────────────────────────────────
# Demo Usage
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Initialize chatbot
    chatbot = RAGChatbot(knowledge_path="projects/rag_chatbot/knowledge")
    chatbot.load_knowledge()
    
    # Example questions to ask
    questions = [
        "What is Automa Dynamics?",
        "What problem does SIAM solve?",
        "Tell me about the Silicon Ceiling.",
        "What divisions does Automa Dynamics have?",
    ]
    
    print("\n" + "="*60)
    print("🤖 RAG Chatbot Demo")
    print("="*60)
    
    for q in questions:
        print(f"\n❓ {q}")
        print("-" * 40)
        answer = chatbot.answer(q, k=3)
        print(answer)
        print()
```

---

## Step 3: Run the Demo

```bash
cd ~/clawd
python projects/rag_chatbot/chatbot.py
```

Expected output:
```
🤖 Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
📂 Loading existing vectorstore from projects/rag_chatbot/knowledge/vectorstore

============================================================
🤖 RAG Chatbot Demo
============================================================

❓ What is Automa Dynamics?
----------------------------------------
Automa Dynamics is an AI company building autonomous systems...
(answer generated from your knowledge base)
```

---

## Step 4: Add an LLM (Optional)

For actual generation, add an LLM:

```python
# With OpenAI
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4", temperature=0)
answer = chatbot.answer("What is SIAM?", llm=llm)

# Or with Ollama (local)
from langchain_community.chat_models import ChatOllama

llm = ChatOllama(model="llama3")
answer = chatbot.answer("What is SIAM?", llm=llm)
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      USER QUESTION                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              1. Embed Question (Sentence-Transformers)      │
│                 "What is SIAM?" → [0.2, -0.1, ...]        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              2. Vector Search (FAISS)                      │
│         Find k most similar document chunks                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              3. Build Prompt                                │
│  Context: [retrieved chunks]                               │
│  Question: "What is SIAM?"                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              4. Generate (LLM)                             │
│         Answer grounded in your data                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    Answer: "SIAM is..."
```

---

## Key Components Explained

| Component | Technology | Purpose |
|-----------|------------|---------|
| Embeddings | sentence-transformers | Convert text to vectors |
| Vector Store | FAISS | Fast similarity search |
| Document Loader | LangChain | Read files from disk |
| Text Splitter | RecursiveCharacterTextSplitter | Chunk documents |
| LLM | OpenAI/Ollama | Generate answers |

---

## Variations & Extensions

### 1. Use Different Embeddings

```python
# More powerful embeddings
model = "sentence-transformers/all-mpnet-base-v2"  # 768-dim

# Or OpenAI embeddings
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
```

### 2. Add More Data Sources

```python
# PDF files
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("document.pdf")
docs = loader.load()

# Web pages
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://example.com")
docs = loader.load()
```

### 3. Hybrid Search

Combine semantic search with keyword search:

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# ... setup base retriever ...
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever
)
```

---

## Production Considerations

1. **Update knowledge**: Re-run `load_knowledge(force_rebuild=True)` when docs change
2. **Caching**: Embeddings are cached in `vectorstore/` folder
3. **Scaling**: FAISS → Pinecone/Weaviate for millions of docs
4. **Evaluation**: Track retrieval quality (hit rate, MRR)

---

## Next Steps for This Project

- [ ] Add more knowledge base documents
- [ ] Swap to GPT-4 or Ollama for generation
- [ ] Add web search (Tavily/SerpAPI) for hybrid RAG
- [ ] Deploy as API (FastAPI + LangServe)
- [ ] Add conversation history (memory)

---

*This chatbot runs entirely locally. Your data never leaves your machine.* ✨
