"""
Ollama Configuration
Shared configuration for both normal and RAG chatbots using Ollama
"""

import os

# --- Ollama Model Configuration ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_LLM_MODEL = "gemma3"  # Google's Gemma3 language model
OLLAMA_EMBEDDING_MODEL = "embeddinggemma"  # Google's embedding model

# --- Model Parameters ---
OLLAMA_MODEL_KWARGS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 512,
    "stream": False
}

# --- Conversation Memory Settings ---
MAX_MEMORY_LENGTH = 20  # Keep last 20 messages (10 exchanges)

# --- Timeout Settings ---
OLLAMA_TIMEOUT = 30  # seconds

# --- Debug Settings ---
OLLAMA_VERBOSE = False  # Set to True for debugging

print(f"🤖 Ollama configuration loaded - LLM: {OLLAMA_LLM_MODEL}, Embeddings: {OLLAMA_EMBEDDING_MODEL}")