import os
import sys
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import mimetypes

# Ensure correct MIME types on Windows
mimetypes.init()
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("application/json", ".json")

# Ensure UTF-8 output
if sys.platform.startswith("win"):
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from src.config import Config, BASE_DIR
from src.db.nosql_manager import get_nosql_db, BaseNoSQLDatabase
from src.auth.security import verify_password, get_password_hash, create_access_token
from src.auth.dependencies import get_current_user, get_optional_user
from src.pipeline.complete_pipeline import CompleteLegalPipeline
from src.models.legal_schemas import (
    UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse,
    SessionCreateRequest, SessionResponse, SessionDetailResponse, MessageResponse,
    QueryRequest
)

# Initialize FastAPI application
app = FastAPI(
    title="Smart Legal Aid Assistance API",
    description="AI-powered legal awareness platform using Grok LLM, ChromaDB vector store, and NoSQL session storage.",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton pipeline instance
_pipeline_instance: Optional[CompleteLegalPipeline] = None

def get_pipeline() -> CompleteLegalPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        print("[INFO] Initializing Complete Legal Pipeline...")
        _pipeline_instance = CompleteLegalPipeline()
    return _pipeline_instance


# ==============================================================================
# HEALTH & METRICS ENDPOINTS
# ==============================================================================

@app.get("/api/health")
async def health_check(db: BaseNoSQLDatabase = Depends(get_nosql_db)):
    """System health check and configuration overview"""
    pipeline = get_pipeline()
    vector_store = pipeline.legal_pipeline.retriever.vector_store
    
    vector_count = 0
    if hasattr(vector_store, "collection"):
        vector_count = vector_store.collection.count()
    elif hasattr(vector_store, "index") and vector_store.index is not None:
        vector_count = vector_store.index.ntotal

    return {
        "status": "healthy",
        "llm_provider": Config.LLM_PROVIDER,
        "grok_model": Config.GROK_MODEL,
        "has_grok_key": bool(Config.GROK_API_KEY),
        "vector_database": Config.VECTOR_DB_TYPE,
        "chroma_cloud_connected": bool(Config.CHROMA_API_KEY and Config.CHROMA_TENANT),
        "indexed_sections_count": vector_count,
        "nosql_database": getattr(db, "backend_name", "NoSQL Document DB"),
        "timestamp": datetime.utcnow().isoformat()
    }


# ==============================================================================
# AUTHENTICATION ENDPOINTS
# ==============================================================================

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(req: UserRegisterRequest, db: BaseNoSQLDatabase = Depends(get_nosql_db)):
    """Register a new user account"""
    username = req.username.strip().lower()
    email = req.email.strip().lower()
    
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
    if db.get_user_by_username(username):
        raise HTTPException(status_code=400, detail="Username is already registered")
    if db.get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email is already registered")
        
    hashed_pwd = get_password_hash(req.password)
    user_data = {
        "username": username,
        "email": email,
        "hashed_password": hashed_pwd,
        "full_name": req.full_name or username
    }
    
    user = db.create_user(user_data)
    user_safe = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user.get("full_name", ""),
        "created_at": user.get("created_at", "")
    }
    
    token = create_access_token({"sub": user["id"], "username": user["username"]})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(**user_safe)
    )

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, db: BaseNoSQLDatabase = Depends(get_nosql_db)):
    """Authenticate user and return JWT bearer token"""
    username = req.username.strip().lower()
    user = db.get_user_by_username(username)
    if not user:
        # Check if email was entered
        user = db.get_user_by_email(username)
        
    if not user or not verify_password(req.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )
        
    user_safe = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user.get("full_name", ""),
        "created_at": user.get("created_at", "")
    }
    
    token = create_access_token({"sub": user["id"], "username": user["username"]})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(**user_safe)
    )

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)):
    """Get authenticated user profile"""
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name", ""),
        created_at=user.get("created_at", "")
    )


# ==============================================================================
# USER SESSIONS ENDPOINTS (NoSQL Stored)
# ==============================================================================

@app.post("/api/sessions", response_model=SessionResponse)
async def create_user_session(
    req: SessionCreateRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: BaseNoSQLDatabase = Depends(get_nosql_db)
):
    """Create a new legal inquiry session for authenticated user"""
    title = (req.title or "New Legal Inquiry").strip()
    session = db.create_session(user_id=user["id"], title=title)
    return SessionResponse(**session)

@app.get("/api/sessions", response_model=List[SessionResponse])
async def list_user_sessions(
    user: Dict[str, Any] = Depends(get_current_user),
    db: BaseNoSQLDatabase = Depends(get_nosql_db)
):
    """Retrieve all inquiry sessions for current user"""
    sessions = db.list_user_sessions(user_id=user["id"])
    return [SessionResponse(**s) for s in sessions]

