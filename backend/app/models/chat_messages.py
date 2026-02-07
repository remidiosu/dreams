from app.database import Base
from app.models.enums.dream_enums import ChatRole, QueryType
from sqlalchemy import Column, Integer, DateTime, Text, String, func, Index, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'), nullable=False)

    role = Column(Enum(ChatRole, name='chat_role'), nullable=False)
    content = Column(Text, nullable=False)
    source_dream_ids = Column(JSONB, default=list)
    source_excerpts = Column(JSONB, default=list)
    query_type = Column(Enum(QueryType, name='query_type'), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_chat_messages_chat_id', 'chat_id'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "role": self.role.value if self.role else None,
            "content": self.content,
            "source_dream_ids": self.source_dream_ids or [],
            "source_excerpts": self.source_excerpts or [],
            "query_type": self.query_type.value if self.query_type else None,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
