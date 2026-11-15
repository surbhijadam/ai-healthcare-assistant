from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class PatientProfileBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    city: Optional[str] = None
    country: Optional[str] = None


class PatientProfileCreate(PatientProfileBase):
    pass


class PatientProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    city: Optional[str] = None
    country: Optional[str] = None


class PatientProfileResponse(PatientProfileBase):
    id: int
    user_id: int
    calculated_age: Optional[int] = None
    calculated_bmi: Optional[float] = None