@app.get("/api/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session_details(
    session_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    db: BaseNoSQLDatabase = Depends(get_nosql_db)
):
    """Retrieve session details and full history of queries/responses"""
    session = db.get_session(session_id)
    if not session or session.get("user_id") != user["id"]:
        raise HTTPException(status_code=404, detail="Session not found")
        
    messages = db.get_session_messages(session_id)
    return SessionDetailResponse(
        session=SessionResponse(**session),
        messages=[MessageResponse(**m) for m in messages]
    )

@app.delete("/api/sessions/{session_id}")
async def delete_user_session(
    session_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    db: BaseNoSQLDatabase = Depends(get_nosql_db)
):
    """Delete a session and all its messages from the NoSQL database"""
    session = db.get_session(session_id)
    if not session or session.get("user_id") != user["id"]:
        raise HTTPException(status_code=404, detail="Session not found")
        
    db.delete_session(session_id)
    return {"status": "success", "message": "Session deleted successfully"}


# ==============================================================================
# PIPELINE QUERY ENDPOINTS
# ==============================================================================

@app.post("/api/sessions/{session_id}/query")
async def query_in_session(
    session_id: str,
    req: QueryRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: BaseNoSQLDatabase = Depends(get_nosql_db),
    pipeline: CompleteLegalPipeline = Depends(get_pipeline)
):
    """
    Execute legal reasoning pipeline within a persistent session.
    Stores user input and structured RAG output in the NoSQL database.
    """
    session = db.get_session(session_id)
    if not session or session.get("user_id") != user["id"]:
        raise HTTPException(status_code=404, detail="Session not found")
        
    user_query = req.query.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    # Store user query message
    user_msg = db.add_message(
        session_id=session_id,
        user_id=user["id"],
        role="user",
        content=user_query
    )
    
    # Run through full RAG pipeline
    result = await pipeline.process(user_query)
    
    # Store assistant structured response message
    assistant_msg = db.add_message(
        session_id=session_id,
        user_id=user["id"],
        role="assistant",
        content=result.get("summary", ""),
        structured_response=result
    )
    
    # Audit log
    sections = [s.get("section") for s in result.get("legal_analysis", {}).get("applicable_sections", [])]
    db.log_query(
        user_id=user["id"],
        session_id=session_id,
        query=user_query,
        matched_sections=sections,
        processing_time_ms=result.get("processing_time_ms", 0)
    )
    
    return {
        "session_id": session_id,
        "user_message_id": user_msg["id"],
        "assistant_message_id": assistant_msg["id"],
        "response": result
    }

@app.post("/api/query")
async def direct_query(
    req: QueryRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user),
    db: BaseNoSQLDatabase = Depends(get_nosql_db),
    pipeline: CompleteLegalPipeline = Depends(get_pipeline)
):
    """
    Direct legal awareness query for guest/quick testing.
    """
    user_query = req.query.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    result = await pipeline.process(user_query)
    
    user_id = user["id"] if user else None
    sections = [s.get("section") for s in result.get("legal_analysis", {}).get("applicable_sections", [])]
    db.log_query(
        user_id=user_id,
        session_id=None,
        query=user_query,
        matched_sections=sections,
        processing_time_ms=result.get("processing_time_ms", 0)
    )
    
    return {
        "status": "success",
        "response": result
    }


# ==============================================================================
# STATIC FRONTEND SERVING
# ==============================================================================

static_dir = BASE_DIR / "static"
if static_dir.exists():
    # Mount Vite assets directory directly (e.g. /assets/index-*.js)
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # Mount static directory for general assets
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/favicon.svg")
    async def serve_favicon():
        fav = static_dir / "favicon.svg"
        if fav.exists():
            return FileResponse(str(fav), media_type="image/svg+xml")
        raise HTTPException(status_code=404)

    @app.get("/")
    async def serve_index():
        return FileResponse(str(static_dir / "index.html"), media_type="text/html")

    # Fallback for client-side routing and static files
    @app.get("/{full_path:path}")
    async def serve_spa_or_file(full_path: str):
        candidate = static_dir / full_path
        if candidate.is_file():
            mime, _ = mimetypes.guess_type(str(candidate))
            return FileResponse(str(candidate), media_type=mime or "application/octet-stream")
        return FileResponse(str(static_dir / "index.html"), media_type="text/html")


if __name__ == "__main__":
    import uvicorn
    print(f"[INFO] Starting Smart Legal Aid Assistance on http://{Config.HOST}:{Config.PORT}")
    uvicorn.run("app:app", host=Config.HOST, port=Config.PORT, reload=False)
