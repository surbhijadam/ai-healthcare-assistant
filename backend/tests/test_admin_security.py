"""
MediCare AI — Phase 11 Administrative Governance, Security Hardening & Automated Testing Suite.
Validates:
- HTTP Security Headers (OWASP Hardening per NFR-02)
- Strict Role-Based Access Control (RBAC) across all administrative endpoints (FR-08.1 / US-08)
- Audit Trail Telemetry and Event Logging (FR-08.2)
- Platform Metrics Aggregation and Database Queries (FR-08.3)
- Rate Limiting and Brute Force Safeguards (NFR-02)
- Frontend ApiClient Administrative Integration
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.main import app
from backend.db.base import Base
from backend.db.session import get_db
from backend.core.security import create_access_token
from backend.core.rate_limiter import rate_limiter
from backend.repositories.audit_repo import audit_repo
from frontend.api_client import HealthcareApiClient

# Tokens
ADMIN_TOKEN = create_access_token({"sub": "admin.security@example.com", "role": "ROLE_ADMIN", "id": 99})
PATIENT_TOKEN = create_access_token({"sub": "patient.security@example.com", "role": "ROLE_USER", "id": 100})

ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
PATIENT_HEADERS = {"Authorization": f"Bearer {PATIENT_TOKEN}"}
INVALID_HEADERS = {"Authorization": "Bearer invalid_token"}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# ==============================================================================
# 1. HTTP Security Headers Hardening (OWASP per NFR-02)
# ==============================================================================

def test_security_headers_present_on_root_and_health(client: TestClient):
    """Verifies that all OWASP recommended security headers are injected."""
    response = client.get("/")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in headers.get("Content-Security-Policy", "")
    assert "geolocation=()" in headers.get("Permissions-Policy", "")


def test_security_headers_present_on_api_endpoints(client: TestClient):
    """Verifies security headers on API v1 routes."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"


# ==============================================================================
# 2. Strict RBAC Enforcement on Administrative Endpoints (FR-08.1 / US-08)
# ==============================================================================

@pytest.mark.parametrize(
    "method,endpoint,payload",
    [
        ("GET", "/api/v1/admin/stats", None),
        ("GET", "/api/v1/admin/activity", None),
        ("GET", "/api/v1/admin/audit-logs", None),
        ("GET", "/api/v1/admin/users", None),
        ("GET", "/api/v1/admin/knowledge-documents", None),
        ("POST", "/api/v1/admin/knowledge-documents", {"title": "Test Guideline"}),
    ],
)
def test_rbac_unauthenticated_requests_rejected(client: TestClient, method: str, endpoint: str, payload: dict):
    """Unauthenticated requests (no token or invalid token) must be rejected with 401 Unauthorized."""
    # 1. Without Authorization header
    res_no_auth = client.request(method, endpoint, json=payload)
    assert res_no_auth.status_code == 401
    body = res_no_auth.json()
    assert body["status"] == "error"

    # 2. With invalid token
    res_invalid = client.request(method, endpoint, json=payload, headers=INVALID_HEADERS)
    assert res_invalid.status_code == 401
    body_inv = res_invalid.json()
    assert body_inv["status"] == "error"


@pytest.mark.parametrize(
    "method,endpoint,payload",
    [
        ("GET", "/api/v1/admin/stats", None),
        ("GET", "/api/v1/admin/activity", None),
        ("GET", "/api/v1/admin/audit-logs", None),
        ("GET", "/api/v1/admin/users", None),
        ("GET", "/api/v1/admin/knowledge-documents", None),
        ("POST", "/api/v1/admin/knowledge-documents", {"title": "Test Guideline"}),
    ],
)
def test_rbac_patient_user_forbidden(client: TestClient, method: str, endpoint: str, payload: dict):
    """Authenticated users with ROLE_USER must be rejected with 403 Forbidden."""
    res = client.request(method, endpoint, json=payload, headers=PATIENT_HEADERS)
    assert res.status_code == 403
    body = res.json()
    assert body["status"] == "error"
    assert "administrator privileges required" in body["detail"].lower()


