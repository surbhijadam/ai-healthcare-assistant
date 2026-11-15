from typing import Optional, List, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.medication import Medication
from backend.repositories.base import BaseRepository


class MedicationRepository(BaseRepository[Medication]):
    """Repository managing user prescriptions and daily adherence statuses."""

    def __init__(self):
        super().__init__(Medication)

    async def get_by_user(
        self, session: AsyncSession, user_id: int, active_only: bool = True
    ) -> List[Medication]:
        query = select(Medication).where(Medication.user_id == user_id)
        if active_only:
            query = query.where(Medication.is_active.is_(True))
        query = query.order_by(Medication.start_date.desc())
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_by_user_and_id(
        self, session: AsyncSession, user_id: int, medication_id: int
    ) -> Optional[Medication]:
        result = await session.execute(
            select(Medication).where(
                Medication.id == medication_id,
                Medication.user_id == user_id
            )
        )
        return result.scalars().first()

    async def toggle_status(
        self, session: AsyncSession, user_id: int, medication_id: int, new_status: str
    ) -> Optional[Medication]:
        med = await self.get_by_user_and_id(session, user_id, medication_id)
        if not med:
            return None
        med.today_status = new_status
        session.add(med)
        await session.flush()
        await session.refresh(med)
        return med

    async def delete_medication(
        self, session: AsyncSession, user_id: int, medication_id: int
    ) -> bool:
        med = await self.get_by_user_and_id(session, user_id, medication_id)
        if not med:
            return False
        await session.delete(med)
        await session.flush()
        return True


medication_repo = MedicationRepository()
