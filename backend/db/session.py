from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from backend.core.config import settings

# 1. Asynchronous SQLAlchemy Engine for FastAPI request lifecycle
# Configured with pool_pre_ping to automatically recover from stale connections
async_engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

# 2. Asynchronous Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# 3. Synchronous SQLAlchemy Engine for Alembic migrations and CLI tasks
# Lazily initialized to prevent ModuleNotFoundError when psycopg/libpq is absent
_sync_engine = None


def get_sync_engine():
    global _sync_engine
    if _sync_engine is None:
        try:
            _sync_engine = create_engine(
                settings.SYNC_DATABASE_URL,
                echo=settings.DEBUG,
                future=True,
                pool_pre_ping=True,
            )
        except Exception:
            _sync_engine = create_engine("sqlite:///./healthcare_dev.db", future=True)
    return _sync_engine


def __getattr__(name: str):
    if name == "sync_engine":
        return get_sync_engine()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# 4. Dependency Injection for FastAPI Route Handlers
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an asynchronous SQLAlchemy database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            if session.is_active:
                await session.commit()
        except Exception:
            if session.is_active:
                await session.rollback()
            raise
        finally:
            await session.close()


def get_test_async_engine(database_url: str) -> AsyncEngine:
    """Helper creating an isolated async engine for testing and CI pipelines."""
    return create_async_engine(
        database_url,
        echo=False,
        future=True,
    )
