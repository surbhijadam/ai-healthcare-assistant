from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from backend.db.base import Base, utcnow


class AuditLog(Base):
    """Clinical governance and security audit log entity (FR-08.2)."""
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # LOGIN_SUCCESS, LOGIN_FAILED, REPORT_UPLOAD, etc.
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # SUCCESS, FAILED
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, server_default=func.now())

    # Relationship
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action='{self.action}' status='{self.status}'>"
