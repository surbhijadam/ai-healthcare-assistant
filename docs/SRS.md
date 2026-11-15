# Software Requirements Specification (SRS)
## Project: AI Healthcare Assistant

**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Project Phase:** Phase 1 – Project Planning and Requirement Analysis  
**Repository Path:** `ai-healthcare-assistant/`

---

## 1. Introduction

### 1.1 Purpose
This document provides a comprehensive description of the functional, non-functional, clinical safety, and architectural requirements for the **AI Healthcare Assistant** web platform. It serves as the single source of truth for design, development, testing, and deployment phases.

### 1.2 Scope & Boundaries
The AI Healthcare Assistant is an **educational health companion and personal health management system**.

#### In-Scope Capabilities
* User registration, profile personalization, and role-based access control (User vs. Admin).
* Centralized health dashboard tracking vitals, active prescriptions, and appointment alerts.
* Conversational AI chatbot powered by Groq LPU inference for answering general medical questions, explaining symptoms, and clarifying clinical terminology.
* Source-grounded Retrieval-Augmented Generation (RAG) backed by PostgreSQL `pgvector` and `Sentence-Transformers`.
* Automated parsing and structured explanation of uploaded PDF laboratory reports using PyMuPDF and PII redaction.
* Medication adherence logging and physician appointment scheduling.
* Administrative document ingestion, knowledge management, and audit log inspection.

#### Explicit Out-of-Scope Boundaries (Safety Constraints)
* **No Autonomous Medical Diagnosis:** The system will never declare that a user has a specific disease or medical condition.
* **No Prescription or Dosage Modification:** The system will never write prescriptions, alter drug dosages, or recommend schedule changes.
* **No Replacement for Emergency Services:** The system will actively intercept red-flag symptoms (e.g., suspected heart attack, stroke, acute trauma) and direct users to emergency hotlines (112 / 911).

### 1.3 Definitions, Acronyms, and Abbreviations
* **SRS:** Software Requirements Specification
* **RAG:** Retrieval-Augmented Generation
* **LLM:** Large Language Model (specifically Llama 3 via Groq)
* **pgvector:** PostgreSQL extension for high-dimensional vector similarity search
* **PII:** Personally Identifiable Information (names, phone numbers, addresses)
* **DPDP Act 2023:** Digital Personal Data Protection Act, 2023 (India)
* **HNSW:** Hierarchical Navigable Small World (graph-based vector index)
* **TTFT:** Time-To-First-Token (metric measuring LLM conversational responsiveness)
* **RBAC:** Role-Based Access Control

---

## 2. Overall System Description

### 2.1 Product Perspective
The platform is designed as a decoupled, two-tier web architecture:
1. **Frontend:** Built with Streamlit, providing an interactive, stateful, multi-page user interface.
2. **Backend:** Asynchronous REST API built with FastAPI, communicating with PostgreSQL 16 for both relational and vector data.
3. **AI Services:** Groq Cloud API for ultra-fast conversational inference; local `Sentence-Transformers` for vector embeddings; `PyMuPDF` for local PDF parsing.

### 2.2 User Classes & Personas

| Role Name | Description | Key Responsibilities |
| :--- | :--- | :--- |
| **`ROLE_USER`** (Patient / Caregiver) | Standard authenticated account. Manages personal health records, chats with the assistant, uploads reports, and tracks meds. | Maintain profile, upload personal lab reports, ask health queries, schedule appointments, track daily doses. |
| **`ROLE_ADMIN`** (Clinical Moderator) | Privileged administrative account. Manages the platform's knowledge base and reviews audit logs. | Ingest verified medical guidelines (PDFs), manage user accounts, inspect system audit logs and error metrics. |
| **System / Scheduled Task** | Automated internal processes. | Runs vector chunking, executes PII redactions, and records audit telemetry. |

### 2.3 User Role Permissions Matrix

| Module / Action | Anonymous Guest | Registered User (`ROLE_USER`) | Administrator (`ROLE_ADMIN`) |
| :--- | :---: | :---: | :---: |
| View Home / Landing Page | Read Only | Full Access | Full Access |
| Register / Login | Full Access | Full Access | Full Access |
| View Personal Dashboard | No | Full Access | Full Access (Self) |
| Interact with AI Chatbot | No | Full Access | Full Access |
| Upload & Analyze Lab Reports | No | Full Access (Own) | Full Access (Own) |
| Manage Medications | No | Full Access (Own) | Full Access (Own) |
| Manage Appointments | No | Full Access (Own) | Full Access (Own) |
| Ingest RAG Knowledge Documents | No | No | Full Access |
| View System Audit Logs | No | No | Full Access |
| Delete Personal Account (Erasure) | No | Full Access (Own) | Full Access (Any) |

