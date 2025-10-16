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
        
        # Try loading from .env file if not found
        if not self.connection_string or self.connection_string == "mongodb://localhost:27017/":
            # Search for .env file in multiple possible locations
            possible_env_paths = [
                # Current directory and parents
                os.path.join(os.path.dirname(__file__), '.env'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'),
                # Project root variations
                os.path.join(os.getcwd(), '.env'),
                os.path.join(os.path.dirname(os.getcwd()), '.env'),
            ]
            
            for env_path in possible_env_paths:
                if os.path.exists(env_path):
                    try:
                        from dotenv import load_dotenv
                        load_dotenv(env_path)
                        new_connection_string = os.getenv('MONGO_URI', self.connection_string)
                        if new_connection_string != self.connection_string:
                            self.connection_string = new_connection_string
                            print(f"📄 Loaded .env from: {env_path}")
                            break
                    except ImportError:
                        print("⚠️ python-dotenv not installed, using environment variables only")
                        break
        
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
        """Set up collections and indexes for optimal performance and uniqueness"""
        if not self.connected or self.db is None:
            return
            
        try:
            # Conversations collection for LLM Q&A
            conversations = self.db[self.conversations_collection_name]
            self._ensure_unique_user_index(conversations, "conversations")
            
            # Create other indexes for conversations collection
            self._create_index_safely(conversations, "timestamp")
            self._create_index_safely(conversations, "context")
            self._create_index_safely(conversations, "section")
            self._create_index_safely(conversations, "last_updated")
            
            # Forms collection for form submissions
            forms = self.db[self.forms_collection_name]
            self._ensure_unique_user_index(forms, "forms")
            
            # Create other indexes for forms collection
            self._create_index_safely(forms, "submission_timestamp")
            self._create_index_safely(forms, "created_at")
            self._create_index_safely(forms, "last_updated")
            
            print(f"📊 MongoDB collections '{self.conversations_collection_name}' and '{self.forms_collection_name}' set up successfully")
            
        except Exception as e:
            print(f"⚠️ Error setting up MongoDB collections: {e}")
    
    def _ensure_unique_user_index(self, collection, collection_type):
        """Ensure user_id has a unique index, handling existing non-unique indexes"""
        try:
            # Check existing indexes
            existing_indexes = collection.list_indexes()
            user_index_exists = False
            user_index_is_unique = False
            
            # Check for both old session_id and new user_id indexes
            for index in existing_indexes:
                index_keys = index.get('key', {})
                if 'user_id' in index_keys and index_keys.get('user_id') == 1:
                    user_index_exists = True
                    user_index_is_unique = index.get('unique', False)
                    break
                elif 'session_id' in index_keys and index_keys.get('session_id') == 1:
                    # Drop old session_id indexes
                    print(f"🔄 Dropping old session_id index on {collection_type} collection...")
                    try:
                        collection.drop_index("session_id_1")
                    except:
                        pass
                    try:
                        collection.drop_index("session_id_unique_idx")
                    except:
                        pass
            
            if user_index_exists and not user_index_is_unique:
                # Drop the existing non-unique index
                print(f"🔄 Dropping existing non-unique user_id index on {collection_type} collection...")
                collection.drop_index("user_id_1")
                user_index_exists = False
            
            if not user_index_exists:
                # Create unique index with explicit name to avoid conflicts
                collection.create_index(
                    "user_id", 
                    unique=True, 
                    name="user_id_unique_idx"
                )
                print(f"✅ Created unique user_id index on {collection_type} collection")
            elif user_index_is_unique:
                print(f"✅ Unique user_id index already exists on {collection_type} collection")
                
        except Exception as e:
            print(f"⚠️ Could not ensure unique user_id index on {collection_type}: {e}")
            print(f"   {collection_type.capitalize()} collection will work without unique constraint")
    
    def _create_index_safely(self, collection, field_name):
        """Create an index safely, ignoring if it already exists"""
        try:
            collection.create_index(field_name)
        except Exception as e:
            # Index probably already exists, which is fine
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                pass  # Ignore duplicate index errors
            else:
                print(f"⚠️ Warning: Could not create index on {field_name}: {e}")
    
    def log_conversation(self, user_message: str, bot_response: str, 
                        context: str = "main_chat", section: Optional[str] = None, 
                        model_used: Optional[str] = None, user_id: Optional[str] = None, 
                        chatbot_type: Optional[str] = None, metadata: Optional[dict] = None) -> bool:
        """
        Accumulate conversation exchanges and update/create complete conversation per user.
        Ensures one conversation document per user_id by using upsert operations.
        Now includes chatbot_type (normal/expert) for each conversation exchange.
        Metadata parameter allows storing additional fields like questiontype.
        """
        if not self.connected or self.db is None:
            return False
            
        try:
            # User ID is required - generate one if not provided (should not happen in normal flow)
            if not user_id:
                print("⚠️ Warning: No user_id provided for conversation logging")
                user_id = self._generate_user_id()
            
            timestamp = datetime.now()
            
            # Create a conversation exchange object
            conversation_exchange = {
                "timestamp": timestamp,
                "user_message": user_message,
                "bot_response": bot_response,
                "model_used": model_used,
                "context": context,
                "section": section,
                "chatbot_type": chatbot_type  # Store which chatbot type was used (normal/expert)
            }
            
            # Use upsert to ensure only one conversation document per user_id
            # This is more robust than find + update/insert separately
            result = self.db[self.conversations_collection_name].update_one(
                {"user_id": user_id},  # Filter
                {
                    "$push": {"conversation_history": conversation_exchange},
                    "$inc": {"total_exchanges": 1},  # Increment counter
                    "$set": {"last_updated": timestamp},
                    "$setOnInsert": {  # Only set these values when creating new document
                        "user_id": user_id,
                        "created_at": timestamp,
                        "user_ip": self._get_user_ip()
                    }
                },
                upsert=True  # Create document if it doesn't exist
            )
            
            if result.upserted_id:
                print(f"📝 New conversation document created for user: {user_id[:8]}...")
            elif result.modified_count > 0:
                print(f"📝 Conversation updated for user: {user_id[:8]}...")
            else:
                print(f"⚠️ No changes made to conversation for user: {user_id[:8]}...")
            
            return True
                
        except Exception as e:
            print(f"❌ Error logging conversation to MongoDB: {e}")
            return False
    
    def save_form_submission(self, user_id: str, data_to_update: Dict[str, Any]) -> bool:
        """
        Update a single document for a given user_id with new form data.
        Uses upsert=True to ensure only one form document per user_id.
        This guarantees one entry per user in the forms collection.
        """
        if not self.connected or self.db is None:
            print("⚠️ MongoDB not connected. Cannot save form submission.")
            return False
            
        if not user_id:
            print("❌ Error: user_id is required for form submission")
            return False
            
        try:
            # The filter to find the document for the current user
            query = {"user_id": user_id}
            
            # Ensure 'user_id' is not in the update payload to avoid conflicts
            data_to_update.pop('user_id', None)
            # Also remove old session_id if present
            data_to_update.pop('session_id', None)
            
            # Add submission timestamp to track when data was last updated
            data_to_update["submission_timestamp"] = datetime.now()

            # The update operation using $set to add/update fields
            # and $setOnInsert to set values only when a new document is created
            update = {
                "$set": {
                    **data_to_update,  # Unpack all new form data
                    "last_updated": datetime.now()
                },
                "$setOnInsert": {
                    "user_id": user_id,
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
                print(f"📋 New form document created for user: {user_id[:8]}...")
                return True
            elif result.modified_count > 0:
                print(f"✅ Form data upserted to MongoDB (User: {user_id[:8]}...)")
                return True
            else:
                # This case can happen if the data submitted is identical to what's already stored
                print(f"📋 No changes to form document for user: {user_id[:8]}... (data unchanged)")
                return True
                
        except Exception as e:
            print(f"❌ Error saving form submission to MongoDB: {e}")
            return False
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get information about a specific user including both conversation and form data.
        Useful for verifying user uniqueness and data integrity.
        """
        if not self.connected or self.db is None:
            return {"error": "MongoDB not connected"}
            
        try:
            # Get conversation data for this user
            conversation_doc = self.db[self.conversations_collection_name].find_one(
                {"user_id": user_id}
            )
            
            # Get form data for this user  
            form_doc = self.db[self.forms_collection_name].find_one(
                {"user_id": user_id}
            )
            
            return {
                "user_id": user_id,
                "conversation_exists": conversation_doc is not None,
                "form_exists": form_doc is not None,
                "conversation_exchanges": conversation_doc.get("total_exchanges", 0) if conversation_doc else 0,
                "conversation_created": conversation_doc.get("created_at") if conversation_doc else None,
                "form_created": form_doc.get("created_at") if form_doc else None,
                "last_conversation_update": conversation_doc.get("last_updated") if conversation_doc else None,
                "last_form_update": form_doc.get("last_updated") if form_doc else None
            }
            
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
            return {"error": str(e)}
    
    def verify_user_uniqueness(self) -> Dict[str, Any]:
        """
        Verify that each user_id appears only once in both collections.
        Returns statistics about user uniqueness.
        """
        if not self.connected or self.db is None:
            return {"error": "MongoDB not connected"}
            
        try:
            # Check conversations collection
            conversation_pipeline = [
                {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}}  # Find duplicates
            ]
            conversation_duplicates = list(self.db[self.conversations_collection_name].aggregate(conversation_pipeline))
            
            # Check forms collection
            forms_pipeline = [
                {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}}  # Find duplicates
            ]
            form_duplicates = list(self.db[self.forms_collection_name].aggregate(forms_pipeline))
            
            # Get total counts
            total_conversations = self.db[self.conversations_collection_name].count_documents({})
            total_forms = self.db[self.forms_collection_name].count_documents({})
            unique_users_conversations = len(list(self.db[self.conversations_collection_name].distinct("user_id")))
            unique_users_forms = len(list(self.db[self.forms_collection_name].distinct("user_id")))
            
            return {
                "conversations_collection": {
                    "total_documents": total_conversations,
                    "unique_users": unique_users_conversations,
                    "has_duplicates": len(conversation_duplicates) > 0,
                    "duplicate_users": conversation_duplicates
                },
                "forms_collection": {
                    "total_documents": total_forms,
                    "unique_users": unique_users_forms,
                    "has_duplicates": len(form_duplicates) > 0,
                    "duplicate_users": form_duplicates
                },
                "summary": {
                    "users_with_conversations": unique_users_conversations,
                    "users_with_forms": unique_users_forms,
                    "data_integrity_ok": len(conversation_duplicates) == 0 and len(form_duplicates) == 0
                }
            }
            
        except Exception as e:
            print(f"❌ Error verifying user uniqueness: {e}")
            return {"error": str(e)}
    
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
    
    def _generate_user_id(self) -> str:
        """Generate a user ID for tracking users"""
        import uuid
        return str(uuid.uuid4())[:8]  # Short user ID
    
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