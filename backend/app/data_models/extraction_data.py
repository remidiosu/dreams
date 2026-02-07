from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class ImageData(BaseModel):
    base64: str
    mime_type: str
    caption: Optional[str] = None


class ExtractPreviewRequest(BaseModel):
    narrative: str = Field("", min_length=0)
    setting: Optional[str] = None
    audio_base64: Optional[str] = None
    audio_mime_type: Optional[str] = None
    images: Optional[list[ImageData]] = None

class ExtractedSymbolData(BaseModel):
    name: str
    category: str = "other"
    context: str = ""
    universal_meaning: Optional[str] = None
    personal_associations: list[str] = []
    personal_meaning: Optional[str] = None
    is_user_added: bool = False

class ExtractedCharacterData(BaseModel):
    name: str
    character_type: str = "unknown_person"
    real_world_relation: Optional[str] = None
    role_in_dream: str = "unknown"
    archetype: Optional[str] = None
    traits: list[str] = []
    context: str = ""
    personal_significance: Optional[str] = None
    is_user_added: bool = False

class ExtractedThemeData(BaseModel):
    theme: str
    is_user_added: bool = False

class ExtractedEmotionData(BaseModel):
    emotion: str
    intensity: int = Field(5, ge=1, le=10)
    emotion_type: str = "during"

class ExtractionPreviewResponse(BaseModel):
    symbols: list[ExtractedSymbolData]
    characters: list[ExtractedCharacterData]
    themes: list[ExtractedThemeData]
    emotions: list[ExtractedEmotionData]
    setting_analysis: Optional[str] = None
    jungian_interpretation: Optional[str] = None
    processed_narrative: Optional[str] = None


class CreateDreamWithExtractionRequest(BaseModel):
    title: Optional[str] = None
    narrative: str = Field(..., min_length=1)
    dream_date: date
    setting: Optional[str] = None
    development: Optional[str] = None
    ending: Optional[str] = None
    lucidity_level: Optional[str] = None
    sleep_quality: Optional[int] = Field(None, ge=1, le=5)
    emotional_intensity: Optional[int] = Field(None, ge=1, le=10)
    is_recurring: bool = False
    is_nightmare: bool = False
    ritual_completed: bool = False
    ritual_description: Optional[str] = None
    personal_interpretation: Optional[str] = None
    symbols: list[ExtractedSymbolData] = []
    characters: list[ExtractedCharacterData] = []
    themes: list[ExtractedThemeData] = []
    emotions: list[ExtractedEmotionData] = []

class DreamCreatedResponse(BaseModel):
    dream_id: int
    title: Optional[str]
    symbols_created: int
    characters_created: int
    themes_created: int
    emotions_created: int
