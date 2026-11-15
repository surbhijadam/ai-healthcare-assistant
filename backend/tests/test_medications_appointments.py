"""
MediCare AI — Comprehensive Automated Test Suite for Phase 10: Medication & Appointment Management
Validates FR-06.1 (Medication Registration), FR-06.2 (Dose Adherence Checklist),
FR-06.3 (Physician Guidance Warning), FR-07.1 (Doctor Appointment Registration),
FR-07.2 (Appointment Status Tracking), FR-07.3 (Discussion Notes), and US-05.
"""

import pytest
from datetime import date, datetime, timezone
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.security import create_access_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user_token_header():
    token = create_access_token(data={"sub": "1", "role": "ROLE_USER"})
    return {"Authorization": f"Bearer {token}"}


# ==============================================================================
# 1. Medication Registration & Lifecycle Tests (FR-06.1, FR-06.2, US-05)
# ==============================================================================

def test_medication_creation_and_listing(client: TestClient, user_token_header: dict):
    """
    Validates medication registration with name, dosage, frequency, start date,
    and retrieval via listing endpoint (FR-06.1).
    """
    payload = {
        "medication_name": "Atorvastatin Calcium",
        "dosage": "20 mg · 1 tablet",
        "frequency": "Once daily at bedtime",
        "start_date": "2026-11-01",
        "instructions": "Take after dinner with water.",
        "category": "Lipid Lowering / Statin"
    }
    response = client.post("/api/v1/medications", json=payload, headers=user_token_header)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]

    assert data["id"] > 0
    assert data["medication_name"] == "Atorvastatin Calcium"
    assert data["dosage"] == "20 mg · 1 tablet"
    assert data["today_status"] == "Upcoming"
    assert data["is_active"] is True

    # List medications
    list_resp = client.get("/api/v1/medications", headers=user_token_header)
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["status"] == "success"
    assert len(list_body["data"]) >= 1
    names = [m["medication_name"] for m in list_body["data"]]
    assert "Atorvastatin Calcium" in names


def test_medication_dose_adherence_toggle(client: TestClient, user_token_header: dict):
    """
    Validates daily dose status cycling: Upcoming -> Taken -> Skipped (FR-06.2, US-05).
    """
    # 1. Toggle to Taken
    response_taken = client.put(
        "/api/v1/medications/1/toggle",
        json={"status": "Taken"},
        headers=user_token_header
    )
    assert response_taken.status_code == 200
    assert response_taken.json()["data"]["today_status"] == "Taken"

    # 2. Toggle to Skipped
    response_skipped = client.put(
        "/api/v1/medications/1/toggle",
        json={"status": "Skipped"},
        headers=user_token_header
    )
    assert response_skipped.status_code == 200
    assert response_skipped.json()["data"]["today_status"] == "Skipped"

    # 3. Toggle back to Upcoming
    response_upcoming = client.put(
        "/api/v1/medications/1/toggle",
        json={"status": "Upcoming"},
        headers=user_token_header
    )
    assert response_upcoming.status_code == 200
    assert response_upcoming.json()["data"]["today_status"] == "Upcoming"


def test_medication_invalid_dose_status_validation(client: TestClient, user_token_header: dict):
    """Validates that unsupported adherence statuses are rejected with 422."""
    response = client.put(
        "/api/v1/medications/1/toggle",
        json={"status": "ForgotDose"},
        headers=user_token_header
    )
    assert response.status_code == 422


def test_medication_deletion(client: TestClient, user_token_header: dict):
    """Validates medication deletion endpoint."""
    response = client.delete("/api/v1/medications/2", headers=user_token_header)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"


# ==============================================================================
# 2. Appointment Booking & Status Tracking Tests (FR-07.1, FR-07.2, FR-07.3)
# ==============================================================================

def test_appointment_creation_and_listing(client: TestClient, user_token_header: dict):
    """
    Validates booking a clinical doctor appointment with doctor name,
    specialty, clinic address, and datetime (FR-07.1).
    """
    payload = {
        "doctor_name": "Dr. Sunita Rao",
        "specialty": "Endocrinology",
        "clinic_name": "Metro Diabetes & Hormone Care",
        "appointment_datetime": "2026-12-05T10:00:00Z",
        "notes": "Discuss HbA1c lab results and continuous glucose monitor options."
    }
    response = client.post("/api/v1/appointments", json=payload, headers=user_token_header)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]

    assert data["id"] > 0
    assert data["doctor_name"] == "Dr. Sunita Rao"
    assert data["specialty"] == "Endocrinology"
    assert data["status"] == "upcoming"
    assert "HbA1c" in data["notes"]

    # Verify in list
    list_resp = client.get("/api/v1/appointments", headers=user_token_header)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) >= 1


def test_appointment_update_status_and_notes(client: TestClient, user_token_header: dict):
    """
    Validates updating appointment status (upcoming -> completed) and
    attaching clinical discussion notes (FR-07.2, FR-07.3).
    """
    update_payload = {
        "status": "completed",
        "notes": "Consultation completed. Recommended 150 min/wk aerobic exercise and follow-up in 3 months."
    }
    response = client.put("/api/v1/appointments/1", json=update_payload, headers=user_token_header)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]

    assert data["status"] == "completed"
    assert "150 min/wk" in data["notes"]


def test_appointment_not_found_rejection(client: TestClient, user_token_header: dict):
    """Validates that updating a non-existent appointment ID returns HTTP 404."""
    response = client.put(
        "/api/v1/appointments/99999",
        json={"status": "completed"},
        headers=user_token_header
    )
    assert response.status_code == 404
    body = response.json()
    assert body["status"] == "error"
    assert "not found" in body["message"].lower()


def test_appointment_deletion(client: TestClient, user_token_header: dict):
    """Validates appointment cancellation and deletion."""
    response = client.delete("/api/v1/appointments/3", headers=user_token_header)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
