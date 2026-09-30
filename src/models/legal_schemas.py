from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

# ==============================================================================
# IPC & LEGAL DOMAIN SCHEMAS
# ==============================================================================

class IPCSection(BaseModel):
    """IPC section model"""
    section_number: str
    title: str
    full_text: str
    main_text: str
    illustrations: Optional[str] = ""
    
    # Legal elements
    essential_elements: List[str] = Field(default_factory=list)
    punishments: List[Dict[str, Any]] = Field(default_factory=list)
    cognizable: Optional[bool] = None
    bailable: Optional[bool] = None
    compoundable: Optional[bool] = None
    jurisdiction: Optional[str] = None

class Scenario(BaseModel):
    """Structured scenario extracted from user narrative"""
    actors: List[str] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)
    victim: str = ""
    objects: List[str] = Field(default_factory=list)
    location: str = ""
    harm_types: List[str] = Field(default_factory=list)
    legal_categories: List[str] = Field(default_factory=list)
    intent_indicators: List[str] = Field(default_factory=list)
    urgency: str = "medium"
    witnesses: List[str] = Field(default_factory=list)
    evidence_mentioned: List[str] = Field(default_factory=list)
    original_text: str = ""

class LegalMatch(BaseModel):
    """A matched IPC section with legal validation and reasoning"""
    section: IPCSection
    relevance_score: float = Field(ge=0, le=1)
    match_reasons: List[str] = Field(default_factory=list)
    missing_elements: List[str] = Field(default_factory=list)
    confidence: str = Field(description="HIGH/MEDIUM/LOW")

class LegalMappingResult(BaseModel):
    """Output of legal mapping phase"""
    scenario: Scenario
    matches: List[LegalMatch] = Field(default_factory=list)
    total_sections_considered: int = 0
    processing_time_ms: int = 0

class IntentClassification(BaseModel):
    """Step 2: Intent and safety classification"""
    is_allowed: bool = True
    intent_type: str = "incident_awareness"  # 'incident_awareness', 'section_lookup', 'prohibited_evasion'
    reason: str = "Query is safe for legal awareness guidance"

# ==============================================================================
# AUTH & USER SCHEMAS
# ==============================================================================

class UserRegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = ""

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = ""
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ==============================================================================
# SESSION & CHAT SCHEMAS
# ==============================================================================

class SessionCreateRequest(BaseModel):
    title: Optional[str] = "New Legal Inquiry"

class SessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0

class MessageResponse(BaseModel):
    id: str
    session_id: str
    user_id: str
    role: str
    content: str
    structured_response: Optional[Dict[str, Any]] = None
    created_at: str

class SessionDetailResponse(BaseModel):
    session: SessionResponse
    messages: List[MessageResponse]

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
