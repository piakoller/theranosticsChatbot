"""
Chatbot Module
Handles OpenRouter API integration and response generation for the Theranostics Chatbot
"""

import requests
import random
from config import (
    MODEL_KWARGS,
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
    OPENROUTER_MODEL,
    PRIMARY_MODEL,
    BACKUP_MODELS,
)
from logging_module import conversation_logger


class TheranosticsBot:
    """Main chatbot class for handling AI responses"""
    
    def __init__(self):
        self.current_model = OPENROUTER_MODEL
        self.openrouter_available = self._check_openrouter_key()
        conversation_logger.set_current_model(self.current_model)
    
    def _check_openrouter_key(self):
        """Check if OpenRouter API key is available"""
        if not OPENROUTER_API_KEY:
            print("❌ OPENROUTER_API_KEY not set in environment variables.")
            return False
        return True
    
    def _get_system_prompt(self, lang='en'):
        """Get the system prompt for patient education, language-aware.

        lang: 'en' or 'de'
        """
        if lang == 'de':
            return (
                "Sie sind ein mitfühlender KI-Assistent, spezialisiert auf Patientenaufklärung zu Theranostik und Nuklearmedizin. "
                "Erklären Sie medizinische Konzepte verständlich, beruhigend und in Alltagssprache.\n\n"
                "Kommunikationsrichtlinien:\n"
                "1. Halten Sie Antworten kurz und klar (1-3 Sätze für einfache Fragen).\n"
                "2. Vermeiden Sie Fachjargon; erklären Sie Begriffe einfach.\n"
                "3. Seien Sie einfühlsam und beruhigend.\n"
                "4. Bei komplexen Themen: kurze Übersicht geben und fragen, ob eine detailliertere Erklärung gewünscht ist.\n"
                "5. Schließen Sie mit einer Einladung zu Nachfragen (z. B. 'Möchten Sie, dass ich einen bestimmten Teil genauer erkläre?').\n"
                "6. Erinnern Sie daran, dass spezifische medizinische Fragen mit dem Behandlungsteam besprochen werden sollten.\n\n"
                "Antwortstil: Kurz, klar, mit 1–2 wichtigen Punkten; immer zum Nachfragen einladen."
            )
        else:
            return (
                "You are a compassionate AI assistant specializing in patient education about theranostics and nuclear medicine. "
                "Help patients understand medical concepts in simple, reassuring terms.\n\n"
                "Communication Guidelines:\n"
                "1. Keep answers concise (1-3 sentences for simple questions).\n"
                "2. Use simple language; avoid jargon.\n"
                "3. Be reassuring and empathetic.\n"
                "4. For complex topics: give a brief overview, then offer more detail if requested.\n"
                "5. End by inviting follow-up questions.\n"
                "6. Remind users to discuss specific medical concerns with their healthcare team.\n\n"
                "Response style: short, clear, 1–2 key points, encourage follow-up."
            )
    
    def generate_openrouter_response(self, message, history, context="main_chat", section=None, lang='en'):
        """Generate response using OpenRouter API with automatic fallback to backup models"""
        
        # List of models to try (current active model first, then backups)
        models_to_try = [self.current_model] + [m for m in BACKUP_MODELS if m != self.current_model]
        first_model_failed = False  # Track if we need to inform user about issues
        
        for i, model in enumerate(models_to_try):
            try:
                # Prepare conversation context with enhanced message formatting
                # Build system prompt according to requested language
                messages = [
                    {"role": "system", "content": self._get_system_prompt(lang=lang)}
                ]
                if history:
                    # Include more context (last 5 exchanges instead of 3)
                    recent_history = history[-10:] if len(history) > 10 else history  # Get last 10 messages (5 exchanges)
                    for msg in recent_history:
                        if msg["role"] in ["user", "assistant"]:
                            messages.append(msg)
                
                # If German requested, add an explicit instruction to reply only in German
                if lang == 'de':
                    messages.append({"role": "system", "content": "Please respond only in German (Deutsch)."})

                # Enhance the user's question with context if it's too brief
                enhanced_message = message
                if len(message.split()) < 5:  # If question is very short
                    enhanced_message = f"Please provide a comprehensive explanation about: {message}"
                
                messages.append({"role": "user", "content": enhanced_message})

                payload = {
                    "model": model,
                    "messages": messages,
                    **MODEL_KWARGS
                }
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://openrouter.ai/",
                    "X-Title": "Theranostics Chatbot"
                }
                response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Try to extract the response with error handling
                    try:
                        assistant_response = result["choices"][0]["message"]["content"].strip()
                    except KeyError as e:
                        # Try alternative response formats
                        if 'message' in result:
                            assistant_response = result['message'].get('content', '')
                        elif 'response' in result:
                            assistant_response = result['response']
                        elif 'text' in result:
                            assistant_response = result['text']
                        else:
                            raise Exception(f"Unknown response format for model {model}")
                    
                    if not assistant_response:
                        assistant_response = "I understand your question. Could you please provide more details so I can give you a more specific answer?"
                    
                    # If we're using a backup model, update the current model and inform user
                    if i > 0 and model != self.current_model:
                        self.current_model = model
                        conversation_logger.set_current_model(model)
                        print(f"✅ Switched to backup model: {model}")
                        # Add a brief notice to the response for users
                        model_name = model.split('/')[-1].replace(':free', '').replace('-', ' ').title()
                        assistant_response = f"*I've switched to a backup model ({model_name}) to ensure I can help you.*\n\n{assistant_response}"
                    
                    # Log the conversation
                    conversation_logger.log_conversation(message, assistant_response, context=context, section=section, model_used=model, metadata={"lang": lang})
                    
                    return assistant_response
                else:
                    # Enhanced error handling for specific error types
                    try:
                        error_data = response.json() if response.text else {}
                        error_message = error_data.get('error', {}).get('message', '')
                        error_code = error_data.get('error', {}).get('code', response.status_code)
                        
                        # Check for specific error conditions that warrant fallback
                        should_fallback = False
                        error_reason = ""
                        
                        if response.status_code == 429:
                            should_fallback = True
                            error_reason = "rate-limited"
                        elif response.status_code == 503:
                            should_fallback = True
                            error_reason = "service unavailable"
                        elif "rate-limited" in error_message.lower():
                            should_fallback = True
                            error_reason = "rate-limited upstream"
                        elif "no instances available" in error_message.lower():
                            should_fallback = True
                            error_reason = "no instances available"
                        elif "provider returned error" in error_message.lower():
                            should_fallback = True
                            error_reason = "provider error"
                        elif response.status_code >= 500:
                            should_fallback = True
                            error_reason = "server error"
                        
                        print(f"❌ Model {model} error ({response.status_code}): {error_reason}")
                        if error_message:
                            print(f"   Details: {error_message[:200]}...")
                        
                        if should_fallback and i < len(models_to_try) - 1:
                            # Mark that we had issues with the primary model
                            if i == 0:
                                first_model_failed = True
                            print(f"🔄 Trying backup model: {models_to_try[i+1]}")
                            continue
                        elif not should_fallback:
                            # For non-fallback errors, return specific message
                            return f"I encountered an issue with the language model. Please try again or contact support if this persists."
                        else:
                            # All models failed
                            if first_model_failed:
                                return "I'm experiencing technical difficulties with all available AI models. Please try again in a few moments, and I'll do my best to help you."
                            else:
                                return "All language models are currently experiencing issues. Please try again in a few moments."
                            
                    except (ValueError, KeyError):
                        # If we can't parse the error response, treat as generic error
                        print(f"❌ Model {model} error: {response.status_code} (unparseable response)")
                        if i < len(models_to_try) - 1:
                            if i == 0:
                                first_model_failed = True
                            print(f"🔄 Trying backup model: {models_to_try[i+1]}")
                            continue
                        else:
                            return "I'm having trouble connecting to the language model. Please try again in a few moments."
                        
            except requests.exceptions.Timeout:
                print(f"⏱️ Timeout with model {model}")
                if i < len(models_to_try) - 1:
                    if i == 0:
                        first_model_failed = True
                    print(f"🔄 Trying backup model: {models_to_try[i+1]}")
                    continue
                else:
                    return "The request timed out. Please try asking your question again."
            except Exception as e:
                print(f"❌ Error with model {model}: {e}")
                if i < len(models_to_try) - 1:
                    if i == 0:
                        first_model_failed = True
                    print(f"🔄 Trying backup model: {models_to_try[i+1]}")
                    continue
                else:
                    return "I apologize, but I'm having trouble processing your request right now. Please try again."
        
        # If we get here, all models failed
        if first_model_failed:
            return "I'm currently experiencing technical difficulties with all available AI models. Please try again in a few moments, and I'll do my best to help you with your question."
        else:
            return "I'm unable to process your request at the moment. Please try again later."
    
    def get_fallback_response(self):
        """Get a fallback response when API is not available"""
        fallback_responses = [
            "I'm currently running in fallback mode. Please ensure OPENROUTER_API_KEY is set in your environment.",
            "I understand you have questions about your treatment. Please feel free to ask about anything that concerns you.",
            "Theranostics can seem complex, but I'm here to explain it in simple terms. What would you like to know?",
            "Many patients have similar concerns about nuclear medicine treatments. What specific questions do you have?",
        ]
        return random.choice(fallback_responses)
    
    def chatbot_response(self, message, history, context="main_chat", section=None, lang='en'):
        """Main chatbot function that uses OpenRouter or falls back to predefined responses"""
        if self.openrouter_available:
            response = self.generate_openrouter_response(message, history, context, section, lang=lang)
        else:
            # Provide language-appropriate fallback message
            if lang == 'de':
                response = "Der Dienst ist derzeit nicht verfügbar. Bitte versuchen Sie es später erneut."
            else:
                response = self.get_fallback_response()
            # Still log fallback responses
            conversation_logger.log_conversation(message, response, context=context, section=section, model_used="fallback", metadata={"lang": lang})
        
        return response
    
    def get_current_model(self):
        """Get the currently active model"""
        return self.current_model
    
    def is_api_available(self):
        """Check if the OpenRouter API is available"""
        return self.openrouter_available


# Global chatbot instance
theranostics_bot = TheranosticsBot()