FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY projects/rag_chatbot/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY projects/rag_chatbot /app/rag_chatbot

# Set environment variables
ENV OLLAMA_HOST=127.0.0.1:11434
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden)
CMD ["uvicorn", "projects.rag_chatbot.api:app", "--host", "0.0.0.0", "--port", "8000"]
