import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from src.config import Config, BASE_DIR

class BaseNoSQLDatabase:
    """Interface for NoSQL Database operations"""
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
        
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError
        
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError
        
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError
        
    def create_session(self, user_id: str, title: str = "New Legal Inquiry") -> Dict[str, Any]:
        raise NotImplementedError
        
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError
        
    def list_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError
        
    def update_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        raise NotImplementedError
        
    def delete_session(self, session_id: str) -> bool:
        raise NotImplementedError
        
    def add_message(self, session_id: str, user_id: str, role: str, content: str, structured_response: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError
        
    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError
        
    def log_query(self, user_id: Optional[str], session_id: Optional[str], query: str, matched_sections: List[str], processing_time_ms: int) -> Dict[str, Any]:
        raise NotImplementedError

    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        raise NotImplementedError


class TinyDocNoSQLDatabase(BaseNoSQLDatabase):
    """
    Embedded pure-Python NoSQL document database using TinyDB.
    Requires zero external services, perfect for local prototyping and instant setup.
    """
    def __init__(self, db_path: Optional[str] = None):
        from tinydb import TinyDB, Query
        
        path = Path(db_path or Config.NOSQL_STORAGE_PATH)
        path.mkdir(parents=True, exist_ok=True)
        self.file_path = path / "nosql_store.json"
        
        self.db = TinyDB(str(self.file_path))
        self.users_table = self.db.table("users")
        self.sessions_table = self.db.table("sessions")
        self.messages_table = self.db.table("messages")
        self.audit_table = self.db.table("audit_logs")
        self.query = Query()
        self.backend_name = "TinyDB (Embedded NoSQL)"

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user = dict(user_data)
        if "id" not in user:
            user["id"] = str(uuid.uuid4())
        if "created_at" not in user:
            user["created_at"] = datetime.utcnow().isoformat()
        self.users_table.insert(user)
        return user

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        res = self.users_table.search(self.query.id == user_id)
        return res[0] if res else None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        res = self.users_table.search(self.query.username == username.strip().lower())
        return res[0] if res else None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        res = self.users_table.search(self.query.email == email.strip().lower())
        return res[0] if res else None

    def create_session(self, user_id: str, title: str = "New Legal Inquiry") -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        session = {
            "id": session_id,
            "user_id": user_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "message_count": 0
        }
        self.sessions_table.insert(session)
        return session

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        res = self.sessions_table.search(self.query.id == session_id)
        return res[0] if res else None

    def list_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        sessions = self.sessions_table.search(self.query.user_id == user_id)
        sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
        return sessions

    def update_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        update_data["updated_at"] = datetime.utcnow().isoformat()
        updated = self.sessions_table.update(update_data, self.query.id == session_id)
        return len(updated) > 0

    def delete_session(self, session_id: str) -> bool:
        self.messages_table.remove(self.query.session_id == session_id)
        deleted = self.sessions_table.remove(self.query.id == session_id)
        return len(deleted) > 0

    def add_message(self, session_id: str, user_id: str, role: str, content: str, structured_response: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        msg_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        msg = {
            "id": msg_id,
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "structured_response": structured_response,
            "created_at": now
        }
        self.messages_table.insert(msg)
        
        # Update session timestamp & count
        session = self.get_session(session_id)
        if session:
            count = session.get("message_count", 0) + 1
            # Auto-title if it's the first user message
            title = session.get("title", "New Legal Inquiry")
            if role == "user" and (title == "New Legal Inquiry" or not title):
                title = (content[:45] + "...") if len(content) > 45 else content
            self.update_session(session_id, {"updated_at": now, "message_count": count, "title": title})
            
        return msg

    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        messages = self.messages_table.search(self.query.session_id == session_id)
        messages.sort(key=lambda m: m.get("created_at", ""))
        return messages

    def log_query(self, user_id: Optional[str], session_id: Optional[str], query: str, matched_sections: List[str], processing_time_ms: int) -> Dict[str, Any]:
        log_entry = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "matched_sections": matched_sections,
            "processing_time_ms": processing_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.audit_table.insert(log_entry)
        return log_entry

    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        all_logs = self.audit_table.all()
        all_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return all_logs[:limit]


class MongoNoSQLDatabase(BaseNoSQLDatabase):
    """MongoDB implementation of NoSQL Database"""
    def __init__(self, uri: str, db_name: str = "legal_aid_db"):
        from pymongo import MongoClient
        self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        # Test connection
        self.client.admin.command('ping')
        self.db = self.client[db_name]
        self.users = self.db["users"]
        self.sessions = self.db["sessions"]
        self.messages = self.db["messages"]
        self.audit = self.db["audit_logs"]
        self.backend_name = "MongoDB (NoSQL Cluster)"
        
        # Ensure indexes
        self.users.create_index("username", unique=True)
        self.users.create_index("email", unique=True)
        self.sessions.create_index("user_id")
        self.messages.create_index("session_id")

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user = dict(user_data)
        if "id" not in user:
            user["id"] = str(uuid.uuid4())
        if "created_at" not in user:
            user["created_at"] = datetime.utcnow().isoformat()
        user["_id"] = user["id"]
        self.users.insert_one(user)
        user.pop("_id", None)
        return user

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        user = self.users.find_one({"id": user_id}, {"_id": 0})
        return user

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        user = self.users.find_one({"username": username.strip().lower()}, {"_id": 0})
        return user

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        user = self.users.find_one({"email": email.strip().lower()}, {"_id": 0})
        return user

    def create_session(self, user_id: str, title: str = "New Legal Inquiry") -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        session = {
            "_id": session_id,
            "id": session_id,
            "user_id": user_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "message_count": 0
        }
        self.sessions.insert_one(session)
        session.pop("_id", None)
        return session

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self.sessions.find_one({"id": session_id}, {"_id": 0})

    def list_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        cursor = self.sessions.find({"user_id": user_id}, {"_id": 0}).sort("updated_at", -1)
        return list(cursor)

    def update_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        update_data["updated_at"] = datetime.utcnow().isoformat()
        res = self.sessions.update_one({"id": session_id}, {"$set": update_data})
        return res.modified_count > 0

    def delete_session(self, session_id: str) -> bool:
        self.messages.delete_many({"session_id": session_id})
        res = self.sessions.delete_one({"id": session_id})
        return res.deleted_count > 0

    def add_message(self, session_id: str, user_id: str, role: str, content: str, structured_response: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        msg_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        msg = {
            "_id": msg_id,
            "id": msg_id,
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "structured_response": structured_response,
            "created_at": now
        }
        self.messages.insert_one(msg)
        msg.pop("_id", None)
        
        session = self.get_session(session_id)
        if session:
            count = session.get("message_count", 0) + 1
            title = session.get("title", "New Legal Inquiry")
            if role == "user" and (title == "New Legal Inquiry" or not title):
                title = (content[:45] + "...") if len(content) > 45 else content
            self.update_session(session_id, {"updated_at": now, "message_count": count, "title": title})
            
        return msg

    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        cursor = self.messages.find({"session_id": session_id}, {"_id": 0}).sort("created_at", 1)
        return list(cursor)

    def log_query(self, user_id: Optional[str], session_id: Optional[str], query: str, matched_sections: List[str], processing_time_ms: int) -> Dict[str, Any]:
        entry = {
            "_id": str(uuid.uuid4()),
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "matched_sections": matched_sections,
            "processing_time_ms": processing_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.audit.insert_one(entry)
        entry.pop("_id", None)
        return entry

    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = self.audit.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
        return list(cursor)


_db_instance: Optional[BaseNoSQLDatabase] = None

def get_nosql_db() -> BaseNoSQLDatabase:
    """
    Factory providing singleton NoSQL database instance.
    Attempts MongoDB first if configured; falls back automatically to TinyDB.
    """
    global _db_instance
    if _db_instance is not None:
        return _db_instance

    backend_pref = Config.NOSQL_BACKEND.lower()
    
    if backend_pref != "tinydb":
        try:
            print(f"[INFO] Connecting to MongoDB at {Config.MONGODB_URI}...")
            mongo_db = MongoNoSQLDatabase(Config.MONGODB_URI, Config.MONGODB_DB_NAME)
            print(f"[OK] Connected to MongoDB ({Config.MONGODB_DB_NAME})")
            _db_instance = mongo_db
            return _db_instance
        except Exception as e:
            print(f"[NOTE] MongoDB not reachable ({e}). Switching to embedded NoSQL storage.")

    # Fallback to TinyDocNoSQLDatabase
    print(f"[INFO] Initializing Embedded NoSQL Storage at {Config.NOSQL_STORAGE_PATH}...")
    _db_instance = TinyDocNoSQLDatabase()
    print(f"[OK] Embedded NoSQL Database active.")
    return _db_instance