---

## 3. Functional Requirements (FR)

### FR-01: Authentication, Authorization & User Profile
* **FR-01.1:** System shall allow user self-registration using a valid email, full name, and password meeting complexity standards (minimum 8 characters, at least 1 number and 1 special character).
* **FR-01.2:** System shall hash passwords using Argon2id with unique cryptographic salts prior to persistence.
* **FR-01.3:** System shall authenticate users and issue an encrypted JWT access token (valid for 60 minutes) upon successful credential verification.
* **FR-01.4:** System shall provide profile management allowing users to update demographic data: date of birth, gender, blood group, emergency contact phone, known allergies, and chronic conditions.
* **FR-01.5:** System shall provide an account deletion endpoint that executes a cascading delete of all user records, uploaded files, and chat history.

### FR-02: Health Overview Dashboard
* **FR-02.1:** System shall display a personalized health snapshot showing BMI calculation, blood group, and allergy tags.
* **FR-02.2:** System shall display summary metrics cards: Total Analyzed Reports, Active Medications Count, and Next Upcoming Appointment.
* **FR-02.3:** System shall present a chronological activity feed listing recent actions (e.g., reports uploaded, appointments booked).

### FR-03: AI Healthcare Chatbot with Safety Guardrails
* **FR-03.1:** System shall provide a conversational chat interface with real-time response streaming.
* **FR-03.2:** System shall prepend a non-diagnostic medical disclaimer to conversational sessions.
* **FR-03.3:** System shall scan user prompts against an emergency keyword dictionary (e.g., chest pain, stroke symptoms, acute shortness of breath). If detected, it shall display an immediate emergency alert with contact numbers (112 / 911) and withhold conversational LLM generation.
* **FR-03.4:** System shall prompt the LLM to strictly decline diagnosing medical conditions, calculating drug dosages, or recommending prescription changes.
* **FR-03.5:** System shall persist all conversation threads and message exchanges in the database, allowing users to browse prior chats.

### FR-04: RAG Healthcare Knowledge Base
* **FR-04.1:** System shall allow administrators to upload approved clinical reference PDFs and health guidelines.
* **FR-04.2:** System shall split ingested documents into recursive semantic chunks of 500 tokens with 50-token overlap.
* **FR-04.3:** System shall compute 384-dimensional dense vector embeddings using `all-MiniLM-L6-v2` and store them in PostgreSQL with `pgvector`.
* **FR-04.4:** System shall execute cosine distance similarity queries (`<=>`) against `document_chunks` using an HNSW index to retrieve the top 3 relevant chunks for any medical query.
* **FR-04.5:** System shall inject retrieved context into the LLM system prompt and output source document titles as citations.

### FR-05: Medical Report Assistant
* **FR-05.1:** System shall accept user-uploaded PDF lab reports (maximum file size: 10 MB, strictly validated MIME-type `application/pdf`).
* **FR-05.2:** System shall extract raw textual and tabular blocks using PyMuPDF (`fitz`).
* **FR-05.3:** System shall sanitize extracted text by scrubbing names, phone numbers, and street addresses before transmitting data to the LLM.
* **FR-05.4:** System shall prompt Groq LLM to extract laboratory parameters into structured JSON matching a strict schema (Test Name, Observed Value, Unit, Reference Range, Status Flag: `Normal`, `Elevated`, or `Low`).
* **FR-05.5:** System shall generate a plain-English educational summary describing what the test reflects and listing suggested questions for the patient to ask their doctor.
* **FR-05.6:** System shall save report metadata, extracted raw text, parsed JSON parameters, and AI summary to the `medical_reports` table.

### FR-06: Medication and Schedule Manager
* **FR-06.1:** System shall allow users to register medications with name, dosage, dosage form, frequency, start date, end date, and instructions.
* **FR-06.2:** System shall provide an interactive daily checklist where users can mark doses as "Taken" or "Skipped".
* **FR-06.3:** System shall display a prominent warning notice advising users never to alter or stop prescribed medications without physician guidance.

### FR-07: Appointment Management
* **FR-07.1:** System shall allow users to record doctor appointments including doctor name, specialty, clinic/hospital address, date, time, and reason for visit.
* **FR-07.2:** System shall allow users to mark appointment status as `Upcoming`, `Completed`, or `Cancelled`.
* **FR-07.3:** System shall allow users to attach custom notes and doctor discussion points to any appointment.

