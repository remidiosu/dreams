from dataclasses import dataclass, field

with open("app/prompts/dream_domain.md", "r") as f:
    DREAM_DOMAIN = f.read()

DREAM_EXAMPLE_QUERIES = [
    "What symbols appear most frequently in my dreams?",
    "When does water appear and what emotions accompany it?",
    "Which characters appear as shadow figures?",
    "What patterns exist between recurring symbols?",
    "How have my dream themes evolved over time?",
    "What emotions are most common in my dreams?",
    "Which dreams feature transformation or change?",
    "What locations appear repeatedly?",
    "Show me dreams where I felt fear or anxiety",
    "What personal meanings have I assigned to recurring symbols?",
]

DREAM_ENTITY_TYPES = [
    "Symbol",
    "Character",
    "Emotion",
    "Theme",
    "Location",
    "Action",
    "Archetype",
    "Object",
    "Animal",
    "Person",
    "PersonalMeaning",
]

@dataclass
class QueryResult:
    response: str
    sources: list[dict] = field(default_factory=list)
    query_type: str = "general"
    processing_time_ms: int = 0

@dataclass
class GraphStats:
    entity_count: int = 0
    relationship_count: int = 0
    chunk_count: int = 0
