# OpenRouter and LLM configuration for IAEA Chatbot
import os

# Try to load environment variables from .env file (for local development)
try:
    from dotenv import load_dotenv
    # Look for .env in parent directory (IAEA Chatbot folder)
    parent_env = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(parent_env):
        load_dotenv(parent_env)
    else:
        load_dotenv()  # Fallback to current directory
except ImportError:
    # dotenv not available (e.g., in HuggingFace Spaces) - use environment variables directly
    print("⚠️  python-dotenv not installed. Using environment variables directly.")

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
PRIMARY_MODEL = "openai/gpt-oss-20b:free"
BACKUP_MODELS = [
    "google/gemma-3-27b-it:free",
    "qwen/qwen-2.5-coder-32b-instruct:free",
    "google/gemini-2.0-flash-exp:free"
]

# Current active model (will be updated if fallback is needed)
OPENROUTER_MODEL = PRIMARY_MODEL
DEFAULT_OPENROUTER_MODEL = PRIMARY_MODEL

# User Study Configuration
# Section order for the Theranostics Chatbot User Study
SECTION_ORDER = ['A', 'B', 'C', 'D', 'E', 'F']
