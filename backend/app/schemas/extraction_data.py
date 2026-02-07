from pathlib import Path
from typing import Optional
from pydantic import BaseModel


class ExtractedSymbol(BaseModel):
    name: str
    category: str
    context: str
    universal_meaning: Optional[str] = None
    personal_associations: list[str] = []

class ExtractedCharacter(BaseModel):
    name: str
    character_type: str
    real_world_relation: Optional[str] = None
    role_in_dream: str
    archetype: Optional[str] = None
    traits: list[str] = []
    context: str

class ExtractedTheme(BaseModel):
    theme: str
    description: str

class ExtractedEmotion(BaseModel):
    emotion: str
    intensity: int
    emotion_type: str = "during"

class DreamExtraction(BaseModel):
    symbols: list[ExtractedSymbol] = []
    characters: list[ExtractedCharacter] = []
    themes: list[ExtractedTheme] = []
    emotions: list[ExtractedEmotion] = []
    setting_analysis: Optional[str] = None
    jungian_interpretation: Optional[str] = None


def build_extraction_prompt(narrative: str, setting: Optional[str] = None) -> str:
    context = f"Dream narrative:\n{narrative}"
    if setting:
        context += f"\n\nSetting: {setting}"

    prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "extraction_prompt.md"
    with open(prompt_path, "r") as f:
        extraction_template = f.read()

    return extraction_template.format(context=context)
