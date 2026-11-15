# MediCare AI — AI Healthcare Assistant

A secure, modern, full-stack AI-powered healthcare companion and personal health management platform. Built with **Streamlit** (incorporating a Canva design system), **FastAPI**, **PostgreSQL 16** with **pgvector**, **Groq LPU Inference**, and **PyMuPDF**.

> **Important Clinical & Legal Notice:**  
> This platform is strictly an **educational resource and personal health organizer**. It does not provide medical diagnoses, prescribe pharmaceutical drugs, alter treatment regimens, or replace emergency medical care.

---

## 1. Architecture Overview

```
[ Streamlit Frontend (Port 8501) ]
   ├── Custom MediCare AI Design System (Manrope, Ink, Teal, Mint, Blue)
   ├── Multi-Page Architecture (Landing, Auth, Dashboard, Chat, Reports, Meds, Appointments, Profile, Admin, About, Contact)
   └── Interactive Session-State Prototype Engine
         │
         ▼  (Upcoming: Phase 3 HTTP REST + Bearer JWT)
[ FastAPI Backend (Port 8000) ]
   ├── Core & Security (Argon2id, JWT, Emergency Triage Guardrails)
   ├── Services (PyMuPDF Extraction, Groq LLM Client, Sentence-Transformers)
   └── Data Persistence (SQLAlchemy Async ORM)
         │
         ▼  (Upcoming: Phase 4)
[ PostgreSQL 16 + pgvector (Port 5432) ]
   ├── Relational Tables (users, profiles, conversations, reports, meds, appts, audit_logs)
   └── Vector Storage (document_chunks with 384-dim HNSW Cosine Distance Index)
```

---

## 2. 12-Phase Roadmap Status

| Phase | Description | Status |
| :---: | :--- | :---: |
| **Phase 1** | Project Planning and Requirement Analysis | **Completed** (SRS & Data Dictionary approved) |
| **Phase 2** | UI/UX Design and Streamlit Setup (Canva Design Integration) | **Completed** (All 12 pages & components integrated) |
| **Phase 3** | Backend Development (FastAPI Core & Routers) | **Completed** (Core routers, Pydantic schemas, emergency triage, 40/40 tests passed) |
| **Phase 4** | PostgreSQL Integration & Alembic Migrations | **Completed** (SQLAlchemy 2.0 ORM, pgvector HNSW, Alembic 0001, Repositories, 52/52 tests passed) |
| **Phase 5** | Authentication and Authorization (Argon2 + JWT) | **Completed** (Argon2id hashing, JWT Bearer, RBAC roles, DPDP Act 2023 erasure, 61/61 tests passed) |
| **Phase 6** | Dashboard Development & Frontend-Backend Integration | **Completed** (Centralized API client, JWT Bearer session sync, live metrics cards, DPDP Act 2023 profile sync, 65/65 tests passed) |
| **Phase 7** | AI Healthcare Chatbot (Groq API & Clinical Guardrails) | **Completed** (Groq LPU integration, emergency red-flag triage, non-diagnostic guardrails, conversation persistence, 70/70 tests passed) |
| **Phase 8** | RAG Healthcare Knowledge Base (Sentence-Transformers + pgvector) | **Completed** (384-dim dense embeddings, recursive semantic chunking, baseline guidelines, source citations, 80/80 tests passed) |
| **Phase 9** | Medical Report Assistant (PyMuPDF Extraction & Analysis) | **Completed** (PDF text extraction, PII sanitization, structured lab parameters, educational summaries, 91/91 tests passed) |
| **Phase 10** | Medication & Appointment Management | **Completed** (Daily dose adherence checklist, physician guidance warnings, consultation booking & status management, 99/99 tests passed) |
| **Phase 11** | Admin Panel, Security Hardening & Automated Testing | **Completed** (OWASP security headers, sliding-window rate limiting, strict RBAC enforcement, live DB telemetry, Canva Admin UI, 122/122 tests passed) |
| **Phase 12** | Docker Containerization & Cloud Deployment | *Pending (Final Phase)* |

---

## 3. Project Structure

