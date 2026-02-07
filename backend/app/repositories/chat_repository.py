from typing import Optional
from datetime import datetime

from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chats import Chat
from app.models.chat_messages import ChatMessage
from app.models.enums.dream_enums import ChatRole, QueryType


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(
            self,
            user_id: int,
            name: Optional[str] = None,
    ) -> Chat:
        if not name:
            count = await self._get_chat_count(user_id)
            name = f"Chat {count + 1}"

        chat = Chat(
            user_id=user_id,
            name=name,
        )
        self.db.add(chat)
        await self.db.flush()
        await self.db.refresh(chat)

        return chat

    async def get_chat(
            self,
            chat_id: int,
            user_id: int,
    ) -> Optional[Chat]:
        query = select(Chat).where(
            and_(Chat.id == chat_id, Chat.user_id == user_id)
        )
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def list_chats(
            self,
            user_id: int,
            per_page: int = 20,
            cursor: Optional[int] = None,
    ) -> tuple[list[Chat], bool]:
        query = select(Chat).where(Chat.user_id == user_id)
        if cursor:
            query = query.where(Chat.id < cursor)

        query = query.order_by(Chat.updated_at.desc(), Chat.id.desc()).limit(per_page + 1)

        result = await self.db.execute(query)
        chats = list(result.scalars().all())

        has_more = len(chats) > per_page
        if has_more:
            chats = chats[:per_page]

        return chats, has_more

    async def update_chat(
            self,
            chat_id: int,
            user_id: int,
            name: str,
    ) -> Optional[Chat]:
        chat = await self.get_chat(chat_id, user_id)
        if not chat:
            return None

        chat.name = name
        await self.db.flush()
        await self.db.refresh(chat)

        return chat

    async def delete_chat(
            self,
            chat_id: int,
            user_id: int,
    ) -> bool:
        chat = await self.get_chat(chat_id, user_id)
        if not chat:
            return False

        await self.db.delete(chat)
        await self.db.flush()

        return True

    async def touch_chat(self, chat_id: int) -> None:
        stmt = (
            update(Chat)
            .where(Chat.id == chat_id)
            .values(updated_at=datetime.utcnow())
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def add_message(
            self,
            chat_id: int,
            role: str,
            content: str,
            source_dream_ids: Optional[list[int]] = None,
            source_excerpts: Optional[list[dict]] = None,
            query_type: Optional[str] = None,
            processing_time_ms: Optional[int] = None,
    ) -> ChatMessage:
        try:
            query_type = QueryType(query_type)
        except Exception:
            query_type = QueryType.GENERAL

        message = ChatMessage(
            chat_id=chat_id,
            role=ChatRole(role),
            content=content,
            source_dream_ids=source_dream_ids or [],
            source_excerpts=source_excerpts or [],
            query_type=query_type,
            processing_time_ms=processing_time_ms,
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        await self.touch_chat(chat_id)

        return message

    async def get_messages(
            self,
            chat_id: int,
            limit: Optional[int] = None,
    ) -> list[ChatMessage]:
        query = (
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at.asc())
        )

        if limit:
            query = query.limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_message_count(self, chat_id: int) -> int:
        query = select(func.count(ChatMessage.id)).where(ChatMessage.chat_id == chat_id)
        result = await self.db.execute(query)

        return result.scalar() or 0

    async def get_chat_with_messages(
            self,
            chat_id: int,
            user_id: int,
    ) -> Optional[tuple[Chat, list[ChatMessage]]]:
        chat = await self.get_chat(chat_id, user_id)
        if not chat:
            return None

        messages = await self.get_messages(chat_id)

        return chat, messages

    async def _get_chat_count(self, user_id: int) -> int:
        query = select(func.count(Chat.id)).where(Chat.user_id == user_id)
        result = await self.db.execute(query)

        return result.scalar() or 0

    async def chat_exists(self, chat_id: int, user_id: int) -> bool:
        query = select(Chat.id).where(
            and_(Chat.id == chat_id, Chat.user_id == user_id)
        )
        result = await self.db.execute(query)
        
        return result.scalar_one_or_none() is not None
