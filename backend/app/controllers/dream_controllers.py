from typing import Optional
from datetime import date

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user_id
from app.repositories.dream_repository import DreamRepository
from app.data_models.dream_data import (
    DreamCreate,
    DreamUpdate,
    DreamResponse,
    DreamSummary,
    DreamListResponse,
    EmotionInDream,
    SymbolInDream,
    CharacterInDream,
    ThemeInDream,
)

dream_router = APIRouter(prefix="/dreams", tags=["Dreams"])


@dream_router.post("", response_model=DreamResponse, status_code=status.HTTP_201_CREATED)
async def create_dream(
        data: DreamCreate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)

    dream = await dream_repo.create_dream(
        user_id=user_id,
        title=data.title,
        narrative=data.narrative,
        dream_date=data.dream_date,
        setting=data.setting,
        development=data.development,
        ending=data.ending,
        emotion_on_waking=data.emotion_on_waking,
        emotional_intensity=data.emotional_intensity,
        lucidity_level=data.lucidity_level,
        sleep_quality=data.sleep_quality,
        is_recurring=data.is_recurring,
        is_nightmare=data.is_nightmare,
        ritual_completed=data.ritual_completed,
        ritual_description=data.ritual_description,
        personal_interpretation=data.personal_interpretation,
        conscious_context=data.conscious_context,
    )

    emotions = []
    if data.emotions:
        emotion_dicts = [e.model_dump() for e in data.emotions]
        await dream_repo.add_dream_emotions(dream.id, emotion_dicts)
        emotions = [
            EmotionInDream(
                emotion=e.emotion,
                emotion_type=e.emotion_type,
                intensity=e.intensity
            ) for e in data.emotions
        ]

    # TODO: If data.auto_extract, trigger AI extraction service

    return DreamResponse(
        id=dream.id,
        user_id=dream.user_id,
        title=dream.title,
        narrative=dream.narrative,
        dream_date=dream.dream_date,
        setting=dream.setting,
        development=dream.development,
        ending=dream.ending,
        emotions=emotions,
        emotion_on_waking=dream.emotion_on_waking,
        emotional_intensity=dream.emotional_intensity,
        lucidity_level=dream.lucidity_level.value if dream.lucidity_level else None,
        sleep_quality=dream.sleep_quality,
        is_recurring=dream.is_recurring or False,
        is_nightmare=dream.is_nightmare or False,
        ritual_completed=dream.ritual_completed or False,
        ritual_description=dream.ritual_description,
        personal_interpretation=dream.personal_interpretation,
        conscious_context=dream.conscious_context,
        is_indexed=dream.is_indexed or False,
        indexed_at=dream.indexed_at,
        ai_extraction_done=dream.ai_extraction_done or False,
        symbols=[],
        characters=[],
        themes=[],
        created_at=dream.created_at,
        updated_at=dream.updated_at,
    )


@dream_router.get("", response_model=DreamListResponse)
async def list_dreams(
        per_page: int = Query(25, ge=1, le=100),
        cursor: Optional[int] = Query(None),
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        emotion: Optional[str] = Query(None),
        has_ritual: Optional[bool] = Query(None),
        lucidity_level: Optional[str] = Query(None),
        is_indexed: Optional[bool] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)

    dream_summaries, has_more = await dream_repo.list_dreams(
        user_id=user_id,
        per_page=per_page,
        cursor=cursor,
        date_from=date_from,
        date_to=date_to,
        emotion=emotion,
        has_ritual=has_ritual,
        lucidity_level=lucidity_level,
        is_indexed=is_indexed,
    )

    summaries = [
        DreamSummary(
            id=ds["dream"].id,
            title=ds["dream"].title,
            dream_date=ds["dream"].dream_date,
            emotions=ds["emotions"],
            emotional_intensity=ds["dream"].emotional_intensity,
            lucidity_level=ds["dream"].lucidity_level.value if ds["dream"].lucidity_level else None,
            is_recurring=ds["dream"].is_recurring or False,
            is_nightmare=ds["dream"].is_nightmare or False,
            ritual_completed=ds["dream"].ritual_completed or False,
            symbol_count=ds["symbol_count"],
            character_count=ds["character_count"],
            created_at=ds["dream"].created_at,
        )
        for ds in dream_summaries
    ]

    next_cursor = summaries[-1].id if has_more and summaries else None

    return DreamListResponse(
        data=summaries,
        has_more=has_more,
        next_cursor=next_cursor,
    )


