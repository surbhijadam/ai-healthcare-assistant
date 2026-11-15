from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    JSON,
    ForeignKey,
    func
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from backend.db.base import Base, utcnow


class MedicalReport(Base):
    """Laboratory and diagnostic report entity (FR-02.1 - FR-02.5, FR-05.6)."""
    __tablename__ = "medical_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    report_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    extracted_raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parsed_parameters: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    doctor_discussion_points: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Reviewed", nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, server_default=func.now())

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="medical_reports")

    def __repr__(self) -> str:
        return f"<MedicalReport id={self.id} user_id={self.user_id} file='{self.file_name}'>"