def test_rbac_admin_stats_authorized(client: TestClient):
    """Admin credentials can access /api/v1/admin/stats (FR-08.3)."""
    res = client.get("/api/v1/admin/stats", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    data = body["data"]
    assert "total_registered_users" in data
    assert "active_users" in data
    assert "knowledge_base_documents" in data
    assert "assistant_interactions_30_days" in data
    assert data["total_registered_users"] > 0


def test_rbac_admin_activity_authorized(client: TestClient):
    """Admin credentials can access /api/v1/admin/activity."""
    res = client.get("/api/v1/admin/activity", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert isinstance(body["data"], list)
    assert len(body["data"]) > 0


def test_rbac_admin_audit_logs_authorized(client: TestClient):
    """Admin credentials can access /api/v1/admin/audit-logs (FR-08.2)."""
    res = client.get("/api/v1/admin/audit-logs", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert isinstance(body["data"], list)
    assert len(body["data"]) > 0


def test_rbac_admin_users_authorized(client: TestClient):
    """Admin credentials can access /api/v1/admin/users."""
    res = client.get("/api/v1/admin/users", headers=ADMIN_HEADERS)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert isinstance(body["data"], list)
    assert len(body["data"]) > 0


def test_rbac_admin_knowledge_documents_lifecycle(client: TestClient):
    """Admin can list and create knowledge documents (FR-04.1 / FR-08.1)."""
    # 1. List existing
    list_res = client.get("/api/v1/admin/knowledge-documents", headers=ADMIN_HEADERS)
    assert list_res.status_code == 200
    list_body = list_res.json()
    assert list_body["status"] == "success"
    initial_count = len(list_body["data"])

    # 2. Ingest new document
    payload = {
        "title": "Phase 11 Clinical Security Advisory",
        "category": "Governance",
        "content": "Administrative security policies require Argon2id password hashing and TLS 1.3 encryption.",
        "source_url": "https://mohfw.gov.in/guidelines/cybersecurity"
    }
    create_res = client.post("/api/v1/admin/knowledge-documents", json=payload, headers=ADMIN_HEADERS)
    assert create_res.status_code == 201
    create_body = create_res.json()
    assert create_body["status"] == "success"
    assert create_body["data"]["title"] == "Phase 11 Clinical Security Advisory"


# ==============================================================================
# 3. Rate Limiter Unit Tests (NFR-02)
# ==============================================================================

def test_rate_limiter_allows_under_threshold():
    """Rate limiter allows requests within configured limits."""
    rate_limiter.reset()
    test_ip = "192.0.2.1"

    for _ in range(5):
        is_limited, _ = rate_limiter.check_rate_limit(test_ip, endpoint="/api/v1/auth/login")
        assert is_limited is False


def test_rate_limiter_blocks_on_brute_force_excess():
    """Rate limiter trips when login attempts exceed login_attempts_per_minute."""
    rate_limiter.reset()
    attacker_ip = "198.51.100.99"

    # Burn through the 15 allowed login attempts
    for _ in range(15):
        is_limited, _ = rate_limiter.check_rate_limit(attacker_ip, endpoint="/api/v1/auth/login")

    # 16th attempt should be blocked
    is_limited, retry_after = rate_limiter.check_rate_limit(attacker_ip, endpoint="/api/v1/auth/login")
    assert is_limited is True
    assert retry_after > 0

    rate_limiter.reset()


# ==============================================================================
# 4. Audit Trail Repository Async Unit Tests (FR-08.2)
# ==============================================================================

@pytest.mark.asyncio
async def test_audit_repo_event_logging():
    """Verifies that audit events can be recorded and queried with proper timestamps."""
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Log event
        log = await audit_repo.log_event(
            session=session,
            action="TEST_SECURITY_AUDIT",
            status="SUCCESS",
            user_id=1,
            ip_address="10.0.0.1",
        )
        await session.commit()
        assert log.id is not None
        assert log.action == "TEST_SECURITY_AUDIT"
        assert log.status == "SUCCESS"

        # Query recent logs
        logs = await audit_repo.get_recent_logs(session, limit=10)
        assert len(logs) == 1
        assert logs[0].action == "TEST_SECURITY_AUDIT"
        assert logs[0].ip_address == "10.0.0.1"

    await test_engine.dispose()


# ==============================================================================
# 5. Frontend ApiClient Administrative Integration
# ==============================================================================

def test_api_client_admin_methods(client: TestClient, monkeypatch):
    """Verifies HealthcareApiClient administrative methods return properly formatted responses."""
    frontend_client = HealthcareApiClient(base_url="http://testserver/api/v1")

    import requests

    def mock_get(url, headers=None, timeout=None):
        path = url.replace("http://testserver", "")
        return client.get(path, headers=headers)

    def mock_post(url, json=None, headers=None, timeout=None):
        path = url.replace("http://testserver", "")
        return client.post(path, json=json, headers=headers)

    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests, "post", mock_post)

    # Pass the test client mock session token
    stats = frontend_client.get_admin_stats(custom_token=ADMIN_TOKEN)
    assert stats["success"] is True
    assert "total_registered_users" in stats["data"]

    activity = frontend_client.get_admin_activity(custom_token=ADMIN_TOKEN)
    assert activity["success"] is True
    assert isinstance(activity["data"], list)

    users = frontend_client.get_admin_users(custom_token=ADMIN_TOKEN)
    assert users["success"] is True
    assert isinstance(users["data"], list)

    audit_logs = frontend_client.get_admin_audit_logs(custom_token=ADMIN_TOKEN)
    assert audit_logs["success"] is True
    assert isinstance(audit_logs["data"], list)

    docs = frontend_client.get_admin_knowledge_documents(custom_token=ADMIN_TOKEN)
    assert docs["success"] is True
    assert isinstance(docs["data"], list)

    new_doc = frontend_client.create_knowledge_document(
        title="Admin Client Ingest Test",
        category="Cardiology",
        content="Blood pressure guidance",
        custom_token=ADMIN_TOKEN,
    )
    assert new_doc["success"] is True
    assert new_doc["data"]["title"] == "Admin Client Ingest Test"
