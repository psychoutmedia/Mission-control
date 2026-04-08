#!/usr/bin/env python3
"""
RAG Chatbot with Chroma Vector Database

A RAG chatbot using Chroma for persistent vector storage.
Based on ollama_rag.py but with Chroma backend.
"""

import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

# LangChain components
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Ollama LLM
from langchain_community.chat_models import ChatOllama

from langchain_core.documents import Document


@dataclass
class ChromaRAGChatbot:
    """RAG chatbot using Chroma for vector storage."""
    
    knowledge_path: str
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model: str = "phi3"
    chroma_path: str = "projects/rag_chatbot/knowledge/chroma_db"
    vectorstore: Optional[Chroma] = None
    chunk_size: int = 500
    chunk_overlap: int = 50
    llm_temperature: float = 0.7
    conversation_history: List[tuple] = None
    max_history_turns: int = 5
    
    def __post_init__(self):
        """Initialize embeddings and LLM."""
        self.conversation_history = []
        
        print(f"🤖 Loading embedding model: {self.embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={'device': 'cpu'}
        )
        
        print(f"🧠 Loading Ollama model: {self.llm_model}")
        self.llm = ChatOllama(
            model=self.llm_model,
            temperature=self.llm_temperature
        )
    
    def load_knowledge(self, force_rebuild: bool = False):
        """Load documents and build Chroma vector store."""
        knowledge_dir = Path(self.knowledge_path)
        chroma_path = Path(self.chroma_path)
        
        # Check for existing Chroma DB
        if chroma_path.exists() and not force_rebuild:
            print(f"📂 Loading existing Chroma DB from {chroma_path}")
            self.vectorstore = Chroma(
                persist_directory=str(chroma_path),
                embedding_function=self.embeddings
            )
            print(f"✅ Loaded {self.vectorstore._collection.count()} documents")
            return
        
        # Load documents
        print(f"📄 Loading documents from {knowledge_dir}")
        try:
            loader = DirectoryLoader(
                str(knowledge_dir),
                glob="**/*.md",
                loader_cls=TextLoader
            )
            documents = loader.load()
        except Exception as e:
            print(f"⚠️ Error loading documents: {e}")
            print("Creating sample knowledge base...")
            documents = self._create_sample_knowledge()
        
        # Split into chunks
        print(f"✂️  Splitting {len(documents)} documents into chunks...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        chunks = splitter.split_documents(documents)
        
        # Filter out empty chunks
        chunks = [chunk for chunk in chunks if chunk.page_content.strip()]
        print(f"📝 Created {len(chunks)} chunks (after filtering empty)")
        
        # Build Chroma vectorstore
        print(f"🧠 Building Chroma vectorstore...")
        chroma_path.mkdir(parents=True, exist_ok=True)
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=str(chroma_path)
        )
        
        print(f"💾 Saved Chroma DB to {chroma_path}")
        print(f"✅ Collection has {self.vectorstore._collection.count()} documents")
    
    def _create_sample_knowledge(self) -> List[Document]:
        """Create sample knowledge base if none exists."""
        sample_docs = []
        
        automa_content = """
# Automa Dynamics

Automa Dynamics is an AI company building autonomous systems.
Our mission: "We don't build tools. We build capabilities."

We have five divisions:
- Helios: Humanoid robotics for dangerous/dull work
- Prometheus: Enterprise AI, Large Cognitive Models
- Aegis: Extreme environments (undersea, orbital, lunar)
- Chorus: Brain-computer interfaces
- Gaia: Autonomous ecosystems (buildings, cities)

Founded 2026 by Mark Stephenson.
"""
        
        siam_content = """
# SIAM - Self-healing Intelligent Agent Middleware

SIAM detects inverted API responses (HTTP 500 = success)
and heals them using ontological memory.

Key results:
- 500→200 response healing
- Fleet-wide pattern broadcasting
- Validated by Google Research

The "Silicon Ceiling" problem: LLMs can't override training priors.
"""
        
        sample_docs.append(Document(
            page_content=automa_content,
            metadata={"source": "about_automa.md"}
        ))
        sample_docs.append(Document(
            page_content=siam_content,
            metadata={"source": "siam_research.md"}
        ))
        
        return sample_docs
    
    def retrieve(self, query: str, k: int = 4) -> List[Document]:
        """Retrieve top-k relevant documents."""
        if not self.vectorstore:
            raise ValueError("Call load_knowledge() first")
        
        docs = self.vectorstore.similarity_search(query, k=k)
        return docs
    
    def retrieve_with_score(self, query: str, k: int = 4) -> List[tuple]:
        """Retrieve documents with relevance scores."""
        if not self.vectorstore:
            raise ValueError("Call load_knowledge() first")
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results
    
    def _build_history_context(self) -> str:
        """Build context string from conversation history."""
        if not self.conversation_history:
            return ""
        
        history_lines = ["\n\nPrevious conversation:"]
        for q, a in self.conversation_history[-self.max_history_turns:]:
            history_lines.append(f"User: {q}")
            history_lines.append(f"Assistant: {a}")
        
        return "\n".join(history_lines)
    
    def add_to_history(self, question: str, answer: str):
        """Add a question-answer pair to conversation history."""
        self.conversation_history.append((question, answer))
        if len(self.conversation_history) > self.max_history_turns * 2:
            self.conversation_history = self.conversation_history[-self.max_history_turns:]
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def answer(self, question: str, k: int = 4) -> str:
        """Answer a question using RAG with Chroma + Ollama."""
        docs = self.retrieve(question, k=k)
        
        if not docs:
            return "I don't have enough information to answer that."
        
        context = "\n\n".join(d.page_content for d in docs)
        history_context = self._build_history_context()
        
        prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question.

