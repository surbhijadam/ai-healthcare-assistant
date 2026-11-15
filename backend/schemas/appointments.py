from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AppointmentBase(BaseModel):
    doctor_name: str = Field(..., min_length=2, max_length=100)
    specialty: Optional[str] = None
    clinic_name: Optional[str] = None
    appointment_datetime: datetime
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    doctor_name: Optional[str] = None
    specialty: Optional[str] = None
    clinic_name: Optional[str] = None
    appointment_datetime: Optional[datetime] = None
    status: Optional[str] = None  # upcoming, completed, cancelled
    notes: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    id: int
    user_id: int
    status: str = "upcoming"
