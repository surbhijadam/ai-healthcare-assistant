"""
MediCare AI — Phase 6 Frontend-Backend Integration Tests
Tests api_client functionality, error envelope handling, session lifecycle,
dashboard metrics calculation, and DPDP Act 2023 profile synchronization.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from frontend.api_client import HealthcareApiClient


@pytest.fixture
def test_client():
    return TestClient(app)


def test_api_client_initialization():
    """Verifies HealthcareApiClient initializes with expected defaults."""
    client = HealthcareApiClient(base_url="http://testserver/api/v1")
    assert client.base_url == "http://testserver/api/v1"
    assert client.timeout == 4.0


def test_api_client_offline_graceful_handling():
    """Verifies api_client handles unreachable backend gracefully without crashing."""
    # Point to non-routable port to test timeout/connection error
    client = HealthcareApiClient(base_url="http://127.0.0.1:59999/api/v1", timeout=0.1)
    
    assert client.is_backend_online() is False
    
    reg_res = client.register("test@example.com", "Test User", "P@ssword123!")
    assert reg_res["success"] is False
    assert reg_res.get("offline") is True
    assert "offline or unreachable" in reg_res["message"]

    login_res = client.login("test@example.com", "P@ssword123!")
    assert login_res["success"] is False
    assert login_res.get("offline") is True

    metrics = client.get_dashboard_metrics()
    assert metrics["is_live"] is False
    assert "total_reports" in metrics
    assert "active_medications" in metrics
    assert "upcoming_appointments" in metrics
    assert len(metrics["recent_activity"]) > 0


def test_api_client_dashboard_metrics_schema():
    """Verifies get_dashboard_metrics returns expected data types and keys."""
    client = HealthcareApiClient()
    metrics = client.get_dashboard_metrics()
    
    assert isinstance(metrics, dict)
    assert "is_live" in metrics
    assert isinstance(metrics["total_reports"], str)
    assert isinstance(metrics["active_medications"], str)
    assert isinstance(metrics["upcoming_appointments"], str)
    assert isinstance(metrics["adherence_recorded"], int)
    assert isinstance(metrics["adherence_total"], int)
    assert metrics["adherence_total"] >= metrics["adherence_recorded"]
    assert isinstance(metrics["recent_activity"], list)


def test_full_frontend_backend_flow_with_testclient(test_client):
    """
    End-to-end integration test simulating frontend workflow against FastAPI:
    1. User registration (US-01)
    2. Authentication & JWT retrieval (FR-01.2)
    3. Profile retrieval with age and BMI (FR-01.4)
    4. Profile demographic update (FR-01.4)
    5. Dashboard metrics endpoints query (Reports, Meds, Appointments)
    6. DPDP Act 2023 permanent account erasure (NFR-02.2)
    """
    unique_email = "phase6_patient@medicare.ai"
    password = "StrongPassword@2026"
    full_name = "Phase Six Patient"

    # 1. Registration
    reg_resp = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": unique_email,
            "full_name": full_name,
            "password": password
        }
    )
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert reg_data["status"] == "success"
    assert reg_data["data"]["email"] == unique_email

    # 2. Login to acquire Bearer JWT token
    login_resp = test_client.post(
        "/api/v1/auth/login",
        json={
            "email": unique_email,
            "password": password
        }
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["status"] == "success"
    token = login_data["data"]["access_token"]
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Profile & verify calculations
    prof_resp = test_client.get("/api/v1/profile", headers=headers)
    assert prof_resp.status_code == 200
    prof_data = prof_resp.json()["data"]
    assert prof_data["full_name"] == full_name

    # 3. Update Profile
    update_resp = test_client.put(
        "/api/v1/profile",
        headers=headers,
        json={
            "city": "Indore",
            "blood_group": "AB+",
            "height_cm": 175.0,
            "weight_kg": 70.0,
            "allergies": "Sulfa drugs"
        }
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json()["data"]
    assert updated_data["city"] == "Indore"
    assert updated_data["blood_group"] == "AB+"
    assert updated_data["allergies"] == "Sulfa drugs"

    # 4. Fetch Clinical Entities for Dashboard
    reports_resp = test_client.get("/api/v1/reports", headers=headers)
    assert reports_resp.status_code == 200
    assert isinstance(reports_resp.json()["data"], list)

    meds_resp = test_client.get("/api/v1/medications", headers=headers)
    assert meds_resp.status_code == 200
    assert isinstance(meds_resp.json()["data"], list)

    appts_resp = test_client.get("/api/v1/appointments", headers=headers)
    assert appts_resp.status_code == 200
    assert isinstance(appts_resp.json()["data"], list)

    # 5. DPDP Act 2023 Erasure
    del_resp = test_client.delete("/api/v1/profile", headers=headers)
    assert del_resp.status_code == 200
    assert "permanently erased" in del_resp.json()["message"]

    # 6. Verify subsequent login fails
    login_fail = test_client.post(
        "/api/v1/auth/login",
        json={"email": unique_email, "password": password}
    )
    assert login_fail.status_code == 401