Context:
{context}
{history_context}

Question: {question}

Answer:"""
        
        try:
            response = self.llm.invoke(prompt)
            answer = response.content if hasattr(response, 'content') else str(response)
            self.add_to_history(question, answer)
            return answer
        except Exception as e:
            return f"Error generating response: {e}\n\nContext:\n{context}"
    
    def get_collection_info(self) -> dict:
        """Get info about the Chroma collection."""
        if not self.vectorstore:
            return {"error": "No vectorstore loaded"}
        
        return {
            "count": self.vectorstore._collection.count(),
            "path": self.chroma_path,
            "embedding_model": self.embedding_model
        }


# ─────────────────────────────────────────────────────────────
# Demo Usage
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    chatbot = ChromaRAGChatbot(
        knowledge_path="projects/rag_chatbot/knowledge",
        chroma_path="projects/rag_chatbot/knowledge/chroma_db",
        llm_model="phi3"
    )
    
    print("\n" + "="*60)
    print("🤖 RAG Chatbot with Chroma + Ollama")
    print("="*60)
    print(f"Model: {chatbot.llm_model}")
    print(f"Embeddings: {chatbot.embedding_model}")
    print(f"Chroma DB: {chatbot.chroma_path}")
    print("="*60 + "\n")
    
    chatbot.load_knowledge()
    
    # Show collection info
    info = chatbot.get_collection_info()
    print(f"\n📊 Collection Info: {info}\n")
    
    questions = [
        "What is Automa Dynamics?",
        "What problem does SIAM solve?",
    ]
    
    print("\n" + "="*60)
    print("Try asking questions:")
    for q in questions:
        print(f"  - {q}")
    print("="*60 + "\n")
    
    print("Enter questions (or 'quit' to exit, 'clear' to reset history):\n")
    while True:
        try:
            question = input("❓ ").strip()
            if question.lower() in ['quit', 'exit', 'q']:
                break
            if question.lower() == 'clear':
                chatbot.clear_history()
                print("🗑️  History cleared.\n")
                continue
            if not question:
                continue
            
            print("\n🤔 Thinking...")
            answer = chatbot.answer(question, k=3)
            print(f"\n📚 Answer:\n{answer}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n👋 Goodbye!")
