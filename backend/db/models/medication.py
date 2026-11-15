from datetime import date
from typing import Optional
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    Date,
    Text,
    ForeignKey
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from backend.db.base import Base


class Medication(Base):
    """Prescription and medication adherence entity (FR-04.1 - FR-04.4, FR-06.1 - FR-06.2)."""
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    medication_name: Mapped[str] = mapped_column(String(150), nullable=False)
    dosage: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "500 mg", "1 puff"
    frequency: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "Twice daily"
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    today_status: Mapped[str] = mapped_column(String(20), default="Upcoming", nullable=False)  # Upcoming, Taken, Skipped

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="medications")

    def __repr__(self) -> str:
        return f"<Medication id={self.id} user_id={self.user_id} name='{self.medication_name}'>"
