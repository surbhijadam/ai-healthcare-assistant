import pytest
import pytest_asyncio
from datetime import date, datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.db.base import Base
from backend.db.models import (
    User,
    UserProfile,
    Conversation,
    Message,
    MedicalReport,
    Medication,
    Appointment,
    KnowledgeDocument,
    DocumentChunk,
    AuditLog,
)
from backend.repositories import (
    user_repo,
    report_repo,
    medication_repo,
    appointment_repo,
    knowledge_repo,
    audit_repo,
)


@pytest_asyncio.fixture
async def async_db_session():
    """Provides an isolated in-memory SQLite async database session for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    await engine.dispose()


# ==============================================================================
# 1. Schema & Metadata Verification
# ==============================================================================

def test_schema_all_tables_registered():
    """Verifies that all 10 core tables from the Data Dictionary are registered."""
    expected_tables = {
        "users",
        "user_profiles",
        "conversations",
        "messages",
        "medical_reports",
        "medications",
        "appointments",
        "knowledge_documents",
        "document_chunks",
        "audit_logs",
    }
    registered = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(registered), f"Missing tables: {expected_tables - registered}"


# ==============================================================================
# 2. User & Clinical Profile Creation & Calculation (FR-01.1, FR-01.4)
# ==============================================================================

@pytest.mark.asyncio
async def test_user_and_profile_creation(async_db_session: AsyncSession):
    user = await user_repo.create_user_with_profile(
        session=async_db_session,
        email="ananya.sharma@example.com",
        password_hash="argon2_hashed_secret",
        full_name="Ananya Sharma",
        date_of_birth=date(1996, 5, 14),
        gender="Female",
        blood_group="B+",
        height_cm=165.0,
        weight_kg=58.5,
        allergies="Penicillin",
        chronic_conditions="Mild intermittent asthma",
        emergency_contact="+91 98111 22334"
    )
    await async_db_session.commit()

    assert user.id is not None
    assert user.email == "ananya.sharma@example.com"
    assert user.role == "ROLE_USER"
    assert user.profile is not None
    assert user.profile.full_name == "Ananya Sharma"

    # Test dynamic age and BMI calculation
    today = date.today()
    expected_age = today.year - 1996 - ((today.month, today.day) < (5, 14))
    assert user.profile.calculated_age == expected_age

    expected_bmi = round(58.5 / ((165.0 / 100.0) ** 2), 1)
    assert user.profile.calculated_bmi == expected_bmi


@pytest.mark.asyncio
async def test_profile_update(async_db_session: AsyncSession):
    user = await user_repo.create_user_with_profile(
        session=async_db_session,
        email="patient.update@example.com",
        password_hash="hashed_pw",
        full_name="Initial Name",
        weight_kg=60.0
    )
    await async_db_session.commit()

    updated = await user_repo.update_profile(
        session=async_db_session,
        user_id=user.id,
        full_name="Updated Name",
        weight_kg=62.5,
        allergies="Sulfa drugs"
    )
    await async_db_session.commit()

    assert updated is not None
    assert updated.full_name == "Updated Name"
    assert updated.weight_kg == 62.5
    assert updated.allergies == "Sulfa drugs"


# ==============================================================================
# 3. Conversations & Messages (FR-03.1 - FR-03.5)
# ==============================================================================

@pytest.mark.asyncio
async def test_conversations_and_messages(async_db_session: AsyncSession):
    user = await user_repo.create_user_with_profile(
        session=async_db_session,
        email="chat.user@example.com",
        password_hash="hash",
        full_name="Chat User"
    )
    await async_db_session.commit()

    # Create conversation
    convo = Conversation(user_id=user.id, title="Understanding Blood Pressure")
    async_db_session.add(convo)
    await async_db_session.flush()

    # Add messages
    user_msg = Message(
        conversation_id=convo.id,
        sender_role="user",
        content="What is normal blood pressure?"
    )
    assistant_msg = Message(
        conversation_id=convo.id,
        sender_role="assistant",
        content="A normal blood pressure reading is generally considered less than 120/80 mmHg.",
        sources_used=[{"document_title": "AHA Hypertension Guidelines", "chunk_id": 12}]
    )
    async_db_session.add_all([user_msg, assistant_msg])
    await async_db_session.commit()

    # Query back
    result = await async_db_session.execute(
        select(Conversation).where(Conversation.id == convo.id)
    )
    loaded_convo = result.scalars().first()
    assert loaded_convo is not None
    assert loaded_convo.title == "Understanding Blood Pressure"

    msgs_res = await async_db_session.execute(
        select(Message).where(Message.conversation_id == convo.id).order_by(Message.id.asc())
    )
    messages = list(msgs_res.scalars().all())
    assert len(messages) == 2
    assert messages[0].sender_role == "user"
    assert messages[1].sender_role == "assistant"
    assert messages[1].sources_used[0]["document_title"] == "AHA Hypertension Guidelines"


# ==============================================================================
# 4. Medical Reports & Extracted Lab Parameters (FR-02.1 - FR-02.5, US-02)
# ==============================================================================

@pytest.mark.asyncio
async def test_medical_reports_crud(async_db_session: AsyncSession):
    user = await user_repo.create_user_with_profile(
        session=async_db_session,
        email="report.patient@example.com",
        password_hash="hash",
        full_name="Report Patient"
    )
    await async_db_session.commit()

    lab_params = [
        {
            "test_name": "Haemoglobin",
            "observed_value": "13.2",
            "reference_range": "12.0–15.5",
            "unit": "g/dL",
            "status": "Normal"
        },
        {
            "test_name": "LDL Cholesterol",
            "observed_value": "108",
            "reference_range": "< 100",
            "unit": "mg/dL",
            "status": "Elevated"
        }
    ]

    report = await report_repo.create_report(
        session=async_db_session,
        user_id=user.id,
        file_name="Annual_wellness_panel.pdf",
        file_path="/storage/reports/Annual_wellness_panel.pdf",
        report_type="Comprehensive Metabolic Panel",
        extracted_raw_text="Patient: Report Patient ... Haemoglobin 13.2 ... LDL 108",
        parsed_parameters=lab_params,
        ai_summary="All parameters are within normal reference limits except for mildly elevated LDL.",
        doctor_discussion_points=["Discuss nutrition habits regarding LDL cholesterol."]
    )
    await async_db_session.commit()

    assert report.id is not None
    assert report.status == "Reviewed"
    assert len(report.parsed_parameters) == 2
    assert report.parsed_parameters[1]["status"] == "Elevated"

    user_reports = await report_repo.get_by_user(async_db_session, user.id)
    assert len(user_reports) == 1
    assert user_reports[0].file_name == "Annual_wellness_panel.pdf"


# ==============================================================================
# 5. Medications & Adherence Tracking (FR-04.1 - FR-04.4, US-04)
# ==============================================================================

@pytest.mark.asyncio
async def test_medications_adherence(async_db_session: AsyncSession):
    user = await user_repo.create_user_with_profile(
        session=async_db_session,
        email="med.patient@example.com",
        password_hash="hash",
        full_name="Med Patient"
    )
    await async_db_session.commit()

    med = Medication(
        user_id=user.id,
        medication_name="Metformin 500mg",
        dosage="500 mg",
        frequency="Twice daily with meals",
        start_date=date(2026, 10, 1),
        category="Diabetes Management",
        is_active=True,
        today_status="Upcoming"
    )
    async_db_session.add(med)
    await async_db_session.commit()

    assert med.id is not None
    assert med.today_status == "Upcoming"

    # Toggle dose status to Taken
    updated_med = await medication_repo.toggle_status(
        async_db_session, user.id, med.id, "Taken"
    )
    await async_db_session.commit()
    assert updated_med.today_status == "Taken"

    # Toggle dose status to Skipped
    updated_med = await medication_repo.toggle_status(
        async_db_session, user.id, med.id, "Skipped"
    )
    await async_db_session.commit()
    assert updated_med.today_status == "Skipped"


# ==============================================================================
# 6. Appointments Management (FR-05.1 - FR-05.3, US-05)
# ==============================================================================

@pytest.mark.asyncio
async def test_appointments_crud(async_db_session: AsyncSession):
    user = await user_repo.create_user_with_profile(
        session=async_db_session,
        email="appt.patient@example.com",
        password_hash="hash",
        full_name="Appt Patient"
    )
    await async_db_session.commit()

    appt_time = datetime(2026, 12, 10, 10, 30, tzinfo=timezone.utc)
    appt = Appointment(
        user_id=user.id,
        doctor_name="Dr. Meera Shah",
        specialty="General Medicine",
        clinic_name="Apex Healthcare Clinic",
        appointment_datetime=appt_time,
        status="upcoming",
        notes="Annual preventive wellness review"
    )
    async_db_session.add(appt)
    await async_db_session.commit()

    assert appt.id is not None
    assert appt.doctor_name == "Dr. Meera Shah"

    # Query appointments by user
    appts = await appointment_repo.get_by_user(async_db_session, user.id)
    assert len(appts) == 1
    assert appts[0].specialty == "General Medicine"


# ==============================================================================
# 7. Knowledge Documents & Vector Chunks (FR-04.1 - FR-04.4)
# ==============================================================================

@pytest.mark.asyncio
async def test_knowledge_document_and_chunks(async_db_session: AsyncSession):
    admin = await user_repo.create_user_with_profile(
        session=async_db_session,
        email="admin.doc@example.com",
        password_hash="hash",
        full_name="Admin Doc",
        role="ROLE_ADMIN"
    )
    await async_db_session.commit()

    doc = await knowledge_repo.create_document(
        session=async_db_session,
        title="Asthma Management Guidelines 2026",
        category="Pulmonology",
        source_url="https://ginasthma.org/2026-report",
        uploaded_by=admin.id
    )
    await async_db_session.commit()

    assert doc.id is not None
    assert doc.title == "Asthma Management Guidelines 2026"

    # Synthetic 384-dimensional vector embedding
    mock_vector = [0.05] * 384
    chunks = await knowledge_repo.add_chunks(
        session=async_db_session,
        document_id=doc.id,
        chunks_data=[
            {
                "chunk_index": 0,
                "chunk_text": "Inhaled corticosteroids form the cornerstone of regular asthma maintenance therapy.",
                "embedding": mock_vector,
                "metadata": {"page": 1, "section": "Treatment"}
            }
        ]
    )
    await async_db_session.commit()

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert len(chunks[0].embedding) == 384


# ==============================================================================
# 8. Audit Logging (FR-08.2)
# ==============================================================================

@pytest.mark.asyncio
async def test_audit_logs(async_db_session: AsyncSession):
    log1 = await audit_repo.log_event(
        session=async_db_session,
        action="USER_LOGIN_SUCCESS",
        status="SUCCESS",
        user_id=1,
        ip_address="192.168.1.100"
    )
    log2 = await audit_repo.log_event(
        session=async_db_session,
        action="LOGIN_FAILED",
        status="FAILED",
        user_id=None,
        ip_address="203.0.113.50"
    )
    await async_db_session.commit()

    assert log1.id is not None
    assert log2.id is not None

    recent_logs = await audit_repo.get_recent_logs(async_db_session, limit=10)
    assert len(recent_logs) >= 2
    actions = [l.action for l in recent_logs]
    assert "USER_LOGIN_SUCCESS" in actions
    assert "LOGIN_FAILED" in actions


# ==============================================================================
# 9. Cascading Deletes & DPDP Act 2023 Right to Erasure (FR-01.4)
# ==============================================================================

@pytest.mark.asyncio
async def test_cascading_deletes_dpdp(async_db_session: AsyncSession):
    """Verifies that deleting a user account cascades to erase all associated personal records."""
    user = await user_repo.create_user_with_profile(
        session=async_db_session,
        email="delete.me@example.com",
        password_hash="hash",
        full_name="Delete Me"
    )
    await async_db_session.commit()
    user_id = user.id

    # Add child records
    convo = Conversation(user_id=user_id, title="Test Conversation")
    report = MedicalReport(
        user_id=user_id, file_name="Test.pdf", file_path="/tmp/test.pdf"
    )
    med = Medication(
        user_id=user_id,
        medication_name="Aspirin",
        dosage="81mg",
        frequency="Daily",
        start_date=date(2026, 1, 1)
    )
    appt = Appointment(
        user_id=user_id,
        doctor_name="Dr. Test",
        appointment_datetime=datetime.now(timezone.utc)
    )
    async_db_session.add_all([convo, report, med, appt])
    await async_db_session.commit()

    # Erase user under DPDP Act 2023
    deleted = await user_repo.delete_user_and_all_data(async_db_session, user_id)
    await async_db_session.commit()
    assert deleted is True

    # Confirm user is erased
    assert await user_repo.get(async_db_session, user_id) is None

    # Confirm all cascading records are deleted
    profile_check = await async_db_session.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    assert profile_check.scalars().first() is None

    convo_check = await async_db_session.execute(
        select(Conversation).where(Conversation.user_id == user_id)
    )
    assert convo_check.scalars().first() is None

    report_check = await async_db_session.execute(
        select(MedicalReport).where(MedicalReport.user_id == user_id)
    )
    assert report_check.scalars().first() is None

    med_check = await async_db_session.execute(
        select(Medication).where(Medication.user_id == user_id)
    )
    assert med_check.scalars().first() is None

    appt_check = await async_db_session.execute(
        select(Appointment).where(Appointment.user_id == user_id)
    )
    assert appt_check.scalars().first() is None


# ==============================================================================
# 10. Alembic Migration & DDL Verification (NFR-05.3)
# ==============================================================================

def test_alembic_migration_head():
    """Verifies Alembic environment, migration head, and script location."""
    import os
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    alembic_cfg = Config(os.path.abspath("alembic.ini"))
    script = ScriptDirectory.from_config(alembic_cfg)
    heads = script.get_heads()
    assert heads == ["0001_initial"]

    rev = script.get_revision("0001_initial")
    assert rev is not None
    assert "pgvector" in rev.doc.lower()


def test_alembic_offline_sql_generation():
    """Verifies that Alembic can compile the complete DDL to static SQL."""
    import os
    import io
    from contextlib import redirect_stdout
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config(os.path.abspath("alembic.ini"))
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        command.upgrade(alembic_cfg, "head", sql=True)

    sql_output = buffer.getvalue()
    assert "CREATE EXTENSION IF NOT EXISTS vector" in sql_output
    assert "CREATE TABLE users" in sql_output
    assert "CREATE TABLE document_chunks" in sql_output
    assert "hnsw" in sql_output

