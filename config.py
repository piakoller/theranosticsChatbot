# OpenRouter and LLM configuration for IAEA Chatbot
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

LLM_TEMPERATURE = 0.1  # Slightly higher for more natural responses
MAX_TOKENS = 500  # Reduced for faster responses - still good for most queries
NUM_CTX = 4096  # Smaller context window for faster processing
MODEL_KWARGS = {
    "temperature": LLM_TEMPERATURE,
    "max_tokens": MAX_TOKENS,
    "top_p": 0.9,  # Nucleus sampling for better quality
    "frequency_penalty": 0.1,  # Reduce repetition
    "presence_penalty": 0.1,  # Encourage diverse topics
}

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model configuration with fallback options
PRIMARY_MODEL = "google/gemma-3-27b-it:free"
BACKUP_MODELS = [
    "qwen/qwen-2.5-coder-32b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "microsoft/phi-3.5-mini-128k-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free"
]

# Current active model (will be updated if fallback is needed)
OPENROUTER_MODEL = PRIMARY_MODEL
DEFAULT_OPENROUTER_MODEL = PRIMARY_MODEL
