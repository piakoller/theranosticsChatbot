"""
Logging Module
Enhanced conversation logging with MongoDB integration and file backup.
Handles conversation storage, form submissions, and analytics.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

# Control logging targets via environment variables:
# ENABLE_MONGODB: if '1', attempt to log to MongoDB (default: '1')
# ENABLE_FILE_LOGS: if '1', also write local JSON backups (default: '0')
ENABLE_MONGODB = os.getenv("ENABLE_MONGODB", "1") == "1"
ENABLE_FILE_LOGS = os.getenv("ENABLE_FILE_LOGS", "0") == "1"

# Import MongoDB handler with graceful fallback
try:
    from mongodb_handler import MongoDBHandler
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("⚠️ MongoDB handler not available, using file-only logging")


class ConversationLogger:
    """Enhanced conversation logger with MongoDB primary storage and file backup"""
    
    def __init__(self, log_dir: str = "conversation_logs"):
        self.log_dir = log_dir
        self.session_id = str(uuid.uuid4())
        self.current_model = None  # Will be set by the chatbot
        # Configure logging backends according to env flags
        self.mongodb_handler = None

        # Create log directory only if file logging is enabled
        if ENABLE_FILE_LOGS:
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception:
                pass

        # Initialize MongoDB handler if requested and available
        if ENABLE_MONGODB:
            if MONGODB_AVAILABLE:
                try:
                    self.mongodb_handler = MongoDBHandler()
                    print("🔄 Conversation logging system initialized with MongoDB")
                except Exception as e:
                    print(f"⚠️ MongoDB initialization failed: {e}")
                    # fall back to file logging if enabled
                    if ENABLE_FILE_LOGS:
                        print("📝 Falling back to file-only logging")
            else:
                print("⚠️ ENABLE_MONGODB is set but mongodb_handler is not available; MongoDB logging disabled")
        else:
            print("⚠️ MongoDB logging disabled via ENABLE_MONGODB=0")
            if ENABLE_FILE_LOGS:
                print("📝 File-only conversation logging enabled")
    
    def set_current_model(self, model_name: str):
        """Set the current AI model being used for conversations"""
        self.current_model = model_name
        print(f"🤖 Current AI model set to: {model_name}")
    
    def log_conversation(self, user_input: str, bot_response: str, 
                        context: Optional[str] = None, 
                        section: Optional[str] = None,
                        model_used: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Log conversation with MongoDB primary storage and file backup
        
        Args:
            user_input: User's message
            bot_response: Bot's response
            context: Optional context information
            section: Optional section identifier (for form sections)
            model_used: Optional model name that generated the response
            metadata: Optional additional metadata
            
        Returns:
            bool: True if logged successfully to at least one storage
        """
        # If neither MongoDB nor local file logging is enabled, do nothing
        if not (ENABLE_MONGODB or ENABLE_FILE_LOGS):
            return False

        timestamp = datetime.now()
        
        # Prepare conversation data
        conversation_data = {
            "session_id": self.session_id,
            "timestamp": timestamp,
            "user_input": user_input,
            "bot_response": bot_response,
            "context": context,
            "metadata": metadata or {}
        }
        
        mongodb_success = False
        file_success = False
        
        # Try MongoDB first
        if self.mongodb_handler:
            try:
                # Combine metadata with model information
                enhanced_metadata = metadata.copy() if metadata else {}
                # Use provided model_used or fall back to self.current_model
                effective_model = model_used or self.current_model
                if effective_model:
                    enhanced_metadata['model_used'] = effective_model
                
                mongodb_success = self.mongodb_handler.log_conversation(
                    user_message=user_input,
                    bot_response=bot_response,
                    context=context,
                    section=section,
                    session_id=self.session_id,
                    model_used=effective_model
                )
                if mongodb_success:
                    print(f"✅ Conversation logged to MongoDB (Session: {self.session_id[:8]}...)")
            except Exception as e:
                print(f"❌ MongoDB logging failed: {e}")
        
        # Optionally maintain file backup if enabled
        if ENABLE_FILE_LOGS:
            try:
                file_success = self._log_to_file(conversation_data)
                if file_success and not mongodb_success:
                    print(f"📝 Conversation logged to file backup (Session: {self.session_id[:8]}...)")
            except Exception as e:
                print(f"❌ File logging failed: {e}")
        
        # Return success if at least one storage method worked
        return mongodb_success or file_success
    
    def _log_to_file(self, conversation_data: Dict[str, Any]) -> bool:
        """Log conversation to file with JSON format"""
        try:
            # Create filename with timestamp
            timestamp_str = conversation_data["timestamp"].strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp_str}_{self.session_id[:8]}.json"
            filepath = os.path.join(self.log_dir, filename)
            
            # Convert datetime to string for JSON serialization
            log_data = conversation_data.copy()
            log_data["timestamp"] = conversation_data["timestamp"].isoformat()
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"File logging error: {e}")
            return False
    
    def save_form_submission(self, form_data: Dict[str, Any]) -> str:
        """
        Save form submission with MongoDB primary storage and file backup
        
        Args:
            form_data: Dictionary containing form submission data
            
        Returns:
            str: Success message indicating where data was saved
        """
        # Short-circuit if neither MongoDB nor file logging enabled
        if not (ENABLE_MONGODB or ENABLE_FILE_LOGS):
            return "Logging disabled"

        mongodb_success = False
        file_success = False
        
        # Add session tracking
        form_data_with_session = form_data.copy()
        form_data_with_session["session_id"] = self.session_id
        form_data_with_session["submission_timestamp"] = datetime.now().isoformat()
        
        # Try MongoDB first
        if self.mongodb_handler:
            try:
                mongodb_success = self.mongodb_handler.save_form_submission(form_data_with_session)
                if mongodb_success:
                    print(f"✅ Form submission saved to MongoDB (Session: {self.session_id[:8]}...)")
            except Exception as e:
                print(f"❌ MongoDB form save failed: {e}")
        
        # Optionally maintain file backup if enabled
        if ENABLE_FILE_LOGS:
            try:
                file_success = self._save_form_to_file(form_data_with_session)
                if file_success and not mongodb_success:
                    print(f"📝 Form submission saved to file backup (Session: {self.session_id[:8]}...)")
            except Exception as e:
                print(f"❌ File form save failed: {e}")
        
        # Return appropriate message
        if mongodb_success and file_success:
            return "Data saved to MongoDB and file backup"
        elif mongodb_success:
            return "Data saved to MongoDB"
        elif file_success:
            return "Data saved to file backup"
        else:
            return "Error: Data could not be saved"
    
    def _save_form_to_file(self, form_data: Dict[str, Any]) -> bool:
        """Save form submission to file backup"""
        try:
            # Create filename with timestamp
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"form_submission_{timestamp_str}_{self.session_id[:8]}.json"
            filepath = os.path.join(self.log_dir, filename)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(form_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"File form save error: {e}")
            return False
    
    def get_session_conversations(self) -> List[Dict[str, Any]]:
        """Get all conversations for the current session"""
        # If neither logging target is enabled, return empty list
        if not (ENABLE_MONGODB or ENABLE_FILE_LOGS):
            return []

        if self.mongodb_handler:
            try:
                return self.mongodb_handler.get_session_conversations(self.session_id)
            except Exception as e:
                print(f"Error retrieving MongoDB conversations: {e}")
        
        # Fallback to file-based retrieval
        return self._get_file_conversations()
    
    def _get_file_conversations(self) -> List[Dict[str, Any]]:
        """Get conversations from file backup"""
        conversations = []
        try:
            for filename in os.listdir(self.log_dir):
                if filename.startswith(f"conversation_") and self.session_id[:8] in filename:
                    filepath = os.path.join(self.log_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        conversations.append(json.load(f))
        except Exception as e:
            print(f"Error reading file conversations: {e}")
        
        return sorted(conversations, key=lambda x: x.get("timestamp", ""))
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        if not (ENABLE_MONGODB or ENABLE_FILE_LOGS):
            return {"total_conversations": 0}

        if self.mongodb_handler:
            try:
                return self.mongodb_handler.get_conversation_stats()
            except Exception as e:
                print(f"Error retrieving MongoDB stats: {e}")
        
        # Fallback to basic file stats
        return {"total_conversations": len(self._get_file_conversations())}
    
    def export_conversations_to_csv(self) -> str:
        """
        Export conversations to CSV format
        
        Returns:
            str: Status message about the export
        """
        try:
            import csv
            from datetime import datetime
            
            # Get all conversations
            if not (ENABLE_MONGODB or ENABLE_FILE_LOGS):
                return "❌ Logging disabled, no conversations to export"

            conversations = self.get_session_conversations()
            
            if not conversations:
                return "❌ No conversations found to export"
            
            # Create filename with timestamp
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversations_export_{timestamp_str}.csv"
            filepath = os.path.join(self.log_dir, filename)
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'session_id', 'user_input', 'bot_response', 'context', 'model_used']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for conv in conversations:
                    # Handle both MongoDB and file formats
                    row = {
                        'timestamp': conv.get('timestamp', ''),
                        'session_id': conv.get('session_id', ''),
                        'user_input': conv.get('user_input', conv.get('user_message', '')),
                        'bot_response': conv.get('bot_response', ''),
                        'context': conv.get('context', ''),
                        'model_used': conv.get('metadata', {}).get('model_used', conv.get('model_used', ''))
                    }
                    writer.writerow(row)
            
            return f"✅ Conversations exported to: {filename}"
            
        except Exception as e:
            error_msg = f"❌ Export failed: {str(e)}"
            print(error_msg)
            return error_msg
    
    def new_session(self) -> str:
        """Start a new conversation session"""
        old_session = self.session_id
        self.session_id = str(uuid.uuid4())
        print(f"🔄 New session started: {self.session_id[:8]}... (Previous: {old_session[:8]}...)")
        return self.session_id


