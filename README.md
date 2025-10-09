---
title: Patient Education Chatbot Study
emoji: 🩺
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
tags:
  - healthcare
  - chatbot
  - patient-education
  - theranostics
  - medical-ai
  - user-study
short_description: Interactive study platform for testing chatbot effectiveness in patient education
---

# Patient Education Chatbot Study

A simplified application for testing the effectiveness of chatbots in patient education, specifically focused on theranostics treatments.

## Overview

This study application tests how well chatbots can provide patient education about theranostics treatments. Participants go through a simple 3-step process:

1. **Demographics**: Basic information collection
2. **Chatbot Interaction**: Interactive conversation with the patient education chatbot  
3. **Feedback**: Evaluation of the chatbot's usefulness, accuracy, and trustworthiness

## Quick Start

The application launches automatically on Hugging Face Spaces. For local development:

```bash
python app.py
```

The application will launch at `http://127.0.0.1:7860`

## Architecture

### Modular Design
- `app.py` - Main application entry point (55 lines)
- `study_config.py` - Configuration constants and settings
- `study_sections.py` - UI section creation functions  
- `study_handlers.py` - Event handlers and business logic
- `study_utils.py` - Utility functions and helpers
- `chatbot.py` - Chatbot functionality and AI integration
- `config.py` - API keys and model configuration
- `logging_module.py` - Data logging and session management
- `mongodb_handler.py` - Database connectivity and data storage

## Features

- ✅ Simple, linear study flow (no navigation issues)
- ✅ Real-time chatbot interaction with OpenRouter API
- ✅ Automatic data collection and MongoDB storage
- ✅ Question tracking and minimum interaction requirements
- ✅ Comprehensive feedback collection with rating scales
- ✅ Clean, responsive UI with Enter key support
- ✅ Modular, maintainable code architecture
- ✅ Session management and unique participant tracking

## Study Data

All study data is automatically saved to MongoDB including:
- Participant demographics (age, gender, education, medical background)
- Complete conversation history with timestamps
- Feedback ratings (usefulness, accuracy, ease of use, trust)
- Suggested improvements and overall comments
- Session tracking and interaction metadata

## Technology Stack

- **Frontend**: Gradio (Python web framework)
- **AI Integration**: OpenRouter API with multiple model support
- **Database**: MongoDB for data persistence
- **Deployment**: Hugging Face Spaces
- Internet connection (for AI model access)

---

*Simplified and focused on patient education research*
