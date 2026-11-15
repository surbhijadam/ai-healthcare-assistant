"""Initial schema with PostgreSQL tables and pgvector HNSW indexing

Revision ID: 0001_initial
Revises: None
Create Date: 2026-11-15 12:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Enable pgvector extension if PostgreSQL dialect
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 1. users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), server_default="ROLE_USER", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users")
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. user_profiles table
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("blood_group", sa.String(length=10), nullable=True),
        sa.Column("emergency_contact", sa.String(length=50), nullable=True),
        sa.Column("allergies", sa.Text(), nullable=True),
        sa.Column("chronic_conditions", sa.Text(), nullable=True),
        sa.Column("height_cm", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("preferred_language", sa.String(length=50), server_default="English", nullable=True),
        sa.Column("country", sa.String(length=100), server_default="India", nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("lifestyle_data", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_profiles_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_user_profiles")
    )
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"], unique=True)

    # 3. conversations table
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=150), server_default="Health Query", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_conversations_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_conversations")
    )
    op.create_index("ix_conversations_user_id", "conversations", ["user_id"], unique=False)

    # 4. messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("sender_role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sources_used", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], name="fk_messages_conversation_id_conversations", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_messages")
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"], unique=False)

    # 5. medical_reports table
    op.create_table(
        "medical_reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("report_type", sa.String(length=100), nullable=True),
        sa.Column("extracted_raw_text", sa.Text(), nullable=True),
        sa.Column("parsed_parameters", sa.JSON(), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("doctor_discussion_points", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="Reviewed", nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_medical_reports_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_medical_reports")
    )
    op.create_index("ix_medical_reports_user_id", "medical_reports", ["user_id"], unique=False)

    # 6. medications table
    op.create_table(
        "medications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("medication_name", sa.String(length=150), nullable=False),
        sa.Column("dosage", sa.String(length=50), nullable=False),
        sa.Column("frequency", sa.String(length=50), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("today_status", sa.String(length=20), server_default="Upcoming", nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_medications_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_medications")
    )
    op.create_index("ix_medications_user_id", "medications", ["user_id"], unique=False)

    # 7. appointments table
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("doctor_name", sa.String(length=100), nullable=False),
        sa.Column("specialty", sa.String(length=100), nullable=True),
        sa.Column("clinic_name", sa.String(length=200), nullable=True),
        sa.Column("appointment_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="upcoming", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_appointments_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_appointments")
    )
    op.create_index("ix_appointments_user_id", "appointments", ["user_id"], unique=False)

    # 8. knowledge_documents table
    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=100), server_default="Clinical Guideline", nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="Reviewed", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], name="fk_knowledge_documents_uploaded_by_users", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_knowledge_documents")
    )

    # 9. document_chunks table with pgvector embedding
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["knowledge_documents.id"], name="fk_document_chunks_document_id_knowledge_documents", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_document_chunks")
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"], unique=False)

    # Add HNSW index for sub-20ms vector cosine distance similarity queries (NFR-01.2)
    if bind.dialect.name == "postgresql":
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw "
            "ON document_chunks USING hnsw (embedding vector_cosine_ops);"
        )

    # 10. audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_audit_logs_user_id_users", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs")
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("document_chunks")
    op.drop_table("knowledge_documents")
    op.drop_table("appointments")
    op.drop_table("medications")
    op.drop_table("medical_reports")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("user_profiles")
    op.drop_table("users")