### FR-08: Admin Governance & Security Audit
* **FR-08.1:** System shall provide an admin dashboard accessible exclusively to accounts with `ROLE_ADMIN`.
* **FR-08.2:** System shall log all significant events (login success, login failure, report upload, report deletion, document ingestion) in the `audit_logs` table with user ID, IP address, and status.
* **FR-08.3:** System shall display real-time platform statistics to administrators: registered users count, total conversations, stored document count, and error counts.

---

## 4. Non-Functional Requirements (NFR)

### NFR-01: Performance & Responsiveness
* **NFR-01.1:** Time-To-First-Token (TTFT) for conversational chat responses shall not exceed 1.5 seconds when using Groq LPU inference.
* **NFR-01.2:** Vector similarity search using pgvector with HNSW indexing shall return top-3 matching chunks in under 20 milliseconds on a 10,000-chunk knowledge base.
* **NFR-01.3:** PDF report parsing and initial text extraction via PyMuPDF shall complete in under 2.0 seconds for documents up to 5 pages.
* **NFR-01.4:** Standard database read/write API endpoints shall respond in under 200 milliseconds under normal load.

### NFR-02: Security & Privacy Compliance
* **NFR-02.1:** Passwords shall be hashed using Argon2id with recommended memory and time cost parameters.
* **NFR-02.2:** All API communication shall enforce HTTPS with TLS 1.3 in production environments.
* **NFR-02.3:** Bearer JWT tokens shall expire after 60 minutes and be cryptographically verified on every protected request.
* **NFR-02.4:** 100% of database interactions shall use SQLAlchemy parameterized queries to prevent SQL injection.
* **NFR-02.5 (DPDP Act 2023):** The platform shall honor the "Right to Erasure" by permanently deleting all user data upon verified user request.
* **NFR-02.6:** Uploaded PDF files shall be stored using non-enumerable UUID file paths outside web-accessible roots to prevent directory traversal.

### NFR-03: Reliability & Availability
* **NFR-03.1:** The backend API shall be stateless, enabling horizontal scaling behind a reverse proxy or load balancer.
* **NFR-03.2:** Unhandled exceptions shall be intercepted by global exception handlers, returning standardized error JSON (`{ "status": "error", "message": "...", "detail": "..." }`) rather than leaking stack traces.

### NFR-04: Usability & Aesthetic Quality
* **NFR-04.1:** The UI shall feature a modern, responsive design using a clean healthcare palette (Deep Slate `#1E293B`, Medical Blue `#0E76A8`, Clean White `#F8FAFC`).
* **NFR-04.2:** Lab test status values shall be color-coded for instant clarity (Green = Normal, Amber/Red = Elevated or Low).
* **NFR-04.3:** The interface shall remain fully usable across desktop screens (>= 1280px) and tablets (>= 768px).

### NFR-05: Maintainability & Code Quality
* **NFR-05.1:** Clean Architecture principles shall be enforced, maintaining strict separation between API controllers, service business logic, and database models.
* **NFR-05.2:** Automated test suites using `pytest` shall cover at least 80% of backend route controllers and service modules.
* **NFR-05.3:** All database schema changes shall be managed through version-controlled Alembic migration scripts.

---

## 5. User Stories & Acceptance Criteria (Gherkin Format)

### US-01: User Registration & Login
> **As a** new patient,  
> **I want to** register an account and log in securely,  
> **So that** my personal medical reports and schedules are private to me.

* **Scenario: Successful Registration**
  * **Given** an unauthenticated visitor on the registration page,
  * **When** they submit a valid email, full name, and strong password,
  * **Then** an account is created with role `ROLE_USER`, password is stored as an Argon2id hash, and a confirmation message is displayed.

* **Scenario: Failed Login with Incorrect Password**
  * **Given** a registered user on the login page,
  * **When** they enter their email and an invalid password,
  * **Then** the system rejects the request with HTTP 401 Unauthorized and displays "Invalid email or password", logging the failure in `audit_logs`.

---

### US-02: AI Healthcare Question with RAG Retrieval
> **As a** patient,  
> **I want to** ask questions about a health topic (e.g., "What is a normal fasting blood sugar level?"),  
> **So that** I get an easy-to-understand explanation backed by medical guidelines.

* **Scenario: Grounded Question Answering**
  * **Given** an authenticated user in the Chatbot screen,
  * **When** they submit a factual medical query,
  * **Then** the system computes query embeddings, retrieves top-3 matching chunks from `document_chunks`, sends the augmented prompt to Groq LLM, streams the educational response, and displays the source document citations.

---

