"""
RAG Chatbot with Ollama and LangChain

This script builds a Retrieval-Augmented Generation (RAG) chatbot that uses Ollama
for both embedding and language models. It loads documents from a local directory,
creates a vector store, and answers questions based on the document content.
"""

import os
from typing import Optional, List, Dict, Any
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Import shared Ollama configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ollama_config import (
    OLLAMA_LLM_MODEL,
    OLLAMA_EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL_KWARGS,
    MAX_MEMORY_LENGTH
)

# --- Configuration ---
# Use a relative path to ensure it works from any location
current_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(current_dir, "data")
VECTOR_DB_PATH = os.path.join(current_dir, "chroma_db")

# Use shared configuration
EMBEDDING_MODEL = OLLAMA_EMBEDDING_MODEL
LLM_MODEL = OLLAMA_LLM_MODEL

# Path to prompt files
PROMPTS_PATH = os.path.join(os.path.dirname(current_dir), "prompts")
EXPERT_PROMPT_FILE = os.path.join(PROMPTS_PATH, "expert_chatbot.txt")

def load_system_prompt():
    """Load the expert chatbot system prompt from file"""
    try:
        with open(EXPERT_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"⚠️ Expert prompt file not found at {EXPERT_PROMPT_FILE}, using default prompt")
        return """Sie sind ein mitfühlender KI-Assistent, spezialisiert auf Patientenaufklärung zu Theranostik und Nuklearmedizin.
Nutzen Sie die bereitgestellten Fachquellen für präzise Antworten und erklären Sie medizinische Konzepte verständlich."""

class RagChatbot:
    """
    A RAG chatbot that loads data, creates a vector store, and answers questions with conversation memory.
    """
    def __init__(self):
        self.vector_store = None
        self.qa_chain = None
        self.conversation_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        self.llm = OllamaLLM(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            **OLLAMA_MODEL_KWARGS
        )
        self.embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL
        )
        
        # Check if the vector store already exists
        if os.path.exists(VECTOR_DB_PATH):
            print("✅ Loading existing vector store...")
            self.vector_store = Chroma(
                persist_directory=VECTOR_DB_PATH, 
                embedding_function=self.embeddings
            )
        else:
            print("🤔 No existing vector store found. Creating a new one...")
            self.create_vector_store()
            
        self.create_qa_chain()

    def create_vector_store(self):
        """
        Loads documents, splits them into chunks, and creates a Chroma vector store.
        """
        print(f"📂 Loading documents from: {DATA_PATH}")
        # Load both .txt and .pdf files
        loader_txt = DirectoryLoader(DATA_PATH, glob="*.txt")
        loader_pdf = DirectoryLoader(DATA_PATH, glob="*.pdf")
        documents = loader_txt.load() + loader_pdf.load()

        if not documents:
            raise ValueError(f"No documents found in {DATA_PATH}. Please add some .txt files.")

        print("✂️ Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)

        print("🧠 Creating vector store with embeddings...")
        self.vector_store = Chroma.from_documents(
            documents=chunks, 
            embedding=self.embeddings,
            persist_directory=VECTOR_DB_PATH
        )
        print(f"✅ Vector store created and persisted at: {VECTOR_DB_PATH}")

    def create_qa_chain(self):
        """
        Creates the conversational Question-Answering chain with memory using the vector store as a retriever.
        """
        if not self.vector_store:
            raise RuntimeError("Vector store is not initialized. Cannot create QA chain.")

        # Load the expert system prompt from file
        expert_system_prompt = load_system_prompt()

        # Define the prompt template for conversational retrieval
        template = f"""{expert_system_prompt}

Verwende den folgenden Kontext und die bisherige Unterhaltung, um die Frage zu beantworten:

Kontext: {{context}}

Bisherige Unterhaltung:
{{chat_history}}

Aktuelle Frage: {{question}}

Antwort:
"""
        
        custom_prompt = PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template=template
        )

        # Create the ConversationalRetrievalChain with memory
        self.conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": custom_prompt},
            return_source_documents=True
        )
        
        print("🔗 Conversational QA chain created successfully.")
        print(f"📋 Using expert prompt from: {EXPERT_PROMPT_FILE}")

    def ask(self, question: str) -> dict:
        """
        Asks a question to the conversational RAG chain and returns the response.
        """
        if not self.conversation_chain:
            return {"error": "Conversation chain is not initialized."}
            
        print(f"\n❓ Asking question: {question}")
        response = self.conversation_chain.invoke({"question": question})
        return response

    def chatbot_response(self, message: str, history: Optional[List] = None, context: str = "main_chat", section: Optional[str] = None, chatbot_type: str = "expert") -> str:
        """
        Interface method compatible with the main chatbot for use in the study.
        Returns just the response text to be compatible with the existing chatbot interface.
        Now includes chatbot_type parameter for consistency with normal chatbot.
        """
        try:
            response = self.ask(message)
            return response.get('answer', 'I apologize, but I encountered an error processing your question.')
        except Exception as e:
            print(f"❌ RAG chatbot error: {e}")
            return "I apologize, but I'm having trouble accessing my knowledge base right now. Please try again later."
    
    def clear_conversation_history(self):
        """
        Clears the conversation memory to start fresh.
        """
        self.memory.clear()
        print("🧹 Conversation history cleared.")
    
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


# Global instance for use in the study
rag_chatbot_instance = None

def get_rag_chatbot():
    """
    Get or create the global RAG chatbot instance.
    """
    global rag_chatbot_instance
    if rag_chatbot_instance is None:
        try:
            rag_chatbot_instance = RagChatbot()
        except Exception as e:
            print(f"❌ Failed to initialize RAG chatbot: {e}")
            rag_chatbot_instance = None
    return rag_chatbot_instance

# --- Main execution block ---
if __name__ == "__main__":
    try:
        # Initialize the chatbot
        chatbot = RagChatbot()

        # --- Example conversation with memory ---
        print("🗣️ Starting conversation with memory...")
        
        # Question 1
        question_1 = "Welche Vorsichtsmaßnahmen muss ich zu Hause beachten?"
        answer_1 = chatbot.ask(question_1)
        
        print("\n--- Response 1 ---")
        print(f"💬 Answer: {answer_1['answer']}")
        print("\n📚 Source Documents:")
        for doc in answer_1.get('source_documents', []):
            print(f"  - {doc.metadata.get('source', 'N/A')}")

        # Question 2 - References previous question
        question_2 = "Wieso ist hier Dosimetrie relevant?"
        answer_2 = chatbot.ask(question_2)

        print("\n--- Response 2 ---")
        print(f"💬 Answer: {answer_2['answer']}")

        # Question 3 - Asks about conversation history
        question_3 = "Welche Frage habe ich davor gestellt?"
        answer_3 = chatbot.ask(question_3)

        print("\n--- Response 3 ---")
        print(f"💬 Answer: {answer_3['answer']}")

        # Show conversation memory
        print("\n--- Conversation History ---")
        memory_messages = chatbot.memory.chat_memory.messages
        for i, message in enumerate(memory_messages):
            print(f"{i+1}. {type(message).__name__}: {message.content[:100]}...")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("   Please ensure you have Ollama running and the required models pulled.")
        print("   Also install the required dependencies:")
        print("   pip install langchain-ollama unstructured")
        print("   ollama pull gemma3")
        print("   ollama pull embeddinggemma")
