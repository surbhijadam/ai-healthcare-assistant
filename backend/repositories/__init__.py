from backend.repositories.base import BaseRepository
from backend.repositories.user_repo import user_repo, UserRepository
from backend.repositories.report_repo import report_repo, ReportRepository
from backend.repositories.medication_repo import medication_repo, MedicationRepository
from backend.repositories.appointment_repo import appointment_repo, AppointmentRepository
from backend.repositories.conversation_repo import conversation_repo, ConversationRepository
from backend.repositories.knowledge_repo import knowledge_repo, KnowledgeRepository
from backend.repositories.audit_repo import audit_repo, AuditRepository

__all__ = [
    "BaseRepository",
    "user_repo",
    "UserRepository",
    "report_repo",
    "ReportRepository",
    "medication_repo",
    "MedicationRepository",
    "appointment_repo",
    "AppointmentRepository",
    "conversation_repo",
    "ConversationRepository",
    "knowledge_repo",
    "KnowledgeRepository",
    "audit_repo",
    "AuditRepository",
]
