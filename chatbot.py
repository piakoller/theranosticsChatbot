"""
Normal Chatbot with Ollama and LangChain

This script builds a normal conversational chatbot that uses Ollama
for language generation with conversation memory, similar to the RAG chatbot
but without document retrieval.
"""

import os
import random
from typing import Optional, List, Dict, Any
from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from ollama_config import (
    OLLAMA_LLM_MODEL,
    OLLAMA_MODEL_KWARGS,
    OLLAMA_BASE_URL,
    MAX_MEMORY_LENGTH
)
from logging_module import conversation_logger

# Import Ollama LLM
try:
    from langchain_ollama import OllamaLLM
    OLLAMA_AVAILABLE = True
except ImportError:
    print("❌ langchain-ollama not installed. Please install it with: pip install langchain-ollama")
    OLLAMA_AVAILABLE = False

# Path to prompt files
PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "prompts")
NORMAL_PROMPT_FILE = os.path.join(PROMPTS_PATH, "normal_chatbot.txt")

def load_system_prompt():
    """Load the normal chatbot system prompt from file"""
    try:
        with open(NORMAL_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"⚠️ Normal prompt file not found at {NORMAL_PROMPT_FILE}, using default prompt")
        return """Sie sind ein mitfühlender KI-Assistent, spezialisiert auf Patientenaufklärung zu Theranostik und Nuklearmedizin.
Erklären Sie medizinische Konzepte verständlich, beruhigend und in Alltagssprache."""


