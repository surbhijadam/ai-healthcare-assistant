from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[int] = None
    stream: bool = False


class DocumentCitation(BaseModel):
    document_title: str
    chunk_id: Optional[int] = None
    similarity_score: Optional[float] = None


class ChatQueryResponse(BaseModel):
    conversation_id: int
    message_id: int
    answer: str
    emergency_intercepted: bool = False
    emergency_warning: Optional[str] = None
    sources_cited: List[DocumentCitation] = []
    disclaimer: str = "Educational information only. Not a medical diagnosis or prescription."


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_role: str  # user, assistant, system
    content: str
    sources_used: Optional[List[Dict[str, Any]]] = None
    created_at: datetime


class ConversationCreateRequest(BaseModel):
    title: Optional[str] = "Health Consultation"


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    message_count: int = 0