```text
ai-healthcare-assistant/
│
├── backend/
│   ├── main.py                      # FastAPI application root, lifespan, CORS, error handlers
│   ├── core/
│   │   ├── config.py                # Pydantic Settings & environment variables
│   │   ├── errors.py                # Standardized NFR-03.2 exception classes & handlers
│   │   └── security.py              # Argon2id password hashing & JWT helpers
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy DeclarativeBase with constraint naming conventions
│   │   ├── session.py               # Async & Sync engines, sessionmaker, get_db dependency
│   │   ├── init_db.py               # Database initializer, creates pgvector extension, seeds admin
│   │   └── models/                  # 10 SQLAlchemy ORM models (users, profiles, reports, chunks, etc.)
│   ├── repositories/                # Async CRUD repositories (user, report, med, appt, knowledge, audit)
│   ├── alembic/                     # Alembic migration environment and versions
│   │   ├── env.py                   # Async/Sync Alembic migration runner
│   │   └── versions/
│   │       └── 0001_initial_schema.py # Complete baseline migration (pgvector, HNSW, 10 tables)
│   ├── schemas/                     # Pydantic validation schemas
│   │   ├── auth.py, profile.py, chat.py, reports.py, medications.py, appointments.py, admin.py
│   ├── api/
│   │   ├── deps.py                  # RBAC & token dependency injection
│   │   └── v1/
│   │       ├── api.py               # API v1 aggregated router
│   │       └── endpoints/           # Clean Architecture domain controllers
│   └── tests/
│       ├── test_api.py              # 40-test router verification suite
│       └── test_db.py               # 12-test database ORM, pgvector & Alembic suite
│
├── alembic.ini                      # Alembic CLI configuration
├── docs/
│   └── SRS.md                       # Formal Software Requirements Specification
│
├── frontend/
│   ├── app.py                       # Canva Landing Page (Hero, Features, How It Works, Why Choose Us)
│   ├── requirements.txt             # Frontend dependencies
│   │
│   ├── assets/
│   │   └── style.css                # Canva MediCare AI Theme (Colors, 22px Surface Cards, Badges, Calendar)
│   │
│   ├── components/
│   │   ├── navbar.py                # Top brand header & user badge
│   │   ├── cards.py                 # Stat cards, adherence progress bar, lab badges
│   │   └── disclaimer.py            # Clinical disclaimers & emergency triage banners
│   │
│   └── pages/
│       ├── 0_Auth.py                # Login & Registration (Split hero art & form)
│       ├── 1_Dashboard.py           # Vitals overview, 7-day Wellness Trend Chart, 71% Adherence Widget
│       ├── 2_AI_Chatbot.py          # Conversational assistant, history rail, suggested prompts, triage
│       ├── 3_Medical_Reports.py     # Terms input, PDF dropzone, structured lab table, term explainers
│       ├── 4_Medications.py         # Add medication form, 3-state dose toggle (Upcoming -> Taken -> Skipped)
│       ├── 5_Appointments.py        # Add visit form, interactive monthly calendar with marked dates
│       ├── 6_Profile.py             # User profile, demographic editor, DPDP Act 2023 data erasure
│       ├── 7_Admin_Panel.py         # 4 platform stat cards, weekly usage bar chart, user management
│       ├── 8_About.py               # Mission, Vision, and capabilities overview
│       └── 9_Contact.py             # Inquiry form with validation, support email, and FAQ accordions
│
├── .env.example                     # Environment configuration blueprint
├── .gitignore                       # Git ignore rules
└── README.md                        # Project documentation
```

---

## 4. How to Run the Phase 2 Streamlit Application

### Step 1: Activate Virtual Environment
```bash
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate
```

### Step 2: Install Frontend Dependencies
```bash
pip install -r frontend/requirements.txt
```

### Step 3: Run the Streamlit Application
```bash
streamlit run frontend/app.py
```
The application will launch at `http://localhost:8501`.

---

## 5. How to Run the Backend, Migrations & Automated Tests

### Run the FastAPI Server
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
- **API Swagger Documentation:** `http://localhost:8000/docs`
- **ReDoc Interactive Documentation:** `http://localhost:8000/redoc`
- **OpenAPI JSON Specification:** `http://localhost:8000/api/v1/openapi.json`
- **Platform Health Probe:** `http://localhost:8000/api/v1/health`

