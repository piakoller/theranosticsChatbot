# API Documentation

## Core Components

### Chatbot Classes

#### TheranosticsBot
Normal conversational chatbot with memory.

```python
from src.core.chatbot import TheranosticsBot

bot = TheranosticsBot()
response = bot.chat("What is theranostics?")
```

#### RAG Engine
Expert chatbot with document retrieval capabilities.

```python
from src.core.rag_engine import get_rag_chatbot

rag_bot = get_rag_chatbot()
response = rag_bot.chat("Explain side effects", mode="expert")
```

### Database Operations

#### MongoDBHandler
Handles all database operations including conversation logging and form submissions.

```python
from src.database.mongodb_handler import MongoDBHandler

db = MongoDBHandler()
db.log_conversation(
    user_message="Question",
    bot_response="Answer",
    user_id="user123",
    chatbot_type="normal",
    metadata={"questiontype": "predefined"}
)
```

### Configuration

#### Settings
Main application configuration in `src/config/settings.py`

#### Ollama Config
LLM model configuration in `src/config/ollama_config.py`

## Study Framework

### Sections
UI components for different study phases:
- Consent section
- Demographics collection
- Chatbot interaction
- Feedback collection

### Handlers
Event handlers for user interactions:
- Form submissions
- Chatbot conversations
- Question handling

### Configuration
Study-specific settings including:
- Predefined questions
- UI styling
- Survey options

## Data Models

### Conversation Document
```json
{
  "user_id": "string",
  "conversation_history": [
    {
      "timestamp": "datetime",
      "user_message": "string",
      "bot_response": "string",
      "chatbot_type": "normal|expert",
      "questiontype": "predefined|follow_up|manual",
      "question_number": "integer"
    }
  ],
  "total_exchanges": "integer",
  "created_at": "datetime",
  "last_updated": "datetime"
}
```

### Form Document
```json
{
  "user_id": "string",
  "form_type": "demographics|feedback|consent",
  "form_data": "object",
  "chatbot_type": "normal|expert",
  "timestamp": "datetime"
}
```

## Error Handling

The application includes comprehensive error handling:
- Graceful fallbacks for missing dependencies
- MongoDB connection error recovery
- Ollama service availability checks
- File system error handling

## Logging

Multiple logging levels available:
- Console output for development
- File logging (optional)
- MongoDB logging (default)
- Error tracking and reporting