from app.database import Base
from sqlalchemy import Column, Integer, DateTime, Text, Boolean, func, Index, ForeignKey, UniqueConstraint


class DreamSymbol(Base):
    __tablename__ = "dream_symbols"

    id = Column(Integer, primary_key=True, index=True)
    dream_id = Column(Integer, ForeignKey('dreams.id', ondelete='CASCADE'), nullable=False)
    symbol_id = Column(Integer, ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False)

    is_ai_extracted = Column(Boolean, default=False)
    is_confirmed = Column(Boolean, default=True)
    context_note = Column(Text, nullable=True)
    personal_meaning = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_dream_symbols_dream_id', 'dream_id'),
        Index('ix_dream_symbols_symbol_id', 'symbol_id'),
        UniqueConstraint('dream_id', 'symbol_id', name='uq_dream_symbol'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "dream_id": self.dream_id,
            "symbol_id": self.symbol_id,
            "is_ai_extracted": self.is_ai_extracted,
            "is_confirmed": self.is_confirmed,
            "context_note": self.context_note,
            "personal_meaning": self.personal_meaning,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