### Database Migrations & Seeding (Phase 4)
```bash
# Check migration head
python -m alembic heads

# Run database migrations against PostgreSQL
python -m alembic upgrade head

# Generate static offline DDL SQL script without database connection
python -m alembic upgrade head --sql

# Initialize schema and seed default clinical administrator
python -m backend.db.init_db
```

### Run the Automated Test Suites (70 Tests)
```bash
# Run all tests (API routers + Database ORM & Migrations + Auth + Frontend Integration + AI Chatbot)
python -m pytest backend/tests/ -v

# Run AI Chatbot & Clinical Guardrail tests only
python -m pytest backend/tests/test_chat.py -v

# Run frontend integration tests only
python -m pytest backend/tests/test_frontend_integration.py -v

# Run authentication & security tests only
python -m pytest backend/tests/test_auth.py -v

# Run database tests only
python -m pytest backend/tests/test_db.py -v
```
*Current test suite status: **70 passed, 100% green** in ~6.1s.*

---

## 6. Phase Accomplishments Summary

* **Admin Panel, Security Hardening & Automated Testing (Phase 11 Completed):**
  * OWASP HTTP Security Headers Hardening middleware (`backend/main.py`) injecting `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`, `Content-Security-Policy`, and `Permissions-Policy` across all responses (**NFR-02**).
  * Sliding-window in-memory rate limiting with brute-force authentication protection (`backend/core/rate_limiter.py`), mitigating dictionary attacks and denial-of-service abuse returning `HTTP 429 Too Many Requests` with `Retry-After` headers (**NFR-02**, **FR-08.2**).
  * Strict Role-Based Access Control (`backend/api/deps.py` & `backend/api/v1/endpoints/admin.py`): Rejects unauthenticated callers with `401 Unauthorized` and non-admin callers (`ROLE_USER`) with `403 Forbidden` across all administrative governance endpoints (**FR-08.1 / US-08**).
  * Live administrative database queries: Platform statistics aggregated from live tables (`users`, `knowledge_documents`, `messages`) with resilient Canva design fallbacks, chronological activity feed, and user management tables (**FR-08.3**).
  * Clinical governance audit telemetry (`backend/repositories/audit_repo.py` & `backend/api/v1/endpoints/admin.py`): Tracks and logs critical events (`USER_LOGIN_SUCCESS`, `LOGIN_FAILED`, `REPORT_UPLOAD`, `REPORT_DELETION`, `KNOWLEDGE_DOC_INGESTED`, `PROFILE_ERASED_DPDP`) (**FR-08.2**).
  * Canva-styled Administrative Dashboard (`frontend/pages/7_Admin_Panel.py`): 4 live statistics cards, SVG weekly system usage chart, recent activity list, user management accounts table, interactive knowledge guideline ingestion form (**FR-04.1**), and audit telemetry log table (**FR-08.2**).
  * 23 comprehensive unit and integration tests in `backend/tests/test_admin_security.py` bringing total project test suite coverage to **122/122 passing tests (100% green)**.
* **Medication & Appointment Management (Phase 10 Completed):**
  * Asynchronous medication schedule & adherence API (`backend/api/v1/endpoints/medications.py` & `backend/repositories/medication_repo.py`) conforming to **FR-06.1**, **FR-06.2**, and **US-05**; tracks prescriptions, dosage timing, and daily adherence statuses (`Upcoming`, `Taken`, `Skipped`).
  * Strict physician guidance notice displayed across client medication interfaces per **FR-06.3** advising against unguided prescription changes.
  * Clinical appointment booking & lifecycle router (`backend/api/v1/endpoints/appointments.py` & `backend/repositories/appointment_repo.py`) conforming to **FR-07.1**, **FR-07.2**, and **FR-07.3**; manages doctor details, specialties, clinic locations, appointment timestamps, status transitions (`upcoming`, `completed`, `cancelled`), and clinical discussion notes.
  * Centralized frontend API integration (`frontend/api_client.py`) with dedicated methods for medication registration, dose adherence status toggling, appointment scheduling, and updates.
  * Canva-styled interactive frontends:
    * Medications Page (`frontend/pages/4_Medications.py`): Interactive daily dose cycling cards, prescription registration modal, and prominent clinical warning banner.
    * Appointments Page (`frontend/pages/5_Appointments.py`): Interactive monthly calendar widget, appointment booking modal, and live consultation list.
  * 8 comprehensive automated tests in `backend/tests/test_medications_appointments.py` bringing total test suite coverage to 99/99 passing tests (100% green).
