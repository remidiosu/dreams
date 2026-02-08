from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.dreams import Dream
from app.models.symbols import Symbol
from app.models.characters import Character
from app.models.dream_symbols import DreamSymbol
from app.models.dream_characters import DreamCharacter
from app.models.dream_emotions import DreamEmotion
from app.models.dream_themes import DreamTheme
from app.schemas.indexing_data import SymbolData, DreamData, CharacterData, EmotionData, ThemeData


class DreamIndexingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dream_with_all_data(self, dream_id: int, user_id: int) -> Optional[DreamData]:
        dream_query = select(Dream).where(
            and_(Dream.id == dream_id, Dream.user_id == user_id)
        )
        dream_result = await self.db.execute(dream_query)
        dream = dream_result.scalar_one_or_none()

        if not dream:
            return None

        symbols = await self._get_dream_symbols(dream_id)
        characters = await self._get_dream_characters(dream_id)
        emotions = await self._get_dream_emotions(dream_id)
        themes = await self._get_dream_themes(dream_id)

        return DreamData(
            id=dream.id,
            title=dream.title,
            narrative=dream.narrative,
            dream_date=dream.dream_date.isoformat() if dream.dream_date else None,
            setting=dream.setting,
            lucidity_level=dream.lucidity_level.value if dream.lucidity_level else None,
            emotional_intensity=dream.emotional_intensity,
            is_recurring=dream.is_recurring or False,
            is_nightmare=dream.is_nightmare or False,
            ritual_completed=dream.ritual_completed or False,
            ritual_description=dream.ritual_description,
            personal_interpretation=dream.personal_interpretation,
            symbols=symbols,
            characters=characters,
            emotions=emotions,
            themes=themes,
        )

    async def _get_dream_symbols(self, dream_id: int) -> list[SymbolData]:
        query = (
            select(Symbol, DreamSymbol)
            .join(DreamSymbol, Symbol.id == DreamSymbol.symbol_id)
            .where(DreamSymbol.dream_id == dream_id)
        )
        result = await self.db.execute(query)
        rows = result.fetchall()

        symbols = []
        for symbol, dream_symbol in rows:
            symbols.append(SymbolData(
                name=symbol.name,
                category=symbol.category.value if symbol.category else "other",
                context=dream_symbol.context_note,
                universal_meaning=symbol.universal_meaning,
                personal_meaning=dream_symbol.personal_meaning,
                personal_associations=[],
            ))

        return symbols

    async def _get_dream_characters(self, dream_id: int) -> list[CharacterData]:
        query = (
            select(Character, DreamCharacter)
            .join(DreamCharacter, Character.id == DreamCharacter.character_id)
            .where(DreamCharacter.dream_id == dream_id)
        )
        result = await self.db.execute(query)
        rows = result.fetchall()

        characters = []
        for character, dream_character in rows:
            characters.append(CharacterData(
                name=character.name,
                character_type=character.character_type.value if character.character_type else "unknown",
                real_world_relation=character.real_world_relation,
                role_in_dream=dream_character.role_in_dream.value if dream_character.role_in_dream else None,
                archetype=dream_character.archetype,
                traits=dream_character.traits or [],
                context=dream_character.context_note,
                personal_significance=dream_character.personal_significance,
            ))

        return characters

    async def _get_dream_emotions(self, dream_id: int) -> list[EmotionData]:
        query = select(DreamEmotion).where(DreamEmotion.dream_id == dream_id)
        result = await self.db.execute(query)
        emotions = result.scalars().all()

        return [
            EmotionData(
                emotion=e.emotion,
                intensity=e.intensity or 5,
                emotion_type=e.emotion_type or "during",
            )
            for e in emotions
        ]

    async def _get_dream_themes(self, dream_id: int) -> list[ThemeData]:
        query = select(DreamTheme).where(DreamTheme.dream_id == dream_id)
        result = await self.db.execute(query)
        themes = result.scalars().all()

        return [ThemeData(theme=t.theme) for t in themes]

    def format_dream_for_indexing(self, dream_data: DreamData) -> str:
        sections = []

        header_parts = [f"[Dream ID: {dream_data.id}]"]
        if dream_data.dream_date:
            header_parts.append(f"[Date: {dream_data.dream_date}]")
        if dream_data.title:
            header_parts.append(f"[Title: {dream_data.title}]")

        flags = []
        if dream_data.is_recurring:
            flags.append("RECURRING")
        if dream_data.is_nightmare:
            flags.append("NIGHTMARE")
        if dream_data.lucidity_level and dream_data.lucidity_level != "none":
            flags.append(f"LUCID ({dream_data.lucidity_level})")
        if flags:
            header_parts.append(f"[{', '.join(flags)}]")

        sections.append(" ".join(header_parts))
        sections.append("")

        if dream_data.setting:
            sections.append(f"SETTING: {dream_data.setting}")
            sections.append("")

        sections.append("DREAM NARRATIVE:")
        sections.append(dream_data.narrative)
        sections.append("")

        if dream_data.symbols:
            sections.append("=" * 50)
            sections.append("SYMBOLS IN THIS DREAM:")
            sections.append("")

            for symbol in dream_data.symbols:
                sections.append(f"• SYMBOL: {symbol.name}")
                sections.append(f"  Category: {symbol.category}")

                if symbol.context:
                    sections.append(f"  Context in dream: {symbol.context}")

                if symbol.universal_meaning:
                    sections.append(f"  Universal meaning: {symbol.universal_meaning}")

                if symbol.personal_meaning:
                    sections.append(f"  >>> PERSONAL MEANING: {symbol.personal_meaning}")

                if symbol.personal_associations:
                    sections.append(f"  Personal associations: {', '.join(symbol.personal_associations)}")

                sections.append("")

        if dream_data.characters:
            sections.append("=" * 50)
            sections.append("CHARACTERS IN THIS DREAM:")
            sections.append("")

            for char in dream_data.characters:
                sections.append(f"• CHARACTER: {char.name}")
                sections.append(f"  Type: {char.character_type}")

                if char.real_world_relation:
                    sections.append(f"  Real-world relation: {char.real_world_relation}")

                if char.role_in_dream:
                    sections.append(f"  Role in dream: {char.role_in_dream}")

                if char.archetype:
                    sections.append(f"  ARCHETYPE: {char.archetype}")

                if char.traits:
                    sections.append(f"  Traits: {', '.join(char.traits)}")

                if char.context:
                    sections.append(f"  What they did: {char.context}")

                if char.personal_significance:
                    sections.append(f"  >>> PERSONAL SIGNIFICANCE: {char.personal_significance}")

                sections.append("")

        if dream_data.emotions:
            sections.append("=" * 50)
            sections.append("EMOTIONS EXPERIENCED:")
            sections.append("")

            during_emotions = [e for e in dream_data.emotions if e.emotion_type == "during"]
            waking_emotions = [e for e in dream_data.emotions if e.emotion_type == "waking"]

            if during_emotions:
                sections.append("During the dream:")
                for emotion in during_emotions:
                    sections.append(f"  • {emotion.emotion} ({emotion.intensity}/10)")

            if waking_emotions:
                sections.append("Upon waking:")
                for emotion in waking_emotions:
                    sections.append(f"  • {emotion.emotion} ({emotion.intensity}/10)")

            sections.append("")

        if dream_data.themes:
            sections.append("=" * 50)
            sections.append("THEMES:")
            theme_names = [t.theme for t in dream_data.themes]
            sections.append(f"  {' | '.join(theme_names)}")
            sections.append("")

        if dream_data.ritual_completed:
            sections.append("=" * 50)
            sections.append("PRE-SLEEP RITUAL: Completed")
            if dream_data.ritual_description:
                sections.append(f"  Description: {dream_data.ritual_description}")
            sections.append("")

        if dream_data.personal_interpretation:
            sections.append("=" * 50)
            sections.append("★★★ DREAMER'S PERSONAL INTERPRETATION ★★★")
            sections.append("(This is the most important part - the dreamer's own understanding)")
            sections.append("")
            sections.append(dream_data.personal_interpretation)
            sections.append("")

        if dream_data.emotional_intensity:
            sections.append(f"[Overall emotional intensity: {dream_data.emotional_intensity}/10]")

        return "\n".join(sections)

    async def prepare_dream_for_indexing(self, dream_id: int, user_id: int) -> Optional[str]:
        dream_data = await self.get_dream_with_all_data(dream_id, user_id)
        if not dream_data:
            return None

        return self.format_dream_for_indexing(dream_data)

    async def prepare_dreams_batch(
            self,
            dream_ids: list[int],
            user_id: int
    ) -> list[dict]:
        results = []

        for dream_id in dream_ids:
            content = await self.prepare_dream_for_indexing(dream_id, user_id)
            if content:
                results.append({
                    "id": dream_id,
                    "content": content,
                })

        return results


def get_indexing_service(db: AsyncSession) -> DreamIndexingService:
    return DreamIndexingService(db)
