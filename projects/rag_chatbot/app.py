#!/usr/bin/env python3
"""
Streamlit Web UI for RAG Chatbot

Run with: streamlit run app.py
"""

import streamlit as st
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chroma_rag import ChromaRAGChatbot


# Page config
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)


@st.cache_resource
def get_chatbot():
    """Initialize chatbot (cached)."""
    return ChromaRAGChatbot(
        knowledge_path="knowledge",
        chroma_path="knowledge/chroma_db",
        llm_model="phi3"
    )


def main():
    st.title("🤖 RAG Chatbot")
    st.markdown("**Local LLM + Chroma Vector DB**")
    
    # Initialize
    chatbot = get_chatbot()
    
    # Load knowledge
    with st.spinner("Loading knowledge base..."):
        chatbot.load_knowledge()
    
    # Show info
    info = chatbot.get_collection_info()
    st.sidebar.markdown("### 📊 Collection Info")
    st.sidebar.write(f"Documents: {info.get('count', 0)}")
    st.sidebar.write(f"Model: {chatbot.llm_model}")
    
    # Chat interface
    st.markdown("---")
    st.markdown("### 💬 Ask me anything")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chatbot.answer(prompt, k=3)
            st.markdown(response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Clear history button
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []
        chatbot.clear_history()
        st.rerun()


if __name__ == "__main__":
    main()
