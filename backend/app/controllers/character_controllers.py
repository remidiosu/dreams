from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user_id
from app.repositories.character_repository import CharacterRepository
from app.repositories.dream_repository import DreamRepository
from app.data_models.symbol_data import AssociationCreate, AssociationResponse
from app.data_models.character_data import (
    DreamCharacterCreate,
    DreamCharacterUpdate,
    DreamCharacterResponse,
    CharacterUpdate,
    CharacterResponse,
    CharacterWithDreamsResponse,
    CharacterListResponse,
    CharacterDreamAppearance,
)


dream_character_router = APIRouter(prefix="/dreams/{dream_id}/characters", tags=["Dream Characters"])


@dream_character_router.post("", response_model=DreamCharacterResponse, status_code=status.HTTP_201_CREATED)
async def add_character_to_dream(
        dream_id: int,
        data: DreamCharacterCreate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)
    char_repo = CharacterRepository(db)
    dream = await dream_repo.get_by_id(dream_id, user_id)
    if not dream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dream not found")

    character, created = await char_repo.get_or_create_character(
        user_id=user_id,
        name=data.name,
        character_type=data.character_type,
        real_world_relation=data.real_world_relation,
    )

    if await char_repo.character_exists_in_dream(dream_id, character.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character already exists in this dream"
        )

    for assoc_text in data.associations:
        await char_repo.add_association(character.id, assoc_text, source="user")

    dream_character = await char_repo.add_character_to_dream(
        dream_id=dream_id,
        character_id=character.id,
        dream_date=dream.dream_date,
        role_in_dream=data.role_in_dream,
        archetype=data.archetype,
        traits=data.traits,
        context_note=data.context_note,
        is_ai_extracted=False,
    )

    associations = await char_repo.get_character_associations(character.id)

    return DreamCharacterResponse(
        id=dream_character.id,
        character_id=character.id,
        name=character.name,
        character_type=character.character_type.value if character.character_type else None,
        real_world_relation=character.real_world_relation,
        role_in_dream=dream_character.role_in_dream.value if dream_character.role_in_dream else None,
        archetype=dream_character.archetype.value if dream_character.archetype else None,
        traits=dream_character.traits or [],
        associations=[
            AssociationResponse(
                id=a.id,
                association_text=a.association_text,
                source=a.source.value,
                is_confirmed=a.is_confirmed,
                created_at=a.created_at,
            ) for a in associations
        ],
        is_ai_extracted=dream_character.is_ai_extracted,
        is_confirmed=dream_character.is_confirmed,
        context_note=dream_character.context_note,
        created_at=dream_character.created_at,
    )