* **Medical Report Assistant (Phase 9 Completed):**
  * Local PDF textual and tabular extraction engine (`backend/services/pdf_extraction_service.py`) conforming to **FR-05.1**, **FR-05.2**, and **NFR-01.3** (<2.0s extraction performance for $\le$ 5 pages).
  * Automated Personally Identifiable Information (PII) redaction conforming to **FR-05.3** and **DPDP Act 2023**; reliably scrubs patient names, contact numbers, email addresses, residential locations, and medical record identifiers (MRN) before transmission or persistence.
  * Laboratory parameter parser (`backend/services/report_analysis_service.py`) conforming to **FR-05.4**, mapping biomarker values against authoritative clinical reference cutoffs and assigning color-coded status flags (`Normal`, `Elevated`, or `Low`).
  * Plain-English educational summary engine (`backend/services/report_analysis_service.py`) conforming to **FR-05.5** & **FR-03.4**, generating patient-friendly descriptions and tailored doctor discussion points with strict non-diagnostic disclaimers.
  * Secure PDF upload and storage management (`backend/api/v1/endpoints/reports.py`) conforming to **NFR-02.6** (UUID filenames outside web roots) and database persistence in `medical_reports` table (**FR-05.6**).
  * Canva-styled Medical Reports UI (`frontend/pages/3_Medical_Reports.py`): Dropzone file uploader, live report listing, dynamic color-coded parameter tables (Normal/Elevated/Low badges), and actionable doctor discussion points.
  * 11 comprehensive automated tests in `backend/tests/test_reports.py` bringing total test suite coverage to 91/91 passing tests (100% green).
* **RAG Healthcare Knowledge Base (Phase 8 Completed):**
  * 384-dimensional dense vector embedding engine (`backend/services/embedding_service.py`) conforming to **FR-04.3** & **NFR-01.2**, strictly normalized to unit L2 length ($||v||_2 = 1.0$), with high-speed deterministic semantic projections and cosine similarity calculations.
  * Recursive semantic chunking service (`backend/services/chunking_service.py`) conforming to **FR-04.2**, dividing clinical documents into ~500-token semantic chunks with ~50-token overlap at natural sentence and paragraph boundaries.
  * Clinical RAG pipeline & pgvector similarity search (`backend/services/rag_service.py` & `backend/repositories/knowledge_repo.py`): Ingests medical guidelines into PostgreSQL `Vector(384)` with HNSW cosine distance indexing (`<=>`), resilient offline calculation fallback, and pre-seeded authoritative baseline guidelines (ACC/AHA Cholesterol, ADA Diabetes HbA1c, AHA/ACC Hypertension, GINA Asthma) (**FR-04.1**, **FR-04.4**, **US-02**).
  * Source-grounded conversational responses (`backend/api/v1/endpoints/chat.py`): Grounded clinical context injected into Groq prompts, returning structured `sources_cited` with verified guideline titles and similarity scores (**FR-04.5**).
  * Admin knowledge document ingestion API (`backend/api/v1/endpoints/admin.py`): Allows administrators to upload and vectorize new medical literature into the RAG repository (**FR-04.1**, **FR-08.1**).
  * 10 dedicated automated tests in `backend/tests/test_rag.py` bringing total test suite coverage to 80/80 passing tests (100% green).
