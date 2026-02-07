from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, email: str, password_hash: str, name: str) -> User:
        user = User(
            email=email,
            password_hash=password_hash,
            name=name,
            graph_path=None,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        query = select(User.id).where(User.email == email)
        result = await self.db.execute(query)

        return result.scalar_one_or_none() is not None

    async def update_graph_path(self, user_id: int, graph_path: str) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.graph_path = graph_path
            await self.db.flush()

    async def update_indexed_count(self, user_id: int, count: int) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.dreams_indexed_count = count
            await self.db.flush()
