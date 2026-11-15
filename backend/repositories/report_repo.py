from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.report import MedicalReport
from backend.repositories.base import BaseRepository


class ReportRepository(BaseRepository[MedicalReport]):
    """Repository managing PDF medical reports and lab parameter extractions."""

    def __init__(self):
        super().__init__(MedicalReport)

    async def get_by_user(
        self, session: AsyncSession, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[MedicalReport]:
        result = await session.execute(
            select(MedicalReport)
            .where(MedicalReport.user_id == user_id)
            .order_by(MedicalReport.uploaded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_user_and_id(
        self, session: AsyncSession, user_id: int, report_id: int
    ) -> Optional[MedicalReport]:
        result = await session.execute(
            select(MedicalReport).where(
                MedicalReport.id == report_id,
                MedicalReport.user_id == user_id
            )
        )
        return result.scalars().first()

    async def create_report(
        self,
        session: AsyncSession,
        user_id: int,
        file_name: str,
        file_path: str,
        report_type: Optional[str] = None,
        extracted_raw_text: Optional[str] = None,
        parsed_parameters: Optional[List[Dict[str, Any]]] = None,
        ai_summary: Optional[str] = None,
        doctor_discussion_points: Optional[List[str]] = None,
    ) -> MedicalReport:
        report = MedicalReport(
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
            report_type=report_type,
            extracted_raw_text=extracted_raw_text,
            parsed_parameters=parsed_parameters,
            ai_summary=ai_summary,
            doctor_discussion_points=doctor_discussion_points,
            status="Reviewed"
        )
        session.add(report)
        await session.flush()
        await session.refresh(report)
        return report

    async def delete_report(
        self, session: AsyncSession, user_id: int, report_id: int
    ) -> bool:
        report = await self.get_by_user_and_id(session, user_id, report_id)
        if not report:
            return False
        await session.delete(report)
        await session.flush()
        return True


report_repo = ReportRepository()