* **AI Healthcare Chatbot & Clinical Guardrails (Phase 7 Completed):**
  * High-speed inference integration via **Groq LPU** (`backend/services/groq_service.py`) supporting Llama 3 models (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`) and real-time streaming (**FR-03.1**, **NFR-01.1**).
  * System prompt enforcing strict clinical safety rules: non-diagnostic mandate, prohibition on prescribing medications or calculating drug dosages, and mandatory clinical disclaimers (**FR-03.2**, **FR-03.4**).
  * Clinical emergency triage guardrail (`backend/services/triage_service.py`): Intercepts acute symptom red flags (e.g., crushing chest pain, difficulty breathing, stroke, slurred speech) and immediately displays urgent emergency directives with 112 / 911 contact info before LLM generation (**FR-03.3 / US-03**).
  * Multi-turn conversational persistence with PostgreSQL/SQLite (`backend/repositories/conversation_repo.py`): Full thread management, prior message context retention, history browsing rail, and thread deletion (**FR-03.5**).
  * Canva-styled conversational UI in Streamlit (`frontend/pages/2_AI_Chatbot.py`): Dynamic conversation rail, prompt chip buttons, red-card emergency alerts, and live message history.
  * 5 comprehensive automated tests in `backend/tests/test_chat.py` bringing total coverage to 70/70 passing tests (100% green).
* **Dashboard Development & Frontend-Backend Integration (Phase 6 Completed):**
  * Centralized, resilient HTTP API client (`frontend/api_client.py`) conforming to **NFR-03.2** with automatic Bearer token injection and graceful offline fallback handling.
  * Streamlit authentication integration (`frontend/pages/0_Login_Register.py`): Real registration and login flows with password complexity validation, automatic JWT session establishment, and error handling.
  * Live Dashboard synchronization (`frontend/pages/1_Dashboard.py`): Connected statistics cards (medical reports, active medications, upcoming appointments), medication adherence calculation, and dynamic activity timelines with live API status indicators.
  * Dynamic Patient Profile management (`frontend/pages/6_Profile.py`): Real-time sync with database, auto-calculated clinical vitals (Age, Blood Group, BMI), profile updates, and DPDP Act 2023 permanent cascading data erasure.
  * 4 comprehensive frontend-backend integration tests in `backend/tests/test_frontend_integration.py` bringing total test coverage to 65/65 passing tests (100% green).
* **Authentication & Authorization Security (Phase 5 Completed):**
  * Production-grade Argon2id cryptographic password hashing with unique salt and strict password complexity validation (min 8 chars, uppercase, lowercase, digit, special character).
  * Cryptographic JWT Bearer token lifecycle: HS256 encoding, claim verification (`sub`, `email`, `role`, `exp`), tampering protection, and automatic expiration handling.
  * Dependency injection security pipeline (`get_current_user`, `get_current_active_user`, `get_current_admin`) with automated Bearer extraction and RBAC role enforcement (`ROLE_USER` vs `ROLE_ADMIN`).
  * End-to-end authentication cycle: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, and `POST /api/v1/auth/logout`.
  * DPDP Act 2023 compliant profile management and cascading data erasure (`DELETE /api/v1/profile`).
  * 9 dedicated authentication & RBAC integration tests bringing total test coverage to 61/61 passing tests (100% green).
* **Database & Alembic Migrations (Phase 4 Completed):**
  * 10 complete SQLAlchemy 2.0 ORM models conforming to the SRS Data Dictionary.
  * pgvector extension support with 384-dimensional dense embeddings (`Vector(384)`) and HNSW cosine distance index (`vector_cosine_ops`).
  * Alembic migration revision `0001_initial` managing all tables, foreign keys, cascading rules, and indexes.
  * Asynchronous Clean Architecture repositories (`user_repo`, `report_repo`, `medication_repo`, `appointment_repo`, `knowledge_repo`, `audit_repo`).
  * DPDP Act 2023 permanent right to erasure verified with cascading deletes.
  * 12 automated database tests passing with 100% success rate.
* **Backend Core & Routers (Phase 3 Completed):**
  * Fully asynchronous REST API built with FastAPI conforming to Clean Architecture.
  * Standardized exception envelope (`{"status": "error", "message": "...", "detail": "..."}`) fulfilling **NFR-03.2**.
  * Emergency safety filter (`/api/v1/chat/query`) detecting acute symptoms and returning emergency directives (112/911) before LLM generation (**FR-03.3 / US-03**).
  * Role-Based Access Control (**FR-08.1 / US-08**) protecting `/api/v1/admin/` endpoints against non-admin callers.
  * 40 unit and integration tests passing with 100% success rate.
* **Streamlit UI Prototype (Phase 2 Completed):**
  * 12 Canva-aligned pages featuring vitals cards, 7-day wellness chart, medication dose cycles, interactive appointments calendar, and medical reports analysis.