@dream_router.get("/{dream_id}", response_model=DreamResponse)
async def get_dream(
        dream_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)

    result = await dream_repo.get_dream_with_associations(dream_id, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dream not found"
        )

    dream = result["dream"]
    emotions = result["emotions"]
    symbols = result["symbols"]
    characters = result["characters"]
    themes = result["themes"]

    return DreamResponse(
        id=dream.id,
        user_id=dream.user_id,
        title=dream.title,
        narrative=dream.narrative,
        dream_date=dream.dream_date,
        setting=dream.setting,
        development=dream.development,
        ending=dream.ending,
        emotions=[
            EmotionInDream(
                emotion=e.emotion,
                emotion_type=e.emotion_type.value if e.emotion_type else "during",
                intensity=e.intensity
            ) for e in emotions
        ],
        emotion_on_waking=dream.emotion_on_waking,
        emotional_intensity=dream.emotional_intensity,
        lucidity_level=dream.lucidity_level.value if dream.lucidity_level else None,
        sleep_quality=dream.sleep_quality,
        is_recurring=dream.is_recurring or False,
        is_nightmare=dream.is_nightmare or False,
        ritual_completed=dream.ritual_completed or False,
        ritual_description=dream.ritual_description,
        personal_interpretation=dream.personal_interpretation,
        conscious_context=dream.conscious_context,
        is_indexed=dream.is_indexed or False,
        indexed_at=dream.indexed_at,
        ai_extraction_done=dream.ai_extraction_done or False,
        symbols=[SymbolInDream(**s) for s in symbols],
        characters=[CharacterInDream(**c) for c in characters],
        themes=[
            ThemeInDream(
                id=t.id,
                theme=t.theme,
                is_ai_extracted=t.is_ai_extracted,
                is_confirmed=t.is_confirmed
            ) for t in themes
        ],
        created_at=dream.created_at,
        updated_at=dream.updated_at,
    )


@dream_router.put("/{dream_id}", response_model=DreamResponse)
async def update_dream(
        dream_id: int,
        data: DreamUpdate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)

    if not await dream_repo.dream_exists(dream_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dream not found"
        )

    updates = data.model_dump(exclude_none=True, exclude={"emotions"})
    dream = await dream_repo.update_dream(dream_id, user_id, **updates)
    if data.emotions is not None:
        emotion_dicts = [e.model_dump() for e in data.emotions]
        await dream_repo.replace_dream_emotions(dream_id, emotion_dicts)

    result = await dream_repo.get_dream_with_associations(dream_id, user_id)
    dream = result["dream"]
    emotions = result["emotions"]
    symbols = result["symbols"]
    characters = result["characters"]
    themes = result["themes"]

    return DreamResponse(
        id=dream.id,
        user_id=dream.user_id,
        title=dream.title,
        narrative=dream.narrative,
        dream_date=dream.dream_date,
        setting=dream.setting,
        development=dream.development,
        ending=dream.ending,
        emotions=[
            EmotionInDream(
                emotion=e.emotion,
                emotion_type=e.emotion_type.value if e.emotion_type else "during",
                intensity=e.intensity
            ) for e in emotions
        ],
        emotion_on_waking=dream.emotion_on_waking,
        emotional_intensity=dream.emotional_intensity,
        lucidity_level=dream.lucidity_level.value if dream.lucidity_level else None,
        sleep_quality=dream.sleep_quality,
        is_recurring=dream.is_recurring or False,
        is_nightmare=dream.is_nightmare or False,
        ritual_completed=dream.ritual_completed or False,
        ritual_description=dream.ritual_description,
        personal_interpretation=dream.personal_interpretation,
        conscious_context=dream.conscious_context,
        is_indexed=dream.is_indexed or False,
        indexed_at=dream.indexed_at,
        ai_extraction_done=dream.ai_extraction_done or False,
        symbols=[SymbolInDream(**s) for s in symbols],
        characters=[CharacterInDream(**c) for c in characters],
        themes=[
            ThemeInDream(
                id=t.id,
                theme=t.theme,
                is_ai_extracted=t.is_ai_extracted,
                is_confirmed=t.is_confirmed
            ) for t in themes
        ],
        created_at=dream.created_at,
        updated_at=dream.updated_at,
    )


