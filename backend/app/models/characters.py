from app.database import Base
from app.models.enums.dream_enums import CharacterType
from sqlalchemy import Column, Integer, DateTime, String, Date, func, Index, ForeignKey, Enum, UniqueConstraint


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    name = Column(String(100), nullable=False)
    name_normalized = Column(String(100), nullable=False)
    character_type = Column(Enum(CharacterType, name='character_type'), nullable=True)

    real_world_relation = Column(String(100), nullable=True)

    occurrence_count = Column(Integer, default=1)
    first_appeared = Column(Date, nullable=True)
    last_appeared = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_characters_user_id', 'user_id'),
        UniqueConstraint('user_id', 'name_normalized', name='uq_user_character'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "name_normalized": self.name_normalized,
            "character_type": self.character_type.value if self.character_type else None,
            "real_world_relation": self.real_world_relation,
            "occurrence_count": self.occurrence_count,
            "first_appeared": self.first_appeared.isoformat() if self.first_appeared else None,
            "last_appeared": self.last_appeared.isoformat() if self.last_appeared else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
