import sys
import asyncio
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.core.config import settings
from backend.core.security import hash_password_fallback
from backend.db.base import Base
from backend.db.session import async_engine, AsyncSessionLocal
from backend.db.models.user import User, UserProfile
from backend.db.models.knowledge import KnowledgeDocument, DocumentChunk


async def seed_data(session: AsyncSession) -> None:
    """Seeds baseline administrator user and verified clinical guidelines."""
    result = await session.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": "admin@example.com"}
    )
    existing_admin = result.scalar_one_or_none()

    if not existing_admin:
        admin_user = User(
            email="admin@example.com",
            password_hash=hash_password_fallback("AdminSecure2026!"),
            role="ROLE_ADMIN",
            is_active=True,
        )
        session.add(admin_user)
        await session.flush()

        admin_profile = UserProfile(
            user_id=admin_user.id,
            full_name="Dr. Clinical Administrator",
            preferred_language="English",
            country="India"
        )
        session.add(admin_profile)

        # Seed sample verified clinical guideline document
        guide_doc = KnowledgeDocument(
            title="Consensus Guidelines on Preventive Cardiovascular Health 2026",
            category="Cardiology",
            source_url="https://clinical.health.gov.in/guidelines/cvd-2026",
            uploaded_by=admin_user.id,
            status="Reviewed"
        )
        session.add(guide_doc)
        await session.commit()
        print("Baseline administrator and clinical reference knowledge seeded successfully.")
    else:
        print("Admin account already exists in database.")


async def init_db(use_sqlite_fallback: bool = False) -> None:
    """Initializes database schema, creates pgvector extension, and seeds default admin account."""
    if use_sqlite_fallback:
        db_url = "sqlite+aiosqlite:///./healthcare_dev.db"
        print(f"Initializing local development SQLite database: {db_url}")
        target_engine = create_async_engine(db_url, echo=False)
        target_session_factory = async_sessionmaker(
            bind=target_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        async with target_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with target_session_factory() as session:
            await seed_data(session)
        await target_engine.dispose()
        print("SQLite development database initialized successfully at ./healthcare_dev.db")
        return

    # Attempt PostgreSQL connection
    try:
        async with asyncio.timeout(5.0):
            async with async_engine.begin() as conn:
                if conn.dialect.name == "postgresql":
                    try:
                        async with conn.begin_nested():
                            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                            print("pgvector extension enabled in PostgreSQL.")
                    except Exception:
                        print("Note: pgvector extension not present in PostgreSQL. Using adaptive vector storage.")
                await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as session:
            await seed_data(session)
        print("PostgreSQL database initialized successfully.")

    except (OSError, TimeoutError, asyncio.TimeoutError, Exception) as err:
        print("\n" + "=" * 70)
        print("PostgreSQL Service Not Reachable")
        print("=" * 70)
        print(f"Connection to '{settings.DATABASE_URL}' was not established: {err}")
        print("\nTo start PostgreSQL 16 with pgvector via Docker, run:")
        print("   docker run --name healthcare-pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=healthcare_db -p 5432:5432 -d pgvector/pgvector:pg16")
        print("\nFalling back to local SQLite database (./healthcare_dev.db)...")
        print("=" * 70 + "\n")
        await init_db(use_sqlite_fallback=True)


if __name__ == "__main__":
    force_sqlite = "--sqlite" in sys.argv
    asyncio.run(init_db(use_sqlite_fallback=force_sqlite))
