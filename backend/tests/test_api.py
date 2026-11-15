import io
import pytest
from datetime import date, datetime, timezone
from fastapi.testclient import TestClient

from backend.main import app

USER_TOKEN_HEADER = {"Authorization": "Bearer mock_user_jwt_token"}
ADMIN_TOKEN_HEADER = {"Authorization": "Bearer mock_admin_jwt_token"}
INVALID_FORMAT_HEADER = {"Authorization": "Basic 12345"}
EXPIRED_TOKEN_HEADER = {"Authorization": "Bearer invalid_token"}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# ==============================================================================
# 1. System & Diagnostic Endpoints
# ==============================================================================

def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "AI Healthcare Assistant" in data["service"]
    assert data["docs_url"] == "/docs"


def test_root_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_v1_health(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["components"]["api_server"] == "online"
    assert data["components"]["emergency_guardrails"] == "active"


def test_api_v1_root(client: TestClient):
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome to AI Healthcare Assistant API v1" in data["message"]


# ==============================================================================
# 2. Authentication Endpoints (FR-01.1 - FR-01.3)
# ==============================================================================

def test_auth_register_success(client: TestClient):
    payload = {
        "email": "test.patient@example.com",
        "password": "StrongPassword123!",
        "full_name": "Test Patient",
        "date_of_birth": "1995-08-20"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["email"] == "test.patient@example.com"
    assert body["data"]["role"] == "ROLE_USER"


def test_auth_register_weak_password_validation(client: TestClient):
    payload = {
        "email": "weak.patient@example.com",
        "password": "short",
        "full_name": "Weak Password",
        "date_of_birth": "1995-08-20"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    body = response.json()
    assert body["status"] == "error"
    assert "validation failed" in body["message"].lower()


def test_auth_login_success(client: TestClient):
    payload = {
        "email": "ananya@example.com",
        "password": "ValidPassword123!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["token_type"] == "bearer"
    assert len(body["data"]["access_token"]) > 10


def test_auth_login_invalid_credentials(client: TestClient):
    payload = {
        "email": "ananya@example.com",
        "password": "wrong_password"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    body = response.json()
    assert body["status"] == "error"
    assert "unauthorized" in body["message"].lower()


def test_auth_me(client: TestClient):
    response = client.get("/api/v1/auth/me", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["role"] == "ROLE_USER"


def test_auth_logout(client: TestClient):
    response = client.post("/api/v1/auth/logout", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"


# ==============================================================================
# 3. Patient Profile Endpoints (FR-01.4 & DPDP Act 2023)
# ==============================================================================

def test_get_profile(client: TestClient):
    response = client.get("/api/v1/profile", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]
    assert "calculated_age" in data
    assert "calculated_bmi" in data
    assert data["calculated_age"] >= 18
    assert data["calculated_bmi"] > 10.0


def test_update_profile(client: TestClient):
    update_data = {
        "blood_group": "B+",
        "weight_kg": 59.0,
        "allergies": "Penicillin and sulfa drugs"
    }
    response = client.put("/api/v1/profile", json=update_data, headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["weight_kg"] == 59.0
    assert body["data"]["allergies"] == "Penicillin and sulfa drugs"


def test_delete_profile(client: TestClient):
    response = client.delete("/api/v1/profile", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert "permanently erased" in body["message"].lower()


# ==============================================================================
# 4. Clinical AI Chat & Emergency Guardrail Endpoints (FR-03.1 - FR-03.5, US-03)
# ==============================================================================

def test_chat_query_educational(client: TestClient):
    payload = {
        "query": "What does a slightly elevated LDL cholesterol level indicate?",
        "conversation_id": 1
    }
    response = client.post("/api/v1/chat/query", json=payload, headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]
    assert data["emergency_intercepted"] is False
    assert len(data["sources_cited"]) > 0
    assert "LDL cholesterol" in data["answer"]


def test_chat_query_emergency_interception(client: TestClient):
    payload = {
        "query": "I am having severe chest pain and crushing pressure radiating to my left arm",
        "conversation_id": 1
    }
    response = client.post("/api/v1/chat/query", json=payload, headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "warning"
    data = body["data"]
    assert data["emergency_intercepted"] is True
    assert "112 / 911" in data["answer"]
    assert "chest pain" in data["emergency_warning"].lower()


def test_chat_list_conversations(client: TestClient):
    response = client.get("/api/v1/chat/conversations", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 1


def test_chat_get_conversation_messages(client: TestClient):
    response = client.get("/api/v1/chat/conversations/1/messages", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert isinstance(body["data"], list)


# ==============================================================================
# 5. Medical Reports Endpoints (FR-02.1 - FR-02.5, US-02)
# ==============================================================================

def test_reports_list(client: TestClient):
    response = client.get("/api/v1/reports", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert len(body["data"]) >= 1


def test_reports_get_detail(client: TestClient):
    response = client.get("/api/v1/reports/1", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["report_id"] == 1
    assert len(body["data"]["parsed_parameters"]) > 0


def test_reports_get_not_found(client: TestClient):
    response = client.get("/api/v1/reports/9999", headers=USER_TOKEN_HEADER)
    assert response.status_code == 404
    body = response.json()
    assert body["status"] == "error"
    assert "not found" in body["message"].lower()


def test_reports_upload_pdf_success(client: TestClient):
    pdf_content = b"%PDF-1.4 Mock PDF Content with Blood Test Results"
    files = {"file": ("blood_test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {"report_type": "Complete Blood Count"}

    response = client.post("/api/v1/reports/upload", files=files, data=data, headers=USER_TOKEN_HEADER)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["file_name"] == "blood_test.pdf"
    assert len(body["data"]["parsed_parameters"]) > 0


def test_reports_upload_invalid_mime(client: TestClient):
    txt_content = b"Not a PDF file"
    files = {"file": ("notes.txt", io.BytesIO(txt_content), "text/plain")}
    data = {"report_type": "Other"}

    response = client.post("/api/v1/reports/upload", files=files, data=data, headers=USER_TOKEN_HEADER)
    assert response.status_code == 415
    body = response.json()
    assert body["status"] == "error"
    assert "only pdf" in body["message"].lower()


def test_reports_delete(client: TestClient):
    response = client.delete("/api/v1/reports/2", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"


# ==============================================================================
# 6. Medication Tracking Endpoints (FR-04.1 - FR-04.4, US-04)
# ==============================================================================

def test_medications_list(client: TestClient):
    response = client.get("/api/v1/medications", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert len(body["data"]) >= 1


def test_medications_create(client: TestClient):
    payload = {
        "medication_name": "Cetirizine 10mg",
        "dosage": "1 tablet (10mg)",
        "frequency": "Once daily at night",
        "start_date": "2026-11-01",
        "instructions": "Take after dinner for seasonal rhinitis",
        "category": "Antihistamine"
    }
    response = client.post("/api/v1/medications", json=payload, headers=USER_TOKEN_HEADER)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["medication_name"] == "Cetirizine 10mg"


def test_medications_toggle_dose(client: TestClient):
    payload = {"status": "Taken"}
    response = client.put("/api/v1/medications/1/toggle", json=payload, headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["today_status"] == "Taken"


def test_medications_delete(client: TestClient):
    response = client.delete("/api/v1/medications/1", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"


# ==============================================================================
# 7. Doctor Appointments Endpoints (FR-05.1 - FR-05.3, US-05)
# ==============================================================================

def test_appointments_list(client: TestClient):
    response = client.get("/api/v1/appointments", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert len(body["data"]) >= 1


def test_appointments_create(client: TestClient):
    payload = {
        "doctor_name": "Dr. Rohit Verma",
        "specialty": "Cardiology",
        "clinic_name": "City Heart Clinic",
        "appointment_datetime": "2026-12-05T11:00:00Z",
        "notes": "Follow-up ECG consultation"
    }
    response = client.post("/api/v1/appointments", json=payload, headers=USER_TOKEN_HEADER)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["doctor_name"] == "Dr. Rohit Verma"


def test_appointments_update(client: TestClient):
    payload = {
        "notes": "Updated notes: Bring lipid panel printout",
        "status": "upcoming"
    }
    response = client.put("/api/v1/appointments/1", json=payload, headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert "lipid panel printout" in body["data"]["notes"]


def test_appointments_delete(client: TestClient):
    response = client.delete("/api/v1/appointments/1", headers=USER_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"


# ==============================================================================
# 8. Admin & Clinical Governance Endpoints (FR-08.1 - FR-08.4, US-08)
# ==============================================================================

def test_admin_stats_forbidden_for_regular_user(client: TestClient):
    response = client.get("/api/v1/admin/stats", headers=USER_TOKEN_HEADER)
    assert response.status_code == 403
    body = response.json()
    assert body["status"] == "error"
    assert "administrator privileges required" in body["detail"].lower()


def test_admin_stats_authorized(client: TestClient):
    response = client.get("/api/v1/admin/stats", headers=ADMIN_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]
    assert data["total_registered_users"] > 0
    assert data["assistant_interactions_30_days"] > 0


def test_admin_activity(client: TestClient):
    response = client.get("/api/v1/admin/activity", headers=ADMIN_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert len(body["data"]) > 0


def test_admin_audit_logs(client: TestClient):
    response = client.get("/api/v1/admin/audit-logs", headers=ADMIN_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert len(body["data"]) > 0


def test_admin_users(client: TestClient):
    response = client.get("/api/v1/admin/users", headers=ADMIN_TOKEN_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert len(body["data"]) > 0


def test_admin_create_knowledge_doc(client: TestClient):
    payload = {
        "title": "Hypertension Clinical Guidelines 2026",
        "category": "Cardiology",
        "source": "Ministry of Health Clinical Advisory"
    }
    response = client.post("/api/v1/admin/knowledge-documents", json=payload, headers=ADMIN_TOKEN_HEADER)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["title"] == "Hypertension Clinical Guidelines 2026"


# ==============================================================================
# 9. Global Error Handling & Standardized Response Verification (NFR-03.2)
# ==============================================================================

def test_not_found_endpoint_format(client: TestClient):
    response = client.get("/api/v1/non_existent_resource")
    assert response.status_code == 404
    body = response.json()
    assert body["status"] == "error"
    assert "message" in body
    assert "detail" in body


def test_invalid_auth_header_format(client: TestClient):
    response = client.get("/api/v1/profile", headers=INVALID_FORMAT_HEADER)
    assert response.status_code == 401
    body = response.json()
    assert body["status"] == "error"
    assert "bearer" in body["detail"].lower()


def test_expired_token(client: TestClient):
    response = client.get("/api/v1/profile", headers=EXPIRED_TOKEN_HEADER)
    assert response.status_code == 401
    body = response.json()
    assert body["status"] == "error"
    assert "invalid or expired" in body["detail"].lower()
