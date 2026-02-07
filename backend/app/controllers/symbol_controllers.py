from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user_id
from app.repositories.symbol_repository import SymbolRepository
from app.repositories.dream_repository import DreamRepository
from app.data_models.symbol_data import (
    DreamSymbolCreate,
    DreamSymbolUpdate,
    DreamSymbolResponse,
    SymbolUpdate,
    SymbolResponse,
    SymbolWithDreamsResponse,
    SymbolListResponse,
    SymbolDreamAppearance,
    AssociationCreate,
    AssociationResponse,
)


dream_symbol_router = APIRouter(prefix="/dreams/{dream_id}/symbols", tags=["Dream Symbols"])


@dream_symbol_router.post("", response_model=DreamSymbolResponse, status_code=status.HTTP_201_CREATED)
async def add_symbol_to_dream(
        dream_id: int,
        data: DreamSymbolCreate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)
    symbol_repo = SymbolRepository(db)

    dream = await dream_repo.get_by_id(dream_id, user_id)
    if not dream:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dream not found")

    symbol, created = await symbol_repo.get_or_create_symbol(
        user_id=user_id,
        name=data.name,
        category=data.category,
    )

    if await symbol_repo.symbol_exists_in_dream(dream_id, symbol.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Symbol already exists in this dream"
        )

    for assoc_text in data.associations:
        await symbol_repo.add_association(symbol.id, assoc_text, source="user")

    dream_symbol = await symbol_repo.add_symbol_to_dream(
        dream_id=dream_id,
        symbol_id=symbol.id,
        dream_date=dream.dream_date,
        context_note=data.context_note,
        is_ai_extracted=False,
    )

    associations = await symbol_repo.get_symbol_associations(symbol.id)

    return DreamSymbolResponse(
        id=dream_symbol.id,
        symbol_id=symbol.id,
        name=symbol.name,
        category=symbol.category.value if symbol.category else None,
        associations=[
            AssociationResponse(
                id=a.id,
                association_text=a.association_text,
                source=a.source.value,
                is_confirmed=a.is_confirmed,
                created_at=a.created_at,
            ) for a in associations
        ],
        is_ai_extracted=dream_symbol.is_ai_extracted,
        is_confirmed=dream_symbol.is_confirmed,
        context_note=dream_symbol.context_note,
        created_at=dream_symbol.created_at,
    )


