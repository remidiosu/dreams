from dataclasses import dataclass
from app.llm.tools.base_tool import BaseTool


@dataclass
class SemanticSearchTool(BaseTool):
    name: str = "semantic_search"
    description: str = "Perform open-ended semantic search across all dream narratives. Use for complex questions that don't fit other tools, or when looking for patterns across multiple dreams. This searches the full text and relationships in the knowledge graph."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question to search for"
                }
            },
            "required": ["question"]
        }

@dataclass
class GetJournalSummaryTool(BaseTool):
    name: str = "get_journal_summary"
    description: str = "Get a summary of the user's dream journal (total dreams, date range, symbol count, etc.). Use to understand the scope of their dream history."
    parameters: dict = None

    def __post_init__(self):
        self.parameters = {
            "type": "object",
            "properties": {}
        }