@dream_character_router.get("", response_model=list[DreamCharacterResponse])
async def list_dream_characters(
        dream_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)
    char_repo = CharacterRepository(db)

    if not await dream_repo.dream_exists(dream_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dream not found")

    characters_data = await char_repo.get_dream_characters(dream_id)

    return [
        DreamCharacterResponse(
            id=cd["dream_character"].id,
            character_id=cd["character"].id,
            name=cd["character"].name,
            character_type=cd["character"].character_type.value if cd["character"].character_type else None,
            real_world_relation=cd["character"].real_world_relation,
            role_in_dream=cd["dream_character"].role_in_dream.value if cd["dream_character"].role_in_dream else None,
            archetype=cd["dream_character"].archetype.value if cd["dream_character"].archetype else None,
            traits=cd["dream_character"].traits or [],
            associations=[
                AssociationResponse(
                    id=a.id,
                    association_text=a.association_text,
                    source=a.source.value,
                    is_confirmed=a.is_confirmed,
                    created_at=a.created_at,
                ) for a in cd["associations"]
            ],
            is_ai_extracted=cd["dream_character"].is_ai_extracted,
            is_confirmed=cd["dream_character"].is_confirmed,
            context_note=cd["dream_character"].context_note,
            created_at=cd["dream_character"].created_at,
        )
        for cd in characters_data
    ]


@dream_character_router.put("/{dream_character_id}", response_model=DreamCharacterResponse)
async def update_dream_character(
        dream_id: int,
        dream_character_id: int,
        data: DreamCharacterUpdate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)
    char_repo = CharacterRepository(db)

    if not await dream_repo.dream_exists(dream_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dream not found")

    dream_character = await char_repo.update_dream_character(
        dream_character_id=dream_character_id,
        dream_id=dream_id,
        role_in_dream=data.role_in_dream,
        archetype=data.archetype,
        traits=data.traits,
        context_note=data.context_note,
        is_confirmed=data.is_confirmed,
    )

    if not dream_character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found in dream")

    character = await char_repo.get_character_by_id(dream_character.character_id, user_id)
    associations = await char_repo.get_character_associations(character.id)

    return DreamCharacterResponse(
        id=dream_character.id,
        character_id=character.id,
        name=character.name,
        character_type=character.character_type.value if character.character_type else None,
        real_world_relation=character.real_world_relation,
        role_in_dream=dream_character.role_in_dream.value if dream_character.role_in_dream else None,
        archetype=dream_character.archetype.value if dream_character.archetype else None,
        traits=dream_character.traits or [],
        associations=[
            AssociationResponse(
                id=a.id,
                association_text=a.association_text,
                source=a.source.value,
                is_confirmed=a.is_confirmed,
                created_at=a.created_at,
            ) for a in associations
        ],
        is_ai_extracted=dream_character.is_ai_extracted,
        is_confirmed=dream_character.is_confirmed,
        context_note=dream_character.context_note,
        created_at=dream_character.created_at,
    )


@dream_character_router.delete("/{dream_character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_character_from_dream(
        dream_id: int,
        dream_character_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)
    char_repo = CharacterRepository(db)

    if not await dream_repo.dream_exists(dream_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dream not found")

    removed = await char_repo.remove_character_from_dream(dream_character_id, dream_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found in dream")

    return None


character_router = APIRouter(prefix="/characters", tags=["Characters"])


@character_router.get("", response_model=CharacterListResponse)
async def list_characters(
        per_page: int = Query(50, ge=1, le=100),
        cursor: Optional[int] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    char_repo = CharacterRepository(db)

    characters, has_more = await char_repo.list_characters(user_id, per_page, cursor)

    character_responses = []
    for character in characters:
        associations = await char_repo.get_character_associations(character.id)
        character_responses.append(
            CharacterResponse(
                id=character.id,
                name=character.name,
                character_type=character.character_type.value if character.character_type else None,
                real_world_relation=character.real_world_relation,
                occurrence_count=character.occurrence_count,
                first_appeared=character.first_appeared,
                last_appeared=character.last_appeared,
                associations=[
                    AssociationResponse(
                        id=a.id,
                        association_text=a.association_text,
                        source=a.source.value,
                        is_confirmed=a.is_confirmed,
                        created_at=a.created_at,
                    ) for a in associations
                ],
                created_at=character.created_at,
                updated_at=character.updated_at,
            )
        )

    return CharacterListResponse(
        data=character_responses,
        has_more=has_more,
        next_cursor=characters[-1].id if has_more and characters else None,
    )


@character_router.get("/{character_id}", response_model=CharacterWithDreamsResponse)
async def get_character(
        character_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    char_repo = CharacterRepository(db)
    result = await char_repo.get_character_with_dreams(character_id, user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    character = result["character"]
    associations = result["associations"]
    dreams = result["dreams"]

    return CharacterWithDreamsResponse(
        id=character.id,
        name=character.name,
        character_type=character.character_type.value if character.character_type else None,
        real_world_relation=character.real_world_relation,
        occurrence_count=character.occurrence_count,
        first_appeared=character.first_appeared,
        last_appeared=character.last_appeared,
        associations=[
            AssociationResponse(
                id=a.id,
                association_text=a.association_text,
                source=a.source.value,
                is_confirmed=a.is_confirmed,
                created_at=a.created_at,
            ) for a in associations
        ],
        dreams=[CharacterDreamAppearance(**d) for d in dreams],
        archetype_counts=result["archetype_counts"],
        common_traits=result["common_traits"],
        created_at=character.created_at,
        updated_at=character.updated_at,
    )


@character_router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
        character_id: int,
        data: CharacterUpdate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    char_repo = CharacterRepository(db)
    character = await char_repo.update_character(
        character_id=character_id,
        user_id=user_id,
        name=data.name,
        character_type=data.character_type,
        real_world_relation=data.real_world_relation,
    )

    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    associations = await char_repo.get_character_associations(character.id)

    return CharacterResponse(
        id=character.id,
        name=character.name,
        character_type=character.character_type.value if character.character_type else None,
        real_world_relation=character.real_world_relation,
        occurrence_count=character.occurrence_count,
        first_appeared=character.first_appeared,
        last_appeared=character.last_appeared,
        associations=[
            AssociationResponse(
                id=a.id,
                association_text=a.association_text,
                source=a.source.value,
                is_confirmed=a.is_confirmed,
                created_at=a.created_at,
            ) for a in associations
        ],
        created_at=character.created_at,
        updated_at=character.updated_at,
    )


@character_router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
        character_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    char_repo = CharacterRepository(db)
    deleted = await char_repo.delete_character(character_id, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    return None


@character_router.post("/{character_id}/associations", response_model=AssociationResponse,
                       status_code=status.HTTP_201_CREATED)
async def add_character_association(
        character_id: int,
        data: AssociationCreate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    char_repo = CharacterRepository(db)
    character = await char_repo.get_character_by_id(character_id, user_id)
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    association = await char_repo.add_association(
        character_id=character_id,
        association_text=data.association_text,
        source="user",
    )

    return AssociationResponse(
        id=association.id,
        association_text=association.association_text,
        source=association.source.value,
        is_confirmed=association.is_confirmed,
        created_at=association.created_at,
    )


@character_router.delete("/{character_id}/associations/{association_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character_association(
        character_id: int,
        association_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    char_repo = CharacterRepository(db)
    character = await char_repo.get_character_by_id(character_id, user_id)
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")

    deleted = await char_repo.delete_association(association_id, character_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Association not found")

    return None
