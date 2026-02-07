from app.database import Base
from app.models.enums.dream_enums import EmotionValence
from sqlalchemy import Column, Integer, String, Text, Enum


class RefEmotion(Base):
    __tablename__ = "ref_emotions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    valence = Column(Enum(EmotionValence, name='emotion_valence'), nullable=True)
    description = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "valence": self.valence.value if self.valence else None,
            "description": self.description,
        }


DEFAULT_EMOTIONS = [
    {"name": "fear", "valence": "negative"},
    {"name": "terror", "valence": "negative"},
    {"name": "anxiety", "valence": "negative"},
    {"name": "confusion", "valence": "neutral"},
    {"name": "joy", "valence": "positive"},
    {"name": "peace", "valence": "positive"},
    {"name": "sadness", "valence": "negative"},
    {"name": "anger", "valence": "negative"},
    {"name": "shame", "valence": "negative"},
    {"name": "guilt", "valence": "negative"},
    {"name": "wonder", "valence": "positive"},
    {"name": "awe", "valence": "ambiguous"},
    {"name": "love", "valence": "positive"},
    {"name": "longing", "valence": "ambiguous"},
    {"name": "nostalgia", "valence": "ambiguous"},
    {"name": "power", "valence": "ambiguous"},
    {"name": "helplessness", "valence": "negative"},
    {"name": "curiosity", "valence": "positive"},
    {"name": "disgust", "valence": "negative"},
    {"name": "surprise", "valence": "neutral"},
]