@dream_symbol_router.get("", response_model=list[DreamSymbolResponse])
async def list_dream_symbols(
        dream_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)
    symbol_repo = SymbolRepository(db)

    if not await dream_repo.dream_exists(dream_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dream not found")

    symbols_data = await symbol_repo.get_dream_symbols(dream_id)

    return [
        DreamSymbolResponse(
            id=sd["dream_symbol"].id,
            symbol_id=sd["symbol"].id,
            name=sd["symbol"].name,
            category=sd["symbol"].category.value if sd["symbol"].category else None,
            associations=[
                AssociationResponse(
                    id=a.id,
                    association_text=a.association_text,
                    source=a.source.value,
                    is_confirmed=a.is_confirmed,
                    created_at=a.created_at,
                ) for a in sd["associations"]
            ],
            is_ai_extracted=sd["dream_symbol"].is_ai_extracted,
            is_confirmed=sd["dream_symbol"].is_confirmed,
            context_note=sd["dream_symbol"].context_note,
            created_at=sd["dream_symbol"].created_at,
        )
        for sd in symbols_data
    ]


@dream_symbol_router.put("/{dream_symbol_id}", response_model=DreamSymbolResponse)
async def update_dream_symbol(
        dream_id: int,
        dream_symbol_id: int,
        data: DreamSymbolUpdate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)
    symbol_repo = SymbolRepository(db)

    if not await dream_repo.dream_exists(dream_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dream not found")

    dream_symbol = await symbol_repo.update_dream_symbol(
        dream_symbol_id=dream_symbol_id,
        dream_id=dream_id,
        context_note=data.context_note,
        is_confirmed=data.is_confirmed,
    )

    if not dream_symbol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found in dream")

    symbol = await symbol_repo.get_symbol_by_id(dream_symbol.symbol_id, user_id)
    associations = await symbol_repo.get_symbol_associations(symbol.id)

    return DreamSymbolResponse(
        id=dream_symbol.id,
        symbol_id=symbol.id,
        name=symbol.name,
        category=symbol.category.value if symbol.category else None,
        associations=[
            AssociationResponse(
                id=a.id,
                association_text=a.association_text,
                source=a.source.value,
                is_confirmed=a.is_confirmed,
                created_at=a.created_at,
            ) for a in associations
        ],
        is_ai_extracted=dream_symbol.is_ai_extracted,
        is_confirmed=dream_symbol.is_confirmed,
        context_note=dream_symbol.context_note,
        created_at=dream_symbol.created_at,
    )


@dream_symbol_router.delete("/{dream_symbol_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_symbol_from_dream(
        dream_id: int,
        dream_symbol_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    dream_repo = DreamRepository(db)
    symbol_repo = SymbolRepository(db)

    if not await dream_repo.dream_exists(dream_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dream not found")

    removed = await symbol_repo.remove_symbol_from_dream(dream_symbol_id, dream_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found in dream")

    return None


symbol_router = APIRouter(prefix="/symbols", tags=["Symbols"])


@symbol_router.get("", response_model=SymbolListResponse)
async def list_symbols(
        per_page: int = Query(50, ge=1, le=100),
        cursor: Optional[int] = Query(None),
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    symbol_repo = SymbolRepository(db)

    symbols, has_more = await symbol_repo.list_symbols(user_id, per_page, cursor)

    symbol_responses = []
    for symbol in symbols:
        associations = await symbol_repo.get_symbol_associations(symbol.id)
        symbol_responses.append(
            SymbolResponse(
                id=symbol.id,
                name=symbol.name,
                category=symbol.category.value if symbol.category else None,
                occurrence_count=symbol.occurrence_count,
                first_appeared=symbol.first_appeared,
                last_appeared=symbol.last_appeared,
                associations=[
                    AssociationResponse(
                        id=a.id,
                        association_text=a.association_text,
                        source=a.source.value,
                        is_confirmed=a.is_confirmed,
                        created_at=a.created_at,
                    ) for a in associations
                ],
                created_at=symbol.created_at,
                updated_at=symbol.updated_at,
            )
        )

    next_cursor = symbols[-1].id if has_more and symbols else None

    return SymbolListResponse(
        data=symbol_responses,
        has_more=has_more,
        next_cursor=next_cursor,
        total_count=len(symbol_responses),
    )

@symbol_router.get("/{symbol_id}", response_model=SymbolWithDreamsResponse)
async def get_symbol(
        symbol_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    symbol_repo = SymbolRepository(db)

    result = await symbol_repo.get_symbol_with_dreams(symbol_id, user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found")

    symbol = result["symbol"]
    associations = result["associations"]
    dreams = result["dreams"]

    return SymbolWithDreamsResponse(
        id=symbol.id,
        name=symbol.name,
        category=symbol.category.value if symbol.category else None,
        occurrence_count=symbol.occurrence_count,
        first_appeared=symbol.first_appeared,
        last_appeared=symbol.last_appeared,
        associations=[
            AssociationResponse(
                id=a.id,
                association_text=a.association_text,
                source=a.source.value,
                is_confirmed=a.is_confirmed,
                created_at=a.created_at,
            ) for a in associations
        ],
        dreams=[SymbolDreamAppearance(**d) for d in dreams],
        created_at=symbol.created_at,
        updated_at=symbol.updated_at,
    )


@symbol_router.put("/{symbol_id}", response_model=SymbolResponse)
async def update_symbol(
        symbol_id: int,
        data: SymbolUpdate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    symbol_repo = SymbolRepository(db)

    symbol = await symbol_repo.update_symbol(
        symbol_id=symbol_id,
        user_id=user_id,
        name=data.name,
        category=data.category,
    )

    if not symbol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found")

    associations = await symbol_repo.get_symbol_associations(symbol.id)

    return SymbolResponse(
        id=symbol.id,
        name=symbol.name,
        category=symbol.category.value if symbol.category else None,
        occurrence_count=symbol.occurrence_count,
        first_appeared=symbol.first_appeared,
        last_appeared=symbol.last_appeared,
        associations=[
            AssociationResponse(
                id=a.id,
                association_text=a.association_text,
                source=a.source.value,
                is_confirmed=a.is_confirmed,
                created_at=a.created_at,
            ) for a in associations
        ],
        created_at=symbol.created_at,
        updated_at=symbol.updated_at,
    )


@symbol_router.delete("/{symbol_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_symbol(
        symbol_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    symbol_repo = SymbolRepository(db)

    deleted = await symbol_repo.delete_symbol(symbol_id, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found")

    return None


@symbol_router.post("/{symbol_id}/associations", response_model=AssociationResponse,
                    status_code=status.HTTP_201_CREATED)
async def add_symbol_association(
        symbol_id: int,
        data: AssociationCreate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    symbol_repo = SymbolRepository(db)
    symbol = await symbol_repo.get_symbol_by_id(symbol_id, user_id)
    if not symbol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found")

    association = await symbol_repo.add_association(
        symbol_id=symbol_id,
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


@symbol_router.delete("/{symbol_id}/associations/{association_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_symbol_association(
        symbol_id: int,
        association_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    symbol_repo = SymbolRepository(db)
    symbol = await symbol_repo.get_symbol_by_id(symbol_id, user_id)
    if not symbol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found")

    deleted = await symbol_repo.delete_association(association_id, symbol_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Association not found")

    return None
