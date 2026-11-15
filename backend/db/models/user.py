from datetime import date, datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Float,
    Text,
    JSON,
    ForeignKey,
    func
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from backend.db.base import Base, utcnow


class User(Base):
    """User account entity for authentication and authorization (FR-01.1 - FR-01.3)."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="ROLE_USER")  # ROLE_USER, ROLE_ADMIN
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        onupdate=utcnow
    )

    # Relationships with cascading lifecycle
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    medical_reports: Mapped[List["MedicalReport"]] = relationship(
        "MedicalReport",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    medications: Mapped[List["Medication"]] = relationship(
        "Medication",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"


class UserProfile(Base):
    """Patient clinical and demographic profile entity (FR-01.4)."""
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    blood_group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    allergies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chronic_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Extended health profile checklist fields
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    preferred_language: Mapped[Optional[str]] = mapped_column(String(50), default="English", nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), default="India", nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    lifestyle_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationship to user
    user: Mapped["User"] = relationship("User", back_populates="profile")

    @property
    def calculated_age(self) -> Optional[int]:
        if not self.date_of_birth:
            return None
        today = date.today()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @property
    def calculated_bmi(self) -> Optional[float]:
        if not self.height_cm or not self.weight_kg or self.height_cm <= 0:
            return None
        height_m = self.height_cm / 100.0
        return round(self.weight_kg / (height_m ** 2), 1)

    def __repr__(self) -> str:
        return f"<UserProfile id={self.id} user_id={self.user_id} name={self.full_name}>"
