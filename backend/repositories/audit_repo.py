from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.audit import AuditLog
from backend.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Repository managing security and administrative audit trails (FR-08.2)."""

    def __init__(self):
        super().__init__(AuditLog)

    async def log_event(
        self,
        session: AsyncSession,
        action: str,
        status: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            status=status,
        )
        session.add(log_entry)
        await session.flush()
        await session.refresh(log_entry)
        return log_entry

    async def get_recent_logs(
        self, session: AsyncSession, limit: int = 50, skip: int = 0
    ) -> List[AuditLog]:
        result = await session.execute(
            select(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())


audit_repo = AuditRepository()
