from app.database import Base
from app.models.enums.dream_enums import LucidityLevel
from sqlalchemy import Column, Integer, DateTime, String, Text, Date, SmallInteger, Boolean, func, Index, ForeignKey, Enum, CheckConstraint


class Dream(Base):
    __tablename__ = "dreams"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=True)
    narrative = Column(Text, nullable=False)
    dream_date = Column(Date, nullable=False)

    setting = Column(Text, nullable=True)
    development = Column(Text, nullable=True)
    ending = Column(Text, nullable=True)
    emotion_on_waking = Column(String(50), nullable=True)
    emotional_intensity = Column(SmallInteger, nullable=True)
    lucidity_level = Column(Enum(LucidityLevel, name='lucidity_level'), nullable=True)
    sleep_quality = Column(SmallInteger, nullable=True)

    ritual_completed = Column(Boolean, default=False)
    ritual_description = Column(Text, nullable=True)

    is_recurring = Column(Boolean, default=False)
    is_nightmare = Column(Boolean, default=False)
    personal_interpretation = Column(Text, nullable=True)

    is_indexed = Column(Boolean, default=False)
    indexed_at = Column(DateTime(timezone=True), nullable=True)
    ai_extraction_done = Column(Boolean, default=False)

    conscious_context = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_dreams_user_id', 'user_id'),
        Index('ix_dreams_dream_date', 'dream_date'),
        Index('ix_dreams_user_date', 'user_id', 'dream_date'),
        CheckConstraint('emotional_intensity BETWEEN 1 AND 10', name='check_emotional_intensity'),
        CheckConstraint('sleep_quality BETWEEN 1 AND 5', name='check_sleep_quality'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "narrative": self.narrative,
            "dream_date": self.dream_date.isoformat() if self.dream_date else None,
            "setting": self.setting,
            "development": self.development,
            "ending": self.ending,
            "emotion_on_waking": self.emotion_on_waking,
            "emotional_intensity": self.emotional_intensity,
            "lucidity_level": self.lucidity_level.value if self.lucidity_level else None,
            "sleep_quality": self.sleep_quality,
            "ritual_completed": self.ritual_completed,
            "ritual_description": self.ritual_description,
            "is_recurring": self.is_recurring,
            "is_nightmare": self.is_nightmare,
            "personal_interpretation": self.personal_interpretation,
            "is_indexed": self.is_indexed,
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
            "ai_extraction_done": self.ai_extraction_done,
            "conscious_context": self.conscious_context,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