class TheranosticsBot:
    """
    A normal conversational chatbot that uses Ollama with conversation memory,
    similar to RAG chatbot but without document retrieval.
    """
    def __init__(self):
        self.conversation_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="response"
        )
        
        if OLLAMA_AVAILABLE:
            self.llm = OllamaLLM(
                model=OLLAMA_LLM_MODEL,
                base_url=OLLAMA_BASE_URL,
                **OLLAMA_MODEL_KWARGS
            )
            self.ollama_available = self._check_ollama_availability()
        else:
            self.llm = None
            self.ollama_available = False
        
        self.current_model = OLLAMA_LLM_MODEL
        conversation_logger.set_current_model(self.current_model)
        print(f"📋 Normal chatbot using prompt from: {NORMAL_PROMPT_FILE}")
        print(f"🤖 Using Ollama model: {OLLAMA_LLM_MODEL}")
    
    def _check_ollama_availability(self):
        """Check if Ollama server is running"""
        if not OLLAMA_AVAILABLE or not self.llm:
            print("❌ Ollama langchain integration not available.")
            return False
        
        try:
            # Test if Ollama server is running by making a simple request
            import requests
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama server is running")
                return True
            else:
                print(f"❌ Ollama server responded with status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to Ollama server: {e}")
            return False
    
    def ask(self, question: str) -> dict:
        """
        Asks a question to the conversational chain and returns the response.
        """
        if not self.ollama_available or not self.llm:
            return {"error": "Ollama is not available."}
            
        try:
            print(f"\n❓ Asking question: {question}")
            
            # Build the conversation context
            system_prompt = self._get_system_prompt(lang='de')
            
            # Create the full prompt with system prompt, memory, and current message
            full_prompt = f"{system_prompt}\n\n"
            
            # Add conversation memory for context
            memory_messages = self.memory.chat_memory.messages
            if memory_messages:
                full_prompt += "Bisherige Unterhaltung:\n"
                for msg in memory_messages[-10:]:  # Last 10 messages for context
                    if hasattr(msg, 'type'):
                        if 'Human' in str(type(msg)):
                            full_prompt += f"Benutzer: {msg.content}\n"
                        elif 'AI' in str(type(msg)):
                            full_prompt += f"Assistent: {msg.content}\n"
                full_prompt += "\n"
            
            # Add current question
            full_prompt += f"Aktuelle Frage: {question}\n\nAntwort:"
            
            # Get response from Ollama
            response = self.llm.invoke(full_prompt)
            
            if not response or not response.strip():
                response = "Entschuldigung, ich konnte keine Antwort generieren. Können Sie Ihre Frage bitte anders formulieren?"
            
            # Add to memory
            from langchain.schema import HumanMessage, AIMessage
            self.memory.chat_memory.add_user_message(question)
            self.memory.chat_memory.add_ai_message(response.strip())
            
            return {"response": response.strip()}
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return {"error": str(e)}
    
    def _get_system_prompt(self, lang='de'):
        """Get the system prompt for patient education, language-aware."""
        if lang == 'de':
            # Load the German prompt from file
            return load_system_prompt()
        else:
            # English fallback
            return (
                "You are a compassionate AI assistant specializing in patient education about theranostics and nuclear medicine. "
                "Help patients understand medical concepts in simple, reassuring terms.\n\n"
                "Communication Guidelines:\n"
                "1. Keep answers concise (1-3 sentences for simple questions).\n"
                "2. Use simple language; avoid jargon.\n"
                "3. Be reassuring and empathetic.\n"
                "4. For complex topics: give a brief overview, then offer more detail if requested.\n"
                "5. End by inviting follow-up questions.\n"
                "Response style: short, clear, 1–2 key points, encourage follow-up."
            )
    
    def chatbot_response(self, message: str, history: Optional[List] = None, context: str = "main_chat", section: Optional[str] = None, lang: str = 'de', chatbot_type: str = "normal") -> str:
        """
        Interface method compatible with the study interface.
        Returns just the response text to be compatible with the existing chatbot interface.
        Now includes chatbot_type parameter to track which chatbot type was used.
        """
        try:
            response = self.ask(message)
            
            if "error" in response:
                error_response = self.get_fallback_response(lang=lang)
                # Still log error responses
                conversation_logger.log_conversation(
                    message, 
                    error_response, 
                    context=context, 
                    section=section, 
                    model_used="error", 
                    metadata={"lang": lang, "error": response["error"]},
                    chatbot_type=chatbot_type
                )
                return error_response
            
            response_text = response.get('response', 'Entschuldigung, ich konnte keine Antwort generieren.')
            
            # Log the conversation
            conversation_logger.log_conversation(
                message, 
                response_text, 
                context=context, 
                section=section, 
                model_used=self.current_model, 
                metadata={"lang": lang},
                chatbot_type=chatbot_type
            )
            
            return response_text
            
        except Exception as e:
            print(f"❌ Normal chatbot error: {e}")
            error_response = "Entschuldigung, ich habe gerade Schwierigkeiten beim Zugriff auf meine Wissensbasis. Bitte versuchen Sie es später erneut."
            
            # Log the error
            conversation_logger.log_conversation(
                message, 
                error_response, 
                context=context, 
                section=section, 
                model_used="error", 
                metadata={"lang": lang, "error": str(e)},
                chatbot_type=chatbot_type
            )
            
            return error_response
    
    def get_fallback_response(self, lang='de'):
        """Get a fallback response when Ollama is not available"""
        if lang == 'de':
            fallback_responses = [
                "Entschuldigung, ich kann derzeit nicht auf das Sprachmodell zugreifen. Bitte versuchen Sie es später erneut.",
                "Ich verstehe, dass Sie Fragen zu Ihrer Behandlung haben. Leider ist das Sprachmodell gerade nicht verfügbar.",
                "Das Sprachmodell ist momentan nicht erreichbar. Bitte stellen Sie sicher, dass Ollama läuft und die Modelle verfügbar sind.",
                "Ich kann Ihnen gerade nicht antworten, da die Verbindung zum Sprachmodell unterbrochen ist.",
            ]
        else:
            fallback_responses = [
                "I'm sorry, I can't access the language model right now. Please try again later.",
                "I understand you have questions about your treatment, but the language model is currently unavailable.",
                "The language model is not accessible at the moment. Please ensure Ollama is running and models are available.",
                "I can't respond right now due to a language model connection issue.",
            ]
        return random.choice(fallback_responses)
    
    def clear_conversation_memory(self):
        """
        Clears the conversation memory to start fresh.
        """
        self.memory.clear()
        print("🧹 Conversation memory cleared.")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Returns the conversation history as a list of message dictionaries.
        """
        messages = []
        for message in self.memory.chat_memory.messages:
            messages.append({
                "type": type(message).__name__,
                "content": message.content
            })
        return messages
    
    def get_memory_length(self) -> int:
        """Get the current number of messages in memory"""
        return len(self.memory.chat_memory.messages)
    
    def get_current_model(self):
        """Get the currently active model"""
        return self.current_model
    
    def is_api_available(self):
        """Check if Ollama is available"""
        return self.ollama_available
    
    def get_memory_summary(self) -> str:
        """Get a summary of the current conversation memory for debugging"""
        messages = self.memory.chat_memory.messages
        if not messages:
            return "No conversation history"
        
        summary = f"Memory contains {len(messages)} messages:\n"
        for i, msg in enumerate(messages[-6:]):  # Show last 6 messages
            msg_type = type(msg).__name__
            content = str(msg.content)
            content_preview = content[:50] + "..." if len(content) > 50 else content
            summary += f"  {i+1}. {msg_type}: {content_preview}\n"
        
        return summary


# Global chatbot instance
theranostics_bot = TheranosticsBot()