from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional


class AssociationCreate(BaseModel):
    association_text: str = Field(..., min_length=1)

class AssociationResponse(BaseModel):
    id: int
    association_text: str
    source: str
    is_confirmed: bool
    created_at: datetime

class DreamSymbolCreate(BaseModel):
    name: str = Field(..., min_length=1)
    category: Optional[str] = None
    associations: list[str] = []
    context_note: Optional[str] = None

class DreamSymbolUpdate(BaseModel):
    context_note: Optional[str] = None
    is_confirmed: Optional[bool] = None

class DreamSymbolResponse(BaseModel):
    id: int
    symbol_id: int
    name: str
    category: Optional[str]
    associations: list[AssociationResponse]
    is_ai_extracted: bool
    is_confirmed: bool
    context_note: Optional[str]
    created_at: datetime

class SymbolUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None

class SymbolResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    occurrence_count: int
    first_appeared: Optional[date]
    last_appeared: Optional[date]
    associations: list[AssociationResponse]
    created_at: datetime
    updated_at: datetime

class SymbolWithDreamsResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    occurrence_count: int
    first_appeared: Optional[date]
    last_appeared: Optional[date]
    associations: list[AssociationResponse]
    dreams: list["SymbolDreamAppearance"]
    created_at: datetime
    updated_at: datetime

class SymbolDreamAppearance(BaseModel):
    dream_id: int
    dream_title: Optional[str]
    dream_date: date
    context_note: Optional[str]
    is_confirmed: bool

class SymbolListResponse(BaseModel):
    data: list[SymbolResponse]
    has_more: bool = False
    next_cursor: Optional[int] = None
    total_count: int = 0
