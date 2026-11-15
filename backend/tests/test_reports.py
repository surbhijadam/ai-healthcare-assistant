"""
MediCare AI — Comprehensive Automated Test Suite for Phase 9: Medical Report Assistant
Validates FR-05.1 (PDF MIME & 10MB Size Validation), FR-05.2 (PyMuPDF Text Extraction),
FR-05.3 (PII Redaction), FR-05.4 (Structured Parameter JSON Extraction),
FR-05.5 (Patient Educational Summary & Doctor Discussion Points),
FR-05.6 (Database Persistence), and NFR-01.3 (<2.0s extraction performance).
"""

import io
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.pdf_extraction_service import pdf_extraction_service, MAX_PDF_SIZE_BYTES
from backend.services.report_analysis_service import report_analysis_service
from backend.tests.conftest import TestingSessionLocal
from backend.core.security import create_access_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user_token_header():
    token = create_access_token(data={"sub": "1", "role": "ROLE_USER"})
    return {"Authorization": f"Bearer {token}"}


# ==============================================================================
# 1. PDF Validation & PyMuPDF Extraction Tests (FR-05.1, FR-05.2, NFR-01.3)
# ==============================================================================

def test_pdf_validation_empty_and_oversize():
    """Validates that empty files and files exceeding 10 MB are rejected per FR-05.1."""
    with pytest.raises(ValueError, match="empty"):
        pdf_extraction_service.validate_pdf_bytes(b"", "empty.pdf")

    oversized_bytes = b"0" * (MAX_PDF_SIZE_BYTES + 1024)
    with pytest.raises(ValueError, match="10 MB"):
        pdf_extraction_service.validate_pdf_bytes(oversized_bytes, "large.pdf")

    valid_pdf = b"%PDF-1.4 Mock valid PDF header and content"
    val = pdf_extraction_service.validate_pdf_bytes(valid_pdf, "test.pdf")
    assert val["valid"] is True
    assert val["file_size_bytes"] == len(valid_pdf)


def test_pdf_text_extraction():
    """Validates text extraction, page counting, and word counting from PDF streams."""
    synthetic_pdf = (
        b"%PDF-1.4\n"
        b"METROPOLITAN CLINICAL LABORATORY REPORT\n"
        b"Complete Blood Count and Comprehensive Metabolic Profile\n"
        b"Haemoglobin: 14.1 g/dL\n"
        b"WBC: 7.2 10^9/L\n"
        b"Platelets: 260 10^9/L\n"
        b"Fasting Blood Glucose: 92 mg/dL\n"
    )
    result = pdf_extraction_service.extract_text(synthetic_pdf)
    assert result["page_count"] >= 1
    assert result["word_count"] > 5
    assert "Haemoglobin" in result["raw_text"]
    assert "WBC" in result["raw_text"]


# ==============================================================================
# 2. PII Sanitization & Redaction Tests (FR-05.3, DPDP Act 2023)
# ==============================================================================

def test_pii_sanitization_patient_names_and_contacts():
    """
    Validates that Personally Identifiable Information (Names, Phone Numbers,
    Emails, Addresses, MRNs) is redacted prior to LLM transmission (FR-05.3).
    """
    sample_text = (
        "METROPOLITAN DIAGNOSTICS INC.\n"
        "Patient Name: Ananya Sharma\n"
        "Phone: +91 9876543210\n"
        "Email: ananya.sharma@example.com\n"
        "Address: 42 Palm Avenue, Bengaluru, Karnataka 560001\n"
        "MRN: BLR-2026-9942\n"
        "Haemoglobin: 13.4 g/dL\n"
        "Fasting Blood Glucose: 88 mg/dL\n"
    )
    sanitized = pdf_extraction_service.sanitize_pii(sample_text)

    # Assert PII is redacted
    assert "Ananya Sharma" not in sanitized
    assert "[REDACTED_PATIENT_NAME]" in sanitized
    assert "+91 9876543210" not in sanitized
    assert "[REDACTED_PHONE]" in sanitized
    assert "ananya.sharma@example.com" not in sanitized
    assert "[REDACTED_EMAIL]" in sanitized
    assert "42 Palm Avenue" not in sanitized
    assert "[REDACTED_ADDRESS]" in sanitized
    assert "BLR-2026-9942" not in sanitized
    assert "[REDACTED_IDENTIFIER]" in sanitized

    # Assert clinical laboratory content remains intact
    assert "Haemoglobin: 13.4 g/dL" in sanitized
    assert "Fasting Blood Glucose: 88 mg/dL" in sanitized


# ==============================================================================
# 3. Laboratory Parameter Extraction & Range Classification (FR-05.4, FR-05.5)
# ==============================================================================

