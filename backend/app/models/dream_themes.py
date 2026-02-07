from app.database import Base
from sqlalchemy import Column, Integer, DateTime, String, Boolean, func, Index, ForeignKey, UniqueConstraint


class DreamTheme(Base):
    __tablename__ = "dream_themes"

    id = Column(Integer, primary_key=True, index=True)
    dream_id = Column(Integer, ForeignKey('dreams.id', ondelete='CASCADE'), nullable=False)

    theme = Column(String(50), nullable=False)
    is_ai_extracted = Column(Boolean, default=False)
    is_confirmed = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_dream_themes_dream_id', 'dream_id'),
        Index('ix_dream_themes_theme', 'theme'),
        UniqueConstraint('dream_id', 'theme', name='uq_dream_theme'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "dream_id": self.dream_id,
            "theme": self.theme,
            "is_ai_extracted": self.is_ai_extracted,
            "is_confirmed": self.is_confirmed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
