"""
MediCare AI — Phase 7 AI Healthcare Chatbot & Clinical Guardrails Tests
Tests emergency triage interception (US-03), Groq LPU inference service,
non-diagnostic clinical disclaimers (FR-03.2 / FR-03.4), and multi-turn persistence (FR-03.5).
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.triage_service import triage_service, ClinicalTriageService
from backend.services.groq_service import groq_service, SYSTEM_CLINICAL_PROMPT, DISCLAIMER_TEXT


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def auth_headers(test_client):
    """Creates a patient account and returns Bearer JWT auth headers."""
    email = "chat_patient@medicare.ai"
    password = "ChatPassword@2026"
    test_client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Chat Patient", "password": password}
    )
    login_res = test_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    token = login_res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_triage_service_unit_evaluation():
    """Unit test: ClinicalTriageService detects acute red-flag symptoms and supplies emergency directives."""
    service = ClinicalTriageService()

    # Normal health question
    normal_res = service.evaluate_query("What does HDL cholesterol do in the body?")
    assert normal_res["is_emergency"] is False
    assert normal_res["emergency_warning"] is None
    assert normal_res["directive"] is None

    # Acute emergency question (chest pain)
    acute_res1 = service.evaluate_query("I have sudden severe crushing chest pain radiating to my arm")
    assert acute_res1["is_emergency"] is True
    assert "chest pain" in acute_res1["emergency_warning"]
    assert "112" in acute_res1["directive"]
    assert "911" in acute_res1["directive"]

    # Acute emergency question (stroke symptoms)
    acute_res2 = service.evaluate_query("My mother has sudden face drooping and slurred speech")
    assert acute_res2["is_emergency"] is True
    assert acute_res2["contacts"]["emergency_india"] == "112"


def test_groq_service_prompt_and_fallback():
    """Unit test: GroqHealthcareService system prompt enforces non-diagnostic rules."""
    assert "NON-DIAGNOSTIC MANDATE" in SYSTEM_CLINICAL_PROMPT
    assert "NO PRESCRIPTION OR DOSAGE ADVICE" in SYSTEM_CLINICAL_PROMPT
    assert "EMERGENCY INTERCEPTION" in SYSTEM_CLINICAL_PROMPT
    assert "Notice: This information is for educational purposes only" in DISCLAIMER_TEXT

    # Educational fallback generation for LDL
    answer = groq_service._generate_educational_fallback("What is LDL cholesterol?")
    assert "Low-Density Lipoprotein" in answer
    assert "Notice" in answer


def test_emergency_red_flag_interception_endpoint(test_client, auth_headers):
    """
    Integration test (US-03 / FR-03.3):
    Emergency red-flag symptom query triggers urgent safety alert, returns 112/911 directives,
    and sets emergency_intercepted = True.
    """
    resp = test_client.post(
        "/api/v1/chat/query",
        headers=auth_headers,
        json={"query": "I feel sudden severe crushing chest pain and difficulty breathing"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "warning"
    payload = data["data"]
    assert payload["emergency_intercepted"] is True
    assert "112" in payload["answer"]
    assert "911" in payload["answer"]
    assert payload["emergency_warning"] is not None


def test_educational_query_with_disclaimer_endpoint(test_client, auth_headers):
    """
    Integration test (US-02 / FR-03.2 / FR-03.4):
    Standard healthcare question returns structured educational response with clinical disclaimer
    and citations.
    """
    resp = test_client.post(
        "/api/v1/chat/query",
        headers=auth_headers,
        json={"query": "What are normal fasting blood glucose levels?"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    payload = data["data"]
    assert payload["emergency_intercepted"] is False
    assert len(payload["answer"]) > 20
    assert "Notice" in payload["answer"] or "educational" in payload["answer"].lower()
    assert len(payload["sources_cited"]) > 0


def test_conversations_persistence_lifecycle(test_client, auth_headers):
    """
    Integration test (FR-03.5):
    1. Create new conversation thread
    2. List conversations
    3. Send message within conversation thread
    4. Retrieve conversation messages
    5. Delete conversation thread
    """
    # 1. Create conversation thread
    create_res = test_client.post(
        "/api/v1/chat/conversations",
        headers=auth_headers,
        json={"title": "Asthma and Allergy Consultation"}
    )
    assert create_res.status_code == 201
    convo = create_res.json()["data"]
    convo_id = convo["id"]
    assert convo["title"] == "Asthma and Allergy Consultation"

    # 2. List conversations
    list_res = test_client.get("/api/v1/chat/conversations", headers=auth_headers)
    assert list_res.status_code == 200
    convos = list_res.json()["data"]
    assert any(c["id"] == convo_id for c in convos)

    # 3. Submit question within the created conversation thread
    chat_res = test_client.post(
        "/api/v1/chat/query",
        headers=auth_headers,
        json={
            "query": "How do maintenance inhalers work for asthma?",
            "conversation_id": convo_id
        }
    )
    assert chat_res.status_code == 200
    assert chat_res.json()["data"]["conversation_id"] == convo_id

    # 4. Retrieve conversation messages
    msgs_res = test_client.get(
        f"/api/v1/chat/conversations/{convo_id}/messages",
        headers=auth_headers
    )
    assert msgs_res.status_code == 200
    msgs = msgs_res.json()["data"]
    assert len(msgs) >= 2  # user message and assistant message
    roles = [m["sender_role"] for m in msgs]
    assert "user" in roles
    assert "assistant" in roles

    # 5. Delete conversation thread
    del_res = test_client.delete(
        f"/api/v1/chat/conversations/{convo_id}",
        headers=auth_headers
    )
    assert del_res.status_code == 200
    assert del_res.json()["data"] is True
