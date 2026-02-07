from typing import Optional
from collections import Counter

from sqlalchemy import select, func, and_, or_, desc, asc, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dreams import Dream
from app.models.symbols import Symbol
from app.models.characters import Character
from app.models.dream_symbols import DreamSymbol
from app.models.dream_characters import DreamCharacter
from app.models.dream_emotions import DreamEmotion
from app.models.dream_themes import DreamTheme


class AgentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_symbols(
            self,
            user_id: int,
            query: str,
            category: Optional[str] = None,
            limit: int = 10,
    ) -> list[dict]:
        conditions = [Symbol.user_id == user_id]
        conditions.append(Symbol.name.ilike(f"%{query}%"))

        if category:
            conditions.append(Symbol.category == category)

        stmt = (
            select(
                Symbol.id,
                Symbol.name,
                Symbol.category,
                Symbol.universal_meaning,
                Symbol.occurrence_count,
                Symbol.first_appeared,
                Symbol.last_appeared,
            )
            .where(and_(*conditions))
            .order_by(desc(Symbol.occurrence_count))
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.fetchall()

        return [
            {
                "id": row[0],
                "name": row[1],
                "category": row[2].value if row[2] else "other",
                "universal_meaning": row[3],
                "occurrence_count": row[4] or 0,
                "first_appeared": row[5].isoformat() if row[5] else None,
                "last_appeared": row[6].isoformat() if row[6] else None,
            }
            for row in rows
        ]

    async def get_symbol_details(
            self,
            user_id: int,
            symbol_name: str,
    ) -> Optional[dict]:
        symbol_stmt = select(Symbol).where(
            and_(
                Symbol.user_id == user_id,
                Symbol.name.ilike(symbol_name)
            )
        )
        symbol_result = await self.db.execute(symbol_stmt)
        symbol = symbol_result.scalar_one_or_none()

        if not symbol:
            return None

        appearances_stmt = (
            select(
                Dream.id,
                Dream.title,
                Dream.dream_date,
                DreamSymbol.context_note,
                DreamSymbol.personal_meaning,
            )
            .join(DreamSymbol, Dream.id == DreamSymbol.dream_id)
            .where(
                and_(
                    DreamSymbol.symbol_id == symbol.id,
                    Dream.user_id == user_id,
                )
            )
            .order_by(desc(Dream.dream_date))
        )
        appearances_result = await self.db.execute(appearances_stmt)
        appearances = appearances_result.fetchall()

        personal_meanings = [
            app[4] for app in appearances if app[4]
        ]

        return {
            "id": symbol.id,
            "name": symbol.name,
            "category": symbol.category.value if symbol.category else "other",
            "universal_meaning": symbol.universal_meaning,
            "occurrence_count": symbol.occurrence_count or len(appearances),
            "first_appeared": symbol.first_appeared.isoformat() if symbol.first_appeared else None,
            "last_appeared": symbol.last_appeared.isoformat() if symbol.last_appeared else None,
            "personal_meanings": personal_meanings,
            "appearances": [
                {
                    "dream_id": app[0],
                    "dream_title": app[1],
                    "dream_date": app[2].isoformat() if app[2] else None,
                    "context": app[3],
                    "personal_meaning": app[4],
                }
                for app in appearances[:10]
            ],
        }

    async def get_symbol_dreams(
            self,
            user_id: int,
            symbol_name: str,
            limit: int = 5,
    ) -> list[dict]:
        stmt = (
            select(
                Dream.id,
                Dream.title,
                Dream.dream_date,
                Dream.narrative,
                DreamSymbol.context_note,
                DreamSymbol.personal_meaning,
            )
            .join(DreamSymbol, Dream.id == DreamSymbol.dream_id)
            .join(Symbol, DreamSymbol.symbol_id == Symbol.id)
            .where(
                and_(
                    Dream.user_id == user_id,
                    Symbol.name.ilike(symbol_name),
                )
            )
            .order_by(desc(Dream.dream_date))
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.fetchall()

        return [
            {
                "dream_id": row[0],
                "title": row[1],
                "date": row[2].isoformat() if row[2] else None,
                "narrative_excerpt": row[3][:300] + "..." if row[3] and len(row[3]) > 300 else row[3],
                "symbol_context": row[4],
                "personal_meaning": row[5],
            }
            for row in rows
        ]

    async def get_symbol_patterns(
            self,
            user_id: int,
            symbol_name: str,
    ) -> dict:
        symbol_stmt = select(Symbol).where(
            and_(Symbol.user_id == user_id, Symbol.name.ilike(symbol_name))
        )
        symbol_result = await self.db.execute(symbol_stmt)
        symbol = symbol_result.scalar_one_or_none()

        if not symbol:
            return {"error": "Symbol not found"}

        dream_ids_stmt = (
            select(DreamSymbol.dream_id)
            .where(DreamSymbol.symbol_id == symbol.id)
        )
        dream_ids_result = await self.db.execute(dream_ids_stmt)
        dream_ids = [row[0] for row in dream_ids_result.fetchall()]

        if not dream_ids:
            return {
                "symbol_name": symbol_name,
                "co_occurring_symbols": [],
                "associated_emotions": [],
                "common_themes": [],
            }

        co_symbols_stmt = (
            select(Symbol.name, func.count(DreamSymbol.id).label("count"))
            .join(DreamSymbol, Symbol.id == DreamSymbol.symbol_id)
            .where(
                and_(
                    DreamSymbol.dream_id.in_(dream_ids),
                    Symbol.id != symbol.id,
                    Symbol.user_id == user_id,
                )
            )
            .group_by(Symbol.name)
            .order_by(desc("count"))
            .limit(10)
        )
        co_symbols_result = await self.db.execute(co_symbols_stmt)
        co_symbols = [{"name": row[0], "count": row[1]} for row in co_symbols_result.fetchall()]

        emotions_stmt = (
            select(DreamEmotion.emotion, func.avg(DreamEmotion.intensity).label("avg_intensity"),
                   func.count(DreamEmotion.id).label("count"))
            .where(DreamEmotion.dream_id.in_(dream_ids))
            .group_by(DreamEmotion.emotion)
            .order_by(desc("count"))
            .limit(10)
        )
        emotions_result = await self.db.execute(emotions_stmt)
        emotions = [
            {"emotion": row[0], "avg_intensity": round(float(row[1]), 1) if row[1] else None, "count": row[2]}
            for row in emotions_result.fetchall()
        ]

        themes_stmt = (
            select(DreamTheme.theme, func.count(DreamTheme.id).label("count"))
            .where(DreamTheme.dream_id.in_(dream_ids))
            .group_by(DreamTheme.theme)
            .order_by(desc("count"))
            .limit(10)
        )
        themes_result = await self.db.execute(themes_stmt)
        themes = [{"theme": row[0], "count": row[1]} for row in themes_result.fetchall()]

        return {
            "symbol_name": symbol_name,
            "total_appearances": len(dream_ids),
            "co_occurring_symbols": co_symbols,
            "associated_emotions": emotions,
            "common_themes": themes,
        }

    async def search_characters(
            self,
            user_id: int,
            query: str,
            character_type: Optional[str] = None,
            limit: int = 10,
    ) -> list[dict]:
        conditions = [Character.user_id == user_id]
        conditions.append(Character.name.ilike(f"%{query}%"))

        if character_type:
            conditions.append(Character.character_type == character_type)

        stmt = (
            select(
                Character.id,
                Character.name,
                Character.character_type,
                Character.real_world_relation,
                Character.occurrence_count,
            )
            .where(and_(*conditions))
            .order_by(desc(Character.occurrence_count))
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.fetchall()

        return [
            {
                "id": row[0],
                "name": row[1],
                "type": row[2].value if row[2] else "unknown",
                "real_world_relation": row[3],
                "occurrence_count": row[4] or 0,
            }
            for row in rows
        ]

    async def get_character_details(
            self,
            user_id: int,
            character_name: str,
    ) -> Optional[dict]:
        char_stmt = select(Character).where(
            and_(
                Character.user_id == user_id,
                Character.name.ilike(character_name)
            )
        )
        char_result = await self.db.execute(char_stmt)
        character = char_result.scalar_one_or_none()

        if not character:
            return None

        appearances_stmt = (
            select(
                Dream.id,
                Dream.title,
                Dream.dream_date,
                DreamCharacter.role_in_dream,
                DreamCharacter.archetype,
                DreamCharacter.traits,
                DreamCharacter.context_note,
                DreamCharacter.personal_significance,
            )
            .join(DreamCharacter, Dream.id == DreamCharacter.dream_id)
            .where(
                and_(
                    DreamCharacter.character_id == character.id,
                    Dream.user_id == user_id,
                )
            )
            .order_by(desc(Dream.dream_date))
        )
        appearances_result = await self.db.execute(appearances_stmt)
        appearances = appearances_result.fetchall()
        archetypes = [app[4] for app in appearances if app[4]]
        archetype_counts = Counter(archetypes)
        personal_significances = [app[7] for app in appearances if app[7]]

        return {
            "id": character.id,
            "name": character.name,
            "type": character.character_type.value if character.character_type else "unknown",
            "real_world_relation": character.real_world_relation,
            "occurrence_count": character.occurrence_count or len(appearances),
            "archetypes_assigned": dict(archetype_counts),
            "personal_significances": personal_significances,
            "appearances": [
                {
                    "dream_id": app[0],
                    "dream_title": app[1],
                    "dream_date": app[2].isoformat() if app[2] else None,
                    "role": app[3].value if app[3] else None,
                    "archetype": app[4],
                    "traits": app[5] or [],
                    "context": app[6],
                    "personal_significance": app[7],
                }
                for app in appearances[:10]
            ],
        }

    async def get_archetype_analysis(
            self,
            user_id: int,
            archetype: str,
    ) -> dict:
        stmt = (
            select(
                Character.id,
                Character.name,
                Character.character_type,
                Dream.id,
                Dream.title,
                Dream.dream_date,
                DreamCharacter.role_in_dream,
                DreamCharacter.context_note,
                DreamCharacter.personal_significance,
            )
            .join(DreamCharacter, Character.id == DreamCharacter.character_id)
            .join(Dream, DreamCharacter.dream_id == Dream.id)
            .where(
                and_(
                    Dream.user_id == user_id,
                    DreamCharacter.archetype.ilike(archetype),
                )
            )
            .order_by(desc(Dream.dream_date))
        )

        result = await self.db.execute(stmt)
        rows = result.fetchall()
        characters = {}
        for row in rows:
            char_id = row[0]
            if char_id not in characters:
                characters[char_id] = {
                    "id": char_id,
                    "name": row[1],
                    "type": row[2].value if row[2] else "unknown",
                    "dream_appearances": [],
                }
            characters[char_id]["dream_appearances"].append({
                "dream_id": row[3],
                "dream_title": row[4],
                "dream_date": row[5].isoformat() if row[5] else None,
                "role": row[6].value if row[6] else None,
                "context": row[7],
                "personal_significance": row[8],
            })

        return {
            "archetype": archetype,
            "total_appearances": len(rows),
            "characters": list(characters.values()),
        }

    async def get_emotion_overview(self, user_id: int) -> dict:
        common_stmt = (
            select(
                DreamEmotion.emotion,
                func.count(DreamEmotion.id).label("count"),
                func.avg(DreamEmotion.intensity).label("avg_intensity"),
            )
            .join(Dream, DreamEmotion.dream_id == Dream.id)
            .where(Dream.user_id == user_id)
            .group_by(DreamEmotion.emotion)
            .order_by(desc("count"))
            .limit(15)
        )

        result = await self.db.execute(common_stmt)
        rows = result.fetchall()

        return {
            "emotions": [
                {
                    "emotion": row[0],
                    "count": row[1],
                    "avg_intensity": round(float(row[2]), 1) if row[2] else None,
                }
                for row in rows
            ],
            "total_emotion_entries": sum(row[1] for row in rows),
        }

    async def get_emotion_dreams(
            self,
            user_id: int,
            emotion: str,
            limit: int = 5,
    ) -> list[dict]:
        stmt = (
            select(
                Dream.id,
                Dream.title,
                Dream.dream_date,
                Dream.narrative,
                DreamEmotion.intensity,
                DreamEmotion.emotion_type,
            )
            .join(DreamEmotion, Dream.id == DreamEmotion.dream_id)
            .where(
                and_(
                    Dream.user_id == user_id,
                    DreamEmotion.emotion.ilike(emotion),
                )
            )
            .order_by(desc(DreamEmotion.intensity), desc(Dream.dream_date))
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.fetchall()

        return [
            {
                "dream_id": row[0],
                "title": row[1],
                "date": row[2].isoformat() if row[2] else None,
                "narrative_excerpt": row[3][:300] + "..." if row[3] and len(row[3]) > 300 else row[3],
                "intensity": row[4],
                "emotion_type": row[5],
            }
            for row in rows
        ]

    async def get_emotion_correlations(
            self,
            user_id: int,
            emotion: str,
    ) -> dict:
        dream_ids_stmt = (
            select(DreamEmotion.dream_id)
            .join(Dream, DreamEmotion.dream_id == Dream.id)
            .where(
                and_(
                    Dream.user_id == user_id,
                    DreamEmotion.emotion.ilike(emotion),
                )
            )
        )
        dream_ids_result = await self.db.execute(dream_ids_stmt)
        dream_ids = [row[0] for row in dream_ids_result.fetchall()]

        if not dream_ids:
            return {
                "emotion": emotion,
                "correlated_symbols": [],
                "correlated_characters": [],
                "correlated_themes": [],
            }

        symbols_stmt = (
            select(Symbol.name, func.count(DreamSymbol.id).label("count"))
            .join(DreamSymbol, Symbol.id == DreamSymbol.symbol_id)
            .where(DreamSymbol.dream_id.in_(dream_ids))
            .group_by(Symbol.name)
            .order_by(desc("count"))
            .limit(10)
        )
        symbols_result = await self.db.execute(symbols_stmt)
        symbols = [{"name": row[0], "count": row[1]} for row in symbols_result.fetchall()]

        chars_stmt = (
            select(Character.name, DreamCharacter.archetype, func.count(DreamCharacter.id).label("count"))
            .join(DreamCharacter, Character.id == DreamCharacter.character_id)
            .where(DreamCharacter.dream_id.in_(dream_ids))
            .group_by(Character.name, DreamCharacter.archetype)
            .order_by(desc("count"))
            .limit(10)
        )
        chars_result = await self.db.execute(chars_stmt)
        characters = [{"name": row[0], "archetype": row[1], "count": row[2]} for row in chars_result.fetchall()]
        themes_stmt = (
            select(DreamTheme.theme, func.count(DreamTheme.id).label("count"))
            .where(DreamTheme.dream_id.in_(dream_ids))
            .group_by(DreamTheme.theme)
            .order_by(desc("count"))
            .limit(10)
        )
        themes_result = await self.db.execute(themes_stmt)
        themes = [{"theme": row[0], "count": row[1]} for row in themes_result.fetchall()]

        return {
            "emotion": emotion,
            "dream_count": len(dream_ids),
            "correlated_symbols": symbols,
            "correlated_characters": characters,
            "correlated_themes": themes,
        }

    async def get_themes_overview(self, user_id: int) -> dict:
        stmt = (
            select(DreamTheme.theme, func.count(DreamTheme.id).label("count"))
            .join(Dream, DreamTheme.dream_id == Dream.id)
            .where(Dream.user_id == user_id)
            .group_by(DreamTheme.theme)
            .order_by(desc("count"))
        )

        result = await self.db.execute(stmt)
        rows = result.fetchall()

        return {
            "themes": [{"theme": row[0], "count": row[1]} for row in rows],
            "total_unique_themes": len(rows),
        }

    async def get_theme_dreams(
            self,
            user_id: int,
            theme: str,
            limit: int = 5,
    ) -> list[dict]:
        stmt = (
            select(
                Dream.id,
                Dream.title,
                Dream.dream_date,
                Dream.narrative,
                Dream.personal_interpretation,
            )
            .join(DreamTheme, Dream.id == DreamTheme.dream_id)
            .where(
                and_(
                    Dream.user_id == user_id,
                    DreamTheme.theme.ilike(theme),
                )
            )
            .order_by(desc(Dream.dream_date))
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.fetchall()

        return [
            {
                "dream_id": row[0],
                "title": row[1],
                "date": row[2].isoformat() if row[2] else None,
                "narrative_excerpt": row[3][:300] + "..." if row[3] and len(row[3]) > 300 else row[3],
                "personal_interpretation": row[4],
            }
            for row in rows
        ]

    async def get_theme_analysis(
            self,
            user_id: int,
            theme: str,
    ) -> dict:
        dream_ids_stmt = (
            select(DreamTheme.dream_id)
            .join(Dream, DreamTheme.dream_id == Dream.id)
            .where(
                and_(
                    Dream.user_id == user_id,
                    DreamTheme.theme.ilike(theme),
                )
            )
        )
        dream_ids_result = await self.db.execute(dream_ids_stmt)
        dream_ids = [row[0] for row in dream_ids_result.fetchall()]

        if not dream_ids:
            return {
                "theme": theme,
                "related_symbols": [],
                "related_characters": [],
                "related_emotions": [],
            }

        symbols_stmt = (
            select(Symbol.name, func.count(DreamSymbol.id).label("count"))
            .join(DreamSymbol, Symbol.id == DreamSymbol.symbol_id)
            .where(DreamSymbol.dream_id.in_(dream_ids))
            .group_by(Symbol.name)
            .order_by(desc("count"))
            .limit(10)
        )
        symbols_result = await self.db.execute(symbols_stmt)
        symbols = [{"name": row[0], "count": row[1]} for row in symbols_result.fetchall()]

        chars_stmt = (
            select(Character.name, DreamCharacter.archetype, func.count(DreamCharacter.id).label("count"))
            .join(DreamCharacter, Character.id == DreamCharacter.character_id)
            .where(DreamCharacter.dream_id.in_(dream_ids))
            .group_by(Character.name, DreamCharacter.archetype)
            .order_by(desc("count"))
            .limit(10)
        )
        chars_result = await self.db.execute(chars_stmt)
        characters = [{"name": row[0], "archetype": row[1], "count": row[2]} for row in chars_result.fetchall()]

        emotions_stmt = (
            select(DreamEmotion.emotion, func.avg(DreamEmotion.intensity).label("avg_intensity"),
                   func.count(DreamEmotion.id).label("count"))
            .where(DreamEmotion.dream_id.in_(dream_ids))
            .group_by(DreamEmotion.emotion)
            .order_by(desc("count"))
            .limit(10)
        )
        emotions_result = await self.db.execute(emotions_stmt)
        emotions = [
            {"emotion": row[0], "avg_intensity": round(float(row[1]), 1) if row[1] else None, "count": row[2]}
            for row in emotions_result.fetchall()
        ]

        return {
            "theme": theme,
            "dream_count": len(dream_ids),
            "related_symbols": symbols,
            "related_characters": characters,
            "related_emotions": emotions,
        }

    async def search_dreams(
            self,
            user_id: int,
            query: str,
            limit: int = 5,
    ) -> list[dict]:
        stmt = (
            select(
                Dream.id,
                Dream.title,
                Dream.dream_date,
                Dream.narrative,
                Dream.is_recurring,
                Dream.is_nightmare,
            )
            .where(
                and_(
                    Dream.user_id == user_id,
                    or_(
                        Dream.narrative.ilike(f"%{query}%"),
                        Dream.title.ilike(f"%{query}%"),
                        Dream.personal_interpretation.ilike(f"%{query}%"),
                    ),
                )
            )
            .order_by(desc(Dream.dream_date))
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.fetchall()

        return [
            {
                "dream_id": row[0],
                "title": row[1],
                "date": row[2].isoformat() if row[2] else None,
                "narrative_excerpt": row[3][:300] + "..." if row[3] and len(row[3]) > 300 else row[3],
                "is_recurring": row[4],
                "is_nightmare": row[5],
            }
            for row in rows
        ]

    async def get_recent_dreams(
            self,
            user_id: int,
            limit: int = 5,
    ) -> list[dict]:
        stmt = (
            select(
                Dream.id,
                Dream.title,
                Dream.dream_date,
                Dream.narrative,
                Dream.emotional_intensity,
                Dream.is_recurring,
                Dream.is_nightmare,
            )
            .where(Dream.user_id == user_id)
            .order_by(desc(Dream.dream_date))
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        rows = result.fetchall()

        return [
            {
                "dream_id": row[0],
                "title": row[1],
                "date": row[2].isoformat() if row[2] else None,
                "narrative_excerpt": row[3][:200] + "..." if row[3] and len(row[3]) > 200 else row[3],
                "emotional_intensity": row[4],
                "is_recurring": row[5],
                "is_nightmare": row[6],
            }
            for row in rows
        ]

    async def get_dream_details(
            self,
            user_id: int,
            dream_id: int,
    ) -> Optional[dict]:
        dream_stmt = select(Dream).where(
            and_(Dream.id == dream_id, Dream.user_id == user_id)
        )
        dream_result = await self.db.execute(dream_stmt)
        dream = dream_result.scalar_one_or_none()

        if not dream:
            return None

        symbols_stmt = (
            select(Symbol.name, DreamSymbol.personal_meaning, DreamSymbol.context_note)
            .join(DreamSymbol, Symbol.id == DreamSymbol.symbol_id)
            .where(DreamSymbol.dream_id == dream_id)
        )
        symbols_result = await self.db.execute(symbols_stmt)
        symbols = [
            {"name": row[0], "personal_meaning": row[1], "context": row[2]}
            for row in symbols_result.fetchall()
        ]

        chars_stmt = (
            select(Character.name, DreamCharacter.archetype, DreamCharacter.personal_significance)
            .join(DreamCharacter, Character.id == DreamCharacter.character_id)
            .where(DreamCharacter.dream_id == dream_id)
        )
        chars_result = await self.db.execute(chars_stmt)
        characters = [
            {"name": row[0], "archetype": row[1], "personal_significance": row[2]}
            for row in chars_result.fetchall()
        ]

        emotions_stmt = select(DreamEmotion).where(DreamEmotion.dream_id == dream_id)
        emotions_result = await self.db.execute(emotions_stmt)
        emotions = [
            {"emotion": e.emotion, "intensity": e.intensity, "type": e.emotion_type}
            for e in emotions_result.scalars().all()
        ]

        themes_stmt = select(DreamTheme.theme).where(DreamTheme.dream_id == dream_id)
        themes_result = await self.db.execute(themes_stmt)
        themes = [row[0] for row in themes_result.fetchall()]

        return {
            "id": dream.id,
            "title": dream.title,
            "date": dream.dream_date.isoformat() if dream.dream_date else None,
            "narrative": dream.narrative,
            "setting": dream.setting,
            "lucidity_level": dream.lucidity_level.value if dream.lucidity_level else None,
            "emotional_intensity": dream.emotional_intensity,
            "is_recurring": dream.is_recurring,
            "is_nightmare": dream.is_nightmare,
            "personal_interpretation": dream.personal_interpretation,
            "symbols": symbols,
            "characters": characters,
            "emotions": emotions,
            "themes": themes,
        }

    async def get_recurring_dreams(
            self,
            user_id: int,
    ) -> list[dict]:
        stmt = (
            select(
                Dream.id,
                Dream.title,
                Dream.dream_date,
                Dream.narrative,
                Dream.personal_interpretation,
            )
            .where(
                and_(
                    Dream.user_id == user_id,
                    Dream.is_recurring == True,
                )
            )
            .order_by(desc(Dream.dream_date))
        )

        result = await self.db.execute(stmt)
        rows = result.fetchall()

        return [
            {
                "dream_id": row[0],
                "title": row[1],
                "date": row[2].isoformat() if row[2] else None,
                "narrative_excerpt": row[3][:300] + "..." if row[3] and len(row[3]) > 300 else row[3],
                "personal_interpretation": row[4],
            }
            for row in rows
        ]

    async def get_journal_summary(self, user_id: int) -> dict:
        total_stmt = select(func.count(Dream.id)).where(Dream.user_id == user_id)
        total_result = await self.db.execute(total_stmt)
        total_dreams = total_result.scalar() or 0
        date_stmt = (
            select(func.min(Dream.dream_date), func.max(Dream.dream_date))
            .where(Dream.user_id == user_id)
        )
        date_result = await self.db.execute(date_stmt)
        date_row = date_result.fetchone()
        symbol_stmt = select(func.count(Symbol.id)).where(Symbol.user_id == user_id)
        symbol_result = await self.db.execute(symbol_stmt)
        total_symbols = symbol_result.scalar() or 0
        char_stmt = select(func.count(Character.id)).where(Character.user_id == user_id)
        char_result = await self.db.execute(char_stmt)
        total_characters = char_result.scalar() or 0

        return {
            "total_dreams": total_dreams,
            "first_dream_date": date_row[0].isoformat() if date_row and date_row[0] else None,
            "last_dream_date": date_row[1].isoformat() if date_row and date_row[1] else None,
            "total_symbols": total_symbols,
            "total_characters": total_characters,
        }
