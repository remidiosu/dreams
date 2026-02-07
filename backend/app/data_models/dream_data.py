from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional


class EmotionInDream(BaseModel):
    emotion: str
    emotion_type: str
    intensity: Optional[int] = None

class SymbolInDream(BaseModel):
    id: int
    symbol_id: int
    name: str
    category: Optional[str]
    associations: list[str]
    is_ai_extracted: bool
    is_confirmed: bool
    context_note: Optional[str]

class CharacterInDream(BaseModel):
    id: int
    character_id: int
    name: str
    character_type: Optional[str]
    real_world_relation: Optional[str]
    role_in_dream: Optional[str]
    archetype: Optional[str]
    traits: list[str]
    associations: list[str]
    is_ai_extracted: bool
    is_confirmed: bool
    context_note: Optional[str]

class ThemeInDream(BaseModel):
    id: int
    theme: str
    is_ai_extracted: bool
    is_confirmed: bool


class EmotionCreate(BaseModel):
    emotion: str
    emotion_type: str = "during"
    intensity: Optional[int] = Field(None, ge=1, le=10)

class DreamCreate(BaseModel):
    title: Optional[str] = None
    narrative: str = Field(..., min_length=1)
    dream_date: date
    setting: Optional[str] = None
    development: Optional[str] = None
    ending: Optional[str] = None

    emotions: list[EmotionCreate] = []
    emotion_on_waking: Optional[str] = None
    emotional_intensity: Optional[int] = Field(None, ge=1, le=10)
    lucidity_level: Optional[str] = None  # "none", "partial", "full"
    sleep_quality: Optional[int] = Field(None, ge=1, le=5)

    is_recurring: bool = False
    is_nightmare: bool = False
    ritual_completed: bool = False
    ritual_description: Optional[str] = None
    personal_interpretation: Optional[str] = None

    conscious_context: Optional[str] = None
    auto_extract: bool = False

class DreamUpdate(BaseModel):
    title: Optional[str] = None
    narrative: Optional[str] = None
    dream_date: Optional[date] = None

    setting: Optional[str] = None
    development: Optional[str] = None
    ending: Optional[str] = None

    emotions: Optional[list[EmotionCreate]] = None
    emotion_on_waking: Optional[str] = None
    emotional_intensity: Optional[int] = Field(None, ge=1, le=10)
    lucidity_level: Optional[str] = None
    sleep_quality: Optional[int] = Field(None, ge=1, le=5)
    is_recurring: Optional[bool] = None
    is_nightmare: Optional[bool] = None
    ritual_completed: Optional[bool] = None
    ritual_description: Optional[str] = None
    personal_interpretation: Optional[str] = None
    conscious_context: Optional[str] = None

class DreamSummary(BaseModel):
    id: int
    title: Optional[str]
    dream_date: date
    emotions: list[str]
    emotional_intensity: Optional[int]
    lucidity_level: Optional[str]
    is_recurring: bool
    is_nightmare: bool
    ritual_completed: bool
    symbol_count: int
    character_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class DreamResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    narrative: str
    dream_date: date
    setting: Optional[str]
    development: Optional[str]
    ending: Optional[str]
    emotions: list[EmotionInDream]
    emotion_on_waking: Optional[str]
    emotional_intensity: Optional[int]

    lucidity_level: Optional[str]
    sleep_quality: Optional[int]
    is_recurring: bool
    is_nightmare: bool
    ritual_completed: bool
    ritual_description: Optional[str]
    personal_interpretation: Optional[str]
    conscious_context: Optional[str]
    is_indexed: bool
    indexed_at: Optional[datetime]
    ai_extraction_done: bool
    symbols: list[SymbolInDream]
    characters: list[CharacterInDream]
    themes: list[ThemeInDream]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DreamListResponse(BaseModel):
    data: list[DreamSummary]
    has_more: bool = False
    next_cursor: Optional[int] = None
    total_count: Optional[int] = None

class DreamFilterParams(BaseModel):
    per_page: int = Field(25, ge=1, le=100)
    cursor: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    emotion: Optional[str] = None
    has_ritual: Optional[bool] = None
    lucidity_level: Optional[str] = None
    is_indexed: Optional[bool] = None
