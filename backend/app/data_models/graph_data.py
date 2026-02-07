from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GraphStatus(BaseModel):
    total_dreams: int
    indexed_dreams: int
    pending_dreams: int
    last_indexed_at: Optional[datetime] = None
    graph_exists: bool
    entity_count: Optional[int] = None
    relationship_count: Optional[int] = None

class IndexResult(BaseModel):
    success: bool
    dreams_indexed: int
    dreams_failed: int
    errors: list[str] = []
    processing_time_ms: int

class IndexDreamResult(BaseModel):
    success: bool
    dream_id: int
    error: Optional[str] = None
    processing_time_ms: int

class GraphNode(BaseModel):
    id: str
    type: str
    label: str
    size: int = 1
    metadata: dict = {}

class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    weight: float = 1.0

class GraphExport(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    stats: dict = {}

class EntitySummary(BaseModel):
    name: str
    type: str
    occurrence_count: int
    connected_entities: int
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

class EntityListResponse(BaseModel):
    data: list[EntitySummary]
    total: int

class EntityDetail(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    occurrence_count: int
    connected_entities: list[dict]
    dream_appearances: list[dict]
    