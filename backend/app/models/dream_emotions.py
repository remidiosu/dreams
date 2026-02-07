from app.database import Base
from app.models.enums.dream_enums import EmotionType
from sqlalchemy import Column, Integer, DateTime, String, SmallInteger, func, \
    Index, ForeignKey, Enum, UniqueConstraint, CheckConstraint


class DreamEmotion(Base):
    __tablename__ = "dream_emotions"

    id = Column(Integer, primary_key=True, index=True)
    dream_id = Column(Integer, ForeignKey('dreams.id', ondelete='CASCADE'), nullable=False)

    emotion = Column(String(50), nullable=False)
    emotion_type = Column(Enum(EmotionType, name='emotion_type'), nullable=False)
    intensity = Column(SmallInteger, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_dream_emotions_dream_id', 'dream_id'),
        Index('ix_dream_emotions_emotion', 'emotion'),
        UniqueConstraint('dream_id', 'emotion', 'emotion_type', name='uq_dream_emotion_type'),
        CheckConstraint('intensity BETWEEN 1 AND 10', name='check_emotion_intensity'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "dream_id": self.dream_id,
            "emotion": self.emotion,
            "emotion_type": self.emotion_type.value if self.emotion_type else None,
            "intensity": self.intensity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