# Global logger instance
conversation_logger = ConversationLogger()


def log_conversation(user_input: str, bot_response: str, 
                    context: Optional[str] = None, 
                    section: Optional[str] = None,
                    model_used: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    Global function for logging conversations
    
    Args:
        user_input: User's message
        bot_response: Bot's response  
        context: Optional context information
        section: Optional section identifier
        model_used: Optional model name that generated the response
        metadata: Optional additional metadata
        
    Returns:
        bool: True if logged successfully
    """
    return conversation_logger.log_conversation(user_input, bot_response, context, section, model_used, metadata)


def get_session_id() -> str:
    """Get current session ID"""
    return conversation_logger.session_id


def new_session() -> str:
    """Start new conversation session"""
    return conversation_logger.new_session()


if __name__ == "__main__":
    # Test the logging system
    print("Testing enhanced conversation logging system...")
    
    # Test conversation logging
    success = log_conversation(
        user_input="Test question about theranostics",
        bot_response="Test response about theranostics treatment",
        context="Testing context",
        metadata={"test": True}
    )
    print(f"Conversation logging test: {'✅ Success' if success else '❌ Failed'}")
    
    # Test form submission
    test_form_data = {
        "age": "45",
        "gender": "Female",
        "diagnosis": "Neuroendocrine tumor",
        "treatment_satisfaction": "Very satisfied",
        "test_submission": True
    }
    
    result = conversation_logger.save_form_submission(test_form_data)
    print(f"Form submission test: {result}")
    
    # Test statistics
    stats = conversation_logger.get_conversation_stats()
    print(f"Statistics: {stats}")
    
    print("✅ Enhanced logging system test completed")