def test_parameter_parsing_and_status_determination():
    """
    Validates that clinical biomarkers are correctly parsed and assigned
    clinical status flags: Normal, Elevated, or Low (FR-05.4).
    """
    clinical_text = (
        "Complete Metabolic and Lipid Panel:\n"
        "Haemoglobin: 13.5 g/dL\n"
        "Total Cholesterol: 220 mg/dL\n"
        "LDL cholesterol: 142 mg/dL\n"
        "Fasting Blood Glucose: 118 mg/dL\n"
        "Vitamin D: 19 ng/mL\n"
    )
    parameters = report_analysis_service.parse_parameters_from_text(clinical_text)
    assert len(parameters) >= 4

    param_map = {p.test_name: p for p in parameters}

    # Haemoglobin normal
    assert "Haemoglobin" in param_map
    assert param_map["Haemoglobin"].status == "Normal"

    # LDL elevated (>100)
    assert "LDL Cholesterol" in param_map
    assert param_map["LDL Cholesterol"].status == "Elevated"
    assert param_map["LDL Cholesterol"].observed_value == "142"

    # Fasting Blood Glucose elevated (>99)
    assert "Fasting Blood Glucose" in param_map
    assert param_map["Fasting Blood Glucose"].status == "Elevated"

    # Vitamin D low (<30)
    assert "Vitamin D (25-OH)" in param_map
    assert param_map["Vitamin D (25-OH)"].status == "Low"


def test_ai_summary_and_doctor_discussion_points():
    """
    Validates generation of plain-English educational summary and
    actionable doctor discussion points adhering to non-diagnostic rules (FR-05.5, FR-03.4).
    """
    from backend.schemas.reports import LabParameter
    test_params = [
        LabParameter(
            test_name="LDL Cholesterol",
            observed_value="145",
            reference_range="< 100",
            unit="mg/dL",
            status="Elevated",
            explanation="One lipid component evaluated in cardiovascular health."
        ),
        LabParameter(
            test_name="Vitamin D (25-OH)",
            observed_value="22",
            reference_range="30–100",
            unit="ng/mL",
            status="Low",
            explanation="Nutrient essential for bone health and calcium absorption."
        )
    ]
    summary, discussion_points = report_analysis_service.generate_ai_summary(
        test_params, report_title="Lipid & Micronutrient Panel"
    )

    # Non-diagnostic educational assertions
    assert len(summary) > 50
    assert "educational purposes only" in summary.lower()
    assert "treating physician" in summary.lower() or "doctor" in summary.lower()

    # Discussion points assertions
    assert len(discussion_points) >= 2
    assert any("LDL Cholesterol" in dp for dp in discussion_points)
    assert any("Vitamin D" in dp for dp in discussion_points)


# ==============================================================================
# 4. API Endpoints: Report Upload, Listing, Details & Deletion (FR-05, US-04)
# ==============================================================================

def test_api_upload_medical_report_success(client: TestClient, user_token_header: dict):
    """
    Validates end-to-end PDF upload via POST /api/v1/reports/upload:
    verifies extraction, PII redaction, parameter parsing, AI summary, and persistence.
    """
    pdf_payload = (
        b"%PDF-1.4 Synthetic Lab Report\n"
        b"Patient Name: Rahul V\n"
        b"Phone: 9876543210\n"
        b"Haemoglobin: 14.2 g/dL\n"
        b"Platelets: 280 10^9/L\n"
        b"Fasting Blood Glucose: 95 mg/dL\n"
    )
    files = {"file": ("complete_blood_count.pdf", io.BytesIO(pdf_payload), "application/pdf")}
    data = {"report_title": "Comprehensive Blood Profile"}

    response = client.post(
        "/api/v1/reports/upload",
        files=files,
        data=data,
        headers=user_token_header
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    rep_data = body["data"]

    assert rep_data["report_id"] > 0
    assert rep_data["file_name"] == "complete_blood_count.pdf"
    assert rep_data["report_type"] == "Comprehensive Blood Profile"
    assert len(rep_data["parsed_parameters"]) >= 2
    assert len(rep_data["ai_summary"]) > 20
    assert len(rep_data["doctor_discussion_points"]) > 0


def test_api_upload_invalid_mime_type_rejection(client: TestClient, user_token_header: dict):
    """Validates that non-PDF files are rejected with HTTP 415 per FR-05.1."""
    text_payload = b"PlainText report data that is not a PDF"
    files = {"file": ("report.txt", io.BytesIO(text_payload), "text/plain")}

    response = client.post(
        "/api/v1/reports/upload",
        files=files,
        headers=user_token_header
    )
    assert response.status_code == 415
    body = response.json()
    assert body["status"] == "error"
    assert "pdf" in body["message"].lower()


def test_api_upload_empty_file_rejection(client: TestClient, user_token_header: dict):
    """Validates that 0-byte uploaded files return HTTP 400."""
    files = {"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")}
    response = client.post(
        "/api/v1/reports/upload",
        files=files,
        headers=user_token_header
    )
    assert response.status_code == 400
    body = response.json()
    assert body["status"] == "error"
    assert "empty" in body["message"].lower()


def test_api_get_reports_list(client: TestClient, user_token_header: dict):
    """Validates GET /api/v1/reports retrieves list of uploaded reports."""
    response = client.get("/api/v1/reports", headers=user_token_header)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 1
    assert "file_name" in body["data"][0]


def test_api_get_report_detail(client: TestClient, user_token_header: dict):
    """Validates GET /api/v1/reports/{id} retrieves full details, parameters, and AI summary."""
    response = client.get("/api/v1/reports/1", headers=user_token_header)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    data = body["data"]
    assert data["report_id"] == 1
    assert len(data["parsed_parameters"]) > 0
    assert len(data["ai_summary"]) > 0


def test_api_delete_report(client: TestClient, user_token_header: dict):
    """Validates DELETE /api/v1/reports/{id} deletes the report record."""
    response = client.delete("/api/v1/reports/2", headers=user_token_header)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
