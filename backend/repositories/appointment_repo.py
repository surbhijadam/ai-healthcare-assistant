from typing import Optional, List, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.appointment import Appointment
from backend.repositories.base import BaseRepository


class AppointmentRepository(BaseRepository[Appointment]):
    """Repository managing clinical appointments."""

    def __init__(self):
        super().__init__(Appointment)

    async def get_by_user(
        self, session: AsyncSession, user_id: int, status_filter: Optional[str] = None
    ) -> List[Appointment]:
        query = select(Appointment).where(Appointment.user_id == user_id)
        if status_filter:
            query = query.where(Appointment.status == status_filter)
        query = query.order_by(Appointment.appointment_datetime.asc())
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_by_user_and_id(
        self, session: AsyncSession, user_id: int, appointment_id: int
    ) -> Optional[Appointment]:
        result = await session.execute(
            select(Appointment).where(
                Appointment.id == appointment_id,
                Appointment.user_id == user_id
            )
        )
        return result.scalars().first()

    async def delete_appointment(
        self, session: AsyncSession, user_id: int, appointment_id: int
    ) -> bool:
        appt = await self.get_by_user_and_id(session, user_id, appointment_id)
        if not appt:
            return False
        await session.delete(appt)
        await session.flush()
        return True


appointment_repo = AppointmentRepository()
