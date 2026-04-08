#!/usr/bin/env python3
"""
FastAPI Server for RAG Chatbot

Run with: uvicorn api:app --reload --port 8000
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chroma_rag import ChromaRAGChatbot

# Initialize app
app = FastAPI(
    title="RAG Chatbot API",
    description="Local LLM-powered chatbot with RAG",
    version="1.0.0"
)

# Initialize chatbot (singleton)
chatbot: Optional[ChromaRAGChatbot] = None


@app.on_event("startup")
async def startup_event():
    """Initialize chatbot on startup."""
    global chatbot
    print("🤖 Initializing RAG Chatbot...")
    chatbot = ChromaRAGChatbot(
        knowledge_path="projects/rag_chatbot/knowledge",
        chroma_path="projects/rag_chatbot/knowledge/chroma_db",
        llm_model="phi3"
    )
    chatbot.load_knowledge()
    print(f"✅ Loaded {chatbot.get_collection_info().get('count', 0)} documents")


# ─────────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str
    k: int = 4


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    conversation_length: int


class HealthResponse(BaseModel):
    status: str
    documents_loaded: int
    model: str


# ─────────────────────────────────────────────────────────────
# API Endpoints
# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Chatbot API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health():
    """Health check endpoint."""
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    info = chatbot.get_collection_info()
    return HealthResponse(
        status="healthy",
        documents_loaded=info.get("count", 0),
        model=chatbot.llm_model
    )


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(request: ChatRequest):
    """
    Chat endpoint.
    
    Send a question and get an answer with RAG context.
    """
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        # Get answer
        answer = chatbot.answer(request.question, k=request.k)
        
        # Get sources
        docs = chatbot.retrieve(request.question, k=request.k)
        sources = [d.page_content[:200] + "..." for d in docs]
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            conversation_length=len(chatbot.conversation_history)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search", tags=["search"])
async def search(q: str, k: int = 4):
    """
    Search the knowledge base.
    
    Returns relevant documents without generating a response.
    """
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        docs = chatbot.retrieve(q, k=k)
        return {
            "query": q,
            "results": [
                {
                    "content": d.page_content,
                    "source": d.metadata.get("source", "unknown")
                }
                for d in docs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear", tags=["conversation"])
async def clear_history():
    """Clear conversation history."""
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    chatbot.clear_history()
    return {"message": "Conversation history cleared"}


@app.get("/conversation", tags=["conversation"])
async def get_conversation():
    """Get conversation history."""
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    return {
        "history": [
            {"question": q, "answer": a}
            for q, a in chatbot.conversation_history
        ],
        "length": len(chatbot.conversation_history)
    }


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
