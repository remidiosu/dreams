from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.data_models.extraction_data import ImageData


class ChatCreate(BaseModel):
    name: Optional[str] = None

class ChatUpdate(BaseModel):
    name: str

class ChatResponse(BaseModel):
    id: int
    name: str
    message_count: int
    created_at: datetime
    updated_at: datetime

class ChatListResponse(BaseModel):
    data: list[ChatResponse]
    has_more: bool
    next_cursor: Optional[int] = None

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    with_references: bool = True
    images: Optional[list[ImageData]] = None

class DreamSource(BaseModel):
    dream_id: int
    dream_title: Optional[str]
    dream_date: str
    excerpt: str
    relevance_score: Optional[float] = None

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: list[DreamSource] = []
    query_type: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: Optional[datetime] = None

class ChatWithMessagesResponse(BaseModel):
    id: int
    name: str
    messages: list[MessageResponse]
    created_at: datetime
    updated_at: datetime

class StreamChunk(BaseModel):
    type: str
    content: Optional[str] = None
    source: Optional[DreamSource] = None
    error: Optional[str] = None
