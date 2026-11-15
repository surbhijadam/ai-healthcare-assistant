from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.user import User, UserProfile
from backend.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository managing User accounts and clinical UserProfiles."""

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        result = await session.execute(
            select(User).options(selectinload(User.profile)).where(User.email == email)
        )
        return result.scalars().first()

    async def get_with_profile(self, session: AsyncSession, user_id: int) -> Optional[User]:
        result = await session.execute(
            select(User).options(selectinload(User.profile)).where(User.id == user_id)
        )
        return result.scalars().first()

    async def create_user_with_profile(
        self,
        session: AsyncSession,
        email: str,
        password_hash: str,
        full_name: str,
        role: str = "ROLE_USER",
        **profile_kwargs: Any
    ) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
        )
        profile = UserProfile(
            full_name=full_name,
            **profile_kwargs
        )
        user.profile = profile
        session.add(user)
        await session.flush()
        return user

    async def get_profile(self, session: AsyncSession, user_id: int) -> Optional[UserProfile]:
        result = await session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalars().first()

    async def update_profile(
        self, session: AsyncSession, user_id: int, **update_fields: Any
    ) -> Optional[UserProfile]:
        profile = await self.get_profile(session, user_id)
        if not profile:
            return None
        for field, value in update_fields.items():
            if hasattr(profile, field) and value is not None:
                setattr(profile, field, value)
        session.add(profile)
        await session.flush()
        await session.refresh(profile)
        return profile

    async def delete_user_and_all_data(self, session: AsyncSession, user_id: int) -> bool:
        """Enforces DPDP Act 2023 permanent right to erasure."""
        user = await self.get(session, user_id)
        if not user:
            return False
        # Cascading deletes will remove profile, reports, messages, meds, appts
        await session.delete(user)
        await session.flush()
        return True


user_repo = UserRepository()
