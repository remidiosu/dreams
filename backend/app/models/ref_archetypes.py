from app.database import Base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB


class RefArchetype(Base):
    __tablename__ = "ref_archetypes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    typical_traits = Column(JSONB, default=list)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "typical_traits": self.typical_traits or [],
        }


DEFAULT_ARCHETYPES = [
    {
        "name": "shadow",
        "description": "Repressed aspects of self, the dark side of personality that the ego does not identify with",
        "typical_traits": ["dark", "threatening", "hidden", "powerful", "rejected"]
    },
    {
        "name": "anima",
        "description": "Feminine aspect in male psyche, representing emotional life and relatedness",
        "typical_traits": ["mysterious", "alluring", "emotional", "intuitive", "seductive"]
    },
    {
        "name": "animus",
        "description": "Masculine aspect in female psyche, representing logos, reason, and action",
        "typical_traits": ["rational", "assertive", "action-oriented", "opinionated", "judgmental"]
    },
    {
        "name": "wise_old_man",
        "description": "Archetype of spirit, meaning, and wisdom; often appears as mentor or guide",
        "typical_traits": ["elderly", "knowing", "calm", "helpful", "mysterious", "authoritative"]
    },
    {
        "name": "wise_old_woman",
        "description": "Great Mother in her positive aspect, intuitive wisdom and connection to nature",
        "typical_traits": ["elderly", "nurturing", "mystical", "earthy", "knowing"]
    },
    {
        "name": "trickster",
        "description": "Chaos, change, boundary-crossing; disrupts the status quo and catalyzes transformation",
        "typical_traits": ["playful", "deceptive", "transformative", "unpredictable", "amoral"]
    },
    {
        "name": "hero",
        "description": "Ego consciousness overcoming obstacles; the drive toward achievement and individuation",
        "typical_traits": ["brave", "determined", "struggling", "young", "ambitious"]
    },
    {
        "name": "mother",
        "description": "Nurturing, protection, origin; can be positive (caring) or negative (devouring)",
        "typical_traits": ["caring", "protective", "overwhelming", "nurturing", "smothering"]
    },
    {
        "name": "father",
        "description": "Authority, order, judgment; represents law, discipline, and worldly power",
        "typical_traits": ["authoritative", "distant", "guiding", "judgmental", "protective"]
    },
    {
        "name": "child",
        "description": "Innocence, potential, vulnerability; represents new beginnings and future possibilities",
        "typical_traits": ["innocent", "playful", "vulnerable", "new", "spontaneous"]
    },
    {
        "name": "self",
        "description": "Wholeness, integration, center of the psyche; the goal of individuation",
        "typical_traits": ["unified", "transcendent", "complete", "balanced", "centered"]
    },
    {
        "name": "persona",
        "description": "Social mask, public self; the face we present to the world",
        "typical_traits": ["performative", "adaptive", "superficial", "social", "protective"]
    },
]