@dream_router.delete("/{dream_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dream(
        dream_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)

    deleted = await dream_repo.delete_dream(dream_id, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dream not found"
        )

    return None


@dream_router.post("/{dream_id}/extract", response_model=DreamResponse)
async def extract_dream_entities(
        dream_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    from app.services.extraction_service import get_extraction_service
    from app.repositories.symbol_repository import SymbolRepository
    from app.repositories.character_repository import CharacterRepository

    dream_repo = DreamRepository(db)
    symbol_repo = SymbolRepository(db)
    character_repo = CharacterRepository(db)

    result = await dream_repo.get_dream_with_associations(dream_id, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dream not found"
        )

    dream = result["dream"]

    if dream.ai_extraction_done:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AI extraction already completed for this dream"
        )

    try:
        extraction_service = get_extraction_service()
        extraction = await extraction_service.extract_and_save(
            dream_id=dream_id,
            user_id=user_id,
            narrative=dream.narrative,
            dream_date=dream.dream_date,
            setting=dream.setting,
            symbol_repo=symbol_repo,
            character_repo=character_repo,
            dream_repo=dream_repo,
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI extraction failed. Please try again."
        )

    result = await dream_repo.get_dream_with_associations(dream_id, user_id)
    dream = result["dream"]
    emotions = result["emotions"]
    symbols = result["symbols"]
    characters = result["characters"]
    themes = result["themes"]

    return DreamResponse(
        id=dream.id,
        user_id=dream.user_id,
        title=dream.title,
        narrative=dream.narrative,
        dream_date=dream.dream_date,
        setting=dream.setting,
        development=dream.development,
        ending=dream.ending,
        emotions=[
            EmotionInDream(
                emotion=e.emotion,
                emotion_type=e.emotion_type.value if e.emotion_type else "during",
                intensity=e.intensity
            ) for e in emotions
        ],
        emotion_on_waking=dream.emotion_on_waking,
        emotional_intensity=dream.emotional_intensity,
        lucidity_level=dream.lucidity_level.value if dream.lucidity_level else None,
        sleep_quality=dream.sleep_quality,
        is_recurring=dream.is_recurring or False,
        is_nightmare=dream.is_nightmare or False,
        ritual_completed=dream.ritual_completed or False,
        ritual_description=dream.ritual_description,
        personal_interpretation=dream.personal_interpretation,
        conscious_context=dream.conscious_context,
        is_indexed=dream.is_indexed or False,
        indexed_at=dream.indexed_at,
        ai_extraction_done=dream.ai_extraction_done or False,
        symbols=[SymbolInDream(**s) for s in symbols],
        characters=[CharacterInDream(**c) for c in characters],
        themes=[
            ThemeInDream(
                id=t.id,
                theme=t.theme,
                is_ai_extracted=t.is_ai_extracted,
                is_confirmed=t.is_confirmed
            ) for t in themes
        ],
        created_at=dream.created_at,
        updated_at=dream.updated_at,
    )
