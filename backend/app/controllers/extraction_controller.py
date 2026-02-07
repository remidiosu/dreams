import base64

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.data_models.extraction_data import ExtractedSymbolData, ExtractedCharacterData, ExtractedThemeData, \
    ExtractionPreviewResponse, ExtractPreviewRequest, ExtractedEmotionData, DreamCreatedResponse, \
    CreateDreamWithExtractionRequest
from app.dependencies.auth import get_current_user_id
from app.repositories.dream_repository import DreamRepository
from app.repositories.symbol_repository import SymbolRepository
from app.repositories.character_repository import CharacterRepository
from app.services.extraction_service import get_extraction_service
from app.services.multimodal_service import get_multimodal_service
from app.logger import logger


extraction_router = APIRouter(prefix="/extract", tags=["Extraction"])


@extraction_router.post("/preview", response_model=ExtractionPreviewResponse)
async def extract_preview(
        data: ExtractPreviewRequest,
        user_id: int = Depends(get_current_user_id),
):
    try:
        narrative = data.narrative or ""
        processed_narrative = None

        # Transcribe audio if provided
        if data.audio_base64 and data.audio_mime_type:
            multimodal = get_multimodal_service()
            audio_bytes = base64.b64decode(data.audio_base64)
            transcript = await multimodal.transcribe_audio(audio_bytes, data.audio_mime_type)
            if transcript:
                if narrative:
                    narrative = f"{narrative}\n\n{transcript}"
                else:
                    narrative = transcript
                processed_narrative = narrative

        if not narrative.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Narrative is required (either text or audio)",
            )

        extraction_service = get_extraction_service()
        extraction = await extraction_service.extract_only(
            narrative=narrative,
            setting=data.setting,
        )

        symbols = [
            ExtractedSymbolData(
                name=s.name,
                category=s.category,
                context=s.context,
                universal_meaning=s.universal_meaning,
                personal_associations=s.personal_associations,
                personal_meaning=None,
                is_user_added=False,
            )
            for s in extraction.symbols
        ]
        characters = [
            ExtractedCharacterData(
                name=c.name,
                character_type=c.character_type,
                real_world_relation=c.real_world_relation,
                role_in_dream=c.role_in_dream,
                archetype=c.archetype,
                traits=c.traits,
                context=c.context,
                personal_significance=None,
                is_user_added=False,
            )
            for c in extraction.characters
        ]
        themes = [
            ExtractedThemeData(
                theme=t.theme,
                is_user_added=False,
            )
            for t in extraction.themes
        ]
        emotions = [
            ExtractedEmotionData(
                emotion=e.emotion,
                intensity=e.intensity,
                emotion_type=e.emotion_type,
            )
            for e in extraction.emotions
        ]

        # Analyze images if provided and merge results
        if data.images:
            multimodal = get_multimodal_service()
            image_dicts = [img.model_dump() for img in data.images]
            image_results = await multimodal.analyze_images(image_dicts)

            existing_symbol_names = {s.name.lower() for s in symbols}
            existing_char_names = {c.name.lower() for c in characters}
            existing_themes = {t.theme.lower() for t in themes}
            existing_emotions = {e.emotion.lower() for e in emotions}

            for result in image_results:
                for sym in result.get("symbols", []):
                    if sym.get("name", "").lower() not in existing_symbol_names:
                        symbols.append(ExtractedSymbolData(
                            name=sym["name"],
                            category=sym.get("category", "other"),
                            context=sym.get("context", "Seen in dream image"),
                            universal_meaning=None,
                            personal_associations=[],
                            personal_meaning=None,
                            is_user_added=False,
                        ))
                        existing_symbol_names.add(sym["name"].lower())

                for char in result.get("characters", []):
                    if char.get("name", "").lower() not in existing_char_names:
                        characters.append(ExtractedCharacterData(
                            name=char["name"],
                            character_type=char.get("character_type", "unknown_person"),
                            real_world_relation=None,
                            role_in_dream="unknown",
                            archetype=None,
                            traits=[],
                            context=char.get("context", "Seen in dream image"),
                            personal_significance=None,
                            is_user_added=False,
                        ))
                        existing_char_names.add(char["name"].lower())

                for theme in result.get("themes", []):
                    if theme.lower() not in existing_themes:
                        themes.append(ExtractedThemeData(theme=theme, is_user_added=False))
                        existing_themes.add(theme.lower())

                for emotion in result.get("emotions", []):
                    if emotion.lower() not in existing_emotions:
                        emotions.append(ExtractedEmotionData(
                            emotion=emotion, intensity=5, emotion_type="during",
                        ))
                        existing_emotions.add(emotion.lower())

        return ExtractionPreviewResponse(
            symbols=symbols,
            characters=characters,
            themes=themes,
            emotions=emotions,
            setting_analysis=extraction.setting_analysis,
            jungian_interpretation=extraction.jungian_interpretation,
            processed_narrative=processed_narrative,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction preview failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Extraction failed. Please try again."
        )


