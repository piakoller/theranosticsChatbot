# Patient Education Chatbot Study

A simplified application for testing the effectiveness of chatbots in patient education, specifically focused on theranostics treatments.

## Overview

This study application tests how well chatbots can provide patient education about theranostics treatments. Participants go through a simple 3-step process:

1. **Demographics**: Basic information collection
2. **Chatbot Interaction**: Interactive conversation with the patient education chatbot
3. **Feedback**: Evaluation of the chatbot's usefulness, accuracy, and trustworthiness

## Quick Start

```bash
python app.py
```

The application will launch at `http://127.0.0.1:7860`

## File Structure

- `app.py` - Main application file
- `chatbot.py` - Chatbot functionality and AI integration
- `config.py` - Configuration settings
- `logging_module.py` - Data logging and session management
- `mongodb_handler.py` - Database connectivity and data storage

## Features

- ✅ Simple, linear study flow (no navigation issues)
- ✅ Real-time chatbot interaction
- ✅ Automatic data collection and MongoDB storage
- ✅ Question tracking and minimum interaction requirements
- ✅ Comprehensive feedback collection
- ✅ Clean, responsive UI

## Study Data

All study data is automatically saved to MongoDB including:
- Participant demographics
- Complete conversation history
- Feedback ratings and comments
- Session tracking and timestamps

## Requirements

- Python 3.7+
- Gradio
- PyMongo (for MongoDB integration)
- Internet connection (for AI model access)

---

*Simplified and focused on patient education research*
