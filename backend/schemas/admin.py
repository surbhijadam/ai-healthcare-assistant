from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl


class PlatformStatsResponse(BaseModel):
    total_registered_users: int = 2480
    active_users: int = 1126
    knowledge_base_documents: int = 84
    assistant_interactions_30_days: int = 8420


class SystemActivityItem(BaseModel):
    title: str
    timestamp_desc: str
    category: str


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str  # LOGIN_SUCCESS, LOGIN_FAILED, REPORT_UPLOAD, etc.
    ip_address: Optional[str] = None
    status: str  # SUCCESS, FAILED
    timestamp: datetime


class KnowledgeDocCreate(BaseModel):
    title: str
    category: Optional[str] = "Clinical Guideline"
    content: Optional[str] = None
    source_url: Optional[str] = None


class KnowledgeDocResponse(BaseModel):
    id: int
    title: str
    category: Optional[str] = None
    status: str = "Reviewed"
    total_chunks: Optional[int] = None
    created_at: datetime
