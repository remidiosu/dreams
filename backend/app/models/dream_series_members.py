from app.database import Base
from sqlalchemy import Column, Integer, Index, ForeignKey, UniqueConstraint


class DreamSeriesMember(Base):
    __tablename__ = "dream_series_members"

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(Integer, ForeignKey('dream_series.id', ondelete='CASCADE'), nullable=False)
    dream_id = Column(Integer, ForeignKey('dreams.id', ondelete='CASCADE'), nullable=False)

    order_index = Column(Integer, nullable=True)

    __table_args__ = (
        Index('ix_dream_series_members_series_id', 'series_id'),
        Index('ix_dream_series_members_dream_id', 'dream_id'),
        UniqueConstraint('series_id', 'dream_id', name='uq_series_dream'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "series_id": self.series_id,
            "dream_id": self.dream_id,
            "order_index": self.order_index,
        }
    