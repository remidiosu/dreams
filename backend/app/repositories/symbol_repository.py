from typing import Optional
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.symbols import Symbol
from app.models.symbol_associations import SymbolAssociation
from app.models.dream_symbols import DreamSymbol
from app.models.dreams import Dream
from app.models.enums.dream_enums import SymbolCategory, AssociationSource


class SymbolRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_symbol(
            self,
            user_id: int,
            name: str,
            category: Optional[str] = None,
    ) -> tuple[Symbol, bool]:
        name_normalized = name.lower().strip()

        query = select(Symbol).where(
            and_(Symbol.user_id == user_id, Symbol.name_normalized == name_normalized)
        )
        result = await self.db.execute(query)
        symbol = result.scalar_one_or_none()

        if symbol:
            return symbol, False

        symbol = Symbol(
            user_id=user_id,
            name=name.strip(),
            name_normalized=name_normalized,
            category=SymbolCategory(category) if category else None,
            occurrence_count=0,
            first_appeared=None,
            last_appeared=None,
        )
        self.db.add(symbol)
        await self.db.flush()
        await self.db.refresh(symbol)

        return symbol, True

    async def get_symbol_by_id(self, symbol_id: int, user_id: int) -> Optional[Symbol]:
        query = select(Symbol).where(
            and_(Symbol.id == symbol_id, Symbol.user_id == user_id)
        )
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def list_symbols(
            self,
            user_id: int,
            per_page: int = 50,
            cursor: Optional[int] = None,
    ) -> tuple[list[Symbol], bool]:
        query = select(Symbol).where(Symbol.user_id == user_id)

        if cursor:
            query = query.where(Symbol.id < cursor)

        query = query.order_by(Symbol.occurrence_count.desc(), Symbol.id.desc()).limit(per_page + 1)

        result = await self.db.execute(query)
        symbols = list(result.scalars().all())

        has_more = len(symbols) > per_page
        if has_more:
            symbols = symbols[:per_page]

        return symbols, has_more

    async def update_symbol(
            self,
            symbol_id: int,
            user_id: int,
            name: Optional[str] = None,
            category: Optional[str] = None,
    ) -> Optional[Symbol]:
        symbol = await self.get_symbol_by_id(symbol_id, user_id)
        if not symbol:
            return None

        if name:
            symbol.name = name.strip()
            symbol.name_normalized = name.lower().strip()
        if category:
            symbol.category = SymbolCategory(category)

        await self.db.flush()
        await self.db.refresh(symbol)

        return symbol

    async def delete_symbol(self, symbol_id: int, user_id: int) -> bool:
        symbol = await self.get_symbol_by_id(symbol_id, user_id)
        if not symbol:
            return False

        await self.db.delete(symbol)
        await self.db.flush()

        return True

    async def add_symbol_to_dream(
            self,
            dream_id: int,
            symbol_id: int,
            dream_date: date,
            context_note: Optional[str] = None,
            is_ai_extracted: bool = False,
            personal_meaning: Optional[str] = None,
    ) -> DreamSymbol:
        dream_symbol = DreamSymbol(
            dream_id=dream_id,
            symbol_id=symbol_id,
            is_ai_extracted=is_ai_extracted,
            is_confirmed=not is_ai_extracted,
            context_note=context_note,
            personal_meaning=personal_meaning,
        )
        self.db.add(dream_symbol)

        symbol = await self.db.get(Symbol, symbol_id)
        if symbol:
            symbol.occurrence_count += 1
            if symbol.first_appeared is None or dream_date < symbol.first_appeared:
                symbol.first_appeared = dream_date
            if symbol.last_appeared is None or dream_date > symbol.last_appeared:
                symbol.last_appeared = dream_date

        await self.db.flush()
        await self.db.refresh(dream_symbol)

        return dream_symbol

    async def get_dream_symbol(
            self,
            dream_symbol_id: int,
            dream_id: int,
    ) -> Optional[DreamSymbol]:
        query = select(DreamSymbol).where(
            and_(DreamSymbol.id == dream_symbol_id, DreamSymbol.dream_id == dream_id)
        )
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_dream_symbols(self, dream_id: int) -> list[dict]:
        query = (
            select(DreamSymbol, Symbol)
            .join(Symbol, DreamSymbol.symbol_id == Symbol.id)
            .where(DreamSymbol.dream_id == dream_id)
        )
        result = await self.db.execute(query)
        rows = result.all()

        symbols = []
        for dream_symbol, symbol in rows:
            associations = await self.get_symbol_associations(symbol.id)
            symbols.append({
                "dream_symbol": dream_symbol,
                "symbol": symbol,
                "associations": associations,
            })

        return symbols

    async def update_dream_symbol(
            self,
            dream_symbol_id: int,
            dream_id: int,
            context_note: Optional[str] = None,
            is_confirmed: Optional[bool] = None,
    ) -> Optional[DreamSymbol]:
        dream_symbol = await self.get_dream_symbol(dream_symbol_id, dream_id)
        if not dream_symbol:
            return None

        if context_note is not None:
            dream_symbol.context_note = context_note
        if is_confirmed is not None:
            dream_symbol.is_confirmed = is_confirmed

        await self.db.flush()
        await self.db.refresh(dream_symbol)

        return dream_symbol

    async def remove_symbol_from_dream(
            self,
            dream_symbol_id: int,
            dream_id: int,
    ) -> bool:
        dream_symbol = await self.get_dream_symbol(dream_symbol_id, dream_id)
        if not dream_symbol:
            return False

        symbol = await self.db.get(Symbol, dream_symbol.symbol_id)
        if symbol and symbol.occurrence_count > 0:
            symbol.occurrence_count -= 1

        await self.db.delete(dream_symbol)
        await self.db.flush()

        return True

    async def add_association(
            self,
            symbol_id: int,
            association_text: str,
            source: str = "user",
    ) -> SymbolAssociation:
        association = SymbolAssociation(
            symbol_id=symbol_id,
            association_text=association_text,
            source=AssociationSource(source),
            is_confirmed=source == "user",
        )
        self.db.add(association)
        await self.db.flush()
        await self.db.refresh(association)

        return association

    async def get_symbol_associations(self, symbol_id: int) -> list[SymbolAssociation]:
        query = select(SymbolAssociation).where(
            SymbolAssociation.symbol_id == symbol_id
        ).order_by(SymbolAssociation.created_at)
        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def delete_association(
            self,
            association_id: int,
            symbol_id: int,
    ) -> bool:
        query = select(SymbolAssociation).where(
            and_(
                SymbolAssociation.id == association_id,
                SymbolAssociation.symbol_id == symbol_id
            )
        )
        result = await self.db.execute(query)
        association = result.scalar_one_or_none()

        if not association:
            return False

        await self.db.delete(association)
        await self.db.flush()

        return True

    async def get_symbol_with_dreams(self, symbol_id: int, user_id: int) -> Optional[dict]:
        symbol = await self.get_symbol_by_id(symbol_id, user_id)
        if not symbol:
            return None

        associations = await self.get_symbol_associations(symbol_id)
        query = (
            select(DreamSymbol, Dream)
            .join(Dream, DreamSymbol.dream_id == Dream.id)
            .where(DreamSymbol.symbol_id == symbol_id)
            .order_by(Dream.dream_date.desc())
        )
        result = await self.db.execute(query)
        rows = result.all()

        dreams = [
            {
                "dream_id": dream.id,
                "dream_title": dream.title,
                "dream_date": dream.dream_date,
                "context_note": dream_symbol.context_note,
                "is_confirmed": dream_symbol.is_confirmed,
            }
            for dream_symbol, dream in rows
        ]

        return {
            "symbol": symbol,
            "associations": associations,
            "dreams": dreams,
        }

    async def symbol_exists_in_dream(self, dream_id: int, symbol_id: int) -> bool:
        query = select(DreamSymbol.id).where(
            and_(DreamSymbol.dream_id == dream_id, DreamSymbol.symbol_id == symbol_id)
        )
        result = await self.db.execute(query)

        return result.scalar_one_or_none() is not None
