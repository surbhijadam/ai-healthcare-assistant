from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LabParameter(BaseModel):
    test_name: str
    observed_value: str
    reference_range: str
    unit: str
    status: str = "Normal"  # Normal, Elevated, Low
    explanation: Optional[str] = None


class ReportUploadResponse(BaseModel):
    report_id: int
    file_name: str
    report_type: Optional[str] = "Routine Clinical Panel"
    parsed_parameters: List[LabParameter]
    ai_summary: str
    doctor_discussion_points: List[str] = []
    uploaded_at: datetime


class ReportListItem(BaseModel):
    id: int
    file_name: str
    report_type: Optional[str] = None
    uploaded_at: datetime
    status: str = "Reviewed"
