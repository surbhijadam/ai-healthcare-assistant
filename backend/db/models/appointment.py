from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from backend.db.base import Base


class Appointment(Base):
    """Clinical doctor appointment entity (FR-05.1 - FR-05.3)."""
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    doctor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    clinic_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    appointment_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="upcoming", nullable=False)  # upcoming, completed, cancelled
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="appointments")

    def __repr__(self) -> str:
        return f"<Appointment id={self.id} user_id={self.user_id} doctor='{self.doctor_name}'>"
