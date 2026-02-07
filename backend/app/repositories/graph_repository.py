from typing import Optional
from datetime import datetime

from sqlalchemy import select, func, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dreams import Dream
from app.models.users import User


class GraphRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_indexing_stats(self, user_id: int) -> dict:
        total_query = select(func.count(Dream.id)).where(Dream.user_id == user_id)
        total_result = await self.db.execute(total_query)
        total_dreams = total_result.scalar() or 0

        indexed_query = select(func.count(Dream.id)).where(
            and_(Dream.user_id == user_id, Dream.is_indexed == True)
        )
        indexed_result = await self.db.execute(indexed_query)
        indexed_dreams = indexed_result.scalar() or 0

        last_indexed_query = (
            select(Dream.updated_at)
            .where(and_(Dream.user_id == user_id, Dream.is_indexed == True))
            .order_by(Dream.updated_at.desc())
            .limit(1)
        )
        last_indexed_result = await self.db.execute(last_indexed_query)
        last_indexed_at = last_indexed_result.scalar_one_or_none()

        return {
            "total_dreams": total_dreams,
            "indexed_dreams": indexed_dreams,
            "pending_dreams": total_dreams - indexed_dreams,
            "last_indexed_at": last_indexed_at,
        }

    async def get_unindexed_dreams(self, user_id: int) -> list[Dream]:
        query = select(Dream).where(
            and_(Dream.user_id == user_id, Dream.is_indexed == False)
        ).order_by(Dream.dream_date.asc())

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_all_dreams_for_indexing(self, user_id: int) -> list[Dream]:
        query = select(Dream).where(
            Dream.user_id == user_id
        ).order_by(Dream.dream_date.asc())

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_dream_for_indexing(self, dream_id: int, user_id: int) -> Optional[Dream]:
        query = select(Dream).where(
            and_(Dream.id == dream_id, Dream.user_id == user_id)
        )
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def mark_dream_indexed(self, dream_id: int) -> None:
        stmt = (
            update(Dream)
            .where(Dream.id == dream_id)
            .values(is_indexed=True, updated_at=datetime.utcnow())
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def mark_dreams_indexed(self, dream_ids: list[int]) -> None:
        if not dream_ids:
            return

        stmt = (
            update(Dream)
            .where(Dream.id.in_(dream_ids))
            .values(is_indexed=True, updated_at=datetime.utcnow())
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def reset_all_indexed_flags(self, user_id: int) -> int:
        count_query = select(func.count(Dream.id)).where(
            and_(Dream.user_id == user_id, Dream.is_indexed == True)
        )
        count_result = await self.db.execute(count_query)
        count = count_result.scalar() or 0

        stmt = (
            update(Dream)
            .where(Dream.user_id == user_id)
            .values(is_indexed=False)
        )
        await self.db.execute(stmt)
        await self.db.flush()

        return count

    async def get_user_graph_path(self, user_id: int) -> Optional[str]:
        query = select(User.graph_path).where(User.id == user_id)
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def update_user_graph_path(self, user_id: int, graph_path: str) -> None:
        stmt = update(User).where(User.id == user_id).values(graph_path=graph_path)
        await self.db.execute(stmt)
        await self.db.flush()

    async def update_user_indexed_count(self, user_id: int, count: int) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(dreams_indexed_count=count)
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def increment_user_indexed_count(self, user_id: int, increment: int = 1) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(dreams_indexed_count=User.dreams_indexed_count + increment)
        )
        await self.db.execute(stmt)
        await self.db.flush()
