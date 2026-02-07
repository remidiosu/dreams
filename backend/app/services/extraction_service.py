import json
from typing import Optional
from datetime import date

from google import genai
from google.genai import types

from app.logger import logger
from app.config import settings
from app.services.gemini_client import generate_content_with_retry
from app.repositories.symbol_repository import SymbolRepository
from app.repositories.character_repository import CharacterRepository
from app.repositories.dream_repository import DreamRepository
from app.schemas.extraction_data import (
    ExtractedCharacter,
    ExtractedSymbol,
    ExtractedEmotion,
    ExtractedTheme,
    DreamExtraction,
    build_extraction_prompt,
)


class GeminiExtractionService:
    def __init__(self):
        api_key = settings.gemini_api_key
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
        self.client = genai.Client(api_key=api_key)
        self.model_name = settings.llm_model

    async def extract_from_dream(
            self,
            narrative: str,
            setting: Optional[str] = None,
    ) -> DreamExtraction:
        prompt = build_extraction_prompt(narrative, setting)

        try:
            response = generate_content_with_retry(
                self.client,
                self.model_name,
                prompt,
                types.GenerateContentConfig(
                    temperature=1.0,
                    thinking_config=types.ThinkingConfig(
                        thinking_level="high",
                    ),
                ),
            )

            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            if text.endswith("```"):
                text = text[:-3]

            data = json.loads(text.strip())

            return DreamExtraction(
                symbols=[ExtractedSymbol(**s) for s in data.get("symbols", [])],
                characters=[ExtractedCharacter(**c) for c in data.get("characters", [])],
                themes=[ExtractedTheme(**t) for t in data.get("themes", [])],
                emotions=[ExtractedEmotion(**e) for e in data.get("emotions", [])],
                setting_analysis=data.get("setting_analysis"),
                jungian_interpretation=data.get("jungian_interpretation"),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response text: {response.text[:500] if response else 'No response'}")
            return DreamExtraction()
        except Exception as e:
            logger.error(f"Error during dream extraction: {e}")
            raise

    async def extract_only(
            self,
            narrative: str,
            setting: Optional[str] = None,
    ) -> DreamExtraction:
        return await self.extract_from_dream(narrative, setting)

    async def save_extraction(
            self,
            dream_id: int,
            user_id: int,
            dream_date: date,
            extraction: DreamExtraction,
            symbol_repo: SymbolRepository,
            character_repo: CharacterRepository,
            dream_repo: DreamRepository,
    ) -> None:
        for symbol in extraction.symbols:
            try:
                sym, _ = await symbol_repo.get_or_create_symbol(
                    user_id=user_id,
                    name=symbol.name,
                    category=symbol.category,
                )

                if not await symbol_repo.symbol_exists_in_dream(dream_id, sym.id):
                    await symbol_repo.add_symbol_to_dream(
                        dream_id=dream_id,
                        symbol_id=sym.id,
                        dream_date=dream_date,
                        context_note=symbol.context,
                        is_ai_extracted=True,
                    )

                    for assoc in symbol.personal_associations:
                        await symbol_repo.add_association(
                            symbol_id=sym.id,
                            association_text=assoc,
                            source="ai_suggested",
                        )
            except Exception as e:
                logger.error(f"Error saving symbol {symbol.name}: {e}")

        for character in extraction.characters:
            try:
                char, _ = await character_repo.get_or_create_character(
                    user_id=user_id,
                    name=character.name,
                    character_type=character.character_type,
                    real_world_relation=character.real_world_relation,
                )

                if not await character_repo.character_exists_in_dream(dream_id, char.id):
                    await character_repo.add_character_to_dream(
                        dream_id=dream_id,
                        character_id=char.id,
                        dream_date=dream_date,
                        role_in_dream=character.role_in_dream,
                        archetype=character.archetype,
                        traits=character.traits,
                        context_note=character.context,
                        is_ai_extracted=True,
                    )
            except Exception as e:
                logger.error(f"Error saving character {character.name}: {e}")

        for theme in extraction.themes:
            try:
                await dream_repo.add_dream_theme(
                    dream_id=dream_id,
                    theme=theme.theme,
                    is_ai_extracted=True,
                )
            except Exception as e:
                logger.error(f"Error saving theme {theme.theme}: {e}")

        existing_emotions = await dream_repo.get_dream_emotions(dream_id)
        existing_emotion_names = {e.emotion.lower() for e in existing_emotions}

        for emotion in extraction.emotions:
            if emotion.emotion.lower() not in existing_emotion_names:
                try:
                    await dream_repo.add_dream_emotion(
                        dream_id=dream_id,
                        emotion=emotion.emotion,
                        emotion_type=emotion.emotion_type,
                        intensity=emotion.intensity,
                    )
                except Exception as e:
                    logger.error(f"Error saving emotion {emotion.emotion}: {e}")

        await dream_repo.mark_ai_extraction_done(dream_id)

    async def extract_and_save(
            self,
            dream_id: int,
            user_id: int,
            narrative: str,
            dream_date: date,
            setting: Optional[str],
            symbol_repo: SymbolRepository,
            character_repo: CharacterRepository,
            dream_repo: DreamRepository,
    ) -> DreamExtraction:
        extraction = await self.extract_from_dream(narrative, setting)
        await self.save_extraction(
            dream_id=dream_id,
            user_id=user_id,
            dream_date=dream_date,
            extraction=extraction,
            symbol_repo=symbol_repo,
            character_repo=character_repo,
            dream_repo=dream_repo,
        )
        return extraction


_extraction_service: Optional[GeminiExtractionService] = None


def get_extraction_service() -> GeminiExtractionService:
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = GeminiExtractionService()

    return _extraction_service