### US-03: Emergency Red-Flag Interception
> **As a** patient experiencing severe acute symptoms,  
> **I want to** be warned immediately if my symptoms require emergency intervention,  
> **So that** I do not delay seeking life-saving medical care.

* **Scenario: Emergency Symptom Triggered**
  * **Given** an authenticated user in the Chatbot screen,
  * **When** they type "I have sudden severe crushing chest pain radiating to my left arm",
  * **Then** the emergency triage filter catches the keywords, bypasses conversational LLM generation, and renders an urgent red alert card directing the user to dial emergency services (112 / 911) immediately.

---

### US-04: Medical Report PDF Upload and Analysis
> **As a** patient,  
> **I want to** upload a PDF of my laboratory test results,  
> **So that** I can see which values are within or outside normal ranges without clinical jargon.

* **Scenario: Successful Lab Report Explanation**
  * **Given** an authenticated user on the Medical Reports page,
  * **When** they upload a valid synthetic lab report PDF (e.g., Complete Blood Count),
  * **Then** PyMuPDF extracts the text, PII is redacted, Groq parses the parameters into structured JSON, the database records the report, and the UI displays a color-coded table of parameters alongside a patient-friendly summary.

---

### US-05: Medication Schedule Tracking
> **As a** patient on daily prescriptions,  
> **I want to** track my daily doses on a checklist,  
> **So that** I adhere to my treatment regimen consistently.

* **Scenario: Marking Dose as Taken**
  * **Given** an active medication registered on the user's account,
  * **When** the user checks the "Taken" box for today's morning dose,
  * **Then** the status updates in the database, the dashboard reflects the completed dose, and a success confirmation appears.

---

## 6. Formal Data Dictionary

