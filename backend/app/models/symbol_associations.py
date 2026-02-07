from app.database import Base
from app.models.enums.dream_enums import AssociationSource
from sqlalchemy import Column, Integer, DateTime, Text, Boolean, func, Index, ForeignKey, Enum


class SymbolAssociation(Base):
    __tablename__ = "symbol_associations"

    id = Column(Integer, primary_key=True, index=True)
    symbol_id = Column(Integer, ForeignKey('symbols.id', ondelete='CASCADE'), nullable=False)

    association_text = Column(Text, nullable=False)
    source = Column(Enum(AssociationSource, name='association_source'), default=AssociationSource.USER)
    is_confirmed = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_symbol_associations_symbol_id', 'symbol_id'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "symbol_id": self.symbol_id,
            "association_text": self.association_text,
            "source": self.source.value if self.source else None,
            "is_confirmed": self.is_confirmed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    