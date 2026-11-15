from fastapi import APIRouter
from backend.api.v1.endpoints import (
    health,
    auth,
    profile,
    chat,
    reports,
    medications,
    appointments,
    admin,
)

api_router = APIRouter()

# Health and System diagnostic endpoints
api_router.include_router(health.router, tags=["Health & System"])

# Authentication endpoints (FR-01.1 to FR-01.3)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Patient Medical Profile endpoints (FR-01.4)
api_router.include_router(profile.router, prefix="/profile", tags=["Patient Profile"])

# AI Chat & Emergency Triage Filter endpoints (FR-03.1 to FR-03.5, US-03)
api_router.include_router(chat.router, prefix="/chat", tags=["AI Health Assistant Chat"])

# Medical Reports & Extraction endpoints (FR-02.1 to FR-02.5, US-02)
api_router.include_router(reports.router, prefix="/reports", tags=["Medical Reports"])

# Medication Tracking & Reminders endpoints (FR-04.1 to FR-04.4, US-04)
api_router.include_router(medications.router, prefix="/medications", tags=["Medications"])

# Doctor Appointments endpoints (FR-05.1 to FR-05.3, US-05)
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])

# Administrator & Clinical Governance endpoints (FR-08.1 to FR-08.4, US-08)
api_router.include_router(admin.router, prefix="/admin", tags=["Admin & Audit"])
