from dataclasses import dataclass
from typing import Optional


@dataclass
class SymbolData:
    name: str
    category: str
    context: Optional[str] = None
    universal_meaning: Optional[str] = None
    personal_meaning: Optional[str] = None
    personal_associations: list[str] = None

    def __post_init__(self):
        if self.personal_associations is None:
            self.personal_associations = []

@dataclass
class CharacterData:
    name: str
    character_type: str
    real_world_relation: Optional[str] = None
    role_in_dream: Optional[str] = None
    archetype: Optional[str] = None
    traits: list[str] = None
    context: Optional[str] = None
    personal_significance: Optional[str] = None

    def __post_init__(self):
        if self.traits is None:
            self.traits = []

@dataclass
class EmotionData:
    emotion: str
    intensity: int = 5
    emotion_type: str = "during"

@dataclass
class ThemeData:
    theme: str

@dataclass
class DreamData:
    id: int
    title: Optional[str]
    narrative: str
    dream_date: str
    setting: Optional[str] = None
    lucidity_level: Optional[str] = None
    emotional_intensity: Optional[int] = None
    is_recurring: bool = False
    is_nightmare: bool = False
    ritual_completed: bool = False
    ritual_description: Optional[str] = None
    personal_interpretation: Optional[str] = None
    symbols: list[SymbolData] = None
    characters: list[CharacterData] = None
    emotions: list[EmotionData] = None
    themes: list[ThemeData] = None

    def __post_init__(self):
        if self.symbols is None:
            self.symbols = []
        if self.characters is None:
            self.characters = []
        if self.emotions is None:
            self.emotions = []
        if self.themes is None:
            self.themes = []
