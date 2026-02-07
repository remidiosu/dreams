from app.database import Base
from app.models.enums.dream_enums import RoleInDream
from sqlalchemy import Column, Integer, DateTime, String, Text, Boolean, func, Index, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB


class DreamCharacter(Base):
    __tablename__ = "dream_characters"

    id = Column(Integer, primary_key=True, index=True)
    dream_id = Column(Integer, ForeignKey('dreams.id', ondelete='CASCADE'), nullable=False)
    character_id = Column(Integer, ForeignKey('characters.id', ondelete='CASCADE'), nullable=False)
    role_in_dream = Column(Enum(RoleInDream, name='role_in_dream'), nullable=True)
    archetype = Column(String(100), nullable=True)
    traits = Column(JSONB, default=list)

    is_ai_extracted = Column(Boolean, default=False)
    is_confirmed = Column(Boolean, default=True)
    context_note = Column(Text, nullable=True)
    personal_significance = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_dream_characters_dream_id', 'dream_id'),
        Index('ix_dream_characters_character_id', 'character_id'),
        Index('ix_dream_characters_archetype', 'archetype'),
        UniqueConstraint('dream_id', 'character_id', name='uq_dream_character'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "dream_id": self.dream_id,
            "character_id": self.character_id,
            "role_in_dream": self.role_in_dream.value if self.role_in_dream else None,
            "archetype": self.archetype,
            "traits": self.traits or [],
            "is_ai_extracted": self.is_ai_extracted,
            "is_confirmed": self.is_confirmed,
            "context_note": self.context_note,
            "personal_significance": self.personal_significance,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
