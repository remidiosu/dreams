from typing import Optional
from datetime import date

from sqlalchemy import select, func, delete, and_, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dreams import Dream
from app.models.dream_emotions import DreamEmotion
from app.models.dream_symbols import DreamSymbol
from app.models.dream_characters import DreamCharacter
from app.models.dream_themes import DreamTheme
from app.models.symbols import Symbol
from app.models.symbol_associations import SymbolAssociation
from app.models.characters import Character
from app.models.character_associations import CharacterAssociation
from app.models.enums.dream_enums import EmotionType


class DreamRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_dream(
            self,
            user_id: int,
            narrative: str,
            dream_date: date,
            title: Optional[str] = None,
            setting: Optional[str] = None,
            development: Optional[str] = None,
            ending: Optional[str] = None,
            emotion_on_waking: Optional[str] = None,
            emotional_intensity: Optional[int] = None,
            lucidity_level: Optional[str] = None,
            sleep_quality: Optional[int] = None,
            is_recurring: bool = False,
            is_nightmare: bool = False,
            ritual_completed: bool = False,
            ritual_description: Optional[str] = None,
            personal_interpretation: Optional[str] = None,
            conscious_context: Optional[str] = None,
    ) -> Dream:
        dream = Dream(
            user_id=user_id,
            title=title or self._generate_title(narrative),
            narrative=narrative,
            dream_date=dream_date,
            setting=setting,
            development=development,
            ending=ending,
            emotion_on_waking=emotion_on_waking,
            emotional_intensity=emotional_intensity,
            lucidity_level=lucidity_level,
            sleep_quality=sleep_quality,
            is_recurring=is_recurring,
            is_nightmare=is_nightmare,
            ritual_completed=ritual_completed,
            ritual_description=ritual_description,
            personal_interpretation=personal_interpretation,
            conscious_context=conscious_context,
        )
        self.db.add(dream)
        await self.db.flush()
        await self.db.refresh(dream)

        return dream

    async def add_dream_emotions(
            self,
            dream_id: int,
            emotions: list[dict]
    ) -> list[DreamEmotion]:
        dream_emotions = []
        for e in emotions:
            emotion_type = EmotionType(e.get("emotion_type", "during"))
            dream_emotion = DreamEmotion(
                dream_id=dream_id,
                emotion=e["emotion"],
                emotion_type=emotion_type,
                intensity=e.get("intensity"),
            )
            self.db.add(dream_emotion)
            dream_emotions.append(dream_emotion)
        await self.db.flush()

        return dream_emotions

    async def get_by_id(self, dream_id: int, user_id: int) -> Optional[Dream]:
        query = select(Dream).where(
            and_(Dream.id == dream_id, Dream.user_id == user_id)
        )
        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_dream_with_associations(self, dream_id: int, user_id: int) -> Optional[dict]:
        dream = await self.get_by_id(dream_id, user_id)
        if not dream:
            return None

        emotions = await self._get_dream_emotions(dream_id)
        symbols = await self._get_dream_symbols_with_associations(dream_id)
        characters = await self._get_dream_characters_with_associations(dream_id)
        themes = await self._get_dream_themes(dream_id)

        return {
            "dream": dream,
            "emotions": emotions,
            "symbols": symbols,
            "characters": characters,
            "themes": themes,
        }

    async def list_dreams(
            self,
            user_id: int,
            per_page: int = 25,
            cursor: Optional[int] = None,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None,
            emotion: Optional[str] = None,
            has_ritual: Optional[bool] = None,
            lucidity_level: Optional[str] = None,
            is_indexed: Optional[bool] = None,
    ) -> tuple[list[dict], bool]:
        query = select(Dream).where(Dream.user_id == user_id)
        if date_from:
            query = query.where(Dream.dream_date >= date_from)
        if date_to:
            query = query.where(Dream.dream_date <= date_to)
        if has_ritual is not None:
            query = query.where(Dream.ritual_completed == has_ritual)
        if lucidity_level:
            query = query.where(Dream.lucidity_level == lucidity_level)
        if is_indexed is not None:
            query = query.where(Dream.is_indexed == is_indexed)

        if emotion:
            query = query.join(DreamEmotion).where(DreamEmotion.emotion == emotion)
        if cursor:
            query = query.where(Dream.id < cursor)

        query = query.order_by(Dream.dream_date.desc(), Dream.id.desc()).limit(per_page + 1)
        result = await self.db.execute(query)
        dreams = list(result.scalars().all())

        has_more = len(dreams) > per_page
        if has_more:
            dreams = dreams[:per_page]

        dream_summaries = []
        for dream in dreams:
            emotions = await self._get_dream_emotion_names(dream.id)
            symbol_count = await self._count_dream_symbols(dream.id)
            character_count = await self._count_dream_characters(dream.id)

            dream_summaries.append({
                "dream": dream,
                "emotions": emotions,
                "symbol_count": symbol_count,
                "character_count": character_count,
            })

        return dream_summaries, has_more

    async def update_dream(
            self,
            dream_id: int,
            user_id: int,
            **updates
    ) -> Optional[Dream]:
        dream = await self.get_by_id(dream_id, user_id)
        if not dream:
            return None

        for field, value in updates.items():
            if value is not None and hasattr(dream, field):
                setattr(dream, field, value)

        await self.db.flush()
        await self.db.refresh(dream)

        return dream

    async def replace_dream_emotions(
            self,
            dream_id: int,
            emotions: list[dict]
    ) -> list[DreamEmotion]:
        await self.db.execute(
            delete(DreamEmotion).where(DreamEmotion.dream_id == dream_id)
        )

        return await self.add_dream_emotions(dream_id, emotions)

    async def mark_as_indexed(self, dream_id: int) -> None:
        dream = await self.db.get(Dream, dream_id)
        if dream:
            dream.is_indexed = True
            from datetime import datetime, timezone
            dream.indexed_at = datetime.now(timezone.utc)
            await self.db.flush()

    async def mark_extraction_done(self, dream_id: int) -> None:
        dream = await self.db.get(Dream, dream_id)
        if dream:
            dream.ai_extraction_done = True
            await self.db.flush()

    async def delete_dream(self, dream_id: int, user_id: int) -> bool:
        dream = await self.get_by_id(dream_id, user_id)
        if not dream:
            return False

        await self.db.delete(dream)
        await self.db.flush()

        return True

    def _generate_title(self, narrative: str, max_length: int = 50) -> str:
        first_line = narrative.split('\n')[0].strip()
        if len(first_line) <= max_length:
            return first_line

        return first_line[:max_length - 3] + "..."

    async def _get_dream_emotions(self, dream_id: int) -> list[DreamEmotion]:
        query = select(DreamEmotion).where(DreamEmotion.dream_id == dream_id)
        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def _get_dream_emotion_names(self, dream_id: int) -> list[str]:
        query = select(DreamEmotion.emotion).where(DreamEmotion.dream_id == dream_id)
        result = await self.db.execute(query)

        return [row[0] for row in result.all()]

    async def _get_dream_themes(self, dream_id: int) -> list[DreamTheme]:
        query = select(DreamTheme).where(DreamTheme.dream_id == dream_id)
        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def _count_dream_symbols(self, dream_id: int) -> int:
        query = select(func.count(DreamSymbol.id)).where(DreamSymbol.dream_id == dream_id)
        result = await self.db.execute(query)

        return result.scalar() or 0

    async def _count_dream_characters(self, dream_id: int) -> int:
        query = select(func.count(DreamCharacter.id)).where(DreamCharacter.dream_id == dream_id)
        result = await self.db.execute(query)

        return result.scalar() or 0

    async def _get_dream_symbols_with_associations(self, dream_id: int) -> list[dict]:
        query = (
            select(DreamSymbol, Symbol)
            .join(Symbol, DreamSymbol.symbol_id == Symbol.id)
            .where(DreamSymbol.dream_id == dream_id)
        )
        result = await self.db.execute(query)
        rows = result.all()

        symbols = []
        for dream_symbol, symbol in rows:
            assoc_query = select(SymbolAssociation.association_text).where(
                SymbolAssociation.symbol_id == symbol.id
            )
            assoc_result = await self.db.execute(assoc_query)
            associations = [row[0] for row in assoc_result.all()]

            symbols.append({
                "id": dream_symbol.id,
                "symbol_id": symbol.id,
                "name": symbol.name,
                "category": symbol.category.value if symbol.category else None,
                "associations": associations,
                "is_ai_extracted": dream_symbol.is_ai_extracted,
                "is_confirmed": dream_symbol.is_confirmed,
                "context_note": dream_symbol.context_note,
            })

        return symbols

    async def _get_dream_characters_with_associations(self, dream_id: int) -> list[dict]:
        query = (
            select(DreamCharacter, Character)
            .join(Character, DreamCharacter.character_id == Character.id)
            .where(DreamCharacter.dream_id == dream_id)
        )
        result = await self.db.execute(query)
        rows = result.all()

        characters = []
        for dream_char, character in rows:
            assoc_query = select(CharacterAssociation.association_text).where(
                CharacterAssociation.character_id == character.id
            )
            assoc_result = await self.db.execute(assoc_query)
            associations = [row[0] for row in assoc_result.all()]

            characters.append({
                "id": dream_char.id,
                "character_id": character.id,
                "name": character.name,
                "character_type": character.character_type.value if character.character_type else None,
                "real_world_relation": character.real_world_relation,
                "role_in_dream": dream_char.role_in_dream.value if dream_char.role_in_dream else None,
                "archetype": dream_char.archetype,
                "traits": dream_char.traits or [],
                "associations": associations,
                "is_ai_extracted": dream_char.is_ai_extracted,
                "is_confirmed": dream_char.is_confirmed,
                "context_note": dream_char.context_note,
            })

        return characters

    async def dream_exists(self, dream_id: int, user_id: int) -> bool:
        query = select(Dream.id).where(
            and_(Dream.id == dream_id, Dream.user_id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_dream_emotions(self, dream_id: int) -> list[DreamEmotion]:
        return await self._get_dream_emotions(dream_id)

    async def add_dream_emotion(
            self,
            dream_id: int,
            emotion: str,
            emotion_type: str = "during",
            intensity: int = None,
    ) -> DreamEmotion:
        dream_emotion = DreamEmotion(
            dream_id=dream_id,
            emotion=emotion,
            emotion_type=EmotionType(emotion_type),
            intensity=intensity,
        )
        self.db.add(dream_emotion)
        await self.db.flush()
        await self.db.refresh(dream_emotion)

        return dream_emotion

    async def add_dream_theme(
            self,
            dream_id: int,
            theme: str,
            is_ai_extracted: bool = False,
    ) -> DreamTheme:
        query = select(DreamTheme).where(
            and_(DreamTheme.dream_id == dream_id, DreamTheme.theme == theme)
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        dream_theme = DreamTheme(
            dream_id=dream_id,
            theme=theme,
            is_ai_extracted=is_ai_extracted,
            is_confirmed=not is_ai_extracted,
        )
        self.db.add(dream_theme)
        await self.db.flush()
        await self.db.refresh(dream_theme)

        return dream_theme

    async def mark_ai_extraction_done(self, dream_id: int) -> None:
        query = (
            update(Dream)
            .where(Dream.id == dream_id)
            .values(ai_extraction_done=True)
        )
        await self.db.execute(query)
        await self.db.flush()
