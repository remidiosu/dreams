from app.database import Base
from sqlalchemy import Column, Integer, DateTime, String, Text, func, Index


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    timezone = Column(String(50), default='UTC')

    graph_path = Column(String(255), nullable=True)
    last_indexed_at = Column(DateTime(timezone=True), nullable=True)
    dreams_indexed_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_users_email', 'email'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "timezone": self.timezone,
            "graph_path": self.graph_path,
            "last_indexed_at": self.last_indexed_at.isoformat() if self.last_indexed_at else None,
            "dreams_indexed_count": self.dreams_indexed_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
