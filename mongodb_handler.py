"""
MongoDB Integration Module
Handles MongoDB connections and data storage for the Theranostics Chatbot
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    from pymongo.database import Database
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("⚠️ PyMongo not installed. MongoDB features will be disabled.")
    print("   Install with: pip install pymongo")


class MongoDBHandler:
    """Handles all MongoDB operations for the chatbot application"""
    
    def __init__(self, connection_string: Optional[str] = None, database_name: str = "theranosticsChatbot"):
        self.connection_string = connection_string or os.getenv(
            "MONGO_URI", 
            os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
        )
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.connected = False
        
        # Collection names
        self.conversations_collection_name = "conversations"  # For LLM Q&A
        self.forms_collection_name = "forms"  # For form submissions
        
        # Try loading from parent directory .env file if not found
        if not self.connection_string or self.connection_string == "mongodb://localhost:27017/":
            parent_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            if os.path.exists(parent_env_path):
                try:
                    from dotenv import load_dotenv
                    load_dotenv(parent_env_path)
                    self.connection_string = os.getenv('MONGO_URI', self.connection_string)
                except ImportError:
                    print("⚠️ python-dotenv not installed, using environment variables only")
        
        if MONGODB_AVAILABLE:
            self.connect()
        else:
            print("❌ MongoDB not available - PyMongo not installed")
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.connected = True
            
            print(f"✅ MongoDB connected successfully to database: {self.database_name}")
            
            # Create collections with indexes for better performance
            self._setup_collections()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("   Falling back to file-based logging...")
            self.connected = False
        except Exception as e:
            print(f"❌ Unexpected MongoDB error: {e}")
            self.connected = False
    
    def _setup_collections(self):
        """Set up collections and indexes"""
        if not self.connected or self.db is None:
            return
            
        try:
            # Conversations collection for LLM Q&A
            conversations = self.db[self.conversations_collection_name]
            conversations.create_index("timestamp")
            conversations.create_index("context")
            conversations.create_index("section")
            conversations.create_index("session_id")
            
            # Forms collection for form submissions
            forms = self.db[self.forms_collection_name]
            forms.create_index("submission_timestamp")
            forms.create_index("age")
            forms.create_index("treatment_satisfaction")
            forms.create_index("session_id")
            
            print(f"📊 MongoDB collections '{self.conversations_collection_name}' and '{self.forms_collection_name}' created successfully")
            
        except Exception as e:
            print(f"⚠️ Error setting up MongoDB collections: {e}")
    
    def log_conversation(self, user_message: str, bot_response: str, 
                        context: str = "main_chat", section: Optional[str] = None, 
                        model_used: Optional[str] = None, session_id: Optional[str] = None) -> bool:
        """Accumulate conversation exchanges and update/create complete conversation per user"""
        if not self.connected or self.db is None:
            return False
            
        try:
            current_session_id = session_id or self._generate_session_id()
            timestamp = datetime.now()
            
            # Create a conversation exchange object
            conversation_exchange = {
                "timestamp": timestamp,
                "user_message": user_message,
                "bot_response": bot_response,
                "model_used": model_used,
                "context": context,
                "section": section
            }
            
            # Try to find existing conversation document for this session
            existing_conversation = self.db[self.conversations_collection_name].find_one({
                "session_id": current_session_id
            })
            
            if existing_conversation:
                # Update existing conversation by appending new exchange
                result = self.db[self.conversations_collection_name].update_one(
                    {"session_id": current_session_id},
                    {
                        "$push": {"conversation_history": conversation_exchange},
                        "$set": {
                            "last_updated": timestamp,
                            "total_exchanges": existing_conversation.get("total_exchanges", 0) + 1
                        }
                    }
                )
                if result.modified_count > 0:
                    print(f"📝 Conversation updated for session: {current_session_id[:8]}...")
                    return True
            else:
                # Create new conversation document
                conversation_doc = {
                    "session_id": current_session_id,
                    "created_at": timestamp,
                    "last_updated": timestamp,
                    "total_exchanges": 1,
                    "user_ip": self._get_user_ip(),
                    "conversation_history": [conversation_exchange]
                }
                
                result = self.db[self.conversations_collection_name].insert_one(conversation_doc)
                
                if result.inserted_id:
                    print(f"📝 New conversation created for session: {current_session_id[:8]}...")
                    return True
            
            print("⚠️ Failed to log conversation to MongoDB")
            return False
                
        except Exception as e:
            print(f"❌ Error logging conversation to MongoDB: {e}")
            return False
    
    def save_form_submission(self, session_id: str, data_to_update: Dict[str, Any]) -> bool:
        """
        Update a single document for a given session_id with new form data.
        Uses upsert=True to create the document if it doesn't exist.
        """
        if not self.connected or self.db is None:
            print("⚠️ MongoDB not connected. Cannot save form submission.")
            return False
            
        try:
            # The filter to find the document for the current session
            query = {"session_id": session_id}
            
            # Ensure 'session_id' is not in the update payload to avoid conflicts
            data_to_update.pop('session_id', None)

            # The update operation using $set to add/update fields
            # and $setOnInsert to set values only when a new document is created
            update = {
                "$set": {
                    **data_to_update,  # Unpack all new form data
                    "last_updated": datetime.now()
                },
                "$setOnInsert": {
                    "session_id": session_id,
                    "created_at": datetime.now(),
                    "user_ip": self._get_user_ip()
                }
            }
            
            # Perform the update operation with upsert=True
            result = self.db[self.forms_collection_name].update_one(
                query,
                update,
                upsert=True
            )
            
            if result.upserted_id:
                print(f"📋 New form document created for session: {session_id}")
                return True
            elif result.modified_count > 0:
                print(f"📋 Form document updated for session: {session_id}")
                return True
            else:
                # This case can happen if the data submitted is identical to what's already stored
                print(f"📋 No changes to form document for session: {session_id}")
                return True
                
        except Exception as e:
            print(f"❌ Error saving form submission to MongoDB: {e}")
            return False
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics from MongoDB"""
        if not self.connected or self.db is None:
            return {"error": "MongoDB not connected"}
            
        try:
            conversations_collection = self.db[self.conversations_collection_name]
            
            total_conversations = conversations_collection.count_documents({})
            
            # Context breakdown
            context_pipeline = [
                {"$group": {"_id": "$context", "count": {"$sum": 1}}}
            ]
            context_stats = list(conversations_collection.aggregate(context_pipeline))
            
            # Daily conversation counts (last 7 days)
            from datetime import timedelta
            seven_days_ago = datetime.now() - timedelta(days=7)
            daily_pipeline = [
                {"$match": {"timestamp": {"$gte": seven_days_ago}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            daily_stats = list(conversations_collection.aggregate(daily_pipeline))
            
            # Model usage stats
            model_pipeline = [
                {"$group": {"_id": "$model_used", "count": {"$sum": 1}}}
            ]
            model_stats = list(conversations_collection.aggregate(model_pipeline))
            
            return {
                "total_conversations": total_conversations,
                "context_breakdown": {item["_id"]: item["count"] for item in context_stats},
                "daily_conversations": {item["_id"]: item["count"] for item in daily_stats},
                "model_usage": {item["_id"]: item["count"] for item in model_stats},
                "collection_name": "conversations"
            }
            
        except Exception as e:
            print(f"❌ Error getting conversation stats: {e}")
            return {"error": str(e)}
    
    def get_form_submission_stats(self) -> Dict[str, Any]:
        """Get form submission statistics from MongoDB"""
        if not self.connected or self.db is None:
            return {"error": "MongoDB not connected"}
            
        try:
            forms_collection = self.db[self.forms_collection_name]
            
            total_submissions = forms_collection.count_documents({})
            
            # Average satisfaction score
            satisfaction_pipeline = [
                {"$group": {"_id": None, "avg_satisfaction": {"$avg": "$treatment_satisfaction"}}}
            ]
            satisfaction_result = list(forms_collection.aggregate(satisfaction_pipeline))
            avg_satisfaction = satisfaction_result[0]["avg_satisfaction"] if satisfaction_result else 0
            
            # Age distribution
            age_pipeline = [
                {"$bucket": {
                    "groupBy": "$user_age",
                    "boundaries": [0, 30, 40, 50, 60, 70, 80, 100],
                    "default": "Other",
                    "output": {"count": {"$sum": 1}}
                }}
            ]
            age_distribution = list(forms_collection.aggregate(age_pipeline))
            
            # Gender distribution
            gender_pipeline = [
                {"$group": {"_id": "$user_gender", "count": {"$sum": 1}}}
            ]
            gender_distribution = list(forms_collection.aggregate(gender_pipeline))
            
            # Most common side effects
            side_effects_pipeline = [
                {"$unwind": "$side_effects"},
                {"$group": {"_id": "$side_effects", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            side_effects_stats = list(forms_collection.aggregate(side_effects_pipeline))
            
            return {
                "total_submissions": total_submissions,
                "average_satisfaction": round(avg_satisfaction, 2) if avg_satisfaction else 0,
                "age_distribution": age_distribution,
                "gender_distribution": {item["_id"]: item["count"] for item in gender_distribution},
                "common_side_effects": {item["_id"]: item["count"] for item in side_effects_stats},
                "collection_name": "form_submissions"
            }
            
        except Exception as e:
            print(f"❌ Error getting form submission stats: {e}")
            return {"error": str(e)}
    
    def export_data_to_json(self, collection_name: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Export data from MongoDB collection to JSON format"""
        if not self.connected or self.db is None:
            return {"error": "MongoDB not connected"}
            
        try:
            collection = self.db[collection_name]
            
            # Get documents with optional limit
            cursor = collection.find().sort("timestamp", -1)  # Most recent first
            if limit:
                cursor = cursor.limit(limit)
            
            documents = []
            for doc in cursor:
                # Create a mutable copy of the document
                mutable_doc = dict(doc)
                # Convert ObjectId to string for JSON serialization
                mutable_doc["_id"] = str(mutable_doc["_id"])
                # Convert datetime to ISO string
                if "timestamp" in mutable_doc and hasattr(mutable_doc["timestamp"], 'isoformat'):
                    mutable_doc["timestamp"] = mutable_doc["timestamp"].isoformat()
                if "submission_timestamp" in mutable_doc and hasattr(mutable_doc["submission_timestamp"], 'isoformat'):
                    mutable_doc["submission_timestamp"] = mutable_doc["submission_timestamp"].isoformat()
                documents.append(mutable_doc)
            
            return {
                "collection": collection_name,
                "count": len(documents),
                "exported_at": datetime.now().isoformat(),
                "data": documents
            }
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            return {"error": str(e)}
    
    def _generate_session_id(self) -> str:
        """Generate a session ID for tracking user sessions"""
        import uuid
        return str(uuid.uuid4())[:8]  # Short session ID
    
    def _get_user_ip(self) -> str:
        """Get user IP address (placeholder for now)"""
        # In a real deployment, you'd get this from the request context
        return "127.0.0.1"  # localhost for development
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.connected = False
            print("🔌 MongoDB connection closed")


# Global MongoDB handler instance
mongodb_handler = MongoDBHandler()


def get_mongodb_status() -> Dict[str, Any]:
    """Get current MongoDB connection status and basic info"""
    if not MONGODB_AVAILABLE:
        return {
            "available": False,
            "connected": False,
            "error": "PyMongo not installed"
        }
    
    return {
        "available": MONGODB_AVAILABLE,
        "connected": mongodb_handler.connected,
        "database": mongodb_handler.database_name if mongodb_handler.connected else None,
        "connection_string": mongodb_handler.connection_string[:50] + "..." if mongodb_handler.connection_string else None
    }