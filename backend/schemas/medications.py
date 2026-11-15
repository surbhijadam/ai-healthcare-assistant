from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class MedicationBase(BaseModel):
    medication_name: str = Field(..., min_length=1, max_length=150)
    dosage: str = Field(..., min_length=1, max_length=50)  # e.g., "500 mg"
    frequency: str = Field(..., min_length=1, max_length=50)  # e.g., "Twice daily"
    start_date: date
    end_date: Optional[date] = None
    instructions: Optional[str] = None
    category: Optional[str] = None


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    instructions: Optional[str] = None
    is_active: Optional[bool] = None


class MedicationResponse(MedicationBase):
    id: int
    user_id: int
    is_active: bool = True
    today_status: str = "Upcoming"  # Upcoming, Taken, Skipped


class DoseToggleRequest(BaseModel):
    status: str = Field(..., pattern="^(Taken|Skipped|Upcoming)$")
    log_date: Optional[date] = None
