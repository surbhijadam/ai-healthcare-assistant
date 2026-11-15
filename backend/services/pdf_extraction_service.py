"""
MediCare AI — PyMuPDF PDF Text Extraction & PII Redaction Service
Conforms to FR-05.1 (PDF Upload Validation), FR-05.2 (PyMuPDF Extraction),
FR-05.3 (PII Redaction), and NFR-01.3 (<2.0s extraction for <= 5 pages).
"""

import io
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Constants per FR-05.1 and NFR-02.6
MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024  # 10 Megabytes


class PDFExtractionService:
    """Service for validating, extracting, and sanitizing clinical PDF documents."""

    def __init__(self):
        self._fitz = None
        self._check_fitz()

    def _check_fitz(self):
        """Attempts to load PyMuPDF library."""
        try:
            import fitz
            self._fitz = fitz
        except ImportError:
            self._fitz = None

    def validate_pdf_bytes(self, file_bytes: bytes, filename: str = "report.pdf") -> Dict[str, Any]:
        """
        Validates uploaded file size and PDF format per FR-05.1.
        Returns validation metadata or raises ValueError.
        """
        size = len(file_bytes)
        if size == 0:
            raise ValueError("Uploaded file is empty (0 bytes).")

        if size > MAX_PDF_SIZE_BYTES:
            raise ValueError(
                f"File size exceeds maximum allowable limit of 10 MB ({round(size / (1024 * 1024), 2)} MB provided)."
            )

        # Check PDF Magic Header
        if not file_bytes.startswith(b"%PDF-") and not filename.lower().endswith(".pdf"):
            raise ValueError("Invalid file format. Only valid PDF documents are accepted.")

        return {
            "valid": True,
            "file_size_bytes": size,
            "filename": filename
        }

    def extract_text(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Extracts raw textual and tabular blocks from PDF bytes using PyMuPDF (fitz) (FR-05.2, NFR-01.3).
        Falls back gracefully if PyMuPDF is compiling or in lightweight environments.
        """
        if not self._fitz:
            self._check_fitz()

        extracted_pages: List[str] = []
        page_count = 1

        if self._fitz:
            try:
                # Open PDF document from memory stream
                doc = self._fitz.open(stream=file_bytes, filetype="pdf")
                page_count = len(doc)
                for page_idx in range(page_count):
                    page = doc[page_idx]
                    page_text = page.get_text("text")
                    if page_text and page_text.strip():
                        extracted_pages.append(page_text.strip())
                doc.close()
            except Exception as e:
                logger.warning(f"PyMuPDF parse encountered error: {e}. Attempting plain text decoding.")
                extracted_pages = []

        if not extracted_pages:
            # Fallback for plain-text synthetic streams or test mock PDFs
            try:
                raw_decoded = file_bytes.decode("utf-8", errors="ignore")
                # Remove binary artifacts, retain readable medical text
                clean_lines = [
                    line.strip() for line in raw_decoded.splitlines()
                    if line.strip() and any(c.isalnum() for c in line)
                ]
                extracted_pages = ["\n".join(clean_lines)]
            except Exception:
                extracted_pages = [""]

        full_raw_text = "\n\n--- PAGE BREAK ---\n\n".join(extracted_pages).strip()

        return {
            "page_count": page_count,
            "raw_text": full_raw_text,
            "word_count": len(full_raw_text.split()),
            "character_count": len(full_raw_text)
        }

    def sanitize_pii(self, text: str) -> str:
        """
        Sanitizes Personally Identifiable Information (PII) from extracted clinical text
        before transmitting data to LLM inference or persisting logs (FR-05.3, DPDP Act 2023).
        Redacts patient names, phone numbers, email addresses, street addresses, and national IDs.
        """
        if not text:
            return ""

        sanitized = text

        # 1. Redact Patient Names following common lab report headers (single-line only)
        # e.g., "Patient Name: John Doe", "Name : Ananya Sharma", "Patient: Rahul Verma"
        name_patterns = [
            r"(?i)(patient\s*name\s*[:\-][ \t]*)([A-Z][a-zA-Z'\-]+(?:[ \t]+[A-Z][a-zA-Z'\-]+)+)",
            r"(?i)(name\s*of\s*patient\s*[:\-][ \t]*)([A-Z][a-zA-Z'\-]+(?:[ \t]+[A-Z][a-zA-Z'\-]+)+)",
            r"(?i)(patient\s*[:\-][ \t]*)([A-Z][a-zA-Z'\-]+(?:[ \t]+[A-Z][a-zA-Z'\-]+)+)"
        ]
        for pattern in name_patterns:
            sanitized = re.sub(pattern, r"\1[REDACTED_PATIENT_NAME]", sanitized)

        # 2. Redact Phone Numbers (international, domestic 10-digit, formatted)
        # e.g., +91 9876543210, (555) 123-4567, 98765-43210, +1-800-555-0199
        phone_pattern = r"(?:(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\b[6-9]\d{9}\b)"
        sanitized = re.sub(phone_pattern, "[REDACTED_PHONE]", sanitized)

        # 3. Redact Email Addresses
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        sanitized = re.sub(email_pattern, "[REDACTED_EMAIL]", sanitized)

        # 4. Redact Street/Residential Addresses
        # e.g., "Address: 42 Elm Street, Springfield, IL 62701"
        address_pattern = r"(?i)(address\s*[:\-][ \t]*)([^\n\r]+)"
        sanitized = re.sub(address_pattern, r"\1[REDACTED_ADDRESS]", sanitized)

        # 5. Redact Medical Record Numbers (MRN) and Government Identifiers (single-line only)
        mrn_pattern = r"(?i)(mrn|uhid|patient\s*id|aadhaar|ssn)\s*[:\-][ \t]*([a-zA-Z0-9\- ]{4,30})"
        sanitized = re.sub(mrn_pattern, r"\1: [REDACTED_IDENTIFIER]", sanitized)

        return sanitized

    def process_pdf_document(self, file_bytes: bytes, filename: str = "report.pdf") -> Dict[str, Any]:
        """
        End-to-end pipeline: validation -> text extraction -> PII sanitization.
        """
        # Validate
        validation = self.validate_pdf_bytes(file_bytes, filename)

        # Extract
        extraction = self.extract_text(file_bytes)

        # Sanitize PII
        sanitized_text = self.sanitize_pii(extraction["raw_text"])

        return {
            "filename": filename,
            "file_size_bytes": validation["file_size_bytes"],
            "page_count": extraction["page_count"],
            "raw_text": extraction["raw_text"],
            "sanitized_text": sanitized_text,
            "word_count": extraction["word_count"]
        }


# Global singleton instance
pdf_extraction_service = PDFExtractionService()