@extraction_router.post("/create", response_model=DreamCreatedResponse)
async def create_dream_with_extraction(
        data: CreateDreamWithExtractionRequest,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    dream_repo = DreamRepository(db)
    symbol_repo = SymbolRepository(db)
    character_repo = CharacterRepository(db)

    try:
        dream = await dream_repo.create_dream(
            user_id=user_id,
            title=data.title,
            narrative=data.narrative,
            dream_date=data.dream_date,
            setting=data.setting,
            development=data.development,
            ending=data.ending,
            lucidity_level=data.lucidity_level,
            sleep_quality=data.sleep_quality,
            emotional_intensity=data.emotional_intensity,
            is_recurring=data.is_recurring,
            is_nightmare=data.is_nightmare,
            ritual_completed=data.ritual_completed,
            ritual_description=data.ritual_description,
            personal_interpretation=data.personal_interpretation,
        )

        symbols_created = 0
        characters_created = 0
        themes_created = 0
        emotions_created = 0

        for symbol_data in data.symbols:
            try:
                sym, _ = await symbol_repo.get_or_create_symbol(
                    user_id=user_id,
                    name=symbol_data.name,
                    category=symbol_data.category,
                )
                await symbol_repo.add_symbol_to_dream(
                    dream_id=dream.id,
                    symbol_id=sym.id,
                    dream_date=data.dream_date,
                    context_note=symbol_data.context,
                    personal_meaning=symbol_data.personal_meaning,
                    is_ai_extracted=not symbol_data.is_user_added,
                )

                for assoc in symbol_data.personal_associations:
                    try:
                        await symbol_repo.add_association(
                            symbol_id=sym.id,
                            association_text=assoc,
                            source="ai_suggested",
                        )
                    except Exception:
                        pass

                symbols_created += 1
            except Exception as e:
                logger.error(f"Error saving symbol {symbol_data.name}: {e}")

        for char_data in data.characters:
            try:
                char, _ = await character_repo.get_or_create_character(
                    user_id=user_id,
                    name=char_data.name,
                    character_type=char_data.character_type,
                    real_world_relation=char_data.real_world_relation,
                )

                await character_repo.add_character_to_dream(
                    dream_id=dream.id,
                    character_id=char.id,
                    dream_date=data.dream_date,
                    role_in_dream=char_data.role_in_dream,
                    archetype=char_data.archetype,
                    traits=char_data.traits,
                    context_note=char_data.context,
                    personal_significance=char_data.personal_significance,
                    is_ai_extracted=not char_data.is_user_added,
                )

                characters_created += 1
            except Exception as e:
                logger.error(f"Error saving character {char_data.name}: {e}")

        for theme_data in data.themes:
            try:
                await dream_repo.add_dream_theme(
                    dream_id=dream.id,
                    theme=theme_data.theme,
                    is_ai_extracted=not theme_data.is_user_added,
                )
                themes_created += 1
            except Exception as e:
                logger.error(f"Error saving theme {theme_data.theme}: {e}")

        for emotion_data in data.emotions:
            try:
                await dream_repo.add_dream_emotion(
                    dream_id=dream.id,
                    emotion=emotion_data.emotion,
                    emotion_type=emotion_data.emotion_type,
                    intensity=emotion_data.intensity,
                )
                emotions_created += 1
            except Exception as e:
                logger.error(f"Error saving emotion {emotion_data.emotion}: {e}")

        await dream_repo.mark_ai_extraction_done(dream.id)
        await db.commit()

        return DreamCreatedResponse(
            dream_id=dream.id,
            title=dream.title,
            symbols_created=symbols_created,
            characters_created=characters_created,
            themes_created=themes_created,
            emotions_created=emotions_created,
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create dream: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create dream. Please try again."
        )
