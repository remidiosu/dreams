from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

from app.data_models.symbol_data import AssociationCreate, AssociationResponse


class DreamCharacterCreate(BaseModel):
    name: str = Field(..., min_length=1)
    character_type: Optional[str] = None
    real_world_relation: Optional[str] = None
    role_in_dream: Optional[str] = None
    archetype: Optional[str] = None
    traits: list[str] = []
    associations: list[str] = []
    context_note: Optional[str] = None

class DreamCharacterUpdate(BaseModel):
    role_in_dream: Optional[str] = None
    archetype: Optional[str] = None
    traits: Optional[list[str]] = None
    context_note: Optional[str] = None
    is_confirmed: Optional[bool] = None

class DreamCharacterResponse(BaseModel):
    id: int
    character_id: int
    name: str
    character_type: Optional[str]
    real_world_relation: Optional[str]
    role_in_dream: Optional[str]
    archetype: Optional[str]
    traits: list[str]
    associations: list[AssociationResponse]
    is_ai_extracted: bool
    is_confirmed: bool
    context_note: Optional[str]
    created_at: datetime

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    character_type: Optional[str] = None
    real_world_relation: Optional[str] = None

class CharacterResponse(BaseModel):
    id: int
    name: str
    character_type: Optional[str]
    real_world_relation: Optional[str]
    occurrence_count: int
    first_appeared: Optional[date]
    last_appeared: Optional[date]
    associations: list[AssociationResponse]
    created_at: datetime
    updated_at: datetime

class CharacterWithDreamsResponse(BaseModel):
    id: int
    name: str
    character_type: Optional[str]
    real_world_relation: Optional[str]
    occurrence_count: int
    first_appeared: Optional[date]
    last_appeared: Optional[date]
    associations: list[AssociationResponse]
    dreams: list["CharacterDreamAppearance"]
    archetype_counts: dict[str, int]
    common_traits: list[str]
    created_at: datetime
    updated_at: datetime

class CharacterDreamAppearance(BaseModel):
    dream_id: int
    dream_title: Optional[str]
    dream_date: date
    role_in_dream: Optional[str]
    archetype: Optional[str]
    traits: list[str]
    context_note: Optional[str]
    is_confirmed: bool

class CharacterListResponse(BaseModel):
    data: list[CharacterResponse]
    has_more: bool = False
    next_cursor: Optional[int] = None
    