| Table Name | Column Name | Data Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **`users`** | `id` | `INTEGER` | No | `PRIMARY KEY`, Auto-inc | Unique identifier for user |
| | `email` | `VARCHAR(255)` | No | `UNIQUE`, Indexed | User login email address |
| | `password_hash` | `VARCHAR(255)` | No | None | Argon2id cryptographic hash |
| | `role` | `VARCHAR(20)` | No | Default: `'user'` | Role (`'user'`, `'admin'`) |
| | `is_active` | `BOOLEAN` | No | Default: `TRUE` | Account active status flag |
| | `created_at` | `TIMESTAMPTZ` | No | Default: `NOW()` | Account creation timestamp |
| | `updated_at` | `TIMESTAMPTZ` | No | Default: `NOW()` | Profile last updated timestamp |
| **`user_profiles`** | `id` | `INTEGER` | No | `PRIMARY KEY`, Auto-inc | Profile primary key |
| | `user_id` | `INTEGER` | No | `UNIQUE`, `FK(users.id)` ON DELETE CASCADE | Associated user account |
| | `full_name` | `VARCHAR(100)` | No | None | User's full display name |
| | `date_of_birth` | `DATE` | Yes | None | Date of birth for age calculation |
| | `gender` | `VARCHAR(20)` | Yes | None | Biological sex / gender |
| | `blood_group` | `VARCHAR(10)` | Yes | None | Blood group (e.g., A+, O-) |
| | `emergency_contact` | `VARCHAR(50)` | Yes | None | Emergency phone number |
| | `allergies` | `TEXT` | Yes | None | Known allergies list |
| | `chronic_conditions` | `TEXT` | Yes | None | Existing medical conditions |
| **`conversations`** | `id` | `INTEGER` | No | `PRIMARY KEY`, Auto-inc | Unique conversation ID |
| | `user_id` | `INTEGER` | No | `FK(users.id)` ON DELETE CASCADE | Owner of the conversation |
| | `title` | `VARCHAR(150)` | No | Default: `'Health Query'` | User-defined or auto-generated title |
| | `created_at` | `TIMESTAMPTZ` | No | Default: `NOW()` | Conversation creation timestamp |
| **`messages`** | `id` | `INTEGER` | No | `PRIMARY KEY`, Auto-inc | Message unique ID |
| | `conversation_id` | `INTEGER` | No | `FK(conversations.id)` ON DELETE CASCADE | Parent conversation thread |
| | `sender_role` | `VARCHAR(20)` | No | Values: `user`,`assistant`,`system` | Identity of message author |
| | `content` | `TEXT` | No | None | Message body text |
| | `sources_used` | `JSONB` | Yes | Default: `NULL` | Array of cited document titles & chunk IDs |
| | `created_at` | `TIMESTAMPTZ` | No | Default: `NOW()` | Message timestamp |
| **`medical_reports`** | `id` | `INTEGER` | No | `PRIMARY KEY`, Auto-inc | Report record ID |
| | `user_id` | `INTEGER` | No | `FK(users.id)` ON DELETE CASCADE | Owner of the report |
| | `file_name` | `VARCHAR(255)` | No | None | Original uploaded file name |
| | `file_path` | `VARCHAR(500)` | No | None | Secure server storage file path |
| | `report_type` | `VARCHAR(100)` | Yes | None | Type (e.g., "Complete Blood Count") |
| | `extracted_raw_text` | `TEXT` | Yes | None | PyMuPDF extracted raw text |
| | `parsed_parameters` | `JSONB` | Yes | None | Structured parameters array |
| | `ai_summary` | `TEXT` | Yes | None | Simplified plain-English summary |
| | `uploaded_at` | `TIMESTAMPTZ` | No | Default: `NOW()` | File upload timestamp |
| **`medications`** | `id` | `INTEGER` | No | `PRIMARY KEY`, Auto-inc | Medication primary key |
| | `user_id` | `INTEGER` | No | `FK(users.id)` ON DELETE CASCADE | Owner of the prescription |
| | `medication_name` | `VARCHAR(150)` | No | None | Commercial or generic drug name |
| | `dosage` | `VARCHAR(50)` | No | None | Dosage amount (e.g., "500 mg") |
| | `frequency` | `VARCHAR(50)` | No | None | Frequency (e.g., "Twice daily") |
| | `start_date` | `DATE` | No | None | Regimen start date |
| | `end_date` | `DATE` | Yes | None | Regimen end date (optional) |
| | `instructions` | `TEXT` | Yes | None | Special instructions |
| | `is_active` | `BOOLEAN` | No | Default: `TRUE` | Active tracking flag |
| **`appointments`** | `id` | `INTEGER` | No | `PRIMARY KEY`, Auto-inc | Appointment ID |
| | `user_id` | `INTEGER` | No | `FK(users.id)` ON DELETE CASCADE | Associated user account |
| | `doctor_name` | `VARCHAR(100)` | No | None | Physician full name |
| | `specialty` | `VARCHAR(100)` | Yes | None | Clinical specialty |
| | `clinic_name` | `VARCHAR(200)` | Yes | None | Clinic or hospital name |
| | `appointment_datetime`| `TIMESTAMPTZ` | No | None | Scheduled date and time |
| | `status` | `VARCHAR(20)` | No | Default: `'upcoming'` | `upcoming`, `completed`, `cancelled` |
| | `notes` | `TEXT` | Yes | None | Discussion notes for the physician |
| **`knowledge_documents`**| `id` | `INTEGER` | No | `PRIMARY KEY`, Auto-inc | Knowledge document ID |
| | `title` | `VARCHAR(255)` | No | None | Guideline or document title |
| | `category` | `VARCHAR(100)` | Yes | None | Medical topic classification |
| | `source_url` | `VARCHAR(500)` | Yes | None | Link to source publication |
| | `uploaded_by` | `INTEGER` | Yes | `FK(users.id)` ON DELETE SET NULL | Admin who uploaded the document |
| | `created_at` | `TIMESTAMPTZ` | No | Default: `NOW()` | Upload timestamp |
| **`document_chunks`**| `id` | `INTEGER` | No | `PRIMARY KEY`, Auto-inc | Chunk ID |
| | `document_id` | `INTEGER` | No | `FK(knowledge_documents.id)` CASCADE| Parent reference document |
| | `chunk_index` | `INTEGER` | No | None | Sequential ordering index |
| | `chunk_text` | `TEXT` | No | None | Segmented text payload |
| | `embedding` | `VECTOR(384)` | No | None (HNSW Indexed) | 384-dimensional vector embedding |
| | `metadata` | `JSONB` | Yes | None | Extra attributes (page, header) |
| **`audit_logs`** | `id` | `INTEGER` | No | `PRIMARY KEY`, Auto-inc | Audit record ID |
| | `user_id` | `INTEGER` | Yes | `FK(users.id)` ON DELETE SET NULL | Acting user (if authenticated) |
| | `action` | `VARCHAR(100)` | No | None | Event name (e.g. `LOGIN_FAILED`) |
| | `ip_address` | `VARCHAR(45)` | Yes | None | Client IP address |
| | `status` | `VARCHAR(20)` | No | None | `SUCCESS` or `FAILED` |
| | `timestamp` | `TIMESTAMPTZ` | No | Default: `NOW()` | Event timestamp |

---

## 7. Approval & Sign-Off

This document forms the foundation for **Phase 2: UI/UX Design and Streamlit Setup**. All features, database columns, and validation parameters developed in subsequent phases must conform to the requirements specified herein.
