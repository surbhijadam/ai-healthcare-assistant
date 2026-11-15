import os
import asyncio
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.main import app
from backend.db.base import Base
from backend.db.session import get_db
from backend.schemas.auth import UserRegisterRequest
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from backend.core.errors import UnauthorizedException

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


# ==============================================================================
# 1. Argon2id Cryptographic Password Hashing (FR-01.2 & NFR-02.1)
# ==============================================================================

def test_argon2id_hashing_and_verification():
    raw_password = "SecureClinical2026!#"
    hashed = hash_password(raw_password)

    # Must be valid Argon2id hash format
    assert hashed.startswith("$argon2id$")
    assert "m=65536,t=3,p=4" in hashed

    # Valid password verification
    assert verify_password(raw_password, hashed) is True
    # Wrong password rejection
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False


def test_password_complexity_validation():
    """FR-01.1: Password must have at least 8 chars, 1 number, 1 special character."""
    # Valid password
    valid = UserRegisterRequest(
        email="doctor@example.com",
        password="ValidPass123!",
        full_name="Dr. Valid",
    )
    assert valid.password == "ValidPass123!"

    # Less than 8 characters
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="doc@example.com",
            password="Sh1!",
            full_name="Short",
        )

    # Missing number
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="doc@example.com",
            password="NoNumberSpecial!",
            full_name="No Number",
        )

    # Missing special character
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            email="doc@example.com",
            password="NoSpecialChar123",
            full_name="No Special",
        )


# ==============================================================================
# 2. JWT Generation & Verification (FR-01.3 & NFR-02.3)
# ==============================================================================

def test_jwt_generation_and_decoding():
    claims = {"sub": "patient@example.com", "id": 42, "role": "ROLE_USER"}
    token = create_access_token(claims)
    assert isinstance(token, str)
    assert len(token.split(".")) == 3  # Standard 3-part header.payload.signature

    decoded = decode_access_token(token)
    assert decoded["sub"] == "patient@example.com"
    assert decoded["id"] == 42
    assert decoded["role"] == "ROLE_USER"
    assert "exp" in decoded
    assert "iat" in decoded
    assert "jti" in decoded


def test_jwt_expiration():
    """NFR-02.3: Expired tokens must be cryptographically rejected."""
    token = create_access_token(
        {"sub": "expired@example.com"},
        expires_delta=timedelta(seconds=-1)
    )
    with pytest.raises(UnauthorizedException) as exc_info:
        decode_access_token(token)
    assert "expired" in str(exc_info.value.detail).lower()


def test_jwt_tampering_rejection():
    token = create_access_token({"sub": "tamper@example.com", "role": "ROLE_USER"})
    # Tamper with the payload part
    header, payload, signature = token.split(".")
    tampered_token = f"{header}.eyJzdWIiOiAiaGFja2VyIn0.{signature}"

    with pytest.raises(UnauthorizedException) as exc_info:
        decode_access_token(tampered_token)
    assert "invalid" in str(exc_info.value.detail).lower()


# ==============================================================================
# 3. Full Registration & Login Endpoints Flow (US-01)
# ==============================================================================

def test_auth_full_registration_and_login_flow(client: TestClient):
    # 1. Register new user
    reg_payload = {
        "email": "clinical.newpatient@example.com",
        "password": "SecurePatientPass2026!",
        "full_name": "Clinical New Patient",
        "date_of_birth": "1992-04-15"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_body = reg_res.json()
    assert reg_body["status"] == "success"
    assert reg_body["data"]["email"] == "clinical.newpatient@example.com"

    # 2. Re-registering with duplicate email must be rejected with 400 Bad Request
    dup_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 400
    dup_body = dup_res.json()
    assert dup_body["status"] == "error"
    assert "already exists" in dup_body["message"].lower()

    # 3. Login with valid credentials
    login_payload = {
        "email": "clinical.newpatient@example.com",
        "password": "SecurePatientPass2026!"
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_body = login_res.json()
    assert login_body["status"] == "success"
    token = login_body["data"]["access_token"]
    assert len(token) > 20

    # 4. Access /auth/me with newly minted cryptographic Bearer JWT
    auth_header = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=auth_header)
    assert me_res.status_code == 200
    me_body = me_res.json()
    assert me_body["data"]["email"] == "clinical.newpatient@example.com"

    # 5. Access /profile with the real JWT
    profile_res = client.get("/api/v1/profile", headers=auth_header)
    assert profile_res.status_code == 200
    profile_body = profile_res.json()
    assert profile_body["status"] == "success"


def test_auth_login_invalid_password_returns_401(client: TestClient):
    payload = {
        "email": "clinical.newpatient@example.com",
        "password": "wrong_password"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    body = response.json()
    assert body["status"] == "error"
    assert "unauthorized" in body["message"].lower()


# ==============================================================================
# 4. Role-Based Access Control with Cryptographic Tokens (FR-08.1 / US-08)
# ==============================================================================

def test_rbac_patient_token_forbidden_on_admin_endpoint(client: TestClient):
    patient_token = create_access_token({"sub": "regular@example.com", "role": "ROLE_USER", "id": 105})
    patient_headers = {"Authorization": f"Bearer {patient_token}"}

    response = client.get("/api/v1/admin/stats", headers=patient_headers)
    assert response.status_code == 403
    body = response.json()
    assert body["status"] == "error"
    assert "administrator privileges required" in body["detail"].lower()


def test_rbac_admin_token_allowed_on_admin_endpoint(client: TestClient):
    admin_token = create_access_token({"sub": "admin.gov@example.com", "role": "ROLE_ADMIN", "id": 2})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    response = client.get("/api/v1/admin/stats", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["total_registered_users"] > 0
