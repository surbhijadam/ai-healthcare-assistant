"""
MediCare AI — Conversation & Message Asynchronous Repository
Conforms to FR-03.5 (Conversation persistence) and Clean Architecture.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete, desc, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.base import BaseRepository
from backend.db.models.conversation import Conversation, Message


class ConversationRepository(BaseRepository[Conversation]):
    """Data access repository for Conversations and Messages."""

    def __init__(self):
        super().__init__(Conversation)

    async def list_conversations(
        self,
        session: AsyncSession,
        user_id: int,
        limit: int = 50
    ) -> List[Conversation]:
        """Lists user conversation threads ordered by newest first with messages preloaded."""
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages))
            .order_by(desc(Conversation.created_at))
            .limit(limit)
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def get_conversation(
        self,
        session: AsyncSession,
        conversation_id: int,
        user_id: int
    ) -> Optional[Conversation]:
        """Retrieves a single conversation for a user."""
        stmt = (
            select(Conversation)
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages))
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_conversation(
        self,
        session: AsyncSession,
        user_id: int,
        title: str = "Health Consultation"
    ) -> Conversation:
        """Creates a new conversation thread."""
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation

    async def get_messages(
        self,
        session: AsyncSession,
        conversation_id: int
    ) -> List[Message]:
        """Retrieves all messages for a specific conversation in chronological order."""
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def add_message(
        self,
        session: AsyncSession,
        conversation_id: int,
        sender_role: str,
        content: str,
        sources_used: Optional[List[Dict[str, Any]]] = None
    ) -> Message:
        """Adds a message to a conversation thread."""
        message = Message(
            conversation_id=conversation_id,
            sender_role=sender_role,
            content=content,
            sources_used=sources_used
        )
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message

    async def delete_conversation(
        self,
        session: AsyncSession,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """Deletes a conversation and cascades message deletions."""
        stmt = delete(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        res = await session.execute(stmt)
        await session.commit()
        return res.rowcount > 0


# Global repository instance
conversation_repo = ConversationRepository()
